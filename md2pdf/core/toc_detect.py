"""Erkennt ein im Dokument vorhandenes Inhaltsverzeichnis (Liste mit #-Links) und markiert es für Seitenzahlen."""

from __future__ import annotations

import re


def _find_first_toc_list(html: str) -> tuple[int, int, str] | None:
    """Findet die erste <ul> oder <ol>, die wie ein TOC aussieht (mehrere Links zu #...).

    Returns (start_pos, end_pos, tag) des öffnenden Tags oder None.
    """
    # Öffnendes Tag: <ul> oder <ol> mit optionalen Attributen
    tag_pattern = re.compile(r"<(ul|ol)(\s[^>]*)?>", re.IGNORECASE)
    # Link zu Anker im Dokument
    anchor_link = re.compile(r'<a\s[^>]*href\s*=\s*["\']#', re.IGNORECASE)

    pos = 0
    while True:
        m = tag_pattern.search(html, pos)
        if not m:
            break
        tag = m.group(1).lower()
        open_start, open_end = m.start(), m.end()
        # Nur das passende Schließ-Tag für diesen Tag-Typ zählen (ul/ol getrennt)
        open_re = re.compile(r"<" + re.escape(tag) + r"(\s[^>]*)?>", re.IGNORECASE)
        close_re = re.compile(r"</" + re.escape(tag) + r"\s*>", re.IGNORECASE)
        depth = 1
        search_start = open_end
        while depth > 0:
            next_open = open_re.search(html, search_start)
            next_close = close_re.search(html, search_start)
            if next_close and (not next_open or next_close.start() < next_open.start()):
                depth -= 1
                if depth == 0:
                    content = html[open_end : next_close.start()]
                    if len(anchor_link.findall(content)) >= 2:
                        return (open_start, open_end, tag)
                search_start = next_close.end()
            elif next_open:
                depth += 1
                search_start = next_open.end()
            else:
                break
        pos = open_end
    return None


def mark_inline_toc(html: str) -> tuple[str, bool]:
    """Wenn am Anfang des Inhalts eine TOC-Liste (ul/ol mit #-Links) steht, wird sie mit
    class=\"toc-in-document\" markiert, damit CSS Seitenzahlen anzeigen kann.

    Returns (modified_html, had_inline_toc).
    """
    found = _find_first_toc_list(html)
    if not found:
        return html, False

    open_start, open_end, tag = found
    # Füge class="toc-in-document" ins öffnende Tag ein
    opening_tag = html[open_start:open_end]
    if 'class="' in opening_tag:
        opening_tag = opening_tag.replace('class="', 'class="toc-in-document ')
    elif "class='" in opening_tag:
        opening_tag = opening_tag.replace("class='", "class='toc-in-document ")
    else:
        opening_tag = opening_tag.replace(">", ' class="toc-in-document">')

    new_html = html[:open_start] + opening_tag + html[open_end:]
    return new_html, True
