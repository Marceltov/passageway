# passageway-connector-markdown

A [passageway](https://github.com/Marceltov/passageway#readme) connector that turns a folder of markdown files into searchable items: a docs folder, an Obsidian vault, a Jekyll or Hugo site, or the articles of the frozen Wikipedia corpus.

## What it does

- **Each markdown file is one item.** Its id is the path relative to the folder (or an `id` in its front matter) and its version is a hash of the file, so an edit re-indexes just that note.
- **Front matter gives the metadata:** title, address, date, tags, id and weight (see the table below).
- **Headings become sections.** Every heading level starts a section whose heading is the trail of its parents, such as `Setup › Linux`, so a hit says where in the note it is.
- **Folders become the breadcrumb**, and **links between notes become related items:** `[text](other.md)` and `[[Other]]`.
- **Files that cannot be indexed are skipped, not fatal.** A file that is not UTF-8 text, holds binary data or is too big is skipped with a warning on stderr, and the rest of the folder is indexed.

## Install

Add the connector to the environment that runs passageway (see [Install](https://github.com/Marceltov/passageway/blob/main/docs/install.md)):

```bash
uv tool install \
  --with 'passageway-connector-markdown @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/markdown' \
  git+https://github.com/Marceltov/passageway
```

## An example

A note `ops/rotating-certificates.md`:

```markdown
---
title: Rotating certificates
tags: [ops, security]
url: https://wiki.example.org/ops/certs
---
# Rotating certificates

Rotate the signing certificate every year.

## Steps

1. Create the new certificate.
2. Follow [the deploy guide](deploy.md).
```

becomes this item (shortened):

```json
{"id": "ops/rotating-certificates.md", "title": "Rotating certificates",
 "url": "https://wiki.example.org/ops/certs", "path": ["ops"], "labels": ["ops", "security"],
 "links": ["ops/deploy.md"],
 "sections": [{"heading": null, "text": "Rotate the signing certificate every year."},
              {"heading": "Steps", "text": "1. Create the new certificate.\n2. Follow [the deploy guide](deploy.md)."}]}
```

## Configure

In `passageway.toml` (use the interpreter that has passageway installed, see [Install](https://github.com/Marceltov/passageway/blob/main/docs/install.md)):

```toml
[[connector]]
name = "notes"
command = ["/path/to/python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "/Users/you/notes", EXCLUDE = "drafts/**|*.draft.md" }
```

| Setting | Default | Meaning |
|---|---|---|
| `FOLDER` | required | The folder to index, including its subfolders |
| `INCLUDE` | `*.md\|*.markdown` | Glob patterns for the files to index, separated by `\|`. `*` stays within a folder, `**` crosses folders, and a pattern without `/` matches the file name at any depth. Replaces the default |
| `EXCLUDE` | | Glob patterns for files to leave out, the same syntax |
| `MAX_FILE_BYTES` | `1048576` | Files larger than this are skipped with a warning. The core accepts at most 4 MiB per item line and the output escapes non-ASCII text, which can triple its size, so keep this at or below 1 MiB unless your notes are plain ASCII |

Always skipped: hidden files and folders (names starting with `.`, such as `.git` and `.obsidian`) and `node_modules`. Symlinked folders are not followed, and a symlinked file counts only if it points inside `FOLDER`.

## Front matter

A file may start with a YAML block between `---` lines. These keys are read; everything else is ignored.

| Key | Used for |
|---|---|
| `title` | The title. Without it: the first `# heading`, then the file name |
| `url` | The address shown with a hit. Without it: the `file://` address of the file |
| `updated` | The date shown with a hit. Without it: the file's modification time |
| `tags` | Labels. A list, or a comma-separated string |
| `id` | A stable id that survives renames and moves. Without it: the relative path. Two files with the same id fail the call and the message names both |
| `weight` | A multiplier for ranking, from 0 to 2 (default 1) |

All values are read as text, so `no` stays `no` and `2026-10-28` stays a date string. Front matter that is not valid YAML is reported on stderr and the file is indexed without it.

## Behavior

- **Sections:** every heading level (`#` to `######`) starts a section whose heading is the trail of its parents. Text before the first heading is its own section. The first `# heading` is the title (when the front matter has no title, or the same one) and is not repeated; a different `# heading` stays a section heading. A `#` inside a fenced code block is not a heading.
- **Links:** `[text](other.md#part)` and `[[Other]]` or `[[Other|text]]` become related items when they point at a note in the folder. Wiki links match the file name without case; a name shared by two files links to neither. Links in code are ignored, and the text itself is not changed.
- **Version:** a hash of the whole file and of the notes it links to, so any change to the file, front matter included, and a link that starts to resolve (its target was created) re-indexes the note.
- **Bad files:** a file that is not UTF-8 text (a BOM is removed), contains binary data or is over `MAX_FILE_BYTES` is skipped with a warning on stderr, not an error.
- **`changed`:** notes modified or moved in since the given time, from the later of each file's modification and change time, so edits appear within a minute, also for files copied in with their old dates.
- **Cost:** every call reads the whole folder, because ids and links need all the notes. A skipped file is reported on every call.

## Not supported

- Headings underlined with `===` or `---` (setext); only `#` headings split. A `#` line inside an HTML comment still counts as a heading.
- Glob character classes (`[ab]`) and braces (`{a,b}`); `*.md` is case sensitive, so `NOTE.MD` is not found without `INCLUDE=*.MD`. A pattern with a `/` is anchored at `FOLDER`, so `drafts/**` matches only the top-level `drafts`; use `**/drafts/**` for any depth.
- Reference-style links (`[text][ref]`) and brackets inside link text.
- File names in a different Unicode form than the link (`Café` typed with a combining accent).

## Test

```bash
uv sync                                  # installs this connector too
uv run pytest connectors/markdown        # offline, on temporary folders
```
