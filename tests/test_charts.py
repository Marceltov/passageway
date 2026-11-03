"""The measurement charts are drawn from the numbers the pages hold (docs_hooks/charts.py), never typed by hand."""

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def charts():
    spec = importlib.util.spec_from_file_location("charts_hook", ROOT / "docs_hooks" / "charts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_chart_marker_is_drawn_and_none_is_left_over():
    hook = charts()
    for page in ["measurements.md", "models.md"]:
        out = hook.on_page_markdown((ROOT / "docs" / page).read_text(), None, None, None)
        assert "<!-- chart:" not in out and "<svg" in out, page


def test_the_outcome_chart_counts_match_the_headline_rates():
    block = (ROOT / "docs" / "measurements.md").read_text().split("<!-- passageway:results:start -->")[1]
    svg = charts().outcomes(block)
    answerable = int(re.search(r"\((\d+) answerable", block).group(1))
    counts = [int(c) for c in re.findall(r": (\d+) of \d+</title>", svg)]
    assert sum(counts[:3]) == answerable
