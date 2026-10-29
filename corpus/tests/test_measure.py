import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "measure.sh"


@pytest.mark.skipif(not shutil.which("bash"), reason="needs bash")
def test_the_script_is_valid_bash():
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True).returncode == 0


def test_the_example_that_shows_every_question_does_not_rewrite_the_published_page():
    text = SCRIPT.read_text()
    assert "--no-write --include-cases" in text  # the documented way to look at the questions
    assert text.count("--include-cases") == 1, "an example with --include-cases but without --no-write would put every question into the page"


def test_the_sweep_includes_the_default_threshold_and_the_page_is_written_by_default():
    text = SCRIPT.read_text()
    assert "0.84,0.845,0.85" in text and "--write docs/measurements.md" in text
