#!/usr/bin/env python3
"""
PCS Inbox Triage — OpenClaw Agent
Triagem automatica da caixa de entrada PCS via Microsoft Graph API.

Buckets:
  URGENTE  -> notifica Flavia + pending.md (CRITICA)
  PENDENTE -> pending.md com prazo estimado
  ARQUIVO  -> marca como lido + label arquivo
  IGNORAR  -> move para lixeira

Uso:
  python3 inbox_triage.py [--dry-run] [--limit N] [--verbose]
"""
import json
import yaml
import os
import re
import sys
import argparse
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

# ── Paths ────────────────────────────────────────────────────────────────────
WORKSPACE     = Path("/root/.openclaw/workspace")
RULES_FILE    = WORKSPACE / "agents/pcs-agent/config/triage_rules.yaml"
PENDING_FILE  = Path("/root/2nd-brain/02-context/pending.md")
MS_GRAPH_CFG  = WORKSPACE / "config/ms-graph-pcs.json"
LOG_FILE      = WORKSPACE / "logs/pcs_triage.log"

BucketType = Literal["urgent", "pending", "archive", "ignore"]

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("pcs_triage")


# ── Config loaders ────────────────────────────────────────────────────────────
def load_rules() -> dict:
    """Carrega regras de triage do arquivo YAML."""
    if not RULES_FILE.exists():
        log.error("triage_rules.yaml nao encontrado: %s", RULES_FILE)
        sys.exit(1)
    with open(RULES_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_ms_graph_config() -> dict:
    """Carrega credenciais Microsoft Graph para conta PCS."""
    if not MS_GRAPH_CFG.exists():
        log.error("ms-graph-pcs.json nao encontrado: %s", MS_GRAPH_CFG)
        sys.exit(1)
    with open(MS_GRAPH_CFG, encoding="utf-8") as f:
        return json.load(f)


# ── Graph API client ──────────────────────────────────────────────────────────
def get_access_token(cfg: dict) -> str:
    """Obtém token OAuth2 via client_credentials."""
    try:
        import urllib.request
        import urllib.parse
        tenant = cfg.get("tenant_id") or cfg.get("tenantId", "")
        client_id = cfg.get("client_id") or cfg.get("clientId", "")
        client_secret = cfg.get("client_secret") or cfg.get("clientSecret", "")
        url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())["access_token"]
    except Exception as e:
        log.error("Falha ao obter token: %s", e)
        sys.exit(1)


def graph_get(token: str, path: str) -> dict:
    """GET request à Microsoft Graph API."""
    import urllib.request
    url = f"https://graph.microsoft.com/v1.0{path}"
    url = url.replace(" ", "%20")  # py3.12 strict URL validation
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def graph_patch(token: str, path: str, body: dict) -> None:
    """PATCH request à Microsoft Graph API."""
    import urllib.request
    url = f"https://graph.microsoft.com/v1.0{path}"
    url = url.replace(" ", "%20")  # py3.12 strict URL validation
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, method="PATCH",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def fetch_unread_messages(token: str, user_email: str, limit: int = 50) -> list:
    """Busca mensagens nao lidas da caixa de entrada."""
    path = (f"/users/{user_email}/mailFolders/inbox/messages"
            f"?$filter=isRead%20eq%20false&$top={limit}"
            f"&$select=id,subject,from,bodyPreview,body,receivedDateTime,categories")
    result = graph_get(token, path)
    return result.get("value", [])


def apply_category(token: str, user_email: str, msg_id: str,
                   current_categories: list[str], category: str,
                   dry_run: bool = False) -> None:
    """Aplica categoria Graph na mensagem sem perder categorias existentes."""
    if not category:
        return
    merged = list(dict.fromkeys(mut for mut in [*(current_categories or []), category] if mut))
    if dry_run:
        log.info("[DRY-RUN] Would apply category %s to %s (merged=%s)", category, msg_id, merged)
        return
    graph_patch(token, f"/users/{user_email}/messages/{msg_id}", {"categories": merged})
    log.info("Categoria aplicada %s em %s", category, msg_id)


# ── Classificação ─────────────────────────────────────────────────────────────
def _contains_any(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in (keywords or []))


