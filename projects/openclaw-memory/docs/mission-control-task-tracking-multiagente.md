# Mission Control — Task Tracking Multiagente

_Atualizado em 2026-04-18_

## Objetivo

Traduzir o Protocolo Multiagente Flávia v1 em uma implementação técnica incremental dentro do Mission Control, criando rastreabilidade real de delegações, handoffs, retries, bloqueios, validações e SLA por tarefa.

## Problema atual

Hoje existe visibilidade parcial da operação, mas ainda faltam elementos centrais para governança multiagente real:
- não há trilha formal única por `task_id`
- spawn, retry e validação ainda não estão modelados como entidades operacionais de primeira classe
- gargalos e tarefas órfãs não aparecem com clareza
- Mission Control ainda mostra mais estado agregado do que fluxo auditável

Resultado: a coordenação existe, mas a observabilidade do multiagente ainda é incompleta.

## Objetivo funcional

Permitir responder, dentro do Mission Control, às perguntas:
- quem recebeu a demanda?
- quem delegou?
- para qual agente?
- com qual objetivo?
- quando começou?
- quanto tempo ficou parado?
- houve retry?
- houve bloqueio?
- a resposta voltou?
- foi validada?
- ficou pendente de humano?
- qual foi o resultado final?

## Escopo da v1

### Inclui
- modelo de dados para tarefas multiagente
- trilha de handoff entre agentes
- estados formais da tarefa
- registro de retry
- registro de bloqueio
- registro de validação
- visão operacional por agente
- base para SLA e alertas

### Não inclui ainda
- automação completa de recuperação
- auto-healing
- billing exato por tarefa
- grafo avançado em tempo real
- replay completo de transcript

## Arquitetura proposta

## 1. Entidade central: TaskExecution

Cada trabalho relevante vira uma entidade rastreável.

Campos mínimos:

```ts
export type TaskExecutionStatus =
  | 'queued'
  | 'running'
  | 'waiting_input'
  | 'blocked'
  | 'failed'
  | 'completed_unvalidated'
  | 'completed_validated'
  | 'cancelled'

export type TaskExecutionType =
  | 'direct'
  | 'delegation'
  | 'pipeline'
  | 'collaboration'
  | 'watchdog'

export interface TaskExecution {
  taskId: string
  parentTaskId?: string | null
  rootTaskId: string
  sessionKey?: string | null
  sourceAgent: string
  targetAgent: string
  executionType: TaskExecutionType
  title: string
  objective: string
  inputSummary?: string | null
  expectedOutput?: string | null
  successCriteria?: string | null
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  status: TaskExecutionStatus
  attempt: number
  maxAttempts: number
  createdAt: string
  startedAt?: string | null
  updatedAt: string
  finishedAt?: string | null
  slaMinutes?: number | null
  validationRequired: boolean
  validatedAt?: string | null
  validatedBy?: string | null
  blockingReason?: string | null
  failureReason?: string | null
  handoffDepth: number
  tags?: string[]
  metadata?: Record<string, unknown>
}
```

## 2. Entidade complementar: TaskEvent

Cada mudança relevante na tarefa gera evento.

```ts
export type TaskEventType =
  | 'created'
  | 'started'
  | 'delegated'
  | 'retry_scheduled'
  | 'retry_started'
  | 'waiting_input'
  | 'blocked'
  | 'failed'
  | 'completed_unvalidated'
  | 'validated'
  | 'cancelled'
  | 'note'

export interface TaskEvent {
  eventId: string
  taskId: string
  timestamp: string
  agentId: string
  type: TaskEventType
  message: string
  payload?: Record<string, unknown>
}
```

## 3. Relação Task ↔ Agent ↔ Session

Precisamos conectar:
- `taskId`
- `agentId`
- `sessionKey`
- eventual `childSessionKey`
- eventual `messageId`/run correlato quando disponível

Isso permite distinguir:
- tarefa delegada mas nunca iniciada
- tarefa iniciada e travada
- tarefa concluída sem validação
- tarefa concluída e validada

## Persistência recomendada

## Opção recomendada para v1
Usar store local simples e robusta dentro do Mission Control.

### Arquivos sugeridos
- `runtime/tasks/task-executions.jsonl`
- `runtime/tasks/task-events.jsonl`

Vantagens:
- rápida implementação
- append-only para auditoria
- fácil ingestão posterior para SQLite/Postgres
- baixo risco de travar rollout

## Evolução futura
Depois migrar para SQLite ou banco operacional leve com índices para consultas mais densas.

## Fluxo operacional esperado

## 1. Criação
Quando a Flávia decidir agir:
- cria `taskId`
- grava `TaskExecution` com `status=queued`
- grava evento `created`

## 2. Início
Quando a execução começar:
- status `running`
- evento `started`

## 3. Delegação
Se houver subagent:
- cria nova `TaskExecution` filha
- `parentTaskId` aponta para a mãe
- `rootTaskId` preserva rastreabilidade do fluxo inteiro
- evento `delegated` tanto na mãe quanto na filha

## 4. Retry
Se falhar e couber retry:
- evento `retry_scheduled`
- nova tentativa incrementa `attempt`
- ou cria nova execução filha da mesma raiz, conforme estratégia escolhida

