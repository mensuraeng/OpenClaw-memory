#!/usr/bin/env python3
"""
CCSP Casa 7 — Mensagem matinal para Victor Evangelista
Roda seg-sex às 8h BRT (11h UTC).
Exceção operacional desta semana: primeira cobrança no sábado às 10h BRT.

Pós-FASE 5:
1. Telegram para o Alê → REMOVIDO. Vira payload entregue à Flávia
   via send_to_flavia.py (visibilidade interna + decisão).
2. Email para o Victor → MANTIDO automático, mas via helper canônico
   msgraph_email.py. Classificado como "envio pré-autorizado" pela
   operação CCSP/MIA (destinatário/cc/cadência/template estáveis).

Flags --dry-run (não envia email) e --skip-email (só Flávia).
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
hoje = datetime.now(BRT)
dia_semana = hoje.weekday()  # 0=seg, 4=sex
dia_str = hoje.strftime("%d/%m/%Y")

SATURDAY_ONE_OFF_DATE = "2026-04-18"
SATURDAY_ONE_OFF_HOUR = 10

EMAIL_TO = "victor.evangelista@miaengenharia.com.br"
EMAIL_CC = ["alexandre@miaengenharia.com.br", "andre@miaengenharia.com.br"]
EMAIL_USER = "flavia@mensuraengenharia.com.br"
EMAIL_ACCOUNT = "mensura"

HELPER_EMAIL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "msgraph_email.py"
)

# Mapeamento dia da semana
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
dia_nome = DIAS[dia_semana]

# ============================================================
# BASE DE DADOS — atualizar semanalmente com o cronograma
# ============================================================
# Estrutura: data_iso -> lista de atividades esperadas
ATIVIDADES = {
    # ── SEMANA 1 ── 02-07/04
    "2026-04-02": [
        "1ª Onda em andamento — testes elétrica, voltagem e tomadas (Suíte 3, Suíte 2, Suíte 1)",
        "Documentar situação do baldrame com fotos + solução proposta no grupo",
        "Alinhar empresa de drenagem: início confirmado para seg 06/04",
        "Solução paliativa no baldrame: lona + brita na área sem fundação",
        "Luminárias removidas na Circulação Íntima (BRB executando rodateto)",
        "RDO do dia até 17h",
    ],
    "2026-04-03": [
        "1ª Onda: continuação elétrica Suíte 3 + Suíte 2 + Suíte 1",
        "Banho 03: checklist em andamento (27 itens, exceto pintura)",
        "Banho 02: checklist em andamento (17 itens, exceto pintura)",
        "Sala de Jantar: checklist em andamento (22 itens)",
        "Confirmar visita Mirim (drywall) para segunda 06/04 às 10h09",
        "RDO do dia até 17h",
    ],
    "2026-04-06": [
        "🔵 DRENAGEM INICIA HOJE — acompanhar mobilização da equipe",
        "Visita Mirim (drywall) 10h09 — acompanhar e registrar orçamento",
        "Iniciar elétrica Banho Casal (Banho 03) + Suíte Casal",
        "1ª Onda: checklist Suíte 3 (meta conclusão: qui 09/04)",
        "Banho 01 Crianças: checklist em andamento (17 itens)",
        "Circulação Íntima: checklist em andamento (12 itens)",
        "RDO do dia até 17h",
    ],
    "2026-04-07": [
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de exaustores para aprovação TOOLS",
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de pintura para aprovação TOOLS",
        "🔴 PRAZO CRÍTICO — Enviar mapa mini-guias + batedores da garagem",
        "🔴 Enviar orçamento de película UV",
        "🔴 Enviar 3 orçamentos gesso/drywall (Mirim + outros 2)",
        "Elétrica Banho Casal em andamento (impermeabilização seg+ter)",
        "1ª Onda: checklist Suíte 3 — DIA CRÍTICO (conclusão amanhã)",
        "RDO do dia até 17h",
    ],
    # ── SEMANA 2 ── 08-14/04
    "2026-04-08": [
        "🔴 RECOMPOSIÇÃO DO BALDRAME — DIA 1 de 2",
        "Coordenar equipe baldrame com equipe de drenagem (não interferir)",
        "Elétrica Banho Casal em andamento",
        "✅ META HOJE: Conclusão Suíte 3 (16 itens checklist)",
        "Suíte 2 Hóspede: finalizar checklist (16 itens)",
        "RDO do dia até 17h",
    ],
    "2026-04-09": [
        "🔴 RECOMPOSIÇÃO DO BALDRAME — DIA 2 (CONCLUSÃO)",
        "✅ META HOJE: Conclusão Suíte 3 confirmada",
        "✅ META HOJE: Conclusão Banho 02 (Hóspede) — 17 itens",
        "✅ META HOJE: Conclusão Suíte 1 (Crianças) — 9 itens",
        "Drenagem: execução dia 4/15",
        "RDO do dia até 17h",
    ],
    "2026-04-10": [
        "🔵 IMPERMEABILIZAÇÃO EXTERNA — DIA 1 de 2",
        "✅ META HOJE: Conclusão Banho 03 (Smaster) — 27 itens",
        "✅ META HOJE: Conclusão Suíte 2 (Hóspede) — 16 itens",
        "Dormitório 4: preparação inicial (início oficial seg 13/04)",
        "Drenagem: execução dia 5/15",
        "RDO do dia até 17h",
    ],
    "2026-04-13": [
        "🔵 IMPERMEABILIZAÇÃO EXTERNA — DIA 2 (CONCLUSÃO)",
        "Dormitório 4: início checklist (17 itens, exceto pintura)",
        "Banho 4: início checklist (15 itens, exceto pintura)",
        "Cozinha: início checklist (22 itens, exceto pintura)",
        "Área de Serviço: início checklist (27 itens)",
        "Cozinha/Circulação: início (5 itens)",
        "Acompanhar aprovação TOOLS: exaustores, pintura, mini-guia, batedor, película",
        "Drenagem: execução dia 8/15",
        "RDO do dia até 17h",
    ],
    "2026-04-14": [
        "✅ META HOJE: Conclusão Banho 01 (Crianças) — 17 itens",
        "✅ META HOJE: Conclusão Circulação Íntima — 12 itens",
        "🔵 RODAPÉ ÁREA EXTERNA — DIA 1 de 2",
        "Pintura — MOBILIZAÇÃO DIA 1: contratar e alinhar empresa",
        "Limpeza geral — MOBILIZAÇÃO DIA 1",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 9/15",
        "RDO do dia até 17h",
    ],
    # ── SEMANA 3 ── 15-22/04
    "2026-04-15": [
        "🔵 RODAPÉ ÁREA EXTERNA — DIA 2 (CONCLUSÃO)",
        "✅ META HOJE: Área externa concluída (baldrame + impermeabilização + rodapé)",
        "Pintura — mobilização DIA 2",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 10/15",
        "RDO do dia até 17h",
    ],
    "2026-04-16": [
        "✅ META HOJE: Instalação dos exaustores mecânicos",
        "Limpeza especializada de pedras — DIA 1 (duração: 10 dias)",
        "Pintura — mobilização DIA 3 (CONCLUSÃO mobilização)",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 11/15",
        "RDO do dia até 17h",
    ],
    "2026-04-17": [
        "✅ META HOJE: Conclusão Dormitório 4 (17 itens)",
        "✅ META HOJE: Conclusão Banho 4 (15 itens)",
        "✅ META HOJE: Conclusão Cozinha (22 itens)",
        "✅ META HOJE: Conclusão Área de Serviço (27 itens)",
        "✅ META HOJE: Conclusão Cozinha/Circulação (5 itens)",
        "Confirmar pintura mobilizada para segunda 20/04",
        "Drenagem: execução dia 12/15",
        "RDO do dia até 17h",
    ],
    "2026-04-20": [
        "🔴 PINTURA GERAL INICIA HOJE — MARCO CRÍTICO SEM FOLGA",
        "✅ Proteção das escadas com cantoneiras concluída conforme ata",
        "Inspecionar umidade do quarto das crianças: retirar rodapé e avaliar impermeabilização",
        "Remarcar posição de saída dos exaustores dos banheiros",
        "Cobrar orçamentos da mureta (mesma pedra) e do acesso lateral com Enéias",
        "Executar ajuste dos toalheiros: subir 50 cm + compra modelos 220V",
        "Confirmar check-list atualizado ao fim do dia",
        "RDO do dia até 17h — obrigatório, sem exceção",
    ],
    "2026-04-21": [
        "Pintura geral em andamento — DIA 2",
        "Cobrar retorno formal da inspeção de umidade no quarto das crianças",
        "Confirmar definição executiva dos exaustores após remarcação",
        "Cobrar andamento dos orçamentos da mureta e do acesso lateral",
        "Registrar itens concluídos no check-list antes do fim do dia",
        "RDO do dia até 17h — obrigatório, sem exceção",
    ],
    "2026-04-22": [
        "Pintura geral em andamento — DIA 3",
        "✅ Proteção das escadas com cantoneiras já concluída — manter registrado no check-list",
        "Fechar compra/execução dos toalheiros 220V",
        "Validar seixo ao redor da casa e avanço da frente externa",
        "Registrar itens concluídos no check-list antes do fim do dia",
        "RDO do dia até 17h — obrigatório, sem exceção",
    ],
    # ── SEMANA 4 ── 23-30/04
    "2026-04-23": [
        "Pintura geral em andamento — DIA 4",
        "Limpeza geral — MOBILIZAÇÃO DIA 1 (5 dias: 23-30/04)",
        "Paisagismo: início (15 dias: 27/04-18/05)",
        "Pedras: preparação início (27/04)",
        "RDO do dia até 17h",
    ],
    "2026-04-27": [
        "Pintura geral em andamento — DIA 6",
        "Pedras: início (10 dias: 27/04-11/05)",
        "Paisagismo: início execução",
        "Limpeza geral: mobilização DIA 3",
        "Limpeza especializada de pedras: conclusão (dia 10/10)",
        "RDO do dia até 17h",
    ],
    # ── SEMANA 5-6 ── 04-15/05
    "2026-05-04": [
        "Pintura geral em andamento — DIA 11",
        "Limpeza interna: início (10 dias: 04-15/05)",
        "Paisagismo: execução em andamento",
        "Pedras: execução em andamento",
        "RDO do dia até 17h",
    ],
    "2026-05-08": [
        "Pintura geral em andamento — DIA 13",
        "✅ META HOJE: Conclusão Garagem + Área Externa completa",
        "Limpeza interna em andamento",
        "Pedras: andamento",
        "RDO do dia até 17h",
    ],
    "2026-05-11": [
        "Pintura geral em andamento — DIA 16",
        "✅ META HOJE: Conclusão Pedras",
        "Chuveirão: instalação hoje (1 dia)",
        "Limpeza externa: início (5 dias: 11-15/05)",
        "RDO do dia até 17h",
    ],
    "2026-05-15": [
        "✅ META HOJE: Conclusão Pintura Geral (interna + externa) — DIA 19",
        "✅ META HOJE: Conclusão Limpeza Interna",
        "✅ META HOJE: Conclusão Limpeza Externa",
        "Paisagismo: conclusão",
        "Preparar para comissionamento — início segunda 18/05",
        "RDO do dia até 17h",
    ],
    # ── SEMANA FINAL ── 18-22/05
    "2026-05-18": [
        "🔵 COMISSIONAMENTO — DIA 1 (5 dias: 18-22/05)",
        "Verificação geral de todos os sistemas: elétrica, hidráulica, exaustores",
        "Checklist final: início item por item",
        "RDO do dia até 17h",
    ],
    "2026-05-22": [
        "🏁 ENTREGA DA OBRA — CONCLUSÃO CHECKLIST FINAL",
        "Todos os itens revisados e assinados",
        "As-built documentado",
        "RDO final entregue",
    ],
}

# Prazos críticos — alerta adicional no rodapé da mensagem
PRAZOS_CRITICOS = {
    "2026-04-07": "🔴 HOJE é o prazo final para envio dos 5 mapas/orçamentos ao TOOLS",
    "2026-04-09": "🔴 HOJE: conclusão obrigatória da Suíte 3",
    "2026-04-10": "🟡 HOJE: conclusão Banho 03, Suíte 2, Banho 02, Suíte 1",
    "2026-04-14": "🟡 HOJE: conclusão Banho 01 + Circulação Íntima",
    "2026-04-15": "🟡 HOJE: área externa deve estar concluída",
    "2026-04-16": "🔴 HOJE: exaustores devem ser instalados",
    "2026-04-17": "🟡 HOJE: conclusão 2ª onda completa",
    "2026-04-20": "🔴 HOJE: pintura inicia junto com checklist diário e RDO até 17h, sem folga no cronograma",
    "2026-04-21": "🔴 HOJE: cobrar retorno formal da umidade do quarto das crianças e definição dos exaustores",
    "2026-04-22": "🟡 HOJE: validar cantoneiras, toalheiros 220V e avanço externo sem perder disciplina diária",
    "2026-05-08": "🟡 HOJE: conclusão garagem + área externa completa",
    "2026-05-15": "🔴 HOJE: pintura + limpeza devem estar concluídas",
    "2026-05-22": "🏁 HOJE: ENTREGA DA OBRA",
}

# ============================================================
def gerar_mensagem():
    hoje_iso = hoje.strftime("%Y-%m-%d")
    
    atividades = ATIVIDADES.get(hoje_iso, [
        "Executar checklists dos ambientes em andamento conforme cronograma",
        "Registrar avanço físico com fotos por ambiente",
        "Documentar qualquer não conformidade ou imprevisto no grupo",
        "Confirmar insumos e materiais necessários para amanhã",
        "RDO do dia até 17h",
    ])
    
    prazo_critico = PRAZOS_CRITICOS.get(hoje_iso, "")
    
    lista = "\n".join(f"  • {a}" for a in atividades)
    
    msg = f"""*📋 CCSP Casa 7 — {dia_nome}, {dia_str}*

