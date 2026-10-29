# Measurements

How well passageway finds the right passage and stays silent when there is none, measured with `passageway eval` on the [sample corpus](reference/corpus.md): 60 Wikipedia articles on deep learning, 30 in English and 30 in German, indexed by the [markdown connector](connectors/markdown.md) as two sources. The 100 questions are in [`corpus/questions.toml`](https://github.com/Marceltov/passageway/blob/main/corpus/questions.toml): 70 have accepted answers and 30 do not, and none of them names a language or a source, because one `recall` searches every source. [Measure retrieval quality](guides/evaluate.md) explains the metrics and the options.

Reproduce a run with `corpus/measure.sh` (it needs the embedding model, see [Install](install.md)). The block below is written by that script, and every run adds a line to the history.

## How to read this

- Every rate carries its 95% interval in brackets. With 70 answerable questions a rate of 85% could really be anywhere from about 75% to 92%; with 30 unanswerable questions silence has a similar width, and a group of 13 to 20 questions is only a hint. A difference between two runs that stays inside the intervals has not been shown to exist.
- The **relevance threshold** decides when a passage is similar enough to be returned. A passage that shares three or more words with the question passes whatever the threshold, so raising it silences loosely worded questions (the near-topic and off-topic groups) but not questions that share words with the corpus. The tables show the whole sweep, not only the best row.
- The questions were drafted with an AI assistant and every accepted answer was checked against the text of the articles before the first run. A question that proves wrong is corrected in its own commit.
- It is one embedding model (multilingual-e5-small, quantised), one small corpus and one machine. Wikipedia text on deep learning is a friendly domain: do not read these numbers as what your own notes will score. Measure those with your own questions.

<!-- passageway:results:start -->
2026-10-29 · passageway 0.1.0 · multilingual-e5-small-int8 (384 dimensions) · relevance threshold 0.845

Darwin arm64, Python 3.14.3 · index built in 21.2 s (corpus-en: 30 items, 818 sections, corpus-de: 30 items, 516 sections)

| Metric | Value |
|---|---|
| Questions | 100 (70 answerable, 30 unanswerable) |
| Hit@1 | 70.0% (58–80%) |
| Hit@3 | 80.0% (69–88%) |
| MRR | 0.748 |
| Silence on unanswerable questions | 80.0% (63–90%) |
| False silence on answerable questions | 1.4% (0–8%) |
| Latency p50 / p95 | 10.3 ms / 14.4 ms |
| Embedding the question | 3.4 ms (33.8% of the latency) |

In brackets: the 95% interval the true rate lies in, given this many questions. A difference between two runs that stays inside the intervals is not a difference.

### Relevance threshold

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.8 | 71.4% | 85.7% | 0.783 | 46.7% | 0.0% | 14.9 ms |
| 0.81 | 71.4% | 85.7% | 0.783 | 53.3% | 0.0% | 14.7 ms |
| 0.82 | 71.4% | 85.7% | 0.783 | 63.3% | 0.0% | 15.2 ms |
| 0.83 | 70.0% | 84.3% | 0.771 | 73.3% | 0.0% | 14.6 ms |
| 0.84 | 70.0% | 80.0% | 0.750 | 80.0% | 0.0% | 14.4 ms |
| 0.85 | 67.1% | 77.1% | 0.719 | 83.3% | 5.7% | 14.5 ms |
| 0.86 | 62.9% | 71.4% | 0.671 | 90.0% | 8.6% | 14.8 ms |
| 0.87 | 60.0% | 68.6% | 0.643 | 90.0% | 11.4% | 15.4 ms |
| 0.88 | 60.0% | 68.6% | 0.643 | 93.3% | 14.3% | 14.6 ms |
| 0.89 | 57.1% | 64.3% | 0.607 | 93.3% | 17.1% | 14.4 ms |
| 0.9 | 47.1% | 52.9% | 0.500 | 93.3% | 27.1% | 15.1 ms |

A passage that shares three or more words with the question is returned whatever the threshold (see How it works), so a high threshold only silences short or loosely worded questions.

### Groups

| Group | Questions | Hit@3 | Silence |
|---|---|---|---|
| definition | 20 | 100.0% (84–100%) | n/a |
| how-why | 19 | 94.7% (75–99%) | n/a |
| paraphrase | 18 | 55.6% (34–75%) | n/a |
| cross-language | 13 | 61.5% (36–82%) | n/a |
| near-topic | 15 | n/a | 60.0% (36–80%) |
| off-topic | 15 | n/a | 100.0% (80–100%) |

### History

| Date | Embedder | Threshold | Questions | Hit@3 | Silence | p95 |
|---|---|---|---|---|---|---|
| 2026-10-29 | multilingual-e5-small-int8 | 0.845 | 100 | 80.0% | 80.0% | 14.4 ms |
<!-- passageway:results:end -->

## Notes on the first run (29 October 2026)

Written by hand after the first run of `corpus/measure.sh`, so it does not change when the block above is rewritten. It is the baseline that the work on embedding models is measured against.

- **Plain questions work; reworded ones often do not.** All 20 definition questions and 18 of 19 how-and-why questions found an accepted article in the top three, but only 10 of 18 paraphrased ones did ("a network that squeezes its input into a small code and then rebuilds it" did not find the autoencoder article).
- **Crossing the language is uneven.** German questions found their English article in 6 of 8 cases, English questions found their German article in 2 of 5. With so few questions this is a hint, not a result.
- **Off-topic questions are always silent; near-topic ones are not.** All 15 off-topic questions returned nothing, but 6 of 15 near-topic ones returned a passage: a technique the corpus does not cover still finds a passage that shares words with it (a question about gradient boosting finds the vanishing gradient problem).
- **The default threshold sits where the two curves cross.** At 0.845 hit@3 and silence are both 80%. Each step of 0.01 in the sweep trades 3 to 7 points of one for 3 to 7 points of the other, which is inside the intervals. The sweep gives no reason to change the default; it does not show that 0.845 is the best value.
- **Latency:** about 10 ms at the median and 14 ms at the 95th percentile on an Apple-silicon laptop, a third of it for embedding the question.
- **Strict on purpose:** a hit counts only if it is one of the listed articles. Some hits at rank 2 or 3 would satisfy a reader too (a question about residual connections is answered well by the vanishing gradient article), so hit@1 is a hard measure.
