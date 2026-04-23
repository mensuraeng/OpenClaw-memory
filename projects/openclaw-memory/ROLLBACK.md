# ROLLBACK.md

## Regra operacional
Antes de mudança estrutural em OpenClaw, cron, automação compartilhada, auth, memória central ou scripts operacionais:
1. rodar `scripts/backup_before_change.sh <rotulo>`
2. registrar o commit atual do workspace
3. só então aplicar a mudança

## O que é mudança estrutural
- patch em `/root/.openclaw/openclaw.json`
- criação, remoção ou alteração relevante de crons
- mudança em scripts usados por rotina automática
- alteração em memória operacional central ou regras do agente
- update de OpenClaw, plugins ou integrações

## Backup atual
O último backup estrutural fica referenciado em:
- `backups/latest-structural-backup.json`

Os arquivos de backup ficam fora do workspace em:
- `/root/openclaw-backups/`

## Rollback do workspace
### Reverter arquivo específico
```bash
git -C /root/.openclaw/workspace checkout <commit> -- caminho/do/arquivo
```

### Reverter tudo para um commit anterior
```bash
git -C /root/.openclaw/workspace reset --hard <commit>
```

## Rollback do state do OpenClaw
### Dry run
```bash
bash /root/.openclaw/workspace/scripts/restore_openclaw_backup.sh /root/openclaw-backups/<arquivo>.tar.gz
```

### Aplicar restore
```bash
bash /root/.openclaw/workspace/scripts/restore_openclaw_backup.sh /root/openclaw-backups/<arquivo>.tar.gz --apply
```

## Estratégia de reversão recomendada
1. identificar o último backup bom em `backups/latest-structural-backup.json`
2. conferir integridade com `openclaw backup verify`
3. reverter workspace via git, se o problema estiver só em arquivo versionado
4. restaurar `/root/.openclaw` pelo script, se o problema estiver em config, cron, credencial ou state do gateway
5. validar com:
```bash
openclaw status
openclaw doctor --non-interactive
```

## Observação importante
Rollback de jobs com side effect externo pode repetir envio se a automação não for idempotente. Em falha ambígua de email/mensagem, preferir revisão humana antes de retry cego.
