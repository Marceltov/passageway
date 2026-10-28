import os
import time
from datetime import datetime, timezone

import pytest

from passageway.protocol import parse_item


# ---- which files ----------------------------------------------------------------------------------

def test_markdown_files_are_found_in_subfolders_and_other_files_are_not(folder):
    folder.write("a.md", "A")
    folder.write("sub/b.markdown", "B")
    folder.write("c.txt", "C")
    folder.write("sub/deeper/d.md", "D")
    assert folder.ids() == ["a.md", "sub/b.markdown", "sub/deeper/d.md"]


def test_hidden_folders_and_files_and_node_modules_are_always_skipped(folder):
    folder.write("keep.md", "K")
    folder.write(".git/notes.md", "x")
    folder.write(".obsidian/plugins/readme.md", "x")
    folder.write(".hidden.md", "x")
    folder.write("node_modules/pkg/readme.md", "x")
    folder.write("sub/.trash/old.md", "x")
    assert folder.ids() == ["keep.md"]


def test_a_symlinked_folder_is_not_followed_and_a_symlink_loop_ends(folder):
    folder.write("real/a.md", "A")
    os.symlink(folder.root / "real", folder.root / "alias")
    os.symlink(folder.root, folder.root / "real" / "loop")
    assert folder.ids() == ["real/a.md"]


