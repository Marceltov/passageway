import sys

from passageway.protocol import Connector
from passageway.testing.contract import check_connector


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(wiki_server):
    url, wiki = wiki_server
    wiki.add(1, "Heligoland", "Island text.\n\n== History ==\nOld.", revid=11)
    wiki.add(2, "Cape Arkona", "Cape text.", revid=22)
    wiki.categories["Category:Lighthouses"] = {"pages": [1, 2], "subcats": []}
    connector = Connector("wikipedia", [sys.executable, "-m", "passageway_connector_wikipedia"],
                          env={"API_URL": url, "PAGE_URL": "http://wiki.example/wiki/", "CATEGORIES": "Lighthouses",
                               "PAUSE_SECONDS": "0"})
    check_connector(connector)
    assert {i.title for i in connector.fetch(["1", "2"])} == {"Heligoland", "Cape Arkona"}
