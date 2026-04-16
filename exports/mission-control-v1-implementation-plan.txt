# Mission Control v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adaptar com segurança o repo base do Mission Control para uma v1 privada, Tailscale-first, com observabilidade do OpenClaw e ações operacionais leves sob allowlist.

**Architecture:** A implementação será um fork interno com refatoração moderada. O trabalho será dividido em auditoria estrutural, isolamento de superfícies perigosas, criação de policy layer explícita, adaptação de fontes de dados do OpenClaw e validação final em modo read-mostly com ações leves permitidas.

**Tech Stack:** Repo base do Mission Control, OpenClaw runtime, Tailscale, Node/TypeScript ou stack nativa do repo base, git.

---

## Estrutura de arquivos prevista

### Documentos de trabalho
- Criar: `docs/mission-control-auditoria-estatica.md`
- Criar: `docs/mission-control-patch-list-v1.md`
- Criar: `docs/mission-control-matriz-permissoes.md`
- Criar: `docs/mission-control-deploy-vps.md`
- Criar: `docs/mission-control-rollback.md`

### Código do fork interno
> Os paths exatos do código dependem da estrutura real do repo clonado. O primeiro bloco do plano fixa isso com inventário obrigatório antes de qualquer patch.

### Diretório recomendado
- Criar: `projects/mission-control/` ou outro diretório dedicado do fork interno, separado do workspace principal da Flávia

---

### Task 1: Inventário estrutural do repo base

**Files:**
- Create: `docs/mission-control-auditoria-estatica.md`
- Inspect: diretório clonado do repo base do Mission Control

- [ ] **Step 1: Listar a árvore principal do repo**

Run:
```bash
find <repo-mission-control> -maxdepth 3 | sort > /tmp/mission-control-tree.txt
```

Expected:
- arquivo com a árvore principal do projeto
- identificação clara de `src/`, `app/`, `pages/`, `api/`, `server/`, `components/`, `lib/`, `scripts/` ou equivalentes

- [ ] **Step 2: Mapear framework, build e comandos reais**

Run:
```bash
cat <repo-mission-control>/package.json
```

Registrar no documento:
- framework
- scripts de dev/build/start/test
- dependências de auth
- dependências de renderização markdown
- dependências de shell/fs

- [ ] **Step 3: Mapear rotas e superfícies sensíveis**

Run:
```bash
find <repo-mission-control> \( -path '*/api/*' -o -path '*/routes/*' -o -path '*/server/*' \) | sort
```

Registrar no documento:
- rotas de leitura
- rotas de escrita
- rotas de terminal/shell
- rotas de filesystem
- rotas de auth

- [ ] **Step 4: Mapear uso de execução de comandos**

Run:
```bash
grep -RInE "child_process|exec\(|spawn\(|execFile\(|pty|terminal" <repo-mission-control>
```

Registrar cada ocorrência com:
- arquivo
- função
- risco
- decisão preliminar (remover, restringir, manter)

- [ ] **Step 5: Mapear leitura/escrita em filesystem**

Run:
```bash
grep -RInE "fs\.|readFile|writeFile|readdir|rm\(|unlink\(|mkdir\(|path\.join|path\.resolve" <repo-mission-control>
```

Registrar:
- quais paths são tocados
- se existe navegação livre
- se existe edição genérica

- [ ] **Step 6: Commitar a auditoria inicial**

```bash
git add docs/mission-control-auditoria-estatica.md
git commit -m "docs: add static audit for mission control base repo"
```

---

### Task 2: Definir matriz de permissões da v1

**Files:**
- Create: `docs/mission-control-matriz-permissoes.md`
- Reference: `docs/mission-control-v1-design.md`
- Reference: `docs/checklist-tecnico-mission-control.md`

- [ ] **Step 1: Listar superfícies de leitura permitidas**

