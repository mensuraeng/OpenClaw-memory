#!/usr/bin/env python3
"""
Upload orçamento Teatro Suzano → Sienge
Formato específico: TEATRO SUZANO - Orçamento SIENGE.xlsx

Suporta checkpoint/resume: salva progresso em /tmp/teatro_upload_checkpoint.json
Limite diário: 100 req/dia (reset ~21:00 BRT = 00:00 UTC)
176 itens no total — precisa de 2 execuções diárias para completar.
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
from pcs_sienge.endpoints.budget import create_resource

try:
    import openpyxl
except ImportError:
    sys.exit("pip3 install openpyxl --break-system-packages")

XLSX_PATH = "/tmp/teatro_suzano.xlsx"
BUILDING_ID = 1354
PUBLIC_CONFIG = "/root/.openclaw/workspace/config/sienge-pcs-public.json"
CHECKPOINT_FILE = "/tmp/teatro_upload_checkpoint.json"
RESULT_FILE = "/tmp/teatro_upload_result.json"
BATCH_LIMIT = 90  # conservative — leave buffer for retries within daily limit


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
    for row in rows[4:]:  # skip header rows 1-4
        desc  = row[4] if len(row) > 4 else None
        unid  = row[5] if len(row) > 5 else None
        qtd   = row[6] if len(row) > 6 else None
        v_bdi = row[8] if len(row) > 8 else None
        total = row[9] if len(row) > 9 else None

        if not desc or v_bdi is None:
            continue

        qtd_f  = parse_float(qtd) or 1.0
        unid   = unid or "UN"
        vbdi_f = parse_float(v_bdi)
        if not vbdi_f:
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


def load_checkpoint() -> dict:
    cp = Path(CHECKPOINT_FILE)
    if cp.exists():
        try:
            return json.loads(cp.read_text())
        except Exception:
            pass
    return {"sent_indices": [], "ok": 0, "errors": [], "complete": False}


def save_checkpoint(cp: dict) -> None:
    Path(CHECKPOINT_FILE).write_text(json.dumps(cp, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file", default=XLSX_PATH)
    parser.add_argument("--building-id", type=int, default=BUILDING_ID)
    parser.add_argument("--config", default=PUBLIC_CONFIG)
    parser.add_argument("--batch-limit", type=int, default=BATCH_LIMIT)
    parser.add_argument("--reset-checkpoint", action="store_true", help="Apaga checkpoint e reinicia do zero")
    args = parser.parse_args()

    if args.reset_checkpoint and Path(CHECKPOINT_FILE).exists():
        Path(CHECKPOINT_FILE).unlink()
        print("Checkpoint resetado.")

    print(f"\n{'='*65}")
    print(f"Upload orçamento → Sienge | Obra {args.building_id} | Teatro Suzano")
    print(f"Modo: {'DRY-RUN' if args.dry_run else 'REAL'} | Config: {args.config}")
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

    # Load checkpoint
    cp = load_checkpoint()
    if cp.get("complete"):
        print("Upload já completo (checkpoint marcado como concluído). Use --reset-checkpoint para refazer.")
        return

    sent_set = set(cp.get("sent_indices", []))
    pending = [(idx, item) for idx, item in enumerate(items) if idx not in sent_set]

    if not pending:
        cp["complete"] = True
        save_checkpoint(cp)
        print("Todos os itens já foram enviados (checkpoint). Upload completo.")
        return

    print(f"2. Retomando upload | {len(sent_set)} já enviados | {len(pending)} pendentes")
    print(f"   Limite desta execução: {args.batch_limit} itens\n")

    cfg = SiengeConfig.from_file(args.config)
    client = SiengeClient(cfg)

    batch = pending[:args.batch_limit]
    ok_this_run = 0
    errors_this_run = []

    print(f"3. Enviando {len(batch)} itens (índices {batch[0][0]}..{batch[-1][0]})...\n")
    for i, (idx, item) in enumerate(batch, 1):
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
            cp["sent_indices"].append(idx)
            cp["ok"] = cp.get("ok", 0) + 1
            ok_this_run += 1
        except SiengeApiError as e:
            err = {"idx": idx, "item": item["descricao"][:50], "error": str(e)[:100]}
            cp.setdefault("errors", []).append(err)
            errors_this_run.append(err)
        except Exception as e:
            err = {"idx": idx, "item": item["descricao"][:50], "error": str(e)[:100]}
            cp.setdefault("errors", []).append(err)
            errors_this_run.append(err)

        # Save checkpoint every 10 items
        if i % 10 == 0:
            save_checkpoint(cp)
            print(f"   {i}/{len(batch)} | OK esta execução: {ok_this_run} | Erros: {len(errors_this_run)}")

        time.sleep(0.35)

    # Final checkpoint save
    total_sent = len(cp["sent_indices"])
    remaining_after = len(items) - total_sent
    if remaining_after == 0:
        cp["complete"] = True
    save_checkpoint(cp)

    print(f"\n{'='*65}")
    print(f"Esta execução: {ok_this_run} enviados | {len(errors_this_run)} erros")
    print(f"Total acumulado: {total_sent}/{len(items)} itens")
    print(f"Restam: {remaining_after} itens para próxima execução")
    print(f"{'='*65}\n")

    if errors_this_run:
        print(f"ERROS ({len(errors_this_run)}):")
        for e in errors_this_run[:10]:
            print(f"  - [{e['idx']}] {e['item']}: {e['error']}")

    result = {
        "ok_this_run": ok_this_run,
        "errors_this_run": len(errors_this_run),
        "total_sent": total_sent,
        "total_items": len(items),
        "remaining": remaining_after,
        "total_orcado": total_orcado,
        "complete": cp.get("complete", False),
        "error_detail": errors_this_run,
    }
    with open(RESULT_FILE, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Log salvo em {RESULT_FILE}")

    if cp.get("complete"):
        print("\nUPLOAD COMPLETO.")


if __name__ == "__main__":
    main()
