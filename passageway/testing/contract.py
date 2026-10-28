"""What every connector must satisfy. Connector authors call check_connector from their own tests."""

from datetime import datetime, timezone

from passageway.protocol import Connector


def check_connector(connector: Connector) -> None:
    versions = connector.list_versions()
    assert connector.check() == len(versions), "check() count must equal the number of listed items"
    ids = list(versions)
    items = connector.fetch(ids)
    assert {i.id for i in items} == set(ids), "fetch must return every listed id"
    for item in items:
        assert item.version == versions[item.id], f"version of {item.id} differs between list and fetch"
    assert connector.fetch(["__passageway-no-such-id__"]) == [], "fetch must skip ids that do not exist"
    assert connector.changed(datetime(2100, 1, 1, tzinfo=timezone.utc)) == [], "nothing can have changed in 2100"
