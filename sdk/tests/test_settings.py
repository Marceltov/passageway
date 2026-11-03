import pytest

from passageway_sdk import SettingsError
from passageway_sdk.settings import flag, names, seconds, whole


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
