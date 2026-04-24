#!/usr/bin/env python3
"""
Upload orçamento Teatro Suzano → Sienge
Formato específico: TEATRO SUZANO - Orçamento SIENGE.xlsx
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pcs_sienge.config import SiengeConfig
from pcs_sienge.client import SiengeClient, SiengeApiError
from pcs_sienge.endpoints.budget import get_resources, create_resource

try:
    import openpyxl
except ImportError:
    sys.exit("pip3 install openpyxl --break-system-packages")

XLSX_PATH = "/tmp/teatro_suzano.xlsx"
BUILDING_ID = 1354


def parse_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def read_excel(path: str) -> list[dict]:
    """
    Colunas (0-indexed raw):
    0=_  1=ITEM  2=REF  3=CÓDIGO  4=DESCRIÇÃO  5=UNID  6=QUANT  7=V.UNIT  8=V.UNIT+BDI  9=TOTAL
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    items = []
    for row in rows[4:]:  # pula cabeçalho nas linhas 1-4
        desc  = row[4] if len(row) > 4 else None
        unid  = row[5] if len(row) > 5 else None
        qtd   = row[6] if len(row) > 6 else None
        v_bdi = row[8] if len(row) > 8 else None
        total = row[9] if len(row) > 9 else None

        # Só itens com descrição + unidade + quantidade + preço
        if not desc or not unid or qtd is None or v_bdi is None:
            continue

        qtd_f  = parse_float(qtd)
        vbdi_f = parse_float(v_bdi)
        if not qtd_f or not vbdi_f:
            continue

        total_f = parse_float(total) or round(qtd_f * vbdi_f, 2)

        items.append({
            "item":       str(row[1]).strip() if row[1] else "",
            "ref":        str(row[2]).strip() if row[2] else "",
            "codigo":     str(row[3]).strip() if row[3] else "",
            "descricao":  str(desc).strip(),
            "unidade":    str(unid).strip(),
            "quantidade": qtd_f,
            "custo_unit": vbdi_f,
            "custo_total": total_f,
        })

    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file", default=XLSX_PATH)
    parser.add_argument("--building-id", type=int, default=BUILDING_ID)
    args = parser.parse_args()

    print(f"\n{'='*65}")
    print(f"Upload orçamento → Sienge | Obra {args.building_id} | Teatro Suzano")
    print(f"Modo: {'DRY-RUN' if args.dry_run else 'REAL'}")
    print(f"{'='*65}\n")

    print("1. Lendo Excel...")
    items = read_excel(args.file)
    total_orcado = sum(i["custo_total"] for i in items)
    print(f"   {len(items)} itens | Total orçado: R$ {total_orcado:,.2f}\n")

    if args.dry_run:
        print(f"   {'Item':<8} {'Ref':<10} {'Código':<12} {'Descrição':<42} {'Un':<8} {'Qtd':>8} {'V+BDI':>10} {'Total':>12}")
        print(f"   {'-'*112}")
        for i in items:
            print(f"   {i['item']:<8} {i['ref']:<10} {i['codigo']:<12} {i['descricao'][:41]:<42} "
                  f"{i['unidade']:<8} {i['quantidade']:>8.3f} {i['custo_unit']:>10.2f} {i['custo_total']:>12.2f}")
        print(f"\n   TOTAL: R$ {total_orcado:,.2f} | {len(items)} itens")
        json.dump(items, open("/tmp/teatro_budget_preview.json", "w"), ensure_ascii=False, indent=2)
        print("   Preview em /tmp/teatro_budget_preview.json")
        return

    cfg = SiengeConfig.from_file()
    client = SiengeClient(cfg)

    print("2. Verificando itens existentes no Sienge...")
    existing = get_resources(client, args.building_id)
    existing_count = existing.raw.get("resultSetMetadata", {}).get("count", 0) if isinstance(existing.raw, dict) else 0
    print(f"   {existing_count} itens já existem na obra {args.building_id}\n")

    print(f"3. Enviando {len(items)} itens...\n")
    ok = 0
    errors = []
    for i, item in enumerate(items, 1):
        payload = {
            "description": item["descricao"],
            "unitId":      item["unidade"],
            "quantity":    item["quantidade"],
            "unitCost":    item["custo_unit"],
        }
        if item["codigo"]:
            payload["auxiliaryCode"] = item["codigo"]

        try:
            create_resource(client, args.building_id, payload)
            ok += 1
        except SiengeApiError as e:
            errors.append({"item": item["descricao"][:50], "error": str(e)[:80]})
        except Exception as e:
            errors.append({"item": item["descricao"][:50], "error": str(e)[:80]})

        if i % 20 == 0 or i == len(items):
            print(f"   {i}/{len(items)} | OK: {ok} | Erros: {len(errors)}")

        time.sleep(0.35)  # ~170 req/min — dentro do limite de 200/min

    print(f"\n{'='*65}")
    print(f"CONCLUÍDO: {ok}/{len(items)} itens enviados")
    print(f"Total orçado carregado: R$ {total_orcado:,.2f}")
    if errors:
        print(f"\nERROS ({len(errors)}):")
        for e in errors[:15]:
            print(f"  - {e['item']}: {e['error']}")
    print(f"{'='*65}\n")

    # Save result log
    result = {"ok": ok, "errors": len(errors), "total": len(items),
              "total_orcado": total_orcado, "error_detail": errors}
    with open("/tmp/teatro_upload_result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Log salvo em /tmp/teatro_upload_result.json")


if __name__ == "__main__":
    main()
