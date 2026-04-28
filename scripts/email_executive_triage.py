#!/usr/bin/env python3
"""Executive email triage for Alexandre's Microsoft 365 mailboxes.

Read-only by default. With --apply-categories, patches Outlook categories only.
Never sends, moves, deletes, archives, or marks messages as read.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path("/root/.openclaw/workspace")
CONFIGS = {
    "mensura": WORKSPACE / "config" / "ms-graph.json",
    "mia": WORKSPACE / "config" / "ms-graph-mia.json",
    "pcs": WORKSPACE / "config" / "ms-graph-pcs.json",
}
MAILBOXES = [
    {"account": "mensura", "user": "alexandre@mensuraengenharia.com.br", "label": "Mensura"},
    {"account": "mia", "user": "alexandre@miaengenharia.com.br", "label": "MIA"},
    {"account": "pcs", "user": "alexandre@pcsengenharia.com.br", "label": "PCS"},
]
STATE_PATH = WORKSPACE / "runtime" / "email-executive-triage" / "state.json"
REPORT_DIR = WORKSPACE / "runtime" / "email-executive-triage" / "reports"

BRT = timezone(timedelta(hours=-3))
UTC = timezone.utc

PRIMARY = ["OBRAS", "FINANCEIRO", "COMERCIAL", "MARKETING & PROPAGANDA", "JURÍDICO & CONTRATOS", "EQUIPE INTERNA", "INSTITUCIONAL", "RUÍDO"]
PRIORITIES = ["CRÍTICO", "IMPORTANTE", "DELEGÁVEL", "INFORMATIVO"]
CATEGORY_COLORS = {
    "CRÍTICO": "preset0",
    "IMPORTANTE": "preset3",
    "DELEGÁVEL": "preset4",
    "INFORMATIVO": "preset7",
    "OBRAS": "preset9",
    "FINANCEIRO": "preset5",
    "COMERCIAL": "preset10",
    "MARKETING & PROPAGANDA": "preset11",
    "JURÍDICO & CONTRATOS": "preset1",
    "EQUIPE INTERNA": "preset6",
    "INSTITUCIONAL": "preset8",
    "RUÍDO": "preset14",
    "VALOR > R$50K": "preset0",
}

NOISE_SENDERS = [
    "noreply", "no-reply", "newsletter", "mailchimp", "rdstation", "hubspot", "sympla",
    "linkedin", "facebook", "instagram", "google alerts", "notification", "notifications",
    "marketing.", "@marketing.", "@news.", "freepik", "decolar", "shopper", "privaterelay.appleid.com",
    "café com ia", "allessandrasinisgalli", "riachuelo", "unidas", "reclameaqui", "latampass",
    "topazlabs", "indeed", "mercadolivre", "artesana", "resultadosdigitaismail",
    "flaviacardososoaresleiloes", "cbrdoc",
]
NOISE_WORDS = [
    "newsletter", "unsubscribe", "descadastrar", "promoção", "promocao", "webinar", "evento gratuito",
    "marketing digital", "até ", " off", "%off", "frete grátis", "frete gratis", "aniversário", "aniversario",
    "seleção", "selecao", "desconto", "cupom", "oferta", "últimos dias", "ultimos dias", "black friday",
    "feastables", "equipamentos inox para laboratório sob medida", "máxima segurança e qualidade",
    "leilão", "leilao", "colecionáveis", "colecionaveis", "news |", "cbrdoc news",
]

OBRAS_ALIASES = {
    "CCSP Casa 7": ["ccsp", "casa 7", "casa sete", "centro cultural são paulo", "centro cultural sao paulo", "victor evangelista"],
    "P&G Louveira": ["26.271.1.120", "consultoria em planejamento", "contrato 26.271", "reunião de atualização de cronograma", "reuniao de atualizacao de cronograma", "laic", "oasis", "p&g", "pg louveira", "p&g louveira", "louveira", "procter", "gamble"],
    "Teatro Suzano": ["teatro suzano", "suzano", "sienge"],
    "Paranapiacaba": ["paranapiacaba"],
}

TEAM_HINTS = {
    "financeiro": ["boleto", "nota fiscal", "nf", "fatura", "cobrança", "cobranca", "pagamento", "vencimento", "imposto", "darfs", "banco"],
    "juridico": ["contrato", "minuta", "aditivo", "notificação", "notificacao", "processo", "multa", "autuação", "autuacao", "cláusula", "clausula"],
    "comercial": ["proposta", "orçamento", "orcamento", "cotação", "cotacao", "lead", "concorrência", "concorrencia", "rfi", "rfp"],
}

@dataclass
class Triage:
    mailbox_label: str
    mailbox_user: str
    id: str
    web_link: str
    received: str
    sender: str
    subject: str
    preview: str
    primary: str
    priority: str
    obra: str | None = None
    amount: float | None = None
    confidence: str = "média"
    reason: str = ""
    action: str = ""
    delegate_to: str | None = None
    categories: list[str] = field(default_factory=list)
    conversation_id: str | None = None


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def token_for(account: str) -> str:
    cfg = load_config(CONFIGS[account])
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": cfg["clientId"],
        "client_secret": cfg["clientSecret"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["access_token"]


def graph(token: str, path: str, method: str = "GET", body: Any = None) -> dict[str, Any]:
    url = "https://graph.microsoft.com/v1.0" + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": 'outlook.body-content-type="text"',
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Graph {method} {path} failed {e.code}: {e.read().decode('utf-8', 'replace')}") from e


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"mailboxes": {}, "critical_pending": {}}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def clean(s: str | None) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def money_amount(text: str) -> float | None:
    # Handles R$ 50.000,00 / 50000 / 50 mil
    candidates: list[float] = []
    for m in re.finditer(r"R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?|[0-9]+(?:,[0-9]{2})?)", text, re.I):
        raw = m.group(1).replace(".", "").replace(",", ".")
        try:
            candidates.append(float(raw))
        except ValueError:
            pass
    for m in re.finditer(r"\b([0-9]+(?:,[0-9]+)?)\s*mil\b", text, re.I):
        try:
            candidates.append(float(m.group(1).replace(",", ".")) * 1000)
        except ValueError:
            pass
    return max(candidates) if candidates else None


def contains_any(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in words)


def alias_matches(text: str, alias: str) -> bool:
    # Avoid false positives from short aliases inside unrelated words.
    if re.fullmatch(r"[a-z0-9&. -]{1,8}", alias, flags=re.I):
        return re.search(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])", text) is not None
    return alias.lower() in text


def detect_obra(text: str) -> str | None:
    t = text.lower()
    for obra, aliases in OBRAS_ALIASES.items():
        if any(alias_matches(t, a) for a in aliases):
            return obra
    return None


def classify(mailbox_label: str, mailbox_user: str, m: dict[str, Any]) -> Triage:
    sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
    subject = clean(m.get("subject") or "(sem assunto)")
    preview = clean(m.get("bodyPreview") or "")
    text = f"{sender} {subject} {preview}".lower()
    amount = money_amount(text)
    obra = detect_obra(text)

    primary = "INFORMATIVO"
    confidence = "média"
    if contains_any(sender, NOISE_SENDERS) or contains_any(text, NOISE_WORDS):
        primary = "RUÍDO"
        confidence = "alta"
    elif obra or contains_any(text, ["obra", "rdo", "medição", "medicao", "cronograma", "canteiro", "diário de obra", "diario de obra", "projeto executivo"]):
        primary = "OBRAS"
        confidence = "alta" if obra else "média"
    elif contains_any(text, TEAM_HINTS["financeiro"]):
        primary = "FINANCEIRO"
        confidence = "alta"
    elif contains_any(text, TEAM_HINTS["juridico"]):
        primary = "JURÍDICO & CONTRATOS"
        confidence = "alta"
    elif contains_any(text, TEAM_HINTS["comercial"]):
        primary = "COMERCIAL"
        confidence = "alta"
    elif contains_any(text, ["crea", "prefeitura", "tce", "tcu", "conselho", "sindicato", "órgão", "orgao", "concessionária", "concessionaria"]):
        primary = "INSTITUCIONAL"
        confidence = "alta"
    elif contains_any(text, ["rh", "folha", "funcionário", "funcionario", "colaborador", "equipe", "férias", "ferias"]):
        primary = "EQUIPE INTERNA"
        confidence = "média"
    elif contains_any(text, ["agência", "agencia", "branding", "mídia", "midia", "rede social", "instagram", "tráfego pago", "trafego pago"]):
        primary = "MARKETING & PROPAGANDA"
        confidence = "média"
    else:
        primary = "INFORMATIVO"
        confidence = "baixa"

    priority = "INFORMATIVO"
    reason_parts: list[str] = []
    if primary == "RUÍDO":
        priority = "INFORMATIVO"
        reason_parts.append("ruído/propaganda sem ação executiva aparente")
    if amount and amount >= 50000:
        priority = "CRÍTICO"
        reason_parts.append(f"valor acima de R$ 50.000 ({amount:,.2f})")
    critical_terms = ["urgente", "hoje", "imediato", "prazo final", "vencimento", "vence amanhã", "vence amanha", "48h", "notificação", "notificacao", "autuação", "autuacao", "multa", "paralisação", "paralisacao", "rompimento", "rescisão", "rescisao", "inadimpl", "protesto"]
    important_terms = ["pendente", "aprovação", "aprovacao", "responder", "retorno", "follow-up", "reunião", "reuniao", "cronograma", "medição", "medicao", "proposta", "contrato"]
    critical_eligible = primary in {"OBRAS", "FINANCEIRO", "JURÍDICO & CONTRATOS", "INSTITUCIONAL", "COMERCIAL"}
    if contains_any(text, critical_terms) and primary != "RUÍDO" and critical_eligible:
        priority = "CRÍTICO"
        reason_parts.append("termo de urgência/risco detectado")
    elif priority != "CRÍTICO" and contains_any(text, important_terms) and primary != "RUÍDO":
        priority = "IMPORTANTE"
        reason_parts.append("exige acompanhamento em até 48h")
    elif primary in {"FINANCEIRO", "JURÍDICO & CONTRATOS", "COMERCIAL", "OBRAS"} and primary != "RUÍDO":
        priority = "IMPORTANTE"
        reason_parts.append("categoria gerencial relevante")

    delegate_to = None
    if priority not in {"CRÍTICO", "INFORMATIVO"}:
        priority = "DELEGÁVEL" if primary in {"EQUIPE INTERNA", "MARKETING & PROPAGANDA"} else priority
    if primary == "FINANCEIRO":
        delegate_to = "Financeiro / responsável administrativo"
    elif primary == "OBRAS":
        delegate_to = "engenheiro/gestor da obra" if obra else "operação de obras"
    elif primary == "COMERCIAL":
        delegate_to = "comercial/orçamentos"
    elif primary == "JURÍDICO & CONTRATOS":
        delegate_to = "jurídico/contratos"
    elif primary == "MARKETING & PROPAGANDA":
        delegate_to = "marketing"
    elif primary == "EQUIPE INTERNA":
        delegate_to = "RH/administrativo"

    if priority == "CRÍTICO":
        action = "avaliar e responder hoje; se for delegar, confirmar responsável e prazo"
    elif priority == "IMPORTANTE":
        action = "tratar em até 48h ou delegar com prazo definido"
    elif priority == "DELEGÁVEL":
        action = f"encaminhar para {delegate_to or 'responsável'} com orientação objetiva"
    else:
        action = "somente ciência; sem ação imediata"

    # Visual rule: if a specific obra is known, do not also add generic OBRAS.
    cats = [priority]
    if primary == "OBRAS" and obra:
        cats.append(f"OBRA — {obra}")
    else:
        cats.append(primary)
    if amount and amount >= 50000:
        cats.append("VALOR > R$50K")

    return Triage(
        mailbox_label=mailbox_label,
        mailbox_user=mailbox_user,
        id=m["id"],
        web_link=m.get("webLink") or "",
        received=m.get("receivedDateTime") or "",
        sender=sender,
        subject=subject,
        preview=preview,
        primary=primary,
        priority=priority,
        obra=obra,
        amount=amount,
        confidence=confidence,
        reason="; ".join(reason_parts) or "classificação heurística sem sinal crítico explícito",
        action=action,
        delegate_to=delegate_to,
        categories=cats,
        conversation_id=m.get("conversationId"),
    )


def fetch_messages(token: str, user: str, since: datetime, limit: int) -> list[dict[str, Any]]:
    since_s = iso_utc(since)
    select = "id,conversationId,subject,from,receivedDateTime,isRead,bodyPreview,webLink,categories,hasAttachments,importance"
    filt = urllib.parse.quote(f"receivedDateTime ge {since_s}")
    path = f"/users/{user}/mailFolders/inbox/messages?$top={limit}&$orderby=receivedDateTime%20desc&$filter={filt}&$select={select}"
    data = graph(token, path)
    return data.get("value", [])


def category_color(name: str) -> str:
    if name.startswith("OBRA —"):
        return "preset9"
    return CATEGORY_COLORS.get(name, "preset7")


def ensure_master_categories(token: str, user: str, names: list[str]) -> None:
    data = graph(token, f"/users/{user}/outlook/masterCategories?$select=id,displayName,color")
    existing = {c.get("displayName"): c for c in data.get("value", [])}
    for name in sorted({n for n in names if n}):
        color = category_color(name)
        current = existing.get(name)
        if not current:
            graph(token, f"/users/{user}/outlook/masterCategories", method="POST", body={"displayName": name, "color": color})
        elif current.get("color") != color:
            graph(token, f"/users/{user}/outlook/masterCategories/{current['id']}", method="PATCH", body={"color": color})


def normalize_existing_categories(categories: list[str]) -> list[str]:
    mapping = {
        "Flávia/OBRAS": "OBRAS",
        "Flávia/FINANCEIRO": "FINANCEIRO",
        "Flávia/COMERCIAL": "COMERCIAL",
        "Flávia/MARKETING & PROPAGANDA": "MARKETING & PROPAGANDA",
        "Flávia/JURÍDICO & CONTRATOS": "JURÍDICO & CONTRATOS",
        "Flávia/EQUIPE INTERNA": "EQUIPE INTERNA",
        "Flávia/INSTITUCIONAL": "INSTITUCIONAL",
        "Flávia/RUÍDO": "RUÍDO",
        "Flávia/CRÍTICO": "CRÍTICO",
        "Flávia/IMPORTANTE": "IMPORTANTE",
        "Flávia/DELEGÁVEL": "DELEGÁVEL",
        "Flávia/INFORMATIVO": "INFORMATIVO",
        "Flávia/Valor>50k": "VALOR > R$50K",
    }
    out = []
    for c in categories:
        if c.startswith("Obra/"):
            new = "OBRA — " + c.split("/", 1)[1]
        else:
            new = mapping.get(c, c)
        if new and new not in out:
            out.append(new)
    return out


def patch_categories(token: str, user: str, msg_id: str, existing: list[str], new: list[str]) -> None:
    merged = []
    for c in normalize_existing_categories(existing) + new:
        if c and c not in merged:
            merged.append(c)
    # If this run knows the specific obra, remove generic/old obra categories to avoid visual duplication.
    desired_obra = {c for c in new if c.startswith("OBRA —")}
    if desired_obra:
        merged = [c for c in merged if c != "OBRAS" and (not c.startswith("OBRA —") or c in desired_obra)]
    ensure_master_categories(token, user, merged)
    graph(token, f"/users/{user}/messages/{msg_id}", method="PATCH", body={"categories": merged})


def triage_all(lookback_hours: int, limit_per_box: int, apply_categories: bool, update_state: bool, ignore_state: bool = False) -> tuple[list[Triage], dict[str, Any]]:
    state = load_state()
    now = datetime.now(UTC)
    all_items: list[Triage] = []
    category_errors: list[str] = []
    mailbox_errors: list[str] = []
    for mb in MAILBOXES:
        key = mb["user"]
        last = None if ignore_state else state.get("mailboxes", {}).get(key, {}).get("last_report_utc")
        if last:
            since = parse_dt(last) - timedelta(minutes=5)
        else:
            since = now - timedelta(hours=lookback_hours)
        try:
            token = token_for(mb["account"])
            msgs = fetch_messages(token, mb["user"], since, limit_per_box)
        except Exception as e:
            mailbox_errors.append(f"{mb['label']} <{mb['user']}>: {e}")
            continue
        # dedupe by id; classification keeps all conversations but report groups later
        for m in msgs:
            item = classify(mb["label"], mb["user"], m)
            all_items.append(item)
            if apply_categories:
                try:
                    patch_categories(token, mb["user"], m["id"], m.get("categories") or [], item.categories)
                except Exception as e:  # category failure must not stop triage
                    category_errors.append(f"{mb['user']} {item.subject[:50]}: {e}")
        if update_state:
            state.setdefault("mailboxes", {}).setdefault(key, {})["last_report_utc"] = iso_utc(now)
    if category_errors:
        state["last_category_errors"] = category_errors[-20:]
    if mailbox_errors:
        state["last_mailbox_errors"] = mailbox_errors[-20:]
    else:
        state.pop("last_mailbox_errors", None)
    if update_state:
        save_state(state)
    return all_items, state


def summarize(items: list[Triage], state: dict[str, Any] | None = None) -> str:
    state = state or {}
    now_brt = datetime.now(BRT).strftime("%d/%m/%Y %H:%M BRT")
    noise = [i for i in items if i.primary == "RUÍDO"]
    visible = [i for i in items if i.primary != "RUÍDO"]
    crit = [i for i in visible if i.priority == "CRÍTICO"]
    imp = [i for i in visible if i.priority == "IMPORTANTE"]
    deleg = [i for i in visible if i.priority == "DELEGÁVEL"]

    def one_line(i: Triage) -> str:
        obra = f" | {i.obra}" if i.obra else ""
        val = f" | R$ {i.amount:,.2f}" if i.amount else ""
        link = f" | {i.web_link}" if i.web_link else ""
        return f"- {i.sender} — {i.subject[:110]} — {i.action}{obra}{val}{link}"

    lines = [f"# Triagem executiva de e-mails — {now_brt}", ""]
    lines.append(f"Escopo: Mensura, MIA e PCS | novos itens analisados: {len(items)} | ruído agregado: {len(noise)}")
    if state.get("last_mailbox_errors"):
        lines.append("⚠️ Caixas com falha de acesso neste ciclo: " + "; ".join(state["last_mailbox_errors"]))
    if state.get("last_category_errors"):
        lines.append("⚠️ Falhas de categorização Office: " + "; ".join(state["last_category_errors"][:3]))
    lines.append("")
    lines.append("## 🔴 CRÍTICOS — responder hoje")
    lines.extend([one_line(i) for i in crit] or ["- Nenhum crítico novo detectado."])
    lines.append("")
    lines.append("## 🟡 IMPORTANTES")
    lines.extend([one_line(i) for i in imp[:12]] or ["- Nenhum importante novo detectado."])
    lines.append("")

    obras: dict[str, list[Triage]] = {}
    for i in visible:
        if i.primary == "OBRAS":
            obras.setdefault(i.obra or "Obra não identificada", []).append(i)
    lines.append("## 📊 RESUMO POR OBRA")
    if obras:
        for obra, arr in sorted(obras.items()):
            c = sum(1 for x in arr if x.priority == "CRÍTICO")
            im = sum(1 for x in arr if x.priority == "IMPORTANTE")
            lines.append(f"- {obra}: {len(arr)} e-mails | {c} críticos | {im} importantes")
    else:
        lines.append("- Nenhum e-mail novo de obra identificado.")
    lines.append("")

    fin = [i for i in visible if i.primary == "FINANCEIRO"]
    lines.append("## 💰 FINANCEIRO DO DIA")
    lines.extend([one_line(i) for i in fin[:10]] or ["- Nenhuma pendência financeira nova detectada."])
    lines.append("")

    com = [i for i in visible if i.primary == "COMERCIAL"]
    lines.append("## 🤝 OPORTUNIDADES COMERCIAIS")
    lines.extend([one_line(i) for i in com[:10]] or ["- Nenhuma oportunidade comercial nova detectada."])
    lines.append("")

    lines.append("## 👥 PARA DELEGAR")
    lines.extend([f"- {i.subject[:90]} → {i.delegate_to or 'responsável a definir'} → {i.action}" for i in deleg[:12]] or ["- Nenhum item delegável novo detectado."])
    lines.append("")

    # simple pattern detection by conversation/sender
    by_sender: dict[str, int] = {}
    for i in visible:
        by_sender[i.sender] = by_sender.get(i.sender, 0) + 1
    patterns = [f"- {s}: {n} e-mails no período" for s, n in sorted(by_sender.items(), key=lambda kv: kv[1], reverse=True) if n >= 3]
    lines.append("## ⚠️ PADRÕES DETECTADOS")
    lines.extend(patterns or ["- Nenhum padrão de reincidência relevante detectado neste ciclo."])
    lines.append("")
    lines.append("## 🧹 RUÍDO")
    lines.append(f"- {len(noise)} itens agregados, sem detalhamento.")
    return "\n".join(lines).strip() + "\n"


def write_report(markdown: str, items: list[Triage]) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BRT).strftime("%Y%m%d-%H%M")
    md = REPORT_DIR / f"triagem-email-{stamp}.md"
    js = REPORT_DIR / f"triagem-email-{stamp}.json"
    md.write_text(markdown, encoding="utf-8")
    js.write_text(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2), encoding="utf-8")
    latest = REPORT_DIR / "latest.md"
    latest_json = REPORT_DIR / "latest.json"
    latest.write_text(markdown, encoding="utf-8")
    latest_json.write_text(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2), encoding="utf-8")
    return md, js


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lookback-hours", type=int, default=18)
    ap.add_argument("--limit-per-box", type=int, default=50)
    ap.add_argument("--apply-categories", action="store_true", help="PATCH Outlook categories on messages")
    ap.add_argument("--update-state", action="store_true", help="Persist last_report timestamp")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet-if-empty", action="store_true")
    ap.add_argument("--ignore-state", action="store_true", help="Ignore last_report timestamp and use lookback window")
    args = ap.parse_args(argv)

    items, state = triage_all(args.lookback_hours, args.limit_per_box, args.apply_categories, args.update_state, args.ignore_state)
    md = summarize(items, state)
    md_path, json_path = write_report(md, items)
    has_material = any(i.priority in {"CRÍTICO", "IMPORTANTE"} and i.primary != "RUÍDO" for i in items)
    result = {
        "ok": True,
        "items": len(items),
        "material": has_material,
        "appliedCategories": bool(args.apply_categories),
        "report": str(md_path),
        "json": str(json_path),
        "latest": str(REPORT_DIR / "latest.md"),
    }
    if args.quiet_if_empty and not has_material:
        print("NO_REPLY")
    elif args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
