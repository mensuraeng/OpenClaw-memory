---
name: hostinger-vps-snapshot
description: Consultar ou criar snapshot manual da VPS Hostinger com segurança. Use para checar snapshot Hostinger, criar snapshot antes de update/mudança estrutural do OpenClaw, ou acionar rotina diária de snapshot. Nunca restaura ou apaga snapshots.
---

# Hostinger VPS Snapshot

## Regras de segurança

- Snapshot Hostinger é rollback rápido, não substitui Backblaze B2 versionado.
- Criar snapshot novo sobrescreve o snapshot anterior.
- Nunca restaurar ou apagar snapshot por esta skill.
- Antes de update/mudança estrutural: consultar snapshot atual; se estiver velho/desalinhado, criar snapshot manual; depois rodar backup estrutural local/B2.
- Token e VM ID devem estar fora do Git, em `/root/.openclaw/.env` ou KeeSpace.

## Configuração necessária

Variáveis:

```bash
HOSTINGER_API_TOKEN=...
HOSTINGER_VM_ID=...
```

## Consultar snapshot atual

```bash
cd /root/.openclaw/workspace
python3 scripts/hostinger_snapshot_check.py --json
```

Interpretação:
- `ok`: snapshot consultado e recente conforme limiar.
- `stale`: snapshot antigo; considerar criar manual antes de update.
- `ok_unparsed`: API respondeu, mas data não foi interpretada automaticamente; verificar payload.
- `blocked`: faltam `HOSTINGER_API_TOKEN` ou `HOSTINGER_VM_ID`.
- `error`: falha de API/autenticação/rede.

## Criar snapshot manual

Exige confirmação explícita no comando:

```bash
cd /root/.openclaw/workspace
python3 scripts/hostinger_snapshot_create.py --yes --json
```

Evidência:
- `runtime/hostinger/snapshot-create-latest.json`
- `runtime/hostinger/snapshot-create-<timestamp>.json`

## Cron diário

Cron deve acionar esta skill/script no máximo uma vez por dia. Delivery só em falha ou estado que exija atenção. Não misturar com update OpenClaw no mesmo cron.
