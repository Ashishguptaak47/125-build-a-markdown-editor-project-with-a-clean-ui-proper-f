import os
import tempfile
import pytest
from markdown_editor.core.parser import MarkdownEngine, MarkdownToken
from markdown_editor.core.stats import DocumentMetrics
from main import run_cli_export


@pytest.fixture
def engine():
    return MarkdownEngine()


def test_tokenization_headings(engine):
    md = "# Title 1\n## Title 2\n### Title 3"
    tokens = engine.tokenize(md)
    assert len(tokens) == 3
    assert tokens[0].type == "heading" and tokens[0].level == 1 and tokens[0].content == "Title 1"
    assert tokens[1].type == "heading" and tokens[1].level == 2 and tokens[1].content == "Title 2"
    assert tokens[2].type == "heading" and tokens[2].level == 3 and tokens[2].content == "Title 3"


def test_tokenization_lists(engine):
    md = "- Item 1\n* Item 2\n1. First\n- [x] Done\n- [ ] Pending"
    tokens = engine.tokenize(md)
    assert tokens[0].type == "list_item" and tokens[0].content == "Item 1"
    assert tokens[1].type == "list_item" and tokens[1].content == "Item 2"
    assert tokens[2].type == "ordered_item" and tokens[2].meta["num"] == "1"
    assert tokens[3].type == "task_item" and tokens[3].meta["checked"] is True
    assert tokens[4].type == "task_item" and tokens[4].meta["checked"] is False


def test_tokenization_code_block(engine):
    md = "```python\nprint('hello world')\n```"
    tokens = engine.tokenize(md)
    assert len(tokens) == 1
    assert tokens[0].type == "code_block"
    assert tokens[0].content == "print('hello world')"
    assert tokens[0].meta["lang"] == "python"


def test_inline_parser(engine):
    line = "Here is **bold** and *italic* and `code` and [Docs](https://example.com)"
    inlines = engine.parse_inline_elements(line)
    types = [item["type"] for item in inlines]
    assert "bold" in types
    assert "italic" in types
    assert "code" in types
    assert "link" in types


def test_to_html_export(engine):
    md = "# Hello\nThis is a **test**.\n\n> Quote here\n---"
    html = engine.to_html(md, title="Test Document")
    assert "<title>Test Document</title>" in html
    assert "<h1>Hello</h1>" in html
    assert "<strong>test</strong>" in html
    assert "<blockquote>" in html
    assert "<hr/>" in html


def test_document_metrics():
    text = "# Header One\n\nThis is a sample document with several words."
    stats = DocumentMetrics.compute_stats(text)
    assert stats["words"] > 5
    assert stats["lines"] >= 3
    assert stats["reading_time_mins"] >= 1

    outline = DocumentMetrics.extract_outline("# First\nContent\n## Sub\nMore\n### Deep")
    assert len(outline) == 3
    assert outline[0]["title"] == "First" and outline[0]["level"] == 1
    assert outline[1]["title"] == "Sub" and outline[1]["level"] == 2
    assert outline[2]["title"] == "Deep" and outline[2]["level"] == 3


def test_cli_export():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f_in:
        f_in.write("# CLI Test\nSample output content.")
        in_path = f_in.name

    out_path = in_path.replace(".md", ".html")
    try:
        res = run_cli_export(in_path, out_path)
        assert res == 0
        assert os.path.exists(out_path)
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "CLI Test" in content
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)
        if os.path.exists(out_path):
            os.remove(out_path)
