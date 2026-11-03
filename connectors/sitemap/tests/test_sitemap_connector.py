from conftest import SITE, html


def test_the_pages_of_the_sitemap_and_the_links_on_them_are_indexed(web):
    assert web.ids() == [f"{SITE}/", f"{SITE}/guide/setup", f"{SITE}/hidden"]


def test_links_are_not_followed_when_asked_not_to(web):
    assert web.ids(FOLLOW_LINKS="false") == [f"{SITE}/", f"{SITE}/guide/setup"]


def test_links_to_other_hosts_are_never_followed(web):
    web.ids()
    assert not any("other.example" in r for r in web.requests)


def test_a_page_has_title_sections_path_and_no_navigation(web):
    page = web.fetch(f"{SITE}/guide/setup")[f"{SITE}/guide/setup"]
    assert page["title"] == "Setup" and page["url"] == f"{SITE}/guide/setup" and page["path"] == ["guide"]
    assert {"heading": "Linux", "text": "Use apt.\n\n```\napt install x\n```"} in page["sections"]
    text = str(page["sections"])
    assert "Menu Home" not in text and "Copyright" not in text


def test_a_page_links_to_the_pages_it_links_to(web):
    page = web.fetch(f"{SITE}/")[f"{SITE}/"]
    assert page["links"] == [f"{SITE}/guide/setup", f"{SITE}/hidden"]


def test_the_version_changes_only_when_the_text_changes(web):
    before = {r["id"]: r["version"] for r in web.call("list")[1]}
    web.pages[f"{SITE}/guide/setup"] = (200, "text/html", html("Setup", "<h1>Setup</h1><p>Install it twice.</p>"))
    after = {r["id"]: r["version"] for r in web.call("list")[1]}
    assert before[f"{SITE}/"] == after[f"{SITE}/"] and before[f"{SITE}/guide/setup"] != after[f"{SITE}/guide/setup"]


def test_a_sitemap_index_is_followed(web):
    web.pages[f"{SITE}/sitemap.xml"] = (200, "application/xml", f"<sitemapindex><sitemap><loc>{SITE}/s1.xml</loc></sitemap></sitemapindex>")
    web.pages[f"{SITE}/s1.xml"] = (200, "application/xml", f"<urlset><url><loc>{SITE}/hidden</loc></url></urlset>")
    assert web.ids(FOLLOW_LINKS="false") == [f"{SITE}/hidden"]


def test_a_site_address_means_its_sitemap_xml(web):
    assert web.ids(SITEMAP=SITE, FOLLOW_LINKS="false") == [f"{SITE}/", f"{SITE}/guide/setup"]


def test_include_and_exclude_are_url_prefixes(web):
    assert web.ids(EXCLUDE=f"{SITE}/hidden") == [f"{SITE}/", f"{SITE}/guide/setup"]
    assert web.ids(INCLUDE=f"{SITE}/guide", FOLLOW_LINKS="false") == [f"{SITE}/guide/setup"]


def test_robots_txt_is_respected(web):
    web.pages[f"{SITE}/robots.txt"] = (200, "text/plain", "User-agent: *\nDisallow: /guide/\n")
    assert web.ids() == [f"{SITE}/", f"{SITE}/hidden"]
    assert f"{SITE}/guide/setup" not in web.requests
    web.requests.clear()
    assert f"{SITE}/guide/setup" in web.ids(RESPECT_ROBOTS="false")


def test_a_missing_page_is_skipped_with_a_warning(web):
    del web.pages[f"{SITE}/guide/setup"]
    code, records, err = web.call("list")
    assert code == 0 and [r["id"] for r in records] == [f"{SITE}/", f"{SITE}/hidden"] and "guide/setup" in err


def test_a_server_error_fails_the_listing_so_nothing_is_deleted(web):
    web.pages[f"{SITE}/guide/setup"] = (503, "text/plain", "busy")
    code, records, err = web.call("list")
    assert code == 1 and records == [] and "503" in err


def test_a_failing_sitemap_fails_the_listing(web):
    del web.pages[f"{SITE}/sitemap.xml"]
    code, records, err = web.call("list")
    assert code == 1 and "sitemap.xml" in err


def test_pages_that_are_not_html_are_skipped(web):
    web.pages[f"{SITE}/guide/setup"] = (200, "application/pdf", "%PDF")
    assert f"{SITE}/guide/setup" not in web.ids()


def test_the_number_of_pages_is_capped(web):
    code, records, err = web.call("list", MAX_PAGES="2")
    assert code == 0 and len(records) == 2 and "MAX_PAGES" in err


def test_settings_are_checked(web):
    assert web.call("list", SITEMAP="")[0] == 2
    assert web.call("list", SITEMAP="ftp://x.example/s.xml")[0] == 2
    assert web.call("list", MAX_PAGES="0")[0] == 2
    assert web.call("list", PAUSE="-1")[0] == 2
    assert web.call("list", FOLLOW_LINKS="maybe")[0] == 2
