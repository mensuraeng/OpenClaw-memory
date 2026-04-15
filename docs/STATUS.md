# Status — OpenClaw Memory

_Atualizado em 2026-04-14_

## O que já está consolidado

### Base do projeto
- repositório publicado em `mensuraeng/OpenClaw-memory`
- branch principal `main`
- autenticação SSH funcional para este host

### Estrutura inicial
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/OPERACAO-NOTURNA.md`
- `docs/CAPTURA-AUTOMATICA.md`
- `memory/inbox/`
- `memory/consolidation/`
- `templates/`
- `scripts/`

### Rotinas implantadas
- bootstrap diário de inbox por agente
- captura mínima em `notes.md` + `events.jsonl`
- consolidação noturna por agente
- resumo mestre por rodada
- cron diária de consolidação com push para o GitHub

## Componentes ativos

### Scripts
- `scripts/bootstrap_openclaw_memory.sh`
- `scripts/capture_event.py`
- `scripts/nightly_consolidate.py`

### Templates
- `templates/inbox-notes.md`
- `templates/consolidation-summary.md`
- `templates/event-example.json`

## Cron ativa
- `openclaw-memory-nightly-consolidation`
- horário: `22:10`
- timezone: `America/Sao_Paulo`
- frequência: `segunda a sábado`
- modelo: `openai/gpt-4o-mini`

## Fluxo consolidado atual

### Durante o dia
1. cada agente pode registrar contexto no inbox diário
2. eventos estruturados entram em `events.jsonl`
3. contexto legível entra também em `notes.md`

### À noite
1. a cron roda o consolidator
2. gera resumos por agente
3. gera resumo mestre da rodada
4. commit e push no repositório
5. silêncio por padrão se tudo correr bem

## Limites atuais
- ainda não há promoção automática para memória institucional transversal
- ainda não há deduplicação semântica entre agentes
- ainda não há classificação automática por decisão, lição e pendência
- a captura ainda precisa ser ligada aos fluxos reais do ecossistema OpenClaw

## Próximas evoluções naturais
1. protocolo de captura automática por tipo de evento
2. promoção automática para memória institucional
3. cruzamento multiagente
4. redução de ruído antes do push final
