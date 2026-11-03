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


def test_a_permalink_anchor_is_not_part_of_the_heading(web):
    web.pages[f"{SITE}/doc"] = (200, "text/html", html("Doc", '<h1>Doc<a class="headerlink" href="#doc" title="Permanent link">¶</a></h1>'
                                                       '<h2 id="a">Setup <a class="headerlink" href="#a">¶</a></h2><p>Text.</p>'))
    page = web.fetch(f"{SITE}/doc")[f"{SITE}/doc"]
    assert page["title"] == "Doc" and [s["heading"] for s in page["sections"]] == ["Setup"]


def test_inline_markup_does_not_add_spaces_inside_a_sentence(web):
    web.pages[f"{SITE}/doc"] = (200, "text/html", html("Doc", "<h1>Doc</h1><p>Edit <code>passageway.toml</code>, or the <em>env</em>file.</p>"))
    text = web.fetch(f"{SITE}/doc")[f"{SITE}/doc"]["sections"][0]["text"]
    assert text == "Edit passageway.toml, or the envfile."


def test_render_hands_pages_to_a_browser_that_builds_them(web):  # a JavaScript site: the served HTML is an empty shell
    web.pages[f"{SITE}/guide/setup"] = (200, "text/html", "<html><body><div id=app></div></body></html>")
    seen = []

    def render(url):
        seen.append(url)
        return 200, html("Setup", "<h1>Setup</h1><p>Built by script.</p>") if "setup" in url else web.pages[url][2]

    items = web.fetch(f"{SITE}/guide/setup", RENDER="true", render=render)
    assert seen == [f"{SITE}/guide/setup"]
    assert items[f"{SITE}/guide/setup"]["sections"][0]["text"] == "Built by script."


def test_render_follows_links_that_script_adds(web):
    def render(url):
        extra = '<a href="/hidden">more</a>' if url == f"{SITE}/" else ""
        return 200, html("P", f"<h1>P</h1><p>{url}</p>{extra}")

    assert f"{SITE}/hidden" in web.ids(RENDER="true", render=render)


def test_render_still_respects_robots_and_reports_a_failed_page(web):
    web.pages[f"{SITE}/robots.txt"] = (200, "text/plain", "User-agent: *\nDisallow: /guide/")
    calls = []

    def render(url):
        calls.append(url)
        return (500, "") if url == f"{SITE}/hidden" else (200, html("P", '<h1>P</h1><p>x</p><a href="/hidden">h</a>'))

    code, records, err = web.call("list", RENDER="true", render=render)
    assert code == 0 and f"{SITE}/guide/setup" not in calls and f"{SITE}/hidden" not in [r["id"] for r in records]
    assert "HTTP 500" in err


def test_render_without_playwright_is_a_settings_error(web, monkeypatch):
    import builtins
    real = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", lambda n, *a, **k: (_ for _ in ()).throw(ImportError()) if n.startswith("playwright") else real(n, *a, **k))
    code, _, err = web.call("list", RENDER="true")
    assert code != 0 and "passageway-connector-sitemap[render]" in err
