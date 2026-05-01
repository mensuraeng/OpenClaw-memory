#!/usr/bin/env python3
"""Telegram Memory Digest v1.

Reads OpenClaw Telegram session transcripts, detects operationally relevant
messages since the previous run, and writes short candidate digests under:
/root/2nd-brain/07-telegram/digests/

This script does not send messages and does not promote facts into canonical
memory. It only creates reviewable digests.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", "/root/.openclaw/workspace"))
SECOND_BRAIN = Path(os.environ.get("SECOND_BRAIN", "/root/2nd-brain"))
SESSIONS_JSON = Path(os.environ.get("OPENCLAW_SESSIONS_JSON", "/root/.openclaw/agents/main/sessions/sessions.json"))
STATE_PATH = WORKSPACE / "runtime" / "telegram-memory-digest" / "state.json"
DIGEST_DIR = SECOND_BRAIN / "07-telegram" / "digests"

SIGNAL_RE = re.compile(
    r"\b("
    r"decid|decisão|decisao|aprov|autoriza|ok[!, ]|faça|faca|implanta|registre|registrar|"
    r"pend[eê]ncia|prazo|venc|cobran|boleto|nota fiscal|nfse|nf-e|contrato|aditivo|medição|medicao|"
    r"cliente|fornecedor|proposta|campanha|linkedin|meta ads|sienge|cron|mem[oó]ria|2nd brain|"
    r"risco|bloqueio|urgente|importante|comita|commit|rollback|backup"
    r")",
    re.IGNORECASE,
)

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{8,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
    re.compile(r"ya29\.[A-Za-z0-9_.-]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(access[_-]?token|api[_-]?key|client[_-]?secret|password|senha)\s*[:=]\s*['\"]?[^\s'\"]{12,}"),
]


@dataclass(frozen=True)
class Surface:
    slug: str
    session_key: str
    memory_file: str
    chat_id: str
    topic_id: str | None
    agent: str
    title: str


SURFACES: list[Surface] = [
    Surface("direct-alexandre", "agent:main:telegram:direct:1067279351", "chats/direct-alexandre.md", "1067279351", None, "main/flavia", "Direct Alexandre ↔ Flávia"),
    Surface("mensura-mkt", "agent:main:telegram:group:-1003366344184:topic:43", "topics/mensura-mkt.md", "-1003366344184", "43", "marketing", "MENSURA / MKT"),
    Surface("mensura-geral", "agent:main:telegram:group:-1003366344184:topic:1", "topics/mensura-geral.md", "-1003366344184", "1", "mensura", "MENSURA / Geral"),
    Surface("financeiro", "agent:main:telegram:group:-1003818163425:topic:13", "topics/financeiro.md", "-1003818163425", "13", "finance", "Financeiro"),
    Surface("mia-geral", "agent:main:telegram:group:-1003704703669:topic:1", "topics/mia-geral.md", "-1003704703669", "1", "mia", "MIA / Geral"),
    Surface("pcs-geral", "agent:main:telegram:group:-1003146152550:topic:1", "topics/pcs-geral.md", "-1003146152550", "1", "pcs", "PCS / Geral"),
    Surface("trade-noticias", "agent:main:telegram:group:-1003794434256:topic:1", "topics/trade-noticias.md", "-1003794434256", "1", "trade", "Trade / Notícias"),
]


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def iso_to_dt(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") in {"text", "input_text"}:
                parts.append(str(item.get("text", "")))
        return "\n".join(p for p in parts if p)
    return ""


def redact(text: str) -> str:
    out = text
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED_SECRET]", out)
    return out.strip()


def compact(text: str, limit: int = 320) -> str:
    text = re.sub(r"\s+", " ", redact(text)).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def parse_user_messages(session_file: Path, since: datetime | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not session_file.exists():
        return rows
    with session_file.open("r", errors="ignore") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") != "message":
                continue
            ts_raw = obj.get("timestamp")
            ts = iso_to_dt(ts_raw or "")
            if not ts:
                continue
            if since and ts <= since:
                continue
            msg = obj.get("message") or {}
            if msg.get("role") != "user":
                continue
            text = text_from_content(msg.get("content"))
            text = redact(text)
            if not text:
                continue
            rows.append({"timestamp": ts_raw, "text": text})
    return rows


def classify(messages: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    signal = []
    for m in messages:
        if SIGNAL_RE.search(m["text"]):
            signal.append(m)
    should_digest = bool(signal) or len(messages) >= 30
    return signal, should_digest


def digest_markdown(surface: Surface, messages: list[dict[str, str]], signal: list[dict[str, str]], generated_at: str) -> str:
    first = messages[0]["timestamp"] if messages else generated_at
    last = messages[-1]["timestamp"] if messages else generated_at
    signal_rows = signal[:12]
    all_rows = messages[:20]

    def bullets(rows: list[dict[str, str]]) -> str:
        if not rows:
            return "- nenhuma"
        return "\n".join(f"- `{r['timestamp']}` — {compact(r['text'])}" for r in rows)

    return f"""# Digest Telegram — {surface.title} — {generated_at[:10]}

