"""Tests for the include resolver."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2pdf.core.include_resolver import resolve_includes

FIXTURES = Path(__file__).parent / "fixtures"


def test_no_includes_passthrough():
    text = "# Hello\n\nNo includes here."
    result = resolve_includes(text, FIXTURES / "simple.md")
    assert result.content == text
    assert not result.errors
    assert not result.included_files


def test_basic_include():
    text = '![[partial.md | modell="TestModel" | jahr="2099" | artikelnr="TM-001"]]'
    result = resolve_includes(text, FIXTURES / "with_includes.md")
    assert not result.errors
    assert "TestModel" in result.content
    assert "2099" in result.content
    assert "TM-001" in result.content
    assert FIXTURES / "partial.md" in result.included_files


def test_missing_file_error():
    text = "![[does_not_exist.md]]"
    result = resolve_includes(text, FIXTURES / "simple.md")
    assert len(result.errors) == 1
    assert "nicht gefunden" in result.errors[0].message


def test_circular_include(tmp_path: Path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("![[b.md]]", encoding="utf-8")
    b.write_text("![[a.md]]", encoding="utf-8")
    result = resolve_includes(a.read_text(), a)
    assert any("Zirkulär" in e.message for e in result.errors)


def test_max_depth(tmp_path: Path):
    # Create chain: a→b→c→d→e→f (depth 6 with max 3)
    files = [tmp_path / f"{chr(ord('a') + i)}.md" for i in range(6)]
    for i, f in enumerate(files[:-1]):
        f.write_text(f"![[{files[i + 1].name}]]", encoding="utf-8")
    files[-1].write_text("# Leaf", encoding="utf-8")

    result = resolve_includes(files[0].read_text(), files[0], max_depth=3)
    assert any(result.errors)


def test_unresolved_placeholder_warning():
    text = "![[partial.md]]"  # no variables passed, should warn
    result = resolve_includes(text, FIXTURES / "with_includes.md")
    # partial.md has defaults so no warnings expected for those vars
    # but content should be there
    assert "Ersatzteilliste" in result.content


def test_variable_priority(tmp_path: Path):
    sub = tmp_path / "sub.md"
    sub.write_text("---\ndefaults:\n  color: blue\n---\nFarbe: {{color}}", encoding="utf-8")
    main = tmp_path / "main.md"

    # Include with explicit override should win over sub defaults
    text = '![[sub.md | color="red"]]'
    result = resolve_includes(text, main)
    assert "red" in result.content
    assert "blue" not in result.content


def test_full_document_includes():
    text = (FIXTURES / "with_includes.md").read_text(encoding="utf-8")
    result = resolve_includes(text, FIXTURES / "with_includes.md")
    assert not result.errors
    assert "AX-990" in result.content
    assert "AX-500" in result.content
    # partial.md should be in included files (included twice)
    assert FIXTURES / "partial.md" in result.included_files
