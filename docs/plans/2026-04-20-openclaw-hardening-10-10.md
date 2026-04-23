# Plano de Ajuste OpenClaw — 10/10

> **Para executores:** use `superpowers:subagent-driven-development` ou `superpowers:executing-plans` para rodar tarefa-a-tarefa. Steps em checkbox (`- [ ]`).
>
> **Este não é um plano de código/TDD.** É um plano de reconfiguração operacional. Cada task tem: edição pontual em arquivo JSON/config → comando de validação → critério de rollback.

**Goal:** levar o gateway OpenClaw de Mensura (v2026.4.15, Linux nativo) de 3,6/10 médio a 10/10 em 5 frentes: Segurança, Performance, Observabilidade, Governança de versão, Higiene operacional.

**Arquitetura do ajuste:** todos os ajustes são no `~/.openclaw/openclaw.json`, em arquivos de state (`exec-approvals.json`), no cron interno (`openclaw cron`), e em unit systemd novo. Nenhuma reinstalação. Backup do JSON antes de cada edição estrutural.

**Tech stack:** OpenClaw 2026.4.15 · Node 22.22.2 · Linux nativo · SQLite/Markdown memory · Telegram + WhatsApp channels · cron interno do OpenClaw.

**Referência externa:** relatório de auditoria técnica OpenClaw (2026-04-20). Auditoria interna: `~/.openclaw/workspace/docs/plans/2026-04-20-openclaw-hardening-10-10.md`.

---

## Pré-flight (obrigatório antes de qualquer task)

