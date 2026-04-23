#!/usr/bin/env python3
"""
Assistente Financeiro — Contas a Pagar
Lê emails das contas Mensura, MIA e PCS buscando boletos, faturas e cobranças.
Cria eventos na agenda com código de barras e lembra o Alê de pagar.
"""

import json, sys, os, re, argparse
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone

CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")

CONTAS_FILE = os.path.expanduser("~/.openclaw/workspace/memory/contas_pagar.json")

USERS = [
    {
        "email": "alexandre@mensuraengenharia.com.br",
        "config": os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json"),
    },
    {
        "email": "alexandre@miaengenharia.com.br",
        "config": os.path.expanduser("~/.openclaw/workspace/config/ms-graph-mia.json"),
    },
    {
        "email": "alexandre@pcsengenharia.com.br",
        "config": os.path.expanduser("~/.openclaw/workspace/config/ms-graph-pcs.json"),
    },
]

# Palavras-chave para identificar emails financeiros (contas a PAGAR)
KEYWORDS_SUBJECT = [
    "boleto", "fatura", "cobrança", "vencimento",
    "condomínio", "condominio",
    "luz", "energia elétrica", "celular", "telefone", "internet", "água", "agua",
    "gás", "gas", "aluguel", "iptu", "ipva", "seguro", "mensalidade",
    "aviso de cobrança", "segunda via", "prazo de pagamento",
    "débito automático", "debito automatico",
]

# Assuntos a ignorar explicitamente (falsos positivos comuns)
KEYWORDS_IGNORE = [
    "documento aguarda sua assinatura",
    "pagamento pix recebido",       # pix recebido = entrada, não saída
    "pix recebido",
    "pagamento confirmado",         # confirmação = já pago
    "sua reserva para",             # confirmação de reserva já paga
    "está confirmado",
    "folha de pagamento",
    "nf-e da compra",               # nota de compra, não boleto
    "autorização de chave pix",
    "solicitação de conexão",
    "acabei de solicitar conexão",
    "windson acabou de enviar",
    "using third-party harnesses",
]

KEYWORDS_BODY = [
    r"\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14,15}",  # boleto padrão
    r"\d{47,48}",  # código de barras numérico
    r"vencimento[:\s]+\d{2}/\d{2}/\d{4}",
    r"data de vencimento",
    r"valor[:\s]+r\$\s*[\d\.,]+",
    r"pagar até",
    r"código de barras",
    r"linha digitável",
    r"pix copia e cola",
    r"chave pix",
]


def load_config():
    with open(CONFIG_FILE) as f:
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
            if r.status == 204:
                return {}
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"Erro {e.code}: {e.read().decode()}", file=sys.stderr)
        return {}


def is_financial_email(subject, body_preview):
    subject_lower = subject.lower()
    body_lower = body_preview.lower()

    # Ignorar falsos positivos explícitos
    for kw in KEYWORDS_IGNORE:
        if kw in subject_lower:
            return False

    for kw in KEYWORDS_SUBJECT:
        if kw in subject_lower:
            return True

    for pattern in KEYWORDS_BODY:
        if re.search(pattern, body_lower, re.IGNORECASE):
            return True

    return False


