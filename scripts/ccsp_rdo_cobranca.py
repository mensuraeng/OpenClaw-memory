#!/usr/bin/env python3
"""
CCSP Casa 7 — Cobrança RDO seg-sex 16:30 BRT (cron 30 19 * * 1-5).

Dois fluxos pós-FASE 5:

1. Telegram para o Alê → REMOVIDO. Vira payload entregue à Flávia
   via send_to_flavia.py. Ela consolida e decide o que fazer com a
   visibilidade interna (mostrar no DM, escrever em log, alertar etc.).

2. Email para o Victor → MANTIDO automático, mas via helper canônico
   msgraph_email.py em vez de chamar a Graph API direto. Esta rotina
   é classificada como "envio pré-autorizado" pela operação CCSP/MIA:
   - destinatário fixo (victor.evangelista@miaengenharia.com.br)
   - cc fixo (alexandre@, andre@miaengenharia.com.br)
   - cadência fixa (seg-sex 16:30 BRT)
   - corpo gerado por template estável (gerar_mensagem_rdo)
   A Flávia recebe o payload em paralelo e pode interromper a rotina
   se identificar problema (interrupção entra em vigor no próximo dia útil).

Flag --dry-run: gera payload e mostra email no stdout sem enviar.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

# permite import do helper send_to_flavia.py do mesmo diretório
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

BRT = timezone(timedelta(hours=-3))

EMAIL_TO = "victor.evangelista@miaengenharia.com.br"
EMAIL_CC = ["alexandre@miaengenharia.com.br", "andre@miaengenharia.com.br"]
EMAIL_USER = "flavia@mensuraengenharia.com.br"
EMAIL_ACCOUNT = "mensura"  # usa ~/.openclaw/workspace/config/ms-graph.json

HELPER_EMAIL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "msgraph_email.py"
)


def gerar_mensagem_rdo(dia_str: str) -> str:
    return f"""⏰ *CCSP Casa 7 — Cobrança RDO | {dia_str}*

Victor, o RDO de hoje ({dia_str}) ainda não foi enviado ou precisa ser conferido.

*Checklist rápido para fechar o dia:*
  ✅ RDO preenchido (mesmo que parcial)
  ✅ Fotos do avanço do dia anexadas
  ✅ Não conformidades registradas com descrição
  ✅ Pendências do dia documentadas no grupo
  ✅ Insumos/materiais que faltam para amanhã levantados

Enviar antes de sair da obra.

_Flávia | MIA Engenharia 🟢_"""


def to_plain_email(markdown_text: str) -> str:
    """Remove marcações leves de markdown para o corpo do email."""
    return markdown_text.replace("*", "").replace("_", "")


def enviar_email_pre_autorizado(corpo: str, subject: str, dry_run: bool) -> int:
    """Chama msgraph_email.py como helper canônico de envio."""
    if dry_run:
        print("--- [DRY RUN] Email NÃO enviado ---", file=sys.stderr)
        print(f"to:      {EMAIL_TO}", file=sys.stderr)
        print(f"cc:      {', '.join(EMAIL_CC)}", file=sys.stderr)
        print(f"user:    {EMAIL_USER}", file=sys.stderr)
        print(f"subject: {subject}", file=sys.stderr)
        print("--- corpo ---", file=sys.stderr)
        print(corpo, file=sys.stderr)
        print("--- fim ---", file=sys.stderr)
        return 0
    cmd = [
        "python3", HELPER_EMAIL, "send",
        "--account", EMAIL_ACCOUNT,
        "--user", EMAIL_USER,
        "--to", EMAIL_TO,
        "--subject", subject,
        "--body", corpo,
    ]
    for c in EMAIL_CC:
        cmd += ["--cc", c]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("Timeout no envio de email pelo helper", file=sys.stderr)
        return 1
    if r.stdout:
        sys.stderr.write(r.stdout)  # log do helper para stderr (stdout = resposta Flávia)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Gera payload e mostra email no stderr; não envia")
    parser.add_argument("--skip-email", action="store_true",
                        help="Só envia payload para Flávia; não tenta email")
    args = parser.parse_args()

    hoje = datetime.now(BRT)
    dia_str = hoje.strftime("%d/%m/%Y")
    msg_markdown = gerar_mensagem_rdo(dia_str)

    payload = {
        "source": "ccsp_rdo_cobranca.py",
        "kind": "cobranca_rdo_diaria",
        "project": "CCSP Casa 7",
        "company": "MIA",
        "urgency": "normal",
        "scheduled_at": hoje.isoformat(),
        "body": msg_markdown,
        "external_action": {
            "kind": "email",
            "policy": "pre_authorized_routine",
            "to": EMAIL_TO,
            "cc": EMAIL_CC,
            "from": EMAIL_USER,
            "subject_template": "CCSP Casa 7 — RDO Pendente | {dia}",
            "dry_run": args.dry_run,
            "skipped": args.skip_email,
        },
    }
    rc_flavia = send_to_flavia(payload)

    if args.skip_email:
        return rc_flavia

    subject = f"CCSP Casa 7 — RDO Pendente | {dia_str}"
    corpo_email = to_plain_email(msg_markdown)
    rc_email = enviar_email_pre_autorizado(corpo_email, subject, args.dry_run)

    return max(rc_flavia, rc_email)


if __name__ == "__main__":
    sys.exit(main())
