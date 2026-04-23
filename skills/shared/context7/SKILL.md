---
name: context7
description: Documentação em tempo real de bibliotecas e frameworks via Context7 MCP. Use para buscar documentação atualizada de libs, exemplos de código, APIs de frameworks. Ativa em pedidos como "como usar [biblioteca]", "documentação do [framework]", "exemplo de código para", "latest docs de".
---

# Context7 — Real-Time Library Documentation

Acesso a documentação atualizada de bibliotecas e frameworks no contexto de desenvolvimento.

## Configuração

- **MCP server:** `context7` (configurado em openclaw.json)
- **Comando:** `npx -y @upstash/context7-mcp@latest`

## MCP Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `resolve-library-id` | Encontrar ID correto de uma biblioteca |
| `get-library-docs` | Buscar documentação com query específica |

## Quando usar

- Antes de usar qualquer biblioteca/framework não familiar
- Verificar APIs mais recentes (evita usar métodos deprecated)
- Buscar exemplos práticos de integração
- Documentação de: React, Next.js, Prisma, FastAPI, n8n, etc.

## Fluxo recomendado

```
1. resolve-library-id(libraryName="fastapi")
2. get-library-docs(
     context7CompatibleLibraryID="/tiangolo/fastapi",
     topic="authentication JWT"
   )
3. Usar documentação no código
```

## Boas práticas

- Queries específicas retornam resultados mais úteis que buscas genéricas
- Combinar com Serena para documentação externa + análise do codebase local
- Para libs locais/privadas, usar Serena em vez de Context7
