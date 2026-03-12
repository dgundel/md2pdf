"""Read MD2PDF_* environment variables for CI/CD-friendly config."""

from __future__ import annotations

import os


# Keys we accept; value is the env var name (without MD2PDF_ prefix)
ENV_KEYS = {
    "theme": "THEME",
    "toc": "TOC",
    "title": "TITLE",
    "author": "AUTHOR",
    "lang": "LANG",
    "page_size": "PAGE_SIZE",
    "watermark": "WATERMARK",
    "config": "CONFIG",
}


def _parse_toc(value: str) -> bool:
    if not value:
        return False
    return value.strip().lower() in ("1", "true", "yes", "on")


def get_env_config() -> dict[str, str | bool | None]:
    """Read MD2PDF_* env vars and return a config dict.

    Unknown MD2PDF_* vars are ignored (no warning for now).
    Priority when merging: CLI overrides > env > frontmatter > defaults.
    """
    result: dict[str, str | bool | None] = {}
    prefix = "MD2PDF_"
    for key, suffix in ENV_KEYS.items():
        var = prefix + suffix
        value = os.environ.get(var)
        if value is None:
            continue
        if key == "toc":
            result[key] = _parse_toc(value)
        else:
            result[key] = value.strip()
    return result
