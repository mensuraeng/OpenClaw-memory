---
name: github-mcp
description: Operações GitHub via MCP (issues, PRs, repositórios, commits, branches). Use para criar issues, abrir PRs, buscar repositórios, revisar código, gerenciar branches. Ativa em pedidos como "cria issue no GitHub", "abre PR", "busca repositório", "lista commits", "revisa PR".
---

# GitHub MCP — GitHub Operations

Acesso completo ao GitHub via Model Context Protocol.

## Configuração

- **MCP server:** `github` (configurado em openclaw.json)
- **Auth:** GITHUB_PERSONAL_ACCESS_TOKEN em openclaw.json → mcp.servers.github.env
- **Scopes necessários:** `repo`, `read:org`, `gist`

### Configurar token
```bash
# Editar /root/.openclaw/openclaw.json
# Substituir PLACEHOLDER_TOKEN por token real:
# "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_SEU_TOKEN_AQUI"
```

## MCP Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `create_issue` | Criar issue em repositório |
| `list_issues` | Listar issues |
| `update_issue` | Atualizar issue |
| `create_pull_request` | Abrir Pull Request |
| `list_pull_requests` | Listar PRs |
| `get_pull_request` | Detalhes de PR |
| `merge_pull_request` | Fazer merge de PR |
| `search_repositories` | Buscar repositórios |
| `get_file_contents` | Ler conteúdo de arquivo |
| `create_or_update_file` | Criar/atualizar arquivo |
| `list_commits` | Listar commits |
| `create_branch` | Criar branch |
| `list_branches` | Listar branches |
| `search_code` | Buscar código no GitHub |

## Quando usar

- Gerenciar issues e backlog de projetos
- Abrir PRs para code review
- Automatizar criação de issues a partir de logs/erros
- Buscar exemplos de código em repositórios públicos
- Auditar histórico de commits

## Exemplos

```
# Criar issue
create_issue(
  owner="mensura-team",
  repo="meu-projeto",
  title="Bug: erro ao processar CSV",
  body="Descrição detalhada..."
)

# Abrir PR
create_pull_request(
  owner="mensura-team", repo="meu-projeto",
  title="feat: pipeline de dados",
  head="feature/pipeline", base="main",
  body="## Changes\n- Nova funcionalidade..."
)
```

## Boas práticas

- Sempre criar branch antes de fazer mudanças
- Issues: usar labels (bug, feature, docs)
- PRs: incluir description clara com contexto
- Token com escopo mínimo necessário
- Nunca commitar secrets no repositório
