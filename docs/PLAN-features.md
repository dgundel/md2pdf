# Implementierungsplan: Features 1, 3, 6, 9, 10, 11

Übersicht der geplanten Änderungen mit Reihenfolge und betroffenen Dateien.

---

## Reihenfolge (Abhängigkeiten beachten)

| Phase | Thema | Abhängigkeit |
|-------|--------|--------------|
| A | **9. Exit-Codes** | keine – Basis für alle Commands |
| B | **3. Umgebungsvariablen** | keine – wird von convert genutzt |
| C | **6. Wasserzeichen erweitert** | nutzt Config wie 3 |
| D | **1. Shell-Completion** | keine |
| E | **11. Config aus Wizard speichern** | nutzt gleiche Config-Struktur wie YAML |
| F | **10. README aufhübschen** | optional zuletzt – zeigt alle Features |

Empfohlene Umsetzung: **A → B → C → D → E → F**.

---

## 9. Exit-Codes dokumentieren und einhalten

**Ziel:** Einheitliche Exit-Codes für Skripte/CI; in README dokumentieren.

**Definierte Codes:**

| Code | Bedeutung | Wann |
|------|-----------|------|
| 0 | Erfolg | Conversion/Command OK |
| 1 | Allgemeiner Fehler | Unerwarteter Fehler, z. B. WeasyPrint-Exception |
| 2 | Nutzung/Validierung | Ungültige Optionen, Theme nicht gefunden, Validierung |
| 3 | I/O | Datei nicht gefunden, Schreibfehler, Permission denied |

**Änderungen:**

1. **Neues Modul `md2pdf/utils/exit_codes.py`** (oder Konstanten in `cli/main.py`):
   - `EXIT_OK = 0`, `EXIT_ERROR = 1`, `EXIT_USAGE = 2`, `EXIT_IO = 3`.
   - Optional: kleine Hilfsfunktion `sys.exit(exit_code)` mit Logging.

2. **`md2pdf/cli/main.py`:**
   - Beim Aufruf von `run_convert`: Rückgabe nicht nur `True/False`, sondern ggf. einen Code (oder weiter `bool` und Mapping `True→0`, `False→1`).
   - `cmd_convert`: statt `raise typer.Exit(0 if success else 1)` → bei `FileNotFoundError` (source), `Theme not found` → Exit 2; bei fehlgeschlagener PDF-Erstellung → 1; bei fehlendem Output-Pfad (Schreibfehler) → 3.
   - `run_convert` sollte explizit `FileNotFoundError` werfen oder einen Fehlertyp zurückgeben, damit main zwischen 2 und 3 unterscheiden kann. **Pragmatisch:** `run_convert` gibt `bool` zurück; in `run_convert` bei „source nicht gefunden“ und „Theme nicht gefunden“ bereits `print_error` + `return False` (Exit 1 vom Callback). Für 2/3: optional in `run_convert` eigene Exceptions oder ein Enum zurückgeben (z. B. `Success`, `UsageError`, `IOError`), dann in `cmd_convert` entsprechend `typer.Exit(2)` / `typer.Exit(3)`.
   - **Einfachvariante:** Nur 0 und 1 nutzen, in README dokumentieren: „0 = Erfolg, 1 = Fehler“. Später 2/3 ergänzen.

3. **`md2pdf/cli/commands/convert.py`:**
   - Bei `source.exists()` → False: Aufrufer soll Exit 3 (I/O) setzen.
   - Bei `load_theme` FileNotFoundError: Exit 2 (Usage/Config).
   - Bei `render_pdf` Fehler: Exit 1.
   - Dazu: `run_convert` könnte einen Enum oder ein kleines Result-Objekt zurückgeben: `(success: bool, exit_code: int)` oder Exceptions durchreichen. **Empfehlung:** `run_convert` returniert ein Tuple `(bool, int)` z. B. `(True, 0)`, `(False, 2)`, `(False, 3)`.

