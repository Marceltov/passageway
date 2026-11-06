# Choosing a model

The three model presets of the built-in embedder, compared on the [sample corpus](reference/corpus.md) with the same 100 questions as the [measurements](measurements.md), each with its own fresh index and its own relevance threshold. `corpus/compare.sh` reproduces it and writes the block below. [Measure retrieval quality](guides/evaluate.md) explains the metrics; the intervals say how little a difference of a few points means.

Each model has its own similarity scale, so the threshold tables are the point of this page: a model's `min_similarity` is read off where hit@3 and silence cross, and that value is the preset's default (`passageway model list` shows it).

<!-- chart:models -->

The chart is drawn from `docs/models.history.json`; the tables below carry every figure.

<!-- passageway:results:start -->
2026-11-06 · passageway 0.4.0 · 100 questions (70 answerable, 30 unanswerable) · Linux x86_64, Python 3.13.5

Each embedder ran with its own fresh index and its own relevance threshold, because similarity scales differ between models. Load is the time to start the model, Index the time to embed all sources.

| Embedder | Dimensions | Threshold | Load | Index | Hit@1 | Hit@3 | MRR | Silence | False silence | p50 / p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| default: multilingual-e5-small-int8 | 384 | 0.845 | 0.8 s | 94.8 s | 75.7% (64–84%) | 84.3% (74–91%) | 0.800 | 80.0% (63–90%) | 0.0% (0–5%) | 19.7 / 28.4 ms |
| e5-base: multilingual-e5-base-int8 | 768 | 0.845 | 1.4 s | 336.8 s | 64.3% (53–74%) | 74.3% (63–83%) | 0.690 | 90.0% (74–96%) | 17.1% (10–28%) | 44.8 / 67.6 ms |
| jina-de: jina-embeddings-v2-base-de-int8 | 768 | 0.845 | 1.2 s | 303.0 s | 34.3% (24–46%) | 35.7% (26–47%) | 0.350 | 93.3% (79–98%) | 48.6% (37–60%) | 37.0 / 55.4 ms |

In brackets: the 95% interval of a rate, the range that holds the true rate in 95 of 100 repetitions with other questions of the same kind. Overlapping intervals are a warning against over-reading a difference, not a test of it. The tables below show point values only.

### Relevance threshold: default

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 29.4 ms |
| 0.45 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.6 ms |
| 0.5 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.9 ms |
| 0.52 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 29.1 ms |
| 0.54 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 29.0 ms |
| 0.55 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.9 ms |
| 0.56 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.9 ms |
| 0.58 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.6 ms |
| 0.6 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.8 ms |
| 0.65 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 28.9 ms |
| 0.7 | 75.7% | 90.0% | 0.824 | 0.0% | 0.0% | 29.1 ms |
| 0.75 | 75.7% | 90.0% | 0.824 | 3.3% | 0.0% | 28.9 ms |
| 0.8 | 75.7% | 90.0% | 0.824 | 40.0% | 0.0% | 28.8 ms |
| 0.81 | 75.7% | 90.0% | 0.824 | 46.7% | 0.0% | 28.7 ms |
| 0.82 | 75.7% | 90.0% | 0.824 | 70.0% | 0.0% | 28.6 ms |
| 0.83 | 75.7% | 88.6% | 0.819 | 73.3% | 0.0% | 28.6 ms |
| 0.84 | 74.3% | 85.7% | 0.798 | 80.0% | 0.0% | 28.4 ms |
| 0.845 | 75.7% | 84.3% | 0.800 | 80.0% | 0.0% | 28.7 ms |
| 0.85 | 71.4% | 82.9% | 0.769 | 83.3% | 5.7% | 28.7 ms |
| 0.86 | 68.6% | 77.1% | 0.729 | 90.0% | 7.1% | 29.7 ms |
| 0.87 | 65.7% | 75.7% | 0.705 | 90.0% | 12.9% | 28.4 ms |
| 0.88 | 65.7% | 74.3% | 0.698 | 93.3% | 12.9% | 28.4 ms |
| 0.9 | 52.9% | 61.4% | 0.569 | 93.3% | 24.3% | 28.4 ms |

### Relevance threshold: e5-base

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 61.9 ms |
| 0.45 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 62.1 ms |
| 0.5 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 62.3 ms |
| 0.52 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 61.9 ms |
| 0.54 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 61.9 ms |
| 0.55 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 62.5 ms |
| 0.56 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 55.6 ms |
| 0.58 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 59.3 ms |
| 0.6 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 58.1 ms |
| 0.65 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 57.5 ms |
| 0.7 | 78.6% | 94.3% | 0.855 | 0.0% | 0.0% | 57.1 ms |
| 0.75 | 78.6% | 94.3% | 0.855 | 16.7% | 0.0% | 55.9 ms |
| 0.8 | 80.0% | 94.3% | 0.864 | 66.7% | 0.0% | 58.4 ms |
| 0.81 | 75.7% | 91.4% | 0.829 | 70.0% | 2.9% | 55.4 ms |
| 0.82 | 72.9% | 82.9% | 0.776 | 83.3% | 5.7% | 54.7 ms |
| 0.83 | 68.6% | 78.6% | 0.733 | 86.7% | 11.4% | 55.7 ms |
| 0.84 | 67.1% | 77.1% | 0.719 | 90.0% | 12.9% | 56.8 ms |
| 0.845 | 64.3% | 74.3% | 0.690 | 90.0% | 17.1% | 54.8 ms |
| 0.85 | 61.4% | 70.0% | 0.655 | 90.0% | 20.0% | 55.0 ms |
| 0.86 | 60.0% | 68.6% | 0.640 | 90.0% | 21.4% | 56.4 ms |
| 0.87 | 52.9% | 61.4% | 0.569 | 90.0% | 27.1% | 55.9 ms |
| 0.88 | 50.0% | 58.6% | 0.540 | 90.0% | 30.0% | 55.2 ms |
| 0.9 | 40.0% | 48.6% | 0.440 | 90.0% | 42.9% | 56.6 ms |

