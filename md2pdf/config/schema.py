"""Pydantic config models for md2pdf jobs."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator


class PageNumberConfig(BaseModel):
    enabled: bool = True
    position: Literal["bottom-center", "bottom-right", "bottom-left"] = "bottom-center"
    format: str = "Seite {page} von {total}"


class TitlePageConfig(BaseModel):
    enabled: bool = False
    title: str = ""
    subtitle: str = ""
    author: str = ""
    date: str = "auto"
    logo: Path | None = None
    version: str = ""


class WatermarkConfig(BaseModel):
    """Watermark text and optional style. Empty text = no watermark."""
    text: str = ""
    color: str = "#b4b4b4"
    opacity: float = 0.18
    angle: float = -35


class JobConfig(BaseModel):
    source: Path
    output: Path
    theme: str = "default"
    custom_theme: Path | None = None
    toc: bool = False
    title_page: TitlePageConfig = TitlePageConfig()
    page_numbers: PageNumberConfig = PageNumberConfig()
    page_size: Literal["A4", "A5", "Letter"] = "A4"
    lang: str = "de"
    watermark: WatermarkConfig | None = None
    syntax_theme: str = "github"
    extra_css: Path | None = None
    max_include_depth: int = 10

    @field_validator("source", "output", mode="before")
    @classmethod
    def to_path(cls, v: str | Path) -> Path:
        return Path(v)

    @field_validator("watermark", mode="before")
    @classmethod
    def watermark_from_str_or_dict(cls, v: str | dict | WatermarkConfig | None) -> WatermarkConfig | None:
        if v is None:
            return None
        if isinstance(v, WatermarkConfig):
            return v
        if isinstance(v, str):
            return WatermarkConfig(text=v) if v.strip() else None
        if isinstance(v, dict):
            return WatermarkConfig(**{k: v[k] for k in ("text", "color", "opacity", "angle") if k in v})
        return None
