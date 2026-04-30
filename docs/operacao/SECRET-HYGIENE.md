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

Última validação do workspace: `block`.

Achado crítico real, sem valores expostos:

- `credentials/ga4-service-account.json`
- `credentials/ga_service_account.json`

Ambos contêm header de chave privada e estão com permissão local `600`. Não aparecem como rastreados pelo Git no check realizado, mas devem continuar fora de commit e idealmente migrar para KeeSpace/cofre ou manter como fallback local explicitamente aceito.

## Próximo passo recomendado

Decidir se esses dois arquivos de service account permanecem como fallback local aceito ou se serão migrados para KeeSpace. Até essa decisão, Secret Hygiene deve permanecer em `block`, não `pass`.
