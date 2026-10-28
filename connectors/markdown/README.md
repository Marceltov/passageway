# passageway-connector-markdown

A [passageway](https://github.com/Marceltov/passageway#readme) connector that turns a folder of markdown files into searchable items: a docs folder, an Obsidian vault, a Jekyll or Hugo site, or the articles of the frozen Wikipedia corpus.

Each file is one item. Its id is the path relative to the folder (or the `id` in its front matter), its version is a hash of the file, and its sections follow the headings (`Setup › Linux`). Folders become the breadcrumb, links to other notes become related items, and front matter gives the title, address, date and tags.

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
| `MAX_FILE_BYTES` | `1048576` | Files larger than this are skipped with a warning |

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

- **Sections:** every heading level (`#` to `######`) starts a section whose heading is the trail of its parents. Text before the first heading is its own section. The first `# heading` is the title and is not repeated. A `#` inside a fenced code block is not a heading.
- **Links:** `[text](other.md#part)` and `[[Other]]` or `[[Other|text]]` become related items when they point at a note in the folder. Wiki links match the file name without case; a name shared by two files links to neither. Links in code are ignored, and the text itself is not changed.
- **Version:** a hash of the whole file, so any change, front matter included, re-indexes the note.
- **Bad files:** a file that is not UTF-8 text (a BOM is removed), contains binary data or is over `MAX_FILE_BYTES` is skipped with a warning on stderr, not an error.
- **`changed`:** notes modified since the given time, from the files' modification times, so edits appear within a minute.
- **Cost:** every call reads the whole folder, because ids and links need all the notes.

## Test

```bash
uv sync                                  # installs this connector too
uv run pytest connectors/markdown        # offline, on temporary folders
```
