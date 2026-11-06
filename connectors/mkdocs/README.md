# passageway-connector-mkdocs

A [passageway](https://github.com/getpassageway/passageway#readme) connector that indexes a website built with [MkDocs](https://www.mkdocs.org/) or [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/): someone else's documentation, when you have the site but not its repository. It reads the site's search index, the file its search box uses, so it needs no crawling, and every hit opens the page at its heading.

## What it does

- **Each section of the search index is one item.** A built MkDocs site publishes `search/search_index.json`, with an entry for every page and every heading in it. Each entry with text becomes an item whose address is the page at that heading (`https://docs.example.org/guide/setup/#linux`), so a hit lands on the passage, not at the top of a long page. The text before a page's first heading is an item of its own at the page's address.
- **The page title is the item's title, the heading is its section,** and the folders of the address are its breadcrumb (`path`), so a `path:` filter works.
- **The id is the address, the version a hash of the text,** so an edit re-indexes only the sections it touched.
- **A site address means its search index.** `https://docs.example.org` is read as `https://docs.example.org/search/search_index.json`; a site under a path (`https://user.github.io/project`) works the same, and the index's own address can be given too.
- **Both search plugins are understood.** Material for MkDocs writes HTML into the index, which becomes text with code blocks and lists kept. MkDocs' own search plugin writes plain text and repeats the whole page in the page's entry; only the part before the first heading is kept there, so a passage is not indexed twice.
- **Any failure fails the whole listing.** A site without a search index, an index that is not one, a server that is down: the sync stops with a message that names the address, so a half-read site never deletes what was indexed before.

When the site publishes an `llms-full.txt` (the `mkdocs-llmstxt` plugin writes one), the [llms.txt connector](https://getpassageway.com/connectors/llmstxt/) reads the markdown itself; when you have the repository, the [Markdown connector](https://getpassageway.com/connectors/markdown/) does. This connector is for the site as it is published.

## Install

Add the connector to the environment that runs passageway (see [Install](https://github.com/getpassageway/passageway/blob/main/docs/install.md)):

```bash
uv tool install --python 3.14 "passageway[mkdocs]"
```

## An example

A site `https://docs.example.org` whose `search/search_index.json` is:

```json
{"docs": [
  {"location": "guide/setup/", "title": "Setup", "text": "<p>How to set it up.</p>"},
  {"location": "guide/setup/#linux", "title": "Linux", "text": "<p>Use the <code>apt</code> package.</p>"}
]}
```

gives, for the second entry, the item:

```json
{
  "id": "https://docs.example.org/guide/setup/#linux",
  "title": "Setup",
  "url": "https://docs.example.org/guide/setup/#linux",
  "path": ["guide", "setup"],
  "sections": [
    {
      "heading": "Linux",
      "text": "Use the apt package."
    }
  ]
}
```

and is configured as:

```toml
[[connector]]
name = "vendor-docs"
command = ["/path/to/python", "-m", "passageway_connector_mkdocs"]
env = { URLS = "https://docs.example.org|https://user.github.io/project", WEIGHTS = "changelog=0.5" }
```

## Settings

All settings are strings in the connector's `env`.

| Setting | Meaning | Default |
|---|---|---|
| `URLS` | Required. Site addresses, or the addresses of their `search_index.json`, separated by `\|`. | |
| `MAX_BYTES` | The largest search index that is read, in bytes. A larger one fails the sync. | `50000000` |
| `WEIGHTS` | Lowers or raises the weight of the sections whose path starts with a prefix: `changelog=0.5,blog/=0.3` (comma-separated `prefix=weight`, the weight above 0, the first match wins). Release notes repeat the vocabulary of how-to pages and push them down the results; a weight below 1 ranks them lower. The path is the page's address without the site's own. | all sections 1.0 |

Requests carry the user agent `passageway-connector-mkdocs`, follow redirects and verify HTTPS against the operating system's trust store.
