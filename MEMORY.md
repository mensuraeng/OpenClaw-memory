# MEMORY.md — Ponte local para o 2nd-brain

_Atualizado em 2026-04-23_

## Função deste arquivo

Este arquivo não é mais a fonte primária de memória operacional da Flávia.
Ele existe como **ponte local**, para orientar humanos e automações legadas durante a transição.

## Fonte de verdade atual

Toda memória institucional e operacional durável passa a viver em:
- `/root/2nd-brain/01-identity/`
- `/root/2nd-brain/02-context/`
- `/root/2nd-brain/03-knowledge/`
- `/root/2nd-brain/04-projects/`
- `/root/2nd-brain/05-journal/`
- `/root/2nd-brain/06-agents/flavia/`
- `/root/2nd-brain/_system/`

## Regras operacionais

- Antes de responder sobre pessoas, preferências, decisões, pendências, projetos ou histórico, buscar primeiro no `2nd-brain`
- `MEMORY.md` do workspace não deve mais competir com `pending.md`, `decisions.md` e `lessons.md` do `2nd-brain`
- `memory/context/*.md` e `memory/projects/*.md` do workspace são legados, exceto quando servirem como material local ainda não migrado ou armazenamento não versionável no `2nd-brain`
- Credenciais locais continuam fora do `2nd-brain`, em caminhos locais do workspace quando necessário

## Onde procurar agora

### Identidade e contexto executivo
- `/root/2nd-brain/06-agents/flavia/AGENT-MAP.md`
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

### Memória específica da Flávia
- `/root/2nd-brain/06-agents/flavia/pending.md`
- `/root/2nd-brain/06-agents/flavia/decisions.md`
- `/root/2nd-brain/06-agents/flavia/lessons.md`
- `/root/2nd-brain/06-agents/flavia/urgent_notifications.md`
- `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md`

### Exceções locais no workspace
- `memory/feedback/` → feedback do Alê
- `memory/context/credentials.md` → credenciais locais não commitáveis
- `scripts/`, `agents/`, `finance/`, `projects/` → código, integrações, testes e operação técnica

## Estado da migração

- Fonte de verdade: migrada para `2nd-brain`
- Boot operacional: deve seguir `AGENT-MAP.md`
- Heartbeat: deve consultar e promover contexto no `2nd-brain`
- Workspace: mantido como camada técnica/local

## Próxima regra simples

Se algo precisa continuar existindo amanhã, gravar no `2nd-brain`.
