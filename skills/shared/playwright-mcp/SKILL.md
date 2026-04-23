---
name: playwright-mcp
description: Browser automation via Playwright MCP server. Use para controlar browsers, navegar em páginas, preencher formulários, tirar screenshots, executar JavaScript no browser. Ativa em pedidos como "abre o browser", "navega para", "clica em", "preenche formulário", "screenshot da página", "automatiza browser".
---

# Playwright MCP — Browser Automation

Controle completo de browser via Model Context Protocol.

## Configuração

- **MCP server:** `playwright` (configurado em openclaw.json)
- **Comando:** `npx -y @playwright/mcp@latest`
- **Browser:** Chromium (headless por padrão)

## MCP Tools disponíveis

| Tool | Descrição |
|------|-----------|
| `browser_navigate` | Navegar para URL |
| `browser_click` | Clicar em elemento (seletor CSS) |
| `browser_type` | Digitar texto em campo |
| `browser_screenshot` | Capturar screenshot |
| `browser_evaluate` | Executar JavaScript na página |
| `browser_wait_for_selector` | Aguardar elemento aparecer |
| `browser_get_text` | Extrair texto de elemento |
| `browser_scroll` | Rolar página |
| `browser_fill` | Preencher campo de formulário |
| `browser_select_option` | Selecionar opção em dropdown |
| `browser_go_back` | Voltar na navegação |
| `browser_close` | Fechar browser |

## Quando usar

- Sites que requerem JavaScript para renderizar conteúdo
- Login e navegação em sistemas autenticados
- Preenchimento de formulários complexos
- Screenshots de páginas para documentação
- Web scraping de SPAs (Single Page Applications)

## Exemplos

```
# Login em sistema
browser_navigate(url="https://app.exemplo.com/login")
browser_fill(selector="#email", value="user@email.com")
browser_fill(selector="#password", value="senha")
browser_click(selector="button[type=submit]")
browser_wait_for_selector(selector=".dashboard")

# Screenshot
browser_screenshot(path="/tmp/screenshot.png")
```

## Boas práticas

- Usar seletores CSS específicos e estáveis
- Adicionar `wait_for_selector` após navegações
- Preferir Firecrawl para scraping simples (mais rápido)
- Usar Playwright apenas quando precisar de interação/JavaScript
