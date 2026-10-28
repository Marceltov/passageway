import io
import json
import subprocess
import sys
import textwrap
from datetime import datetime, timezone

import pytest

from passageway.protocol import Connector as CoreConnector, parse_item
from passageway.testing.contract import check_connector
from passageway_sdk import Connector, SettingsError, SourceError

ITEM = {"id": "a", "title": "Doc a", "url": "http://x/a", "version": "1", "sections": [{"heading": None, "text": "body"}]}


class Demo(Connector):
    name = "demo connector"

    def __init__(self, env, **options):
        self.items = {"a": ITEM, "b": {**ITEM, "id": "b", "version": "2"}}
        if env.get("BAD"):
            raise SettingsError("BAD must not be set")
        self.fail = env.get("FAIL")
        self.options = options

    def versions(self):
        if self.fail == "source":
            raise SourceError("the source is down")
        if self.fail == "crash":
            raise RuntimeError("a bug")
        return {i: r["version"] for i, r in self.items.items()}

    def fetch(self, ids):
        for i in ids:
            if i in self.items:
                yield self.items[i]
            if self.fail == "late" and i == "a":
                raise SourceError("died after the first item")


def call(cls, mode, *, stdin="", env=None, extra=()):
    out, err = io.StringIO(), io.StringIO()
    code = cls.run(["prog", mode, *extra], env or {}, io.StringIO(stdin), out, err)
    return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()


def test_check_counts_the_versions_and_names_the_protocol():
    assert call(Demo, "check")[:2] == (0, [{"ok": True, "count": 2, "protocol": "1"}])


def test_list_prints_id_and_version_per_item():
    assert call(Demo, "list")[:2] == (0, [{"id": "a", "version": "1"}, {"id": "b", "version": "2"}])


def test_fetch_reads_ids_from_stdin_and_skips_blank_lines():
    code, records, _ = call(Demo, "fetch", stdin='{"id": "b"}\n\n{"id": "zzz"}\n')
    assert code == 0 and [r["id"] for r in records] == ["b"]


def test_changed_is_optional_and_prints_nothing_by_default():
    assert call(Demo, "changed", extra=["--since", "2026-01-01T00:00:00Z"])[:2] == (0, [])


def test_changed_receives_an_aware_datetime():
    seen = []

    class Changing(Demo):
        def changed(self, since):
            seen.append(since)
            return [ITEM]

    assert call(Changing, "changed", extra=["--since", "2026-01-01T00:00:00Z"])[1] == [ITEM]
    assert seen == [datetime(2026, 1, 1, tzinfo=timezone.utc)]


@pytest.mark.parametrize("extra", [[], ["--since"], ["--since", "yesterday"], ["--since", "2026-01-01T00:00:00"]])
def test_a_connector_that_implements_changed_needs_a_valid_since(extra):
    class Changing(Demo):
        def changed(self, since):
            return [ITEM]

    code, records, err = call(Changing, "changed", extra=extra)
    assert code == 2 and records == [] and "--since" in err


def test_a_connector_without_changed_does_not_care_about_since():
    assert call(Demo, "changed")[:2] == (0, [])


def test_an_unknown_mode_is_a_usage_error():
    code, records, err = call(Demo, "bogus")
    assert code == 2 and records == [] and "usage" in err


def test_bad_settings_exit_2_with_the_message_and_no_output():
    code, records, err = call(Demo, "list", env={"BAD": "1"})
    assert code == 2 and records == [] and err.strip() == "demo connector: BAD must not be set"


def test_a_source_failure_exits_1_with_the_message_and_no_traceback():
    code, records, err = call(Demo, "list", env={"FAIL": "source"})
    assert code == 1 and records == [] and err.strip() == "demo connector: the source is down"


def test_all_or_nothing_a_failure_after_some_items_prints_nothing():
    code, records, _ = call(Demo, "fetch", stdin='{"id": "a"}\n{"id": "b"}\n', env={"FAIL": "late"})
    assert code == 1 and records == []


def test_an_unexpected_error_is_not_swallowed():
    with pytest.raises(RuntimeError):
        call(Demo, "list", env={"FAIL": "crash"})


def test_expected_errors_can_be_declared_by_the_connector():
    class Declares(Demo):
        expected_errors = (KeyError,)

        def versions(self):
            raise KeyError("missing")

    assert call(Declares, "list")[0] == 1


def test_a_bad_stdin_line_is_a_source_error():
    code, records, err = call(Demo, "fetch", stdin="not json\n")
    assert code == 1 and records == [] and "fetch" in err


def test_options_reach_the_constructor():
    seen = {}

    class Optioned(Demo):
        def __init__(self, env, **options):
            super().__init__(env)
            seen.update(options)

    out = io.StringIO()
    Optioned.run(["prog", "list"], {}, io.StringIO(), out, io.StringIO(), pause=0)
    assert seen == {"pause": 0}


