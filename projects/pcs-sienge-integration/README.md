# PCS Sienge Integration

Base inicial da integração PCS ↔ Sienge.

## Objetivo

Estruturar um conector limpo, auditável e expansível para os módulos de:
- cadastros mestres
- suprimentos
- financeiro

## Estrutura inicial

```text
src/
  pcs_sienge/
    config.py
    auth.py
    client.py
    errors.py
    models.py
    endpoints/
    normalizers/
    storage/
    jobs/
```

## Estado atual

- arquitetura funcional definida
- documentação do MVP consolidada
- autenticação adaptada para OAuth2 com `Basic Auth + client_credentials`
- tenant PCS confirmado: `pcsservices`
- endpoints reais confirmados para token e API REST
- ainda falta a senha gerada do usuário de API e a liberação dos recursos certos

## Configuração esperada

Arquivo: `/root/.openclaw/workspace/config/sienge-pcs.json`

Campos mínimos:
- `companyName`
- `companyId`
- `timezone`
- `subdomain`
- `authType`
- `apiUserName`
- `apiUserId`
- `username`
- `password`
- `tokenUrl`
- `apiBaseUrl`
- `timeoutSeconds`

## O que já está confirmado

- URL base do tenant: `https://pcsservices.sienge.com.br`
- empresa: `PCS OBRAS E LOCAÇÕES LTDA`
- slug do tenant: `pcsservices`
- usuário de API ativo: `project`
- username de auth: `pcsservices-project`
- UUID do usuário de API: `b286dd06-dac8-4ed0-83d3-a8c4f514a61a`
- company UUID: `2c30d0c5-db58-440a-837c-6e61f231b855`
- fluxo de auth: `OAuth2` com `Authorization: Basic base64(username:password)` e body `grant_type=client_credentials`
- endpoint de token: `POST https://pcsservices.sienge.com.br/sienge/oauth/token`
- endpoint REST base: `https://pcsservices.sienge.com.br/sienge/api/v1`

## Próximo passo operacional

Para validar a integração real agora, faltam somente:
1. gerar e copiar a senha do usuário `project`
2. habilitar os recursos realmente necessários para a integração
3. confirmar o primeiro endpoint liberado para teste real

Leitura honesta: hoje os módulos críticos da integração ainda estão bloqueados. Só há autorização para recursos de obra/planejamento.