Bom dia, Victor! Segue o alinhamento do dia:

*Atividades previstas:*
{lista}

*Lembretes permanentes:*
  • RDO diário até 17h — obrigatório
  • Documentar todas as não conformidades com foto no grupo
  • Qualquer imprevisto ou desvio de prazo → comunicar imediatamente

{"⚠️ " + prazo_critico if prazo_critico else ""}

_Qualquer dúvida ou impedimento, avise logo cedo._
_Flávia | MIA Engenharia 🟢_"""
    
    return msg.strip()

# ============================================================
# Conversão markdown → texto plano para o email
# ============================================================
def to_plain_email(markdown_text: str) -> str:
    """Limpa markdown leve para o corpo do email (texto plano)."""
    return markdown_text.replace("*", "").replace("_", "")


# ============================================================
# Email pré-autorizado via helper canônico msgraph_email.py
# ============================================================
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
        sys.stderr.write(r.stdout)  # log do helper para stderr (stdout = resposta Flávia)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode


def dentro_da_janela_permitida() -> bool:
    hoje_iso = hoje.strftime("%Y-%m-%d")
    if dia_semana <= 4:
        return True
    if hoje_iso == SATURDAY_ONE_OFF_DATE and hoje.hour >= SATURDAY_ONE_OFF_HOUR:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra email no stderr; não envia")
    parser.add_argument("--skip-email", action="store_true",
                        help="Só envia payload para Flávia; não tenta email")
    args = parser.parse_args()

    if not dentro_da_janela_permitida():
        print("Fora da janela permitida para envio desta rotina.", file=sys.stderr)
        return 0

    msg_markdown = gerar_mensagem()

    payload = {
        "source": "ccsp_manha_victor.py",
        "kind": "alinhamento_matinal",
        "project": "CCSP Casa 7",
        "company": "MIA",
        "urgency": "normal",
        "scheduled_at": hoje.isoformat(),
        "dia_semana": dia_nome,
        "body": msg_markdown,
        "external_action": {
            "kind": "email",
            "policy": "pre_authorized_routine",
            "to": EMAIL_TO,
            "cc": EMAIL_CC,
            "from": EMAIL_USER,
            "subject_template": "CCSP Casa 7 — Alinhamento do Dia | {dia}",
            "dry_run": args.dry_run,
            "skipped": args.skip_email,
        },
    }
    rc_flavia = send_to_flavia(payload)

    if args.skip_email:
        return rc_flavia

    subject = f"CCSP Casa 7 — Alinhamento do Dia | {dia_str}"
    corpo_email = to_plain_email(msg_markdown)
    rc_email = enviar_email_pre_autorizado(corpo_email, subject, args.dry_run)

    return max(rc_flavia, rc_email)


if __name__ == "__main__":
    sys.exit(main())
