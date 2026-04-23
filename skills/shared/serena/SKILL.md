---
name: serena
description: Análise semântica de codebase local via Serena MCP. Use para entender estrutura de projetos, buscar símbolos, analisar dependências, navegar em código. Ativa em pedidos como "analisa esse codebase", "onde está definido", "quem chama essa função", "estrutura do projeto", "busca no código".
---

# Serena — Semantic Codebase Analysis

Análise semântica e navegação inteligente em codebases locais via MCP.

## Configuração

- **MCP server:** `serena` (configurado em openclaw.json)
- **Comando:** `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`
- **Escopo:** Codebase local do projeto ativo

## MCP Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `list_dir` | Listar estrutura de diretório |
| `find_file` | Encontrar arquivos por padrão |
| `search_files_for_pattern` | Buscar padrão em arquivos |
| `read_file` | Ler conteúdo de arquivo |
| `get_symbols_overview` | Visão geral de símbolos do projeto |
| `find_symbol` | Encontrar definição de símbolo |
| `get_references` | Todas as referências a um símbolo |
| `get_call_graph` | Grafo de chamadas de função |

## Quando usar

- Entender estrutura de projeto desconhecido
- Encontrar onde uma função/classe está definida
- Rastrear todas as referências a um símbolo
- Analisar impacto de mudanças (quem usa esse módulo?)
- Refatoração: entender dependências antes de mudar

## Exemplos

```
# Visão geral do projeto
get_symbols_overview(path="/root/.openclaw/workspace/finance")

# Encontrar definição de função
find_symbol(name="calcular_margem")

# Todas as referências a um símbolo
get_references(symbol="IngestPipeline")
```

## Boas práticas

- Usar antes de qualquer refatoração significativa
- Combinar com Context7 para documentação externa
- Serena entende semântica — preferir sobre grep para navegação de código
