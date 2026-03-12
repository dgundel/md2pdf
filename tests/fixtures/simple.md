---
title: "Testdokument"
author: "Test Author"
lang: de
---

# Hauptüberschrift

Dies ist ein einfaches Testdokument mit **fett** und *kursiv*.

## Abschnitt 1

Ein Absatz mit einem [Link](https://example.com) und `inline code`.

### Unterabschnitt 1.1

- Listenpunkt A
- Listenpunkt B
- Listenpunkt C

## Abschnitt 2 — Tabelle

| Spalte 1 | Spalte 2 | Spalte 3 |
|----------|----------|----------|
| Wert A   | Wert B   | Wert C   |
| Wert D   | Wert E   | Wert F   |

## Abschnitt 3 — Code

```python
def hello(name: str) -> str:
    return f"Hallo, {name}!"

print(hello("Welt"))
```

## Abschnitt 4 — ASCII-Diagramm

```
┌─────────────┐     ┌──────────────────┐
│  Frontmatter│────▶│   JobConfig      │◀── CLI-Flags
│  Parser     │     │  (Pydantic)      │◀── ~/.md2pdf.yaml
└─────────────┘     └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Theme Loader    │
                    └────────┬─────────┘
                             │
              ┌──────────────▼──────────────┐
              │         Pipeline            │
              └─────────────────────────────┘
```

## Abschnitt 5 — Emoji

Unterstützte Zeichen: ✓ ✗ → ← ▶ ▼ ⚠ 🎉 🔥 ✦

## Abschnitt 6 — Checkboxen

- [x] Feature implementiert
- [x] Tests geschrieben
- [ ] Dokumentation fertig
- [ ] Release vorbereitet
