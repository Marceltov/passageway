import json


def test_each_top_level_heading_is_an_item_of_the_file(sites):
    code, records, err = sites.call("list")
    assert code == 0, err
    ids = [r["id"] for r in records]
    assert ids == ["https://docs.example/llms-full.txt#install", "https://docs.example/llms-full.txt#configure"]


def test_a_page_has_its_title_sections_and_the_file_as_address(sites):
    page = sites.fetch("https://docs.example/llms-full.txt#install")["https://docs.example/llms-full.txt#install"]
    assert page["title"] == "Install" and page["url"] == "https://docs.example/llms-full.txt"
    assert page["path"] == ["docs.example"]
    assert {"heading": "Linux", "text": "Use the package manager."} in page["sections"]


def test_a_hash_in_a_code_block_does_not_start_a_page(sites):
    page = sites.fetch("https://docs.example/llms-full.txt#configure")["https://docs.example/llms-full.txt#configure"]
    assert "not a heading" in json.dumps(page["sections"])
    assert len(sites.call("list")[1]) == 2


def test_the_version_changes_only_when_a_page_changes(sites):
    before = {r["id"]: r["version"] for r in sites.call("list")[1]}
    sites.pages["https://docs.example/llms-full.txt"] = sites.pages["https://docs.example/llms-full.txt"].replace("installer", "setup tool")
    after = {r["id"]: r["version"] for r in sites.call("list")[1]}
    assert before["https://docs.example/llms-full.txt#configure"] == after["https://docs.example/llms-full.txt#configure"]
    assert before["https://docs.example/llms-full.txt#install"] != after["https://docs.example/llms-full.txt#install"]


def test_a_direct_url_and_several_sites_are_read(sites):
    sites.pages["https://other.example/docs/llms-full.txt"] = "# Other\n\nText."
    code, records, err = sites.call("list", URLS="https://docs.example|https://other.example/docs/llms-full.txt")
    assert code == 0, err
    assert len(records) == 3


def test_a_file_without_a_heading_is_one_item_named_after_the_host(sites):
    sites.pages["https://docs.example/llms-full.txt"] = "Just text."
    page = next(iter(sites.fetch("https://docs.example/llms-full.txt#docs-example").values()))
    assert page["title"] == "docs.example"


def test_a_missing_file_fails_the_whole_listing_so_nothing_is_deleted(sites):
    code, records, err = sites.call("list", URLS="https://docs.example|https://gone.example")
    assert code == 1 and records == [] and "gone.example" in err


def test_settings_are_checked(sites):
    assert sites.call("list", URLS="")[0] == 2
    assert sites.call("list", URLS="ftp://x.example")[0] == 2
    assert sites.call("list", MAX_BYTES="0")[0] == 2


def test_a_file_over_the_size_limit_fails_the_listing(sites):
    code, _, err = sites.call("list", MAX_BYTES="10")
    assert code == 1 and "MAX_BYTES" in err


def test_a_single_markdown_file_with_front_matter_is_one_item(sites):
    sites.pages["https://docs.example/SKILL.md"] = "---\nname: passageway\n---\n# Passageway\n\nAsk the sources.\n"
    code, records, err = sites.call("list", URLS="https://docs.example/SKILL.md")
    assert code == 0, err
    assert [r["id"] for r in records] == ["https://docs.example/SKILL.md#passageway"]
    page = sites.fetch("https://docs.example/SKILL.md#passageway", URLS="https://docs.example/SKILL.md")
    assert "name: passageway" not in json.dumps(page)  # the front matter is not indexed as text


def test_an_llms_txt_index_is_followed_page_by_page_on_the_same_host(sites):
    sites.pages["https://docs.example/llms.txt"] = (
        "# Example\n\n> A site.\n\n## Docs\n\n- [Start](https://docs.example/start.md): begin here\n"
        "- [Relative](/guide/setup.md)\n- [Elsewhere](https://evil.example/x.md)\n- [Start again](https://docs.example/start.md#top)\n")
    sites.pages["https://docs.example/start.md"] = "# Start\n\nBegin here."
    sites.pages["https://docs.example/guide/setup.md"] = "# Setup\n\nInstall it."
    code, records, err = sites.call("list", URLS="https://docs.example/llms.txt")
    assert code == 0, err
    assert [r["id"] for r in records] == ["https://docs.example/start.md#start", "https://docs.example/guide/setup.md#setup"]
    assert not any("evil.example" in url for url in sites.requests)


