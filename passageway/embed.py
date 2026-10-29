"""Text embedders: the built-in ONNX model, any program speaking the embedder protocol, and a hashing stand-in for tests."""

import hashlib
import logging
import re
from pathlib import Path
from typing import Protocol

import numpy as np

from passageway.config import ConfigError, EmbedderConfig
from passageway.models import DEFAULT_PRESET, PRESETS, ModelError, download, files_missing, model_folder_for, verify

log = logging.getLogger(__name__)


class EmbedderError(Exception):
    """An embedder failed: a program of its own died or answered badly, or the model raised."""


class EmbedderStartError(ConfigError):
    """An embedder could not start. `public` is what an open endpoint may show; the message is for the log."""

    def __init__(self, message: str, public: str):
        super().__init__(message)
        self.public = public


class Embedder(Protocol):
    dim: int
    name: str

    def embed_queries(self, texts: list[str]) -> np.ndarray: ...

    def embed_passages(self, texts: list[str]) -> np.ndarray: ...


def _normalise(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return (v / norms).astype(np.float32)


def token_batches(lengths: list[int], budget: int) -> list[list[int]]:
    """Group indices so each batch's padded size (count × longest) stays within budget.

    Memory at inference grows with the padded batch, so long passages go alone or in pairs
    while short ones share a batch. Sorting by length keeps padding small.
    """
    batches: list[list[int]] = []
    current: list[int] = []
    for i in sorted(range(len(lengths)), key=lambda i: lengths[i]):
        if current and (len(current) + 1) * lengths[i] > budget:
            batches.append(current)
            current = []
        current.append(i)
    if current:
        batches.append(current)
    return batches


class OnnxEmbedder:
    """A built-in model: an ONNX encoder and its tokenizer from a preset, mean pooling over the attention mask, L2-normalised."""

    max_tokens = 512
    # Padded tokens per inference call: 1024 keeps peak RSS near 310 MB for e5-small (8 × 512 reached 550 MB).
    token_budget = 1024

    def __init__(self, model_dir: Path, preset=None, device: str = "auto", threads: int = 4):
        import onnxruntime as ort

        from passageway.models import PRESETS, choose_device

        self.preset = preset or PRESETS["multilingual-e5-small"]
        self.name, self.dim, self.min_similarity = self.preset.label, self.preset.dim, self.preset.min_similarity
        self.max_tokens = self.preset.max_tokens
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = 1
        # The arena would keep the largest batch's peak reserved for the life of the process.
        options.enable_cpu_mem_arena = False
        providers = choose_device(device, ort.get_available_providers())
        self._session = ort.InferenceSession(str(Path(model_dir) / "model.onnx"), options, providers=providers)
        self._inputs = {i.name for i in self._session.get_inputs()}
        self._encode_batch = self._tokenizer(self.preset, Path(model_dir))

    @staticmethod
    def _tokenizer(preset, model_dir: Path):
        """A function from texts to (ids, mask) arrays, padded to the longest text and cut at max_tokens."""
        if preset.tokenizer == "sentencepiece":
            import sentencepiece as spm

            # The SentencePiece model gives the same ids as the HF tokenizer.json at ~60 MB instead of ~280 MB.
            sp = spm.SentencePieceProcessor(model_file=str(model_dir / "sentencepiece.bpe.model"))

            def encode(text: str) -> list[int]:
                # XLM-R ids: fairseq offset of 1 over SentencePiece, its <unk> (0) is 3, wrapped in <s> (0) … </s> (2).
                ids = [3 if i == 0 else i + 1 for i in sp.encode(text)][: preset.max_tokens - 2]
                return [0, *ids, 2]

            pad = 1
        else:
            from tokenizers import Tokenizer

            tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
            tok.enable_truncation(preset.max_tokens)
            tok.no_padding()
            pad = next((i for i in (tok.token_to_id(t) for t in ("[PAD]", "<pad>")) if i is not None), 0)

            def encode(text: str) -> list[int]:
                return tok.encode(text).ids

        def batch(texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
            encoded = [encode(t) for t in texts]
            width = max(len(e) for e in encoded)
            ids = np.full((len(encoded), width), pad, dtype=np.int64)
            mask = np.zeros((len(encoded), width), dtype=np.int64)
            for row, e in enumerate(encoded):
                ids[row, : len(e)] = e
                mask[row, : len(e)] = 1
            return ids, mask

        return batch

    def _embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        lengths = [len(self._encode_batch([t])[0][0]) for t in texts]
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for batch in token_batches(lengths, self.token_budget):
            ids, mask = self._encode_batch([texts[i] for i in batch])
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self._inputs:
                feed["token_type_ids"] = np.zeros_like(ids)
            hidden = self._session.run(None, feed)[0]
            weights = mask[..., None].astype(np.float32)
            out[batch] = (hidden * weights).sum(axis=1) / np.maximum(weights.sum(axis=1), 1e-9)
        return _normalise(out)

    def embed_queries(self, texts: list[str]) -> np.ndarray:
        return self._embed([self.preset.query_prefix + t for t in texts])

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return self._embed([self.preset.passage_prefix + t for t in texts])


class HashEmbedder:
    """Bag of lower-cased words hashed into buckets: overlap in words means similarity. Tests only."""

    name = "hash-test"

    def __init__(self, dim: int = 384):
        self.dim = dim

    def _embed(self, texts: list[str]) -> np.ndarray:
        v = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in re.findall(r"\w+", text.lower()):
                bucket = int.from_bytes(hashlib.blake2b(word.encode(), digest_size=4).digest(), "big")
                v[row, bucket % self.dim] += 1
        return _normalise(v)

    embed_queries = _embed
    embed_passages = _embed


def model_folder(cfg: EmbedderConfig, config) -> Path:
    """Where a preset's files live: one rule with `passageway model` (models.model_folder_for); config.model_dir is the
    server's resolved PASSAGEWAY_MODEL_DIR for the default preset."""
    if cfg.model_dir:
        return cfg.model_dir
    if cfg.model == DEFAULT_PRESET:
        return config.model_dir
    return model_folder_for(cfg.model, config.data_dir, None)


def build_embedder(cfg: EmbedderConfig, config, label: str = "default") -> Embedder:
    """The embedder a configuration describes. A model or program that is not there is a ConfigError, so that a server
    can start in its error mode and say what is wrong instead of crashing."""
    if cfg.kind == "command":
        from passageway.embed_command import CommandEmbedder

        if cfg.min_similarity is None:
            log.warning("embedder %r has no min_similarity: the relevance gate of the built-in model applies, which is "
                        "probably wrong for this one; find a value with `passageway eval --sweep`", label)
        try:
            return CommandEmbedder(label, cfg.command, env=cfg.env, secrets=cfg.secrets, batch_size=cfg.batch_size,
                                   timeout=cfg.timeout)
        except EmbedderError as e:  # its output can hold hosts and paths: only the log gets it
            raise EmbedderStartError(str(e), public=f"the embedder {label!r} could not start; see the server log") from None
    preset = PRESETS[cfg.model]
    folder = model_folder(cfg, config)
    missing, wrong = files_missing(preset, folder), verify(preset, folder)
    if missing or wrong:
        if not cfg.download:
            what = f"missing {', '.join(missing)}" if missing else f"a wrong checksum for {', '.join(wrong)}"
            raise ConfigError(f"the model {cfg.model!r} in {folder} has {what}: run `passageway model download {cfg.model}` "
                              "(download = true in [embedder] does it at start)")
        log.info("fetching the model %s (%d MB) from huggingface.co into %s, pinned and checksummed; the server answers "
                 "once it is there", cfg.model, preset.size_mb, folder)
        try:
            download(preset, folder, report=lambda m: log.info("%s", m))
        except (ModelError, OSError) as e:
            raise ConfigError(f"could not fetch the model {cfg.model!r}: {e}") from None
    try:
        embedder = OnnxEmbedder(folder, preset, cfg.device)
    except ModelError as e:
        raise ConfigError(str(e)) from None
    if cfg.min_similarity is None and getattr(embedder, "min_similarity", None) is None:
        log.warning("the model %r has no measured min_similarity yet, so the default gate of the built-in model (0.845) "
                    "applies, and on another similarity scale almost nothing will pass it: set min_similarity under "
                    "[embedder] from a run of `passageway eval --sweep`", cfg.model)
    return embedder
