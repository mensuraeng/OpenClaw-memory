#!/usr/bin/env python3
"""
CCSP Casa 7 — Cobrança RDO seg-sex 16:30 BRT (cron 30 19 * * 1-5).

Pós-FASE integração com relatorio.json:

1. Antes de gerar a mensagem, faz git pull no repo
   ~/.openclaw/workspace/knowledge/Mia-CCSP-Casa-7 (best effort —
   se falhar, segue com o snapshot local).
2. Lê src/data/relatorio.json e injeta dados frescos (semana,
   avanço, alerta crítico da semana, ações com prazo imediato/hoje)
   na mensagem que vai para o Victor.
3. Se o relatorio.json estiver com mais de 8 dias sem atualização
   (meta.data > 8 dias atrás), cai em modo degradado:
     - manda o email genérico ao Victor (sem dados frescos) com
       um aviso explícito de "relatório semanal desatualizado";
     - notifica a Flávia via send_to_flavia com urgency=high para
       que ela cobre o Alê pela atualização.

Email para o Victor: MANTIDO automático via helper canônico
msgraph_email.py (envio pré-autorizado da rotina CCSP/MIA).
Telegram para o Alê: vira payload via send_to_flavia (visibilidade
interna).

Cap do email: 25 linhas (corta ações urgentes se passar).

Flags:
  --dry-run    gera payload, mostra email no stderr, não envia
  --skip-email só envia payload à Flávia
  --no-pull    pula o git pull (útil em teste local)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

BRT = timezone(timedelta(hours=-3))

EMAIL_TO = "victor.evangelista@miaengenharia.com.br"
EMAIL_CC = ["alexandre@miaengenharia.com.br", "andre@miaengenharia.com.br"]
EMAIL_USER = "flavia@mensuraengenharia.com.br"
EMAIL_ACCOUNT = "mensura"

HELPER_EMAIL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "msgraph_email.py"
)

REPO_DIR = os.path.expanduser("~/.openclaw/workspace/knowledge/Mia-CCSP-Casa-7")
JSON_PATH = os.path.join(REPO_DIR, "src", "data", "relatorio.json")
MAX_AGE_DAYS = 8
MAX_LINHAS_EMAIL = 25

# Marcadores de prazo que disparam destaque "urgente hoje"
PRAZOS_URGENTES = {"hoje", "imediato", "urgente"}

# Checklist genérico (não muda)
CHECKLIST = [
    "✅ RDO preenchido (mesmo que parcial)",
    "✅ Fotos do avanço do dia anexadas",
    "✅ Não conformidades registradas com descrição",
    "✅ Pendências do dia documentadas no grupo",
    "✅ Insumos/materiais que faltam para amanhã levantados",
]


# =============================================================
# Leitura do relatório
# =============================================================
def git_pull(no_pull: bool) -> bool:
    """Best-effort git pull no repo do template. Retorna True se ok."""
    if no_pull:
        return True
    if not os.path.isdir(os.path.join(REPO_DIR, ".git")):
        sys.stderr.write(f"AVISO: {REPO_DIR} não é repo git; pulando pull\n")
        return False
    try:
        r = subprocess.run(
            ["git", "-C", REPO_DIR, "pull", "--ff-only"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode == 0:
            return True
        sys.stderr.write(f"AVISO git pull rc={r.returncode}: {r.stderr.strip()[:200]}\n")
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        sys.stderr.write(f"AVISO git pull falhou: {e}\n")
        return False


def carregar_relatorio() -> dict | None:
    if not os.path.exists(JSON_PATH):
        sys.stderr.write(f"AVISO: relatorio.json não existe em {JSON_PATH}\n")
        return None
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        sys.stderr.write(f"AVISO: falha lendo relatorio.json: {e}\n")
        return None


def idade_relatorio_dias(relatorio: dict, hoje: datetime) -> int | None:
    """Retorna dias desde meta.data; None se faltar / parse falhar."""
    meta = relatorio.get("meta") or {}
    data_str = meta.get("data")
    if not data_str:
        return None
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (hoje.date() - dt).days


# =============================================================
# Filtros de ações urgentes
# =============================================================
def acoes_urgentes(relatorio: dict, hoje: datetime) -> list[dict]:
    """Filtra plano_acao.acoes com prazo hoje/imediato/urgente.

    Reconhece também prazos no formato DD/MM ou DD/MM/AA que batem
    com o dia de execução."""
    acoes = (relatorio.get("plano_acao") or {}).get("acoes") or []
    dia_dd_mm = hoje.strftime("%d/%m")
    dia_dd_mm_aa = hoje.strftime("%d/%m/%y")
    out = []
    for a in acoes:
        prazo_norm = (a.get("prazo") or "").strip().lower()
        if any(m in prazo_norm for m in PRAZOS_URGENTES):
            out.append(a)
            continue
        if prazo_norm == dia_dd_mm or prazo_norm == dia_dd_mm_aa:
            out.append(a)
    # ordena: red antes de amber, depois resto
    color_rank = {"red": 0, "amber": 1}
    out.sort(key=lambda a: color_rank.get((a.get("color") or "").lower(), 9))
    return out


# =============================================================
# Geração da mensagem
# =============================================================
def gerar_mensagem_dinamica(relatorio: dict, hoje: datetime) -> str:
    """Mensagem com dados frescos do relatório semanal."""
    meta = relatorio.get("meta") or {}
    alerta = relatorio.get("alerta_critico") or {}
    dia_str = hoje.strftime("%d/%m/%Y")

    semana = meta.get("semana_label") or ""
    avanco = meta.get("avanco_global")
    avanco_str = f"{avanco}%" if avanco is not None else "?"
    prazo = meta.get("prazo_contratual_label") or ""
    duracao = meta.get("duracao_label") or ""

    linhas: list[str] = []
    linhas.append(f"⏰ *CCSP Casa 7 — Cobrança RDO | {dia_str}*")
    linhas.append("")
    linhas.append(
        f"*Status:* {semana} · Avanço {avanco_str} · Prazo {prazo} ({duracao})"
    )

    if alerta.get("titulo"):
        linhas.append("")
        linhas.append(f"⚠️ *Alerta da semana:* {alerta['titulo']}")

    urgentes = acoes_urgentes(relatorio, hoje)
    if urgentes:
        linhas.append("")
        linhas.append("*Ações com prazo HOJE / imediato:*")
        for a in urgentes:
            resp = a.get("responsavel") or "?"
            titulo = a.get("titulo") or "?"
            linhas.append(f"  • {titulo} — {resp}")

    linhas.append("")
    linhas.append(f"Victor, o RDO de hoje ({dia_str}) precisa ser enviado/conferido.")
    linhas.append("*Checklist do dia:*")
    linhas.extend(f"  {item}" for item in CHECKLIST)
    linhas.append("")
    linhas.append("Enviar antes de sair da obra.")
    linhas.append("")
    linhas.append("_Flávia | MIA Engenharia 🟢_")

    return _aplicar_cap(linhas)


def gerar_mensagem_generica(hoje: datetime, motivo: str) -> str:
    """Fallback quando não há relatório fresco."""
    dia_str = hoje.strftime("%d/%m/%Y")
    linhas = [
        f"⏰ *CCSP Casa 7 — Cobrança RDO | {dia_str}*",
        "",
        f"⚠️ *Aviso interno:* {motivo}",
        "",
        f"Victor, o RDO de hoje ({dia_str}) precisa ser enviado/conferido.",
        "*Checklist do dia:*",
    ]
    linhas.extend(f"  {item}" for item in CHECKLIST)
    linhas.append("")
    linhas.append("Enviar antes de sair da obra.")
    linhas.append("")
    linhas.append("_Flávia | MIA Engenharia 🟢_")
    return "\n".join(linhas)


def _aplicar_cap(linhas: list[str]) -> str:
    """Garante que o email não passe de MAX_LINHAS_EMAIL.

    Se passar, remove ações urgentes do meio (mantém header, alerta,
    checklist e despedida)."""
    if len(linhas) <= MAX_LINHAS_EMAIL:
        return "\n".join(linhas)
    # Estratégia: encontra o bloco de ações ("*Ações com prazo HOJE")
    # e corta linhas dele até caber.
    try:
        inicio_acoes = next(
            i for i, l in enumerate(linhas) if l.startswith("*Ações com prazo")
        )
    except StopIteration:
        # sem bloco de ações; corta do final dos checklists (improvável)
        return "\n".join(linhas[:MAX_LINHAS_EMAIL])

    # Achar o fim do bloco de ações (próxima linha vazia após ele)
    fim_acoes = inicio_acoes + 1
    while fim_acoes < len(linhas) and linhas[fim_acoes].startswith("  •"):
        fim_acoes += 1

    excedente = len(linhas) - MAX_LINHAS_EMAIL
    # Remove tantas linhas de ações quanto necessário, do fim do bloco
    # para o início, preservando pelo menos 1 ação.
    cortar = min(excedente, max(0, (fim_acoes - inicio_acoes - 2)))
    if cortar > 0:
        del linhas[fim_acoes - cortar : fim_acoes]
        # adiciona indicador de truncamento
        linhas.insert(fim_acoes - cortar, f"  • (+{cortar} ação(ões) — ver relatório completo)")
    return "\n".join(linhas[:MAX_LINHAS_EMAIL])


# =============================================================
# Email (helper canônico)
# =============================================================
def to_plain_email(markdown_text: str) -> str:
    return markdown_text.replace("*", "").replace("_", "")


def enviar_email_pre_autorizado(corpo: str, subject: str, dry_run: bool) -> int:
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
        sys.stderr.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode


# =============================================================
# main
# =============================================================
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Gera payload e mostra email no stderr; não envia")
    parser.add_argument("--skip-email", action="store_true",
                        help="Só envia payload para Flávia; não tenta email")
    parser.add_argument("--no-pull", action="store_true",
                        help="Pula o git pull do repo Mia-CCSP-Casa-7")
    args = parser.parse_args()

    hoje = datetime.now(BRT)
    dia_str = hoje.strftime("%d/%m/%Y")

    git_pull(args.no_pull)
    relatorio = carregar_relatorio()

    modo = "dinamico"
    motivo_degradado = ""
    relatorio_idade = None

    if relatorio is None:
        modo = "degradado"
        motivo_degradado = "relatorio.json não encontrado ou ilegível."
    else:
        relatorio_idade = idade_relatorio_dias(relatorio, hoje)
        if relatorio_idade is None:
            modo = "degradado"
            motivo_degradado = "relatorio.json sem meta.data válida."
        elif relatorio_idade > MAX_AGE_DAYS:
            modo = "degradado"
            motivo_degradado = (
                f"relatorio.json desatualizado há {relatorio_idade} dias "
                f"(>{MAX_AGE_DAYS}). Solicitar atualização da semana."
            )

    if modo == "dinamico":
        msg_markdown = gerar_mensagem_dinamica(relatorio, hoje)
        urgency_payload = "normal"
    else:
        msg_markdown = gerar_mensagem_generica(hoje, motivo_degradado)
        urgency_payload = "high"  # alerta para Flávia cobrar atualização

    # Payload para Flávia
    payload = {
        "source": "ccsp_rdo_cobranca.py",
        "kind": "cobranca_rdo_diaria",
        "project": "CCSP Casa 7",
        "company": "MIA",
        "urgency": urgency_payload,
        "scheduled_at": hoje.isoformat(),
        "modo": modo,
        "relatorio_idade_dias": relatorio_idade,
        "relatorio_motivo_degradado": motivo_degradado or None,
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
