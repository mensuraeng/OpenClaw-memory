# MEMORY.md — Painel de Continuidade da Flávia

_Última atualização: 2026-04-19_

## O que este arquivo é

Este arquivo é o painel executivo de continuidade da operação.
Não é arquivo de detalhe, não é diário, não é depósito.
Serve para responder rápido:
- o que está ativo
- o que está travado
- o que está faltando
- onde fica cada contexto relevante

## Estado Atual
_Atualizado automaticamente em 2026-04-19 pelo update_memory_panel.py_

### Pendencias Abertas (10 itens)
- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.
- [ ] **Revalidar fallback real além do microteste de agentes** — o runtime principal dos agentes especializados voltou a responder, mas a cadeia alternativa de modelos ainda precisa de prova operacional específica fora do healthcheck curto.
- [ ] **Corrigir roteamento do domínio de relatórios MIA** — `relatorios.miaengenharia.com.br/ccsp-casa-7/*` ainda cai no fallback da SPA principal em vez de servir páginas estáticas extras como o checklist.
- [ ] **Instagram integration** — confirmar arquitetura final 10/10: conta Instagram Business exata, Facebook Page vinculada, domínio/subdomínio público das páginas legais e objetivo/escopos reais do app antes de live/review.
- [ ] **Novos contatos/equipe** — preencher `memory/context/people.md` conforme equipe e parceiros relevantes surgirem.
- [ ] **Migrar lote 1 para cofre** — revisar saneamento posterior dos arquivos que ainda precisam manter compatibilidade operacional.
- [ ] **Trocar senha mestra do KeePassXC** — substituir a senha atual por uma forte.
- [ ] **Estruturar grupos do cofre** — consolidar grupos padrão: Email, APIs, Social, Infra, Financeiro.
- [ ] **Revisar falha histórica do calendário Mensura** — houve erro `ErrorInvalidUser` em ciclo anterior; confirmar se foi definitivamente sanado ou se ainda reaparece em alguma rota/conta.

### Ultimas Decisoes Ativas
- PCS adota identidade visual oficial enviada pelo Alê (2026-04-13)
- Grupo `MENSURA Engenharia` vira canal do agente da MENSURA (2026-04-13)
- Grupo `PCS Engenharia` vira canal do agente da PCS (2026-04-13)
- Tópico `AGENTE FINANCEIRO` é roteado para o agente `finance` (2026-04-13)
- GitHub será o segundo cérebro operacional (2026-04-14)

### Destaques de Hoje (2026-04-19)
_Sem destaques registrados hoje_
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
- `memory/projects/grupo-telegram-pcs.md` → protocolo operacional do grupo da PCS no Telegram
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
