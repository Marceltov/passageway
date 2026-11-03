# passageway-connector-llmstxt

A [passageway](https://github.com/Marceltov/passageway#readme) connector that indexes the `llms-full.txt` of a list of websites, a single markdown file such as a `SKILL.md`, or the pages an `llms.txt` index links to. Most documentation sites publish one of these for language models, and this connector makes them searchable without crawling.

## What it does

- **Each top-level heading is one item.** A `llms-full.txt` that concatenates a whole site becomes one item per page, with the sections below each heading as passages. Its id is the file's address plus the heading (`https://docs.example.org/llms-full.txt#install`), and its version is a hash of the text, so an edit re-indexes only that page. A `#` inside a code block is not a heading, and front matter at the top of a file is not indexed.
- **A site address reads its `llms-full.txt`.** `https://docs.example.org` is read as `https://docs.example.org/llms-full.txt`.
- **A file address is read as it is:** `https://docs.example.org/llms-full.txt`, `https://passageway.marceltov.de/SKILL.md`, any markdown or text file.
- **An `llms.txt` index is followed.** Every link in it that stays on the same host is fetched and indexed as a file of its own. Links to other hosts are not followed.
- **Any failure fails the whole listing.** A page that returns an error or is not UTF-8 text stops the sync with a message that names it, so a half-read site never deletes what was indexed before.

## Install

Add the connector to the environment that runs passageway (see [Install](https://github.com/Marceltov/passageway/blob/main/docs/install.md)):

```bash
uv tool install \
  --with 'passageway-connector-llmstxt @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/llmstxt' \
  git+https://github.com/Marceltov/passageway
```

## An example

A file `https://docs.example.org/llms-full.txt`:

```markdown
# Install

Run the installer.

## Linux

Use the package manager.
```

becomes the item:

```json
{
  "title": "Install",
  "sections": [
    {"heading": null, "text": "Run the installer."},
    {"heading": "Linux", "text": "Use the package manager."}
  ]
}
```

and is configured as:

```toml
[[connector]]
name = "docs"
command = ["/path/to/python", "-m", "passageway_connector_llmstxt"]
env = { URLS = "https://docs.example.org|https://passageway.marceltov.de/SKILL.md" }
```

## Settings

All settings are strings in the connector's `env`.

| Setting | Meaning | Default |
|---|---|---|
| `URLS` | Required. Site addresses, file addresses and `llms.txt` addresses, separated by `\|`. | |
| `MAX_BYTES` | The largest file that is read, in bytes. A larger one fails the sync. | `20000000` |
| `MAX_PAGES` | The most pages followed from one `llms.txt` index. The rest are skipped with a warning. | `500` |

Requests carry the user agent `passageway-connector-llmstxt`, follow redirects and verify HTTPS against the operating system's trust store.
