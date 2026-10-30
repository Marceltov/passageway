---
name: passageway-evaluate
description: "Measure how well passageway finds the right passage in the user's own sources and stays quiet when nothing fits: a guided question workshop that writes cases.toml, passageway eval on a reused index, the two numbers explained with their interval, a threshold sweep when the gate is off, and a comparison of the embedding models on request. Use when the user asks how good recall is, wants to tune the threshold, pick a model, or check after adding a source."
---

# Evaluate passageway on the user's own questions

Retrieval quality is measured, never guessed (https://passageway.marceltov.de/guides/evaluate/). This skill makes that measurement a conversation: it explains what it is doing and why before every step, builds the questions with the user, and reads the result back in plain words.

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. The page for this skill is https://passageway.marceltov.de/guides/evaluate/: fetch it before the first run and whenever an option below does not behave as described.

Free text (a question, a note's title, a path) is asked in the chat, never through a choice prompt; a choice prompt is only for real alternatives (which mode, which model).

## Say this first

Before any command, in these four lines, in the user's language:

- **What:** it asks your sources questions you would really ask and checks two things: does the right note come up among the top three (**hit@3**), and does it stay quiet when your notes have nothing (**silence**).
- **Why:** those two numbers say whether the relevance gate and the model fit *your* notes; without them a change to either is a guess.
- **When:** once now, with your real sources in; again after adding a big source, and before changing the model or the threshold. Every run adds a line to a history, so a regression shows.
- **How:** you give questions your notes answer and some they do not, we confirm the right note for each, and the run takes a few minutes on a throwaway index. Nothing leaves your machine, and the report quotes none of your notes.

## Determine the mode

**First run** (no `~/.config/passageway/cases.toml` yet), **rerun** (the file exists), **more questions** (grow the file), **tune the threshold**, or **compare models**. Ask only when it is not clear from what the user said.

## Where it runs

`passageway eval` runs where the connectors can reach the sources and reads the same `passageway.toml` and model as the server (`PASSAGEWAY_CONFIG`, `PASSAGEWAY_MODEL_DIR`); no server, token or password is needed. A local install from `/passageway-install` is ready as it is. For a container, put the cases file next to the config mount and run `docker exec pw passageway eval /config/cases.toml --data-dir /data/eval-index`.

## First run: the question workshop

The questions must be the user's own, so the number means something; the skill drives the work of finding them. Keep the file at `~/.config/passageway/cases.toml` (it holds the user's questions and note titles: it stays on the machine, it is not a report).

1. **Real questions first.** Ask for the last five things the user looked up in their notes, or asked Claude that the notes could have answered. These are the best cases.
2. **Topic-led questions.** List the areas of the sources: for Trilium the top-level notes under its wiki root (through a Trilium MCP server if one is registered, else from the titles that a few broad `recall` calls return), for a markdown source the folder names, for Confluence the space keys in the config, for Wikipedia the categories. For each area, draft one or two questions **from the title only**, worded the way the user would ask *before* reading the note, and let the user accept, edit or drop each. The area becomes the `group`, so the report scores per area. Never copy a phrase from a note's body into a question: a passage that shares **three words** with the question is returned by the keyword rescue whatever its similarity, so such a question measures nothing. Mix short and long questions, and both languages when the notes are bilingual (a short question is what the threshold acts on).
3. **Unanswerable questions, two kinds.** Far ones ("what is on the cafeteria menu") and **near-misses**: a sibling topic the user keeps no notes on, proposed next to each area ("you have notes on Kubernetes; nothing on Nomad?"). Near-misses are what tests the gate. A case without `expect` is one the index must stay silent on.
4. **Confirm each answerable question** through the `recall` tool (the MCP server `passageway`): show the title of the first hit and ask whether that is the right note. A yes becomes `expect = ["<title>"]` (a part of the title, heading or address; case does not matter; a title that exists in two languages matches with one entry). A no: ask for the note's title and file that; the run will show whether it is found at all. `expect_id` is for a title that is ambiguous.
5. **Size.** Aim for 10 answerable and 5 unanswerable on day one, 30 and 10 over time. Say what the interval is at the current size: with 10 questions a rate of 80% has an interval of roughly 50–95%, a hint, not a number; with 30 about ±15 points; with 100 about ±7.
6. Write the file and check it parses (`python3 -c 'import tomllib,sys; tomllib.load(open(sys.argv[1],"rb"))' <file>`):

   ```toml
   [targets]            # what a rerun is held to; start from the first run's numbers, not from a wish
   hit_at_3 = 0.8
   silence = 0.8

   [[case]]
   query = "how do I rotate the API token for the build server"
   expect = ["Build server"]
   group = "ops"

   [[case]]
   query = "what is on the cafeteria menu"      # no expect: must stay silent
   ```

## Run it and read it

```bash
passageway eval ~/.config/passageway/cases.toml --data-dir ~/.config/passageway/eval-index --write ~/.config/passageway/measurements.md
```

`--data-dir` keeps the index between runs, so a rerun after editing questions is quick (an index built with another model is refused: delete the folder then). `--write` keeps the history: create the page once with the two markers `<!-- passageway:results:start -->` and `<!-- passageway:results:end -->` on lines of their own; every run appends to the table of the last ten, with date, model, threshold and the numbers. Never point `--data-dir` at the server's live data folder.

Read the report back in plain words, two numbers first: **hit@3** and **silence**, each with its 95% interval, and the one line about the interval's width at this size. Then what to do:

- **hit@3 low, or false silence above 0:** run again with `--include-cases` and look at the misses (it quotes the user's notes, so show it to the user only, never write it to a page). A note that is not found at all is not indexed (the source is missing, or the file is skipped: the server log says) or the `expect` names the wrong title. A note found at rank 4 or 5 is a threshold or wording question.
- **silence low:** noise reaches the model; the gate is too loose for this model and these notes: tune the threshold.
- **both good:** say so, and when to run again (after a big source, before a model change).

## Tune the threshold

```bash
passageway eval ~/.config/passageway/cases.toml --data-dir ~/.config/passageway/eval-index --sweep 0.80,0.82,0.84,0.86,0.88
```

The sweep is cheap (one index, many thresholds). Show the table and where silence and false silence cross; the gate goes where false silence is still 0 and silence is highest. A long question is found at any threshold (the keyword rescue), so only the short unanswerable ones move. To apply: set `min_similarity = <value>` under `[embedder]` in `passageway.toml` and restart the service (`launchctl kickstart -k gui/$(id -u)/de.marceltov.passageway`, `systemctl --user restart passageway`, or `docker compose restart passageway`), then rerun once so the history has the new gate.

## Compare models

Only on request, or when no threshold satisfies both numbers. Say the cost first: each candidate needs its own download (about 0.5 GB per preset, once) and its own index, so this takes minutes and the machine is busy meanwhile. Add the candidates as `[embedders.NAME]` tables to `passageway.toml` (the server ignores them; `passageway model list` shows the presets with their measured gates):

```toml
[embedders.e5-base]
model = "multilingual-e5-base"

[embedders.jina-de]
model = "jina-v2-base-de"
```

```bash
passageway eval compare ~/.config/passageway/cases.toml --write ~/.config/passageway/measurements.md
```

Each candidate runs with its own fresh index at its own gate, because similarity scales differ between models and one shared threshold would favour whichever model it suits. Read the rows back: hit@3 and silence with intervals, index time, latency. Recommend one only when its numbers are outside the other's interval; otherwise say the questions cannot tell them apart yet and the smaller model wins. To apply: `model = "<preset>"` under `[embedder]`, restart as above, delete `~/.config/passageway/eval-index` (it was built with the old model), rerun.

## Rerun

The same command as the first run. Compare with the history table and say what moved and why it could have (a new source, a model, a threshold, more questions). A regression after adding a source is usually that source's noise: a silence drop with its group's questions still found.
