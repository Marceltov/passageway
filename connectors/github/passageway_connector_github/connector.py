"""passageway connector for GitHub repositories: their markdown files and, when asked, their code."""

import base64
import re
import time
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import quote, urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError, first_h1, split_markdown, strip_front_matter
from passageway_sdk.settings import flag, globs, names, whole
from passageway_sdk.web import Reply, Retry, Web

DEFAULT_FILES = ("*.md", "*.mdx", "*.markdown")
MARKDOWN = (".md", ".mdx", ".markdown")
NAME = r"[A-Za-z0-9_.-]+"
SPEC = re.compile(rf"({NAME})/(\*|{NAME})(?:@(\S+))?")
PAGE = 100
CHUNK_MIN, CHUNK_MAX = 40, 80  # lines of code in a section: cut at a blank line once past the first, always at the second


@dataclass(frozen=True)
class Repo:
    key: str  # owner/name, or owner/name@branch when the branch was named: the start of every id
    full_name: str
    branch: str
    html_url: str


@dataclass(frozen=True)
class File:
    repo: Repo
    path: str
    sha: str

    @property
    def id(self) -> str:
        return f"{self.repo.key}/{self.path}"


def code_sections(text: str) -> list[dict]:
    """Code as sections of 40 to 80 lines, cut at a blank line where one comes, each headed by its line range."""
    lines = text.splitlines()
    out, start = [], 0
    while start < len(lines):
        end = min(start + CHUNK_MAX, len(lines))
        cut = next((i for i in range(start + CHUNK_MIN, end) if not lines[i].strip()), end)
        chunk = lines[start:cut]
        first = next((n for n, l in enumerate(chunk) if l.strip()), None)
        if first is not None:
            last = max(n for n, l in enumerate(chunk) if l.strip())
            body = "\n".join(chunk[first:last + 1])
            out.append({"heading": f"Lines {start + first + 1}–{start + last + 1}", "text": body})
        start = cut + 1 if cut < end else cut
    return out


