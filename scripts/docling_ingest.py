#!/usr/bin/env python3
"""
Docling Ingest — converte docs novos para o RAG automaticamente
Monitora /workspace/docs/ e converte tudo que ainda não tem .md em /workspace/docling-output/

Uso:
  python3 docling_ingest.py           # processa novos arquivos
  python3 docling_ingest.py --force   # reprocessa tudo
"""

import sys
import os
from pathlib import Path
from docling.document_converter import DocumentConverter

DOCS_DIR   = Path("/root/.openclaw/workspace/docs")
OUTPUT_DIR = Path("/root/.openclaw/workspace/docling-output")
SUPPORTED  = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".txt"}

def ingest(force: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in DOCS_DIR.rglob("*") if f.suffix.lower() in SUPPORTED]

    if not files:
        print("Nenhum arquivo encontrado em docs/")
        return

    converter = None
    processed = 0
    skipped   = 0

    for file in files:
        rel      = file.relative_to(DOCS_DIR)
        out_file = OUTPUT_DIR / rel.with_suffix(".md")

        if out_file.exists() and not force:
            skipped += 1
            continue

        if converter is None:
            converter = DocumentConverter()

        out_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = converter.convert(str(file))
            md     = result.document.export_to_markdown()
            out_file.write_text(md, encoding="utf-8")
            print(f"  ✅ {rel} → {out_file.relative_to(OUTPUT_DIR)} ({len(md):,} chars)")
            processed += 1
        except Exception as e:
            print(f"  ❌ {rel} — erro: {e}")

    print(f"\nConcluído: {processed} convertidos, {skipped} já existiam (use --force para reprocessar).")

if __name__ == "__main__":
    force = "--force" in sys.argv
    ingest(force)