## Origem

- Chat ID: `{surface.chat_id}`
- Topic ID: `{surface.topic_id or '-'}`
- Session key: `{surface.session_key}`
- Memória de superfície: `07-telegram/{surface.memory_file}`
- Período: `{first}` → `{last}`
- Gerado por: `scripts/telegram_memory_digest.py`
- Maturidade: candidato; revisar antes de promover para fonte canônica

## Sinais detectados

{bullets(signal_rows)}

## Amostra de mensagens novas

{bullets(all_rows)}

## Promoção recomendada

- [ ] revisar se há decisão para `02-context/decisions.md`
- [ ] revisar se há pendência para `02-context/pending.md`
- [ ] revisar se há contexto de projeto para `04-projects/...`
- [ ] revisar se há atualização curta para `07-telegram/{surface.memory_file}`

## Segurança

- Segredos conhecidos foram redigidos automaticamente quando detectados.
- Este digest não autoriza ação externa, financeira, jurídica, contratual ou reputacional.
"""


def run_git_commit(paths: list[Path], message: str) -> str:
    if not paths:
        return "no paths"
    rels = [str(p.relative_to(SECOND_BRAIN)) for p in paths if str(p).startswith(str(SECOND_BRAIN))]
    if not rels:
        return "no 2nd-brain paths"
    subprocess.run(["git", "-C", str(SECOND_BRAIN), "add", "--", *rels], check=True)
    diff = subprocess.run(["git", "-C", str(SECOND_BRAIN), "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return "no changes"
    subprocess.run(["git", "-C", str(SECOND_BRAIN), "commit", "-m", message], check=True)
    head = subprocess.check_output(["git", "-C", str(SECOND_BRAIN), "rev-parse", "--short", "HEAD"], text=True).strip()
    return head


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate candidate Telegram memory digests from OpenClaw session logs.")
    ap.add_argument("--execute", action="store_true", help="Write digests and update state. Default is dry-run.")
    ap.add_argument("--commit", action="store_true", help="Commit created digests in /root/2nd-brain.")
    ap.add_argument("--surface", action="append", help="Limit to one or more surface slugs.")
    ap.add_argument("--since", help="Override last processed timestamp, ISO-8601.")
    ap.add_argument("--min-signal", type=int, default=1, help="Minimum signal messages required to write digest unless threshold count is reached.")
    args = ap.parse_args()

    sessions = load_json(SESSIONS_JSON, {})
    state = load_json(STATE_PATH, {"surfaces": {}})
    state.setdefault("surfaces", {})
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    selected = {s.slug for s in SURFACES if not args.surface or s.slug in set(args.surface)}
    created: list[Path] = []
    report: list[dict[str, Any]] = []

    for surface in SURFACES:
        if surface.slug not in selected:
            continue
        meta = sessions.get(surface.session_key)
        if not meta:
            report.append({"surface": surface.slug, "status": "no_session"})
            continue
        session_file = Path(meta.get("sessionFile") or "")
        since_raw = args.since or state["surfaces"].get(surface.slug, {}).get("last_processed_at")
        since = iso_to_dt(since_raw) if since_raw else None
        messages = parse_user_messages(session_file, since)
        signal, should_digest = classify(messages)
        if len(signal) < args.min_signal and len(messages) < 30:
            should_digest = False

        entry: dict[str, Any] = {
            "surface": surface.slug,
            "session_file": str(session_file),
            "new_messages": len(messages),
            "signal_messages": len(signal),
            "status": "digest_pending" if should_digest else "no_digest",
        }
        if should_digest:
            fname = f"{now[:10]}_{surface.slug}_{now[11:19].replace(':','')}.md"
            out = DIGEST_DIR / fname
            entry["digest"] = str(out)
            if args.execute:
                DIGEST_DIR.mkdir(parents=True, exist_ok=True)
                out.write_text(digest_markdown(surface, messages, signal, now))
                created.append(out)
        if args.execute and messages:
            state["surfaces"][surface.slug] = {
                "last_processed_at": messages[-1]["timestamp"],
                "last_session_file": str(session_file),
                "last_run_at": now,
            }
        report.append(entry)

    commit_ref = None
    if args.execute:
        save_json(STATE_PATH, state)
        if args.commit and created:
            commit_ref = run_git_commit(created, "Add Telegram memory digests")

    print(json.dumps({"mode": "execute" if args.execute else "dry-run", "generated_at": now, "created": [str(p) for p in created], "commit": commit_ref, "report": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
