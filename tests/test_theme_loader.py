"""Tests for the theme loader."""

from __future__ import annotations

import pytest

from md2pdf.themes.loader import load_theme, list_themes
from md2pdf.themes.schema import ThemeConfig


def test_list_themes_returns_all_builtins():
    themes = list_themes()
    assert "default" in themes
    assert "academic" in themes
    assert "minimal" in themes
    assert "corporate" in themes
    assert "dark" in themes
    assert "github" in themes


def test_load_default_theme():
    theme = load_theme("default")
    assert isinstance(theme, ThemeConfig)
    assert theme.name == "default"


def test_load_all_builtins():
    for name in list_themes():
        theme = load_theme(name)
        assert isinstance(theme, ThemeConfig)
        assert theme.name == name


def test_theme_has_emoji_fallback():
    for name in list_themes():
        theme = load_theme(name)
        assert len(theme.fonts.emoji_fallback) >= 2
        assert "Noto Color Emoji" in theme.fonts.emoji_fallback


def test_theme_colors_not_empty():
    theme = load_theme("dark")
    assert theme.colors.background != theme.colors.text
    assert theme.colors.primary


def test_unknown_theme_raises():
    with pytest.raises(FileNotFoundError, match="not found"):
        load_theme("does-not-exist")


def test_custom_theme_from_file(tmp_path):
    yaml_content = """
name: custom-test
colors:
  primary: "#ff0000"
  text: "#000000"
  background: "#ffffff"
  code_bg: "#f0f0f0"
  link: "#ff0000"
  border: "#cccccc"
  heading: "#000000"
  table_header_bg: "#eeeeee"
fonts:
  emoji_fallback:
    - "Noto Color Emoji"
    - "Apple Color Emoji"
    - "Segoe UI Emoji"
margins:
  top: 20
  right: 20
  bottom: 20
  left: 20
header:
  show: false
footer:
  show: true
"""
    custom = tmp_path / "custom-test.yaml"
    custom.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(custom))
    assert theme.name == "custom-test"
    assert theme.colors.primary == "#ff0000"
