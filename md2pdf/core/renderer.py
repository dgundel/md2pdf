"""Renderer: assembles final HTML from all components."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from md2pdf.config.schema import JobConfig
from md2pdf.core.image_resolver import embed_images
from md2pdf.core.parser import parse_markdown, TocEntry
from md2pdf.core.title_page import build_title_page_html
from md2pdf.core.toc import build_toc_html
from md2pdf.core.toc_detect import mark_inline_toc
from md2pdf.themes.schema import ThemeConfig

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def _page_number_css_content(fmt: str) -> str:
    """Convert format string to CSS counter expression."""
    # e.g. "Seite {page} von {total}" → "Seite " counter(page) " von " counter(pages)
    result = fmt.replace("{page}", '" counter(page) "').replace("{total}", '" counter(pages) "')
    # Wrap the whole thing in quotes for CSS content
    return f'"{result}"'


def render_html(
    markdown_body: str,
    config: JobConfig,
    theme: ThemeConfig,
    toc_entries: list[TocEntry] | None = None,
) -> tuple[str, list[str]]:
    """Render the complete HTML document ready for WeasyPrint.

    Returns (html_string, warnings).
    """
    warnings: list[str] = []

    # 1. Parse markdown
    parse_result = parse_markdown(markdown_body)
    all_toc_entries = (toc_entries or []) + parse_result.toc_entries

    # 2. Embed images
    content_html, img_warnings = embed_images(parse_result.html, config.source.parent)
    warnings.extend(img_warnings)

    # 2b. Vorhandenes Inhaltsverzeichnis im Dokument erkennen und für Seitenzahlen markieren
    content_html, has_inline_toc = mark_inline_toc(content_html)

    # 3. Build optional blocks
    title_page_html = ""
    if config.title_page.enabled:
        title_page_html = build_title_page_html(config.title_page, config.source.parent)

    toc_html = ""
    if config.toc and all_toc_entries and not has_inline_toc:
        toc_html = build_toc_html(all_toc_entries, config.lang)

    # 4. Extra CSS
    extra_css = ""
    if config.extra_css and config.extra_css.exists():
        extra_css = config.extra_css.read_text(encoding="utf-8")

    # 5. Page number CSS content: "Seite " counter(page) " von " counter(pages)
    pn_fmt = config.page_numbers.format
    page_number_css = (
        pn_fmt
        .replace("{page}", '" counter(page) "')
        .replace("{total}", '" counter(pages) "')
    )

    # 6. Jinja2 render
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("base.html")

    html = template.render(
        lang=config.lang,
        theme=theme,
        page_size=config.page_size,
        page_numbers=config.page_numbers,
        page_number_text=page_number_css,
        watermark=config.watermark or "",
        title_page_html=title_page_html,
        toc_html=toc_html,
        content_html=content_html,
        extra_css=extra_css,
    )

    return html, warnings