def extract_barcode(text):
    """Tenta extrair código de barras / linha digitável do texto."""
    patterns = [
        r"\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14,15}",
        r"\d{47,48}",
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group(0).strip()
    return None


def extract_due_date(text):
    """Tenta extrair data de vencimento do texto."""
    patterns = [
        r"vencimento[:\s]+(\d{2}/\d{2}/\d{4})",
        r"vence[:\s]+(\d{2}/\d{2}/\d{4})",
        r"pagar até[:\s]+(\d{2}/\d{2}/\d{4})",
        r"data de vencimento[:\s]+(\d{2}/\d{2}/\d{4})",
        r"(\d{2}/\d{2}/\d{4})",  # fallback: qualquer data no formato BR
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y")
            except:
                continue
    return None


def extract_value(text):
    """Tenta extrair valor monetário."""
    match = re.search(r"r\$\s*([\d\.,]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def load_contas():
    if os.path.exists(CONTAS_FILE):
        with open(CONTAS_FILE) as f:
            return json.load(f)
    return {"contas": [], "pagos": []}


def save_contas(data):
    os.makedirs(os.path.dirname(CONTAS_FILE), exist_ok=True)
    with open(CONTAS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_calendar_event(token, user, conta):
    """Cria evento de lembrete na agenda."""
    due = conta.get("vencimento")
    if not due:
        return None

    try:
        due_dt = datetime.strptime(due, "%d/%m/%Y")
    except:
        return None

    # Lembrete 2 dias antes às 9h
    reminder_dt = due_dt - timedelta(days=2)
    reminder_dt = reminder_dt.replace(hour=9, minute=0, second=0)
    reminder_end = reminder_dt + timedelta(hours=1)

    barcode = conta.get("codigo_barras", "Não identificado")
    valor = conta.get("valor", "Não identificado")
    descricao = conta.get("descricao", conta.get("assunto", "Conta"))
    conta_email = conta.get("conta", "")

    subject = f"💰 Pagar: {descricao} — vence {due}"
    body = f"""CONTA A PAGAR
━━━━━━━━━━━━━━━━━━━━━━━━━━
Descrição: {descricao}
Conta: {conta_email}
Vencimento: {due}
Valor: R$ {valor}

CÓDIGO DE BARRAS / LINHA DIGITÁVEL:
{barcode}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Após pagar, envie o comprovante para a Flávia dar baixa.
"""

    payload = {
        "subject": subject,
        "start": {"dateTime": reminder_dt.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": reminder_end.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "America/Sao_Paulo"},
        "body": {"contentType": "Text", "content": body},
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 60,
        "categories": ["Contas a Pagar"],
    }

    result = graph_request(token, f"/users/{user}/events", method="POST", body=payload)
    return result.get("id")


def fetch_financial_emails(token, user, days_back=8):
    """Busca emails financeiros dos últimos N dias."""
    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode({
        "$top": "50",
        "$filter": f"receivedDateTime ge {since}",
        "$select": "id,subject,from,receivedDateTime,bodyPreview,body",
        "$orderby": "receivedDateTime desc",
    })
    path = f"/users/{user}/mailFolders/inbox/messages?{params}"
    data = graph_request(token, path)
    return data.get("value", [])


def scan_emails(args):
    contas_data = load_contas()
    existing_ids = {c["email_id"] for c in contas_data["contas"]}

    novas_contas = []
    # Agenda Mensura como padrão para eventos
    cfg_mensura = load_config()
    token_mensura = get_token(cfg_mensura)
    calendar_user = USERS[0]["email"]

    for user_entry in USERS:
        user = user_entry["email"]
        cfg_path = user_entry["config"]

        # Carregar config específica da conta
        with open(cfg_path) as f:
            cfg = json.load(f)
        token = get_token(cfg)

        print(f"\n📬 Escaneando {user}...")
        emails = fetch_financial_emails(token, user, days_back=8)
        print(f"   {len(emails)} emails recentes encontrados")

        for email in emails:
            msg_id = email.get("id", "")
            if msg_id in existing_ids:
                continue

            subject = email.get("subject", "")
            body_preview = email.get("bodyPreview", "")

            # Buscar corpo completo para extração
            full_body = ""
            if email.get("body"):
                full_body = email["body"].get("content", "")

            combined_text = f"{subject} {body_preview} {full_body}"

            if not is_financial_email(subject, body_preview):
                continue

            print(f"\n   💡 Email financeiro encontrado: {subject[:60]}")

            barcode = extract_barcode(combined_text)
            due_date = extract_due_date(combined_text)
            value = extract_value(combined_text)
            sender = email.get("from", {}).get("emailAddress", {}).get("address", "")

            conta = {
                "id": f"{user}_{msg_id[:16]}",
                "email_id": msg_id,
                "conta": user,
                "assunto": subject,
                "descricao": subject[:80],
                "remetente": sender,
                "recebido": email.get("receivedDateTime", "")[:10],
                "vencimento": due_date.strftime("%d/%m/%Y") if due_date else None,
                "valor": value,
                "codigo_barras": barcode,
                "status": "pendente",
                "evento_id": None,
            }

            # Criar evento na agenda (sempre na conta Mensura)
            if due_date:
                event_id = create_calendar_event(token_mensura, calendar_user, conta)
                if event_id:
                    conta["evento_id"] = event_id
                    print(f"   📅 Evento criado na agenda (vence {due_date.strftime('%d/%m/%Y')})")
                else:
                    print(f"   ⚠️  Não foi possível criar evento na agenda")
            else:
                print(f"   ⚠️  Vencimento não identificado — evento não criado")

            contas_data["contas"].append(conta)
            existing_ids.add(msg_id)
            novas_contas.append(conta)

    save_contas(contas_data)

    # Relatório final
    print("\n" + "="*50)
    print(f"📊 RESUMO — CONTAS A PAGAR")
    print("="*50)

    if not novas_contas:
        print("✅ Nenhuma nova conta encontrada esta semana.")
    else:
        print(f"\n🆕 {len(novas_contas)} nova(s) conta(s) identificada(s):\n")
        for c in novas_contas:
            venc = c.get("vencimento") or "⚠️ não identificado"
            valor = c.get("valor") or "não identificado"
            barcode = c.get("codigo_barras") or "⚠️ não identificado"
            evento = "✅ na agenda" if c.get("evento_id") else "⚠️ sem evento"
            print(f"  📄 {c['descricao'][:60]}")
            print(f"     Conta: {c['conta']}")
            print(f"     Vencimento: {venc} | Valor: R$ {valor}")
            print(f"     Código de barras: {barcode[:40] if barcode else '—'}...")
            print(f"     Agenda: {evento}\n")

    # Pendentes antigas
    pendentes = [c for c in contas_data["contas"] if c.get("status") == "pendente"]
    if pendentes:
        print(f"\n⏳ Total pendente no histórico: {len(pendentes)} conta(s)")

    return novas_contas


def list_contas(args):
    contas_data = load_contas()
    pendentes = [c for c in contas_data["contas"] if c.get("status") == "pendente"]
    pagos = contas_data.get("pagos", [])

    print(f"\n💰 CONTAS A PAGAR — {len(pendentes)} pendente(s)\n")
    for c in pendentes:
        venc = c.get("vencimento") or "⚠️ sem data"
        valor = c.get("valor") or "?"
        barcode = c.get("codigo_barras") or "⚠️ não identificado"
        print(f"  [{c['id'][:12]}]")
        print(f"  📄 {c['descricao'][:60]}")
        print(f"  Vencimento: {venc} | Valor: R$ {valor}")
        print(f"  Código: {barcode[:60]}")
        print()

    print(f"✅ Pagas no histórico: {len(pagos)}")


def mark_paid(args):
    conta_id = args.id
    contas_data = load_contas()

    for i, c in enumerate(contas_data["contas"]):
        if c["id"].startswith(conta_id) or c["id"] == conta_id:
            c["status"] = "pago"
            c["pago_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            contas_data["pagos"].append(contas_data["contas"].pop(i))
            save_contas(contas_data)
            print(f"✅ Conta marcada como paga: {c['descricao'][:60]}")
            return

    print(f"❌ Conta não encontrada: {conta_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assistente Financeiro — Contas a Pagar")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("scan", help="Escanear emails buscando contas")
    sub.add_parser("list", help="Listar contas pendentes")
    paid = sub.add_parser("paid", help="Marcar conta como paga")
    paid.add_argument("id", help="ID da conta (prefixo suficiente)")

    args = parser.parse_args()

    if args.cmd == "scan":
        scan_emails(args)
    elif args.cmd == "list":
        list_contas(args)
    elif args.cmd == "paid":
        mark_paid(args)
    else:
        parser.print_help()
