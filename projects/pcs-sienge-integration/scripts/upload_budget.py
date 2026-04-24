#!/usr/bin/env python3
"""
Upload orçamento Teatro Suzano → Sienge (building-cost-estimations)

Uso:
    python3 upload_budget.py --file /tmp/teatro_suzano.xlsx [--dry-run] [--building-id 1354]

Fluxo:
    1. Lê o Excel e normaliza as linhas
    2. Consulta planilhas existentes da obra no Sienge
    3. Para cada linha: cria ou atualiza recurso no orçamento
    4. Imprime relatório final

Formato esperado do Excel (colunas flexíveis — detectadas por nome):
    Código | Descrição | Unidade | Quantidade | Custo Unitário | Custo Total
    (aceita variações de capitalização e espaço)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcs_sienge.config import SiengeConfig
from pcs_sienge.client import SiengeClient
from pcs_sienge.endpoints.budget import get_sheets, get_resources, create_resource

try:
    import openpyxl
except ImportError:
    sys.exit("Instale openpyxl: pip3 install openpyxl --break-system-packages")


# ---------------------------------------------------------------------------
# Column name aliases (normalizado → campo interno)
# ---------------------------------------------------------------------------
COL_ALIASES = {
    "codigo":       ["codigo", "code", "cód", "cod", "item"],
    "descricao":    ["descricao", "descrição", "description", "desc", "nome", "name", "servico", "serviço"],
    "unidade":      ["unidade", "un", "unit", "und"],
    "quantidade":   ["quantidade", "qtd", "qty", "quant", "qtde"],
    "custo_unit":   ["custo unitário", "custo unitario", "unit cost", "preco unitario", "preço unitário", "vl unit", "valor unit"],
    "custo_total":  ["custo total", "total", "valor total", "vl total"],
}


def normalize(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s.lower().strip()).encode("ascii", "ignore").decode()


def detect_columns(headers: list[str]) -> dict[str, int]:
    """Mapeia nome de campo interno → índice da coluna."""
    norm_headers = [normalize(h) for h in headers]
    mapping = {}
    for field, aliases in COL_ALIASES.items():
        for alias in aliases:
            try:
                idx = norm_headers.index(normalize(alias))
                mapping[field] = idx
                break
            except ValueError:
                continue
    return mapping


def parse_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace("R$", "").replace(".", "").replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def read_excel(path: str) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    # Detect header row (first row with at least 3 non-empty cells that look like headers)
    header_idx = 0
    col_map = {}
    for i, row in enumerate(rows[:10]):
        non_empty = [str(c) for c in row if c is not None and str(c).strip()]
        if len(non_empty) >= 3:
            candidate = detect_columns([str(c) if c is not None else "" for c in row])
            if len(candidate) >= 3:
                header_idx = i
                col_map = candidate
                break

    if not col_map:
        raise ValueError(
            "Não foi possível detectar cabeçalho. Colunas esperadas: "
            "Código, Descrição, Unidade, Quantidade, Custo Unitário"
        )

    print(f"  Cabeçalho na linha {header_idx + 1}: {col_map}")

    items = []
    for row in rows[header_idx + 1:]:
        if all(c is None for c in row):
            continue
        cells = list(row)

        descricao = cells[col_map["descricao"]] if "descricao" in col_map else None
        if not descricao or str(descricao).strip() == "":
            continue

        item = {
            "codigo":      str(cells[col_map["codigo"]]).strip() if "codigo" in col_map and cells[col_map["codigo"]] else "",
            "descricao":   str(descricao).strip(),
            "unidade":     str(cells[col_map["unidade"]]).strip() if "unidade" in col_map and cells[col_map["unidade"]] else "un",
            "quantidade":  parse_float(cells[col_map["quantidade"]]) if "quantidade" in col_map else None,
            "custo_unit":  parse_float(cells[col_map["custo_unit"]]) if "custo_unit" in col_map else None,
            "custo_total": parse_float(cells[col_map["custo_total"]]) if "custo_total" in col_map else None,
        }

        # Derive missing value
        if item["quantidade"] and item["custo_unit"] and not item["custo_total"]:
            item["custo_total"] = round(item["quantidade"] * item["custo_unit"], 2)
        if item["custo_total"] and item["quantidade"] and not item["custo_unit"]:
            item["custo_unit"] = round(item["custo_total"] / item["quantidade"], 6)

        if item["quantidade"] and (item["custo_unit"] or item["custo_total"]):
            items.append(item)

    return items


def build_sienge_payload(item: dict, sheet_id: int) -> dict:
    """Converte linha do Excel para payload da API Sienge."""
    payload = {
        "sheetId": sheet_id,
        "description": item["descricao"],
        "unitId": item["unidade"],
        "quantity": item["quantidade"],
    }
    if item.get("codigo"):
        payload["code"] = item["codigo"]
    if item.get("custo_unit") is not None:
        payload["unitCost"] = item["custo_unit"]
    return payload


def main():
    parser = argparse.ArgumentParser(description="Upload orçamento Teatro Suzano → Sienge")
    parser.add_argument("--file", required=True, help="Caminho do .xlsx")
    parser.add_argument("--building-id", type=int, default=1354, help="ID da obra no Sienge (padrão: 1354)")
    parser.add_argument("--sheet-id", type=int, default=None, help="ID da planilha de orçamento (usa a 1ª se omitido)")
    parser.add_argument("--dry-run", action="store_true", help="Não faz POST, só mostra o que faria")
    parser.add_argument("--config", default=None, help="Caminho do sienge-pcs.json")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"Upload orçamento → Sienge")
    print(f"Obra: {args.building_id} | Arquivo: {args.file}")
    print(f"Modo: {'DRY-RUN' if args.dry_run else 'REAL'}")
    print(f"{'='*60}\n")

    # --- 1. Parse Excel ---
    print("1. Lendo Excel...")
    items = read_excel(args.file)
    print(f"   {len(items)} itens válidos encontrados")
    if not items:
        sys.exit("Nenhum item encontrado. Verifique o formato do arquivo.")

    total_orcado = sum(i["custo_total"] or 0 for i in items)
    print(f"   Total orçado: R$ {total_orcado:,.2f}\n")

    # --- 2. Conectar Sienge ---
    cfg = SiengeConfig.from_file(args.config)
    client = SiengeClient(cfg)

    if not args.dry_run:
        # --- 3. Obter planilha ---
        print("2. Consultando planilhas da obra no Sienge...")
        sheets_result = get_sheets(client, args.building_id)
        sheets = sheets_result.items if sheets_result.items else (sheets_result.raw if isinstance(sheets_result.raw, list) else [])

        if not sheets:
            print(f"   Nenhuma planilha encontrada para obra {args.building_id}.")
            print("   Crie uma planilha de orçamento no Sienge primeiro.")
            sys.exit(1)

        sheet_id = args.sheet_id or sheets[0].get("id") or sheets[0].get("sheetId")
        print(f"   Usando planilha ID: {sheet_id}")
        print(f"   Planilhas disponíveis: {[s.get('id') or s.get('sheetId') for s in sheets[:5]]}\n")

        # --- 4. Upload linha a linha ---
        print("3. Enviando itens para o Sienge...")
        ok = 0
        errors = []
        for i, item in enumerate(items, 1):
            payload = build_sienge_payload(item, sheet_id)
            try:
                result = create_resource(client, args.building_id, payload)
                ok += 1
                if i % 10 == 0 or i == len(items):
                    print(f"   {i}/{len(items)} enviados ({ok} OK, {len(errors)} erros)")
            except Exception as e:
                errors.append({"item": item["descricao"][:40], "error": str(e)[:80]})

        print(f"\n{'='*60}")
        print(f"RESULTADO: {ok}/{len(items)} itens enviados com sucesso")
        if errors:
            print(f"ERROS ({len(errors)}):")
            for err in errors[:10]:
                print(f"  - {err['item']}: {err['error']}")
        print(f"{'='*60}\n")

    else:
        # Dry-run: mostra as primeiras 20 linhas
        print("2. [DRY-RUN] Prévia dos primeiros 20 itens:\n")
        print(f"  {'#':<4} {'Código':<12} {'Descrição':<40} {'Un':<5} {'Qtd':>8} {'Custo Unit':>12} {'Total':>12}")
        print(f"  {'-'*95}")
        for i, item in enumerate(items[:20], 1):
            print(f"  {i:<4} {item['codigo']:<12} {item['descricao'][:39]:<40} {item['unidade']:<5} "
                  f"{(item['quantidade'] or 0):>8.2f} {(item['custo_unit'] or 0):>12.2f} {(item['custo_total'] or 0):>12.2f}")
        if len(items) > 20:
            print(f"  ... e mais {len(items) - 20} itens")
        print(f"\n  Total orçado: R$ {total_orcado:,.2f}")
        print(f"\n  Para executar de verdade: remova --dry-run\n")

        # Salvar JSON de preview
        out_path = "/tmp/teatro_suzano_budget_preview.json"
        with open(out_path, "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"  Preview salvo em: {out_path}")


if __name__ == "__main__":
    main()
