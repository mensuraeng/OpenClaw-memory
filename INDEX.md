# INDEX  OpenClaw Workspace

> Mapa de navegao rpida. Atualizado: 2026-04-23.

## Fonte de Verdade: 2nd-brain
- `/root/2nd-brain/` — memória institucional e identidade (source of truth)
- GitHub: mensuraeng/2nd-brain (main)

## Identidade (2nd-brain)
- `/root/2nd-brain/_system/SOUL.md`  Identidade, tom, vibe e guardrails
- `/root/2nd-brain/_system/BOOT.md`  Protocolo de boot
- `/root/2nd-brain/01-identity/mission-values.md`  Misso e valores
- `/root/2nd-brain/06-agents/flavia/AGENT-MAP.md`  Boot e guia operacional Flvia

## Contexto Operacional (2nd-brain)
- `/root/2nd-brain/02-context/pending.md`  Tarefas ativas
- `/root/2nd-brain/02-context/decisions.md`  Decises
- `/root/2nd-brain/02-context/lessons.md`  Aprendizados
- `/root/2nd-brain/01-identity/people.md`  Pessoas

## Dirios
- `/root/2nd-brain/05-journal/2026/YYYY-MM-DD.md`

## Workspace (scripts, skills, config)
- `AGENTS.md`  Regras operacionais da Flvia (aponta para 2nd-brain)
- `scripts/`  Automações e integrações
- `agents/`  Configs locais dos subagentes
- `memory/feedback/`  Registro de aprovações/rejeições do Al (local)
- `memory/context/credentials.md`  Credenciais (local, nunca commitado)

## Sync
- 2nd-brain: a cada 2h via cron → mensuraeng/2nd-brain
- Workspace: a cada 2h via /root/openclaw-git-sync.sh → mensuraeng/OpenClaw-memory
- Consolidate: 22h via nightly_consolidate.py
