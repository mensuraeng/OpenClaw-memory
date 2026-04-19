# OpenClaw Memory

Memória operacional distribuída para times de agentes usando GitHub como memória institucional de longo prazo.

## Ideia central

- durante o dia, cada agente grava em memória curta
- à noite, um consolidator organiza, deduplica e promove o que importa
- o GitHub guarda a memória longa compartilhada

## Arquitetura

- `memory/inbox/` → captura bruta por agente
- `memory/consolidation/` → saídas da consolidação noturna
- `docs/` → regras, arquitetura e operação
- `scripts/` → automações de captura e consolidação
- `templates/` → modelos de arquivos de inbox e consolidação

## Fluxo

1. agentes trabalham normalmente
2. contexto útil entra no inbox
3. eventos OpenClaw de alto sinal podem ser capturados automaticamente
4. consolidator noturno processa o dia
5. memória institucional é promovida
6. consultas executivas podem ler a memória institucional consolidada
7. no dia seguinte, os agentes começam com contexto coletivo atualizado

## Scripts principais

- `scripts/capture_event.py` → captura manual/estruturada
- `scripts/capture_openclaw_event.py` → captura automática de eventos OpenClaw de alto sinal
- `scripts/nightly_consolidate.py` → consolidação noturna + promoção institucional
- `scripts/promote_institutional_memory.py` → classificação e promoção institucional
- `scripts/executive_memory_query.py` → consulta executiva inicial sobre a memória institucional
- `scripts/executive_memory_brief.py` → briefing executivo textual da memória institucional
- `scripts/import_mission_control_events.py` → importa eventos relevantes do Mission Control para o second brain

## Status

Projeto em evolução funcional, já operando como second brain com captura, consolidação, promoção e consulta inicial.