## 5. Bloqueio
Se depender de input, auth, ferramenta ou aprovação:
- status `blocked` ou `waiting_input`
- `blockingReason` preenchido
- evento correspondente

## 6. Retorno do especialista
Ao receber resultado:
- `completed_unvalidated`
- registrar resumo do retorno
- se validação passar, mudar para `completed_validated`

## Regra de modelagem importante

### Conclusão não validada e validada são estados diferentes
Isso é obrigatório para impedir falso positivo operacional.

## Consultas que o Mission Control deve suportar

### Painel executivo
- tarefas abertas por agente
- tarefas bloqueadas
- tarefas com SLA vencido
- tarefas em retry
- tarefas concluídas validadas nas últimas 24h

### Painel operacional
- fila por agente
- handoffs recentes
- tempo médio por etapa
- filhos órfãos ou sem atualização
- tarefas com muitas tentativas

### Drill-down por tarefa
- dados da tarefa
- timeline de eventos
- cadeia pai/filho
- responsável atual
- motivo de bloqueio
- evidência de validação

## Componentes sugeridos no Mission Control

## Backend
Criar biblioteca:
- `src/lib/task-tracking.ts`

Funções sugeridas:
- `createTaskExecution()`
- `startTaskExecution()`
- `delegateTaskExecution()`
- `blockTaskExecution()`
- `failTaskExecution()`
- `completeTaskExecution()`
- `validateTaskExecution()`
- `appendTaskEvent()`
- `listTaskExecutions()`
- `listTaskEvents(taskId)`
- `getTaskTree(taskId)`
- `getTaskMetrics()`

Criar rotas API:
- `src/app/api/tasks/route.ts`
- `src/app/api/tasks/[taskId]/route.ts`
- `src/app/api/tasks/[taskId]/events/route.ts`
- `src/app/api/tasks/metrics/route.ts`

## Frontend
Criar páginas ou blocos:
- `/tasks`
- `/tasks/[taskId]`
- widget em `/office`
- widget no dashboard principal

Componentes sugeridos:
- `TaskStatusBoard.tsx`
- `TaskTimeline.tsx`
- `TaskTree.tsx`
- `TaskSlaCard.tsx`
- `BlockedTasksList.tsx`
- `AgentTaskLoadCard.tsx`

## Métricas iniciais

### Por agente
- abertas
- bloqueadas
- validadas 24h
- falhas 24h
- tempo médio até início
- tempo médio até conclusão validada

### Por fluxo
- taxa de delegação
- taxa de retry
- taxa de bloqueio
- taxa de validação
- SLA estourado

## Regras de UI

1. `blocked` e `waiting_input` precisam aparecer com destaque claro.
2. `completed_unvalidated` nunca pode parecer verde de concluído final.
3. tarefa mãe e tarefa filha precisam ser visualmente conectadas.
4. gargalo de SLA deve ficar visível no dashboard principal.
5. foco deve ser fluxo e exceção, não volume bonito.

## Rollout recomendado

## Fase 1 — Foundation
Implementar:
- modelo `TaskExecution`
- modelo `TaskEvent`
- store JSONL
- API básica
- página simples `/tasks`

Objetivo:
- registrar tarefas novas manualmente via código da Flávia / integrações do Mission Control

## Fase 2 — Handoff real
Implementar:
- relação pai/filho
- timeline por tarefa
- métricas básicas
- lista de bloqueios e SLA vencido

Objetivo:
- tornar visível onde a delegação quebra

## Fase 3 — Integração com spawn/subagents
Implementar:
- correlação com `sessionKey`
- gravação automática de eventos de delegação
- atualização automática de status por retorno do filho

Objetivo:
- sair de log manual e entrar em trilha operacional viva

## Fase 4 — Governança
Implementar:
- alertas de tarefa órfã
- alerta de SLA vencido
- ranking de falhas por agente
- heatmap de retries e bloqueios

## Critério de pronto por fase

### Fase 1 pronta quando
- tarefas podem ser criadas, listadas e consultadas
- timeline básica funciona
- store resiste a reinício

### Fase 2 pronta quando
- pai/filho está visível
- bloqueios aparecem claramente
- dashboard mostra SLA e gargalos

### Fase 3 pronta quando
- uma delegação real gera rastreio automático do início ao fim
- é possível provar quem delegou, quando e com qual resultado

### Fase 4 pronta quando
- Mission Control alerta exceções sem exigir investigação manual inicial

## Riscos e cuidados

1. Não começar grande demais.
   - JSONL primeiro, banco depois.

2. Não modelar transcript completo logo de início.
   - primeiro eventos estruturados, depois profundidade.

3. Não misturar atividade cosmética com tarefa real.
   - task tracking precisa refletir trabalho relevante.

4. Não chamar qualquer spawn de sucesso.
   - só vale o ciclo completo de execução e validação.

## Recomendação final

O melhor próximo passo é implementar a **Fase 1** no Mission Control com o menor caminho robusto:
- store JSONL
- lib de task tracking
- API `/tasks`
- página simples de lista + detalhe

Isso já cria a espinha dorsal correta sem inflar complexidade cedo demais.
