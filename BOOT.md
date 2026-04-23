# BOOT.md — Ponte de Startup para o 2nd-brain

_Execute mentalmente ao iniciar cada sessão_

## Sequência obrigatória

### 1. Fonte de verdade
- Boot oficial: `/root/2nd-brain/06-agents/flavia/AGENT-MAP.md`
- Memória, identidade e contexto durável vivem em `/root/2nd-brain/`
- Workspace `/root/.openclaw/workspace/` serve para scripts, skills, configs, caches e arquivos locais

### 2. Ordem mínima de leitura
- `/root/2nd-brain/01-identity/company.md`
- `/root/2nd-brain/01-identity/people.md`
- `/root/2nd-brain/01-identity/mission-values.md`
- `/root/2nd-brain/01-identity/user.md`
- `/root/2nd-brain/02-context/pending.md`
- `/root/2nd-brain/02-context/decisions.md`
- `/root/2nd-brain/02-context/lessons.md`
- `/root/2nd-brain/_system/SOUL.md`
- `/root/2nd-brain/_system/BOOT.md`
- `/root/2nd-brain/_system/HEARTBEAT.md`
- `/root/2nd-brain/06-agents/flavia/AGENT-MAP.md`
- arquivos específicos do agente indicados no AGENT-MAP

### 3. Regras de boot
- Não carregar `MEMORY.md` nem `memory/context/*.md` do workspace como fonte primária
- Não usar `memory/projects/*.md` do workspace como memória canônica
- Só consultar memória legada do workspace quando o conteúdo for local, transitório, técnico ou ainda não migrado
- Se algo precisa valer depois desta sessão, gravar no `2nd-brain`
- Em conflito entre workspace e `2nd-brain`, vence o `2nd-brain`

## Integrações ativas

| Sistema | Conta | Status |
|---------|-------|--------|
| Email | alexandre@mensuraengenharia.com.br | ✅ |
| Email | alexandre@miaengenharia.com.br | ✅ |
| Calendário | Mensura + MIA | ✅ |
| SharePoint | Mensura + MIA | ✅ |
| Telegram | @AlexAguiar22 | ✅ |
| VPS | 76.13.161.249 | ✅ |
| GitHub 2nd-brain | mensuraeng/2nd-brain (main) | ✅ |

## Scripts disponíveis (workspace)

- `scripts/msgraph_email.py` — listar, ler, enviar, mover emails
- `scripts/msgraph_calendar.py` — listar, criar, deletar eventos
- `scripts/relatorio_cursos_telegram.py` — relatório semanal de cursos (sexta 16h BRT)
- `scripts/nightly_consolidate.py` — consolidação noturna do 2nd-brain e journal
