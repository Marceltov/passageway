# Measure retrieval quality

`passageway eval` asks your sources the questions you care about and reports how often the right passage comes back, and how often passageway correctly stays silent when nothing fits. Run it before you change the embedding model or the relevance threshold, and in CI to catch a regression. The numbers it prints are yours to publish: by default a report contains no question, no title and no address from your sources (it does carry the source names and group labels you chose, see below).

## Write the questions

A cases file is TOML. Each `[[case]]` is a question and the answers that count as right.

```toml
[targets]            # optional: what --enforce checks
hit_at_3 = 0.8
silence = 0.8
p95_ms = 300

[[case]]
query = "what is the vanishing gradient problem"
expect = ["Vanishing gradient problem"]

[[case]]
query = "wie funktioniert Backpropagation"
expect = ["Backpropagation"]          # matches the English and the German article
group = "german questions"

[[case]]
query = "what is on the cafeteria menu"   # no expect: nothing should be found
```

- **`expect`** lists texts that must be part of a hit's title, heading or address (case does not matter). Any one of them in any of the top three hits counts as a hit. A title that exists in two languages is matched by one entry.
- **`expect_id`** lists exact item ids, for a title that is ambiguous.
- **No `expect` at all** marks a question the index must stay silent about. Any hit counts against the silence score.
- **`group`** is an optional label; the report shows the scores per group.
- Questions never say which source to search, because `recall` searches all of them.

A typo in a key is an error (it would otherwise silently turn a question into one that must stay silent).

## Run it

```bash
passageway eval cases.toml
```

It reads your `passageway.toml` and the embedding model like the server does (`PASSAGEWAY_CONFIG` and `PASSAGEWAY_MODEL_DIR`), builds every source into a **throwaway index** so it measures a fresh build and never touches your live one, asks the questions in-process, and prints a report. No server, token or password is needed.

| Option | What it does |
|---|---|
| `--config PATH`, `--model-dir DIR` | Use another `passageway.toml`, or another folder for the default built-in model (a non-default preset keeps `<data dir>/models/<preset>` or its `model_dir`) |
| `--data-dir DIR` | Keep the index in `DIR` and reuse it on the next run, which is faster while you refine questions. An index built with another embedding model is refused. Do not point it at your server's live data folder: eval would sync that index while the server is using it |
| `--threshold X` | Use `X` as the relevance threshold (`min_similarity`) for this run |
| `--sweep 0.80,0.84,0.88` | Also run at each of these thresholds and show them side by side. The index is built once, so a sweep costs little. This is how you choose a threshold for a model |
| `--enforce` | Exit 1 when a value in `[targets]` is not met, for CI. A cases file that has no `[targets]` gives a warning and exit 0, because there is nothing to check |
| `--out DIR` | Write `report.json` (for machines) and `report.md` into `DIR` |
| `--write PAGE` | Update the block between `<!-- passageway:results:start -->` and `<!-- passageway:results:end -->` in your own page, and keep a history of runs next to it. The page is checked before the run, so a missing marker does not cost a measurement |
| `--include-cases` | Also report every question, what was found and its rank. This quotes your sources, so leave it off for anything you publish |

Exit codes: 0 for a finished run, 1 for `--enforce` below the targets or a source that failed to sync (a partial index would give misleading numbers), 2 for a bad cases file, option or configuration.

## Read the report

| Metric | Meaning |
|---|---|
| Hit@1, Hit@3 | Share of answerable questions whose first, or one of the first three, hits is accepted |
| MRR | Mean of 1 / rank of the first accepted hit; 1.0 means always first |
| Silence | Share of unanswerable questions for which nothing was returned. Low silence means noise reaches the model |
| False silence | Share of answerable questions for which nothing was returned. High means the threshold is too strict |
| Latency p50 / p95 | Time to answer, including embedding the question; the report also shows the embedding's share. A warm-up question is not counted |

Every rate is followed by its **95% interval** in brackets, for example `85.0% (77–91%)`: given this many questions, the true rate could lie anywhere in it (a Wilson interval; it is also in `report.json` under `intervals`). The interval is not symmetric near 0% and 100%. Two runs on the same questions are paired, so overlapping intervals can hide a real change: they warn against over-reading a difference, they do not test for one. The sweep and history tables show point values only. With 40 answerable questions a rate of 85% has an interval of about ±11 points, with 100 about ±7, and a group of 8 questions is only a hint.

A metric with no question behind it shows `n/a` and fails a target on it: with no unanswerable question, silence is not 100%, it is unknown.

Silence and false silence pull against each other as the threshold moves, and `--sweep` shows where they cross for your sources and your model.

One rule limits what a threshold can do: a passage that shares **three or more words** with the question is returned whatever its similarity (the keyword rescue in [How it works](../how-it-works.md)). A long, specific question therefore stays found at any threshold, and a sweep silences only short or loosely worded ones. Word your unanswerable questions the way a user would, not as strings of rare words, or they will not measure the threshold.

A target is compared with the value the report shows: two of three questions is 66.7%, which meets a target of 0.667.

## Publish the numbers

Put the two markers, each **on a line of its own**, in a page of your docs, say `docs/measurements.md`, and run:

```bash
passageway eval cases.toml --write docs/measurements.md
```

The block between the markers is replaced with the run, the metrics, the groups and the targets, followed by a table of the last ten runs. Markers inside a code block are ignored, so a page can explain them, and the page keeps its line endings. Running it again with the same date, model, threshold and passageway version replaces that run instead of adding one. The history lives in `docs/measurements.history.json` and belongs in version control.

The report records the date, the passageway version, the embedding model, the threshold, the number of items and sections per source (under the source names from your `passageway.toml`), the **group labels** you chose, and a machine line (operating system, processor architecture and Python version, so that latencies can be put in context). It never records a host name. The source names and group labels are your own words, so pick ones you are happy to publish.

To fail a CI job on a regression, put `[targets]` in the cases file and add `--enforce`.

## Compare embedding models

```bash
passageway eval compare cases.toml
```

runs the same questions once per embedder and puts them side by side. The candidates are the `[embedders.NAME]` tables of your `passageway.toml` (see [Configuration](../configuration.md#the-embedder)), and `default` is the `[embedder]` the server uses. Each candidate gets its **own fresh index** and runs at **its own `min_similarity`**, because similarity scales differ between models; comparing them at one shared threshold would favour whichever model that value happens to suit. The report names the threshold of each.

| Option | What it does |
|---|---|
| `--embedder NAME` | Compare only these candidates; repeat it. At least two are needed. Default: `default` and every `[embedders.NAME]` |
| `--config PATH`, `--model-dir DIR` | As for a single run |
| `--threshold X` | Use one threshold for every candidate instead of their own |
| `--sweep 0.80,0.84,0.88` | Also show every candidate at these thresholds, one table each |
| `--out DIR` | Write `report.json` (`"kind": "compare"`, one entry per candidate) and `report.md` |
| `--write PAGE` | Update the marked block of your page with the comparison, and add one history line per embedder |

Each row shows the model's name and dimensions, the **load** time (starting the model) and the **index** time (embedding every source), then the quality metrics with their intervals. Every embedder is started before the first index is built, so one that cannot start costs nothing; it also means they are all loaded at once for a moment. Exit codes: 0 for a finished comparison, 1 for a source that failed to sync or an embedder that failed on the questions, 2 for bad input or an embedder that cannot start. The comparison holds no question, title or address.

## Not yet

The [sample corpus](../reference/corpus.md) has a public set of 100 questions and the first [published measurements](../measurements.md), which show the whole sweep. The [roadmap](../roadmap.md) has the order of what comes next.
