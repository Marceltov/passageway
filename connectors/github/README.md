# passageway-connector-github

A [passageway](https://github.com/getpassageway/passageway#readme) connector that indexes GitHub repositories: by default their documentation (the README and every markdown file), and their code when you ask for it. Name the repositories one by one, or every repository of a user or an organisation.

## What it does

- **Each file is one item,** read from the default branch (or the branch you name). Its id is the repository and the path (`acme/docs/guide/setup.md`), its address the file on github.com, and its version the file's git blob sha, so listing a repository costs one call and reads no file, and an edit re-indexes only that file.
- **Markdown files are cut at their headings.** The first `#` heading is the title (else the file name; a README at the top of the repository is titled by the repository), front matter is left out, and the repository and folders are the breadcrumb (`path`), so a `path:` filter works.
- **Code, when `FILES` asks for it, is cut into passages of 40 to 80 lines,** at a blank line where one comes, each headed by its line range (`Lines 41–96`). Files that are not UTF-8 text (images, archives) are skipped with a warning.
- **`owner/*` is every repository of a user or an organisation.** Forks and archived repositories are left out unless `FORKS` or `ARCHIVED` says otherwise. With a `TOKEN`, an organisation's private repositories are included where the token can read them, and so are the token owner's own.
- **Any failure fails the whole listing.** A repository that is missing or unreadable, a refused token, a used-up rate limit or a server that is down stops the sync with a message that says what to do, so a half-read repository never deletes what was indexed before. A rate limit names the time it resets.

Without a token GitHub allows 60 API calls an hour from one address: enough to list a few repositories, not to read many files. Indexing reads each file once (one call per file) and then only the files that changed, so give it a token for anything but a small public repository. A fine-grained personal access token with read access to *Contents* and *Metadata* of the repositories is enough.

## Install

Add the connector to the environment that runs passageway (see [Install](https://github.com/getpassageway/passageway/blob/main/docs/install.md)):

```bash
uv tool install --python 3.14 "passageway[github]"
```

## An example

A file `guide/setup.md` in `acme/docs`:

```markdown
# Setup

Install it.

## Linux

Use the package manager.
```

becomes the item:

```json
{
  "id": "acme/docs/guide/setup.md",
  "title": "Setup",
  "url": "https://github.com/acme/docs/blob/main/guide/setup.md",
  "path": ["acme/docs", "guide"],
  "sections": [
    {
      "heading": null,
      "text": "Install it."
    },
    {
      "heading": "Linux",
      "text": "Use the package manager."
    }
  ]
}
```

and is configured as:

```toml
[[connector]]
name = "github"
command = ["/path/to/python", "-m", "passageway_connector_github"]
env = { REPOS = "acme/docs|acme/api@release|ann/*" }
secrets = { TOKEN = "env:GITHUB_TOKEN" }
```

To index the code of a repository as well as its documentation:

```toml
env = { REPOS = "acme/api", FILES = "*.md|src/**/*.py", EXCLUDE = "src/**/test_*.py" }
```

## Settings

All settings are strings in the connector's `env`; `TOKEN` belongs in `secrets`.

| Setting | Meaning | Default |
|---|---|---|
| `REPOS` | Required. Repositories separated by `\|`: `owner/repo`, `owner/repo@branch` (the branch is then part of every id), or `owner/*` for every repository of a user or an organisation. | |
| `TOKEN` | A GitHub personal access token, as a secret reference. Needed for private repositories and for more than 60 API calls an hour. | none |
| `FILES` | The files to index, as glob patterns separated by `\|`, matched against the path in the repository: `**` crosses folders, `*` stays in one, and a pattern without `/` matches the file name in any folder. A file that does not end in `.md`, `.mdx` or `.markdown` is indexed as code. | `*.md\|*.mdx\|*.markdown` |
| `EXCLUDE` | Files to leave out, as glob patterns like `FILES`. | none |
| `FORKS` | `true` to include forks in `owner/*`. | `false` |
| `ARCHIVED` | `true` to include archived repositories in `owner/*`. | `false` |
| `MAX_FILES` | The most files indexed from one repository; the rest are skipped with a warning. | `5000` |
| `MAX_FILE_BYTES` | The largest file that is indexed, in bytes; larger ones are skipped with a warning. | `1000000` |
| `API_URL` | The REST API address, for GitHub Enterprise Server: `https://github.example.org/api/v3`. | `https://api.github.com` |

Requests carry the user agent `passageway-connector-github` and verify HTTPS against the operating system's trust store.
