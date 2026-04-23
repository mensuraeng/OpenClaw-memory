# Plano de Execução — Arquitetura dos Agentes

_Atualizado em 2026-04-13_

## Objetivo

Consolidar a arquitetura dos agentes com menos ruído, menos sobreposição e fronteiras mais claras.

## Diagnóstico atual

### Agentes presentes na configuração
- main
- rh
- marketing
- producao
- finance
- mia
- mensura
- autopilot
- juridico
- bi
- suprimentos
- pcs

### Situação encontrada
- havia sobreposição entre `finance` e `financeiro`
- `autopilot` tem nome genérico e fronteira fraca
- `pcs` já existe formalmente na configuração
- parte dos agentes configurados não tem diretório `agent/` explícito, o que sugere configuração ainda incompleta ou heterogênea

## Decisão arquitetural

### Estrutura-alvo
Manter como estrutura principal:
- main
- mensura
- mia
- pcs
- finance
- juridico
- marketing
- producao
- bi
- suprimentos
- rh

### Estrutura a revisar
- `autopilot` → absorver em `mensura` ou renomear só se houver função autônoma recorrente

## Execução em fases

### Fase 1 — Consolidação documental e de escopo
**Status:** concluída

Executado:
- arquitetura recomendada documentada em `docs/arquitetura-agentes.md`
- plano executivo registrado neste arquivo
- `pcs` reconhecido como agente separado da arquitetura-alvo

### Fase 2 — Preparação do agente PCS
**Status:** pronto para configurar

Executar:
1. criar entrada `pcs` em `agents.list`
2. apontar workspace para `/root/.openclaw/workspace-pcs` ou outro caminho definitivo
3. definir nome de exibição
4. criar diretório de agente se necessário
5. alinhar memória e escopo operacional da PCS

### Fase 3 — Higienização de redundância
**Status:** pendente

#### 3.1 finance
Resultado da inspeção:
- há uso real do agente `finance`
- há workspace próprio em `/root/.openclaw/workspace/finance`
- há skills próprias
- há sessões reais registradas
- há bindings ativos para `miafinance` em Telegram e WhatsApp

Decisão aplicada:
- `finance` foi consolidado como agente principal de finanças
- `financeiro` foi removido da configuração ativa
- o escopo financeiro oficial fica concentrado em `finance`

#### 3.2 autopilot
Executar:
- confirmar se o agente tem rotina autônoma real
- se não tiver, remover da configuração
- absorver responsabilidade em `mensura`
- se tiver função própria, renomear com fronteira explícita

## Ações seguras já executadas
- arquitetura dos agentes documentada
- plano de execução documentado
- `pcs` incluído como parte da estrutura-alvo
- `finance` consolidado como agente principal de finanças
- `financeiro` removido da configuração ativa
- `autopilot` mantido como item de revisão estrutural

## Próximo passo recomendado

### Agora
1. `pcs` já foi criado formalmente
2. revisar `autopilot`
3. depois revisar naming e fronteiras finais dos agentes

## Critério de encerramento

A arquitetura estará limpa quando:
- `pcs` existir formalmente
- `finance` estiver consolidado como frente principal de finanças
- `autopilot` estiver absorvido ou renomeado com função clara
- cada agente tiver função própria, fronteira clara e baixo overlap