- [ ] **P.1 — Snapshot de segurança**

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.pre-hardening-$STAMP.bak
cp ~/.openclaw/exec-approvals.json ~/.openclaw/exec-approvals.json.pre-hardening-$STAMP.bak
openclaw security audit --deep --json > ~/.openclaw/logs/audit-pre-hardening-$STAMP.json
openclaw cron list > ~/.openclaw/logs/crons-pre-hardening-$STAMP.txt
tar czf ~/openclaw-backups/pre-hardening-$STAMP.tar.gz -C ~/.openclaw openclaw.json exec-approvals.json agents workspace 2>/dev/null | tail -5
echo "Pre-flight OK: $STAMP"
```

- [ ] **P.2 — Validar healthz/readyz atuais**

```bash
curl -sS http://127.0.0.1:18789/healthz
curl -sS http://127.0.0.1:18789/readyz
```

Registrar estado atual; critério de regressão se `healthz` parar de retornar 200.

- [ ] **P.3 — Anotar baseline de custo (opcional mas recomendado)**

```bash
openclaw cost report --window 24h 2>&1 | tee ~/.openclaw/logs/cost-baseline-$STAMP.txt
```

---

## FASE 1 — Segurança (6 tasks · severidade 🔴)

Objetivo: eliminar os 2 warns do `security audit` e fechar a superfície de ataque para "personal assistant + hardened".

### Task 1.1 — Corrigir `gateway.nodes.denyCommands` (nomes inválidos)

**File:** `~/.openclaw/openclaw.json` → chave `gateway.nodes.denyCommands`

- [ ] **Step 1: Listar nomes válidos**

```bash
openclaw security audit --deep --json | jq '.findings[] | select(.checkId=="gateway.nodes.deny_commands_ineffective") | .remediation'
```

- [ ] **Step 2: Editar JSON**

Substituir array atual:
```json
["camera.snap","camera.clip","screen.record","contacts.add","calendar.add","reminders.add","sms.send"]
```
Por (nomes válidos que realmente mitigam):
```json
["canvas.eval","canvas.a2ui.push","canvas.a2ui.pushJSONL","canvas.navigate"]
```

- [ ] **Step 3: Validar**

```bash
openclaw security audit --deep --json | jq '.findings[] | select(.checkId=="gateway.nodes.deny_commands_ineffective")'
```
Esperado: vazio (warn eliminado).

- [ ] **Step 4: Commit (diff)**

```bash
diff ~/.openclaw/openclaw.json.pre-hardening-*.bak ~/.openclaw/openclaw.json | head -30
```

---

### Task 1.2 — `fs.workspaceOnly: true` em `agents.defaults`

**File:** `~/.openclaw/openclaw.json` → chave `agents.defaults.tools.fs`

- [ ] **Step 1: Inserir (ou alterar) bloco**

```json
"tools": {
  "fs": {
    "enabled": true,
    "workspaceOnly": true,
    "operations": ["read","write","edit","apply_patch"]
  }
}
```

- [ ] **Step 2: Testar escrita fora do workspace**

```bash
openclaw exec --agent main --tool fs.write --path /tmp/test-escape.txt --content "x" 2>&1 | head
```
Esperado: recusa por política.

- [ ] **Step 3: Testar escrita dentro do workspace**

```bash
openclaw exec --agent main --tool fs.write --path ~/.openclaw/workspace/tmp/sanity.txt --content "ok" 2>&1 | head
cat ~/.openclaw/workspace/tmp/sanity.txt && rm ~/.openclaw/workspace/tmp/sanity.txt
```

---

### Task 1.3 — `sandbox.mode: "all"` para agentes de execução remota

**File:** `~/.openclaw/openclaw.json` → `agents.defaults.sandbox` **e** override em `agents.list.<agente>.sandbox`

Estratégia: sandbox global "all"; `main` (operador dono) mantém escapes explícitos via `sandbox.mode: "none"` apenas quando necessário.

- [ ] **Step 1: Definir default global**

```json
"agents": {
  "defaults": {
    "sandbox": { "mode": "all", "backend": "docker" }
  }
}
```

- [ ] **Step 2: Override em `main` (se precisar de exec no host)**

```json
"agents": { "list": { "main": { "sandbox": { "mode": "none" } } } }
```

- [ ] **Step 3: Validar**

```bash
openclaw security audit --deep --json | jq '.findings[] | select(.checkId=="security.trust_model.multi_user_heuristic")'
```
Esperado: vazio (warn some) ou severidade reduzida.

- [ ] **Step 4: Smoke test de cada canal**

```bash
openclaw agents list
openclaw cron run heartbeat:check-tatico --dry-run 2>&1 | tail -20
```

---

### Task 1.4 — `session.dmScope: "per-channel-peer"`

**File:** `~/.openclaw/openclaw.json` → chave `session.dmScope`

- [ ] **Step 1: Trocar valor**

De `"main"` para `"per-channel-peer"`.

- [ ] **Step 2: Documentar impacto**

Sessões atuais compartilhadas serão segmentadas por `(channel, peer)`. Mensagens históricas ficam na sessão `main` legada; novas DMs criam sessão própria.

- [ ] **Step 3: Validar com teste DM**

Enviar DM do operador `1067279351`; verificar diretório novo em `~/.openclaw/agents/main/sessions/`:

```bash
ls -lt ~/.openclaw/agents/main/sessions | head -5
```

---

### Task 1.5 — `controlUi.allowedOrigins` explícito

**File:** `~/.openclaw/openclaw.json` → `gateway.controlUi.allowedOrigins`

- [ ] **Step 1: Inserir bloco**

```json
"controlUi": {
  "allowInsecureAuth": false,
  "allowedOrigins": [
    "http://127.0.0.1:18789",
    "http://localhost:18789"
  ]
}
```

- [ ] **Step 2: Testar painel**

```bash
openclaw dashboard 2>&1 | head
curl -sS -H "Origin: http://evil.com" http://127.0.0.1:18789/ -I 2>&1 | head
```
Esperado: requests de origem não-listada negadas em CORS.

---

### Task 1.6 — `customBindHost` para `127.0.0.1` (fechar standby)

**File:** `~/.openclaw/openclaw.json` → `gateway.customBindHost`

- [ ] **Step 1: Alterar**

De `"0.0.0.0"` → `"127.0.0.1"`.

Motivo: bind atual é `loopback` (seguro), mas `customBindHost: 0.0.0.0` é bomba-relógio se alguém trocar `bind` para `lan`.

- [ ] **Step 2: Validar**

```bash
ss -tlnp | grep 18789
```
Esperado: somente `127.0.0.1:18789`.

---

## FASE 2 — Performance / Custo (9 tasks · severidade 🔴)

Objetivo: ativar as 5 alavancas do relatório externo + limpeza de sessions.

### Task 2.1 — `agents.defaults.contextInjection: "continuation-skip"`

- [ ] **Step 1: Inserir chave**

```json
"agents": { "defaults": { "contextInjection": "continuation-skip" } }
```

- [ ] **Step 2: Smoke (enviar mensagem, medir tokens de prompt)**

```bash
openclaw cost report --window 1h 2>&1 | tail -10
```
Comparar com baseline de P.3 após 24 h.

---

### Task 2.2 — `bootstrapMaxChars` + `bootstrapTotalMaxChars`

- [ ] **Step 1: Inserir limites**

```json
"agents": {
  "defaults": {
    "bootstrapMaxChars": 8000,
    "bootstrapTotalMaxChars": 24000
  }
}
```

- [ ] **Step 2: Validar que IDENTITY/SOUL/MEMORY não excedem**

```bash
for a in main finance mia mensura pcs croncheap autopilot; do
  ws=$(openclaw agents get $a --json 2>/dev/null | jq -r .workspace)
  [ -d "$ws" ] && wc -c "$ws"/{IDENTITY,SOUL,USER,MEMORY,AGENTS,TOOLS,HEARTBEAT}.md 2>/dev/null | tail -1
  echo "  agent=$a"