4. **README.md:** Neuer Abschnitt „Exit-Codes“ (z. B. nach CLI-Referenz) mit Tabelle und Beispiel für Skripte:
   ```bash
   md2pdf convert doc.md
   case $? in 0) echo OK ;; 2) echo Config/Theme ;; 3) echo Datei/IO ;; *) echo Fehler ;; esac
   ```

**Dateien:** `md2pdf/utils/exit_codes.py` (neu), `md2pdf/cli/main.py`, `md2pdf/cli/commands/convert.py`, `README.md`.

---

## 3. Umgebungsvariablen für CI/CD

**Ziel:** Optionale Konfiguration über `MD2PDF_*`; Priorität: CLI > Env > Frontmatter > Defaults.

**Vorgesehene Variablen (Auswahl):**

- `MD2PDF_THEME` – Theme-Name
- `MD2PDF_TOC` – 1/true/yes = TOC an
- `MD2PDF_TITLE` – Dokumenttitel
- `MD2PDF_AUTHOR` – Autor
- `MD2PDF_LANG` – Sprache (de, en, …)
- `MD2PDF_PAGE_SIZE` – A4, A5, Letter
- `MD2PDF_WATERMARK` – Wasserzeichen-Text (falls 6 noch nicht erweitert)
- `MD2PDF_CONFIG` – Pfad zu Config-Datei (für 11)

Unbekannte `MD2PDF_*` können mit Warning ignoriert werden (optional).

**Änderungen:**

1. **Neues Modul `md2pdf/config/env.py`:**
   - `get_env_config() -> dict`: `os.environ` nach `MD2PDF_*` durchsuchen, Keys normalisieren (z. B. `MD2PDF_THEME` → `theme`), Werte typgerecht (z. B. `MD2PDF_TOC` → bool), dict zurückgeben.
   - Gültige Keys dokumentieren (Liste oder Konstante).

2. **`md2pdf/config/frontmatter.py`:**
   - In `frontmatter_to_jobconfig`: nach `overrides` und vor Nutzung der Defaults die Env-Config einlesen. Regel: **CLI-Overrides > Env > Frontmatter > Defaults**. D. h. Env-Werte nur setzen, wenn der Key nicht schon in `overrides` vorkommt.
   - Signatur anpassen: z. B. `overrides: dict` um Env-Dict ergänzen (intern: `effective = {**get_env_config(), **overrides}` für Defaults).

3. **`md2pdf/cli/commands/convert.py`:**
   - Beim Aufbau von `overrides` die CLI-Werte weiterhin zuerst setzen. Env kommt in `frontmatter_to_jobconfig` (siehe oben). Keine doppelte Logik in convert nötig, wenn frontmatter alle Env-Werte als „Override-Niedrigpriorität“ bekommt.

4. **README.md:** Abschnitt „Umgebungsvariablen“ mit Tabelle (Variable, Beschreibung, Beispiel).

**Dateien:** `md2pdf/config/env.py` (neu), `md2pdf/config/frontmatter.py`, `README.md`.

---

## 6. Wasserzeichen erweiterbar (Farbe, Opacity, Winkel)

**Ziel:** Wasserzeichen nicht nur Text, sondern auch Farbe, Deckkraft, Winkel konfigurierbar (Frontmatter + CLI + Env).

**Änderungen:**

1. **`md2pdf/config/schema.py`:**
   - Neues Modell `WatermarkConfig(BaseModel)`:
     - `text: str = ""` (leer = kein Wasserzeichen)
     - `color: str = "#b4b4b4"`
     - `opacity: float = 0.18` (0.0–1.0)
     - `angle: float = -35` (Grad)
   - `JobConfig`: `watermark: str | None` ersetzen durch `watermark: WatermarkConfig | None = None`. **Abwärtskompatibel:** Wenn Frontmatter/CLI weiterhin nur `watermark: "ENTWURF"` liefert, beim Parsen in ein `WatermarkConfig(text="ENTWURF")` umwandeln (in frontmatter_to_jobconfig oder Validator).

2. **`md2pdf/config/frontmatter.py`:**
   - Bei `fm.get("watermark")`: wenn str → `WatermarkConfig(text=...)`; wenn dict → `WatermarkConfig(**...)`.
   - Env: z. B. `MD2PDF_WATERMARK` (nur Text), optional `MD2PDF_WATERMARK_COLOR`, `_OPACITY`, `_ANGLE` für Erweiterung.

