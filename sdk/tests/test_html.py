from passageway_sdk.html import clean, to_markdown
from selectolax.lexbor import LexborHTMLParser


def test_headings_paragraphs_lists_and_code_become_markdown():
    html = ("<h1>Setup</h1><p>Install it.</p><h2>Linux</h2><ul><li>apt</li><li>dnf</li></ul>"
            "<pre><code>uv sync\nuv run pytest</code></pre>")
    assert to_markdown(html) == "# Setup\n\nInstall it.\n\n## Linux\n\n- apt\n\n- dnf\n\n```\nuv sync\nuv run pytest\n```"


def test_inline_markup_adds_no_space_inside_a_sentence():
    assert to_markdown("<p>Edit <code>passageway.toml</code>, or the <em>env</em>file.</p>") == "Edit passageway.toml, or the envfile."


def test_navigation_scripts_and_permalink_anchors_are_left_out():
    html = '<nav>Home</nav><h2 id="a">Setup <a class="headerlink" href="#a">¶</a></h2><script>x()</script><p>Text.</p>'
    assert to_markdown(html) == "## Setup\n\nText."


def test_a_parsed_node_works_as_well_as_a_string():
    tree = LexborHTMLParser("<body><nav>x</nav><main><p>Only this.</p></main></body>")
    assert to_markdown(tree.css_first("main")) == "Only this."


def test_clean_collapses_whitespace():
    assert clean("  a \n\t b  ") == "a b"