done
```

- [ ] **Step 3: Se algum agente excede 24000 chars totais, reduzir na task 2.3 abaixo**

---

### Task 2.3 — `heartbeat.isolatedSession: true`

- [ ] **Step 1: Inserir**

```json
"agents": {
  "defaults": {
    "heartbeat": {
      "every": "55m",
      "model": "google/gemini-2.5-flash-lite",
      "isolatedSession": true
    }
  }
}
```

Nota: `every` sobe de `30m` → `55m` para casar com TTL de cache de 1h (preparação para task 2.4).

- [ ] **Step 2: Validar impacto nos tokens do heartbeat**

```bash
openclaw logs --follow --grep heartbeat 2>&1 | head -20
```
Esperado: promptTokens por heartbeat cai de ~100k para ~2-5k.

---

### Task 2.4 — `cacheRetention: "long"` para modelos Anthropic/OpenAI

- [ ] **Step 1: Editar bloco `models`**

```json
"agents": {
  "defaults": {
    "models": {
      "openai-codex/gpt-5.4": { "params": { "cacheRetention": "long" } },
      "anthropic/claude-sonnet-4-6": { "params": { "cacheRetention": "long" } },
      "openai/gpt-5.4": { "params": { "cacheRetention": "long" } },
      "openai/gpt-5.4-pro": { "params": { "cacheRetention": "long" } },
      "openai/gpt-4o-mini": {},
      "google/gemini-3.1-pro-preview": {}
    }
  }
}
```

(Gemini usa cache implícito, não precisa do flag; 4o-mini é barato demais para compensar.)

- [ ] **Step 2: Validar cache-hit ratio após 24 h**

```bash
openclaw cost report --window 24h --by model 2>&1
```
Esperado: hit ratio > 60% em openai-codex (modelo dominante).

---

### Task 2.5 — `memorySearch.query.hybrid` + `batch`

- [ ] **Step 1: Editar bloco**

```json
"agents": {
  "defaults": {
    "memorySearch": {
      "enabled": true,
      "provider": "gemini",
      "model": "gemini-embedding-001",
      "fallback": "none",
      "query": {
        "hybrid": {
          "vectorWeight": 0.7,
          "textWeight": 0.3,
          "mmr": { "enabled": true, "lambda": 0.7 },
          "temporalDecay": { "enabled": true, "halfLifeDays": 30 }
        }
      },
      "remote": {
        "batch": { "enabled": true, "concurrency": 2, "wait": true }
      },
      "cache": { "enabled": true, "maxEntries": 50000 }
    }
  }
}
```

- [ ] **Step 2: Reindexar**

```bash
openclaw memory index --force 2>&1 | tail -20
```

- [ ] **Step 3: Smoke de recall**

```bash
openclaw memory search --agent main "ultima decisao de cronograma" 2>&1 | head -20
```

---

### Task 2.6 — `session.maintenance.mode: "enforce"` + limpar `main/sessions` (334 MB)

- [ ] **Step 1: Configurar enforce**

```json
"session": {
  "dmScope": "per-channel-peer",
  "maintenance": {
    "mode": "enforce",
    "maxAgeDays": 60,
    "maxMessagesPerSession": 2000
  }
}
```

- [ ] **Step 2: Dry-run**

```bash
openclaw sessions cleanup --dry-run --agent main 2>&1 | tee /tmp/cleanup-main.txt
```

- [ ] **Step 3: Revisar output, se coerente executar**

```bash
openclaw sessions cleanup --agent main 2>&1 | tail -20
du -sh ~/.openclaw/agents/main/sessions
```
Esperado: < 100 MB.

---

### Task 2.7 — `NODE_COMPILE_CACHE` + `OPENCLAW_NO_RESPAWN=1` (systemd)

Depende de Task 4.1 (criar unit systemd). Fazer aqui só o patch do env.

- [ ] **Step 1: Inserir no unit systemd (após Task 4.1)**

```
Environment="NODE_COMPILE_CACHE=/root/.openclaw/cache/node-compile"
Environment="OPENCLAW_NO_RESPAWN=1"
```

- [ ] **Step 2: Validar startup time**

```bash
systemctl restart openclaw-gateway
journalctl -u openclaw-gateway --since "1 min ago" | grep -iE "ready|started"
```

---

### Task 2.8 — Purgar workspaces `_old_*` e `financeiro.bak-20260414`

- [ ] **Step 1: Backup**

```bash
tar czf ~/openclaw-backups/old-workspaces-$(date +%Y%m%d).tar.gz \
  -C ~/.openclaw/agents _old_bi _old_juridico _old_marketing _old_producao _old_rh _old_suprimentos financeiro.bak-20260414 2>&1 | tail
