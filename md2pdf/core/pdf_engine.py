"""PDF engine: HTML → PDF via WeasyPrint."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PdfResult:
    success: bool
    output_path: Path | None = None
    page_count: int = 0
    file_size_bytes: int = 0
    error: str | None = None


def render_pdf(html: str, output_path: Path) -> PdfResult:
    """Render HTML to PDF using WeasyPrint.

    Returns a PdfResult with metadata about the generated file.
    """
    try:
        from weasyprint import HTML  # type: ignore
        from weasyprint.document import Document  # type: ignore

        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc: Document = HTML(string=html, base_url=str(output_path.parent)).render()
        page_count = len(doc.pages)
        doc.write_pdf(output_path)

        return PdfResult(
            success=True,
            output_path=output_path,
            page_count=page_count,
            file_size_bytes=output_path.stat().st_size,
        )
    except ImportError:
        return PdfResult(
            success=False,
            error=(
                "WeasyPrint ist nicht installiert.\n"
                "  → pip install weasyprint"
            ),
        )
    except Exception as exc:
        return PdfResult(success=False, error=str(exc))
