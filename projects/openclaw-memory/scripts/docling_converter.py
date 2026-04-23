#!/usr/bin/env python3
"""
Docling Batch Converter
Converte PDF, DOCX, PPTX, XLSX → Markdown
Uso: python3 docling_converter.py [pasta_entrada] [pasta_saida]
"""

import sys
import os
from pathlib import Path
from docling.document_converter import DocumentConverter

SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".txt"}

def convert_all(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = [f for f in input_path.rglob("*") if f.suffix.lower() in SUPPORTED]

    if not files:
        print(f"Nenhum arquivo suportado encontrado em: {input_dir}")
        return

    print(f"Encontrados {len(files)} arquivo(s). Iniciando conversão...\n")
    converter = DocumentConverter()

    for file in files:
        rel = file.relative_to(input_path)
        out_file = output_path / rel.with_suffix(".md")
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = converter.convert(str(file))
            md = result.document.export_to_markdown()
            out_file.write_text(md, encoding="utf-8")
            print(f"  ✅ {rel} → {out_file.name} ({len(md):,} chars)")
        except Exception as e:
            print(f"  ❌ {rel} — erro: {e}")

    print(f"\nConcluído. Arquivos salvos em: {output_path}")

if __name__ == "__main__":
    input_dir  = sys.argv[1] if len(sys.argv) > 1 else "/root/.openclaw/workspace/referencias"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/root/.openclaw/workspace/docling-output"
    convert_all(input_dir, output_dir)
