---
name: mensura-autopilot
description: Use when creating or operating a proactive project-monitoring agent for construction portfolios, especially daily executive checklists, silence detection, risk alerts, and 7am progress summaries for MENSURA, MIA, or PCS projects.
---

# Mensura Autopilot

Skill para operar um agente proativo de acompanhamento de obras com foco em governança executiva, detecção de risco e relatórios objetivos.

## Quando usar
Use esta skill quando a demanda envolver:
- monitoramento diário de obras ou carteira de projetos
- checklist executivo recorrente
- detecção de silêncio operacional
- consolidação de alertas por obra
- relatório matinal de status
- desenho ou ajuste de automação proativa para MENSURA, MIA ou PCS

## Objetivo
Transformar acompanhamento reativo em rotina proativa, com:
- leitura curta do portfólio
- alertas acionáveis
- critérios de escalonamento
- cadência operacional clara

## Regras operacionais
- Priorizar objetividade, não volume de texto.
- Relatório diário deve caber em leitura rápida de fundador/direção.
- Alerta sem ação recomendada é incompleto.
- Não enviar comunicação externa sem confirmação explícita do Alê.
- Para agendamentos recorrentes, usar cron.
- Se precisar desenhar regras, formatos ou critérios, leia as referências desta skill.

## Estrutura da skill
Leia conforme a necessidade:
- `references/architecture.md` para arquitetura operacional do autopilot
- `references/checklists.md` para checklist diário e gatilhos de alerta
- `references/report-template.md` para formato do relatório 7h
- `references/rollout-plan.md` para implantação em fases
- `references/ccsp-casa7-relatorio.md` quando o pedido for `Relatório CCSP - Casa 7` ou quando for necessário consolidar cronograma + ata + deliberações no padrão executivo MIA dessa obra
- `references/pg-louveira-relatorio-semanal.md` quando o pedido for `Relatório P&G`, `Relatório semanal P&G` ou relatório executivo da obra P&G no padrão MENSURA

## Entregáveis típicos
- desenho do autopilot por empresa ou portfólio
- checklist operacional por obra
- regras de alerta e priorização
- cronograma de execução recorrente
- relatório executivo padronizado
- relatório `CCSP - Casa 7` no padrão executivo MIA, consolidando cronograma, ata e deliberações
- relatório semanal `P&G Louveira` no padrão executivo MENSURA, consolidando cronograma, riscos, look ahead, fornecedores críticos e plano de ação
- plano de rollout com guardrails

## Guardrails
- Não transformar heartbeat em spam.
- Não monitorar sem critério explícito de relevância.
- Não sofisticar antes de existir checklist mínimo confiável.
- Não misturar rotina de obra, rotina comercial e rotina institucional no mesmo loop sem separação clara.
