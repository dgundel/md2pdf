"""Merge YAML frontmatter into JobConfig."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from md2pdf.config.schema import JobConfig, PageNumberConfig, TitlePageConfig
from md2pdf.config.env import get_env_config


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


def _get(overrides: dict, env: dict, fm: dict, key: str, default: Any = None) -> Any:
    """Priority: overrides > env > frontmatter > default."""
    if key in overrides:
        return overrides[key]
    if key in env and env[key] is not None:
        return env[key]
    return fm.get(key, default)


def frontmatter_to_jobconfig(
    source: Path,
    fm: dict[str, Any],
    overrides: dict[str, Any] | None = None,
) -> JobConfig:
    """Build a JobConfig from frontmatter + env + CLI overrides.

    Priority: overrides (CLI) > env (MD2PDF_*) > frontmatter > defaults
    """
    overrides = overrides or {}
    env = get_env_config()

    output = overrides.get("output") or fm.get("output") or source.with_suffix(".pdf")
    if isinstance(output, str):
        output = Path(output)

    title_page_data = fm.get("title_page", {})
    if isinstance(title_page_data, dict):
        title_page = TitlePageConfig(
            enabled=overrides.get("title_page_enabled", title_page_data.get("enabled", False)),
            title=_get(overrides, env, fm, "title") or title_page_data.get("title", ""),
            subtitle=_get(overrides, env, fm, "subtitle") or title_page_data.get("subtitle", ""),
            author=_get(overrides, env, fm, "author") or title_page_data.get("author", ""),
            date=overrides.get("date") or title_page_data.get("date") or fm.get("date", "auto"),
            logo=overrides.get("logo") or title_page_data.get("logo") or fm.get("logo"),
            version=_get(overrides, env, fm, "version") or title_page_data.get("version", ""),
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

    toc_default = fm.get("toc", False)
    if isinstance(env.get("toc"), bool):
        toc_default = env["toc"]
    toc = overrides.get("toc", toc_default)

    return JobConfig(
        source=source,
        output=Path(output),
        theme=_get(overrides, env, fm, "theme", "default"),
        custom_theme=overrides.get("custom_theme") or fm.get("custom_theme"),
        toc=toc,
        title_page=title_page,
        page_numbers=page_numbers,
        page_size=_get(overrides, env, fm, "page_size", "A4"),
        lang=_get(overrides, env, fm, "lang", "de"),
        watermark=_get(overrides, env, fm, "watermark") or fm.get("watermark"),
        syntax_theme=overrides.get("syntax_theme") or fm.get("syntax_theme", "github"),
        extra_css=overrides.get("extra_css") or fm.get("extra_css"),
    )
