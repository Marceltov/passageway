# Choosing a model

The three built-in models compared on the [sample corpus](reference/corpus.md) with the same 100 questions as the [measurements](measurements.md), each with its own fresh index and its own relevance threshold. `corpus/compare.sh` reproduces it and writes the block below. [Measure retrieval quality](guides/evaluate.md) explains the metrics; the intervals say how little a difference of a few points means.

Each model has its own similarity scale, so the threshold tables are the point of this page: a model's `min_similarity` is read off where hit@3 and silence cross, and that value is the preset's default (`passageway model list` shows it).

<!-- passageway:results:start -->
2026-10-29 · passageway 0.2.0 · 100 questions (70 answerable, 30 unanswerable) · Darwin arm64, Python 3.14.3

Each embedder ran with its own fresh index and its own relevance threshold, because similarity scales differ between models. Load is the time to start the model, Index the time to embed all sources.

| Embedder | Dimensions | Threshold | Load | Index | Hit@1 | Hit@3 | MRR | Silence | False silence | p50 / p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| default: multilingual-e5-small-int8 | 384 | 0.845 | 0.3 s | 21.5 s | 77.1% (66–85%) | 88.6% (79–94%) | 0.826 | 80.0% (63–90%) | 1.4% (0–8%) | 7.7 / 11.4 ms |
| e5-base: multilingual-e5-base-int8 | 768 | 0.845 | 0.4 s | 47.3 s | 68.6% (57–78%) | 75.7% (64–84%) | 0.714 | 86.7% (70–95%) | 10.0% (5–19%) | 14.4 / 22.6 ms |
| jina-de: jina-embeddings-v2-base-de-int8 | 768 | 0.845 | 0.2 s | 54.4 s | 37.1% (27–49%) | 44.3% (33–56%) | 0.405 | 96.7% (83–99%) | 44.3% (33–56%) | 14.7 / 22.6 ms |

In brackets: the 95% interval of a rate, the range that holds the true rate in 95 of 100 repetitions with other questions of the same kind. Overlapping intervals are a warning against over-reading a difference, not a test of it. The tables below show point values only.

### Relevance threshold: default

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.6 ms |
| 0.45 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.5 ms |
| 0.5 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.6 ms |
| 0.52 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.4 ms |
| 0.54 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.7 ms |
| 0.55 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.5 ms |
| 0.56 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.5 ms |
| 0.58 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.3 ms |
| 0.6 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.5 ms |
| 0.65 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.7 ms |
| 0.7 | 78.6% | 90.0% | 0.840 | 0.0% | 0.0% | 11.6 ms |
| 0.75 | 78.6% | 90.0% | 0.840 | 6.7% | 0.0% | 11.4 ms |
| 0.8 | 78.6% | 90.0% | 0.840 | 46.7% | 0.0% | 11.4 ms |
| 0.81 | 78.6% | 90.0% | 0.840 | 53.3% | 0.0% | 11.4 ms |
| 0.82 | 78.6% | 90.0% | 0.840 | 63.3% | 0.0% | 11.4 ms |
| 0.83 | 77.1% | 88.6% | 0.829 | 73.3% | 0.0% | 11.4 ms |
| 0.84 | 78.6% | 88.6% | 0.833 | 80.0% | 0.0% | 11.4 ms |
| 0.845 | 77.1% | 88.6% | 0.826 | 80.0% | 1.4% | 11.3 ms |
| 0.85 | 72.9% | 84.3% | 0.783 | 83.3% | 5.7% | 11.2 ms |
| 0.86 | 70.0% | 77.1% | 0.736 | 90.0% | 8.6% | 11.0 ms |
| 0.87 | 67.1% | 74.3% | 0.707 | 90.0% | 11.4% | 11.2 ms |
| 0.88 | 65.7% | 72.9% | 0.693 | 93.3% | 14.3% | 11.2 ms |
| 0.9 | 51.4% | 57.1% | 0.543 | 93.3% | 27.1% | 11.3 ms |

