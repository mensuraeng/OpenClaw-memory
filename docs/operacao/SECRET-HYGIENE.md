# Secret Hygiene

Atualizado em 2026-04-30.

## Objetivo

Varredura segura de possíveis segredos no workspace e no `2nd-brain`, sem imprimir valores reais.

## Script

```bash
python3 scripts/secret_hygiene.py --workspace --json
python3 scripts/secret_hygiene.py --workspace --second-brain --json
```

Saídas:

- `runtime/secret-hygiene/latest.json`
- `runtime/secret-hygiene/latest.md`
- `runtime/secret-hygiene/secret-hygiene-<timestamp>.json`
- `runtime/secret-hygiene/secret-hygiene-<timestamp>.md`

## Guardrails

- Não imprime valores reais de segredo.
- Usa fingerprint hash de valor canonicalizado por `trim`.
- Não faz chamada externa.
- Não executa ação destrutiva.
- Rebaixa fixtures de teste para revisão quando detecta tokens sintéticos em arquivos de teste.
- Ignora diretórios pesados/ruidosos como `.git`, `node_modules`, `.venvs`, `site-packages`, backups e artefatos runtime.

## O que detecta

- chaves OpenAI;
- tokens GitHub;
- tokens Slack;
- Google API keys;
- AWS access keys;
- headers de chave privada;
- atribuições genéricas sensíveis (`token`, `secret`, `api_key`, `password`, etc.).

## Status atual

Última validação do workspace antes da correção: `block` por chave privada GA4 em `credentials/`.

Correção aplicada em 2026-05-01:

- removidos do workspace `credentials/ga4-service-account.json` e `credentials/ga_service_account.json`;
- service account consolidada como fallback local root-owned `0600` em `/root/.secrets/ga4-service-account.json`;
- consumidores atualizados para ler `GA4_SERVICE_ACCOUNT_FILE` ou fallback `/root/.secrets/ga4-service-account.json`.

## Próximo passo recomendado

Migrar também o arquivo de service account GA4 para entrada KeeSpace/KeePassXC quando o cofre estiver desbloqueado. Até lá, o segredo saiu do workspace e permanece como fallback local controlado.