def _extract_deadline_from_body(body: str) -> datetime | None:
    """Tenta extrair data de prazo do corpo do email."""
    patterns = [
        r"prazo[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
        r"vencimento[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
        r"até[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
        r"data limite[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
    ]
    for pat in patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            try:
                return datetime.strptime(m.group(1), "%d/%m/%Y").replace(
                    tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def classify_email(email: dict, rules: dict) -> BucketType:
    """
    Classifica um email em um dos 4 buckets.
    Ordem de prioridade: urgent > pending > archive > ignore
    """
    sender = (email.get("from", {})
                    .get("emailAddress", {})
                    .get("address", "")).lower()
    sender_name = (email.get("from", {})
                        .get("emailAddress", {})
                        .get("name", "")).lower()
    subject  = (email.get("subject") or "").lower()
    preview  = (email.get("bodyPreview") or "").lower()
    body     = (email.get("body", {}).get("content") or "").lower()
    received = email.get("receivedDateTime", "")

    # ── URGENT ──────────────────────────────────────────────────────────────
    urg = rules.get("urgent", {})
    if _contains_any(sender + " " + sender_name, urg.get("senders", [])):
        return "urgent"
    if _contains_any(subject, urg.get("subject_keywords", [])):
        return "urgent"
    if _contains_any(body + preview, urg.get("body_keywords", [])):
        return "urgent"
    # Verifica prazo <= max_days_to_deadline
    deadline = _extract_deadline_from_body(body)
    max_days = urg.get("max_days_to_deadline", 5)
    if deadline:
        now = datetime.now(timezone.utc)
        if 0 <= (deadline - now).days <= max_days:
            return "urgent"

    # ── PENDING ─────────────────────────────────────────────────────────────
    pend = rules.get("pending", {})
    if _contains_any(subject + " " + preview, pend.get("triggers", [])):
        return "pending"

    # ── IGNORE ──────────────────────────────────────────────────────────────
    ign = rules.get("ignore", {})
    if _contains_any(sender, ign.get("blocklist", [])):
        return "ignore"
    if _contains_any(subject, ign.get("subject_patterns", [])):
        return "ignore"

    # ── ARCHIVE ─────────────────────────────────────────────────────────────
    arch = rules.get("archive", {})
    if _contains_any(sender + " " + sender_name, arch.get("senders", [])):
        return "archive"
    if _contains_any(subject, arch.get("subject_patterns", [])):
        return "archive"
    if _contains_any(body + preview, arch.get("body_patterns", [])):
        return "archive"

    # Default: pending se nao classificado
    return "pending"


# ── Ações por bucket ─────────────────────────────────────────────────────────
def add_to_pending(email: dict, priority: str, rules: dict,
                   dry_run: bool = False) -> None:
    """Adiciona email ao pending.md com prioridade e prazo."""
    subject  = email.get("subject", "(sem assunto)")
    sender   = (email.get("from", {})
                     .get("emailAddress", {})
                     .get("address", ""))
    received = email.get("receivedDateTime", "")[:10]
    body     = (email.get("body", {}).get("content") or "")
    deadline = _extract_deadline_from_body(body)
    deadline_str = deadline.strftime("%d/%m/%Y") if deadline else "verificar"
    estimate_days = rules.get("pending", {}).get("deadline_estimate_days", 5)
    if priority == "PENDENTE" and not deadline:
        est = (datetime.now(timezone.utc) + timedelta(days=estimate_days))
        deadline_str = f"estimado {est.strftime('%d/%m/%Y')}"

    entry = (
        f"\n## [{priority}] {subject}\n"
        f"- **De:** {sender}\n"
        f"- **Recebido:** {received}\n"
        f"- **Prazo:** {deadline_str}\n"
        f"- **Ação:** A definir\n"
    )
    if dry_run:
        log.info("[DRY-RUN] Would append to pending.md:\n%s", entry)
        return
    with open(PENDING_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    log.info("Adicionado ao pending.md [%s]: %s", priority, subject)


def notify_flavia(email: dict, dry_run: bool = False) -> None:
    """Protocolo interno de notificacao urgente para Flávia."""
    subject = email.get("subject", "(sem assunto)")
    sender  = (email.get("from", {})
                    .get("emailAddress", {})
                    .get("address", ""))
    msg = f"[URGENTE] E-mail critico recebido de {sender}: {subject}"
    if dry_run:
        log.info("[DRY-RUN] NOTIFICACAO FLAVIA: %s", msg)
        return
    # Escreve em arquivo de notificacoes urgentes para pickup pelo agente
    notif_file = WORKSPACE / "memory/context/urgent_notifications.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(notif_file, "a", encoding="utf-8") as f:
        f.write(f"\n- [{ts}] {msg}\n")
    log.warning("URGENTE — Flavia notificada: %s", subject)


def mark_as_read_and_archive(token: str, user_email: str,
                              msg_id: str, dry_run: bool = False) -> None:
    """Marca email como lido."""
    if dry_run:
        log.info("[DRY-RUN] Would mark as read: %s", msg_id)
        return
    graph_patch(token, f"/users/{user_email}/messages/{msg_id}",
                {"isRead": True})
    log.info("Arquivado (marcado como lido): %s", msg_id)


def move_to_trash(token: str, user_email: str,
                  msg_id: str, dry_run: bool = False) -> None:
    """Move email para a lixeira."""
    if dry_run:
        log.info("[DRY-RUN] Would move to trash: %s", msg_id)
        return
    import urllib.request
    url = (f"https://graph.microsoft.com/v1.0"
           f"/users/{user_email}/messages/{msg_id}/move")
    data = json.dumps({"destinationId": "deleteditems"}).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()
    log.info("Movido para lixeira: %s", msg_id)


# ── Runner principal ──────────────────────────────────────────────────────────
def run_triage(dry_run: bool = False, limit: int = 50,
               verbose: bool = False) -> None:
    """Executa triagem completa da inbox PCS."""
    log.info("=== PCS INBOX TRIAGE INICIADO (dry_run=%s) ===", dry_run)

    cfg = load_ms_graph_config()
    rules = load_rules()
    user_email = (
        cfg.get("user_email")
        or cfg.get("userEmail")
        or cfg.get("default_user")
        or cfg.get("defaultUser")
        or cfg.get("mailbox")
        or ""
    )

    if not user_email:
        log.error("user_email nao encontrado em ms-graph-pcs.json")
        sys.exit(1)

    log.info("Autenticando para: %s", user_email)
    token = get_access_token(cfg)

    log.info("Buscando ate %d mensagens nao lidas...", limit)
    messages = fetch_unread_messages(token, user_email, limit)
    log.info("Total de mensagens: %d", len(messages))

    stats = {"urgent": 0, "pending": 0, "archive": 0, "ignore": 0}
    category_rules = rules.get("categories", {})

    for msg in messages:
        msg_id  = msg.get("id", "")
        subject = msg.get("subject", "(sem assunto)")
        bucket  = classify_email(msg, rules)
        stats[bucket] += 1
        current_categories = msg.get("categories") or []
        category = category_rules.get(bucket, "")

        if verbose:
            log.info("[%s] %s", bucket.upper(), subject)

        apply_category(token, user_email, msg_id, current_categories, category, dry_run)

        if bucket == "urgent":
            notify_flavia(msg, dry_run)
            add_to_pending(msg, "CRITICA", rules, dry_run)

        elif bucket == "pending":
            add_to_pending(msg, "PENDENTE", rules, dry_run)

        elif bucket == "archive":
            mark_as_read_and_archive(token, user_email, msg_id, dry_run)

        elif bucket == "ignore":
            move_to_trash(token, user_email, msg_id, dry_run)

    log.info("=== TRIAGE CONCLUIDO ===")
    log.info("Urgente: %d | Pendente: %d | Arquivo: %d | Ignorar: %d",
             stats["urgent"], stats["pending"],
             stats["archive"], stats["ignore"])


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PCS Inbox Triage — OpenClaw Agent")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simula acoes sem executar")
    parser.add_argument("--limit", type=int, default=50,
                        help="Numero maximo de emails a processar")
    parser.add_argument("--verbose", action="store_true",
                        help="Log detalhado por email")
    args = parser.parse_args()
    run_triage(dry_run=args.dry_run, limit=args.limit, verbose=args.verbose)
