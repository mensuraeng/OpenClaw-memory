# Claude Code — Integração local

Quando precisar de análise técnica profunda, posso consultar
o Claude Code instalado localmente na VPS.

## Quando usar
- Analisar scripts Python com erro
- Revisar configuração do OpenClaw
- Diagnosticar problema em arquivo de config
- Propor correção em código existente

## Como usar
Internamente executo:
python3 scripts/consultar_claude_code.py --prompt "<consulta>"

## Limites
- Timeout: 120 segundos
- Modo: plan only (não executa comandos diretamente)
- Sem acesso a credenciais ou arquivos sensíveis
