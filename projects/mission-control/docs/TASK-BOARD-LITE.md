# Task Board Lite — Flávia / Mission Control

_Atualizado em 2026-04-26_

## Objetivo

Transformar pendências reais do `2nd-brain` em tarefas rastreáveis no Mission Control, sem criar um sistema pesado de multiagentes antes da operação básica estabilizar.

Fonte primária continua sendo:

- `/root/2nd-brain/02-context/pending.md`

O Mission Control passa a ser a camada de execução/observabilidade:

- tarefa
- responsável/agente sugerido
- status
- risco
- bloqueio
- validação
- histórico de eventos

## Regra de ouro

Não é para criar barulho. É para evitar tarefa órfã.

Se a pendência não exige ação, decisão, bloqueio ou rastreio, ela não merece virar tarefa.

## Fluxo v1

1. A Flávia mantém `pending.md` como visão executiva.
2. O script importa itens abertos para `runtime/tasks/task-executions.jsonl`.
3. Cada item recebe:
   - `taskId`
   - `targetAgent` estimado (`main`, `finance`, `mensura`, `mia`, `pcs`)
   - `riskLevel`
   - `status`
   - tags operacionais
   - link lógico com a seção original do `pending.md`
4. O dashboard `/tasks` mostra tarefas abertas, bloqueadas, paradas e validadas.
5. Conclusões importantes voltam para o `2nd-brain`.

## Comandos

```bash
cd /root/.openclaw/workspace/projects/mission-control
npm run tasks:import-pending
```

Dry-run antes de mexer no store:

```bash
node ./scripts/import-pending-to-tasks.mjs --dry-run
```

## Estados

- `queued`: ação interna ainda não iniciada
- `running`: execução em andamento
- `waiting_input`: depende do Alê ou terceiro
- `blocked`: bloqueio operacional real
- `completed_unvalidated`: concluída, mas ainda sem validação da Flávia
- `completed_validated`: concluída e validada
- `failed`: falhou
- `cancelled`: cancelada

## Política de agente

A classificação é intencionalmente simples:

- financeiro/documentos fiscais/pagamentos → `finance`
- Mensura/P&G/LinkedIn/comercial → `mensura`
- MIA/CCSP/Casa 7 → `mia`
- PCS/Sienge/SPTrans/SPObras/licitação/patrimônio → `pcs`
- resto → `main`

Isso não substitui julgamento da Flávia. Só dá um primeiro dono para não deixar item solto.

## O que NÃO fazer agora

- Não criar 10 agentes novos.
- Não ligar heartbeat de 15 minutos para tudo.
- Não mandar subagent trabalhar sem critério de sucesso.
- Não notificar o Alê sobre status vazio.
- Não tratar o painel como fonte de verdade acima do `2nd-brain`.

## Working memory automática

Tarefas abertas com risco `high` ou `critical` recebem arquivo de memória de trabalho em:

```text
runtime/tasks/working/<taskId>.md
```

Esse arquivo existe para reduzir perda de contexto em tarefas críticas. Ele deve conter:

- objetivo
- status atual
- responsável sugerido
- critério de sucesso
- próximo passo
- notas de decisão/bloqueio

Regra: se a tarefa é crítica/alta e não tem `working.md`, a base não está sólida.

## Próxima evolução recomendada

Quando o básico estiver estável:

1. registrar handoff real quando `sessions_spawn` for usado;
2. gerar standup diário só com bloqueios, decisões e entregas materiais;
3. adicionar reconciliação automática entre tarefas concluídas e `pending.md`.