Incluir no documento:
```md
## Leitura permitida
- host metrics aprovadas
- agents inventory
- recent sessions sanitizadas
- cron jobs/status
- docs allowlisted
- memory allowlisted
- config/log excerpts allowlisted
```

- [ ] **Step 2: Listar superfícies de leitura proibidas**

Incluir:
```md
## Leitura proibida
- leitura completa de config sensível
- leitura irrestrita de logs brutos
- navegação livre no filesystem
- qualquer path fora da allowlist
```

- [ ] **Step 3: Listar ações leves permitidas**

Incluir:
```md
## Ações permitidas na v1
- refresh manual
- ack de alerta
- copiar comando seguro
- abrir link interno
- rerun de coleta safe explicitamente allowlisted
```

- [ ] **Step 4: Listar ações proibidas**

Incluir:
```md
## Ações proibidas na v1
- terminal web
- shell arbitrário
- reinício irrestrito de serviço
- edição ampla de arquivos
- edição de arquivos-raiz sensíveis
- ações destrutivas
```

- [ ] **Step 5: Commitar matriz**

```bash
git add docs/mission-control-matriz-permissoes.md
git commit -m "docs: add mission control permissions matrix"
```

---

### Task 3: Gerar patch list técnica fechada

**Files:**
- Create: `docs/mission-control-patch-list-v1.md`
- Reference: `docs/mission-control-auditoria-estatica.md`
- Reference: `docs/mission-control-matriz-permissoes.md`

- [ ] **Step 1: Criar tabela de rotas perigosas**

Incluir estrutura:
```md
| Área | Arquivo | Risco | Ação v1 | Observação |
| --- | --- | --- | --- | --- |
| API | src/... | terminal remoto | remover | fora do escopo da v1 |
```

- [ ] **Step 2: Criar tabela de refactors obrigatórios**

Incluir colunas:
```md
| Componente | Problema | Refactor necessário | Prioridade |
```

- [ ] **Step 3: Criar tabela de adapters OpenClaw**

Incluir:
```md
| Adapter | Fonte | Saída esperada | Sanitização |
| --- | --- | --- | --- |
| agents | openclaw config/runtime | lista de agentes | ocultar campos sensíveis |
| sessions | openclaw sessions | sessões recentes | resumir e sanitizar |
| crons | cron runtime | jobs/status | omitir payloads sensíveis |
```

- [ ] **Step 4: Criar tabela de bloqueios explícitos**

Incluir:
```md
| Item | Status v1 |
| --- | --- |
| terminal web | bloqueado |
| file edit genérico | bloqueado |
| memory write amplo | bloqueado |
```

- [ ] **Step 5: Commitar patch list**

```bash
git add docs/mission-control-patch-list-v1.md
git commit -m "docs: add mission control v1 patch list"
```

---

### Task 4: Preparar fork interno e baseline de trabalho

**Files:**
- Create: `projects/mission-control/`
- Copy/Clone: código-base para o fork interno
- Create: `projects/mission-control/README.local.md`

- [ ] **Step 1: Criar diretório dedicado do fork**

Run:
```bash
mkdir -p /root/.openclaw/workspace/projects/mission-control
```

Expected:
- diretório dedicado criado

- [ ] **Step 2: Copiar ou clonar a base para o diretório interno**

Exemplo:
```bash
rsync -a --delete <repo-mission-control>/ /root/.openclaw/workspace/projects/mission-control/
```

Expected:
- fork de trabalho isolado do repo fonte inicial

- [ ] **Step 3: Criar README local de operação**

Conteúdo mínimo:
```md
# Mission Control local fork

- origem do código
- objetivo da adaptação
- status: v1 hardening em andamento
- acesso: privado via Tailscale
```

- [ ] **Step 4: Inicializar branch de trabalho**

```bash
git -C /root/.openclaw/workspace checkout -b feat/mission-control-v1
```

Ou, se o fork tiver repo próprio:
```bash
git -C /root/.openclaw/workspace/projects/mission-control checkout -b feat/mission-control-v1
```

