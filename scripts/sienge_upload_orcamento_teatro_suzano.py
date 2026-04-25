"""
Upload do orçamento do Teatro Suzano para o Sienge via API.

Estrutura:
  level 1 → OBRA GERAL (id=3, mantém)
  level 2 → 11 seções do Excel (Serviços Preliminares, Demolições, etc.)
  level 3 → 175 itens detalhados sob cada seção

Executa em loop até o lock de sessão liberar.
Notifica via Telegram ao concluir.
"""

from __future__ import annotations

import json
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

XLSX_PATH = Path("/root/.openclaw/media/inbound/TEATRO_SUZANO_-_Orçamento_SIENGE---a578199b-c08f-4e47-8b28-4fa262e595bc.xlsx")
CONFIG_PATH = Path("/root/.openclaw/workspace/config/sienge-pcs.json")
OPENCLAW_CONFIG_PATH = Path("/root/.openclaw/openclaw.json")
BUILDING_ID = 1354
SHEET_UNIT_ID = 1
TELEGRAM_CHAT_ID = "1067279351"


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
        item_col = row[1]
        ref_col = row[2]
        desc_col = row[4]
        unit_col = row[5]
        qty = row[6]
        price_bdi = row[8]

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


def build_payload(items: list[ExcelItem]) -> list[dict]:
    """
    Monta payload hierárquico:
      level 1 → OBRA GERAL (id=3)
      level 2 → seção do Excel
      level 3 → item detalhado
    A API Sienge infere parentesco pela sequência + campo level.
    Não existe campo parentItemId.
    """
    by_section: dict[str, list[ExcelItem]] = defaultdict(list)
    section_order: list[str] = []
    for it in items:
        if it.section not in by_section:
            section_order.append(it.section)
        by_section[it.section].append(it)

    payload: list[dict] = [
        {"id": "3", "description": "OBRA GERAL", "workItemId": None, "quantity": None, "level": 1},
    ]

    for section in section_order:
        payload.append({
            "description": section,
            "workItemId": None,
            "quantity": None,
            "level": 2,
        })
        for it in by_section[section]:
            payload.append({
                "description": f"[{it.item}] {it.description}",
                "workItemId": None,
                "quantity": it.quantity,
                "level": 3,
            })

    return payload


def _auth(cfg: dict) -> str:
    return "Basic " + base64.b64encode(f"{cfg['username']}:{cfg['password']}".encode()).decode()


def _tg_token() -> str:
    try:
        d = json.loads(OPENCLAW_CONFIG_PATH.read_text())
        return d["channels"]["telegram"]["botToken"]
    except Exception:
        return ""


def send_telegram(text: str):
    token = _tg_token()
    if not token:
        return
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def try_upload(cfg: dict, payload: list) -> tuple[int, str]:
    base = f"https://api.sienge.com.br/{cfg['subdomain']}/public/api/v1"
    url = f"{base}/building-cost-estimations/{BUILDING_ID}/sheets/{SHEET_UNIT_ID}/items"
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": _auth(cfg),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def print_summary(items: list[ExcelItem]):
    by_sec: dict[str, float] = defaultdict(float)
    for it in items:
        by_sec[it.section] += it.total
    print("\n📋 Orçamento enviado:")
    for sec, total in by_sec.items():
        print(f"   {sec}: R${total:,.2f}")
    print(f"   {'─'*55}")
    print(f"   TOTAL GERAL: R${sum(by_sec.values()):,.2f}")


def main():
    cfg = json.loads(CONFIG_PATH.read_text())

    print("📊 Parseando Excel...")
    items = parse_excel(XLSX_PATH)
    total_geral = sum(i.total for i in items)
    sections = list(dict.fromkeys(i.section for i in items))
    print(f"   {len(items)} itens · {len(sections)} seções · Total R${total_geral:,.2f}")
    print(f"   Seções: {', '.join(sections)}")

    payload = build_payload(items)
    print(f"\n📦 Payload: {len(payload)} entradas (1 raiz + {len(sections)} seções + {len(items)} itens)")
    print("   Estrutura: OBRA GERAL (L1) → seção (L2) → item detalhado (L3)")

    max_attempts = 60  # até 5h de espera (5min cada)
    for attempt in range(1, max_attempts + 1):
        print(f"\n[{attempt}/{max_attempts}] Tentando upload... ", end="", flush=True)
        status, body = try_upload(cfg, payload)

        if status == 422 and "alocada" in body:
            print("⏳ Lock ativo (PHILIPPE.SANTOS) — aguardando 5 min...")
            time.sleep(300)
            continue

        if status in (200, 201, 204):
            print(f"✅ SUCESSO ({status})")
            print_summary(items)
            send_telegram(
                f"✅ <b>Teatro Suzano — Orçamento importado no Sienge</b>\n\n"
                f"🏗 <b>{len(sections)} seções</b> + <b>{len(items)} itens</b>\n"
                f"💰 <b>Total: R${total_geral:,.2f}</b>\n\n"
                f"Estrutura: L1 OBRA GERAL → L2 seção → L3 item\n"
                f"buildingId {BUILDING_ID} · planilha {SHEET_UNIT_ID}"
            )
            return

        if status == 429:
            print(f"⚠️ Rate limit (429) — aguardando 10 min...")
            time.sleep(600)
            continue

        if status == 400:
            print(f"❌ Erro 400: {body[:400]}")
            send_telegram(f"❌ <b>Teatro Suzano Sienge</b> — Erro 400\n<code>{body[:300]}</code>")
            return

        print(f"❌ Erro inesperado ({status}): {body[:200]}")
        send_telegram(f"❌ <b>Teatro Suzano Sienge</b> — Erro {status}\n<code>{body[:200]}</code>")
        return

    msg = f"⚠️ Lock não liberou após {max_attempts} tentativas (5h). Pedir para Philippe fechar a planilha no Sienge."
    print(f"\n{msg}")
    send_telegram(f"⚠️ <b>Teatro Suzano Sienge</b>\n{msg}")


if __name__ == "__main__":
    main()
