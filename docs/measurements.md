# Measurements

How well passageway finds the right passage and stays silent when there is none, measured with `passageway eval` on the [sample corpus](reference/corpus.md): 60 Wikipedia articles on deep learning, 30 in English and 30 in German, indexed by the [markdown connector](connectors/markdown.md) as two sources. The 100 questions are in [`corpus/questions.toml`](https://github.com/Marceltov/passageway/blob/main/corpus/questions.toml): 70 have accepted answers and 30 do not, and none of them names a language or a source, because one `recall` searches every source. [Measure retrieval quality](guides/evaluate.md) explains the metrics and the options.

Reproduce a run with `corpus/measure.sh` (it needs the embedding model, see [Install](install.md)). The block below is written by that script, and every run adds a line to the history.

## How to read this

- Every rate carries its 95% interval in brackets. With 70 answerable questions a rate of 85% could really be anywhere from about 75% to 92%; with 30 unanswerable questions silence has a similar width, and a group of 13 to 20 questions is only a hint. A difference between two runs that stays inside the intervals has not been shown to exist.
- The **relevance threshold** decides when a passage is similar enough to be returned. A passage that shares three or more words with the question passes whatever the threshold, so raising it silences loosely worded questions (the near-topic and off-topic groups) but not questions that share words with the corpus. The tables show the whole sweep, not only the best row.
- The questions were drafted with an AI assistant and every accepted answer was checked against the text of the articles before the first run. A question that proves wrong is corrected in its own commit.
- It is one embedding model (multilingual-e5-small, quantised), one small corpus and one machine. Wikipedia text on deep learning is a friendly domain: do not read these numbers as what your own notes will score. Measure those with your own questions.

<!-- passageway:results:start -->
<!-- passageway:results:end -->
