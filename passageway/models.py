"""The built-in embedding models: presets pinned to a Hugging Face revision and checksums, their download, the device."""

import hashlib
import platform
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

HUB = "https://huggingface.co"
USER_AGENT = "passageway (+https://github.com/Marceltov/passageway)"
DEFAULT_PRESET = "multilingual-e5-small"
DEVICES = ("auto", "cpu", "coreml")


class ModelError(Exception):
    pass


@dataclass(frozen=True)
class Preset:
    name: str
    repo: str
    revision: str
    files: dict[str, tuple[str, str]]  # file in the model folder -> (path in the repo, sha256)
    tokenizer: str  # "sentencepiece" (XLM-R ids with the fairseq offset) or "tokenizers" (a tokenizer.json)
    query_prefix: str
    passage_prefix: str
    max_tokens: int
    pooling: str  # "mean"
    dim: int
    min_similarity: float | None  # the relevance gate measured for this model on the sample corpus; None: not yet
    label: str  # the embedder name the index records

    @property
    def size_mb(self) -> int:
        return SIZES_MB.get(self.name, 0)


SENTENCEPIECE = "cfc8146abe2a0488e9e2a0c56de7952f7c11ab059eca145a0a727afce0db2865"
SIZES_MB = {"multilingual-e5-small": 123, "multilingual-e5-base": 283, "jina-v2-base-de": 164}

