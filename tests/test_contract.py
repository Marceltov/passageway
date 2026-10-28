import json
import sys

import pytest

from passageway.protocol import Connector, ConnectorError
from passageway.testing.contract import check_connector

ITEMS = [
    {"id": "a", "title": "Alpha", "url": "http://x/a", "version": "1", "updated": "2026-10-01T00:00:00Z",
     "sections": [{"heading": "H", "text": "alpha body"}]},
    {"id": "b", "title": "Beta", "url": "http://x/b", "version": "2", "updated": "2026-10-20T00:00:00Z",
     "sections": []},
]


def fake(tmp_path, items=ITEMS, **env):
    path = tmp_path / "items.json"
    path.write_text(json.dumps(items))
    return Connector("fake", [sys.executable, "-m", "passageway.testing.fake_connector"],
                     env={"FAKE_ITEMS": str(path), **env})


def test_fake_connector_passes_the_contract(tmp_path):
    check_connector(fake(tmp_path))


def test_fake_changed_filters_by_updated(tmp_path):
    from datetime import datetime, timezone
    items = fake(tmp_path).changed(datetime(2026, 10, 10, tzinfo=timezone.utc))
    assert [i.id for i in items] == ["b"]


def test_fake_failure_mode(tmp_path):
    with pytest.raises(ConnectorError, match="fake failure"):
        fake(tmp_path, FAKE_FAIL="list").list_versions()


def test_contract_catches_a_version_mismatch(tmp_path):
    class Lying(Connector):
        def list_versions(self):
            return {k: "other" for k in super().list_versions()}

    base = fake(tmp_path)
    liar = Lying("fake", base._command, env=base._env)
    with pytest.raises(AssertionError, match="version"):
        check_connector(liar)
