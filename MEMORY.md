# MEMORY.md — Painel de Continuidade da Flávia

_Última atualização: 2026-04-22_

## O que este arquivo é

Este arquivo é o painel executivo de continuidade da operação.
Não é arquivo de detalhe, não é diário, não é depósito.
Serve para responder rápido:
- o que está ativo
- o que está travado
- o que está faltando
- onde fica cada contexto relevante

## Estado Atual
_Atualizado manualmente em 2026-04-22 durante saneamento da Memória v2_

### Pendências Abertas (8 frentes executivas)
- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.
- [ ] **Revalidar fallback real além do microteste de agentes** — ainda falta prova operacional específica da cadeia alternativa de modelos.
- [ ] **Instagram integration** — confirmar arquitetura final 10/10 antes de live/review.
- [ ] **Reforçar governança da memória operacional** — sincronizar painel, promover conteúdos permanentes e reduzir duplicação entre diário, contexto e projetos.
- [ ] **Classificar base PCS↔Sienge** — separar obras executáveis, centros de custo administrativos e itens ambíguos.
- [ ] **Descobrir rota financeira real do Teatro Suzano no Sienge** — obter gastos/títulos/payables da obra `1354` com endpoint válido.
- [ ] **Aguardar romaneio da MIA para conciliação** — cruzar comprovantes com notas e consolidar `pago`, `pendente`, `parcial` e `ambíguo`.

### Últimas decisões ativas
- GitHub será o segundo cérebro operacional (2026-04-14)
- Memória documental deve ser separada por empresa e pela frente pessoal do Alê (2026-04-20)
- A base PCS↔Sienge deve ter memória operacional como fonte principal, com arquivo documental reduzido a ponte (2026-04-22)
- Comprovante bancário isolado da MIA deve ficar como histórico bruto, sem atribuição prematura a obra específica (2026-04-22)
- Claude-Mem entra só como referência de arquitetura; a memória da Flávia evolui por cirurgia de consolidação, não por substituição da base atual (2026-04-22)

### Destaques de Hoje (2026-04-22)
- Corrigido o roteamento do domínio de relatórios MIA Casa 7; rotas públicas passaram a servir conteúdo correto.
- Base PCS↔Sienge promovida para memória operacional em `memory/context/pcs-sienge-obras-centros-de-custo.md`.
- Histórico de comprovantes da MIA iniciado e preservado para conciliação futura.
- Blueprint inicial da **Memória v2 da Flávia** criado em `memory/context/memoria-v2-flavia.md`.
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
