"""Interactive TUI Wizard — Textual-based, Claude CLI inspired."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    Switch,
)

from md2pdf.config.file_config import save_config_from_wizard


THEME_COLORS: dict[str, tuple[str, str, str]] = {
    "default":   ("#2563eb", "#1a1a1a", "#ffffff"),
    "academic":  ("#1a237e", "#212121", "#ffffff"),
    "minimal":   ("#000000", "#333333", "#ffffff"),
    "corporate": ("#003366", "#1a1a2e", "#ffffff"),
    "dark":      ("#60a5fa", "#e2e8f0", "#0f172a"),
    "github":    ("#0969da", "#1f2328", "#ffffff"),
    "liberation": ("#2563eb", "#1a1a1a", "#ffffff"),
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _start_cwd() -> Path:
    """Verzeichnis, in dem der Nutzer md2pdf aufgerufen hat (nicht Projektroot)."""
    start_cwd = os.environ.get("MD2PDF_START_CWD")
    if start_cwd:
        p = Path(start_cwd)
        return p if p.is_dir() else Path.cwd()
    return Path.cwd()


def _resolve_path(user_input: str) -> Path:
    """Eingegebenen Pfad auflösen; relative Pfade gelten relativ zum Start-CWD."""
    p = Path(user_input.strip())
    if not p.is_absolute():
        p = (_start_cwd() / p).resolve()
    return p


def _find_md_files(max_entries: int = 30) -> list[tuple[str, str]]:
    """Find .md files in start directory (where user ran md2pdf) and subdirs; return [(label, path), ...] for Select."""
    cwd = _start_cwd()
    seen: set[Path] = set()
    options: list[tuple[str, str]] = []
    try:
        for p in sorted(cwd.rglob("*.md")):
            if len(options) >= max_entries:
                break
            try:
                if not p.is_file() or p in seen:
                    continue
                rel = p.relative_to(cwd)
                seen.add(p)
                label = str(rel) if len(str(rel)) <= 50 else f"...{str(rel)[-47:]}"
                options.append((label, str(p)))
            except (OSError, ValueError):
                continue
    except OSError:
        pass
    return options


# ── Screens ────────────────────────────────────────────────────────────────────

class FileSelectScreen(Screen):
    """Screen 1: pick the source .md file."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        md_options = _find_md_files()
        select_options: list[tuple[str, str]] = [("— Datei wählen oder unten eingeben —", "")]
        select_options.extend(md_options)

        yield Header(show_clock=False)
        yield Container(
            Static("✦ md2pdf", classes="brand"),
            Static("Schritt 1 von 4 — Quelldatei", classes="step-label"),
            Label("Vorschläge (Dropdown):"),
            Select(select_options, value="", prompt="Markdown-Datei auswählen…", id="file-select"),
            Label("Markdown-Datei (.md):"),
            Input(placeholder="z.B. ./readme.md oder docs/handbuch.md", id="file-input"),
            Static("", id="file-preview", classes="preview"),
            Horizontal(
                Button("Weiter →", variant="primary", id="next"),
                Button("Beenden", variant="error", id="quit"),
                classes="btn-row",
            ),
            classes="wizard-box",
        )
        yield Footer()

    @on(Select.Changed, "#file-select")
    def on_file_select(self, event: Select.Changed) -> None:
        if event.value and event.value != "":
            self.query_one("#file-input", Input).value = str(event.value)
            self.query_one("#file-input", Input).focus()
            self._update_preview_from_path(Path(event.value))

    def _update_preview_from_path(self, p: Path) -> None:
        preview = self.query_one("#file-preview", Static)
        if p.exists() and p.suffix == ".md":
            lines = p.read_text(encoding="utf-8").splitlines()[:6]
            snippet = "\n".join(lines)
            preview.update(f"[dim]Vorschau:[/dim]\n[dim]{snippet}[/dim]")
        elif p != Path("."):
            preview.update("[red]Datei nicht gefunden[/red]")
        else:
            preview.update("")

    @on(Input.Changed, "#file-input")
    def update_preview(self, event: Input.Changed) -> None:
        if not event.value:
            self.query_one("#file-preview", Static).update("")
        else:
            self._update_preview_from_path(_resolve_path(event.value))

    @on(Button.Pressed, "#next")
    def go_next(self) -> None:
        val = self.query_one("#file-input", Input).value.strip()
        if not val:
            self.query_one("#file-preview", Static).update("[red]Bitte eine Datei angeben[/red]")
            return
        p = _resolve_path(val)
        if not p.exists():
            self.query_one("#file-preview", Static).update("[red]Datei nicht gefunden[/red]")
            return
        self.app.wizard_data["source"] = str(p)
        self.app.push_screen(ThemeSelectScreen())

    @on(Button.Pressed, "#quit")
    def quit_app(self) -> None:
        self.app.exit()


