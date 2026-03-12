"""Tests for the markdown parser."""

from __future__ import annotations

from md2pdf.core.parser import parse_markdown
from md2pdf.config.frontmatter import extract_frontmatter


def test_heading_extraction():
    md = "# Title\n## Section\n### Sub"
    result = parse_markdown(md)
    assert len(result.toc_entries) == 3
    assert result.toc_entries[0].level == 1
    assert result.toc_entries[0].title == "Title"
    assert result.toc_entries[1].level == 2
    assert result.toc_entries[2].level == 3


def test_anchor_slugification():
    md = "# Hello World!\n## Über uns"
    result = parse_markdown(md)
    assert result.toc_entries[0].anchor == "hello-world"
    assert "ber" in result.toc_entries[1].anchor  # ü stripped


def test_duplicate_anchors():
    md = "# Test\n# Test\n# Test"
    result = parse_markdown(md)
    anchors = [e.anchor for e in result.toc_entries]
    assert len(set(anchors)) == 3  # all unique


def test_table_rendered():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    result = parse_markdown(md)
    assert "<table" in result.html
    assert "<th" in result.html
    assert "<td" in result.html


def test_code_block_rendered():
    md = "```python\nprint('hi')\n```"
    result = parse_markdown(md)
    assert "<pre>" in result.html or "<code" in result.html


def test_frontmatter_extraction():
    text = "---\ntitle: Test\nauthor: Me\n---\n# Body"
    fm, body = extract_frontmatter(text)
    assert fm["title"] == "Test"
    assert fm["author"] == "Me"
    assert body.strip() == "# Body"


def test_frontmatter_missing():
    text = "# No frontmatter"
    fm, body = extract_frontmatter(text)
    assert fm == {}
    assert body == text


def test_no_headings():
    md = "Just a paragraph.\n\nAnother one."
    result = parse_markdown(md)
    assert result.toc_entries == []
    assert "<p>" in result.html
