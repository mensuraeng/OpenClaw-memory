#!/usr/bin/env python3
"""
Relatório semanal de cursos — Construção Civil
Roda toda sexta às 16h BRT (cron 0 19 * * 5).

Pós-FASE 5: NÃO fala mais com Telegram.
Gera o relatório (curadoria) e entrega como payload à Flávia,
que decide a saída final (resumir, consolidar com prioridades,
mostrar no DM, registrar etc.).

Domínio: formação profissional / cursos. Sem agente especializado
correspondente — Flávia resolve direta.

Flag --skip-flavia: imprime o relatório no stdout sem entregar.
"""

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402


def generate_report(search_results=None) -> str:
    today = datetime.now().strftime("%d/%m/%Y")

    report = f"""📚 RELATÓRIO SEMANAL — CURSOS CONSTRUÇÃO CIVIL
📅 {today} | Curadoria por James

Foco: cursos curtos, workshops, treinamentos, certificações e eventos.
Excluídos: MBAs, pós-graduações e formações de longa duração.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TOP 5 OPORTUNIDADES DA SEMANA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ POWER BI PARA CONSTRUÇÃO CIVIL
📌 Instituição: EngenhaBIM
📋 Categoria: Curso técnico online
🎯 Tema: Power BI aplicado a obras — KPIs, dashboards, planejamento, orçamento
💻 Formato: Online (acesso por 1 ano)
🔗 engenhabim.com/curso/powerbi
👥 Para: Engenheiros e gestores que querem dashboards e indicadores em obras

✅ Por que vale:
100% focado em construção civil. Usa dados reais de obras, integra com Revit/BIM. Cobre planejamento, orçamento e controle visual. Curta duração, alto impacto imediato no dia a dia.
⚠️ Verificar preço atual — oferta por tempo limitado mencionada no site.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ LEAN CONSTRUCTION COM ÊNFASE EM LPS (Last Planner System)
📌 Instituição: HIGESTOR
📋 Categoria: Curso / Treinamento
🎯 Tema: Lean Construction + Last Planner System — teoria e prática
💻 Formato: Online
🔗 app.higestor.com.br/inscricao/16012/05-lean-construction-com-enfase-em-lps-n-a
👥 Para: Engenheiros, coordenadores e planejadores de obras

✅ Por que vale:
Abordagem prática e teórica do LPS — método mais eficaz para controle de obras no Brasil. Curta duração. Aplicável diretamente no canteiro na semana seguinte ao treinamento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ CURSOS GRATUITOS CONSTRUÇÃO CIVIL — MEC / INSTITUTOS FEDERAIS
📌 Instituição: MEC + Institutos Federais
📋 Categoria: Qualificação técnica (certificação)
🎯 Tema: Construção Civil e Engenharia — temas variados
💻 Formato: Online, 100% gratuito
⏱ Carga horária: 20h por módulo (certificado incluído)
🔗 conectaprofessores.com/cursos-gratuitos-construcao-civil
👥 Para: Profissionais buscando certificações rápidas sem custo

✅ Por que vale:
Custo zero, certificado oficial. Ideal para complementar o currículo com qualificações rápidas e pontuais.
⚠️ Conteúdo pode ser introdutório — verificar temas disponíveis antes de se inscrever.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ WORKSHOP / TREINAMENTOS SENAI-SP
📌 Instituição: SENAI-SP
📋 Categoria: Treinamento técnico / Workshop
🎯 Tema: Gestão de obras, qualidade, NRs, produtividade
💻 Formato: Online e presencial (SP)
🔗 sp.senai.br/construcao-civil
👥 Para: Engenheiros, mestres de obra, coordenadores técnicos

✅ Por que vale:
SENAI tem programação contínua de treinamentos curtos e altamente práticos. Verificar agenda semanal — sempre há novidades em gestão de obras, NRs e qualidade.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ EVENTOS E TREINAMENTOS SINDUSCON-SP
📌 Instituição: SindusCon-SP
📋 Categoria: Eventos, workshops, palestras
🎯 Tema: Mercado, normas, gestão, inovação na construção civil
💻 Formato: Presencial e online (São Paulo)
🔗 sindusconsp.com.br/cursos
👥 Para: Profissionais e executivos da construção civil

✅ Por que vale:
Maior entidade setorial de SP — programação atualizada com o que há de mais relevante no mercado. Networking de alto nível. Verificar agenda semanal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FECHAMENTO DA SEMANA

⭐ Top 3 recomendações:
1. Power BI para Construção Civil (EngenhaBIM)
2. Lean Construction + LPS (HIGESTOR)
3. Treinamentos SENAI-SP (verificar agenda)

⚡ Melhor opção de curto prazo:
Power BI EngenhaBIM — inscrição imediata, resultado visível em semanas

🚀 Melhor ganho estratégico:
Lean Construction + LPS — diferencial competitivo direto na gestão de obras

💰 Melhor custo-benefício:
Cursos gratuitos MEC/IFs — certificação sem custo

⏸ Atenção, mas não urgente:
SindusCon e SENAI — acompanhar a programação semanal; surgem boas oportunidades pontuais

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤝 James — seu assistente de inteligência profissional"""

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Imprime o relatório no stdout; não entrega à Flávia")
    args = parser.parse_args()

    today = datetime.now().strftime("%d/%m/%Y")
    report = generate_report({})

    if args.skip_flavia:
        print(report)
        return 0

    payload = {
        "source": "relatorio_cursos_telegram.py",
        "kind": "relatorio_semanal_cursos",
        "project": None,
        "company": None,
        "domain": "formacao_profissional",
        "urgency": "low",
        "scheduled_at": datetime.now().isoformat(),
        "body": report,
    }
    return send_to_flavia(payload)


if __name__ == "__main__":
    sys.exit(main())
