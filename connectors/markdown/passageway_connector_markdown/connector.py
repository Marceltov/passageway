"""passageway connector for a folder of markdown files with front matter."""

import hashlib
import os
import posixpath
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

import yaml
from passageway_sdk import Connector, SettingsError, SourceError, first_h1, split_markdown, strip_code

DEFAULT_INCLUDE = ("*.md", "*.markdown")
SKIP_DIRS = frozenset({"node_modules"})
FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n(?:(.*?)\r?\n)?(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.S)
# [[wiki link]] or [text](target); no brackets or line breaks inside, which also keeps the matching linear
LINK = re.compile(r"\[\[([^\[\]\n]+)\]\]|\[[^\[\]\n]*\]\(([^()\n]*)\)")
SCHEME = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")


def _list(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in env.get(key, "").split("|") if p.strip())


def _int(env: Mapping[str, str], key: str, default: int, low: int) -> int:
    raw = env.get(key, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        raise SettingsError(f"{key} must be a whole number, got {raw!r}") from None
    if value < low:
        raise SettingsError(f"{key} must be at least {low}, got {value}")
    return value


def _glob(pattern: str) -> re.Pattern:
    """A glob over the path relative to the folder. `**` crosses folders; a pattern without `/` matches the file name anywhere."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(("" if "/" in pattern else "(?:.*/)?") + out + r"\Z")


@dataclass(frozen=True)
class Note:
    rel: str  # the path relative to the folder, with `/`
    path: Path
    id: str
    meta: dict
    body: str
    version: str  # the content and the links it resolves to: a link that starts to resolve changes it
    mtime: float
    changed: float  # the later of modification and change time: a note moved in keeps its old mtime
    links: tuple[str, ...] = ()


class Markdown(Connector):
    name = "markdown connector"
    expected_errors = (OSError,)

    def __init__(self, env: Mapping[str, str]):
        folder = env.get("FOLDER", "").strip()
        if not folder or not Path(folder).is_dir():
            raise SettingsError(f"FOLDER must be an existing folder, got {folder!r}")
        self.root = Path(folder).resolve()
        self.include = [_glob(p) for p in _list(env, "INCLUDE") or DEFAULT_INCLUDE]
        self.exclude = [_glob(p) for p in _list(env, "EXCLUDE")]
        self.max_bytes = _int(env, "MAX_FILE_BYTES", 1024 * 1024, 1)

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {note.id: note.version for note in self._notes().values()}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        notes = self._notes()
        for item_id in ids:
            if item_id in notes:
                yield self._item(notes[item_id])

    def changed(self, since: datetime) -> Iterator[dict]:
        # ponytail: every call reads the whole folder (ids and links need it); a cache if a vault ever has tens of thousands of notes
        for note in self._notes().values():
            if note.changed >= since.timestamp():
                yield self._item(note)

    # -- the folder --------------------------------------------------------------------------

    def _wanted(self, rel: str) -> bool:
        return any(g.match(rel) for g in self.include) and not any(g.match(rel) for g in self.exclude)

    def _paths(self) -> Iterator[tuple[str, Path]]:
        def unreadable(e: OSError) -> None:
            self.warn(f"skipped {Path(e.filename).relative_to(self.root).as_posix()}/: {e.strerror}")

        for dirpath, dirnames, filenames in os.walk(self.root, onerror=unreadable):  # does not follow symlinked folders
            dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
                                 and not os.path.islink(os.path.join(dirpath, d)))
            for name in sorted(filenames):
                path = Path(dirpath, name)
                rel = path.relative_to(self.root).as_posix()
                if name.startswith(".") or not self._wanted(rel) or not path.is_file():
                    continue
                if path.is_symlink() and not path.resolve().is_relative_to(self.root):
                    continue  # a link out of the folder would index files that are not in it
                yield rel, path

    def _notes(self) -> dict[str, Note]:
        notes: dict[str, Note] = {}
        for rel, path in self._paths():
            note = self._read(rel, path)
            if note is None:
                continue
            if note.id in notes:
                raise SourceError(f"two notes have the id {note.id!r}: {notes[note.id].rel} and {rel}")
            notes[note.id] = note
        finder = _Links(notes)
        for item_id, note in notes.items():
            found = tuple(finder.of(note))
            digest = hashlib.sha256((note.version + "\n".join(found)).encode()).hexdigest()[:16]
            notes[item_id] = replace(note, links=found, version=digest)
        return notes

    def _read(self, rel: str, path: Path) -> Note | None:
        try:
            stat = path.stat()
            if stat.st_size > self.max_bytes:
                self.warn(f"skipped {rel}: larger than MAX_FILE_BYTES ({self.max_bytes})")
                return None
            raw = path.read_bytes()
        except OSError as e:  # gone since the listing, or unreadable
            self.warn(f"skipped {rel}: {e.strerror or e}")
            return None
        try:
            if b"\0" in raw:
                raise UnicodeDecodeError("utf-8", b"", 0, 1, "binary data")
            text = raw.decode("utf-8-sig")  # also removes a BOM
        except UnicodeDecodeError:
            self.warn(f"skipped {rel}: not UTF-8 text")
            return None
        meta, body = self._front_matter(rel, text)
        return Note(rel, path, _text(meta, "id") or rel, meta, body, hashlib.sha256(raw).hexdigest(), stat.st_mtime,
                    max(stat.st_mtime, stat.st_ctime))

    def _front_matter(self, rel: str, text: str) -> tuple[dict, str]:
        match = FRONT_MATTER.match(text)
        if not match:
            return {}, text
        body = text[match.end():]
        try:
            # BaseLoader keeps every scalar a string, so `no` stays "no" and a date stays "2026-10-28"; it builds no objects
            meta = yaml.load(match.group(1) or "", Loader=yaml.BaseLoader)
        except (yaml.YAMLError, RecursionError):  # RecursionError: a few thousand nested brackets
            self.warn(f"{rel}: front matter is not valid YAML, indexed without it")
            return {}, body
        if meta is not None and not isinstance(meta, dict):
            self.warn(f"{rel}: front matter is not a mapping of keys, indexed without it")
            return {}, body
        return meta or {}, body

    # -- the item ----------------------------------------------------------------------------

    def _item(self, note: Note) -> dict:
        meta = note.meta
        title = _text(meta, "title")
        heading = None if title else first_h1(note.body)  # an H1 that is the title is not repeated as a heading
        item = {
            "id": note.id,
            "title": title or heading or PurePosixPath(note.rel).stem,
            "url": _text(meta, "url") or note.path.as_uri(),
            "version": note.version,
            "updated": _text(meta, "updated") or datetime.fromtimestamp(note.mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sections": split_markdown(note.body, skip_first_h1=heading is not None),
        }
        if folders := list(PurePosixPath(note.rel).parent.parts):
            item["path"] = folders
        if labels := _tags(meta.get("tags")):
            item["labels"] = labels
        if note.links:
            item["links"] = list(note.links)
        weight = _text(meta, "weight")
        if weight is not None:
            try:
                value = float(weight)
                if not 0 <= value <= 2:
                    raise ValueError
                item["weight"] = value
            except ValueError:
                self.warn(f"{note.rel}: weight must be a number from 0 to 2, got {weight!r}; ignored")
        return item


def _text(meta: dict, key: str) -> str | None:
    value = meta.get(key)
    return value.strip() or None if isinstance(value, str) else None


def _tags(value) -> list[str]:
    if isinstance(value, str):
        value = value.split(",")
    return [t.strip() for t in value if isinstance(t, str) and t.strip()] if isinstance(value, list) else []


class _Links:
    """Finds the notes a note links to: by path for [text](file.md), by file name for [[Name]]."""

    def __init__(self, notes: dict[str, Note]):
        self.by_path = {n.rel: n.id for n in notes.values()}
        stems: dict[str, list[str]] = {}
        for n in notes.values():
            stems.setdefault(PurePosixPath(n.rel).stem.casefold(), []).append(n.id)
        self.by_stem = {stem: ids[0] for stem, ids in stems.items() if len(ids) == 1}  # an ambiguous name links to nothing

    def of(self, note: Note) -> list[str]:
        found: list[str] = []
        for wiki, target in LINK.findall(strip_code(note.body)):
            item_id = self._wiki(wiki) if wiki else self._path(note, target)
            if item_id and item_id != note.id and item_id not in found:
                found.append(item_id)
        return found

    def _wiki(self, wiki: str) -> str | None:
        target = re.split(r"\\?\|", wiki)[0].split("#")[0].strip()  # `\|` is how a table cell escapes the pipe
        target = target[:-3] if target.lower().endswith(".md") else target
        for candidate in (f"{target}.md", f"{target}.markdown"):  # [[folder/Name]] names the folder when the name is ambiguous
            if candidate in self.by_path:
                return self.by_path[candidate]
        return self.by_stem.get(PurePosixPath(target).name.casefold())

    def _path(self, note: Note, target: str) -> str | None:
        target = target.strip()
        if target.startswith("<") and ">" in target:  # <a target with spaces> and an optional title after it
            target = target[1:target.index(">")]
        else:
            target = target.split()[0] if target else ""
        target = unquote(target.split("#")[0].split("?")[0])
        if not target or SCHEME.match(target):
            return None
        joined = target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(note.rel), target)
        resolved = posixpath.normpath(joined)
        return None if resolved.startswith("..") else self.by_path.get(resolved)


def main() -> None:
    Markdown.main()
