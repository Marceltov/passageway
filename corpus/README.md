# The sample corpus

A small, fixed set of Wikipedia articles on **deep learning**, 30 in English (`en/`) and 30 in German (`de/`), so that measurements of retrieval quality can be repeated by anyone against the same text. The articles are CC BY-SA 4.0, not AGPL: see [LICENSE.md](https://github.com/Marceltov/passageway/blob/main/corpus/LICENSE.md).

The files are the corpus. Each has front matter with its title, address, revision and licence, and its sections are `##` headings. Wikipedia changes every day, so nothing is fetched at test time: the revision in each file says which version it is. The [markdown connector](https://passageway.marceltov.de/connectors/markdown/) indexes a folder of them:

```toml
[[connector]]
name = "corpus-en"
command = ["/path/to/python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "/path/to/passageway/corpus/en" }
```

Use one connector per language folder (`en` and `de`). A question is then answered from both languages together, as it will be in real use.

## The articles

Chosen by hand: the core concepts of deep learning (backpropagation, convolutional and recurrent networks, attention and the transformer, regularisation, language models). The German list is not a translation of the English one, because several topics have no German article of their own; each folder's `ATTRIBUTION.txt` lists exactly what it holds.

## The questions and the measurements

`questions.toml` holds 100 questions for the corpus: 70 with accepted answers and 30 that nothing in the corpus answers, in English and German, none naming a language or a source. `measure.sh` runs them with `passageway eval` and updates the [measurements page](https://passageway.marceltov.de/measurements/); it needs the embedding model, and `measure.sh --no-write --include-cases --out DIR` shows every question without touching the page. The accepted answers are file names, so an answer such as `backpropagation.md` accepts the article of that name in both languages.

## Refreshing it

`snapshot.py` writes the files. It is a maintenance script, not part of the Wikipedia connector, and uses the connector as a library:

```bash
OUT=corpus/en LANGUAGE=en TITLES="$(paste -sd'|' corpus/en/titles.txt)" FORCE=1 uv run python corpus/snapshot.py
```

Each folder's `titles.txt` is the list of articles it holds, so this repeats the same selection. `FORCE=1` replaces the whole folder, and the new files are written next to it first, so a failed run leaves the old ones.

Its settings are the Wikipedia connector's (`LANGUAGE`, `TITLES`, `CATEGORIES`, `CATEGORY_DEPTH`, `SKIP_SECTIONS`, `CONTACT` and the others) plus `OUT` (the folder to write), `LIMIT` (keep only the N longest articles) and `FORCE=1` (overwrite existing files). A refresh fetches today's revisions, so it changes the corpus: do it deliberately and expect measurements to move.
