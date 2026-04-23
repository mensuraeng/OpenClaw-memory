# Estado operacional - Antigravity MCP

_Atualizado em 2026-04-21 13:58 BRT_

## Objetivo
Manter a conexão do Antigravity com o MCP do OpenClaw funcionando corretamente pela tailnet, sem diagnosticar errado scaffold/adapter quando o problema real for transporte HTTP privado.

## Estado operacional atual
- status: **bloqueado com causa real**
- diagnóstico: **executado e validado**
- documentação do ajuste: **executada**
- aplicação do ajuste no ambiente Windows do Antigravity: **ainda não executada aqui**

## Capacidade validada
### Ferramenta: conexão remota MCP via `mcp-remote`
- padrão: usar `mcp-remote` com endpoint tailnet e flags corretas de transporte
- fallback: revalidar conectividade/URL/transport antes de recriar MCP ou alterar scaffold
- nível de productização: diagnóstico operacional validado, mas aplicação live ainda depende do ambiente Windows onde o Antigravity roda
- limitações: endpoint HTTP privado exige flag explícita de allow-http
- última validação real: 2026-04-21
- evidência: erro reproduzido `Non-HTTPS URLs are only allowed for localhost or when --allow-http`

## Configuração correta
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
        "http-only",
        "--allow-http"
      ],
      "disabled": false
    }
  }
}
```

## Bloqueio real atual
- o ajuste ainda não foi aplicado no `mcp_config.json` do Windows/Antigravity
- sem acesso/aplicação nesse ambiente, não há como marcar a frente como executada

## Próximo passo correto
1. aplicar a configuração correta no Antigravity
2. reiniciar o Antigravity
3. validar conexão MCP real
4. só então promover o estado para executado
