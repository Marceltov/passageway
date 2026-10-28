import os
import sys

import pytest

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

pytestmark = pytest.mark.skipif(os.environ.get("PASSAGEWAY_LIVE") != "1", reason="set PASSAGEWAY_LIVE=1 to hit Wikipedia")


def test_a_small_real_category_passes_the_contract():
    connector = Connector("wikipedia", [sys.executable, "-m", "passageway_connector_wikipedia"], timeout=120,
                          env={"CATEGORIES": "Lighthouses in Germany", "CATEGORY_DEPTH": "0", "MAX_PAGES": "60",
                               "CONTACT": "passageway live test"})
    check_connector(connector)
