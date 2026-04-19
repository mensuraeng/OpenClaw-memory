# Rollout plan - Mensura Autopilot

## Fase 1 - desenho operacional
Objetivo: consolidar critério antes de automação.

Entregas:
- lista de obras monitoradas
- checklist diário validado
- template do relatório 7h
- regra de alertas
- definição de fontes de entrada

## Fase 2 - operação assistida
Objetivo: rodar o autopilot com intervenção humana.

Entregas:
- rotina diária controlada
- ajustes de priorização
- revisão de ruído vs sinal
- consolidação de memória por obra

## Fase 3 - automação recorrente
Objetivo: transformar em rotina previsível.

Entregas:
- cron 7h BRT
- geração automática do resumo
- alertas extraordinários sob regra estrita

## Fase 4 - evolução preditiva
Objetivo: aprender padrões por obra e por tipo de risco.

Entregas:
- histórico de recorrência
- padrões de atraso
- padrões de silêncio operacional
- critérios melhores de escalonamento

## Guardrails do rollout
- não automatizar antes de validar checklist
- não escalar para mais obras sem reduzir ruído
- não gerar relatório diário se a fonte estiver pobre demais
- não confundir frequência com inteligência
