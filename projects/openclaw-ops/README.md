# openclaw-ops

CLI operacional read-only para saúde da operação OpenClaw.

## Comandos v0.1

```bash
./bin/openclaw-ops status
./bin/openclaw-ops health
./bin/openclaw-ops crons logs
./bin/openclaw-ops cost daily
./bin/openclaw-ops backup status
./bin/openclaw-ops cleanup dry-run
./bin/openclaw-ops guardrails
```

Todos os comandos principais aceitam `--json` quando aplicável.

## Guardrails

- Não reinicia gateway/serviços.
- Não altera config.
- Não roda update.
- Não apaga/pruna arquivos.
- Não envia mensagens externas.
- Não faz restore/rollback.
- Limpeza é apenas diagnóstico `cleanup dry-run`.

Para crons, a fonte autoritativa segue sendo a ferramenta nativa `cron`; esta CLI v0.1 apenas inventaria logs locais.
