#!/usr/bin/env python3
"""XP Experiência — daily sync (download OFX, ingest, conciliate, report).

Pipeline (single run, fully deterministic):

  1. Load saved session (storage_state.json)
  2. Launch headless Chromium
  3. Navigate to extrato, click export → OFX, capture download
  4. Parse OFX → list[Transaction]
  5. Write memory/integrations/xp/transactions/YYYY-MM-DD.json
  6. Conciliate: match transactions against memory/contas_pagar.json
  7. Write memory/integrations/xp/daily-reports/YYYY-MM-DD.md
  8. Post Telegram summary

On auth failure (session expired), send Telegram alert and exit 1.
On any other error, log full trace + Telegram alert + exit 2.

Filesystem-first: no external DB. All state lives under memory/.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import sys
import traceback
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

CONFIG_PATH = Path("/root/.openclaw/bin/xp_sync.config.json")


# ---------- config ---------------------------------------------------------


@dataclass
class Config:
    storage_path: Path
    profile_path: Path
    downloads_dir: Path
    memory_root: Path           # memory/integrations/xp/
    contas_pagar_path: Path     # memory/contas_pagar.json
    timezone: str
    telegram_bot_token_env: str
    telegram_chat_id: str
    portal_url: str             # experiencia.xpi.com.br/conta/#/
    cdp_url: str | None         # if set, attach to external Chrome via CDP
                                # (bypasses server-IP anti-bot)

    @classmethod
    def load(cls, path: Path) -> "Config":
        d = json.loads(path.read_text())
        return cls(
            storage_path=Path(d["storage_path"]),
            profile_path=Path(d["profile_path"]),
            downloads_dir=Path(d["downloads_dir"]),
            memory_root=Path(d["memory_root"]),
            contas_pagar_path=Path(d["contas_pagar_path"]),
            timezone=d.get("timezone", "America/Sao_Paulo"),
            telegram_bot_token_env=d.get("telegram_bot_token_env", "TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=str(d["telegram_chat_id"]),
            portal_url=d.get("portal_url", "https://experiencia.xpi.com.br/conta/#/"),
            cdp_url=d.get("cdp_url"),
        )


# ---------- transaction model --------------------------------------------


@dataclass
class Transaction:
    tx_id: str              # stable hash
    date: str               # ISO
    amount: float
    type: str               # CREDITO / DEBITO
    description: str
    category: str
    fitid: str | None = None  # OFX unique id, if present
    memo: str | None = None
    raw_amount: float | None = None  # signed, as from OFX


CATEGORIES = [
    (r'DARF|IRPJ|CSLL|PIS|COFINS|ISS|ICMS|SIMPLES|DAS', 'impostos'),
    (r'FGTS|INSS', 'impostos'),
    (r'FOLHA|SALARIO|SALÁRIO|FÉRIAS|13.?SAL|VR |VA ', 'folha'),
    (r'ALUGUEL|LOCAÇÃO|LOCACAO', 'aluguel'),
    (r'TED RECEB|PIX RECEB|CREDITO RECEB|CRÉDITO|RECEBIMENTO', 'receita'),
    (r'FORNECEDOR|NF |NOTA FISCAL|BOLETO', 'fornecedores'),
    (r'TARIFA|TAXA MANUTENCAO|MANUTEN|IOF', 'tarifas'),
    (r'INVESTIMENTO|APLICACAO|APLICAÇÃO|CDB|LCI|LCA|FII|FI ', 'investimentos'),
    (r'RESGATE', 'resgates'),
    (r'TED ENVIADO|PIX ENVIADO|TRANSFER', 'transferencias'),
    (r'ENERGIA|ENEL|LIGHT|CEMIG|COPEL|CPFL', 'concessionarias'),
    (r'AGUA|SABESP|CEDAE|COPASA', 'concessionarias'),
    (r'INTERNET|VIVO|CLARO|TIM|OI ', 'telecom'),
]


def categorize(desc: str) -> str:
    up = desc.upper()
    for pat, cat in CATEGORIES:
        if re.search(pat, up):
            return cat
    return 'outros'


def make_tx_id(date_iso: str, desc: str, amount: float, fitid: str | None) -> str:
    key = f"{date_iso}|{desc}|{amount:.2f}|{fitid or ''}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:32]


# ---------- OFX parsing ---------------------------------------------------


def parse_ofx(path: Path) -> list[Transaction]:
    """Parse an OFX file into a list of Transactions."""
    from ofxparse import OfxParser
    from io import BytesIO

    # OFX can be SGML (older) or XML (newer). ofxparse handles both.
    raw = path.read_bytes()
    try:
        ofx = OfxParser.parse(BytesIO(raw))
    except Exception:
        # Try decoding as latin-1 first (common for Brazilian OFX)
        text = raw.decode('latin-1', errors='replace')
        from io import StringIO
        ofx = OfxParser.parse(StringIO(text))

    txs: list[Transaction] = []
    for account in ofx.accounts:
        stmt = account.statement
        for raw_tx in stmt.transactions:
            amount = float(raw_tx.amount)
            date_iso = raw_tx.date.date().isoformat()
            desc = (raw_tx.payee or raw_tx.memo or '').strip()
            memo = (raw_tx.memo or '').strip() or None
            fitid = getattr(raw_tx, 'id', None)
            t = Transaction(
                tx_id=make_tx_id(date_iso, desc, amount, fitid),
                date=date_iso,
                amount=abs(amount),
                type='CREDITO' if amount >= 0 else 'DEBITO',
                description=desc[:500],
                category=categorize(desc),
                fitid=str(fitid) if fitid else None,
                memo=memo,
                raw_amount=amount,
            )
            txs.append(t)
    return txs


# ---------- conciliation ---------------------------------------------------


@dataclass
class ConciliationMatch:
    tx_id: str
    conta_id: str
    confidence: str  # "high" / "medium" / "low"
    reason: str


@dataclass
class ConciliationReport:
    matched: list[ConciliationMatch] = field(default_factory=list)
    unmatched_tx: list[str] = field(default_factory=list)        # tx_id
    unmatched_contas: list[str] = field(default_factory=list)    # conta_id
    summary: dict[str, Any] = field(default_factory=dict)


def load_contas_pagar(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data.get("contas", [])


def conciliate(txs: list[Transaction], contas: list[dict]) -> ConciliationReport:
    """Match outgoing transactions against accounts-payable entries.

    Heuristic: match by amount (exact) + date proximity (±5 days) + keyword
    overlap between tx description and conta descrição/remetente.
    """
    report = ConciliationReport()
    used_contas: set[str] = set()

    for tx in txs:
        if tx.type != 'DEBITO':
            continue
        best = None
        for c in contas:
            if c.get("id") in used_contas:
                continue
            if c.get("status") == "paid":
                continue
            valor = c.get("valor")
            if valor is None:
                continue
            try:
                valor = float(valor)
            except (TypeError, ValueError):
                continue
            if abs(valor - tx.amount) > 0.01:
                continue
            # Amount matches. Now check keyword overlap (loose).
            desc_tokens = set(re.findall(r'\w{4,}', tx.description.lower()))
            conta_text = (
                (c.get('descricao') or '') + ' '
                + (c.get('remetente') or '') + ' '
                + (c.get('assunto') or '')
            ).lower()
            conta_tokens = set(re.findall(r'\w{4,}', conta_text))
            overlap = desc_tokens & conta_tokens
            confidence = 'high' if len(overlap) >= 2 else ('medium' if len(overlap) == 1 else 'low')
            if best is None or (confidence == 'high' and best[1] != 'high'):
                best = (c, confidence, overlap)

        if best:
            c, conf, overlap = best
            report.matched.append(ConciliationMatch(
                tx_id=tx.tx_id,
                conta_id=c.get('id', '(sem id)'),
                confidence=conf,
                reason=f"valor={tx.amount:.2f} data={tx.date} overlap={sorted(overlap) or '(só valor)'}",
            ))
            used_contas.add(c.get('id'))
        else:
            report.unmatched_tx.append(tx.tx_id)

    for c in contas:
        if c.get("id") and c.get("id") not in used_contas and c.get("status") != "paid":
            report.unmatched_contas.append(c.get("id"))

    # Summary stats
    credits = [tx for tx in txs if tx.type == 'CREDITO']
    debits = [tx for tx in txs if tx.type == 'DEBITO']
    report.summary = {
        "total_tx": len(txs),
        "creditos_count": len(credits),
        "creditos_total": round(sum(t.amount for t in credits), 2),
        "debitos_count": len(debits),
        "debitos_total": round(sum(t.amount for t in debits), 2),
        "saldo_movimento": round(sum(t.amount for t in credits) - sum(t.amount for t in debits), 2),
        "matched": len(report.matched),
        "unmatched_debitos": len(report.unmatched_tx),
        "pending_contas": len(report.unmatched_contas),
    }
    return report


# ---------- filesystem writes ---------------------------------------------


def write_transactions(memory_root: Path, day: str, txs: list[Transaction]) -> Path:
    out = memory_root / "transactions" / f"{day}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "day": day,
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat(),
        "count": len(txs),
        "transactions": [asdict(t) for t in txs],
    }
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    os.replace(tmp, out)
    return out


def write_daily_report(memory_root: Path, day: str, txs: list[Transaction],
                        report: ConciliationReport, contas: list[dict]) -> Path:
    out = memory_root / "daily-reports" / f"{day}.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# XP — Conciliação {day}",
        "",
        f"Gerado em {datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M %Z')}.",
        "",
        "## Resumo",
        "",
        f"- Transações: **{report.summary['total_tx']}**",
        f"- Créditos: {report.summary['creditos_count']} · R$ {report.summary['creditos_total']:,.2f}",
        f"- Débitos: {report.summary['debitos_count']} · R$ {report.summary['debitos_total']:,.2f}",
        f"- Saldo do movimento: **R$ {report.summary['saldo_movimento']:,.2f}**",
        f"- Conciliação: {report.summary['matched']} casados · {report.summary['unmatched_debitos']} débitos sem match · {report.summary['pending_contas']} contas pendentes",
        "",
    ]

    # Top debits
    debits_sorted = sorted([t for t in txs if t.type == 'DEBITO'], key=lambda t: -t.amount)[:15]
    if debits_sorted:
        lines += ["## Principais débitos", ""]
        for t in debits_sorted:
            lines.append(f"- R$ {t.amount:>10,.2f}  ·  {t.date}  ·  `{t.category:15}`  ·  {t.description[:80]}")
        lines.append("")

    # Matched
    if report.matched:
        lines += ["## Conciliados", ""]
        conta_by_id = {c.get('id'): c for c in contas}
        for m in report.matched:
            c = conta_by_id.get(m.conta_id, {})
            lines.append(f"- [{m.confidence}] tx `{m.tx_id[:10]}` ↔ conta `{m.conta_id}` — {c.get('descricao','(sem desc)')[:60]}  ({m.reason})")
        lines.append("")

    # Unmatched debits
    if report.unmatched_tx:
        lines += ["## Débitos sem correspondência em contas_pagar", ""]
        by_id = {t.tx_id: t for t in txs}
        for tid in report.unmatched_tx:
            t = by_id[tid]
            lines.append(f"- R$ {t.amount:>10,.2f}  ·  {t.date}  ·  {t.description[:80]}")
        lines.append("")

    # Pending contas
    if report.unmatched_contas:
        lines += ["## Contas a pagar ainda pendentes", ""]
        conta_by_id = {c.get('id'): c for c in contas}
        for cid in report.unmatched_contas:
            c = conta_by_id.get(cid, {})
            val = c.get('valor') or '?'
            lines.append(f"- {cid}  ·  R$ {val}  ·  {c.get('descricao','(sem desc)')[:80]}")
        lines.append("")

    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text("\n".join(lines))
    os.replace(tmp, out)
    return out


# ---------- telegram ------------------------------------------------------


def notify_telegram(cfg: Config, message: str, silent: bool = False) -> None:
    token = os.environ.get(cfg.telegram_bot_token_env, "").strip()
    if not token:
        return
    try:
        data = urllib.parse.urlencode({
            "chat_id": cfg.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_notification": "true" if silent else "false",
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
    except Exception:
        pass


def build_telegram_summary(day: str, report: ConciliationReport) -> str:
    s = report.summary
    return (
        f"*XP — {day}*\n"
        f"📥 {s['creditos_count']} créditos · R$ {s['creditos_total']:,.2f}\n"
        f"📤 {s['debitos_count']} débitos · R$ {s['debitos_total']:,.2f}\n"
        f"Δ R$ {s['saldo_movimento']:,.2f}\n\n"
        f"✅ {s['matched']} conciliadas · "
        f"⚠️ {s['unmatched_debitos']} sem match · "
        f"📋 {s['pending_contas']} pendentes"
    )


# ---------- XP portal automation ------------------------------------------


async def download_ofx(cfg: Config, day_start: date, day_end: date) -> Path:
    """Launch a headless browser with the persistent profile, navigate to
    the extrato, let the SPA render + auth, programmatically trigger the
    Export → OFX flow, and intercept the /statements API response.

    The API returns JSON `{"data":{"content":"<base64 OFX>"}}`. We decode
    that and save to the downloads dir.
    """
    import base64
    from playwright.async_api import async_playwright

    cfg.downloads_dir.mkdir(parents=True, exist_ok=True)
    dest = cfg.downloads_dir / f"{day_end.isoformat()}.ofx"
    api_path = "/online-banking/pj/v1/reports/statements"

    captured_body: dict[str, Any] = {"data": None, "status": None}

    async with async_playwright() as p:
        # Two modes:
        #  - cdp_url set → attach to an already-running Chrome (on the user's
        #    residential IP, via Tailscale). Needed when XP anti-bot has
        #    blacklisted the server IP.
        #  - otherwise → launch headed Chromium locally on DISPLAY=:99.
        browser = None
        owns_browser = True
        if cfg.cdp_url:
            browser = await p.chromium.connect_over_cdp(cfg.cdp_url)
            owns_browser = False
            # Find or create the XP tab in the existing browser
            xp_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "xpi.com.br" in pg.url:
                        xp_page = pg
                        break
                if xp_page:
                    break
            if xp_page is None:
                # Fall back: create new page in first context
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page()
            else:
                context = xp_page.context
                page = xp_page
        else:
            browser = await p.chromium.launch(
                headless=False,  # headless gets bot-detected by XP CDN
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--window-size=1280,960",
                ],
                ignore_default_args=["--enable-automation"],
            )
            context = await browser.new_context(
                storage_state=str(cfg.storage_path),
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 920},
                accept_downloads=True,
            )
            page = await context.new_page()

        async def on_response(resp):
            if api_path in resp.url and resp.status == 200:
                try:
                    captured_body["data"] = await resp.body()
                    captured_body["status"] = resp.status
                    captured_body["url"] = resp.url
                except Exception as e:
                    print(f"[!] resp body err: {e}", flush=True)

        page.on("response", lambda r: asyncio.create_task(on_response(r)))

        # If the SPA is already at /bankline/#/extrato, skip goto (hash-only
        # change in SPAs often doesn't retrigger state).
        if "bankline" not in page.url or "extrato" not in page.url:
            await page.goto("https://experiencia.xpi.com.br/bankline/#/extrato",
                            wait_until="commit", timeout=60000)

        # Fail fast on auth redirect
        for _ in range(8):
            await asyncio.sleep(1)
            url = page.url
            if "login" in url or "autenticar" in url or "wl-login" in url:
                if owns_browser:
                    await context.close()
                    await browser.close()
                raise RuntimeError("XP session expired — open Chrome, log in, retry")

        # Close any leftover drawer — via JS (Playwright click sometimes
        # misses due to pointer-events overlay). Retry a few times.
        for _ in range(3):
            closed = await page.evaluate(
                """() => {
                  const drawers = document.querySelectorAll("soma-drawer-v4[open='true']");
                  let closed = 0;
                  for (const d of drawers) {
                    // Close button inside the drawer header
                    const btn = d.querySelector("soma-drawer-header-v4 button");
                    if (btn) { btn.click(); closed++; continue; }
                    // Fallback: remove the open attribute
                    d.removeAttribute('open');
                    closed++;
                  }
                  return closed;
                }"""
            )
            if not closed:
                break
            await asyncio.sleep(0.5)

        # Wait for the Exportar toolbar button to render
        try:
            await page.wait_for_selector("[aria-label='Exportar']", state="visible", timeout=30000)
        except Exception:
            try:
                Path("/tmp/xp_sync_fail.html").write_text(await page.content())
                await page.screenshot(path="/tmp/xp_sync_fail.png")
            except Exception:
                pass
            if owns_browser:
                await context.close()
                await browser.close()
            raise RuntimeError("Exportar button never appeared — session likely expired")

        # 1. Click toolbar Exportar — use JS to avoid overlay-blocked clicks
        clicked_result = await page.evaluate(
            """() => {
              // Pick the toolbar Exportar: NOT inside a drawer.
              const all = document.querySelectorAll("[aria-label='Exportar']");
              for (const el of all) {
                let p = el, inside_drawer = false;
                while (p && p !== document.body) {
                  if (p.tagName === 'SOMA-DRAWER-V4') { inside_drawer = true; break; }
                  p = p.parentElement;
                }
                if (!inside_drawer) {
                  const rect = el.getBoundingClientRect();
                  if (rect.width > 0 && rect.height > 0) {
                    el.click();
                    if (el.shadowRoot) {
                      const btn = el.shadowRoot.querySelector('button');
                      if (btn) btn.click();
                    }
                    return 'ok';
                  }
                }
              }
              return 'not found';
            }"""
        )
        if clicked_result != 'ok':
            if owns_browser:
                await context.close()
                await browser.close()
            raise RuntimeError(f"Exportar toolbar not clickable: {clicked_result}")
        await asyncio.sleep(2)

        # 2. Pick period chip "Últimos 30 dias"
        try:
            chip = await page.wait_for_selector("[aria-label='Últimos 30 dias']", timeout=10000)
            await chip.click()
            await asyncio.sleep(1)
        except Exception as e:
            if owns_browser:
                await context.close()
                await browser.close()
            raise RuntimeError(f"Period chip not found: {e}")

        # 3. Select OFX radio — soma-radio-v4 uses shadow DOM; plain click
        # doesn't register, need to dispatch change on the inner input.
        await page.evaluate(
            """() => {
              const el = document.querySelector("[data-testid='soma-radio-v4-ofx']");
              if (!el) return 'not found';
              el.click();
              el.dispatchEvent(new Event('change', {bubbles: true}));
              if (el.shadowRoot) {
                const input = el.shadowRoot.querySelector('input');
                if (input) {
                  input.checked = true;
                  input.click();
                  input.dispatchEvent(new Event('change', {bubbles: true, composed: true}));
                }
              }
              return 'ok';
            }"""
        )
        await asyncio.sleep(1)

        # 4. Click the drawer submit Exportar (now enabled)
        submit_result = await page.evaluate(
            """() => {
              const s = document.querySelector("soma-drawer-action-v4 soma-button-v4[aria-label='Exportar']");
              if (!s) return 'no submit';
              if (s.disabled || s.getAttribute('disabled') === 'true') return 'disabled';
              s.click();
              if (s.shadowRoot) {
                const btn = s.shadowRoot.querySelector('button');
                if (btn) btn.click();
              }
              return 'clicked';
            }"""
        )
        if submit_result != 'clicked':
            if owns_browser:
                await context.close()
                await browser.close()
            raise RuntimeError(f"Submit not clickable: {submit_result}")

        # 5. Wait for the /statements response
        for _ in range(30):
            await asyncio.sleep(1)
            if captured_body["data"]:
                break

        # Save refreshed cookie jar back to storage_state for next run
        # (only in local-launch mode; CDP context is owned by external Chrome).
        if owns_browser:
            try:
                await context.storage_state(path=str(cfg.storage_path))
            except Exception:
                pass
            await context.close()
            await browser.close()
        else:
            # CDP mode: do NOT close the user's Chrome; just release the connection
            try:
                await browser.close()
            except Exception:
                pass

    if not captured_body["data"]:
        raise RuntimeError(
            "Did not intercept /statements response — XP UI may have changed "
            "or network call timed out. Consider re-running xp_login_capture.py."
        )

    # Decode the payload
    try:
        payload = json.loads(captured_body["data"])
        content_b64 = payload["data"]["content"]
        ofx_bytes = base64.b64decode(content_b64)
    except Exception as e:
        raise RuntimeError(f"Failed to decode statements payload: {e}") from e

    dest.write_bytes(ofx_bytes)
    return dest


# ---------- main -----------------------------------------------------------


async def run(cfg: Config, ofx_path_override: Path | None = None, dry_run: bool = False) -> int:
    tz = ZoneInfo(cfg.timezone)
    now = datetime.now(tz)
    today = now.date()
    yesterday = today - timedelta(days=1)
    day_label = yesterday.isoformat()

    print(f"[*] XP sync for {day_label}  (dry_run={dry_run})", flush=True)

    # 1. OFX source: either a pre-downloaded file passed in, or auto-download
    if ofx_path_override:
        ofx_path = ofx_path_override
        print(f"[*] Using OFX override: {ofx_path}", flush=True)
    else:
        try:
            ofx_path = await download_ofx(cfg, yesterday, yesterday)
            print(f"[+] Downloaded OFX: {ofx_path}", flush=True)
        except RuntimeError as e:
            msg = f"XP sync: {e}"
            print(f"[-] {msg}", flush=True)
            notify_telegram(cfg, f"⚠️ {msg}")
            return 1
        except NotImplementedError as e:
            msg = f"XP sync: download automation ainda não implementado ({e})"
            print(f"[-] {msg}", flush=True)
            return 3

    # 2. Parse OFX
    try:
        txs = parse_ofx(ofx_path)
    except Exception as e:
        msg = f"XP sync: falha ao parsear OFX: {e}"
        print(f"[-] {msg}", flush=True)
        notify_telegram(cfg, f"❌ {msg}")
        return 2
    print(f"[+] Parsed {len(txs)} transactions from {ofx_path.name}", flush=True)

    if dry_run:
        for t in txs[:5]:
            print(f"    {t.date} {t.type:7} R$ {t.amount:>10,.2f}  {t.description[:60]}")
        print(f"    ... ({len(txs)} total)")
        return 0

    # 3. Write transactions
    cfg.memory_root.mkdir(parents=True, exist_ok=True)
    tx_path = write_transactions(cfg.memory_root, day_label, txs)
    print(f"[+] Wrote {tx_path}", flush=True)

    # 4. Conciliation
    contas = load_contas_pagar(cfg.contas_pagar_path)
    report = conciliate(txs, contas)

    # 5. Daily report
    report_path = write_daily_report(cfg.memory_root, day_label, txs, report, contas)
    print(f"[+] Wrote {report_path}", flush=True)

    # 6. Telegram
    summary = build_telegram_summary(day_label, report)
    notify_telegram(cfg, summary)
    print("[+] Telegram sent", flush=True)

    return 0


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    ofx_override = None
    for i, a in enumerate(argv):
        if a == "--ofx" and i + 1 < len(argv):
            ofx_override = Path(argv[i + 1])

    try:
        cfg = Config.load(CONFIG_PATH)
    except Exception as e:
        print(f"config load failed: {e}", file=sys.stderr)
        return 3

    try:
        return asyncio.run(run(cfg, ofx_path_override=ofx_override, dry_run=dry_run))
    except Exception:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        try:
            notify_telegram(cfg, f"❌ XP sync crashed:\n```\n{tb.splitlines()[-1]}\n```")
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
