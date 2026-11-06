import json

SITE = "https://docs.example"  # the site of the fixture


def test_every_section_with_text_is_an_item_whose_address_opens_at_its_heading(sites):
    assert set(sites.versions()) == {f"{SITE}/", f"{SITE}/guide/setup/", f"{SITE}/guide/setup/#linux", f"{SITE}/changelog/"}


def test_a_section_carries_its_page_title_and_heading_and_the_folders_as_breadcrumb(sites):
    item = sites.fetch(f"{SITE}/guide/setup/#linux")[f"{SITE}/guide/setup/#linux"]
    assert item["title"] == "Setup"
    assert item["url"] == f"{SITE}/guide/setup/#linux"
    assert item["path"] == ["guide", "setup"]
    assert item["sections"] == [{"heading": "Linux", "text": "Use the apt package.\n\n```\napt install example\n```"}]


def test_the_text_before_the_first_heading_is_the_page_item(sites):
    item = sites.fetch(f"{SITE}/guide/setup/")[f"{SITE}/guide/setup/"]
    assert item["title"] == "Setup" and item["sections"] == [{"heading": None, "text": "How to set it up."}]


def test_plain_mkdocs_repeats_the_whole_page_in_its_page_entry_and_only_the_intro_is_kept(sites):
    # mkdocs' own search plugin: tag-stripped text, and the page entry holds the whole page, headings included
    sites.pages[f"{SITE}/search/search_index.json"] = {"docs": [
        {"location": "setup/", "title": "Setup", "text": "How to set it up. Linux Use the package. Windows Use the installer."},
        {"location": "setup/#linux", "title": "Linux", "text": "Use the package."},
        {"location": "setup/#windows", "title": "Windows", "text": "Use the installer."},
    ]}
    items = sites.fetch(f"{SITE}/setup/", f"{SITE}/setup/#windows")
    assert items[f"{SITE}/setup/"]["sections"] == [{"heading": None, "text": "How to set it up."}]
    assert items[f"{SITE}/setup/#windows"]["sections"] == [{"heading": "Windows", "text": "Use the installer."}]


def test_a_site_under_a_path_and_an_index_address_both_work(sites):
    sites.pages["https://user.example/project/search/search_index.json"] = sites.index
    assert f"https://user.example/project/guide/setup/#linux" in sites.versions(URLS="https://user.example/project")
    assert f"https://user.example/project/changelog/" in sites.versions(URLS="https://user.example/project/search/search_index.json")


def test_an_edit_changes_only_that_sections_version(sites):
    before = sites.versions()
    index = json.loads(json.dumps(sites.index))
    index["docs"][2]["text"] = "<p>Use the <code>dnf</code> package.</p>"
    sites.pages[f"{SITE}/search/search_index.json"] = index
    after = sites.versions()
    assert [i for i in before if before[i] != after[i]] == [f"{SITE}/guide/setup/#linux"]


def test_a_weight_per_path_prefix_lowers_a_part_of_a_site_and_changes_its_version(sites):
    before = sites.versions()
    items = sites.fetch(f"{SITE}/changelog/", f"{SITE}/guide/setup/", WEIGHTS="changelog=0.5")
    assert items[f"{SITE}/changelog/"]["weight"] == 0.5 and "weight" not in items[f"{SITE}/guide/setup/"]
    assert sites.versions(WEIGHTS="changelog=0.5")[f"{SITE}/changelog/"] != before[f"{SITE}/changelog/"]


def test_a_site_without_a_search_index_fails_the_listing_and_names_it(sites):
    code, records, err = sites.call("list", URLS="https://other.example")
    assert code == 1 and records == [] and "https://other.example/search/search_index.json" in err


def test_a_server_that_is_down_fails_the_listing(sites):
    sites.status = 503
    assert sites.call("list")[0] == 1


def test_an_index_that_is_not_an_mkdocs_index_fails_the_listing(sites):
    sites.pages[f"{SITE}/search/search_index.json"] = "<html>not json</html>"
    code, _, err = sites.call("list")
    assert code == 1 and "search index" in err


def test_fetch_skips_ids_that_are_gone_or_belong_to_no_site(sites):
    assert sites.fetch(f"{SITE}/gone/", "https://elsewhere.example/x/", "not an address") == {}


def test_settings_are_checked(sites):
    for bad in ({"URLS": ""}, {"URLS": "ftp://docs.example"}, {"WEIGHTS": "changelog"}, {"MAX_BYTES": "0"}):
        assert sites.call("list", **bad)[0] == 2, bad
