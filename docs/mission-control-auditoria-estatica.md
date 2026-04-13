# Auditoria estática do repo base `tenacitOS`

_Data: 2026-04-13_
_Base auditada: `/root/.openclaw/workspace/tmp/repo-audit-tenacitos`_

## 1. Resumo executivo

O repo base é um painel Next.js 16 com App Router, focado em observabilidade e operação local, mas hoje expõe superfícies amplas demais para o nosso padrão de risco.

Conclusão objetiva:
- **serve como base de fork interno**, mas
- **não deve ir para produção como está**, e
- exige **hardening real antes de qualquer deploy**.

Os principais riscos encontrados não são malware ou dependência suspeita. O problema está em **superfície privilegiada demais**:
- terminal web com execução de shell
- ações rápidas com comandos do host
- leitura e escrita em arquivos do workspace
- leitura de arquivos-raiz sensíveis
- mutações operacionais destrutivas em cron e sistema

---

## 2. Stack e estrutura real

### Stack detectada
- **Framework:** Next.js `16.1.6`
- **UI:** React `19.2.3`
- **Linguagem:** TypeScript
- **Persistência local:** `better-sqlite3`
- **Markdown:** `react-markdown`
- **Visual/3D:** `three`, `@react-three/fiber`, `@react-three/drei`, `@react-three/rapier`

### Scripts principais
- `npm run dev` → `next dev -H 0.0.0.0`
- `npm run build` → `next build`
- `npm run start` → `next start -H 0.0.0.0`
- `npm run lint` → `eslint`

### Estrutura principal
- `src/app/(dashboard)/...` → páginas do painel
- `src/app/api/...` → rotas de API com leitura, escrita e ações do sistema
- `src/components/...` → componentes da UI
- `src/lib/...` → utilitários de paths, skills, uso, activity log
- `src/middleware.ts` → middleware global
- `scripts/...` → scripts auxiliares
- `data/...` → dados locais do painel

---

## 3. Superfícies reais encontradas

## 3.1 UI com áreas sensíveis expostas

Páginas relevantes em `src/app/(dashboard)/`:
- `actions`
- `agents`
- `cron`
- `files`
- `git`
- `logs`
- `memory`
- `sessions`
- `system`
- `terminal`

Leitura direta disso:
- o produto já nasce com ambição de **observabilidade + operação ativa**
- isso conflita com a nossa decisão de v1 mais restrita

## 3.2 APIs de maior risco

### Terminal web
- `src/app/api/terminal/route.ts`
- UI ligada em `src/app/(dashboard)/terminal/page.tsx`

Risco:
- executa shell via `exec`
- apesar de allowlist, continua sendo shell remoto no browser
- isso está **fora do escopo da v1**

### Quick actions com shell
- `src/app/api/actions/route.ts`

Ações identificadas:
- `restart-gateway`
- `clear-temp`
- `usage-stats`
- `heartbeat`
- `npm-audit`
- `git-status`

Risco:
- usa `exec`
- mistura ações inocentes com ações administrativas reais
- inclui restart de serviço e limpeza de arquivos
- uma allowlist existe, mas o desenho ainda é amplo demais para v1

### Filesystem read/write/delete/upload
Rotas identificadas:
- `src/app/api/files/route.ts`
- `src/app/api/files/write/route.ts`
- `src/app/api/files/delete/route.ts`
- `src/app/api/files/mkdir/route.ts`
- `src/app/api/files/upload/route.ts`
- `src/app/api/files/download/route.ts`
- `src/app/api/browse/route.ts`

Risco:
- leitura e escrita reais no workspace/OpenClaw dir
- criação de diretórios, upload, delete, write
- browser de arquivos genérico
- superfície muito ampla para prompt injection persistente e erro operacional

### System route com leitura e mutação de config local
- `src/app/api/system/route.ts`

Comportamentos encontrados:
- lê `IDENTITY.md`
- lê `TOOLS.md`
- lê `~/.openclaw/openclaw.json`
- lê/escreve `.env.local`
- ação `change_password`
- ação `clear_activity_log`

Risco:
- mistura observabilidade com mutação de credencial local
- lê arquivos que no nosso ambiente devem ser tratados como sensíveis

### Cron com operações destrutivas/ativas
- `src/app/api/cron/route.ts`
- `src/app/api/cron/run/route.ts`

Comportamentos encontrados:
- lista cron jobs via CLI
- enable/disable job
- delete job
- trigger manual com `openclaw cron run --force`

Risco:
- vai além de observabilidade
- já entra em governança ativa de rotina operacional
- isso pode existir depois, mas na nossa v1 precisa entrar de forma muito mais restrita

### Logs em streaming e monitor de sistema
- `src/app/api/logs/stream/route.ts`
- `src/app/api/system/monitor/route.ts`
- `src/app/api/system/services/route.ts`
- `src/app/api/health/route.ts`

