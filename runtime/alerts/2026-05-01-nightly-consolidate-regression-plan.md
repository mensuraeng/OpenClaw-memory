# Plano de contenção — regressão nightly_consolidate

Criado em: 2026-05-01

## Problema

O cron diário abaixo executa às 01:00 BRT e roda um script legado que sobrescreve arquivos canônicos do 2nd-brain a partir de `workspace/memory/context`:

```cron
0 1 * * * python3 /root/.openclaw/workspace/projects/openclaw-memory/scripts/nightly_consolidate.py >> /root/.openclaw/logs/openclaw-consolidate.log 2>&1
```

Arquivos afetados no commit `3acc806 nightly: sync 2026-05-01`:

- `/root/2nd-brain/02-context/pending.md`
- `/root/2nd-brain/02-context/decisions.md`
- `/root/2nd-brain/02-context/lessons.md`

Versão boa conhecida: `44c2ce9`.

## Causa raiz

`nightly_consolidate.py` copia:

```text
/root/.openclaw/workspace/memory/context/{pending,decisions,lessons}.md
```

para:

```text
/root/2nd-brain/02-context/{pending,decisions,lessons}.md
```

Isto inverte a fonte de verdade atual. O 2nd-brain deve vencer o workspace legado, não o contrário.

## Correção recomendada

1. Fazer backup estrutural/local antes de alterar automação.
2. Alterar `nightly_consolidate.py` para nunca sobrescrever `2nd-brain/02-context` a partir do workspace legado.
3. Restaurar os três arquivos canônicos de `44c2ce9`.
4. Commitar restauração no 2nd-brain.
5. Rodar validações:

```bash
git -C /root/2nd-brain diff --stat 3acc806..HEAD -- 02-context/pending.md 02-context/decisions.md 02-context/lessons.md
python3 /root/2nd-brain/_system/validate_inbox_sidecars.py
python3 /root/.openclaw/workspace/scripts/operational_health.py
```

## Comandos candidatos — não executar sem confirmação

```bash
bash /root/.openclaw/workspace/scripts/backup_before_change.sh nightly-consolidate-regression-2026-05-01
```

```bash
git -C /root/2nd-brain checkout 44c2ce9 -- 02-context/pending.md 02-context/decisions.md 02-context/lessons.md
git -C /root/2nd-brain add 02-context/pending.md 02-context/decisions.md 02-context/lessons.md
git -C /root/2nd-brain commit -m "restore: recover context files after nightly regression"
```

## Status

Aguardando confirmação humana para mudança estrutural de automação e restauração de memória central.
