---
name: ghost-cms
description: Gerenciamento de conteúdo e blog via Ghost CMS (http://localhost:2368). Use para criar posts, atualizar conteúdo, gerenciar tags e autores, publicar artigos. Ativa em pedidos como "cria um post no blog", "lista os artigos do Ghost", "publica conteúdo", "atualiza post".
---

# Ghost CMS — Content Management

Acesso completo à instância Ghost local via Admin API.

## Configuração

- **Admin API URL:** `http://localhost:2368/ghost/api/admin/`
- **Content API URL:** `http://localhost:2368/ghost/api/content/`
- **Painel web:** http://localhost:2368/ghost

### Obter API Key
```bash
# Via painel: Settings → Integrations → Add Custom Integration
# Ou verificar no banco MySQL:
docker exec ghost_mysql mysql -u ghost -pghostpassword ghost \
  -e "SELECT name, secret FROM api_keys LIMIT 10;" 2>/dev/null
```

## Endpoints Admin API

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | `/posts/` | Listar posts |
| POST | `/posts/` | Criar post |
| PUT | `/posts/{id}/` | Atualizar post |
| DELETE | `/posts/{id}/` | Deletar post |
| GET | `/pages/` | Listar páginas |
| POST | `/pages/` | Criar página |
| GET | `/tags/` | Listar tags |
| POST | `/tags/` | Criar tag |
| GET | `/authors/` | Listar autores |
| POST | `/images/upload/` | Upload de imagem |

## Quando usar

- Criar e publicar artigos de blog
- Atualizar conteúdo existente
- Gerenciar tags e categorias
- Automatizar publicação de conteúdo gerado por IA
- Integrar pipeline: IA gera conteúdo → Ghost publica → Postiz distribui

## Pipeline típico

```
IA gera artigo
  → POST /ghost/api/admin/posts/ (status: draft)
  → Revisar no painel Ghost
  → PUT /posts/{id}/ (status: published)
  → Postiz distribui nas redes sociais
```

## Boas práticas

- Sempre criar posts como `draft` primeiro para revisão
- Usar tags consistentes para organizar conteúdo
- Imagens: fazer upload via `/images/upload/` antes de referenciar
- Integrar com n8n para automação de publicação agendada
