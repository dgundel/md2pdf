"""Load/save config from YAML files (e.g. from wizard or -c/--config)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def wizard_data_to_config_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Convert wizard_data to a YAML-serializable config dict (no source)."""
    return {
        "theme": data.get("theme", "default"),
        "toc": data.get("toc", False),
        "title_page": data.get("title_page", False),
        "page_numbers": data.get("page_numbers", True),
        "lang": data.get("lang", "de"),
        "page_size": data.get("page_size", "A4"),
        "title": data.get("doc_title", ""),
        "author": data.get("author", ""),
    }


def save_config_from_wizard(data: dict[str, Any], path: Path) -> None:
    """Write wizard_data as YAML config file (without source)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cfg = wizard_data_to_config_dict(data)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)


def load_config_file(path: Path) -> dict[str, Any]:
    """Load config from YAML file and return overrides for frontmatter_to_jobconfig.

    Keys are normalized to match override names: theme, toc, title_page_enabled,
    page_numbers_enabled, lang, page_size, title, author.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config-Datei nicht gefunden: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    overrides: dict[str, Any] = {}
    if "theme" in data:
        overrides["theme"] = data["theme"]
    if "toc" in data:
        overrides["toc"] = data["toc"]
    if "title_page" in data:
        overrides["title_page_enabled"] = data["title_page"]
    if "page_numbers" in data:
        overrides["page_numbers_enabled"] = data["page_numbers"]
    if "lang" in data:
        overrides["lang"] = data["lang"]
    if "page_size" in data:
        overrides["page_size"] = data["page_size"]
    if "title" in data:
        overrides["title"] = data["title"]
    if "author" in data:
        overrides["author"] = data["author"]
    return overrides
