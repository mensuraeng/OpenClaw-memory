#!/usr/bin/env python3
"""
Microsoft Graph API - Gerenciador de Calendário
Uso: msgraph_calendar.py <comando> [opções]
"""

import json, sys, os, argparse, re
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")
ACCOUNT_CONFIG_MAP = {
    "mensura": os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json"),
    "mia": os.path.expanduser("~/.openclaw/workspace/config/ms-graph-mia.json"),
    "pcs": os.path.expanduser("~/.openclaw/workspace/config/ms-graph-pcs.json"),
}

def load_config(config_path=None, account=None):
    if config_path:
        path = os.path.expanduser(config_path)
    elif account:
        key = account.strip().lower()
        if key not in ACCOUNT_CONFIG_MAP:
            raise SystemExit(f"Conta inválida: {account}. Use: {', '.join(sorted(ACCOUNT_CONFIG_MAP))}")
        path = ACCOUNT_CONFIG_MAP[key]
    else:
        path = DEFAULT_CONFIG_FILE
    with open(path) as f:
        return json.load(f)

def get_token(cfg):
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

def graph_request(token, path, method="GET", body=None):
    url = f"https://graph.microsoft.com/v1.0{path}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            if r.status in (204, 201) and not r.headers.get("Content-Length", "1") != "0":
                return {}
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"Erro {e.code}: {e.read().decode()}")
        sys.exit(1)

BRT = timezone(timedelta(hours=-3))

def parse_event_dt(dt_str, tz_str):
    """Converte dateTime retornado pela API para horário de Brasília."""
    if not dt_str:
        return ""
    # A API pode retornar com ou sem 'Z'. Normaliza para UTC.
    dt_str_clean = dt_str.rstrip('Z')
    try:
        dt = datetime.fromisoformat(dt_str_clean)
    except ValueError:
        return dt_str[:16].replace("T", " ")
    # Se o timeZone do evento já é America/Sao_Paulo, não há conversão a fazer
    # A API retorna dateTime no fuso do evento; se for UTC, converte.
    if tz_str in ("UTC", "tzone://Microsoft/Utc", ""):
        dt = dt.replace(tzinfo=timezone.utc).astimezone(BRT)
    else:
        # Já está no fuso correto (America/Sao_Paulo ou similar)
        dt = dt.replace(tzinfo=BRT)
    return dt.strftime("%Y-%m-%d %H:%M")

def list_events(token, user, days=7):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    start_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Solicita o fuso do evento junto com os dados
    path = f"/users/{user}/calendarView?startDateTime={start_str}&endDateTime={end_str}&$orderby=start/dateTime&$select=id,subject,start,end,location,organizer,isAllDay,bodyPreview&$top=20"
    data = graph_request(token, path)
    events = data.get("value", [])
    if not events:
        print(f"Nenhum evento nos próximos {days} dias.")
        return
    print(f"📅 Próximos {days} dias ({len(events)} eventos):\n")
    for e in events:
        start_obj = e.get("start", {})
        end_obj = e.get("end", {})
        start = parse_event_dt(start_obj.get("dateTime", ""), start_obj.get("timeZone", ""))
        end_t = parse_event_dt(end_obj.get("dateTime", ""), end_obj.get("timeZone", ""))
        loc = e.get("location", {}).get("displayName", "")
        org = e.get("organizer", {}).get("emailAddress", {}).get("name", "")
        all_day = " (dia inteiro)" if e.get("isAllDay") else ""
        print(f"📌 {e.get('subject','(sem título)')}{all_day}")
        print(f"   ⏰ {start} → {end_t}")
        if loc: print(f"   📍 {loc}")
        if org: print(f"   👤 {org}")
        print(f"   🔑 {e['id'][:20]}...")
        print()

def create_event(token, user, subject, start, end, location="", body="", attendees=None):
    payload = {
        "subject": subject,
        "start": {"dateTime": start, "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": end, "timeZone": "America/Sao_Paulo"},
        "body": {"contentType": "Text", "content": body},
    }
    if location:
        payload["location"] = {"displayName": location}
    if attendees:
        payload["attendees"] = [{"emailAddress": {"address": a}, "type": "required"} for a in attendees.split(",")]
    result = graph_request(token, f"/users/{user}/events", method="POST", body=payload)
    print(f"✅ Evento criado: {result.get('subject')} (ID: {result.get('id','')[:20]}...)")

def delete_event(token, user, event_id):
    graph_request(token, f"/users/{user}/events/{event_id}", method="DELETE")
    print(f"✅ Evento removido.")

def resolve_user(args_user, cfg):
    user = args_user or cfg.get("defaultUser")
    if not user:
        print("Erro: nenhum usuário resolvido. Defina --user ou 'defaultUser' no JSON de configuração.")
        sys.exit(1)
    return user

def main():
    p = argparse.ArgumentParser(description="Gerenciador de calendário Microsoft Graph")
    p.add_argument("cmd", choices=["list","create","delete"], help="Comando")
    p.add_argument("--account", choices=["mensura","mia","pcs"], help="Conta/config a usar")
    p.add_argument("--config", help="Caminho explícito do arquivo de configuração")
    p.add_argument("--user", help="Usuário/calendário alvo")
    p.add_argument("--days", type=int, default=7, help="Dias a listar (padrão: 7)")
    p.add_argument("--id", help="ID do evento")
    p.add_argument("--subject", help="Título do evento")
    p.add_argument("--start", help="Início (ex: 2026-04-01T09:00:00)")
    p.add_argument("--end", help="Fim (ex: 2026-04-01T10:00:00)")
    p.add_argument("--location", default="", help="Local")
    p.add_argument("--body", default="", help="Descrição")
    p.add_argument("--attendees", default="", help="Convidados (emails separados por vírgula)")
    args = p.parse_args()

    cfg = load_config(config_path=args.config, account=args.account)
    user = resolve_user(args.user, cfg)
    token = get_token(cfg)

    if args.cmd == "list":
        list_events(token, user, args.days)
    elif args.cmd == "create":
        if not all([args.subject, args.start, args.end]):
            print("--subject, --start e --end são obrigatórios"); sys.exit(1)
        create_event(token, user, args.subject, args.start, args.end, args.location, args.body, args.attendees)
    elif args.cmd == "delete":
        if not args.id: print("--id obrigatório"); sys.exit(1)
        delete_event(token, user, args.id)

if __name__ == "__main__":
    main()