class ThemeSelectScreen(Screen):
    """Screen 2: choose a theme with colour swatches."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        items = []
        for name, (primary, text, bg) in THEME_COLORS.items():
            swatch = f"[bold on {primary}]   [/bold on {primary}]"
            label = f" {swatch} [bold]{name}[/bold]"
            items.append(ListItem(Label(label), id=f"theme-{name}"))

        yield Container(
            Static("✦ md2pdf", classes="brand"),
            Static("Schritt 2 von 4 — Theme auswählen", classes="step-label"),
            ListView(*items, id="theme-list"),
            Static("", id="theme-desc", classes="preview"),
            Horizontal(
                Button("← Zurück", id="back"),
                Button("Weiter →", variant="primary", id="next"),
                classes="btn-row",
            ),
            classes="wizard-box",
        )
        yield Footer()

    @on(ListView.Highlighted)
    def on_highlight(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            name = event.item.id.removeprefix("theme-")
            self.app.wizard_data["theme"] = name
            primary, text, bg = THEME_COLORS.get(name, ("#000", "#000", "#fff"))
            desc = self.query_one("#theme-desc", Static)
            desc.update(f"[dim]Primärfarbe:[/dim] [bold {primary}]{primary}[/bold {primary}]  "
                        f"[dim]Text:[/dim] {text}  [dim]Hintergrund:[/dim] {bg}")

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#next")
    def go_next(self) -> None:
        if "theme" not in self.app.wizard_data:
            self.app.wizard_data["theme"] = "default"
        self.app.push_screen(OptionsScreen())


class OptionsScreen(Screen):
    """Screen 3: TOC, title page, page numbers, language."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(
            Static("✦ md2pdf", classes="brand"),
            Static("Schritt 3 von 4 — Optionen", classes="step-label"),

            Horizontal(Label("Inhaltsverzeichnis (TOC)"), Switch(id="sw-toc"), classes="option-row"),
            Horizontal(Label("Titelseite erstellen"),     Switch(id="sw-title"), classes="option-row"),
            Horizontal(Label("Seitenzahlen"),             Switch(value=True, id="sw-pn"), classes="option-row"),

            Label("Titel (optional):"),
            Input(placeholder="Dokumenttitel", id="inp-title"),
            Label("Autor (optional):"),
            Input(placeholder="Autor / Organisation", id="inp-author"),

            Label("Sprache:"),
            Select(
                [("Deutsch (de)", "de"), ("English (en)", "en"), ("Français (fr)", "fr")],
                value="de",
                id="sel-lang",
            ),

            Label("Seitengröße:"),
            Select(
                [("A4", "A4"), ("A5", "A5"), ("Letter", "Letter")],
                value="A4",
                id="sel-pagesize",
            ),

            Horizontal(
                Button("← Zurück", id="back"),
                Button("Weiter →", variant="primary", id="next"),
                classes="btn-row",
            ),
            classes="wizard-box",
        )
        yield Footer()

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#next")
    def go_next(self) -> None:
        d = self.app.wizard_data
        d["toc"] = self.query_one("#sw-toc", Switch).value
        d["title_page"] = self.query_one("#sw-title", Switch).value
        d["page_numbers"] = self.query_one("#sw-pn", Switch).value
        d["doc_title"] = self.query_one("#inp-title", Input).value.strip()
        d["author"] = self.query_one("#inp-author", Input).value.strip()
        d["lang"] = self.query_one("#sel-lang", Select).value
        d["page_size"] = self.query_one("#sel-pagesize", Select).value
        self.app.push_screen(SummaryScreen())


