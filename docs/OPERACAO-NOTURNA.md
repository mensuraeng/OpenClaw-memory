# Operação Noturna — OpenClaw Memory

## Objetivo

Rodar uma consolidação diária simples, previsível e auditável dos inboxes dos agentes.

## Escopo do MVP

No primeiro estágio, a consolidação noturna:
- percorre os inboxes do dia
- gera um resumo por agente
- gera um resumo mestre da rodada
- prepara material para promoção posterior à memória institucional

## O que ela ainda não faz

- deduplicação semântica avançada
- promoção automática para `decisions.md`, `lessons.md` e `pending.md`
- vínculo automático entre projetos e pessoas
- detecção inteligente de conflito multiagente

## Script

```bash
python3 scripts/nightly_consolidate.py 2026-04-14
```

Sem data explícita, usa o dia atual.

## Saídas

- `memory/consolidation/YYYY-MM-DD/summary.md`
- `memory/consolidation/YYYY-MM-DD/<agent>-summary.md`

## Estratégia

Começar simples.
Primeiro garantir:
- execução confiável
- estrutura auditável
- rotina estável

Depois sofisticar a inteligência de promoção.
