# Matriz de permissões v1 do Mission Control

_Data: 2026-04-13_

## Regra-mãe

A v1 é **Tailscale-first**, com foco em **observabilidade operacional** e apenas **ações leves explicitamente allowlisted**.

Tudo que parecer:
- shell genérico
- filesystem genérico
- config bruta
- mutação ampla do host

fica fora.

---

## 1. Leitura permitida

| Domínio | Permitido na v1 | Observação |
| --- | --- | --- |
| Host summary | sim | CPU, memória, disco, uptime, status derivado |
| Agents | sim | inventário, status, contagens, metadados sanitizados |
| Sessions | sim | recentes, resumidas, sanitizadas |
| Cron | sim | lista, estado, próxima execução, último run |
| Docs | sim | somente allowlist explícita em `docs/` |
| Memory | sim | somente subset aprovado em `memory/` |
| Logs | parcial | trechos resumidos/sanitizados, não stream bruto geral |
| Config | parcial | apenas campos derivados e não sensíveis |

---

## 2. Leitura proibida

| Domínio | Bloqueio |
| --- | --- |
| Root files sensíveis | `SOUL.md`, `USER.md`, `IDENTITY.md`, `AGENTS.md`, `TOOLS.md` |
| Config bruta | `openclaw.json`, `.env`, `.env.local`, secrets e tokens |
| File browser genérico | qualquer navegação livre por workspace |
| Logs brutos irrestritos | stream contínuo e completo do host |
| Sessões brutas completas | quando houver risco de segredo/contexto excessivo |

---

## 3. Ações permitidas

| Ação | Status v1 | Condição |
| --- | --- | --- |
| Refresh manual | permitido | sem side effect externo |
| Ack de alerta | permitido | auditável |
| Abrir recurso interno | permitido | navegação interna |
| Copiar comando seguro | permitido | sem execução automática |
| Rerun seguro específico | condicional | só para jobs allowlisted |

---

## 4. Ações proibidas

| Ação | Motivo |
| --- | --- |
| Terminal web | shell remoto fora do escopo |
| Execução arbitrária | risco operacional e de exfiltração |
| Restart/stop/start amplo de serviços | alto impacto |
| Docker control amplo | alto impacto |
| Editar arquivos genericamente | persistência indevida e erro operacional |
| Upload/delete/mkdir genéricos | filesystem amplo demais |
| Alterar senha por painel | não cabe na v1 |
| Escrever `.env.local` | sensível |
| Deletar cron job | destrutivo |
| Toggle irrestrito de cron | risco de quebrar rotina operacional |

---

## 5. Allowlist inicial sugerida para leitura de arquivos

## `docs/`
- `docs/prd-mission-control-openclaw.md`
- `docs/checklist-tecnico-mission-control.md`
- `docs/mission-control-v1-design.md`
- `docs/mission-control-v1-implementation-plan.md`
- `docs/mission-control-auditoria-estatica.md`
- `docs/mission-control-patch-list-v1.md`
- `docs/mission-control-matriz-permissoes.md`

## `memory/`
Permitir apenas subset deliberado, por exemplo:
- notas específicas aprovadas
- arquivos temáticos não sensíveis e úteis à operação
- nunca por navegação livre

---

## 6. Mapeamento dos paths auditados para decisão v1

| Path real do repo base | Decisão v1 |
| --- | --- |
| `src/app/api/terminal/route.ts` | bloquear/remover |
| `src/app/api/actions/route.ts` | reescrever com catálogo mínimo |
| `src/app/api/files/route.ts` | restringir a allowlist explícita |
| `src/app/api/files/write/route.ts` | remover/bloquear |
| `src/app/api/files/delete/route.ts` | remover/bloquear |
| `src/app/api/files/mkdir/route.ts` | remover/bloquear |
| `src/app/api/files/upload/route.ts` | remover/bloquear |
| `src/app/api/browse/route.ts` | remover/bloquear |
| `src/app/api/cron/route.ts` | leitura primeiro |
| `src/app/api/cron/run/route.ts` | condicional e allowlisted |
| `src/app/api/system/route.ts` | quebrar em endpoints derivados |
| `src/app/api/system/services/route.ts` | remover ações amplas |
| `src/app/api/logs/stream/route.ts` | substituir por acesso resumido |

---

## 7. Critério de aceitação

A v1 só passa se:
- não existir terminal web utilizável
- não existir file manager genérico com write/delete/upload
- arquivos-raiz sensíveis estiverem fora de alcance
- config sensível não aparecer bruta
- ações manuais forem poucas, explícitas e auditáveis
