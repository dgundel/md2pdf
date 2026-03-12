"""Shared Rich console and styled output helpers."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.theme import Theme

_theme = Theme(
    {
        "brand": "bold bright_white",
        "step": "cyan",
        "ok": "bold green",
        "warn": "yellow",
        "error": "bold red",
        "dim": "dim white",
        "path": "bright_cyan underline",
    }
)

console = Console(theme=_theme, highlight=False)

BRAND = "[brand]✦ md2pdf[/brand]"


def print_header(version: str = "1.0.0") -> None:
    """Print the branded header."""
    console.print()
    console.rule(f"[brand]✦ md2pdf  v{version}[/brand]", style="dim")
    console.print()


def print_step(label: str, detail: str = "") -> None:
    console.print(f"  [step]◆[/step] {label}" + (f"  [dim]{detail}[/dim]" if detail else ""))


def print_ok(message: str) -> None:
    console.print(f"  [ok]✓[/ok] {message}")


def print_warn(message: str) -> None:
    console.print(f"  [warn]⚠[/warn]  {message}")


def print_error(message: str) -> None:
    console.print(f"  [error]✗[/error]  {message}")


def format_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 / 1024:.1f} MB"
