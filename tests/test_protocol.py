import json
import sys
import textwrap
import time
from datetime import datetime, timezone

import pytest

from passageway.protocol import Connector, ConnectorError, Item, Section, parse_item


def cmd(tmp_path, body: str) -> list[str]:
    path = tmp_path / "connector.py"
    path.write_text(textwrap.dedent(body))
    return [sys.executable, str(path)]


ITEM = {"id": "a", "title": "T", "url": "http://x/a", "version": "1",
        "sections": [{"heading": "H", "text": "body"}]}


def test_parse_item_minimal_and_full():
    assert parse_item(ITEM) == Item("a", "T", "http://x/a", "1", (Section("H", "body"),))
    full = {**ITEM, "weight": 0.8, "path": ["P"], "links": [{"id": "z", "title": "Z"}],
            "labels": ["l"], "updated": "2026-10-28T09:00:00Z"}
    assert parse_item(full) == Item("a", "T", "http://x/a", "1", (Section("H", "body"),), 0.8, ("P",),
                                    (("z", "Z"),), ("l",), "2026-10-28T09:00:00Z")


@pytest.mark.parametrize("bad", [
    {**ITEM, "id": ""}, {**ITEM, "version": 1}, {**ITEM, "sections": "x"},
    {**ITEM, "sections": [{"heading": "H"}]}, {**ITEM, "weight": 3}, {**ITEM, "weight": True},
    {**ITEM, "path": "P"}, {**ITEM, "links": [{"id": "z"}]}, [], {k: v for k, v in ITEM.items() if k != "url"},
])
def test_parse_item_rejects(bad):
    with pytest.raises(ValueError):
        parse_item(bad)


def test_list_versions(tmp_path):
    c = cmd(tmp_path, '''
        import json, sys
        if sys.argv[1] == "list":
            print(json.dumps({"id": "a", "version": "1"})); print(json.dumps({"id": "b", "version": "2"}))
    ''')
    assert Connector("c", c).list_versions() == {"a": "1", "b": "2"}


def test_list_rejects_duplicate_ids(tmp_path):
    c = cmd(tmp_path, '''
        import json
        for _ in range(2): print(json.dumps({"id": "a", "version": "1"}))
    ''')
    with pytest.raises(ConnectorError, match="duplicate id"):
        Connector("c", c).list_versions()


def test_fetch_sends_ids_on_stdin_and_parses_items(tmp_path):
    c = cmd(tmp_path, '''
        import json, sys
        if sys.argv[1] == "fetch":
            for line in sys.stdin:
                i = json.loads(line)["id"]
                print(json.dumps({"id": i, "title": "T" + i, "url": "http://x/" + i, "version": "1",
                                  "sections": [{"heading": None, "text": "body " + i}]}))
    ''')
    items = Connector("c", c).fetch(["a", "b"])
    assert [i.id for i in items] == ["a", "b"] and items[1].sections == (Section(None, "body b"),)


def test_fetch_of_unrequested_id_fails_and_returns_nothing(tmp_path):
    c = cmd(tmp_path, '''
        import json
        print(json.dumps({"id": "other", "title": "T", "url": "u", "version": "1", "sections": []}))
    ''')
    with pytest.raises(ConnectorError, match="not requested"):
        Connector("c", c).fetch(["a"])


def test_non_zero_exit_fails_with_status_and_stderr(tmp_path):
    c = cmd(tmp_path, '''
        import json, sys
        print(json.dumps({"id": "a", "version": "1"}))
        print("token expired", file=sys.stderr); sys.exit(3)
    ''')
    with pytest.raises(ConnectorError, match=r"status 3.*token expired"):
        Connector("c", c).list_versions()


def test_secret_values_are_masked_in_errors(tmp_path):
    c = cmd(tmp_path, '''
        import os, sys
        print("bad token " + os.environ["TOKEN"], file=sys.stderr); sys.exit(1)
    ''')
    with pytest.raises(ConnectorError) as e:
        Connector("c", c, secrets={"TOKEN": "s3cret"}).list_versions()
    assert "s3cret" not in str(e.value) and "***" in str(e.value)


def test_malformed_line_names_connector_and_line(tmp_path):
    c = cmd(tmp_path, 'print(\'{"id": "a", "version": "1"}\'); print("not json")')
    with pytest.raises(ConnectorError, match=r"connector 'c'.*line 2"):
        Connector("c", c).list_versions()


def test_overlong_line_fails(tmp_path):
    c = cmd(tmp_path, 'print("x" * 5000)')
    with pytest.raises(ConnectorError, match="longer than"):
        Connector("c", c, max_line_bytes=1000).list_versions()


def test_output_over_the_call_limit_fails(tmp_path):
    c = cmd(tmp_path, '''
        import json
        for i in range(500): print(json.dumps({"id": str(i), "version": "1"}))
    ''')
    with pytest.raises(ConnectorError, match="more than"):
        Connector("c", c, max_output_bytes=2000).list_versions()


def test_timeout_kills_the_connector(tmp_path):
    c = cmd(tmp_path, 'import time; time.sleep(30)')
    with pytest.raises(ConnectorError, match="timed out"):
        Connector("c", c, timeout=0.5).list_versions()


def test_environment_is_isolated_and_carries_marker_env_and_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv("LEAKED", "1")
    c = cmd(tmp_path, '''
        import json, os
        print(json.dumps({"id": "env", "version": json.dumps(sorted(
            k for k in os.environ if k in ("LEAKED", "PASSAGEWAY_PROTOCOL", "URL", "TOKEN")))}))
    ''')
    versions = Connector("c", c, env={"URL": "u"}, secrets={"TOKEN": "t"}).list_versions()
    assert json.loads(versions["env"]) == ["PASSAGEWAY_PROTOCOL", "TOKEN", "URL"]


def test_changed_passes_since_in_utc(tmp_path):
    c = cmd(tmp_path, '''
        import json, sys
        print(json.dumps({"id": "x", "title": "T", "url": "u", "version": sys.argv[3], "sections": []}))
    ''')
    since = datetime(2026, 10, 28, 9, 0, 0, tzinfo=timezone.utc)
    assert Connector("c", c).changed(since)[0].version == "2026-10-28T09:00:00Z"


def test_check_returns_count(tmp_path):
    c = cmd(tmp_path, 'import json; print(json.dumps({"ok": True, "count": 42}))')
    assert Connector("c", c).check() == 42


def test_timeout_also_kills_children_the_connector_started(tmp_path):
    # a shell wrapper that forks: killing only the shell would leave the child holding the pipe open
    c = ["sh", "-c", f"{sys.executable} -c 'import time; time.sleep(8)'; true"]
    started = time.monotonic()
    with pytest.raises(ConnectorError, match="timed out"):
        Connector("c", c, timeout=0.5).list_versions()
    assert time.monotonic() - started < 4
