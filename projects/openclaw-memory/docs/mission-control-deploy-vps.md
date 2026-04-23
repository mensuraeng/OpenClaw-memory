# Deploy do Mission Control no VPS

_Data: 2026-04-13_

## Introdução
Documentar o processo de deploy para o Mission Control utilizando acesso Tailscale, garantindo segurança e controle.

### Bind Restrito
- O serviço deve escutar apenas na interface/bind aprovado.  
- Acesso deve ser apenas via Tailscale, sem exposição pública.

### Variáveis Críticas de Auth
- APP_SECRET  
- senha/admin auth  
- cookie seguro  
- rate limit config  