```

- [ ] **Step 2: Remover**

```bash
rm -rf ~/.openclaw/agents/_old_bi ~/.openclaw/agents/_old_juridico \
       ~/.openclaw/agents/_old_marketing ~/.openclaw/agents/_old_producao \
       ~/.openclaw/agents/_old_rh ~/.openclaw/agents/_old_suprimentos \
       ~/.openclaw/agents/financeiro.bak-20260414
rm -rf ~/.openclaw/workspace-financeiro
```

- [ ] **Step 3: Validar agents list intacto**

```bash
openclaw agents list | grep -c "^- "
```
Esperado: 13 agentes (sem o `_old_*`).

---

### Task 2.9 — Criar identificações faltantes nos agentes incompletos

Identificado na auditoria anterior (rh, marketing, producao sem MEMORY.md; croncheap idem).

- [ ] **Step 1: Criar MEMORY.md esqueleto onde falta**

```bash
for a in rh marketing producao croncheap; do
  ws=~/.openclaw/workspace-$a
  [ "$a" = "croncheap" ] && ws=~/.openclaw/workspace-croncheap
  [ ! -f "$ws/MEMORY.md" ] && cat > "$ws/MEMORY.md" <<EOF
# MEMORY.md — $a

_Criado em $(date +%Y-%m-%d)_

## Estrutura
- \`memory/context/lessons.md\` — lições aprendidas
- \`memory/context/decisions.md\` — decisões do Alê
- \`memory/context/pending.md\` — pendências
- \`memory/YYYY-MM-DD.md\` — memória diária (append-only)
EOF
done
```

