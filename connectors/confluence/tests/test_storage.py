"""Confluence's storage format becomes readable text without losing what a page says."""

import pytest

from passageway_connector_confluence.connector import storage_to_html
from passageway_connector_confluence.html import html_to_sections


def text(storage):
    return [(" › ".join(s.heading_path) or None, s.text) for s in html_to_sections(storage_to_html(storage))]


def test_a_self_closing_macro_with_attributes_does_not_swallow_what_follows():
    out = text('<ac:structured-macro ac:name="toc" ac:schema-version="1" ac:macro-id="m1" /><h2>A</h2><p>a</p>'
               '<ac:structured-macro ac:name="info" ac:schema-version="1"><ac:rich-text-body><p>tip</p></ac:rich-text-body></ac:structured-macro>')
    assert out == [("A", "a\ntip")]


def test_nested_macros_keep_every_part_in_order():
    out = text('<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">More</ac:parameter><ac:rich-text-body>'
               '<p>Before</p><ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[echo hi]]></ac:plain-text-body></ac:structured-macro>'
               '<p>After code</p><ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[two]]></ac:plain-text-body></ac:structured-macro>'
               '</ac:rich-text-body></ac:structured-macro><p>Tail</p>')
    assert out == [(None, "Before\necho hi\nAfter code\ntwo\nTail")]


def test_a_user_mention_and_a_later_title_link_do_not_delete_the_sections_between():
    out = text('<p>Owner: <ac:link><ri:user ri:userkey="abc"/></ac:link></p><h2>Install</h2><p>Run the installer.</p>'
               '<h2>Rollback</h2><p>See <ac:link><ri:page ri:content-title="FAQ"/></ac:link>.</p>')
    assert out == [(None, "Owner:"), ("Install", "Run the installer."), ("Rollback", "See FAQ.")]


def test_code_keeps_its_markup_as_text():
    out = text('<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[<div class="x">a & b</div> <ac:foo>keep</ac:foo>]]></ac:plain-text-body></ac:structured-macro>')
    assert out == [(None, '<div class="x">a & b</div> <ac:foo>keep</ac:foo>')]


def test_task_lists_placeholders_and_status_macros():
    out = text('<ac:task-list><ac:task><ac:task-id>1</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>Buy milk</ac:task-body></ac:task>'
               '<ac:task><ac:task-id>2</ac:task-id><ac:task-status>complete</ac:task-status><ac:task-body>Ship</ac:task-body></ac:task></ac:task-list>'
               '<p><ac:placeholder>Type here</ac:placeholder>Real</p><p>State: <ac:structured-macro ac:name="status"><ac:parameter ac:name="title">DONE</ac:parameter></ac:structured-macro></p>')
    assert out == [(None, "- Buy milk\n- Ship\nReal\nState: DONE")]


def test_links_images_emoticons_layouts_and_entities():
    out = text('<ac:layout><ac:layout-section><ac:layout-cell><p>Left &amp; <ac:emoticon ac:name="smile"/> &nbsp;&eacute;</p>'
               '<p><ac:link><ri:page ri:space-key="OPS" ri:content-title="Deploying"/><ac:link-body><strong>deploy</strong> it</ac:link-body></ac:link></p>'
               '<ac:image><ri:attachment ri:filename="x.png"/></ac:image><p>Tail</p></ac:layout-cell></ac:layout-section></ac:layout>')
    assert out == [(None, "Left & é\ndeploy it\nTail")]


def test_malformed_storage_still_gives_text():
    assert text("<p>a <b>bold</p> unclosed & stray") == [(None, "a bold\nunclosed & stray")]


def test_headings_below_h3_stay_in_the_text():
    assert text("<h2>A</h2><h4>Sub</h4><p>x</p>") == [("A", "Sub\nx")]
