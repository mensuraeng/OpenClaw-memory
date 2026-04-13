# Matriz de Permissões da V1

_Data: 2026-04-13_

## Leitura Permitida
- host metrics aprovadas  
- agents inventory  
- recent sessions sanitizadas  
- cron jobs/status  
- docs allowlisted  
- memory allowlisted  
- config/log excerpts allowlisted  

## Leitura Proibida
- leitura completa de config sensível  
- leitura irrestrita de logs brutos  
- navegação livre no filesystem  
- qualquer path fora da allowlist  

## Ações Leves Permitidas
- refresh manual  
- ack de alerta  
- copiar comando seguro  
- abrir link interno  
- rerun de coleta safe explicitamente allowlisted  

## Ações Proibidas
- terminal web  
- shell arbitrário  
- reinício irrestrito de serviço  
- edição ampla de arquivos  
- edição de arquivos-raiz sensíveis  
- ações destrutivas  