### Relevance threshold: jina-de

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 78.6% | 90.0% | 0.831 | 53.3% | 1.4% | 56.3 ms |
| 0.45 | 77.1% | 88.6% | 0.821 | 53.3% | 1.4% | 57.7 ms |
| 0.5 | 74.3% | 81.4% | 0.774 | 70.0% | 4.3% | 55.9 ms |
| 0.52 | 74.3% | 81.4% | 0.774 | 73.3% | 5.7% | 57.7 ms |
| 0.54 | 74.3% | 80.0% | 0.767 | 80.0% | 7.1% | 56.7 ms |
| 0.55 | 70.0% | 75.7% | 0.724 | 80.0% | 11.4% | 55.4 ms |
| 0.56 | 65.7% | 71.4% | 0.681 | 80.0% | 17.1% | 56.3 ms |
| 0.58 | 57.1% | 61.4% | 0.590 | 86.7% | 25.7% | 58.9 ms |
| 0.6 | 52.9% | 54.3% | 0.536 | 93.3% | 28.6% | 57.8 ms |
| 0.65 | 44.3% | 45.7% | 0.450 | 93.3% | 38.6% | 55.3 ms |
| 0.7 | 35.7% | 37.1% | 0.364 | 93.3% | 47.1% | 55.4 ms |
| 0.75 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.4 ms |
| 0.8 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.3 ms |
| 0.81 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.9 ms |
| 0.82 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.8 ms |
| 0.83 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 56.4 ms |
| 0.84 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 57.4 ms |
| 0.845 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.3 ms |
| 0.85 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 56.5 ms |
| 0.86 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 56.7 ms |
| 0.87 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 55.5 ms |
| 0.88 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 56.5 ms |
| 0.9 | 34.3% | 35.7% | 0.350 | 93.3% | 48.6% | 56.7 ms |

### History

| Date | Embedder | Threshold | Questions | Hit@3 | Silence | p95 |
|---|---|---|---|---|---|---|
| 2026-11-06 | default: multilingual-e5-small-int8 | 0.845 | 100 | 84.3% | 80.0% | 28.4 ms |
| 2026-11-06 | e5-base: multilingual-e5-base-int8 | 0.845 | 100 | 74.3% | 90.0% | 67.6 ms |
| 2026-11-06 | jina-de: jina-embeddings-v2-base-de-int8 | 0.845 | 100 | 35.7% | 93.3% | 55.4 ms |
| 2026-10-29 | default: multilingual-e5-small-int8 | 0.845 | 100 | 88.6% | 80.0% | 11.4 ms |
| 2026-10-29 | e5-base: multilingual-e5-base-int8 | 0.845 | 100 | 75.7% | 86.7% | 22.6 ms |
| 2026-10-29 | jina-de: jina-embeddings-v2-base-de-int8 | 0.845 | 100 | 44.3% | 96.7% | 22.6 ms |
<!-- passageway:results:end -->

## Notes on the comparison (29 October 2026)

Written by hand after the first run of `corpus/compare.sh` on a CPU, so it does not change when the block above is rewritten.

- **The rule for a preset's gate:** the threshold with the highest sum of hit@3 and silence in its sweep, the lower one on a tie. It gives `multilingual-e5-small` 0.845 (unchanged: 0.84 and 0.845 tie), `multilingual-e5-base` 0.83 and `jina-v2-base-de` 0.56. Each preset carries that value, and `passageway model list` shows it.
- **Jina at its gate is the quietest model here:** silence 97% against e5-small's 80%, with hit@3 inside the same interval (86% against 89%) and false silence 6% against 1%. Its similarity scale is nothing like e5's: a match sits around 0.5, an unrelated passage near 0; with e5 the two lie at 0.85 and 0.80. That is why a gate is measured per model and never carried over.
- **The default stays `multilingual-e5-small`:** it is the smallest and fastest (indexing the corpus in 21 s against Jina's 54 s, answering in 8 ms against 14 ms), and the Trilium connector's parity was measured with it. For German-heavy sources, or where silence on off-topic questions matters more than speed, `model = "jina-v2-base-de"` is the better choice on these numbers.
- **`multilingual-e5-base` does not earn its size** on this corpus: at its gate it finds less than e5-small (hit@3 86% against 89%) and costs twice the indexing time.
- **CoreML was measured and turned off by default:** on these int8 models it ran four times slower than the CPU and gave different vectors (far off for Jina), so `device = "auto"` means CPU; `coreml` stays as an opt-in.
- The same limits apply as on the [measurements page](measurements.md): one corpus of 60 Wikipedia articles, one machine, and intervals of about ±10 points; the reworded questions are what every model misses most.