@pytest.mark.parametrize("bad", [
    {**ITEM, "id": ""}, {**ITEM, "version": 1}, {**ITEM, "sections": "x"}, {**ITEM, "sections": [{"heading": "H"}]},
    {**ITEM, "weight": 3}, {**ITEM, "weight": True}, {**ITEM, "path": "P"}, {**ITEM, "links": [""]},
    {k: v for k, v in ITEM.items() if k != "url"}, [],
])
def test_an_invalid_item_is_a_source_error_naming_the_problem(bad):
    class Bad(Demo):
        def fetch(self, ids):
            yield bad

    code, records, err = call(Bad, "fetch", stdin='{"id": "a"}\n')
    assert code == 1 and records == [] and "invalid item" in err


@pytest.mark.parametrize("bad", [
    {**ITEM, "id": ""}, {**ITEM, "version": 1}, {**ITEM, "weight": 3}, {**ITEM, "links": [""]},
    {**ITEM, "sections": [{"heading": 3, "text": "x"}]}, {**ITEM, "updated": 5},
])
def test_the_sdk_and_the_core_validate_alike(bad):
    class Bad(Demo):
        def fetch(self, ids):
            yield bad

    sdk_accepts = call(Bad, "fetch", stdin='{"id": "a"}\n')[0] == 0
    try:
        parse_item(bad)
        core_accepts = True
    except ValueError:
        core_accepts = False
    assert sdk_accepts is core_accepts is False


def test_output_is_ascii_safe_so_a_locale_without_utf8_cannot_crash_it():
    class Umlaut(Demo):
        def fetch(self, ids):
            yield {**ITEM, "title": "Köln Süd"}

    out = io.StringIO()
    Umlaut.run(["prog", "fetch"], {}, io.StringIO('{"id": "a"}\n'), out, io.StringIO())
    assert out.getvalue().isascii() and json.loads(out.getvalue())["title"] == "Köln Süd"


FOLDER = '''
import hashlib
from pathlib import Path

from passageway_sdk import Connector, SettingsError


class Folder(Connector):
    name = "folder connector"

    def __init__(self, env):
        self.root = Path(env.get("FOLDER", "")).resolve()
        if not self.root.is_dir():
            raise SettingsError(f"FOLDER must be an existing folder, got {env.get('FOLDER')!r}")

    def files(self):
        return {p.relative_to(self.root).as_posix(): p for p in sorted(self.root.rglob("*.txt"))}

    def versions(self):
        return {i: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for i, p in self.files().items()}

    def fetch(self, ids):
        for i, p in self.files().items():
            if i in ids:
                yield {"id": i, "title": p.stem, "url": p.as_uri(), "version": self.versions()[i],
                       "sections": [{"heading": None, "text": p.read_text(encoding="utf-8")}]}


Folder.main()
'''


def test_a_folder_connector_is_under_thirty_lines_and_passes_the_contract_check(tmp_path):
    assert len(FOLDER.strip().splitlines()) < 30
    script = tmp_path / "folder.py"
    script.write_text(FOLDER)
    notes = tmp_path / "notes"
    (notes / "sub").mkdir(parents=True)
    (notes / "a.txt").write_text("Alpha note.")
    (notes / "sub" / "b.txt").write_text("Beta note.")
    connector = CoreConnector("folder", [sys.executable, str(script)], env={"FOLDER": str(notes)})
    check_connector(connector)
    assert {i.id for i in connector.fetch(["a.txt", "sub/b.txt"])} == {"a.txt", "sub/b.txt"}


def test_main_exits_with_the_code_as_a_real_process(tmp_path):
    script = tmp_path / "folder.py"
    script.write_text(FOLDER)
    run = subprocess.run([sys.executable, str(script), "list"], capture_output=True, text=True,
                         env={"PATH": "/usr/bin", "FOLDER": str(tmp_path / "missing")})
    assert run.returncode == 2 and run.stdout == "" and "FOLDER must be an existing folder" in run.stderr


@pytest.mark.parametrize("line", ['{"id": 1}', '{"id": null}', '{"id": ""}', '[]', '{"name": "a"}'])
def test_fetch_ids_must_be_non_empty_strings(line):
    code, records, err = call(Demo, "fetch", stdin=line + "\n")
    assert code == 1 and records == [] and "fetch expects" in err


@pytest.mark.parametrize("versions", [{"": "1"}, {2: "1"}, {"a": 3}, {"a": None}])
def test_list_entries_are_validated_like_the_core_does(versions):
    class Listing(Demo):
        def versions(self):
            return versions

    code, records, err = call(Listing, "list")
    assert code == 1 and records == [] and "invalid" in err


@pytest.mark.parametrize("count", [-1, 1.5, "3", True, None])
def test_a_custom_count_must_be_a_whole_number_from_zero(count):
    class Counting(Demo):
        def count(self):
            return count

    code, records, err = call(Counting, "check")
    assert code == 1 and records == [] and "count" in err


def test_fetch_may_only_return_requested_ids():
    class Greedy(Demo):
        def fetch(self, ids):
            yield {**ITEM, "id": "zzz"}

    code, records, err = call(Greedy, "fetch", stdin='{"id": "a"}\n')
    assert code == 1 and records == [] and "zzz" in err and "not requested" in err


def test_the_usage_message_names_the_program():
    assert "prog" in call(Demo, "bogus")[2]
