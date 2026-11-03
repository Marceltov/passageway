# passageway-connector-sitemap

A [passageway](https://github.com/Marceltov/passageway#readme) connector that indexes a website from its sitemap: a product's public documentation, a help centre, a company site. It reads `sitemap.xml`, fetches every page and, if you let it, follows the links on those pages to the ones the sitemap forgot.

## What it does

- **Each page is one item.** Its id is the page address and its version is a hash of the extracted text, so an edit re-indexes only that page. The main content of the page is kept (`<main>`, else `<article>`, else the body); navigation, headers, footers, scripts and forms are left out, and headings become sections.
- **A site address means its sitemap.** `https://docs.example.org` is read as `https://docs.example.org/sitemap.xml`. A sitemap index (a sitemap that lists sitemaps) is followed.
- **It follows links, on the same host only.** A link on an indexed page to another page of the site, one the sitemap did not list, is indexed too. Turn that off with `FOLLOW_LINKS`. Links to other hosts are never followed.
- **The folders of the address become the breadcrumb,** and the links between indexed pages become related items.
- **It is polite.** It reads `robots.txt` and skips what it forbids, waits between requests, identifies itself, and stops at a page limit.
- **A page that is gone is skipped, a server that fails stops the sync.** A `404` or a file that is not HTML is skipped with a warning. A `5xx`, a `429` or a network error fails the whole listing, so a site that is down for a minute never deletes what was indexed before.

## Install

Add the connector to the environment that runs passageway (see [Install](https://github.com/Marceltov/passageway/blob/main/docs/install.md)):

```bash
uv tool install \
  --with 'passageway-connector-sitemap @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/sitemap' \
  git+https://github.com/Marceltov/passageway
```

## An example

A page `https://docs.example.org/guide/setup`:

```html
<html><head><title>Setup | Example</title></head>
<body><nav>Home Docs</nav>
<main><h1>Setup</h1><p>Install it.</p><h2>Linux</h2><p>Use the package manager.</p></main>
<footer>Copyright</footer></body></html>
```

becomes the item:

```json
{
  "title": "Setup",
  "path": ["guide"],
  "sections": [
    {"heading": null, "text": "Install it."},
    {"heading": "Linux", "text": "Use the package manager."}
  ]
}
```

and is configured as:

```toml
[[connector]]
name = "docs"
command = ["/path/to/python", "-m", "passageway_connector_sitemap"]
env = { SITEMAP = "https://docs.example.org", EXCLUDE = "https://docs.example.org/blog/" }
```

## Settings

All settings are strings in the connector's `env`.

| Setting | Meaning | Default |
|---|---|---|
| `SITEMAP` | Required. Site addresses or sitemap addresses, separated by `\|`. Their hosts are the only ones crawled. | |
| `FOLLOW_LINKS` | `true` or `false`: also index pages that the sitemap does not list but an indexed page links to. | `true` |
| `INCLUDE` | Address prefixes, separated by `\|`: only addresses that start with one are indexed. | all |
| `EXCLUDE` | Address prefixes, separated by `\|`, that are never indexed. | none |
| `MAX_PAGES` | The most pages indexed. The rest are skipped with a warning. | `500` |
| `PAUSE` | Seconds to wait between requests. | `0.2` |
| `RESPECT_ROBOTS` | `true` or `false`: skip what `robots.txt` forbids for this crawler. | `true` |
| `RENDER` | `true` or `false`: open every page in a headless browser first, for sites whose pages a script builds. Needs `passageway-connector-sitemap[render]` and `playwright install chromium`. | `false` |
| `CONTACT` | An address or URL added to the user agent, so a site's owner can reach you. | none |

A page that a script builds in the browser has little text in what the server sends: Teamscale's documentation pages, for one, hand back a one-line notice. Set `RENDER = "true"` and the connector opens each page in a headless Chromium and reads what the script built (slower, and it needs the `render` extra and the browser, about 150 MB, downloaded once by `playwright install chromium`). If the site publishes an `llms-full.txt` or `llms.txt`, the [llms.txt connector](https://passageway.marceltov.de/connectors/llmstxt/) is faster and needs no browser.

Requests carry the user agent `passageway-connector-sitemap`, follow redirects and verify HTTPS against the operating system's trust store. Only crawl sites you may index.
