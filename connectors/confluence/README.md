# passageway-connector-confluence

A [passageway](https://github.com/Marceltov/passageway#readme) connector for **Confluence Data Center** (and Server): the current pages of the spaces you name, read through the REST API with GET requests only, using a personal access token. Written from the public REST documentation.

## What it does

- **Each page is one item.** Its id is the content id, its version changes with every page version and with its labels, and its link opens the page in Confluence.
- **Headings become sections:** `h1`, `h2` and `h3` split a page into passages with their heading trail (`Setup › Linux`); lists, tables and code macros are kept readable; long sections are cut at about 350 tokens.
- **Labels become labels** (`space:OPS` plus the page's own), **ancestors become the path** (nearest last, up to four), and every page weighs 1.0.
- **Macros:** code and noformat macros keep their text; boxes, expands, sections, columns, excerpts and every other macro with a body keep what they hold; a status macro keeps its title; a table of contents, Jira issues, images, emoticons and other macros without a body are left out. Task lists become lists. Links keep their text, or the linked page's title. Blog posts and attachments are not indexed.
- **Edits appear within a minute:** `changed` asks Confluence with CQL for the pages modified since the last poll (fourteen hours early, because CQL reads the time in the server's zone; unchanged versions cost nothing). Deletions, moves out of the spaces and labels that take a page out of scope are settled at the next reconcile. A space that lists no pages is reported as a warning, so a wrong key or a token without permission does not pass in silence.

## Configure

Create a personal access token under your profile in Confluence (Data Center and Server 7.9 and later). The connector only ever sends GET requests.

```toml
[[connector]]
name = "wiki"
command = ["/path/to/python", "-m", "passageway_connector_confluence"]
env = { URL = "https://wiki.example.org", SPACES = "OPS|HR" }
secrets = { TOKEN = "env:CONFLUENCE_TOKEN" }
```

| Setting | Default | Meaning |
|---|---|---|
| `URL` | required | The Confluence site, e.g. `https://wiki.example.org` (with its context path, if any) |
| `SPACES` | required | Space keys to index, separated by `\|` |
| `TOKEN` | required | A personal access token, as a secret reference such as `env:CONFLUENCE_TOKEN` |
| `INCLUDE_LABELS` | | Only pages carrying one of these labels, separated by `\|` |
| `EXCLUDE_LABELS` | | Pages carrying one of these labels are left out |
| `MAX_PAGES` | `5000` | Upper bound on the spaces together; more fails with a message instead of indexing a subset |
| `TIMEOUT` | `30` | Seconds per request |
| `PAUSE_SECONDS` | `0` | Pause between requests, for a busy server |
| `VERIFY_TLS` | `true` | `false` turns certificate checking off. A CA your operating system trusts already works without it (see [Certificates](https://passageway.marceltov.de/configuration/#certificates)), so prefer adding the CA there |

## Behaviour

- **Retries:** 429 and 5xx answers and network errors are retried with a growing wait (1 s, doubling up to 60 s; a longer `Retry-After` is honoured up to 300 s) until a request has waited 15 minutes in total; the error then says how many attempts and how long it waited. Every wait of 10 s or more is logged as it starts (`HTTP 429 … waiting 16 s (15 s of 900 s waited)`), so a sync that waits does not look hung. A 401 says to check the token; any other error fails the call and nothing is stored.
- **A throttled or large space** needs more than the core's default `timeout = 300` for the whole `list` or `fetch`: waiting out one rate limit can take minutes. Raise `timeout` in its `[[connector]]` entry (`3600` is a start), or set `PAUSE_SECONDS` so fewer requests are throttled in the first place.
- **Cloud:** Atlassian Cloud authenticates with an e-mail address and an API token and serves the API under `/wiki`; it is not supported yet ([ADR 0005](https://passageway.marceltov.de/adr/0005-confluence-data-center-first/)).
- **Tested against a fake** of the Data Center API in this repository, not against a live Confluence.

## Test

```bash
uv run pytest connectors/confluence        # offline, against an in-test Confluence
```