Risco:
- uso de `spawn` e `exec`
- chance de exposição excessiva de estado interno do host
- útil para observabilidade, mas exige recorte e sanitização

### Search / memory com leitura ampla demais
- `src/app/api/search/route.ts`
- `src/app/api/memory/search/route.ts`
- `src/app/api/files/route.ts`

Risco:
- `src/app/api/files/route.ts` expõe root files como:
  - `MEMORY.md`
  - `SOUL.md`
  - `USER.md`
  - `AGENTS.md`
  - `TOOLS.md`
  - `IDENTITY.md`
- isso contraria diretamente a nossa decisão de bloquear arquivos-raiz sensíveis na v1

---

## 4. Achados técnicos específicos

## 4.1 O terminal não é aceitável na v1

Arquivo:
- `src/app/api/terminal/route.ts`

Mesmo com bloqueios explícitos, ele:
- usa `exec`
- permite composição com pipes e segmentos
- mantém shell remoto como feature do produto

Decisão recomendada:
- **remover da v1** ou devolver `403` fixo por policy

## 4.2 O browser de arquivos é genérico demais

Arquivo:
- `src/app/api/browse/route.ts`

Problema:
- permite navegar qualquer path dentro de `OPENCLAW_DIR/<workspace>`
- isso não é allowlist por domínio funcional, é só contenção por base path

Decisão recomendada:
- trocar por readers específicos e allowlist explícita
- eliminar navegação livre por workspace

## 4.3 A API de files atual viola o desenho de segurança da nossa v1

Arquivo:
- `src/app/api/files/route.ts`

Problema:
- expõe leitura de arquivos-raiz sensíveis
- `PUT` salva conteúdo diretamente em markdown permitido
- o conjunto permitido atual inclui root files que devem ser read-only para nós

Decisão recomendada:
- remover `PUT` da v1
- bloquear root files sensíveis
- limitar leitura a subset específico de `docs/` e `memory/`

## 4.4 Há escrita e deleção explícitas no filesystem

Arquivos:
- `src/app/api/files/write/route.ts`
- `src/app/api/files/delete/route.ts`
- `src/app/api/files/mkdir/route.ts`
- `src/app/api/files/upload/route.ts`

Problema:
- isso já é administração ativa do host/workspace
- é incompatível com a postura segura da v1

Decisão recomendada:
- bloquear integralmente na v1

## 4.5 Quick actions precisam ser redesenhadas

Arquivo:
- `src/app/api/actions/route.ts`

Problema:
- `restart-gateway` é ação administrativa relevante
- `clear-temp` remove arquivos
- `heartbeat` usa `curl` a domínio externo na lógica interna
- `npm-audit` faz shell encadeado no diretório do mission control

Decisão recomendada:
- substituir por action gateway mínimo
- permitir só ações leves e explicitamente allowlisted

## 4.6 Cron atual vai além da v1 aprovada

Arquivos:
- `src/app/api/cron/route.ts`
- `src/app/api/cron/run/route.ts`

Problema:
- além de listar, já altera enable/disable, remove e executa jobs

Decisão recomendada:
- v1 deve começar com leitura
- ações manuais leves precisam de recorte muito menor que o código atual

## 4.7 System route mistura info útil com material sensível

Arquivo:
- `src/app/api/system/route.ts`

Problema:
- lê `TOOLS.md` e `openclaw.json`
- faz escrita em `.env.local`
- expõe detalhes que não cabem brutos na v1

Decisão recomendada:
- quebrar em adapters menores
- só expor subset derivado e sanitizado

---

## 5. Avaliação por área

| Área | Estado atual | Risco | Ação recomendada |
| --- | --- | --- | --- |
| Host/system | útil, mas amplo | médio-alto | manter subset sanitizado |
| Agents | promissor | médio | adaptar para arquitetura real OpenClaw |
| Sessions | útil | médio | manter com sanitização |
| Cron | útil porém ativo demais | alto | reduzir para leitura + ação leve muito específica |
| Files | amplo demais | crítico | substituir por allowlist estrita |
| Memory | mistura leitura e escrita | crítico | leitura controlada, sem escrita ampla |
| Terminal | presente | crítico | remover/bloquear |
| Quick actions | presente | alto | reduzir e reescrever |
| Logs | potencialmente útil | médio-alto | expor só subset aprovado |
| Config | sensível | alto | expor só dados derivados |

---

## 6. Conclusão

O repo tem valor como ponto de partida porque já oferece:
- estrutura de dashboard
- páginas úteis de operação
- integração com OpenClaw em vários pontos
- UI pronta para agentes, sessões, cron, sistema e arquivos

Mas ele precisa de intervenção séria para virar o nosso Mission Control.

Veredito:
- **base aproveitável**
- **não pronta para produção**
- **hardening obrigatório antes de qualquer deploy**

Próximo artefato ligado a esta auditoria:
- `docs/mission-control-patch-list-v1.md`
