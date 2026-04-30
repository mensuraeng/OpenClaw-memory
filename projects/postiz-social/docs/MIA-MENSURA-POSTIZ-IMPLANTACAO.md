# Postiz Social Hub — MIA + MENSURA

## Objetivo

Centralizar agendamento/publicação social de MIA e MENSURA em Postiz self-hosted, preservando separação editorial e aprovação humana.

## URL inicial

- Tailscale/local: `http://100.124.198.120:4007`
- Produção recomendada após DNS/SSL: `https://social.mensuraengenharia.com.br`

## Workspaces a criar no primeiro acesso

1. `MIA Engenharia`
2. `MENSURA Engenharia`

## Regras

- MIA e MENSURA nunca compartilham calendário, copy, identidade ou campanha.
- Nenhuma publicação externa sem aprovação explícita do Alexandre.
- MIA: quiet luxury, governança patrimonial aplicada à construção.
- MENSURA: técnico-institucional, números antes de adjetivos, funil Marketing → CRM → reunião → diagnóstico → contrato.

## OAuth callbacks para configurar depois do domínio definitivo

Postiz exige URL pública HTTPS para OAuth estável.

### Instagram / Facebook Business

- `https://social.mensuraengenharia.com.br/integrations/social/instagram`
- `https://social.mensuraengenharia.com.br/integrations/social/instagram-standalone`

### LinkedIn

- `https://social.mensuraengenharia.com.br/integrations/social/linkedin`
- `https://social.mensuraengenharia.com.br/integrations/social/linkedin-page`

## Estado esperado

- Instagram oficial: depende de Meta App/Business Manager.
- LinkedIn página: depende de permissões LinkedIn/Community Management ou Advertising API conforme Postiz.
- Fallback temporário: publicação manual assistida.
