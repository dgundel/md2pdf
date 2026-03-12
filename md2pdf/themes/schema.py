"""Pydantic schema for theme configuration."""

from __future__ import annotations

from pydantic import BaseModel


class FontConfig(BaseModel):
    body: str = "Georgia, serif"
    heading: str = "Georgia, serif"
    mono: str = '"Cascadia Code", "JetBrains Mono", "Fira Code", monospace'
    emoji_fallback: list[str] = ["Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji"]
    base_size: str = "11pt"
    heading_scale: float = 1.25


class ColorConfig(BaseModel):
    primary: str = "#2563eb"
    text: str = "#1a1a1a"
    background: str = "#ffffff"
    code_bg: str = "#f4f4f4"
    link: str = "#2563eb"
    border: str = "#d1d5db"
    heading: str = "#111111"
    table_header_bg: str = "#f3f4f6"


class MarginConfig(BaseModel):
    top: int = 25
    right: int = 20
    bottom: int = 25
    left: int = 20


class HeaderFooterConfig(BaseModel):
    show: bool = False
    content: str = ""
    border: bool = True


class ThemeConfig(BaseModel):
    name: str
    colors: ColorConfig = ColorConfig()
    fonts: FontConfig = FontConfig()
    margins: MarginConfig = MarginConfig()
    header: HeaderFooterConfig = HeaderFooterConfig()
    footer: HeaderFooterConfig = HeaderFooterConfig(show=True)
