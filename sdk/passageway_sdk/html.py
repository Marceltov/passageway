"""HTML to markdown-ish text for connectors whose source is a web page. Needs the extra: `pip install passageway-sdk[html]`."""

import re

try:
    from selectolax.lexbor import LexborHTMLParser, LexborNode
except ImportError as e:  # the SDK itself has no dependencies; this module is the one that has
    raise ImportError("passageway_sdk.html needs selectolax: install passageway-sdk[html]") from e

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "iframe", "template", "head", "button"}
LEAF_TAGS = {"p", "td", "th", "dt", "dd", "figcaption", "summary", "caption"}
BLOCK_TAGS = {"p", "div", "li", "ul", "ol", "table", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote",
              "section", "article", "figure", "details", "summary", "dt", "dd", "br"}


def clean(s: str) -> str:
    """Runs of whitespace as one space, trimmed."""
    return re.sub(r"\s+", " ", s).strip()


def _inline(node: LexborNode) -> str:
    """The text of a node: markup inside a sentence adds no space, a block or a line break does; permalink anchors are left out."""
    parts = []
    for child in node.iter(include_text=True):
        if child.tag == "-text":
            parts.append(child.text_content or "")
        elif child.tag in SKIP_TAGS or "headerlink" in (child.attributes.get("class") or "").split():
            continue
        elif child.tag in BLOCK_TAGS:
            parts.append(f" {_inline(child)} ")
        else:
            parts.append(_inline(child))
    return clean("".join(parts))


def _blocks(node: LexborNode, out: list[str]) -> None:
    for child in node.iter(include_text=True):
        tag = child.tag
        if tag == "-text":
            if text := clean(child.text_content or ""):
                out.append(text)
        elif tag in SKIP_TAGS:
            continue
        elif len(tag) == 2 and tag[0] == "h" and tag[1] in "123456":
            if text := _inline(child):
                out.append(f"{'#' * int(tag[1])} {text}")
        elif tag == "pre":
            out.append("```\n" + (child.text(deep=True, strip=False) or "").strip("\n") + "\n```")
        elif tag == "li" and not child.css_first("ul, ol"):
            if text := _inline(child):
                out.append(f"- {text}")
        elif tag in LEAF_TAGS:
            if text := _inline(child):
                out.append(text)
        else:
            _blocks(child, out)


def to_markdown(html: "str | LexborNode") -> str:
    """Headings as `#` lines, `<pre>` as fenced code, list items as `- `, paragraphs apart by a blank line; navigation,
    headers, footers, scripts, forms and permalink anchors left out. Takes an HTML string (a page or a fragment) or a node."""
    root = LexborHTMLParser(html).body if isinstance(html, str) else html
    out: list[str] = []
    if root is not None:
        _blocks(root, out)
    return "\n\n".join(out).strip()