- [ ] **Step 2: Inicializar dir runtime dos 6 agentes sem `~/.openclaw/agents/<name>/agent`**

```bash
for a in rh marketing producao juridico bi suprimentos; do
  openclaw agents init $a 2>&1 | tail -5
done
```

---

## FASE 3 — Governança de Versão (3 tasks · severidade 🔴)

### Task 3.1 — Pinning explícito da versão

- [ ] **Step 1: Fixar 2026.4.15 no package global**

```bash
npm install -g openclaw@2026.4.15
npm ls -g openclaw
```

- [ ] **Step 2: Anotar SHA git do release atual**

```bash
openclaw --version
# já reporta commit 041266a — registrar em docs/
```

---

### Task 3.2 — Desativar `selfupdate:openclaw-core` automático → manual com gate

- [ ] **Step 1: Desativar cron automático**

```bash
openclaw cron list | awk '/selfupdate:openclaw-core/ {print $1}' | xargs openclaw cron disable
```

- [ ] **Step 2: Criar cron de *check* (não-apply)**

```bash
openclaw cron create \
  --name "selfupdate:check-only" \
  --schedule "cron 0 9 * * 1 @ America/Sao_Paulo" \
  --agent main \
  --prompt 'Rode npm view openclaw@latest version e compare com openclaw --version. Se diferente, mande mensagem no Telegram topic da Flávia mostrando changelog da versão. NÃO atualize.'
```

- [ ] **Step 3: Documentar procedure de upgrade manual**

Criar `~/.openclaw/workspace/docs/procedure-openclaw-upgrade.md` descrevendo: backup → `npm install -g openclaw@<versao>` → `openclaw gateway restart` → smoke tests (health/readyz/agents list/cron run) → rollback via backup.

---

### Task 3.3 — Smoke test pós-upgrade (cron one-shot manual)

- [ ] **Step 1: Criar script**

`/usr/local/bin/openclaw-smoke.sh`:

```bash
#!/usr/bin/env bash
set -eo pipefail
curl -fsS http://127.0.0.1:18789/healthz | grep -q '"ok":true'
curl -fsS http://127.0.0.1:18789/readyz | grep -q '"ready":true' || echo "WARN: readyz not ready"
openclaw agents list | grep -c "^- " | awk '$1>=13'
openclaw security audit --deep --json | jq '.summary.critical' | awk '$1==0'
echo "smoke OK"
```

- [ ] **Step 2: Usar após cada upgrade**

---

## FASE 4 — Observabilidade (4 tasks · severidade 🟡)

### Task 4.1 — systemd unit para openclaw-gateway

- [ ] **Step 1: Criar `/etc/systemd/system/openclaw-gateway.service`**

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/openclaw-gateway
Restart=always
RestartSec=2
TimeoutStartSec=90
Environment="NODE_COMPILE_CACHE=/root/.openclaw/cache/node-compile"
Environment="OPENCLAW_NO_RESPAWN=1"
StandardOutput=append:/tmp/openclaw/systemd.log
StandardError=append:/tmp/openclaw/systemd.err

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 2: Parar processo avulso**

```bash
kill 2054651 2>/dev/null || true
```

- [ ] **Step 3: Ativar**

```bash
systemctl daemon-reload
systemctl enable --now openclaw-gateway
systemctl status openclaw-gateway
curl -sS http://127.0.0.1:18789/healthz
```

---

### Task 4.2 — OTel / OTLP export

- [ ] **Step 1: Inserir bloco em openclaw.json**

```json
"diagnostics": {
  "otel": {
    "enabled": true,
    "endpoint": "http://127.0.0.1:4317",
    "sampleRate": 1.0,
    "serviceName": "openclaw-mensura"
  }
}
```

- [ ] **Step 2: Rodar coletor (opcional no host)**

