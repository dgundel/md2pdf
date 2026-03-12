"""Build title page HTML."""

from __future__ import annotations

import base64
from datetime import date
from pathlib import Path

from md2pdf.config.schema import TitlePageConfig


def build_title_page_html(cfg: TitlePageConfig, base_dir: Path) -> str:
    """Generate title page HTML block."""
    display_date = cfg.date
    if display_date == "auto" or not display_date:
        display_date = date.today().strftime("%d. %B %Y")

    logo_html = ""
    if cfg.logo:
        logo_path = (base_dir / cfg.logo).resolve()
        if logo_path.exists():
            data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
            ext = logo_path.suffix.lower().lstrip(".")
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "svg": "image/svg+xml"}.get(ext, "image/png")
            logo_html = f'<img class="title-logo" src="data:{mime};base64,{data}" alt="Logo">'

    version_html = ""
    if cfg.version:
        version_html = f'<p class="title-version">Version {cfg.version}</p>'

    subtitle_html = ""
    if cfg.subtitle:
        subtitle_html = f'<p class="title-subtitle">{cfg.subtitle}</p>'

    author_html = ""
    if cfg.author:
        author_html = f'<p class="title-author">{cfg.author}</p>'

    return f"""
<div class="title-page">
    {logo_html}
    <h1 class="title-main">{cfg.title}</h1>
    {subtitle_html}
    {version_html}
    <div class="title-meta">
        {author_html}
        <p class="title-date">{display_date}</p>
    </div>
</div>
<div class="page-break"></div>
"""
