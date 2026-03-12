"""md2pdf watch — re-render on file changes."""

from __future__ import annotations

import time
from pathlib import Path

from md2pdf.cli.commands.convert import run_convert
from md2pdf.utils.console import console, print_step, print_warn


def run_watch(source: Path, **kwargs) -> None:
    """Watch source file (and its includes) for changes and re-render."""
    try:
        from watchdog.observers import Observer  # type: ignore
        from watchdog.events import FileSystemEventHandler, FileModifiedEvent  # type: ignore
    except ImportError:
        console.print("[error]✗[/error]  watchdog nicht installiert.\n  → pip install watchdog")
        return

    console.print(f"\n  [cyan]◆[/cyan] Beobachte [bright_cyan]{source}[/bright_cyan] — [dim]Ctrl+C zum Beenden[/dim]\n")

    last_run: dict[str, float] = {"t": 0.0}
    DEBOUNCE = 0.5  # seconds

    class Handler(FileSystemEventHandler):
        def on_modified(self, event: FileModifiedEvent) -> None:
            if event.is_directory:
                return
            now = time.monotonic()
            if now - last_run["t"] < DEBOUNCE:
                return
            last_run["t"] = now
            p = Path(event.src_path)
            if p.suffix in (".md", ".yaml", ".yml", ".css", ".png", ".jpg", ".jpeg", ".svg"):
                console.rule("[dim]Änderung erkannt[/dim]", style="dim")
                run_convert(source, **kwargs)

    observer = Observer()
    observer.schedule(Handler(), str(source.parent), recursive=True)
    observer.start()

    # Initial render
    run_convert(source, **kwargs)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n  [dim]Watch-Modus beendet.[/dim]\n")
    observer.join()