class SummaryScreen(Screen):
    """Screen 4: summary + confirm."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        d = self.app.wizard_data
        rows = [
            ("Quelldatei",       d.get("source", "—")),
            ("Theme",            d.get("theme", "default")),
            ("TOC",              "✓" if d.get("toc") else "—"),
            ("Titelseite",       "✓" if d.get("title_page") else "—"),
            ("Seitenzahlen",     "✓" if d.get("page_numbers", True) else "—"),
            ("Titel",            d.get("doc_title") or "—"),
            ("Autor",            d.get("author") or "—"),
            ("Sprache",          d.get("lang", "de")),
            ("Seitengröße",      d.get("page_size", "A4")),
        ]
        table_text = "\n".join(f"  [dim]{k}:[/dim]  {v}" for k, v in rows)

        yield Header(show_clock=False)
        yield Container(
            Static("✦ md2pdf", classes="brand"),
            Static("Schritt 4 von 4 — Zusammenfassung", classes="step-label"),
            Static(table_text, classes="summary-table"),
            Horizontal(
                Button("← Zurück", id="back"),
                Button("💾 Config speichern", id="save-config"),
                Button("🚀 Rendern", variant="success", id="render"),
                Button("Beenden", variant="error", id="quit"),
                classes="btn-row",
            ),
            classes="wizard-box",
        )
        yield Footer()

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#save-config")
    def save_config(self) -> None:
        default_path = _start_cwd() / "md2pdf.yaml"
        self.app.push_screen(SaveConfigScreen(str(default_path)))

    @on(Button.Pressed, "#render")
    def do_render(self) -> None:
        self.app.exit(result=self.app.wizard_data)

    @on(Button.Pressed, "#quit")
    def quit_app(self) -> None:
        self.app.exit()


class SaveConfigScreen(Screen):
    """Small screen: enter path and save config YAML."""

    BINDINGS = [Binding("escape", "app.pop_screen", "Abbrechen")]

    def __init__(self, default_path: str = "./md2pdf.yaml") -> None:
        super().__init__()
        self._default_path = default_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(
            Static("✦ Config speichern", classes="brand"),
            Label("Pfad zur YAML-Config-Datei:"),
            Input(value=self._default_path, placeholder="./md2pdf.yaml", id="config-path"),
            Static("", id="config-msg", classes="preview"),
            Horizontal(
                Button("Abbrechen", id="cancel"),
                Button("Speichern", variant="primary", id="save"),
                classes="btn-row",
            ),
            classes="wizard-box",
        )
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#save")
    def save(self) -> None:
        path_str = self.query_one("#config-path", Input).value.strip()
        if not path_str:
            self.query_one("#config-msg", Static).update("[red]Bitte einen Pfad angeben.[/red]")
            return
        path = _resolve_path(path_str)
        try:
            save_config_from_wizard(self.app.wizard_data, path)
            self.query_one("#config-msg", Static).update(f"[green]Gespeichert: {path}[/green]")
            self.app.pop_screen()
        except OSError as e:
            self.query_one("#config-msg", Static).update(f"[red]Fehler: {e}[/red]")


# ── App ────────────────────────────────────────────────────────────────────────

WIZARD_CSS = """
Screen {
    background: $surface;
}

.brand {
    text-style: bold;
    color: $accent;
    padding: 0 0 0 1;
    margin-bottom: 0;
}

.step-label {
    color: $text-muted;
    padding: 0 0 1 1;
    border-bottom: solid $primary-darken-2;
    margin-bottom: 1;
}

.wizard-box {
    margin: 1 2;
    padding: 1 2;
}

.option-row {
    height: 3;
    align: left middle;
    margin-bottom: 1;
}

.option-row Label {
    width: 30;
    padding-right: 2;
}

.btn-row {
    margin-top: 1;
    height: 3;
    align: left middle;
}

.btn-row Button {
    margin-right: 1;
}

.preview {
    padding: 1;
    color: $text-muted;
    margin-top: 1;
    height: auto;
    max-height: 8;
    overflow: hidden;
}

.summary-table {
    padding: 1 0;
    height: auto;
}

#file-select {
    margin-bottom: 1;
}

Input {
    margin-bottom: 1;
}

Label {
    margin-top: 1;
}

ListView {
    height: 12;
    border: solid $primary-darken-2;
}
"""


class WizardApp(App):
    """The md2pdf interactive TUI wizard."""

    CSS = WIZARD_CSS
    TITLE = "md2pdf"
    SUB_TITLE = "Interactive Mode"
    BINDINGS = [Binding("q", "quit", "Beenden")]

    def __init__(self) -> None:
        super().__init__()
        self.wizard_data: dict[str, Any] = {}

    def on_mount(self) -> None:
        self.push_screen(FileSelectScreen())


def run_interactive() -> dict[str, Any] | None:
    """Launch the wizard, return collected config or None if cancelled."""
    app = WizardApp()
    result = app.run()
    return result if isinstance(result, dict) else None
