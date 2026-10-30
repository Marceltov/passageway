# passageway-connector-wikipedia

A [passageway](https://github.com/Marceltov/passageway#readme) connector that turns part of Wikipedia (or any MediaWiki site) into searchable items: a **topic** (categories), some **titles**, or a **place**. English and German are both tested; any language code works.

Each article is one item. Its id is the page id, its version is the revision id, and its sections follow the article's headings (`History › 19th century`). Boilerplate sections such as References or Einzelnachweise are left out.

## Configure

In `passageway.toml`, one `[[connector]]` per language (use the interpreter that has passageway installed, see [Install](https://github.com/Marceltov/passageway/blob/main/docs/install.md)):

```toml
[[connector]]
name = "deep-learning-en"
command = ["/path/to/python", "-m", "passageway_connector_wikipedia"]
env = { LANGUAGE = "en", CATEGORIES = "Deep learning", CATEGORY_DEPTH = "0" }

[[connector]]
name = "deep-learning-de"
command = ["/path/to/python", "-m", "passageway_connector_wikipedia"]
env = { LANGUAGE = "de", CATEGORIES = "Kategorie:Deep Learning" }

[[connector]]
name = "munich"
command = ["/path/to/python", "-m", "passageway_connector_wikipedia"]
env = { LANGUAGE = "de", GEO = "48.1372,11.5756,5000" }   # articles within 5 km of central Munich
```

| Setting | Default | Meaning |
|---|---|---|
| `LANGUAGE` | `en` | Wikipedia language code |
| `CATEGORIES` | | Categories, separated by `\|`. A bare name gets the `Category:` prefix; a name with a prefix (`Kategorie:...`) is used as given |
| `CATEGORY_DEPTH` | `1` | How many levels of subcategories to follow (`0` = only the listed categories) |
| `TITLES` | | Article titles, separated by `\|`; redirects are followed, missing pages are ignored |
| `GEO` | | `lat,lon,radius_in_meters`: articles about places near a point. The radius is limited to 10 to 10000 m by MediaWiki, so this suits a city or neighbourhood, not a region. For a region use `CATEGORIES` |
| `MAX_PAGES` | `500` | Upper bound on the scope. A bigger scope fails with a message instead of being cut off |
| `SKIP_SECTIONS` | English and German boilerplate | Headings to leave out, separated by `\|`; `none` keeps everything. A skipped heading also skips its subsections |
| `API_URL`, `PAGE_URL` | derived from `LANGUAGE` | Point at another MediaWiki site |
| `CONTACT` | | Added to the User-Agent; Wikimedia asks automated clients to identify themselves |
| `PAUSE_SECONDS` | `0.1` | Pause between requests |

At least one of `CATEGORIES`, `TITLES` or `GEO` is required.

## Behavior

- **Polite:** sequential requests with a descriptive User-Agent, `maxlag`, and back-off on 429 and 503.
- **Redirects:** redirect pages inside a category are left out; `TITLES` follow redirects to the real article.
- **Retries:** 429, 502, 503 and 504 answers, `maxlag` and network errors are retried with a growing wait (1 s, doubling up to 60 s; a longer `Retry-After` is honored up to 300 s) until a request has waited 15 minutes in total; the error then says how many attempts and how long it waited. Waiting out a long rate limit needs a core `timeout` above its default of 300 s.
- **No `changed` mode:** edits appear at the next reconcile (every 30 minutes by default).
- **Content license:** Wikipedia text is CC BY-SA 4.0. The link on each item points to the source article; its history page lists the authors.

## Test

```bash
uv sync                                                              # installs this connector too
uv run pytest connectors/wikipedia                                   # offline, against an in-test MediaWiki server
PASSAGEWAY_LIVE=1 uv run pytest connectors/wikipedia/tests/test_wikipedia_live.py   # real Wikipedia
```
