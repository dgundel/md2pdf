"""Generate table-of-contents HTML from heading entries."""

from __future__ import annotations

from md2pdf.core.parser import TocEntry

LANG_STRINGS = {
    "de": "Inhaltsverzeichnis",
    "en": "Table of Contents",
    "fr": "Table des matières",
    "es": "Índice",
    "it": "Indice",
}


def build_toc_html(entries: list[TocEntry], lang: str = "de") -> str:
    """Build a nested <ul> TOC from heading entries."""
    if not entries:
        return ""

    title = LANG_STRINGS.get(lang, LANG_STRINGS["en"])
    min_level = min(e.level for e in entries)

    lines = [
        f'<nav class="toc">',
        f"  <h2 class=\"toc-title\">{title}</h2>",
        "  <ul>",
    ]

    prev_level = min_level
    for entry in entries:
        rel = entry.level - min_level
        if entry.level > prev_level:
            lines.append("  " * rel + "<ul>")
        elif entry.level < prev_level:
            for _ in range(prev_level - entry.level):
                lines.append("  " * rel + "</ul>")

        indent = "  " * (rel + 2)
        lines.append(
            f'{indent}<li>'
            f'<a href="#{entry.anchor}">{entry.title}</a>'
            f"</li>"
        )
        prev_level = entry.level

    # Close any open nested lists
    for _ in range(prev_level - min_level):
        lines.append("    </ul>")

    lines += ["  </ul>", "</nav>"]
    return "\n".join(lines)
