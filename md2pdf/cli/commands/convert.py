"""md2pdf convert — single file conversion command."""

from __future__ import annotations

import time
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from md2pdf.config.frontmatter import extract_frontmatter, frontmatter_to_jobconfig
from md2pdf.core.include_resolver import resolve_includes
from md2pdf.core.renderer import render_html
from md2pdf.core.pdf_engine import render_pdf
from md2pdf.themes.loader import load_theme
from md2pdf.utils.console import (
    console, print_header, print_step, print_ok, print_warn, print_error, format_size
)


def run_convert(
    source: Path,
    output: Path | None = None,
    theme: str = "default",
    toc: bool = False,
    title_page: bool = False,
    author: str = "",
    title: str = "",
    lang: str = "de",
    page_size: str = "A4",
    watermark: str | None = None,
    no_page_numbers: bool = False,
    page_number_format: str = "",
    extra_css: Path | None = None,
    open_after: bool = False,
    verbose: bool = False,
) -> bool:
    """Execute a single Markdown → PDF conversion.

    Returns True on success, False on failure.
    """
    start = time.monotonic()
    print_header()

    if not source.exists():
        print_error(f"Datei nicht gefunden: {source}")
        return False

    # 1. Read source + extract frontmatter
    print_step("Lese", source.name)
    raw_text = source.read_text(encoding="utf-8")
    fm, body = extract_frontmatter(raw_text)

    overrides: dict = {}
    if title:
        overrides["title"] = title
    if author:
        overrides["author"] = author
    if toc:
        overrides["toc"] = True
    if title_page:
        overrides["title_page_enabled"] = True
    if lang:
        overrides["lang"] = lang
    if page_size:
        overrides["page_size"] = page_size
    if watermark:
        overrides["watermark"] = watermark
    if no_page_numbers:
        overrides["page_numbers_enabled"] = False
    if page_number_format:
        overrides["page_number_format"] = page_number_format
    if extra_css:
        overrides["extra_css"] = extra_css
    if output:
        overrides["output"] = output
    if theme != "default":
        overrides["theme"] = theme

    config = frontmatter_to_jobconfig(source, fm, overrides)

    # 2. Resolve includes
    include_result = resolve_includes(body, source, max_depth=config.max_include_depth)
    n_includes = len(include_result.included_files)
    if n_includes:
        print_step("Löse Includes auf", f"({n_includes} {'Datei' if n_includes == 1 else 'Dateien'})")
    for err in include_result.errors:
        print_error(str(err))
    for w in include_result.warnings:
        print_warn(w)
    if include_result.errors:
        return False

    # 3. Load theme
    try:
        theme_cfg = load_theme(config.theme)
        print_step("Lade Theme", config.theme)
    except FileNotFoundError as e:
        print_error(str(e))
        return False

    # 4. Render HTML
    print_step("Rendere HTML")
    html, render_warnings = render_html(include_result.content, config, theme_cfg)
    for w in render_warnings:
        print_warn(w)

    img_count = html.count("data:image/")
    if img_count:
        print_step("Bilder eingebettet", f"({img_count})")

    if config.toc:
        print_step("Generiere TOC")

    # 5. Render PDF with progress bar
    print_step("Erstelle PDF")
    with Progress(
        SpinnerColumn(),
        TextColumn("  [cyan]{task.description}[/cyan]"),
        BarColumn(bar_width=30),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Rendering…", total=None)
        pdf_result = render_pdf(html, config.output)
        progress.update(task, completed=True)

    elapsed = time.monotonic() - start

    if not pdf_result.success:
        print_error(f"PDF-Erstellung fehlgeschlagen:\n  {pdf_result.error}")
        return False

    # 6. Success summary
    console.print()
    print_ok(
        f"PDF erstellt: [path]{config.output}[/path]\n"
        f"    [dim]Seiten: {pdf_result.page_count}  •  "
        f"Größe: {format_size(pdf_result.file_size_bytes)}  •  "
        f"Zeit: {elapsed:.1f}s[/dim]"
    )
    console.print()

    if open_after:
        import subprocess, sys
        cmd = {"darwin": "open", "win32": "start", "linux": "xdg-open"}.get(sys.platform, "xdg-open")
        subprocess.Popen([cmd, str(config.output)])

    return True