Se não houver stack remota, rodar `otel-collector-contrib` local em container para validar que spans/metrics saem.

- [ ] **Step 3: Validar**

```bash
openclaw logs --follow --grep otel 2>&1 | head -10
```

---

### Task 4.3 — Cron de `security audit --deep --json`

- [ ] **Step 1: Criar cron**

```bash
openclaw cron create \
  --name "security:audit-daily" \
  --schedule "cron 0 5 * * * @ America/Sao_Paulo" \
  --agent croncheap \
  --prompt 'Rode: openclaw security audit --deep --json. Se summary.critical > 0, alerte no Telegram topic da Flávia com findings. Senão, apenas registre em ~/.openclaw/logs/audit-daily-YYYY-MM-DD.json.'
```

- [ ] **Step 2: Validar primeira execução**

```bash
openclaw cron run security:audit-daily
ls -lt ~/.openclaw/logs/audit-daily-*.json | head
```

---

### Task 4.4 — Investigar e corrigir 5 crons em `error`

Crons: `update-clawflows-direct`, `skills:provenance-audit`, `heartbeat:pulso-matinal`, `CCSP Casa 7 — Relatório`, `mia-status-semanal`.

- [ ] **Step 1: Puxar last run de cada um**

```bash
for id in 110ca43a-5305-49a9-a594-a4bcc30f2202 bccbbe65-8b13-4f19-a784-60c35936aa48 \
          e8f517f2-405c-4b3e-96ce-4bb35000e5c2 ed8307d6-b869-4c85-8f80-903c12b54830 \
          310bef26-4339-4288-b0f8-bdfb5541bf0c; do
  echo "=== $id ==="
  openclaw cron logs $id --limit 1 2>&1 | tail -30
done
```

- [ ] **Step 2: Classificar erro por categoria**

- Falta de allowlist exec → corrigir em Task 5.1
- Prompt quebrado → editar cron
- Modelo indisponível → fallback

- [ ] **Step 3: Re-rodar manualmente após fix**

```bash
openclaw cron run <id>
```

---

## FASE 5 — Cron hardening contra issue #69161 (2 tasks · severidade 🔴→🟡)

### Task 5.1 — Pre-allowlist binários usados pelos crons

- [ ] **Step 1: Extrair binários chamados pelos prompts de cron**

```bash
openclaw cron list --json 2>/dev/null | jq -r '.[] | .prompt // empty' \
  | grep -oE '/usr/bin/[a-z0-9_-]+|/usr/local/bin/[a-z0-9_-]+' | sort -u
```

- [ ] **Step 2: Para cada binário, adicionar em `exec-approvals.json` → `agents.croncheap.allowlist`**

Padrão:
```json
{
  "id": "<uuidgen>",
  "pattern": "/usr/bin/<binario>",
  "source": "allow-always",
  "scope": "cron"
}
```

Alvo mínimo esperado: `npm`, `git`, `jq`, `curl`, `bash`, `python3`.

- [ ] **Step 3: Validar**

```bash
jq '.agents.croncheap.allowlist | length' ~/.openclaw/exec-approvals.json
```

---

### Task 5.2 — Política "cron sem prompt interativo"

- [ ] **Step 1: Editar `openclaw.json`**

```json
"approvals": {
  "cron": {
    "mode": "allowlist-only",
    "onMissing": "fail-fast"
  }
}
```

Impede cron de entrar em loop pedindo aprovação — falha rápido e loga.

- [ ] **Step 2: Smoke com cron barato**

```bash
openclaw cron run cost:guard-daily
```

---

## FASE 6 — WhatsApp degradado (1 task · severidade 🟡)

### Task 6.1 — Diagnosticar `readyz: failing:["whatsapp"]`

- [ ] **Step 1: Probe canal**

```bash
openclaw channels status --probe 2>&1 | grep -i whatsapp
```

- [ ] **Step 2: Ver logs recentes**

```bash
grep -i whatsapp /tmp/openclaw/openclaw-2026-04-20.log | tail -40
```

