#!/usr/bin/env python3
"""Launcher: aus Projektroot mit aktivem venv ausführen (./md2pdf_run.py ...)."""
import os
import sys

# Projektroot sicherstellen, damit das Paket "md2pdf" gefunden wird
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
# Start-CWD für interaktiven Modus merken (vor chdir), damit .md im Aufrufverzeichnis gefunden werden
os.environ["MD2PDF_START_CWD"] = os.getcwd()
os.chdir(_root)

from md2pdf.cli.main import app

if __name__ == "__main__":
    app()
