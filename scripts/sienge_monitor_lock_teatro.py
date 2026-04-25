"""
Monitor de lock do orçamento Teatro Suzano no Sienge.
Tenta upload a cada 5 minutos. Notifica Telegram quando concluir.
"""

from __future__ import annotations

import json
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass


XLSX_PATH = Path("/root/.openclaw/media/inbound/TEATRO_SUZANO_-_Orçamento_SIENGE---a578199b-c08f-4e47-8b28-4fa262e595bc.xlsx")
CONFIG_PATH = Path("/root/.openclaw/workspace/config/sienge-pcs.json")
BUILDING_ID = 1354
SHEET_UNIT_ID = 1

OPENCLAW_CONFIG_PATH = Path("/root/.openclaw/openclaw.json")
TELEGRAM_CHAT_ID = "1067279351"  # Alexandre DM


def _get_tg_token() -> str:
    try:
        d = json.loads(OPENCLAW_CONFIG_PATH.read_text())
        return d["channels"]["telegram"]["botToken"]
    except Exception:
        return ""


@dataclass
class ExcelItem:
    item: str
    section: str
    description: str
    unit: str | None
    quantity: float
    unit_price_bdi: float
    total: float
    is_nao_incidente: bool


def parse_excel(path: Path) -> list[ExcelItem]:
    import openpyxl
    wb = openpyxl.load_workbook(str(path))
    ws = wb["Orçamento"]
    items: list[ExcelItem] = []
    current_section = ""
    is_nao_incidente = False

    for row in ws.iter_rows(min_row=5, values_only=True):
        item_col, ref_col, _, desc_col, unit_col = row[1], row[2], row[3], row[4], row[5]
        qty, price_bdi = row[6], row[8]

        if isinstance(item_col, int) and isinstance(ref_col, str) and not row[3] and not desc_col:
            current_section = ref_col
            if "NÃO INCIDENTE" in ref_col:
                is_nao_incidente = True
            continue

        if not item_col or item_col in ("ITEM", "Aditivo", "ADITIVO"):
            continue
        if not isinstance(qty, (int, float)) or not isinstance(price_bdi, (int, float)):
            continue
        if qty == 0 and price_bdi == 0:
            continue

        items.append(ExcelItem(
            item=str(item_col),
            section=current_section,
            description=str(desc_col)[:200] if desc_col else "",
            unit=str(unit_col) if unit_col else None,
            quantity=float(qty),
            unit_price_bdi=float(price_bdi),
            total=float(qty) * float(price_bdi),
            is_nao_incidente=is_nao_incidente,
        ))
    return items


def _auth(cfg: dict) -> str:
    return "Basic " + base64.b64encode(f"{cfg['username']}:{cfg['password']}".encode()).decode()


def try_upload(cfg: dict, payload: list) -> tuple[int, str]:
    import requests
    base = f"https://api.sienge.com.br/{cfg['subdomain']}/public/api/v1"
    r = requests.put(
        f"{base}/building-cost-estimations/{BUILDING_ID}/sheets/{SHEET_UNIT_ID}/items",
        auth=(cfg["username"], cfg["password"]),
        json=payload,
        timeout=30,
    )
    return r.status_code, r.text


def send_telegram(token: str, chat_id: str, text: str):
    import requests
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )


def build_payload(items: list[ExcelItem]) -> list[dict]:
    return [
        {
            "description": f"[{it.item}] {it.description}",
            "workItemId": None,
            "quantity": it.quantity,
            "level": 2,
        }
        for it in items
    ]


def main():
    cfg = json.loads(CONFIG_PATH.read_text())

    tg_token = _get_tg_token()

    print("📊 Parseando Excel...")
    items = parse_excel(XLSX_PATH)
    total_geral = sum(i.total for i in items)
    print(f"   {len(items)} itens · Total R${total_geral:,.2f}")

    payload = build_payload(items)

    attempt = 0
    while True:
        attempt += 1
        print(f"\n[{attempt}] Tentando upload... ", end="", flush=True)
        try:
            status, body = try_upload(cfg, payload)
        except Exception as e:
            print(f"ERRO: {e}")
            time.sleep(300)
            continue

        if status == 422 and "alocada" in body:
            print("⏳ Lock ativo (PHILIPPE.SANTOS) — próxima tentativa em 5 min")
            time.sleep(300)
            continue

        if status in (200, 201, 204):
            print(f"✅ SUCESSO ({status})")
            msg = (
                f"✅ <b>Teatro Suzano — Orçamento enviado ao Sienge</b>\n\n"
                f"📊 <b>{len(items)} itens</b> importados com sucesso\n"
                f"💰 <b>Total: R${total_geral:,.2f}</b>\n\n"
                f"Nível 2 · buildingId {BUILDING_ID} · planilha {SHEET_UNIT_ID}"
            )
            if tg_token:
                send_telegram(tg_token, TELEGRAM_CHAT_ID, msg)
            print(msg)
            return

        if status == 400:
            # Tenta com workItemId genérico como fallback
            print(f"400 — tentando fallback com workItemId=80002...")
            for entry in payload:
                entry["workItemId"] = 80002
            continue

        print(f"❌ Erro inesperado ({status}): {body[:200]}")
        if tg_token:
            send_telegram(tg_token, TELEGRAM_CHAT_ID,
                f"❌ <b>Teatro Suzano Sienge</b> — Erro {status} no upload.\n<code>{body[:200]}</code>")
        return


if __name__ == "__main__":
    main()
