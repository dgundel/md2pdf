"""Filesystem utilities."""
from __future__ import annotations
from pathlib import Path


def find_user_config() -> Path | None:
    """Find user-level config at ~/.config/md2pdf/config.yaml."""
    cfg = Path.home() / ".config" / "md2pdf" / "config.yaml"
    return cfg if cfg.exists() else None


def find_user_themes_dir() -> Path:
    """Return user themes directory, creating it if needed."""
    d = Path.home() / ".config" / "md2pdf" / "themes"
    d.mkdir(parents=True, exist_ok=True)
    return d
