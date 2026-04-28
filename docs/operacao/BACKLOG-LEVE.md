# Backlog Leve — PRD, Epic, Story e QA

_Atualizado em 2026-04-28_

## Objetivo

Transformar ideia e sinal operacional em execução rastreável, sem depender de Jira no começo.

## Estrutura

```text
runtime/operational-backlog/
├── epics/
├── stories/
├── prd/
├── qa/
├── done/
└── rejected/
```

## Fluxo

```text
sinal → PRD/epic → story → execução → QA → done/rejected
```

## Quando criar PRD

Criar PRD quando houver:
- mudança estrutural;
- automação nova;
- integração nova;
- alteração com risco;
- tarefa recorrente que precisa virar processo.

## Quando criar story simples

Criar story quando for:
- ajuste pequeno;
- melhoria isolada;
- checklist operacional;
- bug sem grande impacto.

## Critério de pronto

Nada vira `done` sem:
- evidência;
- QA proporcional;
- owner;
- rollback/contenção quando aplicável;
- memória atualizada se for decisão/lição durável.