- [ ] **Step 3: Reemparelhar conta `miafinance` se expirou**

```bash
openclaw whatsapp pair --account miafinance 2>&1 | head
```

- [ ] **Step 4: Validar**

```bash
curl -sS http://127.0.0.1:18789/readyz
```
Esperado: `"ready":true` ou `failing: []`.

---

## Pós-execução (cálculo do score 10/10)

- [ ] **F.1 — Re-rodar security audit**

```bash
openclaw security audit --deep --json | jq '.summary'
```
Esperado: `{critical:0, warn:0, info:0-1}`.

- [ ] **F.2 — Re-rodar cost report e comparar com baseline**

```bash
openclaw cost report --window 24h 2>&1 > ~/.openclaw/logs/cost-post-hardening.txt
diff ~/.openclaw/logs/cost-baseline-*.txt ~/.openclaw/logs/cost-post-hardening.txt
```
Esperado: redução > 30% em tokens de prompt (heartbeat isolado + cache).

- [ ] **F.3 — Re-rodar matriz de score**

| Categoria | Antes | Meta | Check |
|---|:-:|:-:|:-:|
| Implantação | 7/10 | 10/10 | systemd ativo + pinning |
| Segurança / Trust | 4/10 | 10/10 | sandbox all + fs workspaceOnly + denyCommands válidos + dmScope per-channel |
| Performance / Custo | 2/10 | 10/10 | 5 alavancas ligadas + sessions < 100MB |
| Observabilidade | 4/10 | 10/10 | OTel + cron audit + logs rotacionados |
| Sessions / Memória | 3/10 | 10/10 | maintenance enforce + mmr + temporalDecay |
| Governança de versão | 2/10 | 10/10 | pinning + selfupdate check-only + smoke script |

- [ ] **F.4 — Commit do `openclaw.json` no backup externo**

```bash
cp ~/.openclaw/openclaw.json ~/openclaw-backups/openclaw.json.post-hardening-$(date +%Y%m%d).bak
tar czf ~/openclaw-backups/post-hardening-$(date +%Y%m%d).tar.gz -C ~/.openclaw openclaw.json exec-approvals.json
```

---

## Rollback global (se algo quebrar)

```bash
STAMP=<timestamp do pre-flight>
systemctl stop openclaw-gateway 2>/dev/null
cp ~/.openclaw/openclaw.json.pre-hardening-$STAMP.bak ~/.openclaw/openclaw.json
cp ~/.openclaw/exec-approvals.json.pre-hardening-$STAMP.bak ~/.openclaw/exec-approvals.json
systemctl start openclaw-gateway 2>/dev/null || openclaw-gateway &
curl -sS http://127.0.0.1:18789/healthz
```

---

## Ordem sugerida de execução

Sequência com menor risco e melhor dependência:

1. **Pré-flight** (P.1 → P.3)
2. **Fase 1** (1.1 → 1.6) — hardening da superfície primeiro
3. **Fase 4.1** (systemd) — isolado, viabiliza 2.7
4. **Fase 2** (2.1 → 2.9) — performance depois da segurança
5. **Fase 5** (5.1 → 5.2) — depende de 2.9 (dir runtime dos agentes)
6. **Fase 4** (4.2 → 4.4) — observabilidade
7. **Fase 6** (6.1) — WhatsApp
8. **Fase 3** (3.1 → 3.3) — governança por último para pinning da versão já validada
9. **Pós-execução** (F.1 → F.4)

Tempo estimado: 2–3 horas se nada falhar · 4–6 h com smoke tests entre fases.

---

## Itens NÃO incluídos (por decisão)

- Migração para Node 24 (22.22.2 está suportado; migração é ruído sem ganho claro agora)
- Migração para Docker/K8s (audit externo prefere Linux nativo para um operador)
- Helm chart / HA (não existe oficialmente)
- Mudança de provider primário (stack está validada com openai-codex)