- [ ] **Step 5: Commitar baseline**

```bash
git add projects/mission-control/README.local.md
git commit -m "chore: prepare internal mission control fork baseline"
```

---

### Task 5: Remover superfícies proibidas da v1

**Files:**
- Modify: arquivos reais de rotas/handlers identificados na auditoria
- Reference: `docs/mission-control-patch-list-v1.md`

- [ ] **Step 1: Escrever teste de negação para terminal web**

Exemplo de teste a adaptar ao framework:
```ts
it('blocks terminal endpoint in v1', async () => {
  const res = await request(app).post('/api/terminal').send({ cmd: 'whoami' })
  expect([403, 404]).toContain(res.status)
})
```

- [ ] **Step 2: Rodar teste e confirmar falha se endpoint ainda existir**

Run:
```bash
npm test -- terminal-block.test
```

Expected:
- FAIL se a superfície ainda estiver ativa

- [ ] **Step 3: Remover rota ou bloquear por policy hardcoded da v1**

Exemplo:
```ts
export async function POST() {
  return Response.json({ error: 'disabled in v1' }, { status: 403 })
}
```

- [ ] **Step 4: Repetir para edição genérica de arquivos**

Exemplo de teste:
```ts
it('blocks generic file write endpoint in v1', async () => {
  const res = await request(app).post('/api/files/write').send({ path: 'memory/x.md', content: 'x' })
  expect([403, 404]).toContain(res.status)
})
```

- [ ] **Step 5: Commitar remoção das superfícies proibidas**

```bash
git add .
git commit -m "hardening: disable terminal and generic file writes for v1"
```

---

### Task 6: Implementar policy layer explícita

**Files:**
- Create: caminhos reais equivalentes a `projects/mission-control/src/lib/policy.ts`
- Modify: handlers de docs, memory, config, logs e actions
- Test: arquivo de testes da policy

- [ ] **Step 1: Criar teste de allowlist de path**

```ts
it('allows only approved docs and memory paths', () => {
  expect(isAllowedPath('docs/ok.md')).toBe(true)
  expect(isAllowedPath('memory/context/ok.md')).toBe(true)
  expect(isAllowedPath('../secret')).toBe(false)
  expect(isAllowedPath('/root/.ssh/id_rsa')).toBe(false)
})
```

- [ ] **Step 2: Implementar policy mínima**

```ts
const ALLOWED_PREFIXES = ['docs/', 'memory/', 'memory/context/', 'memory/projects/']
const BLOCKED_FILES = ['SOUL.md', 'AGENTS.md', 'MEMORY.md', 'USER.md', 'IDENTITY.md', 'TOOLS.md']

export function isAllowedPath(input: string): boolean {
  if (!input || input.includes('..')) return false
  const normalized = input.replace(/^\/+/, '')
  if (BLOCKED_FILES.includes(normalized)) return false
  return ALLOWED_PREFIXES.some(prefix => normalized.startsWith(prefix))
}
```

- [ ] **Step 3: Criar teste para ação allowlisted**

```ts
it('allows only light actions in v1', () => {
  expect(isAllowedAction('refresh')).toBe(true)
  expect(isAllowedAction('ack-alert')).toBe(true)
  expect(isAllowedAction('restart-service')).toBe(false)
  expect(isAllowedAction('write-memory')).toBe(false)
})
```

- [ ] **Step 4: Implementar allowlist de ações**

```ts
const ALLOWED_ACTIONS = ['refresh', 'ack-alert', 'copy-command', 'open-link', 'rerun-safe-check']
export const isAllowedAction = (action: string) => ALLOWED_ACTIONS.includes(action)
```

- [ ] **Step 5: Commitar policy layer**

```bash
git add .
git commit -m "feat: add explicit policy layer for mission control v1"
```

---

### Task 7: Implementar adapters de leitura do OpenClaw

