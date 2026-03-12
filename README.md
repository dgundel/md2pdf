# ✦ md2pdf

Convert Markdown to beautiful, professional PDFs — with themes, includes, TOC, title pages, and a gorgeous interactive CLI.

[![CI](https://github.com/dgundel/md2pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/dgundel/md2pdf/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Inhaltsverzeichnis

- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [CLI-Referenz](#cli-referenz)
- [Frontmatter-Konfiguration](#frontmatter-konfiguration)
- [Include-System](#include-system)
- [Themes](#themes)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)
- [Contributing](#contributing)

## Installation

**Aus Quellcode (empfohlen):**

```bash
git clone https://github.com/dgundel/md2pdf.git
cd md2pdf
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
# oder: pip install -r requirements.txt
```

**Systemweiter Aufruf `md2pdf`:** Symlink in ein Verzeichnis legen, das in deiner `PATH` liegt (z. B. `~/.local/bin`):

```bash
ln -sf "$(pwd)/bin/md2pdf" ~/.local/bin/md2pdf
```

Danach kannst du von überall `md2pdf convert …` usw. aufrufen. Voraussetzung: `~/.local/bin` steht in deiner PATH (bei den meisten Linux-Desktops bereits der Fall).

Für Emoji-Support (Linux):
```bash
sudo apt install fonts-noto-color-emoji
```

## Schnellstart

[Beispiel-Datei](examples/sample.md) zum Ausprobieren: `md2pdf convert examples/sample.md -o beispiel.pdf`

Nach Aktivierung des venv (`source .venv/bin/activate`) im Projektordner:

```bash
# Einfachste Verwendung (Launcher-Skript)
./md2pdf_run.py convert report.md

# Oder direkt als Modul
python -m md2pdf.cli.main convert report.md

# Mit Theme und TOC
./md2pdf_run.py convert report.md --theme academic --toc

# Interaktiver Wizard
./md2pdf_run.py interactive
# oder: ./md2pdf_run.py
```

---

## CLI-Referenz

### `md2pdf convert`

```
./md2pdf_run.py convert <datei.md> [OPTIONS]

Optionen:
  -o, --output PATH          Ausgabe-PDF (default: <input>.pdf)
  -c, --config PATH          Config-Datei (YAML) laden — Werte als Basis, CLI überschreibt
  -t, --theme TEXT           Theme-Name oder Pfad zu .yaml  [default: default]
  --toc                      Inhaltsverzeichnis generieren
  --title-page               Titelseite aktivieren
  --author TEXT              Autor-Name
  --title TEXT               Dokumenttitel
  --lang TEXT                Sprache (de/en/fr/...)  [default: de]
  --page-size TEXT           A4 | A5 | Letter  [default: A4]
  --watermark TEXT           Wasserzeichen-Text (z.B. "ENTWURF")
  --no-page-numbers          Seitenzahlen deaktivieren
  --page-number-format TEXT  Format z.B. "{page}/{total}"
  --extra-css PATH           Zusätzliche CSS-Datei
  --open                     PDF nach Erstellung öffnen
  -v, --verbose              Ausführliche Ausgabe
```

### `md2pdf watch`

Automatisches Re-Rendering bei Dateiänderungen:

```bash
./md2pdf_run.py watch report.md --theme minimal
```

Beobachtet die Quelldatei **und alle eingebetteten Includes**.

### `md2pdf batch`

Mehrere Dateien auf einmal konvertieren:

```bash
./md2pdf_run.py batch "docs/*.md" --output-dir ./pdfs --theme corporate
```

### `md2pdf themes`

Alle verfügbaren Themes mit Farbvorschau anzeigen:

```bash
./md2pdf_run.py themes
```

### `md2pdf interactive`

Interaktiver TUI-Wizard mit Schritt-für-Schritt-Konfiguration:

```bash
./md2pdf_run.py interactive
# oder einfach:
./md2pdf_run.py
```

### Shell-Completion

Tab-Completion für Befehle und Optionen:

```bash
# Bash — in ~/.bashrc eintragen
eval "$(md2pdf --show-completion bash)"

# Zsh — in ~/.zshrc eintragen
eval "$(md2pdf --show-completion zsh)"

# Fish — Completions speichern
md2pdf --show-completion fish > ~/.config/fish/completions/md2pdf.fish
```

Einmalig installieren (persistent): `md2pdf --install-completion zsh` (bzw. bash/fish).

### Exit-Codes

Für Skripte und CI:

| Code | Bedeutung |
|------|-----------|
| 0 | Erfolg |
| 1 | Allgemeiner Fehler (z. B. PDF-Erstellung fehlgeschlagen) |
| 2 | Nutzung/Validierung (ungültige Optionen, Theme nicht gefunden) |
| 3 | I/O (Datei nicht gefunden, Schreibfehler) |

Beispiel:

```bash
md2pdf convert doc.md
case $? in
  0) echo "OK" ;;
  2) echo "Config/Theme prüfen" ;;
  3) echo "Datei/Rechte prüfen" ;;
  *) echo "Fehler" ;;
esac
```

---

## Frontmatter-Konfiguration

Konfiguriere das Dokument direkt im Markdown-Header:

```yaml
---
title: "Projektbericht Q1"
subtitle: "Interne Dokumentation"
author: "Anna Schmidt"
date: "2026-03-11"
version: "1.2.0"
theme: corporate
logo: ./assets/logo.png
toc: true
lang: de
page_size: A4
watermark: "ENTWURF"   # oder erweitert:
# watermark:
#   text: "ENTWURF"
#   color: "#888888"
#   opacity: 0.15
#   angle: -45
page_numbers:
  format: "Seite {page} von {total}"
  position: bottom-center
title_page:
  enabled: true
---
```

**Priorität:** CLI-Flags > Config-Datei (`-c`) > Umgebungsvariablen > Frontmatter > Defaults

**Config-Datei aus Wizard:** Im interaktiven Modus (Schritt 4) auf „Config speichern“ klicken und Pfad angeben (z. B. `./md2pdf.yaml`). Anschließend: `md2pdf convert doc.md -c md2pdf.yaml`.

### Umgebungsvariablen (CI/CD)

Optionale Konfiguration über `MD2PDF_*`:

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `MD2PDF_THEME` | Theme-Name | `academic` |
| `MD2PDF_TOC` | Inhaltsverzeichnis (1/true/yes = an) | `1` |
| `MD2PDF_TITLE` | Dokumenttitel | `Bericht Q1` |
| `MD2PDF_AUTHOR` | Autor | `Max Mustermann` |
| `MD2PDF_LANG` | Sprache | `de`, `en` |
| `MD2PDF_PAGE_SIZE` | Seitengröße | `A4`, `Letter` |
| `MD2PDF_WATERMARK` | Wasserzeichen-Text | `ENTWURF` |
| `MD2PDF_CONFIG` | Pfad zu Config-Datei (bei `-c`) | `./md2pdf.yaml` |

Beispiel GitHub Actions:

```yaml
- name: PDF erzeugen
  env:
    MD2PDF_THEME: corporate
    MD2PDF_TOC: "1"
    MD2PDF_AUTHOR: ${{ github.repository_owner }}
  run: md2pdf convert ./docs/ -o ./out/
```

---

## Include-System

Bette andere Markdown-Dateien ein — ideal für modulare Dokumentation.

### Syntax

```markdown
![[dateiname.md]]
![[dateiname.md | key=value | key2=value2]]
```

### Platzhalter in Sub-Dateien

`ersatzteilliste.md`:
```markdown
---
defaults:
  modell: "Unbekanntes Modell"
  artikelnr: "XXX-000"
---

## Ersatzteilliste — {{modell}}

| Pos. | Art.-Nr.            |
|------|---------------------|
| 1    | {{artikelnr}}-01    |
| 2    | {{artikelnr}}-02    |
```

`bedienungsanleitung.md`:
```markdown
# Bedienungsanleitung

![[ersatzteilliste.md | modell="AX-990" | artikelnr="AX-990"]]
![[ersatzteilliste.md | modell="AX-500" | artikelnr="AX-500"]]
```

### Regeln

- Pfade relativ zur einbettenden Datei
- Verschachtelung bis 10 Ebenen
- Zirkuläre Includes werden erkannt und als Fehler gemeldet
- Nicht gefundene Variablen bleiben als `{{var}}` sichtbar + Warning
- TOC enthält alle Headings aus allen Includes

---

## Themes

Sechs eingebaute Themes:

| Theme       | Stil                          |
|-------------|-------------------------------|
| `default`   | Klassisch, serifenlose Überschriften |
| `academic`  | Akademisch, serifenbetonter Fließtext |
| `minimal`   | Maximale Reduktion, kein Schnörkel |
| `corporate` | Professionell, Corporate-Blau |
| `dark`      | Dunkler Hintergrund           |
| `github`    | GitHub Markdown-Style         |
| `liberation`| Liberation Serif/Sans/Mono (system fonts) |

### Custom Theme

Eigenes Theme als `.yaml`:

```yaml
name: mein-theme

colors:
  primary: "#e63946"
  text: "#1d3557"
  background: "#f1faee"
  code_bg: "#e8f4f8"
  link: "#e63946"
  border: "#a8dadc"
  heading: "#1d3557"
  table_header_bg: "#457b9d"

fonts:
  body: "Georgia, serif"
  heading: "'Helvetica Neue', sans-serif"
  mono: "'JetBrains Mono', monospace"
  emoji_fallback:
    - "Noto Color Emoji"
    - "Apple Color Emoji"
  base_size: "11pt"

margins:
  top: 25
  right: 20
  bottom: 25
  left: 20

header:
  show: false
footer:
  show: true
  border: false
```

Verwenden:
```bash
./md2pdf_run.py convert report.md --theme ./mein-theme.yaml
```

Oder unter `~/.config/md2pdf/themes/mein-theme.yaml` ablegen — wird automatisch erkannt.

---

## ASCII-Diagramme

ASCII-Diagramme in Code-Blöcken werden mit einem Monospace-Font gerendert der Box-Drawing-Zeichen perfekt darstellt:

````markdown
```
┌─────────────┐     ┌──────────────────┐
│  Parser     │────▶│   Config         │
└─────────────┘     └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Pipeline       │
                    └──────────────────┘
```
````

Unterstützte Zeichen: `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯ → ← ▶ ▼ ▲`

---

## Emoji-Support

Emojis werden über einen Font-Fallback-Stack unterstützt. Alle Themes enthalten:

```
Noto Color Emoji → Apple Color Emoji → Segoe UI Emoji
```

Auf Linux:
```bash
sudo apt install fonts-noto-color-emoji
```

---

## Entwicklung

```bash
git clone https://github.com/dgundel/md2pdf.git
cd md2pdf
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

## Lizenz

[MIT](LICENSE).

## Contributing

Issues und Pull Requests sind willkommen. Bitte zuerst ein Issue öffnen für größere Änderungen.
