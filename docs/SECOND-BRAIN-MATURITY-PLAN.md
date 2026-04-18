# Second Brain, plano de maturidade operacional

_Data: 2026-04-18_

## Objetivo
Transformar o OpenClaw Memory de MVP de captura/consolidação em segundo cérebro operacional, institucional e auditável.

## O salto que faltava
O gargalo do estado anterior era claro:
- capturava
- consolidava
- publicava
- mas ainda dependia de promoção manual para virar memória útil de verdade

Isso impedia maturidade.

## O que foi implantado agora

### 1. Promoção institucional automática
Novo script:
- `scripts/promote_institutional_memory.py`

Função:
- ler eventos dos inboxes diários
- classificar em:
  - `decision`
  - `pending`
  - `lesson`
  - `project`
- promover automaticamente para:
  - `memory/institutional/decisions.md`
  - `memory/institutional/pending.md`
  - `memory/institutional/lessons.md`
  - `memory/institutional/projects.md`
- evitar duplicação simples por cabeçalho normalizado
- registrar índice consolidado em:
  - `memory/institutional/index.json`

### 2. Consolidação noturna agora fecha o ciclo
`nightly_consolidate.py` passou a:
- consolidar os inboxes
- executar a promoção institucional
- registrar resumo do que foi promovido

Isso elimina a principal lacuna do MVP.

## Novo modelo operacional

### Camada 1 — Captura
- `memory/inbox/YYYY-MM-DD/<agent>/events.jsonl`
- `memory/inbox/YYYY-MM-DD/<agent>/notes.md`

### Camada 2 — Consolidação
- `memory/consolidation/YYYY-MM-DD/*.md`
- `memory/consolidation/YYYY-MM-DD/summary.md`

### Camada 3 — Institucionalização
- `memory/institutional/decisions.md`
- `memory/institutional/pending.md`
- `memory/institutional/lessons.md`
- `memory/institutional/projects.md`
- `memory/institutional/index.json`

## O que isso resolve
- reduz dependência de curadoria manual diária
- transforma evento em memória reutilizável
- cria trilha mais auditável entre captura e permanência
- aproxima o sistema do papel de segundo cérebro real

## O que ainda falta para maturidade plena
1. deduplicação semântica real
2. score de relevância por evento
3. vínculo entre pessoas, projetos e decisões
4. política de retenção/arquivamento
5. promoção também a partir de saídas de ferramentas e sessões, não só inbox manual
6. camada executiva de consulta tipo "o que mudou desde X" por tema/empresa

## Leitura honesta
Agora o sistema deixa de ser apenas um repositório com resumo noturno.
Ainda não é o estado final perfeito, mas já entra na categoria de **segundo cérebro operacional de verdade**, porque:
- captura
- consolida
- promove
- versiona
- publica

## Próximo passo recomendado
A próxima fase certa é:
- integrar captura automática dos eventos mais importantes do ecossistema OpenClaw
- melhorar a qualidade da promoção com heurística melhor
- criar consultas executivas orientadas a decisão
