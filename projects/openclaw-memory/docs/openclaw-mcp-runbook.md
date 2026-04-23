# OpenClaw MCP bridge — runbook

**Instalado em:** 2026-04-21
**Finalidade:** expor o workspace do OpenClaw (memória, projetos, crons, NotebookLM) como ferramentas MCP read-only, para que o Google Antigravity (rodando na Windows do Alê) consuma contexto da operação ao redigir relatórios e executar tarefas do dia-a-dia.

## Arquitetura

```
   ┌──────────────────────────────┐
   │  Windows (alesurface)        │
   │  ┌────────────────────────┐  │
   │  │  Google Antigravity    │  │   Tailscale
   │  │    MCP client ─────────┼──┼──────────────┐
   │  └────────────────────────┘  │              │
   └──────────────────────────────┘              │
                                                 ▼
   ┌─────────────────────────────────────────────────────────┐
   │  Linux server (srv1546384, 100.124.198.120)             │
   │                                                         │
   │  openclaw-mcp.service  (systemd, auto-restart)          │
   │    └─ FastMCP Streamable-HTTP @ 100.124.198.120:5800    │
   │                                                         │
   │       Tools (read-only):                                │
   │         list_projects          notebooklm_inventory     │
   │         read_project           notebooklm_read_note     │
   │         read_memory            list_crons               │
   │         list_memory            search_knowledge         │
   │                                                         │
   │  Backend: /root/.openclaw/workspace/ (same repo que     │
   │    sincroniza via cron diário com GitHub).              │
   └─────────────────────────────────────────────────────────┘
```

**Segurança** — o servidor faz bind apenas na interface Tailscale (`100.124.198.120`). Não é alcançável do IPv4 público (`76.13.161.249`). Somente dispositivos no seu tailnet (`aa.mensura@`) conseguem abrir o socket.

## Configuração no Antigravity (Windows)

O arquivo `mcp_config.json` do Antigravity fica em:

```
C:\Users\<você>\.gemini\antigravity\mcp_config.json
```

Adicione o entry `openclaw` (coexistindo com os que já estiverem lá):

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "http://100.124.198.120:5800/mcp",
        "--transport",
        "http-only"
      ],
      "disabled": false
    }
  }
}
```

Por que `mcp-remote` e não `serverUrl` direto: o Antigravity no launch priorizou configs que passam por um shim (`npx mcp-remote`) para bridges HTTP que não usam OAuth. É o padrão atualmente documentado pela comunidade para servers MCP locais/privados.

Depois de salvar o arquivo, reinicie o Antigravity. O servidor "openclaw" deve aparecer na lista de MCP servers dentro do IDE (geralmente em Settings → MCP).

## Testar do lado do Antigravity

No chat do Antigravity, peça:

> "Use openclaw para listar os projetos rastreados na memória."

Ou algo mais direto:

> "Puxe o último relatório da CCSP Casa 7 de openclaw.read_project('ccsp-casa7') e me gere um resumo executivo."

## Ferramentas expostas

| Tool | O que faz | Args |
|---|---|---|
| `list_projects` | Lista todos os projetos em `memory/projects/` | — |
| `read_project(name)` | Lê todos os `.md` do projeto (concat) | `name: str` |
| `list_memory(path="")` | Lista arquivos numa pasta de memória | `path?: str` |
| `read_memory(path)` | Lê um arquivo relativo a `memory/`, max 500 KB | `path: str` |
| `search_knowledge(query, limit=30)` | Busca ripgrep no workspace inteiro | `query: str, limit?: int` |
| `list_crons` | Lista jobs cron do OpenClaw com schedule e status | — |
| `notebooklm_inventory` | Lista notebooks do NotebookLM com contagem de notas | — |
| `notebooklm_read_note(notebook_id, note_id)` | Lê nota específica | `notebook_id: str, note_id: str` |

### Guardas

- `read_memory` / `list_memory` / `read_project` rejeitam paths que escapam de `memory/` (tentativa com `../` retorna erro).
- Leitura cap em 500 KB por chamada — output maior é truncado com marca `[truncated at 500 KB]`.
- `search_knowledge` limita query a 200 chars e limit a 200.
- Sem ferramentas de escrita. Sem shell.

## Operação

### Status

```bash
systemctl status openclaw-mcp.service
ss -tlnp | grep 5800
journalctl -u openclaw-mcp.service -n 30 --no-pager
```

### Testar do lado Linux (fora do Antigravity)

```bash
/root/.openclaw/venvs/mcp/bin/python -c "
import asyncio
from fastmcp import Client
async def main():
    async with Client('http://100.124.198.120:5800/mcp') as c:
        print([t.name for t in await c.list_tools()])
asyncio.run(main())
"
```

### Reiniciar após mudança no `openclaw_mcp.py`

```bash
systemctl restart openclaw-mcp.service
```

### Adicionar uma ferramenta nova

1. Edite `scripts/openclaw_mcp.py`, adicione uma função decorada com `@mcp.tool(description=...)`.
2. Aplique guardrails (use `_safe_under` para paths).
3. `systemctl restart openclaw-mcp.service`.
4. Commit + push — `backup_workspace.sh` às 02:15 publica automaticamente, ou manual.

### Desabilitar temporariamente

```bash
systemctl disable --now openclaw-mcp.service
```

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Antigravity não enxerga o server | `mcp_config.json` mal formado, ou Antigravity não reiniciado | Validar JSON, reiniciar Antigravity |
| Timeout na primeira chamada | Tailscale caiu do lado Windows | `tailscale status` em ambos |
| `ToolError: ripgrep não instalado` | Servidor sem `rg` | `apt install ripgrep` |
| `path ... escapes allowed root` | Cliente pediu path fora de `memory/` | Corrigir path; é feature, não bug |
| Processo restartando em loop | Ver `journalctl -u openclaw-mcp -n 50` |

## Evoluções futuras

- **Escrita** — `write_memory(path, content)` e `append_memory_day(fact)` depois de 1-2 semanas de uso estável (pra Antigravity gravar conclusões diretamente na memória).
- **Auth por bearer token** — quando/se o servidor deixar de ser exclusivamente tailnet.
- **Resources** — expor `openclaw://memory/...` como MCP resources (além de tools), permitindo Antigravity "anexar" arquivos como contexto.
- **Ferramentas de projeto específicas** — e.g., `ccsp_casa7_latest_report()`, `mensura_financial_summary()`, para atalhos usados no dia-a-dia.