3. **`md2pdf/core/renderer.py`:**
   - `watermark` als `WatermarkConfig | None` an Template übergeben; wenn `config.watermark` None oder `config.watermark.text` leer → kein Wasserzeichen.

4. **`templates/base.html`:**
   - Wasserzeichen-Block: statt fester Werte `content`, `color`, `transform` aus Template-Variablen:
     - `watermark_text`, `watermark_color`, `watermark_opacity`, `watermark_angle`.
   - CSS: `color: {{ watermark_color }}` (evtl. als rgba mit opacity), `opacity: {{ watermark_opacity }}`, `transform: translate(-50%,-50%) rotate({{ watermark_angle }}deg)`.

5. **CLI `md2pdf/cli/main.py` + `commands/convert.py`:**
   - Optionen: `--watermark TEXT`, `--watermark-color`, `--watermark-opacity`, `--watermark-angle` (optional, nur wenn ihr die einfache Variante erweitern wollt). Sonst nur Frontmatter + Env.

6. **README + Frontmatter-Doku:** Wasserzeichen-Beispiel um color/opacity/angle erweitern.

**Dateien:** `md2pdf/config/schema.py`, `md2pdf/config/frontmatter.py`, `md2pdf/core/renderer.py`, `templates/base.html`, ggf. `md2pdf/cli/main.py`, `md2pdf/cli/commands/convert.py`, `README.md`.

---

## 1. Shell-Completion

**Ziel:** `md2pdf completion bash|zsh|fish` (evtl. PowerShell) ausgeben; Nutzer kann das in Shell-Profil einbinden.

**Änderungen:**

1. **`md2pdf/cli/main.py`:**
   - Typer unterstützt Completion: `add_completion=True` (oder expliziter Befehl). Typer hat `@app.command()` für `completion` mit Unteroptionen für shell. Siehe Typer-Doku: `typer.main.get_completion_info()` oder eingebauter `completion`-Befehl.
   - **Variante A:** Neuer Befehl `completion` mit Option `--shell [bash|zsh|fish|powershell]`, ruft intern z. B. `typer.main.get_completion_info()` oder nutzt Click’s `get_completion_script` (Typer baut auf Click). Typer: `app = typer.Typer(add_completion=True)` fügt automatisch `md2pdf --install-completion` / `md2pdf --show-completion` hinzu.
   - **Variante B:** Eigenes Command `md2pdf completion bash` das die Completion-Script-Generierung auslöst. In Typer: `import typer; print(typer.main.get_completion_script(shell="bash"))` o. ä. – genaue API prüfen.
   - Praktisch: `add_completion=True` setzen, dann gibt es z. B. `--install-completion` und `--show-completion`. In README dokumentieren: „Shell-Completion: `eval \"$(md2pdf --show-completion bash)\"`“ (oder wie Typer es ausgibt).

2. **README.md:** Abschnitt „Shell-Completion“ mit Befehlen für bash, zsh, fish.

**Dateien:** `md2pdf/cli/main.py`, `README.md`.

---

## 11. Config aus Wizard speichern

**Ziel:** Nach dem interaktiven Wizard optional eine YAML-Config-Datei speichern; `convert` kann diese Datei mit `-c/--config` laden.

**Änderungen:**

1. **Config-Datei-Format:** Eine YAML-Datei, die zu den bestehenden Frontmatter-/Job-Optionen passt, z. B.:
   - `theme`, `toc`, `title_page`, `author`, `title`, `lang`, `page_size`, `watermark` (evtl. als Objekt wenn 6 umgesetzt), `page_numbers` (enabled, format, position). Kein `source`/`output` (die bleiben CLI-Argumente).

2. **`md2pdf/config/schema.py` oder neues `md2pdf/config/file_config.py`:**
   - Modell für die gespeicherte Config (nur Optionen, die der Wizard setzt), z. B. `SavedJobConfig` oder Wiederverwendung von Teilen von `JobConfig` (ohne source/output).

