import json
import os
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
pytestmark = pytest.mark.skipif(not shutil.which("jq"), reason="the release scripts need jq")


def run(script, *args, cwd=ROOT, env=None):
    return subprocess.run(["bash", str(SCRIPTS / script), *args], cwd=cwd, capture_output=True, text=True,
                          env={**os.environ, **(env or {})})


def project_version():
    import tomllib
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


# ---- check-version.sh ---------------------------------------------------------------------------

def test_a_tag_that_matches_pyproject_passes():
    assert run("check-version.sh", f"v{project_version()}").returncode == 0


def test_a_tag_that_differs_from_pyproject_fails_with_both_versions_in_the_message():
    done = run("check-version.sh", "v99.0.0")
    assert done.returncode != 0 and "99.0.0" in done.stderr and project_version() in done.stderr


@pytest.mark.parametrize("tag", ["1.0.0", "v1", "v1.0.0; rm -rf /", "v1.0.0 extra", "main", ""])
def test_a_malformed_tag_is_refused(tag):
    assert run("check-version.sh", tag).returncode != 0


# ---- release-notes.sh ---------------------------------------------------------------------------

@pytest.fixture
def repo(tmp_path):
    """A git repo with one annotated tag, and a fake `gh` that answers the release-notes API call."""
    git = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True, text=True)  # noqa: E731
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.org")
    git("config", "user.name", "T")
    (tmp_path / "f").write_text("x")
    git("add", "f")
    git("commit", "-q", "-m", "Merge pull request #9 from someone/branch")
    git("tag", "-a", "v1.2.3", "-m", "The headline of this release.\n\nA second paragraph.")
    git("tag", "v1.2.4")  # lightweight: no message of its own
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        'echo "$@" >> "$GH_LOG"\n'
        "cat <<'BODY'\n"
        "## What's Changed\n"
        "* Something merged in https://example.org/pull/1\n"
        "\n"
        "**Full Changelog**: https://example.org/compare\n"
        "BODY\n")
    fake.chmod(0o755)
    return tmp_path, {"PATH": f"{bin_dir}:{os.environ['PATH']}", "GH_LOG": str(tmp_path / "gh.log"),
                      "GITHUB_REPOSITORY": "Marceltov/passageway", "GH_TOKEN": "x"}


def test_release_notes_have_the_tag_message_the_merged_prs_and_install_instructions(repo):
    cwd, env = repo
    out = run("release-notes.sh", "v1.2.3", cwd=cwd, env=env)
    assert out.returncode == 0, out.stderr
    notes = out.stdout
    assert notes.startswith("The headline of this release.")
    assert "A second paragraph." in notes
    assert "Something merged" in notes and "Full Changelog" in notes
    assert "git+https://github.com/Marceltov/passageway@v1.2.3" in notes
    assert "#subdirectory=connectors/wikipedia" in notes
    assert "https://passageway.marceltov.de" in notes


def test_a_lightweight_tag_gets_no_borrowed_commit_message(repo):
    cwd, env = repo
    notes = run("release-notes.sh", "v1.2.4", cwd=cwd, env=env).stdout
    assert "Merge pull request" not in notes and notes.lstrip().startswith("## What")


def test_the_previous_tag_bounds_the_generated_list(repo):
    cwd, env = repo
    run("release-notes.sh", "v1.2.4", cwd=cwd, env=env)
    assert "previous_tag_name=v1.2.3" in (cwd / "gh.log").read_text()


def test_pre_release_and_stray_tags_never_become_the_previous_release(repo):
    cwd, env = repo
    git = lambda *a: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True)  # noqa: E731
    git("tag", "v1.2.4-rc1")
    git("tag", "vendor-sync")
    git("tag", "-a", "v1.2.5", "-m", "next")
    run("release-notes.sh", "v1.2.5", cwd=cwd, env=env)
    assert "previous_tag_name=v1.2.4 " in (cwd / "gh.log").read_text() + " "


def test_the_first_release_has_no_previous_tag(tmp_path):
    git = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True, text=True)  # noqa: E731
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.org")
    git("config", "user.name", "T")
    (tmp_path / "f").write_text("x")
    git("add", "f")
    git("commit", "-q", "-m", "first")
    git("tag", "-a", "v0.1.0", "-m", "First release.")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text('#!/usr/bin/env bash\necho "$@" >> "$GH_LOG"\necho "## What\'s Changed"\n')
    (bin_dir / "gh").chmod(0o755)
    env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "GH_LOG": str(tmp_path / "gh.log"),
           "GITHUB_REPOSITORY": "Marceltov/passageway"}
    done = run("release-notes.sh", "v0.1.0", cwd=tmp_path, env=env)
    assert done.returncode == 0 and "previous_tag_name" not in (tmp_path / "gh.log").read_text()