### Relevance threshold: e5-base

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 21.7 ms |
| 0.45 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.7 ms |
| 0.5 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.1 ms |
| 0.52 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.7 ms |
| 0.54 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 21.5 ms |
| 0.55 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.7 ms |
| 0.56 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.0 ms |
| 0.58 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.3 ms |
| 0.6 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 22.1 ms |
| 0.65 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 23.1 ms |
| 0.7 | 75.7% | 91.4% | 0.829 | 0.0% | 0.0% | 23.1 ms |
| 0.75 | 75.7% | 91.4% | 0.829 | 13.3% | 0.0% | 22.2 ms |
| 0.8 | 75.7% | 90.0% | 0.821 | 56.7% | 1.4% | 22.1 ms |
| 0.81 | 75.7% | 91.4% | 0.826 | 70.0% | 1.4% | 22.9 ms |
| 0.82 | 77.1% | 91.4% | 0.831 | 73.3% | 1.4% | 22.7 ms |
| 0.83 | 72.9% | 85.7% | 0.786 | 80.0% | 4.3% | 22.1 ms |
| 0.84 | 68.6% | 77.1% | 0.721 | 83.3% | 10.0% | 21.8 ms |
| 0.845 | 68.6% | 75.7% | 0.714 | 86.7% | 10.0% | 22.2 ms |
| 0.85 | 67.1% | 74.3% | 0.700 | 90.0% | 12.9% | 22.8 ms |
| 0.86 | 65.7% | 72.9% | 0.686 | 90.0% | 17.1% | 22.3 ms |
| 0.87 | 61.4% | 67.1% | 0.638 | 90.0% | 22.9% | 21.8 ms |
| 0.88 | 51.4% | 57.1% | 0.538 | 90.0% | 31.4% | 22.3 ms |
| 0.9 | 42.9% | 48.6% | 0.452 | 90.0% | 41.4% | 21.5 ms |

### Relevance threshold: jina-de

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.4 | 80.0% | 88.6% | 0.840 | 53.3% | 0.0% | 23.0 ms |
| 0.45 | 80.0% | 88.6% | 0.843 | 63.3% | 0.0% | 22.9 ms |
| 0.5 | 78.6% | 84.3% | 0.814 | 80.0% | 1.4% | 23.2 ms |
| 0.52 | 77.1% | 85.7% | 0.810 | 86.7% | 4.3% | 22.6 ms |
| 0.54 | 77.1% | 85.7% | 0.812 | 90.0% | 4.3% | 22.5 ms |
| 0.55 | 77.1% | 85.7% | 0.810 | 93.3% | 4.3% | 22.0 ms |
| 0.56 | 78.6% | 85.7% | 0.817 | 96.7% | 5.7% | 22.2 ms |
| 0.58 | 77.1% | 84.3% | 0.802 | 96.7% | 5.7% | 22.3 ms |
| 0.6 | 77.1% | 84.3% | 0.802 | 96.7% | 5.7% | 22.9 ms |
| 0.65 | 74.3% | 84.3% | 0.790 | 96.7% | 7.1% | 22.3 ms |
| 0.7 | 70.0% | 80.0% | 0.748 | 96.7% | 11.4% | 22.3 ms |
| 0.75 | 50.0% | 57.1% | 0.533 | 96.7% | 31.4% | 22.6 ms |
| 0.8 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.1 ms |
| 0.81 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 21.9 ms |
| 0.82 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.1 ms |
| 0.83 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 21.8 ms |
| 0.84 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.5 ms |
| 0.845 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.2 ms |
| 0.85 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.8 ms |
| 0.86 | 37.1% | 44.3% | 0.405 | 96.7% | 44.3% | 22.3 ms |
| 0.87 | 35.7% | 42.9% | 0.390 | 96.7% | 45.7% | 22.2 ms |
| 0.88 | 35.7% | 42.9% | 0.390 | 96.7% | 45.7% | 22.0 ms |
| 0.9 | 35.7% | 42.9% | 0.390 | 96.7% | 45.7% | 22.2 ms |

### History

| Date | Embedder | Threshold | Questions | Hit@3 | Silence | p95 |
|---|---|---|---|---|---|---|
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
