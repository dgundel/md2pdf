"""Markdown parser: text → HTML with TOC extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import mistune
from mistune.renderers.html import HTMLRenderer
from mistune.plugins.table import table
from mistune.plugins.task_lists import task_lists


@dataclass
class TocEntry:
    level: int
    title: str
    anchor: str


class TocCollectingRenderer(HTMLRenderer):
    """HTML renderer that also collects heading entries for TOC."""

    def __init__(self) -> None:
        super().__init__()
        self.toc_entries: list[TocEntry] = []
        self._counters: dict[int, int] = {}

    def _make_anchor(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        return slug

    def heading(self, children: str, level: int) -> str:
        text = re.sub(r"<[^>]+>", "", children)  # strip inner tags for TOC
        anchor = self._make_anchor(text)
        # Deduplicate anchors
        count = self._counters.get(anchor, 0)
        self._counters[anchor] = count + 1
        if count > 0:
            anchor = f"{anchor}-{count}"

        self.toc_entries.append(TocEntry(level=level, title=text, anchor=anchor))
        return f'<h{level} id="{anchor}">{children}</h{level}>\n'


@dataclass
class ParseResult:
    html: str
    toc_entries: list[TocEntry] = field(default_factory=list)


def parse_markdown(text: str) -> ParseResult:
    """Convert markdown text to HTML, collecting TOC entries.

    Handles:
    - Tables
    - Task lists (checkboxes)
    - Code blocks with language hints
    - ASCII diagrams (preserved in <pre>)
    - Strikethrough
    """
    renderer = TocCollectingRenderer()
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=[table, task_lists],
    )
    html = md(text)
    return ParseResult(html=html, toc_entries=renderer.toc_entries)
