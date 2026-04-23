# Notion — Flávia Edition

Skill para operar Notion como base de trabalho real da operação, não como repositório solto.

## Objetivo

Usar Notion para:
- reuniões
- kanban
- base de conteúdo
- CRM
- páginas operacionais por empresa

## Workspaces/integrations atuais

- `OpenClaw - Mensura`
- `OpenClaw - MIA Engenharia`
- `OpenClaw - PCS Engenharia`

As API keys ficam no **KeePassXC**.

## Regra crítica

A API do Notion **não enxerga tudo automaticamente**.
Para funcionar, a página ou database precisa ser compartilhada com a integração correta.

## Fluxo correto

### 1. Identificar workspace certo
Antes de consultar ou gravar, definir qual integração usar:
- Mensura
- MIA Engenharia
- PCS Engenharia

### 2. Confirmar acesso
Se a página/database não aparecer:
- verificar se foi compartilhada com a integração
- não assumir que a API falhou

### 3. Operações prioritárias
- encontrar última reunião
- listar databases acessíveis
- criar página operacional
- consultar itens recentes
- estruturar bases de tarefa, CRM e conteúdo

## Casos de uso imediatos

### Reuniões
- localizar última reunião
- resumir decisões
- identificar próximos passos

### Operação
- kanban executivo
- pipeline de pautas
- CRM simples
- acompanhamento de entregas

## Saída recomendada
Sempre responder com:
- workspace usado
- página/database consultada
- resultado encontrado
- se houve bloqueio de permissão, dizer explicitamente

## Regras
- Não misturar workspaces sem dizer qual foi usado
- Não tratar ausência de resultado como erro antes de checar compartilhamento
- Priorizar leitura e estrutura operacional antes de sair criando páginas demais

## Fit operacional

Notion entra como camada de organização viva da operação, desde que cada integração esteja conectada ao workspace correto e às páginas certas.
