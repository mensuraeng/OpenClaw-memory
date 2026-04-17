#!/usr/bin/env python3
"""
Monitor Semanal — Flávia
Roda toda segunda-feira às 8h BRT (cron 0 11 * * 1).

Monitora:
  - cronogramas .mpp das obras ativas (P&G Louveira / Mensura, CCSP / MIA)
  - emails não lidos com palavras-chave de alerta (últimas 48h)
  - agenda da semana (próximos 7 dias) por conta

Pós-FASE 5: NÃO fala mais com Telegram. Função send_telegram removida
(antes era código morto desde 16/04 - script estava silencioso há 1 semana).
Gera o relatório consolidado e entrega como payload à Flávia, que decide
a saída final (mostrar no DM, alertar, delegar para mensura/mia se algum
domínio exigir profundidade).

Urgência calculada:
  high   se há alerta em P&G Louveira (projeto crítico - notificação legal)
         ou cronograma sem atualização há >10 dias
  normal se há ≥1 alerta de qualquer tipo
  low    se nenhum alerta

Flags:
  --skip-flavia    imprime relatório no stdout; não entrega à Flávia
  --print          alias retrocompat
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

# Obras ativas monitoradas — arquivo .mpp mais recente
OBRAS_ATIVAS = [
    {
        "empresa": "Mensura",
        "nome": "P&G Louveira",
        "config": "/root/.openclaw/workspace/config/ms-graph.json",
        "site_name": "SUMEngenhariaPGLouveira",
        "busca": "P&G - Cronograma Diretor",
        "alerta_dias": 7
    },
    {
        "empresa": "MIA",
        "nome": "CCSP Casa 7",
        "config": "/root/.openclaw/workspace/config/ms-graph-mia.json",
        "site_name": "CCSP-Casa7",
        "busca": "CCSP CASA 3 - Cronograma Executivo",
        "alerta_dias": 7
    },
]

CONTAS = [
    {
        "label": "Mensura",
        "user": "alexandre@mensuraengenharia.com.br",
        "config": "/root/.openclaw/workspace/config/ms-graph.json"
    },
    {
        "label": "MIA",
        "user": "alexandre@miaengenharia.com.br",
        "config": "/root/.openclaw/workspace/config/ms-graph-mia.json"
    },
    {
        "label": "PCS",
        "user": "alexandre@pcsengenharia.com.br",
        "config": "/root/.openclaw/workspace/config/ms-graph-pcs.json"
    }
]

# Palavras-chave que indicam urgência / atraso / pendência
KEYWORDS_ALERTA = [
    "atraso", "atrasado", "atrasada", "prazo", "urgente", "urgência",
    "pendente", "pendência", "vencimento", "vencido", "não entregue",
    "relatório", "cronograma", "obra", "obra parada", "problema",
    "pleito", "bloqueio", "sem resposta", "aguardando", "atençao",
    "atenção", "crítico", "risco", "alerta"
]

def get_token(cfg_file):
    with open(cfg_file) as f:
        cfg = json.load(f)
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": cfg["clientId"],
        "client_secret": cfg["clientSecret"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)["access_token"]

def graph(token, path):
    url = f"https://graph.microsoft.com/v1.0{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.request.HTTPError as e:
        return {"error": e.read().decode()}

def check_emails_urgentes(token, user, label):
    """Busca emails não lidos com palavras-chave de alerta"""
    alertas = []
    # Buscar emails não lidos recentes (últimas 48h)
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = f"/users/{user}/mailFolders/inbox/messages?$filter=isRead+eq+false+and+receivedDateTime+ge+{since}&$top=50&$select=id,subject,from,receivedDateTime,bodyPreview"
    data = graph(token, path)
    msgs = data.get("value", [])
    
    for m in msgs:
        subject = m.get("subject", "").lower()
        preview = m.get("bodyPreview", "").lower()
        texto = subject + " " + preview
        
        for kw in KEYWORDS_ALERTA:
            if kw in texto:
                sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
                date = m.get("receivedDateTime", "")[:16].replace("T", " ")
                alertas.append(f"  📧 [{date}] De: {sender}\n     Assunto: {m.get('subject','')}")
                break
    
    return alertas

def check_calendario_semana(token, user, label):
    """Lista eventos da semana atual"""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=7)
    path = f"/users/{user}/calendarView?startDateTime={now.strftime('%Y-%m-%dT%H:%M:%SZ')}&endDateTime={end.strftime('%Y-%m-%dT%H:%M:%SZ')}&$orderby=start/dateTime&$select=subject,start,end,location,organizer&$top=15"
    data = graph(token, path)
    events = []
    for e in data.get("value", []):
        start = e.get("start", {}).get("dateTime", "")[:16].replace("T", " ")
        loc = e.get("location", {}).get("displayName", "")
        loc_str = f" | 📍 {loc}" if loc else ""
        events.append(f"  📌 {start}{loc_str}\n     {e.get('subject','')}")
    return events

def check_emails_relatorios(token, user):
    """Busca emails sobre relatórios pendentes"""
    alertas = []
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    keywords = ["relatório", "relatorio", "report", "entrega", "pendente", "pending"]
    
    for kw in keywords[:2]:  # Limitar buscas
        path = f"/users/{user}/messages?$search=\"{kw}\"&$top=5&$select=subject,from,receivedDateTime,isRead"
        data = graph(token, path)
        for m in data.get("value", []):
            if not m.get("isRead"):
                sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
                alertas.append(f"  📋 {m.get('subject','')} | De: {sender}")
    return alertas

def check_cronogramas():
    """Monitora arquivos .mpp das obras ativas"""
    alertas = []
    ok = []

    configs_cache = {}

    def get_token_cached(cfg_file):
        if cfg_file not in configs_cache:
            configs_cache[cfg_file] = get_token(cfg_file)
        return configs_cache[cfg_file]

    for obra in OBRAS_ATIVAS:
        token = get_token_cached(obra["config"])
        # Buscar site
        sites = graph(token, "/sites?search=*&$select=id,name&$top=30")
        site_id = None
        for s in sites.get("value", []):
            sn = s.get("name","").lower()
            if obra["site_name"].lower() in sn or sn in obra["site_name"].lower():
                site_id = s["id"]
                break
        if not site_id:
            alertas.append(f"❌ {obra['empresa']} | {obra['nome']}: site não encontrado")
            continue
        # Buscar arquivo mais recente
        search = graph(token, f"/sites/{site_id}/drive/root/search(q='.mpp')?$select=name,lastModifiedDateTime&$top=20")
        files = [f for f in search.get("value",[]) if obra["busca"].lower() in f.get("name","").lower()]
        if not files:
            alertas.append(f"⚠️ {obra['empresa']} | {obra['nome']}: nenhum arquivo encontrado")
            continue
        latest = max(files, key=lambda x: x.get("lastModifiedDateTime",""))
        last_dt = datetime.fromisoformat(latest["lastModifiedDateTime"].replace("Z","+00:00"))
        days_ago = (datetime.now(timezone.utc) - last_dt).days
        modified = latest["lastModifiedDateTime"][:10]
        if days_ago > 10:
            status = "🔴 OBRA ENCERRADA?" if days_ago > 10 else "🚨 ATRASO"
            alertas.append(f"{status} {obra['empresa']} | {obra['nome']}: {days_ago} dias sem atualização\n     Arquivo: {latest['name']} | Última edição: {modified}")
        elif days_ago > obra["alerta_dias"]:
            alertas.append(f"⚠️ {obra['empresa']} | {obra['nome']}: cronograma sem atualização há {days_ago} dias\n     Arquivo: {latest['name']} | Última edição: {modified}")
        else:
            ok.append(f"✅ {obra['empresa']} | {obra['nome']}: atualizado há {days_ago} dia(s) ({modified})")
    return alertas, ok

def coletar_dados():
    """Coleta tudo e retorna dados estruturados + relatório textual + sumário."""
    today = datetime.now().strftime("%d/%m/%Y")
    dia_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][datetime.now().weekday()]

    report_lines = [
        f"🔍 MONITOR SEMANAL — {dia_semana}, {today}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "📁 CRONOGRAMAS DE OBRA",
        "",
    ]

    crono_alertas, crono_ok = check_cronogramas()
    for item in crono_ok:
        report_lines.append(f"  {item}")
    for item in crono_alertas:
        report_lines.append(f"  {item}")
    report_lines.append("")
    report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report_lines.append("")

    emails_por_conta = {}
    eventos_por_conta = {}
    erros_por_conta = {}
    total_emails_alerta = 0

    for conta in CONTAS:
        try:
            token = get_token(conta["config"])
            report_lines.append(f"🏢 {conta['label'].upper()} ({conta['user']})")
            report_lines.append("")

            alertas_email = check_emails_urgentes(token, conta["user"], conta["label"])
            emails_por_conta[conta["label"]] = alertas_email
            total_emails_alerta += len(alertas_email)
            if alertas_email:
                report_lines.append(f"⚠️ Emails com palavras de alerta ({len(alertas_email)}):")
                report_lines.extend(alertas_email[:5])
            else:
                report_lines.append("✅ Sem emails urgentes não lidos")
            report_lines.append("")

            eventos = check_calendario_semana(token, conta["user"], conta["label"])
            eventos_por_conta[conta["label"]] = eventos
            if eventos:
                report_lines.append(f"📅 Agenda da semana ({len(eventos)} eventos):")
                report_lines.extend(eventos[:5])
            else:
                report_lines.append("📅 Sem eventos esta semana")

            report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            report_lines.append("")

        except Exception as e:
            erros_por_conta[conta["label"]] = str(e)
            report_lines.append(f"❌ Erro ao verificar {conta['label']}: {e}")
            report_lines.append("")

    total_alertas = len(crono_alertas) + total_emails_alerta
    if total_alertas > 0:
        report_lines.append(f"🚨 ATENÇÃO: {total_alertas} item(s) precisam de sua atenção")
    else:
        report_lines.append("✅ Semana sem alertas críticos detectados")
    report_lines.append("")

    report = "\n".join(report_lines)

    # Cálculo de urgency
    pg_critico = any("P&G" in a or "Louveira" in a for a in crono_alertas)
    crono_muito_atrasado = any("OBRA ENCERRADA" in a or "ATRASO" in a for a in crono_alertas)
    if pg_critico or crono_muito_atrasado:
        urgency = "high"
    elif total_alertas > 0:
        urgency = "normal"
    else:
        urgency = "low"

    summary = {
        "cronogramas": {
            "ok": len(crono_ok),
            "alertas": len(crono_alertas),
            "alertas_lista": crono_alertas,
        },
        "emails_alerta_total": total_emails_alerta,
        "emails_por_conta": {k: len(v) for k, v in emails_por_conta.items()},
        "eventos_por_conta": {k: len(v) for k, v in eventos_por_conta.items()},
        "erros_por_conta": erros_por_conta,
        "total_alertas": total_alertas,
        "pg_louveira_critico": pg_critico,
    }
    return report, summary, urgency


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Imprime relatório no stdout; não entrega à Flávia")
    parser.add_argument("--print", action="store_true",
                        help="Alias retrocompat para --skip-flavia")
    args = parser.parse_args()
    skip_flavia = args.skip_flavia or args.print

    report, summary, urgency = coletar_dados()

    if skip_flavia:
        print(report)
        return 0

    payload = {
        "source": "monitor_semanal.py",
        "kind": "monitor_semanal_consolidado",
        "project": None,
        "company": None,
        "domain": "monitoramento_executivo",
        "urgency": urgency,
        "scheduled_at": datetime.now().isoformat(),
        "summary": summary,
        "body": report,
    }
    return send_to_flavia(payload)


if __name__ == "__main__":
    sys.exit(main())