def test_a_broken_link_in_an_index_fails_the_listing(sites):
    sites.pages["https://docs.example/llms.txt"] = "# Example\n\n- [Gone](https://docs.example/gone.md)\n"
    code, records, err = sites.call("list", URLS="https://docs.example/llms.txt")
    assert code == 1 and records == [] and "gone.md" in err


def test_the_number_of_pages_followed_from_an_index_is_capped(sites):
    sites.pages["https://docs.example/llms.txt"] = "".join(f"- [P{n}](https://docs.example/p{n}.md)\n" for n in range(5))
    for n in range(5):
        sites.pages[f"https://docs.example/p{n}.md"] = f"# P{n}\n\ntext"
    code, records, err = sites.call("list", URLS="https://docs.example/llms.txt", MAX_PAGES="3")
    assert code == 0 and len(records) == 3 and "MAX_PAGES" in err


TEAMSCALE = """---
url: /changelog/v1/patch-releases.md
---

# Patch Releases

Fixes.

## Details

# Not a new page

Still the same page.

---
url: /howto/install.md
---

# Install

Run it.

---
url: /howto/no-heading.md
---

Text without any heading.
"""
FULL = "https://docs.example/llms-full.txt"


def test_front_matter_with_a_url_starts_a_page_wherever_it_is_in_the_file(sites):
    sites.pages[FULL] = TEAMSCALE
    ids = [r["id"] for r in sites.call("list")[1]]
    assert ids == [f"{FULL}#/changelog/v1/patch-releases.md", f"{FULL}#/howto/install.md", f"{FULL}#/howto/no-heading.md"]


def test_such_a_page_links_to_its_own_address_and_carries_its_folders(sites):
    sites.pages[FULL] = TEAMSCALE
    page = sites.fetch(f"{FULL}#/howto/install.md")[f"{FULL}#/howto/install.md"]
    assert page["url"] == "https://docs.example/howto/install"  # the .md of the file's path is dropped
    assert page["title"] == "Install"
    assert page["path"] == ["docs.example", "howto"]
    assert "url:" not in json.dumps(page["sections"])  # the front matter block is not text


def test_a_page_runs_to_the_next_block_even_over_its_own_headings(sites):
    sites.pages[FULL] = TEAMSCALE
    page = sites.fetch(f"{FULL}#/changelog/v1/patch-releases.md")[f"{FULL}#/changelog/v1/patch-releases.md"]
    assert "Still the same page" in json.dumps(page["sections"])
    assert page["path"] == ["docs.example", "changelog", "v1"]


def test_a_page_without_a_heading_is_titled_by_the_last_part_of_its_path(sites):
    sites.pages[FULL] = TEAMSCALE
    page = sites.fetch(f"{FULL}#/howto/no-heading.md")[f"{FULL}#/howto/no-heading.md"]
    assert page["title"] == "no-heading"


def test_text_before_the_first_block_is_still_indexed(sites):
    sites.pages[FULL] = "# Intro\n\nWelcome.\n\n" + TEAMSCALE
    ids = [r["id"] for r in sites.call("list")[1]]
    assert ids[0] == f"{FULL}#intro" and len(ids) == 4


def test_front_matter_in_a_code_block_is_not_a_page(sites):
    sites.pages[FULL] = "# Guide\n\n```\n---\nurl: /fake.md\n---\n```\n"
    assert [r["id"] for r in sites.call("list")[1]] == [f"{FULL}#guide"]


def test_a_weight_per_path_prefix_lowers_a_part_of_a_site(sites):
    sites.pages[FULL] = TEAMSCALE
    pages = sites.fetch(f"{FULL}#/changelog/v1/patch-releases.md", f"{FULL}#/howto/install.md", WEIGHTS="changelog=0.5")
    assert pages[f"{FULL}#/changelog/v1/patch-releases.md"]["weight"] == 0.5
    assert "weight" not in pages[f"{FULL}#/howto/install.md"]


def test_a_changed_weight_changes_the_version_so_the_index_follows(sites):
    sites.pages[FULL] = TEAMSCALE
    before = {r["id"]: r["version"] for r in sites.call("list")[1]}
    after = {r["id"]: r["version"] for r in sites.call("list", WEIGHTS="changelog=0.5")[1]}
    assert before[f"{FULL}#/changelog/v1/patch-releases.md"] != after[f"{FULL}#/changelog/v1/patch-releases.md"]
    assert before[f"{FULL}#/howto/install.md"] == after[f"{FULL}#/howto/install.md"]


def test_weights_are_checked(sites):
    for bad in ("changelog", "changelog=heavy", "changelog=0", "=0.5"):
        assert sites.call("list", WEIGHTS=bad)[0] == 2, bad
