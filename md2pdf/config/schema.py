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
    watermark: str | None = None
    syntax_theme: str = "github"
    extra_css: Path | None = None
    max_include_depth: int = 10

    @field_validator("source", "output", mode="before")
    @classmethod
    def to_path(cls, v: str | Path) -> Path:
        return Path(v)