class GitHub(Connector):
    name = "github connector"

    def __init__(self, env: Mapping[str, str], *, transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        self.specs = []
        for spec in names(env, "REPOS"):
            m = SPEC.fullmatch(spec)
            if not m or (m.group(2) == "*" and m.group(3)):
                raise SettingsError(f"REPOS must be owner/repo, owner/repo@branch or owner/*, got {spec!r}")
            self.specs.append(m.groups())
        if not self.specs:
            raise SettingsError("REPOS must name at least one repository")
        api = env.get("API_URL", "").strip() or "https://api.github.com"
        if urlparse(api).scheme not in ("http", "https") or not urlparse(api).netloc:
            raise SettingsError(f"API_URL must be an http(s) address, got {api!r}")
        self.files = globs(env, "FILES", DEFAULT_FILES)
        self.exclude = globs(env, "EXCLUDE", ())
        self.forks = flag(env, "FORKS", False)
        self.archived = flag(env, "ARCHIVED", False)
        self.max_files = whole(env, "MAX_FILES", 5000)
        self.max_file_bytes = whole(env, "MAX_FILE_BYTES", 1_000_000)
        self.token = env.get("TOKEN", "").strip()
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self._web = Web("passageway-connector-github", base_url=api.rstrip("/") + "/", headers=headers, pause=0.05,
                        max_bytes=self.max_file_bytes * 2 + 1_000_000, retry=Retry(), log=self.warn, transport=transport,
                        sleep=sleep)
        self._repos: list[Repo] | None = None

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {f.id: f.sha for repo in self._all() for f in self._tree(repo)}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        wanted = set(ids)
        for repo in self._all():
            if not any(i.startswith(repo.key + "/") for i in wanted):
                continue
            for file in self._tree(repo):
                if file.id in wanted and (item := self._item(file)) is not None:
                    yield item

    # -- the API -----------------------------------------------------------------------------

    def _get(self, path: str, params: Mapping[str, str] | None = None) -> Reply | None:
        """The reply to a GET; None for a 404. A used-up rate limit, a refused token or any other failure raises."""
        reply = self._web.get(path, params=params)
        if reply.status == 200:
            return reply
        if reply.status == 404:
            return None
        if reply.status in (403, 429) and reply.headers.get("x-ratelimit-remaining") == "0":
            reset = reply.headers.get("x-ratelimit-reset", "")
            when = datetime.fromtimestamp(int(reset), UTC).strftime(" (it resets at %H:%M UTC)") if reset.isdigit() else ""
            more = "" if self.token else "; without a TOKEN GitHub allows 60 requests an hour, with one 5000"
            raise SourceError(f"the GitHub API rate limit is used up{when}{more}")
        if reply.status == 401:
            raise SourceError("GitHub answered HTTP 401: check TOKEN (a personal access token that can read the repositories)")
        raise SourceError(f"GitHub answered HTTP {reply.status} for {path}")

    def _all(self) -> list[Repo]:
        if self._repos is None:
            repos: dict[str, Repo] = {}
            for owner, name, branch in self.specs:
                for repo in (self._owned(owner) if name == "*" else [self._one(owner, name, branch)]):
                    repos.setdefault(repo.key, repo)
            self._repos = list(repos.values())
        return self._repos

    def _one(self, owner: str, name: str, branch: str | None) -> Repo:
        reply = self._get(f"repos/{owner}/{name}")
        if reply is None:
            hint = "" if self.token else "; a private one needs a TOKEN"
            raise SourceError(f"{owner}/{name}: no such repository, or TOKEN cannot read it{hint}")
        return self._repo(reply.json(), branch)

    def _repo(self, data: dict, branch: str | None = None) -> Repo:
        key = data["full_name"] + (f"@{branch}" if branch else "")
        return Repo(key, data["full_name"], branch or data["default_branch"], data["html_url"])

    def _owned(self, owner: str) -> list[Repo]:
        user = self._get(f"users/{owner}")
        if user is None:
            raise SourceError(f"{owner}/*: no such user or organisation on GitHub")
        if user.json().get("type") == "Organization":
            path, params = f"orgs/{owner}/repos", {"type": "all"}
        elif self.token and (me := self._get("user")) is not None and me.json().get("login", "").lower() == owner.lower():
            path, params = "user/repos", {"affiliation": "owner"}  # the token's own account: its private repositories too
        else:
            path, params = f"users/{owner}/repos", {"type": "owner"}
        found, page = [], 1
        while True:
            batch = self._get(path, {**params, "per_page": str(PAGE), "page": str(page)})
            data = batch.json() if batch else []
            found += [r for r in data if (self.forks or not r["fork"]) and (self.archived or not r["archived"])]
            if len(data) < PAGE:
                return [self._repo(r) for r in found]
            page += 1

    def _tree(self, repo: Repo) -> list[File]:
        reply = self._get(f"repos/{repo.full_name}/git/trees/{quote(repo.branch, safe='')}", {"recursive": "1"})
        if reply is None:
            self.warn(f"skipped {repo.key}: the branch {repo.branch!r} has no files")
            return []
        data = reply.json()
        if data.get("truncated"):
            self.warn(f"{repo.key}: GitHub cut the file list short; some files are missing")
        files = []
        for entry in sorted(data.get("tree", []), key=lambda e: e["path"]):
            path = entry["path"]
            if entry.get("type") != "blob" or not self.files(path) or self.exclude(path):
                continue
            if entry.get("size", 0) > self.max_file_bytes:
                self.warn(f"skipped {repo.key}/{path}: larger than MAX_FILE_BYTES ({self.max_file_bytes})")
                continue
            files.append(File(repo, path, entry["sha"]))
        if len(files) > self.max_files:
            self.warn(f"{repo.key} has {len(files)} matching files; only the first {self.max_files} are indexed (MAX_FILES)")
        return files[:self.max_files]

    # -- the items ---------------------------------------------------------------------------

    def _text(self, file: File) -> str | None:
        reply = self._get(f"repos/{file.repo.full_name}/git/blobs/{file.sha}")
        if reply is None:
            return None  # gone since the listing
        raw = base64.b64decode(reply.json().get("content", ""))
        try:
            if b"\0" in raw:
                raise UnicodeDecodeError("utf-8", b"", 0, 1, "binary data")
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            self.warn(f"skipped {file.id}: not UTF-8 text")
            return None

    def _item(self, file: File) -> dict | None:
        text = self._text(file)
        if text is None:
            return None
        folder, _, name = file.path.rpartition("/")
        if file.path.lower().endswith(MARKDOWN):
            body = strip_front_matter(text)
            h1 = None if not folder and name.lower().startswith("readme.") else first_h1(body)
            title = h1 or (file.repo.full_name if not folder and name.lower().startswith("readme.") else name)
            sections = split_markdown(body, skip_first_h1=bool(h1))
        else:
            title, sections = name, code_sections(text)
        return {
            "id": file.id,
            "title": title,
            "url": f"{file.repo.html_url}/blob/{quote(file.repo.branch, safe='/')}/{quote(file.path, safe='/')}",
            "version": file.sha,
            "sections": sections,
            "path": [file.repo.full_name, *([p for p in folder.split("/") if p])],
        }


def main() -> None:
    GitHub.main()
