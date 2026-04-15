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
3. consolidator noturno processa o dia
4. memória institucional é promovida
5. no dia seguinte, os agentes começam com contexto coletivo atualizado

## Status

Projeto inicial em implantação.