3. **`md2pdf/cli/interactive.py`:**
   - Nach erfolgreichem „Rendern“ (oder auf separatem Schritt): Optionaler Schritt „Config speichern?“ mit Eingabe des Pfads (Default: `./md2pdf.yaml` oder `~/.config/md2pdf/default.yaml`). Wenn Nutzer Pfad bestätigt: `wizard_data` in YAML schreiben (nur die Keys, die als Config sinnvoll sind).
   - Oder: Neuer Button „Config speichern“ auf Summary-Screen, der einen FileDialog oder Input für Pfad öffnet (Textual: `Input` mit Default-Pfad). Gespeichert wird dann die aktuelle `wizard_data` als YAML.

4. **`md2pdf/cli/main.py` (convert):**
   - Neue Option `--config` / `-c` (Pfad zu YAML). Wenn gesetzt: Datei laden, Werte als Default-Overrides für diesen Run verwenden (Priorität: CLI > Config-Datei > Env > Frontmatter).

5. **`md2pdf/config/frontmatter.py` oder neue Funktion:**
   - `load_config_file(path: Path) -> dict`: YAML lesen, dict zurückgeben. Dieses dict wird in `frontmatter_to_jobconfig` als zusätzliche Override-Quelle verwendet (unterhalb CLI, über Env/Frontmatter).

6. **`md2pdf/cli/commands/convert.py`:**
   - Wenn `config_path` gesetzt: `load_config_file(config_path)` aufrufen und das Ergebnis in `overrides` einarbeiten (mit niedrigerer Priorität als die expliziten CLI-Argumente). D. h. zuerst Config-Datei laden → als Basis-Overrides; dann CLI-Overrides oben drauf.

7. **README:** Config-Wizard und `-c` in CLI-Referenz und ggf. eigenem Abschnitt beschreiben.

**Dateien:** `md2pdf/config/file_config.py` oder Erweiterung in `frontmatter.py`, `md2pdf/cli/interactive.py`, `md2pdf/cli/main.py`, `md2pdf/cli/commands/convert.py`, `README.md`.

---

## 10. README aufhübschen

**Ziel:** Inhaltsverzeichnis, Beispiele, ggf. weitere Badges.

**Änderungen:**

1. **Table of Contents** oben unter der Beschreibung:
   - Links zu: Installation, Schnellstart, CLI-Referenz, Frontmatter, Includes, Themes, (ASCII/Emoji), Entwicklung, Lizenz, Contributing. Mit Anker-IDs (GitHub erzeugt sie aus Überschriften automatisch).

2. **Beispiele:**
   - Ordner `examples/` anlegen (oder im Repo belassen und in README verlinken).
   - Mindestens eine Beispiel-Markdown-Datei + optional ein Screenshot/PDF-Vorschau (z. B. `examples/example-output.png` oder Hinweis „Siehe Beispiel-PDF in `examples/`“). In README: „[Beispiel-PDFs](examples/)“.

3. **Badges:**
   - Bereits: CI.
   - Optional: License (MIT), Python 3.x. Kein Codecov nötig, wenn kein Coverage-Step in CI.

4. **Struktur:** Kurz prüfen, dass alle neuen Features (Env, Exit-Codes, Completion, Config speichern, Wasserzeichen-Optionen) in der passenden Sektion erwähnt werden.

**Dateien:** `README.md`, ggf. `examples/README.md` oder eine `examples/sample.md` + optional Screenshot.

---

## Kurz-Checkliste

- [ ] **9** – Exit-Codes Modul + convert/main anpassen + README
- [ ] **3** – `config/env.py` + Frontmatter + README Env-Tabelle
- [ ] **6** – WatermarkConfig + Schema/Frontmatter/Renderer/Template + CLI/Frontmatter-Doku
- [ ] **1** – Typer Completion aktivieren + README Completion
- [ ] **11** – Config speichern im Wizard + `-c` in convert + load_config_file + README
- [ ] **10** – README TOC + examples/ + Badges

Nach dem Plan können die Punkte nacheinander in dieser Reihenfolge umgesetzt werden.
