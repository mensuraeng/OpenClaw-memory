# KeeSpace — Protocolo de Segredos Operacionais

_Atualizado: 2026-04-28_

## Princípio

KeeSpace/KeePassXC é o cofre oficial. Workspace, 2nd-brain e memória não devem guardar tokens, API keys, webhooks secretos ou senhas em texto.

## Estado atual

- Este protocolo é o mapa para todos os agentes. Se um agente precisar de credencial, ele deve começar por este arquivo e pelo mapa `/root/.openclaw/workspace/memory/integrations/credentials-map.md`.
- Vault local detectado: `/root/.secrets/flavia-vault.kdbx`
- CLI disponível: `keepassxc-cli`
- Camada de resolução criada: `scripts/secret_config.py`
- Configs comerciais redigidas para referências:
  - `config/hubspot-mensura.json`
  - `config/phantombuster-mensura.json`
- Fallback temporário local, fora do workspace: `/root/.secrets/openclaw-commercial.env` com permissão `0600`
- Fallback LinkedIn local, fora do workspace: `/root/.secrets/openclaw-linkedin.env` com permissão `0600`
- Fallback PCS/Sienge local, fora do workspace: `/root/.secrets/sienge-pcs.env` com permissão `0600` até gravação no KeeSpace/KeePassXC

## Caminho final

Mover os segredos do fallback temporário para KeeSpace nas entradas:

| Segredo | Env | Entrada KeeSpace sugerida |
|---|---|---|
| HubSpot MENSURA access token | `HUBSPOT_MENSURA_ACCESS_TOKEN` | `OpenClaw/MENSURA/HubSpot/access-token` |
| Make webhook comercial | `HUBSPOT_MENSURA_MAKE_WEBHOOK` | `OpenClaw/MENSURA/Make/webhook-mensura-commercial` |
| Phantombuster API key | `PHANTOMBUSTER_MENSURA_API_KEY` | `OpenClaw/MENSURA/Phantombuster/api-key` |
| LinkedIn MENSURA token pessoal | `LINKEDIN_MENSURA_ACCESS_TOKEN` | `OpenClaw/MENSURA/LinkedIn/personal-access-token` |
| PCS Sienge basic auth | `SIENGE_PCS_USERNAME` / `SIENGE_PCS_PASSWORD` | `OpenClaw/PCS/Sienge/api-basic` |

## Como o resolver funciona

`secret_config.py` resolve referências com prioridade para KeeSpace quando a entrada existir no config:

1. KeePassXC/KeeSpace, se houver acesso via env:
   - `KEEPASSXC_DATABASE` ou `KEESPACE_DATABASE`
   - `KEEPASSXC_PASSWORD_FILE` ou `KEESPACE_PASSWORD_FILE`, se necessário
   - `KEEPASSXC_KEY_FILE` ou `KEESPACE_KEY_FILE`, se necessário
2. variável de ambiente direta;
3. arquivo local root-owned (`/root/.secrets/openclaw-commercial.env` e equivalentes durante migração), somente se `OPENCLAW_SECRET_MODE` permitir fallback.

Modos suportados:
- `OPENCLAW_SECRET_MODE=keespace`: exige KeeSpace/env do processo; não carrega fallback local.
- `OPENCLAW_SECRET_MODE=env`: usa somente env já exportado no processo; não carrega fallback local.
- `OPENCLAW_SECRET_MODE=fallback` ou vazio: permite fallback local `0600` para compatibilidade temporária.

## Validação

```bash
python3 scripts/secret_config.py config/hubspot-mensura.json --check
python3 scripts/secret_config.py config/phantombuster-mensura.json --check
python3 scripts/secret_config.py config/linkedin-mensura.json --check
```

Saída esperada: `ok: true` e `plaintext_secret_paths: []`.

## Regra operacional

- Novo segredo nunca entra em `config/*.json` como valor literal.
- Config deve guardar referência `env` + entrada KeeSpace sugerida.
- Se uma automação precisar de segredo e ele não resolver, ela deve falhar fechado, sem tentar ação externa parcial.
- Rotação de tokens deve atualizar KeeSpace/fallback local, não código nem memória.
- Nenhum agente deve pedir token em chat nem copiar segredo para resposta. Se faltar acesso, pedir desbloqueio/entrada no KeeSpace, não o valor do segredo.

## Como outros agentes encontram

1. Ler `/root/.openclaw/workspace/memory/context/mapa-agentes.md` para a regra geral.
2. Ler este arquivo para o protocolo.
3. Ler `/root/.openclaw/workspace/memory/integrations/credentials-map.md` para saber onde cada integração vive.
4. Usar `scripts/secret_config.py` quando houver config com referência `env`/KeeSpace.

## Pendência para 100% KeeSpace puro

Remover os fallbacks `/root/.secrets/openclaw-commercial.env`, `/root/.secrets/openclaw-linkedin.env`, `/root/.secrets/make.env`, `/root/.secrets/notion.env` e `/root/.secrets/sienge-pcs.env` depois que o vault estiver acessível por KeePassXC/KeeSpace no runtime. Até lá, o risco saiu do workspace/versionamento, mas ainda existe segredo local temporário.

Para modo KeeSpace puro, exportar no runtime:

```bash
export OPENCLAW_SECRET_MODE=keespace
export KEESPACE_DATABASE=/root/.secrets/flavia-vault.kdbx
# export KEESPACE_PASSWORD_FILE=/path/root-owned/0600/password-file   # se usado
# export KEESPACE_KEY_FILE=/path/root-owned/0600/key-file             # se usado
```
