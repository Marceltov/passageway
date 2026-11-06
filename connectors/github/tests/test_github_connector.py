import hashlib


def sha(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()


def test_by_default_the_markdown_files_of_the_default_branch_are_the_items(github):
    assert sorted(github.versions()) == ["acme/docs/README.md", "acme/docs/guide/notes.markdown", "acme/docs/guide/setup.md"]


def test_the_version_is_the_blob_sha_so_listing_reads_no_file(github):
    versions = github.versions()
    assert versions["acme/docs/README.md"] == sha(github.repos["acme/docs"]["files"]["README.md"].encode())
    assert not [r for r in github.requests if "/git/blobs/" in r.url.path]


def test_a_markdown_file_has_its_heading_as_title_its_sections_and_a_link_to_github(github):
    item = github.fetch("acme/docs/guide/setup.md")["acme/docs/guide/setup.md"]
    assert item["title"] == "Setup"
    assert item["url"] == "https://github.com/acme/docs/blob/main/guide/setup.md"
    assert item["path"] == ["acme/docs", "guide"]
    assert item["sections"] == [{"heading": None, "text": "Install it."}, {"heading": "Linux", "text": "Use the package manager."}]


def test_a_file_without_a_heading_is_titled_by_its_name_and_the_root_readme_by_the_repository(github):
    items = github.fetch("acme/docs/guide/notes.markdown", "acme/docs/README.md")
    assert items["acme/docs/guide/notes.markdown"]["title"] == "notes.markdown"
    assert items["acme/docs/README.md"]["title"] == "acme/docs"
    assert items["acme/docs/README.md"]["sections"] == [{"heading": "Acme docs", "text": "Start here."}]


def test_files_takes_globs_and_code_is_cut_into_line_ranges(github):
    assert "acme/docs/src/app.py" in github.versions(FILES="*.md|src/**/*.py")
    item = github.fetch("acme/docs/src/app.py", FILES="src/*.py")["acme/docs/src/app.py"]
    assert item["title"] == "app.py" and item["url"] == "https://github.com/acme/docs/blob/main/src/app.py"
    headings = [s["heading"] for s in item["sections"]]
    assert headings[0].startswith("Lines 1–") and len(headings) >= 2
    assert all(s["text"].startswith("def f") for s in item["sections"])  # a cut falls between functions, not inside one
    assert "\n".join(s["text"] for s in item["sections"]).count("def f") == 40


def test_binary_and_oversized_files_are_skipped_with_a_warning(github):
    code, records, err = github.call("fetch", '{"id": "acme/docs/logo.png"}\n', FILES="*.png")
    assert code == 0 and records == [] and "logo.png" in err
    code, records, err = github.call("list", MAX_FILE_BYTES="20")
    assert code == 0 and [r["id"] for r in records] == ["acme/docs/guide/notes.markdown"] and "MAX_FILE_BYTES" in err


def test_exclude_leaves_files_out(github):
    assert sorted(github.versions(EXCLUDE="guide/**")) == ["acme/docs/README.md"]


def test_an_owner_wildcard_takes_its_repositories_without_forks_and_archived_ones(github):
    assert {i.split("/")[1] for i in github.versions(REPOS="acme/*")} == {"docs"}
    assert {i.split("/")[1] for i in github.versions(REPOS="acme/*", FORKS="true", ARCHIVED="true")} == {"docs", "old", "forked"}
    assert list(github.versions(REPOS="ann/*")) == ["ann/notes/ideas.md"]


def test_a_token_reaches_private_repositories(github):
    assert "acme/secret/README.md" not in github.versions(REPOS="acme/*")
    item = github.fetch("acme/secret/README.md", REPOS="acme/*", TOKEN="t0ken")["acme/secret/README.md"]
    assert item["url"] == "https://github.com/acme/secret/blob/trunk/README.md"
    assert all(r.headers["authorization"] == "Bearer t0ken" for r in github.requests[-3:])


def test_a_branch_can_be_named_and_is_part_of_the_id(github):
    github.repos["acme/docs"]["default_branch"] = "develop"
    assert "acme/docs@develop/README.md" in github.versions(REPOS="acme/docs@develop")


def test_an_edit_changes_only_that_files_version(github):
    before = github.versions()
    github.repos["acme/docs"]["files"]["README.md"] = "# Acme docs\n\nStart over here.\n"
    after = github.versions()
    assert [i for i in before if before[i] != after[i]] == ["acme/docs/README.md"]


def test_fetch_reads_one_blob_per_file(github):
    github.fetch("acme/docs/README.md", "acme/docs/guide/setup.md")
    assert len([r for r in github.requests if "/git/blobs/" in r.url.path]) == 2


def test_fetch_skips_ids_that_are_gone_or_of_no_configured_repository(github):
    assert github.fetch("acme/docs/gone.md", "other/repo/README.md", "nonsense") == {}


def test_a_missing_repository_fails_the_listing_and_says_a_token_may_be_needed(github):
    code, records, err = github.call("list", REPOS="acme/nope")
    assert code == 1 and records == [] and "acme/nope" in err and "TOKEN" in err


def test_a_used_up_rate_limit_fails_the_listing_and_says_what_to_do(github):
    github.rate_limited = True
    code, _, err = github.call("list")
    assert code == 1 and "rate limit" in err and "TOKEN" in err


def test_a_bad_token_and_a_server_that_is_down_fail_the_listing(github):
    code, _, err = github.call("list", TOKEN="wrong")
    assert code == 1 and "TOKEN" in err
    github.down = True
    assert github.call("list")[0] == 1


def test_too_many_files_are_cut_with_a_warning(github):
    code, records, err = github.call("list", MAX_FILES="2")
    assert code == 0 and len(records) == 2 and "MAX_FILES" in err


def test_the_api_address_can_point_at_github_enterprise(github):
    github.versions(API_URL="https://ghe.example/api/v3/")
    assert all(str(r.url).startswith("https://ghe.example/api/v3/") for r in github.requests)


def test_settings_are_checked(github):
    for bad in ({"REPOS": ""}, {"REPOS": "justaname"}, {"REPOS": "a/b/c"}, {"MAX_FILES": "0"}, {"FORKS": "maybe"},
                {"API_URL": "ftp://x"}):
        assert github.call("list", **bad)[0] == 2, bad