def test_a_symlinked_file_counts_only_if_it_points_inside_the_folder(folder, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.md"
    outside.write_text("secret")
    folder.write("inside.md", "I")
    os.symlink(folder.root / "inside.md", folder.root / "link-in.md")
    os.symlink(outside, folder.root / "link-out.md")
    assert folder.ids() == ["inside.md", "link-in.md"]


def test_include_replaces_the_default_and_exclude_removes(folder):
    for name in ("a.md", "docs/b.md", "docs/c.md", "docs/c.draft.md", "other/d.md", "e.txt"):
        folder.write(name, "x")
    assert folder.ids(INCLUDE="docs/**/*.md") == ["docs/b.md", "docs/c.draft.md", "docs/c.md"]
    assert folder.ids(INCLUDE="docs/*.md|a.md") == ["a.md", "docs/b.md", "docs/c.draft.md", "docs/c.md"]
    assert folder.ids(EXCLUDE="*.draft.md|other/**") == ["a.md", "docs/b.md", "docs/c.md"]  # no slash: any depth
    assert folder.ids(INCLUDE="*.txt") == ["e.txt"]


# ---- the item --------------------------------------------------------------------------------------

def test_the_item_is_valid_and_has_the_path_as_id_and_a_content_hash_as_version(folder):
    folder.write("guides/setup.md", "# Setup guide\n\nInstall it.\n")
    item = folder.fetch("guides/setup.md")["guides/setup.md"]
    parsed = parse_item(item)  # the core's own parser accepts it
    assert parsed.id == "guides/setup.md" and parsed.title == "Setup guide"
    assert parsed.path == ("guides",) and parsed.url.startswith("file://") and parsed.url.endswith("/guides/setup.md")
    assert [(s.heading, s.text) for s in parsed.sections] == [(None, "Install it.")]
    folder.write("guides/setup.md", "# Setup guide\n\nInstall it, then run it.\n")
    assert folder.fetch("guides/setup.md")["guides/setup.md"]["version"] != item["version"]


def test_the_version_ignores_nothing_a_change_to_the_front_matter_changes_it(folder):
    folder.write("a.md", "---\ntags: [x]\n---\nBody")
    before = folder.fetch("a.md")["a.md"]["version"]
    folder.write("a.md", "---\ntags: [y]\n---\nBody")
    assert folder.fetch("a.md")["a.md"]["version"] != before


def test_the_title_is_the_front_matter_title_else_the_first_heading_else_the_file_name(folder):
    folder.write("a.md", "---\ntitle: From front matter\n---\n# Heading\nbody")
    folder.write("b.md", "intro\n\n# From heading\nbody")
    folder.write("c-note.md", "just text")
    got = folder.fetch("a.md", "b.md", "c-note.md")
    assert [got[i]["title"] for i in ("a.md", "b.md", "c-note.md")] == ["From front matter", "From heading", "c-note"]


def test_front_matter_gives_url_updated_tags_weight_and_id(folder):
    folder.write("a.md", "---\nurl: https://example.org/a\nupdated: 2026-10-05\ntags: [ops, security]\n"
                         "weight: 1.5\nid: stable-a\n---\nBody")
    item = folder.fetch("stable-a")["stable-a"]
    assert (item["url"], item["updated"], item["labels"], item["weight"]) == (
        "https://example.org/a", "2026-10-05", ["ops", "security"], 1.5)


def test_tags_may_be_a_comma_separated_string_and_scalars_stay_text(folder):
    folder.write("a.md", "---\ntags: ops, security\n---\nBody")
    folder.write("b.md", "---\ntags:\n  - no\n  - 2026-10-28\n---\nBody")  # YAML 1.1 would make these False and a date
    got = folder.fetch("a.md", "b.md")
    assert got["a.md"]["labels"] == ["ops", "security"] and got["b.md"]["labels"] == ["no", "2026-10-28"]


def test_updated_defaults_to_the_modification_time_in_utc(folder):
    path = folder.write("a.md", "Body")
    os.utime(path, (1_700_000_000, 1_700_000_000))
    assert folder.fetch("a.md")["a.md"]["updated"] == "2023-11-14T22:13:20Z"


def test_the_front_matter_is_not_indexed_as_text(folder):
    folder.write("a.md", "---\ntitle: T\nsecret_key: zebra-key\n---\nBody text")
    sections = folder.fetch("a.md")["a.md"]["sections"]
    assert [s["text"] for s in sections] == ["Body text"]


def test_broken_front_matter_warns_and_the_note_is_still_indexed(folder):
    folder.write("a.md", "---\ntitle: [unclosed\n---\nBody text")
    code, records, err = folder.call("fetch", '{"id": "a.md"}\n')
    assert code == 0 and records[0]["title"] == "a" and records[0]["sections"][0]["text"] == "Body text"
    assert "a.md" in err and "front matter" in err


def test_a_front_matter_that_is_not_a_mapping_is_ignored_with_a_warning(folder):
    folder.write("a.md", "---\n- just\n- a list\n---\nBody")
    code, records, err = folder.call("fetch", '{"id": "a.md"}\n')
    assert code == 0 and records[0]["sections"][0]["text"] == "Body" and "front matter" in err


def test_an_unclosed_fence_means_no_front_matter(folder):
    folder.write("a.md", "---\nnot front matter, a rule above text\n")
    assert folder.fetch("a.md")["a.md"]["sections"][0]["text"].startswith("---")


def test_a_bad_weight_is_ignored_with_a_warning(folder):
    folder.write("a.md", "---\nweight: heavy\n---\nBody")
    code, records, err = folder.call("fetch", '{"id": "a.md"}\n')
    assert code == 0 and "weight" not in records[0] and "weight" in err


def test_sections_follow_the_headings_and_the_first_h1_is_the_title(folder):
    folder.write("a.md", "# Guide\nIntro.\n\n## Setup\nInstall.\n\n### Linux\nApt.\n")
    item = folder.fetch("a.md")["a.md"]
    assert item["title"] == "Guide"
    assert [(s["heading"], s["text"]) for s in item["sections"]] == [
        (None, "Intro."), ("Setup", "Install."), ("Setup › Linux", "Apt.")]


# ---- ids ------------------------------------------------------------------------------------------

def test_two_notes_with_the_same_id_fail_the_call_naming_both(folder):
    folder.write("a.md", "---\nid: same\n---\nA")
    folder.write("sub/b.md", "---\nid: same\n---\nB")
    code, records, err = folder.call("list")
    assert code == 1 and records == [] and "same" in err and "a.md" in err and "sub/b.md" in err


# ---- links ----------------------------------------------------------------------------------------

def test_links_to_other_notes_become_ids_of_existing_files(folder):
    folder.write("guides/setup.md", "Setup")
    folder.write("guides/usage.md", "Usage")
    folder.write("index.md", "See [setup](guides/setup.md#linux), [usage](guides/usage.md?x=1), "
                             "[web](https://example.org/x.md), [gone](missing.md), [anchor](#top), "
                             "and [encoded](guides/set%75p.md).")
    assert folder.fetch("index.md")["index.md"]["links"] == ["guides/setup.md", "guides/usage.md"]


def test_relative_links_resolve_from_the_notes_own_folder(folder):
    folder.write("a/one.md", "[two](../b/two.md) and [three](./three.md)")
    folder.write("b/two.md", "Two")
    folder.write("a/three.md", "Three")
    assert folder.fetch("a/one.md")["a/one.md"]["links"] == ["b/two.md", "a/three.md"]


def test_wiki_links_match_the_file_name_ignoring_case_and_skip_ambiguous_names(folder):
    folder.write("Setup.md", "S")
    folder.write("x/Dup.md", "D1")
    folder.write("y/dup.md", "D2")
    folder.write("n.md", "[[setup]] [[Setup|the guide]] [[Dup]] [[Nothing]] [[Setup#Linux]]")
    assert folder.fetch("n.md")["n.md"]["links"] == ["Setup.md"]


def test_links_use_front_matter_ids_and_ignore_code(folder):
    folder.write("target.md", "---\nid: stable-target\n---\nT")
    folder.write("other.md", "O")
    folder.write("n.md", "[t](target.md)\n```\n[o](other.md)\n```\nand `[o](other.md)` inline")
    assert folder.fetch("n.md")["n.md"]["links"] == ["stable-target"]


def test_a_note_does_not_link_to_itself(folder):
    folder.write("a.md", "[me](a.md) [[a]]")
    assert "links" not in folder.fetch("a.md")["a.md"]


# ---- bad files --------------------------------------------------------------------------------------

def test_a_bom_is_removed(folder):
    folder.write("a.md", b"\xef\xbb\xbf# Title\n\nBody", binary=True)
    item = folder.fetch("a.md")["a.md"]
    assert item["title"] == "Title" and item["sections"][0]["text"] == "Body"


def test_files_that_are_not_text_are_skipped_with_a_warning(folder):
    folder.write("ok.md", "fine")
    folder.write("latin.md", "caf\xe9".encode("latin-1"), binary=True)
    folder.write("binary.md", b"abc\x00def", binary=True)
    code, records, err = folder.call("list")
    assert code == 0 and [r["id"] for r in records] == ["ok.md"]
    assert "latin.md" in err and "binary.md" in err


def test_a_file_over_the_limit_is_skipped_with_a_warning(folder):
    folder.write("small.md", "x" * 100)
    folder.write("big.md", "x" * 101)
    code, records, err = folder.call("list", MAX_FILE_BYTES="100")
    assert code == 0 and [r["id"] for r in records] == ["small.md"] and "big.md" in err


def test_a_file_that_vanishes_between_list_and_fetch_is_skipped(folder):
    path = folder.write("a.md", "A")
    folder.write("b.md", "B")
    assert folder.ids() == ["a.md", "b.md"]
    path.unlink()
    assert list(folder.fetch("a.md", "b.md")) == ["b.md"]


def test_non_ascii_text_is_written_ascii_safe(folder):
    folder.write("a.md", "# Köln\n\nGröße", )
    code, records, _ = folder.call("fetch", '{"id": "a.md"}\n')
    assert records[0]["title"] == "Köln" and records[0]["sections"][0]["text"] == "Größe"


# ---- check and changed ------------------------------------------------------------------------------

def test_check_counts_the_notes(folder):
    folder.write("a.md", "A")
    folder.write("b.md", "B")
    assert folder.call("check")[:2] == (0, [{"ok": True, "count": 2, "protocol": "1"}])


def test_changed_returns_the_notes_modified_or_moved_in_since(folder):
    soon = int(time.time()) + 3600  # whole seconds: a fraction can be stored a few nanoseconds short
    old = folder.write("old.md", "Old")
    new = folder.write("new.md", "New")
    os.utime(old, (1_700_000_000, 1_700_000_000))  # an old mtime, but its ctime is now: it was just put here
    os.utime(new, (soon, soon))
    now = datetime.fromtimestamp(time.time() - 60, timezone.utc).isoformat()
    assert sorted(r["id"] for r in folder.call("changed", extra=["--since", now])[1]) == ["new.md", "old.md"]
    later = datetime.fromtimestamp(time.time() + 60, timezone.utc).isoformat()  # after the move, before the mtime of new
    assert [r["id"] for r in folder.call("changed", extra=["--since", later])[1]] == ["new.md"]
    exact = datetime.fromtimestamp(soon, timezone.utc).isoformat()
    assert [r["id"] for r in folder.call("changed", extra=["--since", exact])[1]] == ["new.md"]  # inclusive


# ---- settings ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("settings,message", [
    ({"FOLDER": ""}, "FOLDER"),
    ({"FOLDER": "/no/such/folder"}, "FOLDER"),
    ({"MAX_FILE_BYTES": "lots"}, "MAX_FILE_BYTES"),
    ({"MAX_FILE_BYTES": "0"}, "MAX_FILE_BYTES"),
])
def test_bad_settings_exit_2_with_a_message_and_no_output(folder, settings, message):
    import io

    from passageway_connector_markdown.connector import Markdown
    out, err = io.StringIO(), io.StringIO()
    env = {"FOLDER": str(folder.root), **settings}
    assert Markdown.run(["markdown", "list"], env, io.StringIO(), out, err) == 2
    assert out.getvalue() == "" and message in err.getvalue()


