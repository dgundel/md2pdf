"""Load and validate themes from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from md2pdf.themes.schema import ThemeConfig, ColorConfig, FontConfig, MarginConfig, HeaderFooterConfig

BUILTIN_DIR = Path(__file__).parent / "builtin"


def list_themes() -> list[str]:
    """Return names of all available builtin themes."""
    return [f.stem for f in BUILTIN_DIR.glob("*.yaml")]


def load_theme(name_or_path: str) -> ThemeConfig:
    """Load a theme by name (builtin) or file path (custom).

    Raises FileNotFoundError if theme cannot be found.
    """
    path = Path(name_or_path)

    if path.exists() and path.suffix in (".yaml", ".yml"):
        return _load_from_file(path)

    builtin_path = BUILTIN_DIR / f"{name_or_path}.yaml"
    if builtin_path.exists():
        return _load_from_file(builtin_path)

    available = ", ".join(list_themes())
    raise FileNotFoundError(
        f"Theme '{name_or_path}' not found. Available themes: {available}"
    )


def _load_from_file(path: Path) -> ThemeConfig:
    """Parse a YAML theme file into a ThemeConfig."""
    with open(path, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    colors = ColorConfig(**data.get("colors", {}))
    fonts_data = data.get("fonts", {})
    fonts = FontConfig(**fonts_data)
    margins = MarginConfig(**data.get("margins", {}))

    header_data = data.get("header", {})
    footer_data = data.get("footer", {})
    header = HeaderFooterConfig(**header_data)
    footer = HeaderFooterConfig(**footer_data)

    return ThemeConfig(
        name=data.get("name", path.stem),
        colors=colors,
        fonts=fonts,
        margins=margins,
        header=header,
        footer=footer,
    )