PRESETS: dict[str, Preset] = {
    "multilingual-e5-small": Preset(
        "multilingual-e5-small", "Xenova/multilingual-e5-small", "761b726dd34fb83930e26aab4e9ac3899aa1fa78",
        {"model.onnx": ("onnx/model_quantized.onnx", "f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193"),
         "sentencepiece.bpe.model": ("sentencepiece.bpe.model", SENTENCEPIECE)},
        "sentencepiece", "query: ", "passage: ", 512, "mean", 384, 0.845, "multilingual-e5-small-int8"),
    "multilingual-e5-base": Preset(
        "multilingual-e5-base", "Xenova/multilingual-e5-base", "1ec9243030a27d1a115d5c340572074c125b58b2",
        {"model.onnx": ("onnx/model_int8.onnx", "9ddfd8b45086dabc59a7e1bb00463225dace8954962418b240840f2153bc87da"),
         "sentencepiece.bpe.model": ("sentencepiece.bpe.model", SENTENCEPIECE)},
        "sentencepiece", "query: ", "passage: ", 512, "mean", 768, None, "multilingual-e5-base-int8"),
    "jina-v2-base-de": Preset(
        "jina-v2-base-de", "jinaai/jina-embeddings-v2-base-de", "3f9eede875721714945b6a99a3198299243cf2be",
        {"model.onnx": ("onnx/model_quantized.onnx", "b19a38d186594d9784e6a2c8954035a6928b5da1df402e7942d25021cf488b6b"),
         "tokenizer.json": ("tokenizer.json", "376c53a06d6911569afc19f584002a11dbcd6b871afb6d96b8600eb3c4e7e7a7"),
         "config.json": ("config.json", "8d4c498741937d1467af5be739dc0fbcc4d033eb1fb93ece4f1c9c6bbdd37ec5")},
        "tokenizers", "", "", 512, "mean", 768, None, "jina-embeddings-v2-base-de-int8"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_missing(preset: Preset, folder: Path) -> list[str]:
    return [name for name in preset.files if not (folder / name).is_file()]


def verify(preset: Preset, folder: Path) -> list[str]:
    """The files whose checksum is not the pinned one (missing files are not listed: see files_missing)."""
    return [name for name, (_, sha) in preset.files.items() if (folder / name).is_file() and _sha256(folder / name) != sha]


def download(preset: Preset, folder: Path, *, base_url: str = HUB, report=None) -> bool:
    """Fetch the preset's files into `folder` unless they are all there and right. Everything goes to a temporary folder
    first and is verified; only a complete, verified set is moved into place. Returns True when something was fetched."""
    folder = Path(folder)
    if not files_missing(preset, folder) and not verify(preset, folder):
        return False
    tmp = folder.with_name(folder.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    try:
        for name, (remote, sha) in preset.files.items():
            url = f"{base_url}/{preset.repo}/resolve/{preset.revision}/{remote}"
            if report:
                report(f"downloading {preset.repo}/{remote}")
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=60) as r, \
                        open(tmp / name, "wb") as out:
                    expected = r.headers.get("Content-Length")
                    shutil.copyfileobj(r, out, 1 << 20)
            except urllib.error.HTTPError as e:
                raise ModelError(f"{url}: HTTP {e.code}") from None
            except (urllib.error.URLError, OSError, TimeoutError) as e:
                raise ModelError(f"{url}: {getattr(e, 'reason', e)}") from None
            if expected and (tmp / name).stat().st_size != int(expected):
                raise ModelError(f"{url}: the download ended after {(tmp / name).stat().st_size} of {expected} bytes")
            if _sha256(tmp / name) != sha:
                raise ModelError(f"{url}: the checksum does not match the one pinned for {preset.name}; the file was not kept")
        if folder.exists():
            shutil.rmtree(folder)
        tmp.rename(folder)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True


def choose_device(device: str, available: list[str], system: str | None = None, machine: str | None = None) -> list[str]:
    """The onnxruntime providers for a device setting. `auto` is CoreML on an Apple-silicon Mac when the runtime has it."""
    system = system or sys.platform
    machine = machine or platform.machine()
    coreml = "CoreMLExecutionProvider" in available
    if device == "coreml" and not coreml:
        raise ModelError("device = \"coreml\" needs the CoreML provider, which this onnxruntime does not have")
    apple = system.startswith("darwin") and machine in ("arm64", "aarch64")
    if device == "coreml" or (device == "auto" and apple and coreml):
        return ["CoreMLExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]


def main(argv: list[str]) -> int:
    """passageway model list | download [PRESET] | verify [PRESET]."""
    import argparse
    import os

    from passageway.config import default_data_dir

    p = argparse.ArgumentParser(prog="passageway model", description="The built-in embedding models: list the presets, "
                                "download one (pinned to a revision, every file verified by checksum), verify one.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="the presets and what they are")
    for name in ("download", "verify"):
        q = sub.add_parser(name)
        q.add_argument("preset", nargs="?", default=DEFAULT_PRESET)
        q.add_argument("--model-dir", type=Path, help="the folder (default: <data dir>/models/<preset>, or PASSAGEWAY_MODEL_DIR "
                                                       "for the default preset)")
    args = p.parse_args(argv)
    if args.command == "list":
        for name, preset in PRESETS.items():
            gate = f"min_similarity {preset.min_similarity}" if preset.min_similarity is not None else "min_similarity not measured yet"
            print(f"{name:24s} {preset.dim:4d} dimensions  {preset.size_mb:4d} MB  {gate}"
                  + ("  (default)" if name == DEFAULT_PRESET else ""))
        return 0
    if args.preset not in PRESETS:
        print(f"model: unknown preset {args.preset!r} (known: {', '.join(PRESETS)})", file=sys.stderr)
        return 2
    preset = PRESETS[args.preset]
    data_dir = Path(os.environ.get("PASSAGEWAY_DATA_DIR") or default_data_dir())
    folder = args.model_dir or (Path(os.environ["PASSAGEWAY_MODEL_DIR"]) if args.preset == DEFAULT_PRESET
                                and os.environ.get("PASSAGEWAY_MODEL_DIR") else data_dir / "models" / args.preset)
    if args.command == "download":
        try:
            fetched = download(preset, folder, base_url=os.environ.get("PASSAGEWAY_MODEL_HUB", HUB), report=print)
        except ModelError as e:
            print(f"model: {e}", file=sys.stderr)
            return 1
        print(f"{args.preset}: {'downloaded and verified' if fetched else 'already there and verified'} in {folder}")
        return 0
    missing, wrong = files_missing(preset, folder), verify(preset, folder)
    if missing or wrong:
        print(f"{args.preset} in {folder}: " + "; ".join(filter(None, [f"missing {', '.join(missing)}" if missing else "",
                                                                        f"wrong checksum: {', '.join(wrong)}" if wrong else ""])))
        return 1
    print(f"{args.preset} in {folder}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
