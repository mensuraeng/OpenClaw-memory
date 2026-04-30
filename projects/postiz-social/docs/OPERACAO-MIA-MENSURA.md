# Operação Postiz — MIA + MENSURA

## Serviço

```bash
cd /root/.openclaw/workspace/projects/postiz-social
docker compose ps
docker compose logs --tail=120 postiz
docker compose restart postiz
```

## Endereço atual

- `http://100.124.198.120:4007`

Este endereço está em Tailscale/local. OAuth público estável exigirá domínio HTTPS.

## Workspaces

Criar no primeiro acesso:

1. `MIA Engenharia`
2. `MENSURA Engenharia`

Não misturar canais, copies, calendários ou assets entre workspaces.

## Segurança

Depois que o primeiro administrador for criado:

1. editar `/root/.openclaw/workspace/projects/postiz-social/docker-compose.yml`
2. trocar `DISABLE_REGISTRATION: 'false'` para `DISABLE_REGISTRATION: 'true'`
3. rodar:

```bash
cd /root/.openclaw/workspace/projects/postiz-social
docker compose up -d
```

## Domínio/SSL recomendado

Opção pragmática inicial: hub único.

- `social.mensuraengenharia.com.br` → `127.0.0.1:4007` ou `100.124.198.120:4007`

Callbacks Postiz:

- Instagram: `/integrations/social/instagram`
- Instagram Standalone: `/integrations/social/instagram-standalone`
- LinkedIn profile: `/integrations/social/linkedin`
- LinkedIn page: `/integrations/social/linkedin-page`

## Observação de recurso

Postiz + Temporal + Elasticsearch é pesado para o VPS atual. Por isso foi implantado um hub único com workspaces separados, não duas pilhas duplicadas. Se houver crescimento, migrar Postiz para VPS maior ou separar instâncias.
