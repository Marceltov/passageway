import pytest

from passageway_sdk import SettingsError
from passageway_sdk.settings import flag, globs, names, seconds, weight_of, weights, whole


def test_names_splits_at_a_bar_and_drops_blanks():
    assert names({"A": " x | y ||z "}, "A") == ("x", "y", "z")
    assert names({}, "A") == ()


def test_whole_reads_a_whole_number_with_a_default_and_a_floor():
    assert whole({}, "N", 5) == 5
    assert whole({"N": " 7 "}, "N", 5) == 7
    assert whole({"N": "0"}, "N", 5, low=0) == 0
    for bad in ("x", "1.5", "0"):
        with pytest.raises(SettingsError, match="N"):
            whole({"N": bad}, "N", 5)


def test_flag_reads_true_or_false_only():
    assert flag({}, "F", True) is True and flag({"F": "False"}, "F", True) is False and flag({"F": " true "}, "F", False) is True
    with pytest.raises(SettingsError, match="F"):
        flag({"F": "maybe"}, "F", True)


def test_seconds_reads_a_number_that_is_not_negative():
    assert seconds({}, "S", 0.2) == 0.2 and seconds({"S": "0"}, "S", 0.2) == 0.0
    for bad in ("x", "-1"):
        with pytest.raises(SettingsError, match="S"):
            seconds({"S": bad}, "S", 0.2)


def test_weights_reads_prefix_weight_pairs_in_order():
    assert weights({"W": " changelog=0.5, /archive/=0.3 "}, "W") == [("changelog", 0.5), ("archive/", 0.3)]
    assert weights({}, "W") == []
    for bad in ("changelog", "changelog=0", "=0.5", "a=x", "a=-1"):
        with pytest.raises(SettingsError, match="W must be"):
            weights({"W": bad}, "W")


def test_weight_of_takes_the_first_matching_prefix():
    table = [("changelog/v1", 0.2), ("changelog", 0.5)]
    assert weight_of(table, "/changelog/v1/x") == 0.2
    assert weight_of(table, "changelog/v2") == 0.5
    assert weight_of(table, "howto") == 1.0


def test_globs_match_paths_with_double_star_across_folders_and_bare_names_at_any_depth():
    wanted = globs({"I": "docs/**/*.md|a.md"}, "I", ("*.md",))
    assert [p for p in ("a.md", "x/a.md", "docs/b.md", "docs/x/y/c.md", "src/b.md", "docs/b.txt") if wanted(p)] == \
        ["a.md", "x/a.md", "docs/b.md", "docs/x/y/c.md"]
    assert globs({}, "I", ("*.md",))("deep/down/z.md") and not globs({}, "I", ())("z.md")
    assert globs({"I": "src/*.py"}, "I", ())("src/a.py") and not globs({"I": "src/*.py"}, "I", ())("src/x/a.py")
