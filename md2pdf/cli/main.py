"""md2pdf CLI — main entrypoint via Typer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from md2pdf import __version__
from md2pdf.themes.loader import list_themes
from md2pdf.utils.console import console, print_header, BRAND

app = typer.Typer(
    name="md2pdf",
    help="Convert Markdown to beautiful PDFs.",
    add_completion=False,
    rich_markup_mode="rich",
)


# ── convert ───────────────────────────────────────────────────────────────────

@app.command("convert")
def cmd_convert(
    source: Path = typer.Argument(..., help="Quelldatei (.md)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Ausgabe-PDF (default: <input>.pdf)"),
    theme: str = typer.Option("default", "--theme", "-t", help="Theme-Name oder Pfad zu .yaml"),
    toc: bool = typer.Option(False, "--toc", help="Inhaltsverzeichnis generieren"),
    title_page: bool = typer.Option(False, "--title-page", help="Titelseite aktivieren"),
    author: str = typer.Option("", "--author", help="Autor"),
    title: str = typer.Option("", "--title", help="Dokumenttitel"),
    lang: str = typer.Option("de", "--lang", help="Sprache (de/en/fr/...)"),
    page_size: str = typer.Option("A4", "--page-size", help="A4 | A5 | Letter"),
    watermark: Optional[str] = typer.Option(None, "--watermark", help="Wasserzeichen-Text"),
    no_page_numbers: bool = typer.Option(False, "--no-page-numbers", help="Seitenzahlen deaktivieren"),
    page_number_format: str = typer.Option("", "--page-number-format", help='Format z.B. "{page}/{total}"'),
    extra_css: Optional[Path] = typer.Option(None, "--extra-css", help="Zusätzliche CSS-Datei"),
    open_after: bool = typer.Option(False, "--open", help="PDF nach Erstellung öffnen"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Ausführliche Ausgabe"),
) -> None:
    """Convert a Markdown file to PDF."""
    from md2pdf.cli.commands.convert import run_convert
    success = run_convert(
        source=source,
        output=output,
        theme=theme,
        toc=toc,
        title_page=title_page,
        author=author,
        title=title,
        lang=lang,
        page_size=page_size,
        watermark=watermark,
        no_page_numbers=no_page_numbers,
        page_number_format=page_number_format,
        extra_css=extra_css,
        open_after=open_after,
        verbose=verbose,
    )
    raise typer.Exit(0 if success else 1)


# ── watch ─────────────────────────────────────────────────────────────────────

@app.command("watch")
def cmd_watch(
    source: Path = typer.Argument(..., help="Quelldatei (.md)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    theme: str = typer.Option("default", "--theme", "-t"),
    toc: bool = typer.Option(False, "--toc"),
    title_page: bool = typer.Option(False, "--title-page"),
    lang: str = typer.Option("de", "--lang"),
    page_size: str = typer.Option("A4", "--page-size"),
) -> None:
    """Watch a Markdown file and re-render on changes."""
    from md2pdf.cli.commands.watch import run_watch
    run_watch(
        source=source,
        output=output,
        theme=theme,
        toc=toc,
        title_page=title_page,
        lang=lang,
        page_size=page_size,
    )


# ── batch ─────────────────────────────────────────────────────────────────────

@app.command("batch")
def cmd_batch(
    pattern: str = typer.Argument(..., help='Glob-Muster, z.B. "docs/*.md"'),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Ausgabeverzeichnis"),
    theme: str = typer.Option("default", "--theme", "-t"),
    toc: bool = typer.Option(False, "--toc"),
    lang: str = typer.Option("de", "--lang"),
) -> None:
    """Convert multiple Markdown files matching a glob pattern."""
    from md2pdf.cli.commands.batch import run_batch
    run_batch(pattern=pattern, output_dir=output_dir, theme=theme, toc=toc, lang=lang)


# ── themes ────────────────────────────────────────────────────────────────────

@app.command("themes")
def cmd_themes() -> None:
    """List all available themes with colour preview."""
    from md2pdf.cli.interactive import THEME_COLORS
    print_header(__version__)
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Theme", style="bold")
    table.add_column("Primär")
    table.add_column("Text")
    table.add_column("Hintergrund")

    for name in list_themes():
        colors = THEME_COLORS.get(name, ("—", "—", "—"))
        primary, text, bg = colors
        swatch = f"[on {primary}]   [/on {primary}]"
        table.add_row(name, f"{swatch} {primary}", text, bg)

    console.print(table)
    console.print()


# ── interactive ───────────────────────────────────────────────────────────────

@app.command("interactive")
def cmd_interactive() -> None:
    """Launch the interactive TUI wizard."""
    from md2pdf.cli.interactive import run_interactive
    from md2pdf.cli.commands.convert import run_convert

    data = run_interactive()
    if not data:
        raise typer.Exit(0)

    run_convert(
        source=Path(data["source"]),
        theme=data.get("theme", "default"),
        toc=data.get("toc", False),
        title_page=data.get("title_page", False),
        author=data.get("author", ""),
        title=data.get("doc_title", ""),
        lang=data.get("lang", "de"),
        page_size=data.get("page_size", "A4"),
        no_page_numbers=not data.get("page_numbers", True),
    )


# ── default: no args → interactive ────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Version anzeigen"),
) -> None:
    """✦ md2pdf — Convert Markdown to beautiful PDFs."""
    if version:
        console.print(f"{BRAND}  [dim]v{__version__}[/dim]")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        cmd_interactive()