# ---- review findings ------------------------------------------------------------------------------

def test_deeply_nested_front_matter_warns_and_does_not_fail_the_source(folder):
    folder.write("deep.md", "---\nx: " + "[" * 5000 + "]" * 5000 + "\n---\nBody")
    folder.write("good.md", "Good")
    code, records, err = folder.call("list")
    assert code == 0 and sorted(r["id"] for r in records) == ["deep.md", "good.md"] and "deep.md" in err


@pytest.mark.parametrize("text", ["[" * 300_000, "[[" * 150_000, "[a](" * 75_000])
def test_a_pathological_line_does_not_make_link_finding_slow(folder, text):
    folder.write("a.md", text)
    started = time.monotonic()
    assert folder.fetch("a.md")["a.md"]["id"] == "a.md"
    assert time.monotonic() - started < 5


def test_the_version_changes_when_a_link_starts_to_resolve(folder):
    folder.write("a.md", "see [[New Idea]] and [x](other.md)")
    before = folder.call("list")[1][0]["version"]
    folder.write("New Idea.md", "N")
    folder.write("other.md", "O")
    after = {r["id"]: r["version"] for r in folder.call("list")[1]}
    assert after["a.md"] != before
    assert folder.fetch("a.md")["a.md"]["links"] == ["New Idea.md", "other.md"]


