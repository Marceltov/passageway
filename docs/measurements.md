# Measurements

How well passageway finds the right passage and stays silent when there is none, measured with `passageway eval` on the [sample corpus](reference/corpus.md): 60 Wikipedia articles on deep learning and neighbouring topics, 30 in English and 30 in German, indexed by the [markdown connector](connectors/markdown.md) as two sources. The 100 questions are in [`corpus/questions.toml`](https://github.com/Marceltov/passageway/blob/main/corpus/questions.toml): 70 have accepted answers and 30 do not, and none of them names a language or a source, because one `recall` searches every source. [Measure retrieval quality](guides/evaluate.md) explains the metrics and the options.

Reproduce a run with `corpus/measure.sh` (it needs the embedding model, see [Install](install.md)). The block below is written by that script. The history at the end of it gets one line per day, model, threshold and passageway version; a repeated run replaces its line.

## How to read this

- **Intervals.** The rates in the first and in the group table carry their 95% interval in brackets. With 70 answerable questions a rate of 85% could really be anywhere from about 75% to 92%; with 30 unanswerable questions a silence of 90% could be anywhere from about 74% to 97%, which is wider; a group of 7 to 25 questions is only a hint. The sweep and history tables show point values only. Overlapping intervals are a warning against over-reading a difference, not a test of it.
- **The threshold.** The relevance threshold decides when a passage is similar enough to be returned. A passage that shares three or more words with the question is returned whatever the threshold. Raising it therefore silences loosely worded questions, but it also loses real answers (false silence reaches 27% at 0.90), and two unanswerable questions are never silenced, because they share words with the corpus. The tables show the whole sweep, not only the best row.
- **The questions.** They were drafted with an AI assistant that had also chosen the corpus, and every accepted answer was checked against the text of the articles before the first run. An independent review after that run found accepted answers that were incomplete and six questions called cross-language that were not, because the other language explains the topic too. Those were corrected in a separate commit and the run was repeated; both are in the git history, and the notes below give the first run's figures. The accepted answers are file names, so one accepts the article of that name in both languages. A miss can still be a correct article that is not on the list.
- **The corpus.** The German list includes general articles; "Neuronales Netz", for example, is the neuroscience article. It is one embedding model (multilingual-e5-small, quantised), 60 articles and one machine. Wikipedia text on deep learning is a friendly domain: do not read these numbers as what your own notes will score. Measure those with your own questions.

<!-- passageway:results:start -->
2026-10-29 · passageway 0.1.0 · multilingual-e5-small-int8 (384 dimensions) · relevance threshold 0.845

Darwin arm64, Python 3.14.3 · index built in 20.9 s (corpus-en: 30 items, 818 sections, corpus-de: 30 items, 516 sections)

| Metric | Value |
|---|---|
| Questions | 100 (70 answerable, 30 unanswerable) |
| Hit@1 | 77.1% (66–85%) |
| Hit@3 | 88.6% (79–94%) |
| MRR | 0.826 |
| Silence on unanswerable questions | 80.0% (63–90%) |
| False silence on answerable questions | 1.4% (0–8%) |
| Latency p50 / p95 | 10.0 ms / 14.0 ms |
| Embedding the question | 3.4 ms (34.0% of the latency) |

In brackets: the 95% interval of a rate, the range that holds the true rate in 95 of 100 repetitions with other questions of the same kind. Overlapping intervals are a warning against over-reading a difference, not a test of it. The tables below show point values only.

### Relevance threshold

| Threshold | Hit@1 | Hit@3 | MRR | Silence | False silence | p95 |
|---|---|---|---|---|---|---|
| 0.8 | 78.6% | 90.0% | 0.840 | 46.7% | 0.0% | 13.9 ms |
| 0.81 | 78.6% | 90.0% | 0.840 | 53.3% | 0.0% | 14.2 ms |
| 0.82 | 78.6% | 90.0% | 0.840 | 63.3% | 0.0% | 13.6 ms |
| 0.83 | 77.1% | 88.6% | 0.829 | 73.3% | 0.0% | 14.1 ms |
| 0.84 | 78.6% | 88.6% | 0.833 | 80.0% | 0.0% | 14.3 ms |
| 0.845 | 77.1% | 88.6% | 0.826 | 80.0% | 1.4% | 13.8 ms |
| 0.85 | 72.9% | 84.3% | 0.783 | 83.3% | 5.7% | 13.7 ms |
| 0.86 | 70.0% | 77.1% | 0.736 | 90.0% | 8.6% | 13.5 ms |
| 0.87 | 67.1% | 74.3% | 0.707 | 90.0% | 11.4% | 13.9 ms |
| 0.88 | 65.7% | 72.9% | 0.693 | 93.3% | 14.3% | 14.1 ms |
| 0.89 | 62.9% | 68.6% | 0.657 | 93.3% | 17.1% | 13.9 ms |
| 0.9 | 51.4% | 57.1% | 0.543 | 93.3% | 27.1% | 13.9 ms |

A passage that shares three or more words with the question is returned whatever the threshold (see How it works), so a high threshold only silences short or loosely worded questions.

### Groups

| Group | Questions | Hit@3 | Silence |
|---|---|---|---|
| definition | 25 | 96.0% (80–99%) | n/a |
| how-why | 20 | 100.0% (84–100%) | n/a |
| paraphrase | 18 | 61.1% (39–80%) | n/a |
| cross-language | 7 | 100.0% (65–100%) | n/a |
| near-topic | 15 | n/a | 60.0% (36–80%) |
| off-topic | 15 | n/a | 100.0% (80–100%) |

### History

| Date | Embedder | Threshold | Questions | Hit@3 | Silence | p95 |
|---|---|---|---|---|---|---|
| 2026-10-29 | multilingual-e5-small-int8 | 0.845 | 100 | 88.6% | 80.0% | 14.0 ms |
<!-- passageway:results:end -->

## Notes on the runs (29 October 2026)

Written by hand, so it does not change when the block above is rewritten. The numbers above are the baseline for the work on embedding models.

- **The first run and the corrected one.** The first run, before the review, scored hit@3 80.0% (69–88%), hit@1 70.0% and MRR 0.748, with 8 of 13 cross-language questions found. The corrections added articles that really explain a topic to the accepted answers of 14 questions, regrouped 6 of the 13 cross-language questions, and replaced one unanswerable question whose topic the German overview describes (k-nearest neighbours became Metropolis-Hastings). Silence did not change.
- **Plain questions work; reworded ones less.** 24 of 25 definition questions and all 20 how-and-why questions found an accepted article in the top three, but only 11 of 18 paraphrased ones did ("a network that squeezes its input into a small code and then rebuilds it" did not find the autoencoder article).
- **The seven cross-language questions were all found,** but they are few, and several carry a word that is the same in both languages ("Residual Network", "Hyperparameter", "Boltzmann"), which helps a word-based match. Read it as "does not fail", not as a measure of cross-language retrieval.
- **Off-topic questions are always silent; near-topic ones are not.** All 15 off-topic questions returned nothing, but 6 of 15 near-topic ones returned a passage: a technique the corpus does not cover still finds a passage that shares words with it (a question about gradient boosting finds the vanishing gradient problem).
- **The threshold.** At the default 0.845, hit@3 is 88.6% and silence 80.0%. At 0.85 they are 84.3% and 83.3%, at 0.86 77.1% and 90.0%: from 0.84 to 0.86 hit@3 loses 11.5 points and silence gains 10. 0.84 gives the same hit@3 and silence as 0.845 and no false silence, a difference far inside the intervals. The sweep gives no reason to change the default; it does not show that 0.845 is the best value.
- **Latency:** about 10 ms at the median and 14 ms at the 95th percentile on a Darwin arm64 machine, a third of it for embedding the question.
- **Strict on purpose:** a hit counts only if it is one of the listed articles, so hit@1 is a hard measure. Some hits at rank 2 or 3 are arguably good answers that are not on the list.