**Files:**
- Create: adapters reais para host, agents, sessions, crons, docs, memory, config/logs
- Test: arquivos de teste por adapter ou suíte consolidada

- [ ] **Step 1: Criar adapter de host com saída mínima**

Exemplo de interface:
```ts
export type HostStatus = {
  cpuPercent: number
  memoryPercent: number
  diskPercent: number
  uptimeSeconds: number
  gatewayStatus: 'ok' | 'degraded' | 'down'
}
```

- [ ] **Step 2: Criar adapter de agents**

Exemplo de interface:
```ts
export type AgentCard = {
  id: string
  workspace?: string
  role?: string
  lastActivity?: string
  status?: 'ok' | 'idle' | 'degraded'
}
```

- [ ] **Step 3: Criar adapter de sessions sanitizadas**

Exemplo de interface:
```ts
export type SessionCard = {
  sessionKey: string
  agentId?: string
  lastActivity?: string
  summary?: string
}
```

- [ ] **Step 4: Criar adapter de crons**

Exemplo de interface:
```ts
export type CronCard = {
  name: string
  schedule: string
  nextRun?: string
  lastRun?: string
  status?: 'ok' | 'warning' | 'error'
}
```

- [ ] **Step 5: Criar adapter de docs/memory/config/logs com policy aplicada**

Requisito:
- toda leitura passa pela policy layer
- logs/config retornam apenas subset permitido

- [ ] **Step 6: Commitar adapters**

```bash
git add .
git commit -m "feat: add openclaw read adapters for mission control v1"
```

---

### Task 8: Conectar UI aos dados reais da v1

**Files:**
- Modify: páginas, componentes e cards reais do fork
- Test: testes de renderização/componentes

- [ ] **Step 1: Criar teste de render para dashboard principal**

```ts
it('renders host, agents, sessions and crons cards', async () => {
  render(<Dashboard />)
  expect(screen.getByText(/host/i)).toBeInTheDocument()
  expect(screen.getByText(/agents/i)).toBeInTheDocument()
  expect(screen.getByText(/sessions/i)).toBeInTheDocument()
  expect(screen.getByText(/crons/i)).toBeInTheDocument()
})
```

- [ ] **Step 2: Ligar host/agents/sessions/crons aos adapters**

Implementar o mínimo para:
- cards carregarem dados reais
- falhas isoladas não derrubarem a tela inteira

- [ ] **Step 3: Ligar docs browser e memory browser à policy**

Requisito:
- navegação só em allowlist
- mensagens de negação claras

- [ ] **Step 4: Expor logs/config parciais como cards ou visões controladas**

Requisito:
- nada de raw dump completo
- mostrar só o subset aprovado

- [ ] **Step 5: Commitar integração da UI**

```bash
git add .
git commit -m "feat: connect dashboard ui to safe openclaw data sources"
```

---

### Task 9: Implementar ações operacionais leves

**Files:**
- Modify: action gateway real
- Modify: UI de ações
- Test: testes de autorização/ação

- [ ] **Step 1: Criar teste para ação permitida**

```ts
it('executes ack-alert when allowlisted', async () => {
  const res = await request(app).post('/api/actions').send({ action: 'ack-alert', payload: { id: 'a1' } })
  expect([200, 202]).toContain(res.status)
})
```

- [ ] **Step 2: Criar teste para ação proibida**

```ts
it('blocks restart-service in v1', async () => {
  const res = await request(app).post('/api/actions').send({ action: 'restart-service' })
  expect(res.status).toBe(403)
})
```

- [ ] **Step 3: Implementar action gateway com allowlist fechada**

Exemplo:
```ts
if (!isAllowedAction(action)) {
  return Response.json({ error: 'action not allowed in v1' }, { status: 403 })
}
```

- [ ] **Step 4: Expor na UI apenas ações permitidas**

Requisito:
- botões só para ações approved
- nada de affordance para ação proibida

- [ ] **Step 5: Commitar action gateway**

