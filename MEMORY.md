# MEMORY.md — Painel de Continuidade da Flávia

_Última atualização: 2026-04-13_

## O que este arquivo é

Este arquivo é o painel executivo de continuidade da operação.
Não é arquivo de detalhe, não é diário, não é depósito.
Serve para responder rápido:
- o que está ativo
- o que está travado
- o que está faltando
- onde fica cada contexto relevante

## Estado Atual

### Frentes ativas
- **Setup OpenClaw + Flávia** — em andamento
- **Automações Microsoft Graph** — ativas para Mensura, MIA e Flávia
- **Grupo Telegram MENSURA** — ativo como canal operacional do agente da MENSURA
- **Monitor semanal** — ativo, segunda 8h BRT
- **Relatório de cursos** — ativo, sexta 16h BRT
- **Monitoramento de cronogramas** — ativo para P&G Louveira e CCSP Casa 3
- **PCS Engenharia** — posicionamento, narrativa institucional e estrutura comercial em evolução

### Pendências críticas
- LinkedIn Client ID + Secret
- Instagram App ID + Secret
- OpenAI API key válida para Whisper + embeddings
- Confirmar SSH key antes de hardening
- Revisar falha de calendário da conta Mensura quando houver janela para isso

### Integrações ativas
- Email Mensura ✅
- Email MIA ✅
- Email Flávia ✅
- Calendário ✅
- SharePoint ✅
- Telegram ✅
- VPS ✅

### Riscos ou atenção
- `memory_search()` está indisponível por erro de API key de embeddings
- Parte do contexto de longo prazo existe, mas ainda precisa de consolidação contínua por tema
- Há risco de espalhamento de contexto em notas diárias se não houver promoção periódica para arquivos temáticos

## Onde está cada coisa

### Contexto estrutural
- `memory/context/business-context.md` → contexto consolidado das empresas
- `memory/context/decisions.md` → decisões permanentes
- `memory/context/lessons.md` → lições aprendidas e erros recorrentes
- `memory/context/pending.md` → pendências aguardando ação ou input
- `memory/context/people.md` → pessoas e relações importantes
- `memory/context/pcs-engenharia.md` → memória dedicada da PCS

### Projetos
- `memory/projects/setup-openclaw-flavia.md` → setup da operação Flávia
- `memory/projects/automacoes-msgraph.md` → email, calendário e SharePoint
- `memory/projects/grupo-telegram-mensura.md` → protocolo operacional do grupo da MENSURA no Telegram
- `memory/projects/monitor-semanal.md` → rotina semanal de monitoramento
- `memory/projects/relatorio-cursos.md` → relatório semanal de cursos
- `memory/projects/pcs-comercial-posicionamento.md` → posicionamento comercial da PCS

### Conteúdo e apoio
- `memory/content/ideas.md` → ideias de conteúdo
- `memory/content/drafts/` → rascunhos em andamento
- `memory/integrations/telegram-map.md` → mapa de chats, grupos e tópicos
- `memory/integrations/credentials-map.md` → mapa de credenciais
- `memory/sessions/` → histórico bruto de sessões
- `memory/YYYY-MM-DD.md` → rascunho diário

## Regras de uso

- Antes de abrir arquivos grandes, buscar o tema e ler só o necessário
- Se algo importa além da sessão atual, registrar no arquivo temático certo
- Não duplicar conteúdo detalhado aqui
- Atualizar este painel quando mudar estado, prioridade, risco ou localização de contexto
- Se um projeto deixar de ser relevante, tirar do estado atual e manter só no arquivo temático

## Próxima melhoria recomendada

- Consolidar pendências e decisões espalhadas das notas diárias para os arquivos de contexto
- Resolver a chave de OpenAI para reativar embeddings, `memory_search()` e fluxos de Whisper
