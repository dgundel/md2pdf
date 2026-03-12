"""Resolve and embed images as Base64 data URIs."""

from __future__ import annotations

import base64
import re
from pathlib import Path

SUPPORTED = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}

IMG_SRC_RE = re.compile(r'(<img\s[^>]*src=")([^"]+)(")', re.IGNORECASE)


def embed_images(html: str, base_dir: Path) -> tuple[str, list[str]]:
    """Replace all <img src="..."> with base64 data URIs.

    Returns (modified_html, list_of_warnings).
    """
    warnings: list[str] = []

    def replacer(m: re.Match) -> str:
        prefix, src, suffix = m.group(1), m.group(2), m.group(3)
        if src.startswith("data:") or src.startswith("http"):
            return m.group(0)  # already embedded or remote — leave as-is

        img_path = (base_dir / src).resolve()
        if not img_path.exists():
            warnings.append(f"⚠  Bild nicht gefunden: {src}")
            # Return a placeholder
            name = Path(src).name
            placeholder = (
                f'<span class="img-missing" title="Bild nicht gefunden: {name}">'
                f"[Bild: {name}]</span>"
            )
            return placeholder

        ext = img_path.suffix.lower()
        mime = SUPPORTED.get(ext, "image/png")
        data = base64.b64encode(img_path.read_bytes()).decode("ascii")
        return f'{prefix}data:{mime};base64,{data}{suffix}'

    result = IMG_SRC_RE.sub(replacer, html)
    return result, warnings
