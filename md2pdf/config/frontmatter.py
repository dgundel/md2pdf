"""Merge YAML frontmatter into JobConfig."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from md2pdf.config.schema import JobConfig, PageNumberConfig, TitlePageConfig


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown text.

    Returns a tuple of (frontmatter_dict, body_without_frontmatter).
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, text

    fm_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:])
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}

    return fm, body


def frontmatter_to_jobconfig(
    source: Path,
    fm: dict[str, Any],
    overrides: dict[str, Any] | None = None,
) -> JobConfig:
    """Build a JobConfig from frontmatter + CLI overrides.

    Priority: overrides > frontmatter > defaults
    """
    overrides = overrides or {}

    output = overrides.get("output") or fm.get("output") or source.with_suffix(".pdf")

    title_page_data = fm.get("title_page", {})
    if isinstance(title_page_data, dict):
        title_page = TitlePageConfig(
            enabled=overrides.get("title_page_enabled", title_page_data.get("enabled", False)),
            title=overrides.get("title") or title_page_data.get("title") or fm.get("title", ""),
            subtitle=overrides.get("subtitle") or title_page_data.get("subtitle") or fm.get("subtitle", ""),
            author=overrides.get("author") or title_page_data.get("author") or fm.get("author", ""),
            date=overrides.get("date") or title_page_data.get("date") or fm.get("date", "auto"),
            logo=overrides.get("logo") or title_page_data.get("logo") or fm.get("logo"),
            version=overrides.get("version") or title_page_data.get("version") or fm.get("version", ""),
        )
    else:
        title_page = TitlePageConfig()

    pn_data = fm.get("page_numbers", {})
    if isinstance(pn_data, dict):
        page_numbers = PageNumberConfig(
            enabled=overrides.get("page_numbers_enabled", pn_data.get("enabled", True)),
            position=overrides.get("page_number_position") or pn_data.get("position", "bottom-center"),
            format=overrides.get("page_number_format") or pn_data.get("format", "Seite {page} von {total}"),
        )
    else:
        page_numbers = PageNumberConfig()

    return JobConfig(
        source=source,
        output=Path(output),
        theme=overrides.get("theme") or fm.get("theme", "default"),
        custom_theme=overrides.get("custom_theme") or fm.get("custom_theme"),
        toc=overrides.get("toc", fm.get("toc", False)),
        title_page=title_page,
        page_numbers=page_numbers,
        page_size=overrides.get("page_size") or fm.get("page_size", "A4"),
        lang=overrides.get("lang") or fm.get("lang", "de"),
        watermark=overrides.get("watermark") or fm.get("watermark"),
        syntax_theme=overrides.get("syntax_theme") or fm.get("syntax_theme", "github"),
        extra_css=overrides.get("extra_css") or fm.get("extra_css"),
    )
