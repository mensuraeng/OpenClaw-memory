# msgraph CLI

CLI read-only para Microsoft Graph usando as configs locais Mensura/MIA/PCS.

## Comandos v0.1

```bash
./bin/msgraph status
./bin/msgraph health
./bin/msgraph inbox list --account mensura --limit 5
./bin/msgraph inbox read --account mensura --id <message-id>
./bin/msgraph inbox folders --account mensura
./bin/msgraph calendar list --account mensura --days 7
./bin/msgraph guardrails
```

## Guardrails

- Não envia email.
- Não move/arquiva/deleta email.
- Não cria/deleta/edita evento.
- Não baixa anexos no v0.1.
- Não imprime segredos.
