import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Built in two halves so this file does not match itself.
OLD = ("Marceltov" + "/passageway", "marceltov" + "/passageway")


def test_no_reference_to_the_old_owner():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    stale = [f"{f}:{n}" for f in files if (ROOT / f).is_file()
             for n, line in enumerate((ROOT / f).read_text(errors="ignore").splitlines(), 1)
             if any(old in line for old in OLD)]
    assert not stale, f"the repository lives at getpassageway/passageway: {stale[:10]}"
