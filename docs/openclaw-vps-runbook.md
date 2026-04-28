# OpenClaw VPS Runbook

Atualizado: 2026-04-28

## Modo oficial de execucao

### Core OpenClaw

- Raiz operacional: `/root/.openclaw`
- Workspace principal: `/root/.openclaw/workspace`
- Fonte de verdade institucional: `/root/2nd-brain`
- Agentes: `/root/.openclaw/agents`
- Credenciais locais: `/root/.openclaw/credentials` e `/root/.openclaw/workspace/credentials`
- Segredos de contexto local: `/root/.openclaw/workspace/memory/context`
- Cron interno OpenClaw: `/root/.openclaw/cron/jobs.json`

### Mission Control

- Projeto: `/root/.openclaw/workspace/projects/mission-control`
- Processo: PM2
- Nome PM2: `mission-control`
- Porta local: `3001`
- Healthcheck: `http://127.0.0.1:3001/api/health`
- Logs PM2:
  - `/root/.pm2/logs/mission-control-out.log`
  - `/root/.pm2/logs/mission-control-error.log`

### Servicos systemd relevantes

- `pm2-root.service`: supervisor do Mission Control.
- `docker.service`: containers auxiliares.
- `nginx.service`: proxy HTTP/HTTPS.
- `tailscaled.service`: rede privada Tailscale.
- `openclaw-mcp.service`: ponte MCP local.
- `xp-sync.timer` / `xp-sync.service`: rotina externa de conciliacao XP, dependente do Chrome remoto do Ale.

### Docker

Servicos auxiliares rodam em Docker:

- Supabase local `trade`.
- Supabase local `mensura-schedule-control`.
- `n8n`.
- `ghost`.
- `postiz`.
- `temporal`.
- sandboxes OpenClaw.

Docker nao e o supervisor do Mission Control.

## Fronteiras de arquitetura

### Core

Inclui:

- OpenClaw runtime.
- Agentes e sessoes.
- Mission Control.
- 2nd-brain.
- Cron interno OpenClaw.

Mudancas aqui exigem backup e validacao.

### Integracoes

Incluem:

- LinkedIn.
- Microsoft Graph.
- WhatsApp.
- Sienge.
- XP.
- Supabase cloud/local.
- Backblaze B2.

Mudancas aqui exigem cuidado com credenciais, side effects externos e logs sem segredo.

### Servicos auxiliares

Incluem:

- n8n.
- Ghost.
- Postiz.
- Temporal.
- Supabase local.
- Notion/NotebookLM sync.

Podem afetar operacao, mas nao devem ser confundidos com o core OpenClaw.

## Politica de segredos

- Segredo real nunca deve ir para Git nem para o 2nd-brain.
- Arquivos reais de segredo devem usar permissao `600`.
- Diretorios com credenciais devem usar permissao `700`.
- Templates podem ser versionados como `.example`, sem valores reais.
- Auth/browser profiles ficam em `/root/.openclaw/credentials/**`.

## Backups

### Politica desejada

- Manter 3 dias de protecao total.
- B2: 2 conjuntos remotos.
- VPS: 1 conjunto local mais recente.

### Scripts

- Backup `2nd-brain`: `/root/.openclaw/workspace/scripts/backup_2nd_brain_b2.py`
- Backup full streaming VPS: `/root/.openclaw/workspace/scripts/backup_vps_full_b2_stream.py`
- Retencao segura: `/root/.openclaw/workspace/scripts/backup_retention_b2.py`

### Prefixos B2

- Full VPS: `flavia/vps-full/`
- 2nd-brain: `flavia/2nd-brain/`

### Validacao

```bash
python3 /root/.openclaw/workspace/scripts/backup_retention_b2.py --dry-run
```

## Healthcheck padrao

```bash
pm2 jlist
curl -sS -i http://127.0.0.1:3001/api/health
systemctl --failed --no-pager
docker ps
df -h /
python3 /root/.openclaw/workspace/scripts/backup_retention_b2.py --dry-run
```

Observacao: alguns comandos de rede local podem falhar dentro de sandbox; validar fora do sandbox quando necessario.

## Recuperacao rapida

### Mission Control fora do ar

1. Verificar PM2:
   ```bash
   pm2 jlist
   ```
2. Ver logs:
   ```bash
   tail -120 /root/.pm2/logs/mission-control-error.log
   tail -120 /root/.pm2/logs/mission-control-out.log
   ```
3. Validar build se houve mudanca:
   ```bash
   cd /root/.openclaw/workspace/projects/mission-control
   npm run build
   ```
4. Recarregar somente se necessario:
   ```bash
   pm2 reload mission-control
   ```

### Disco alto

1. Verificar uso:
   ```bash
   df -h /
   du -sh /root/openclaw-backups /root/.pm2/logs /var/log /root/.openclaw/workspace/runtime 2>/dev/null
   ```
2. Nunca apagar backups full locais se `flavia/vps-full/` nao tiver conjunto completo no B2.
3. Rodar retencao em dry-run antes de qualquer exclusao:
   ```bash
   python3 /root/.openclaw/workspace/scripts/backup_retention_b2.py --dry-run
   ```

### XP sync

`xp-sync` depende do Chrome remoto do Ale em `100.88.24.55:9222`. Se CDP nao estiver disponivel, a rotina deve pular sem marcar systemd failed.

Nao rodar sincronizacao manual sem confirmacao, pois envolve acesso XP e side effects externos.

## Regras de manutencao

- Fazer backup antes de mudanca estrutural.
- Nao atualizar OpenClaw core sem aprovacao explicita.
- Nao remover cron duplicado sem decisao por item.
- Nao imprimir segredo em terminal, log ou relatorio.
- Preferir `dry-run` antes de limpeza.
- Validar com comando objetivo antes de declarar concluido.
