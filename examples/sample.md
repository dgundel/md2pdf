---
title: "md2pdf Beispiel"
subtitle: "Demonstration der Features"
author: "Max Mustermann"
theme: default
toc: true
title_page: true
lang: de
page_size: A4
---

# Einleitung

Dieses Dokument zeigt **md2pdf**-Features: Titelseite, Inhaltsverzeichnis, Code-Blöcke und Tabellen.

## Überschrift Ebene 2

Normaler Fließtext mit *Kursiv* und **Fett**.

### Code

```python
def hello():
    print("Hallo, md2pdf!")
```

### Tabelle

| Feature   | Unterstützt |
|----------|-------------|
| TOC      | ✓           |
| Titelseite | ✓         |
| Themes   | ✓           |

## Fazit

PDF mit `md2pdf convert sample.md` erzeugen.
