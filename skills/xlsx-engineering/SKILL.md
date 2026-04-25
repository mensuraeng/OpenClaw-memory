---
name: xlsx-engineering
description: Use when creating, reading, editing, validating, cleaning, or converting Excel/CSV/TSV spreadsheets for engineering, construction control, budgets, measurements, EVM, procurement maps, cash flow, Sienge exports, or proposal comparisons. Trigger when the primary input or deliverable is .xlsx, .xlsm, .csv, or .tsv.
---

# XLSX Engineering

Use this skill for spreadsheet-first work in Mensura/MIA/PCS contexts: orçamento, medição, curva S, EVM, compras, concorrência de fornecedores, fluxo de caixa, Sienge exports, cronograma físico-financeiro and tabular cleanup.

## Operating rules

- Prefer `pandas` for bulk analysis/cleaning and `openpyxl` for Excel formulas, formatting, sheets, widths, colors, validations, and comments.
- Preserve existing workbook structure, formulas, names, sheets, formatting, and styles unless explicitly asked to redesign.
- For calculated deliverables, write Excel formulas whenever the workbook should remain updateable. Do not hardcode Python-calculated totals, percentages, deltas, or ratios when an Excel formula is the right artifact.
- After writing formulas, run `scripts/recalc_xlsx.py <file.xlsx>` to recalculate with LibreOffice and scan for formula errors.
- Do not claim an Excel file is ready until it opens/recalculates cleanly or you have named the blocker.

## Construction/business conventions

- Use clear sheet names: `Resumo`, `Base`, `Medição`, `Compras`, `Cronograma`, `EVM`, `Premissas`, `Fornecedores`.
- Keep assumptions in explicit cells/sheets and reference them in formulas.
- Mark user-editable inputs in blue font or light yellow fill when creating new workbooks.
- Use Brazilian formats when relevant: `R$ #.##0,00`, dates `dd/mm/aaaa`, percentages `0,0%`.
- Include source notes for hardcoded values when provenance matters: document, date, page/tab, system/export.
- For comparisons, include `responsável`, `prazo`, `condição comercial`, `risco`, and `próxima ação`, not only price.

## Minimal workflow

1. Inspect workbook/sheets and infer structure.
2. Make the smallest safe transformation.
3. Save to a new output file unless the user explicitly asked to overwrite.
4. Recalculate/validate:
   ```bash
   python3 skills/shared/xlsx-engineering/scripts/recalc_xlsx.py caminho/arquivo.xlsx
   ```
5. Report what changed and what was validated.