def test_an_h1_that_is_not_the_title_stays_a_heading(folder):
    folder.write("a.md", "---\ntitle: Front\n---\n# Intro\ntext\n## Setup\nx")
    item = folder.fetch("a.md")["a.md"]
    assert item["title"] == "Front"
    assert [(s["heading"], s["text"]) for s in item["sections"]] == [("Intro", "text"), ("Intro › Setup", "x")]


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read anything")
def test_an_unreadable_folder_is_reported_not_silently_dropped(folder):
    folder.write("top.md", "T")
    folder.write("locked/a.md", "A")
    (folder.root / "locked").chmod(0)
    try:
        code, records, err = folder.call("list")
    finally:
        (folder.root / "locked").chmod(0o755)
    assert code == 0 and [r["id"] for r in records] == ["top.md"] and "locked" in err


def test_a_wiki_link_with_a_folder_picks_the_right_one_of_two_same_named_notes(folder):
    folder.write("a/Note.md", "A")
    folder.write("b/Note.md", "B")
    folder.write("n.md", "[[a/Note]] and [[b/Note|the other]] and [[Note]]")
    assert folder.fetch("n.md")["n.md"]["links"] == ["a/Note.md", "b/Note.md"]


def test_a_link_target_in_angle_brackets_may_contain_spaces(folder):
    folder.write("my note.md", "M")
    folder.write("n.md", "[x](<my note.md>) and [y](<my note.md> \"title\")")
    assert folder.fetch("n.md")["n.md"]["links"] == ["my note.md"]


def test_an_escaped_pipe_in_a_wiki_link_inside_a_table(folder):
    folder.write("Setup.md", "S")
    folder.write("n.md", "| a |\n|---|\n| [[Setup\\|the guide]] |")
    assert folder.fetch("n.md")["n.md"]["links"] == ["Setup.md"]


def test_the_yaml_document_end_marker_closes_the_front_matter(folder):
    folder.write("a.md", "---\ntitle: T\n...\nBody")
    item = folder.fetch("a.md")["a.md"]
    assert item["title"] == "T" and item["sections"][0]["text"] == "Body"