def test_an_empty_tag_message_adds_no_leading_blank_lines(repo):
    cwd, env = repo
    subprocess.run(["git", "tag", "-a", "v1.2.9", "-m", ""], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_EDITOR": "true"})
    notes = run("release-notes.sh", "v1.2.9", cwd=cwd, env=env).stdout
    assert notes.startswith("## What")


def test_a_tag_that_does_not_exist_fails_clearly_before_calling_github(repo):
    cwd, env = repo
    done = run("release-notes.sh", "v9.9.9", cwd=cwd, env=env)
    assert done.returncode != 0 and "no such tag" in done.stderr
    assert not (cwd / "gh.log").exists()


# ---- post-to-notefeed.sh ------------------------------------------------------------------------

class FakeNotefeed:
    def __init__(self):
        self.notes = []      # posted notes: {"headers": {...}, "body": str}
        self.requests = []   # (method, path, headers)
        self.fail_post = False


@pytest.fixture
def notefeed():
    state = FakeNotefeed()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            state.requests.append(("GET", self.path, dict(self.headers)))
            tag = parse_qs(url.query).get("tag", [None])[0]
            hits = [n for n in state.notes if tag in n["headers"].get("X-Note-Tags", "").split(",")]
            body = json.dumps({"notes": hits[:1]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            state.requests.append(("POST", self.path, dict(self.headers)))
            if state.fail_post:
                self.send_response(500)
                self.end_headers()
                return
            state.notes.append({"headers": dict(self.headers), "body": body})
            self.send_response(201)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    state.url = f"http://127.0.0.1:{server.server_port}"
    yield state
    server.shutdown()


def post(notefeed, tmp_path, tag="v1.2.3", **env):
    notes = tmp_path / "notes.md"
    notes.write_text("## Release\n\nWhat changed.\n")
    base = {"NOTEFEED_URL": notefeed.url, "NOTEFEED_FEED": "feedname", "NOTEFEED_FEED_PASSWORD": "pw",
            "GITHUB_REPOSITORY": "Marceltov/passageway"}
    return run("post-to-notefeed.sh", tag, str(notes), env={**base, **env})


def test_it_posts_the_notes_once_with_title_tags_and_password(notefeed, tmp_path):
    done = post(notefeed, tmp_path)
    assert done.returncode == 0, done.stderr
    assert len(notefeed.notes) == 1
    note = notefeed.notes[0]
    assert "What changed." in note["body"]
    assert note["headers"]["X-Note-Title"] == "passageway 1.2.3"
    assert note["headers"]["X-Note-Tags"] == "release,passageway,passageway-v1.2.3"
    assert note["headers"]["X-Feed-Password"] == "pw"
    assert note["headers"]["Content-Type"] == "text/markdown"


def test_a_rerun_does_not_post_twice(notefeed, tmp_path):
    post(notefeed, tmp_path)
    again = post(notefeed, tmp_path)
    assert again.returncode == 0 and "already on notefeed" in again.stdout
    assert len(notefeed.notes) == 1


def test_another_tag_is_a_new_note(notefeed, tmp_path):
    post(notefeed, tmp_path, tag="v1.2.3")
    post(notefeed, tmp_path, tag="v1.2.4")
    assert len(notefeed.notes) == 2


def test_without_the_feed_secret_it_posts_nothing_and_succeeds(notefeed, tmp_path):
    done = post(notefeed, tmp_path, NOTEFEED_FEED="")
    assert done.returncode == 0 and notefeed.requests == [] and "not posting" in done.stdout


def test_a_missing_repository_name_is_a_clear_error(notefeed, tmp_path):
    done = post(notefeed, tmp_path, GITHUB_REPOSITORY="")
    assert done.returncode != 0 and "GITHUB_REPOSITORY is not set" in done.stderr and notefeed.requests == []


def test_a_failed_post_fails_the_script(notefeed, tmp_path):
    notefeed.fail_post = True
    assert post(notefeed, tmp_path).returncode != 0


# ---- the workflow -------------------------------------------------------------------------------

def test_the_release_workflow_calls_only_scripts_that_exist_and_posts_with_the_secrets():
    import re

    import yaml

    text = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    workflow = yaml.safe_load(text)
    assert workflow[True]["push"]["tags"] == ["v*"]  # PyYAML reads the key `on` as True
    for script in set(re.findall(r"scripts/[\w.-]+\.sh", text)):
        path = ROOT / script
        assert path.is_file() and os.access(path, os.X_OK), f"{script} is called by the workflow but is not executable"
    assert re.search(r"secrets\.NOTEFEED_FEED_PASSWORD\s*}}", text) and re.search(r"secrets\.NOTEFEED_FEED\s*}}", text)
    assert "contents: write" in text
    # a user-supplied tag must never be interpolated into a shell command
    for step in workflow["jobs"]["release"]["steps"]:
        assert "inputs.tag" not in step.get("run", ""), "inputs.tag must go through the environment"
    # the tag is validated before any other step sees it
    first_run = next(step["run"] for step in workflow["jobs"]["release"]["steps"] if "run" in step)
    assert "check-version.sh" in first_run, "scripts/check-version.sh must be the first run step"
