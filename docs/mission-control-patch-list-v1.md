# Patch list v1 do Mission Control

_Data: 2026-04-13_
_Base auditada: `/root/.openclaw/workspace/tmp/repo-audit-tenacitos`_

## Objetivo

Traduzir a auditoria estática em intervenção concreta para o fork interno do Mission Control v1.

Princípio da v1:
- leitura útil primeiro
- ação leve só quando for explicitamente allowlisted
- nada de shell genérico
- nada de filesystem genérico
- nada de exposição bruta de config sensível

---

## Bloco A, cortes obrigatórios antes de qualquer deploy

## A1. Desabilitar terminal web

**Paths reais**
- `src/app/api/terminal/route.ts`
- `src/app/(dashboard)/terminal/page.tsx`

**Problema**
- shell remoto via browser, mesmo com allowlist

**Patch v1**
- remover item do menu/UI
- rota deve retornar `403` fixo ou ser removida do fork

**Prioridade**
- P0

## A2. Remover quick actions perigosas

**Path real**
- `src/app/api/actions/route.ts`

**Problema**
- mistura observabilidade com shell administrativo
- inclui `restart-gateway`, `clear-temp`, `heartbeat`, `npm-audit`

**Patch v1**
- substituir por adapter interno com catálogo fechado de ações leves
- v1 permitir no máximo:
  - refresh de coleta
  - ack de alerta
  - copiar comando seguro
- bloquear restart, limpeza e audit shell-driven

**Prioridade**
- P0

## A3. Bloquear mutações genéricas em filesystem

**Paths reais**
- `src/app/api/files/write/route.ts`
- `src/app/api/files/delete/route.ts`
- `src/app/api/files/mkdir/route.ts`
- `src/app/api/files/upload/route.ts`
- `src/app/api/files/download/route.ts`
- `src/app/api/browse/route.ts`

**Problema**
- escrita, deleção, upload e navegação livre no workspace

**Patch v1**
- remover do fork ou retornar `403` por policy
- substituir por endpoints de leitura especializados
- sem upload, delete, mkdir, write genérico na v1

**Prioridade**
- P0

## A4. Restringir API de memory/files a allowlist real

**Path real**
- `src/app/api/files/route.ts`

**Problema**
- hoje expõe root files sensíveis, inclusive:
  - `MEMORY.md`
  - `SOUL.md`
  - `USER.md`
  - `AGENTS.md`
  - `TOOLS.md`
  - `IDENTITY.md`
- também aceita `PUT`

**Patch v1**
- remover `PUT`
- trocar allowlist por lista explícita de leitura:
  - `docs/mission-control-*`
  - `docs/checklist-tecnico-mission-control.md`
  - subset aprovado de `memory/`
- bloquear totalmente arquivos-raiz sensíveis

**Prioridade**
- P0

---

## Bloco B, reduzir superfície operacional

## B1. Reescrever cron para modo observabilidade primeiro

**Paths reais**
- `src/app/api/cron/route.ts`
- `src/app/api/cron/run/route.ts`

**Problema**
- atual implementação já lista, habilita, desabilita, remove e executa jobs

**Patch v1**
- fase inicial: apenas leitura de jobs e últimos estados
- eventual ação leve: `run` só em allowlist explícita de jobs seguros
- bloquear `DELETE`
- bloquear toggle global por padrão

**Prioridade**
- P1

## B2. Reescrever services control

**Paths reais**
- `src/app/api/system/services/route.ts`
- `src/app/api/system/monitor/route.ts`
- `src/app/api/logs/stream/route.ts`

**Problema**
- hoje permite start/stop/restart/logs para systemd, pm2 e docker
- logs em streaming direto do host

**Patch v1**
- monitor: manter leitura de status e métricas sanitizadas
- services: remover `start`, `stop`, `restart` da v1
- logs: expor só tail resumido e sanitizado, sem stream bruto contínuo no primeiro corte

**Prioridade**
- P1

## B3. Sanitizar system route

**Path real**
- `src/app/api/system/route.ts`

**Problema**
- mistura leitura útil com acesso a `openclaw.json`, `TOOLS.md` e escrita em `.env.local`

**Patch v1**
- separar em endpoints derivados:
  - `/api/system/summary`
  - `/api/system/integrations`
  - `/api/system/host-stats`
- remover `change_password`
- remover qualquer escrita em `.env.local`
- não expor config crua

**Prioridade**
- P1

---

## Bloco C, alinhar com arquitetura OpenClaw real

## C1. Criar camada de adapters em vez de shell disperso

**Problema**
- o repo base usa `exec`, `execSync` e `spawn` em várias rotas como mecanismo principal

**Patch v1**
- centralizar integração em adapters internos por domínio:
  - `agents`
  - `sessions`
  - `cron`
  - `host`
  - `memory`
- política primeiro, execução depois

**Prioridade**
- P1

## C2. Introduzir policy layer explícita

**Problema**
- hoje a contenção está distribuída em regex, arrays locais e base-path checks

**Patch v1**
- criar política declarativa com:
  - recursos permitidos
  - ações permitidas
  - paths permitidos
  - jobs permitidos
  - serviços permitidos
- UI e API devem depender dessa camada, não de allowlists soltas

**Prioridade**
- P1

## C3. Mapear superfícies da v1 para páginas realmente mantidas

**Manter na v1**
- host summary
- agents inventory
- sessions recentes sanitizadas
- cron leitura
- docs allowlisted
- memory allowlisted
- alertas e status geral

**Remover da v1**
- terminal
- file manager genérico
- edição genérica
- upload/delete/mkdir
- service control amplo
- password/config mutation

**Prioridade**
- P1

---

## Bloco D, UI e UX de segurança

## D1. Deixar claro o que é leitura e o que é ação

**Patch v1**
- separar blocos da UI em:
  - leitura
  - ação leve
- ações devem ter rotulagem explícita, escopo visível e confirmação

**Prioridade**
- P2

## D2. Logar toda ação manual

**Patch v1**
- qualquer ação leve precisa de trilha:
  - quem acionou
  - quando
  - qual recurso
  - resultado

**Prioridade**
- P2

---

## Ordem recomendada de execução

1. **P0** cortar terminal, files genéricos, write/delete/upload/mkdir e quick actions perigosas
2. **P1** reescrever cron/services/system para modo seguro e derivado
3. **P1** criar adapters + policy layer
4. **P2** limpar UI e reforçar trilha de auditoria

---

## Saída esperada após este patch set

Ao final do corte v1, o fork interno deve ficar assim:
- painel útil para leitura operacional
- sem shell remoto
- sem file manager genérico
- sem mutação ampla do host
- sem leitura de arquivos-raiz sensíveis
- com poucas ações leves, explícitas e auditáveis
