---
name: firecrawl
description: Web scraping e crawling avançado via Firecrawl (http://localhost:3002). Use para extrair conteúdo de páginas web, fazer crawl de sites, mapear estrutura de domínios, pesquisar na web. Ativa em pedidos como "scrape esse site", "extrai o conteúdo de", "crawl desse domínio", "mapa do site". MCP server configurado como firecrawl e firecrawl-mcp em openclaw.json.
---

# Firecrawl — Advanced Web Scraping

Acesso à instância Firecrawl local para scraping, crawling e mapeamento de sites.

## Configuração

- **URL base:** `http://localhost:3002`
- **Auth:** `Authorization: Bearer mensura-2026`
- **MCP servers:** `firecrawl` e `firecrawl-mcp` (configurados em openclaw.json)
- **Stack Docker:** firecrawl + firecrawl-redis + firecrawl-postgres + firecrawl-rabbit

## Endpoints REST

| Método | Endpoint | Uso |
|--------|----------|-----|
| POST | `/v1/scrape` | Extrair conteúdo de uma URL |
| POST | `/v1/crawl` | Crawl recursivo de um domínio |
| GET | `/v1/crawl/{id}` | Status de crawl assíncrono |
| POST | `/v1/map` | Mapa de URLs de um domínio |
| POST | `/v1/search` | Pesquisa web (se configurado) |

## MCP Tools disponíveis

- `firecrawl_scrape` — scrape de URL única
- `firecrawl_crawl` — crawl de domínio
- `firecrawl_map` — mapa de site
- `firecrawl_search` — pesquisa web

## Quando usar

- Extrair conteúdo de páginas para análise
- Monitorar sites de concorrentes
- Coletar dados de pesquisa
- Alimentar pipelines de análise com conteúdo web

## Exemplos

```bash
# Scrape de URL
curl -s -X POST http://localhost:3002/v1/scrape \
  -H "Authorization: Bearer mensura-2026" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com", "formats": ["markdown"]}'

# Mapa de site
curl -s -X POST http://localhost:3002/v1/map \
  -H "Authorization: Bearer mensura-2026" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com"}'
```

## Troubleshooting

Se container em restart loop:
```bash
docker logs firecrawl --tail 30
# O worker nuq-prefetch-worker depende do RabbitMQ estar pronto
docker restart firecrawl-rabbit && sleep 15 && docker restart firecrawl
```

## Boas práticas

- Preferir MCP tools quando disponível (mais estável que REST direto)
- Para crawls grandes, usar endpoint assíncrono e checar status
- Usar `formats: ["markdown"]` para conteúdo limpo
- Limitar `maxDepth` para evitar crawls infinitos