```bash
git add .
git commit -m "feat: add light allowlisted actions for mission control v1"
```

---

### Task 10: Hardening de deploy Tailscale-first

**Files:**
- Create: `docs/mission-control-deploy-vps.md`
- Create: `docs/mission-control-rollback.md`
- Modify: configs de ambiente/deploy do fork

- [ ] **Step 1: Documentar bind restrito e acesso pela tailnet**

Incluir:
```md
- serviço escuta apenas em interface/bind aprovado
- acesso somente via Tailscale
- sem exposição pública aberta
```

- [ ] **Step 2: Documentar variáveis críticas de auth**

Incluir:
```md
- APP_SECRET
- senha/admin auth
- cookie secure
- rate limit config
```

- [ ] **Step 3: Criar rollback objetivo**

Incluir:
```md
1. parar serviço mission control
2. restaurar build/config anterior
3. validar que OpenClaw principal permanece intacto
4. revisar logs mínimos
```

- [ ] **Step 4: Validar build e start locais**

Run:
```bash
npm install
npm run build
npm run start
```

Expected:
- build ok
- start ok
- app sobe sem expor rotas proibidas

- [ ] **Step 5: Commitar docs e hardening de deploy**

```bash
git add .
git commit -m "docs: add deploy and rollback guidance for mission control v1"
```

---

### Task 11: Validação final de segurança e aceite

**Files:**
- Reference: `docs/checklist-tecnico-mission-control.md`
- Reference: `docs/mission-control-patch-list-v1.md`
- Modify: código final se algum gap aparecer

- [ ] **Step 1: Rodar suíte de testes**

Run:
```bash
npm test
```

Expected:
- suíte verde

- [ ] **Step 2: Rodar smoke de rotas proibidas**

Exemplos:
```bash
curl -i http://127.0.0.1:<porta>/api/terminal
curl -i -X POST http://127.0.0.1:<porta>/api/actions -d '{"action":"restart-service"}'
```

Expected:
- `403` ou `404`

- [ ] **Step 3: Rodar smoke de rotas permitidas**

Exemplos:
```bash
curl -i http://127.0.0.1:<porta>/api/agents
curl -i http://127.0.0.1:<porta>/api/crons
```

Expected:
- `200`
- payloads sanitizados

- [ ] **Step 4: Revisar checklist de aceite**

Conferir explicitamente:
- sem terminal web
- sem file write genérico
- sem navegação livre
- sem edição de arquivos sensíveis
- Tailscale-first documentado
- ações leves somente por allowlist

- [ ] **Step 5: Commit final de aceite técnico**

```bash
git add .
git commit -m "chore: finalize mission control v1 hardening and acceptance"
```

---

## Self-review do plano

### Cobertura da spec
- estratégia de fork interno com refatoração moderada: coberta nas Tasks 1, 4 e 5
- Tailscale-first: coberta na Task 10
- observabilidade de host/agentes/sessões/crons: coberta nas Tasks 7 e 8
- docs/memory controlados: coberta nas Tasks 6, 7 e 8
- logs/config parciais: coberta nas Tasks 6, 7 e 8
- ações leves: coberta na Task 9
- bloqueio de terminal/web write amplo: coberta nas Tasks 5, 6 e 11

### Placeholder scan
- O único ponto dependente de contexto real do repo é a resolução dos arquivos concretos do fork. Isso foi tratado explicitamente na Task 1 como gate obrigatório antes de patch.

### Consistência
- Policy layer governa leitura e ação em todas as tasks posteriores.
- Não há ação destrutiva incluída no plano.

---

Plan complete and saved to `docs/mission-control-v1-implementation-plan.md`.

Two execution options:

**1. Subagent-Driven (recommended)** - eu despacho um subagent por bloco/tarefa, reviso entre etapas e acelero sem perder controle

**2. Inline Execution** - eu executo neste fluxo, em sequência, com checkpoints

Qual abordagem você quer?
