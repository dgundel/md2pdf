"""md2pdf batch — convert multiple markdown files."""

from __future__ import annotations

import glob
from pathlib import Path

from md2pdf.cli.commands.convert import run_convert
from md2pdf.utils.console import console, print_ok, print_error


def run_batch(pattern: str, output_dir: Path | None = None, merge: bool = False, **kwargs) -> None:
    """Convert all files matching glob pattern."""
    files = sorted(Path(f) for f in glob.glob(pattern, recursive=True) if f.endswith(".md"))

    if not files:
        print_error(f"Keine .md Dateien gefunden für: {pattern}")
        return

    console.print(f"\n  [cyan]◆[/cyan] Batch-Modus: [dim]{len(files)} Dateien[/dim]\n")

    success = 0
    fail = 0
    for md_file in files:
        out = None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            out = output_dir / md_file.with_suffix(".pdf").name

        ok, _ = run_convert(md_file, output=out, **kwargs)
        if ok:
            success += 1
        else:
            fail += 1

    console.print()
    print_ok(f"Batch abgeschlossen: {success} erfolgreich, {fail} Fehler")
