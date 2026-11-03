from passageway.rank import Hit
from passageway.render import approx_tokens, fit, render


def hit(n, source="s", links=()):
    return Hit(source, f"i{n}", f"Title {n}", f"http://x/{n}", ["decision"], ["Ops"], "Steps",
               "rotate the cert " * 3, 1.0, list(links))


def test_empty_hits_render_nothing():
    assert render([]) == "" and fit([]) == ("", [])


def test_render_lists_title_labels_url_and_passage():
    text = render([hit(1)])
    assert text.startswith("Recall results (s)")
    assert "1. Title 1 [decision] http://x/1" in text and "Ops › Steps" in text and "rotate the cert" in text


def test_several_sources_are_tagged_and_links_listed():
    text = render([hit(1, "a", links=[("Beta", "http://x/b")]), hit(2, "b")])
    assert "@a" in text and "@b" in text and "related: Beta http://x/b" in text


def test_budget_drops_hits_from_the_end():
    text, shown = fit([hit(n) for n in range(1, 8)], max_tokens=120)
    assert 1 <= len(shown) < 7 and shown[0].item_id == "i1"


def test_one_very_long_hit_still_fits_the_budget():
    long = hit(1)
    long.title = "word " * 2000
    long.path = ["folder"] * 500
    text, shown = fit([long], max_tokens=400)
    assert approx_tokens(text) <= 400 and [h.item_id for h in shown] == ["i1"]
    assert "http://x/1" in text  # the link is what makes a hit useful, it is never cut
