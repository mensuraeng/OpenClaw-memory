import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';

const TASKS_DIR = path.join(process.cwd(), 'runtime', 'tasks');
const EXECUTIONS_PATH = path.join(TASKS_DIR, 'task-executions.jsonl');
const EVENTS_PATH = path.join(TASKS_DIR, 'task-events.jsonl');

export type TaskExecutionStatus =
  | 'queued'
  | 'running'
  | 'waiting_input'
  | 'blocked'
  | 'failed'
  | 'completed_unvalidated'
  | 'completed_validated'
  | 'cancelled';

export type TaskExecutionType =
  | 'direct'
  | 'delegation'
  | 'pipeline'
  | 'collaboration'
  | 'watchdog';

export interface TaskExecution {
  taskId: string;
  parentTaskId?: string | null;
  rootTaskId: string;
  sessionKey?: string | null;
  childSessionKey?: string | null;
  sourceAgent: string;
  targetAgent: string;
  executionType: TaskExecutionType;
  title: string;
  objective: string;
  inputSummary?: string | null;
  expectedOutput?: string | null;
  successCriteria?: string | null;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  status: TaskExecutionStatus;
  attempt: number;
  maxAttempts: number;
  createdAt: string;
  startedAt?: string | null;
  updatedAt: string;
  finishedAt?: string | null;
  slaMinutes?: number | null;
  dueAt?: string | null;
  staleAfterMinutes?: number | null;
  validationRequired: boolean;
  validatedAt?: string | null;
  validatedBy?: string | null;
  blockingReason?: string | null;
  failureReason?: string | null;
  handoffDepth: number;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

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
  | 'sla_breached'
  | 'stale_detected'
  | 'orphan_detected'
  | 'session_observed'
  | 'note';

export interface TaskEvent {
  eventId: string;
  taskId: string;
  timestamp: string;
  agentId: string;
  type: TaskEventType;
  message: string;
  payload?: Record<string, unknown>;
}

function ensureStore() {
  if (!fs.existsSync(TASKS_DIR)) {
    fs.mkdirSync(TASKS_DIR, { recursive: true });
  }
  if (!fs.existsSync(EXECUTIONS_PATH)) {
    fs.writeFileSync(EXECUTIONS_PATH, '', 'utf-8');
  }
  if (!fs.existsSync(EVENTS_PATH)) {
    fs.writeFileSync(EVENTS_PATH, '', 'utf-8');
  }
}

function readJsonl<T>(filePath: string): T[] {
  ensureStore();
  const raw = fs.readFileSync(filePath, 'utf-8').trim();
  if (!raw) return [];
  return raw
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line) as T);
}

function appendJsonl<T>(filePath: string, row: T) {
  ensureStore();
  fs.appendFileSync(filePath, `${JSON.stringify(row)}\n`, 'utf-8');
}

function overwriteExecutions(rows: TaskExecution[]) {
  ensureStore();
  const content = rows.map((row) => JSON.stringify(row)).join('\n');
  fs.writeFileSync(EXECUTIONS_PATH, content ? `${content}\n` : '', 'utf-8');
}

export function listTaskExecutions() {
  return readJsonl<TaskExecution>(EXECUTIONS_PATH).sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export function findTaskByMetadata(key: string, value: string) {
  return listTaskExecutions().find((task) => String(task.metadata?.[key] ?? '') === value) ?? null;
}

export function listTaskEvents(taskId?: string) {
  const rows = readJsonl<TaskEvent>(EVENTS_PATH).sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  return taskId ? rows.filter((row) => row.taskId === taskId) : rows;
}

export function getTaskExecution(taskId: string) {
  return listTaskExecutions().find((row) => row.taskId === taskId) ?? null;
}

export function createTaskExecution(input: {
  parentTaskId?: string | null;
  rootTaskId?: string;
  sessionKey?: string | null;
  childSessionKey?: string | null;
  sourceAgent: string;
  targetAgent: string;
  executionType: TaskExecutionType;
  title: string;
  objective: string;
  inputSummary?: string | null;
  expectedOutput?: string | null;
  successCriteria?: string | null;
  riskLevel?: TaskExecution['riskLevel'];
  slaMinutes?: number | null;
  staleAfterMinutes?: number | null;
  validationRequired?: boolean;
  handoffDepth?: number;
  tags?: string[];
  metadata?: Record<string, unknown>;
}) {
  const now = new Date().toISOString();
  const taskId = randomUUID();
  const dueAt = input.slaMinutes ? new Date(Date.now() + input.slaMinutes * 60_000).toISOString() : null;
  const task: TaskExecution = {
    taskId,
    parentTaskId: input.parentTaskId ?? null,
    rootTaskId: input.rootTaskId ?? taskId,
    sessionKey: input.sessionKey ?? null,
    childSessionKey: input.childSessionKey ?? null,
    sourceAgent: input.sourceAgent,
    targetAgent: input.targetAgent,
    executionType: input.executionType,
    title: input.title,
    objective: input.objective,
    inputSummary: input.inputSummary ?? null,
    expectedOutput: input.expectedOutput ?? null,
    successCriteria: input.successCriteria ?? null,
    riskLevel: input.riskLevel ?? 'medium',
    status: 'queued',
    attempt: 1,
    maxAttempts: 2,
    createdAt: now,
    updatedAt: now,
    slaMinutes: input.slaMinutes ?? null,
    dueAt,
    staleAfterMinutes: input.staleAfterMinutes ?? 30,
    validationRequired: input.validationRequired ?? true,
    handoffDepth: input.handoffDepth ?? 0,
    tags: input.tags ?? [],
    metadata: input.metadata ?? {},
  };
  appendJsonl(EXECUTIONS_PATH, task);
  appendTaskEvent({
    taskId,
    agentId: input.sourceAgent,
    type: 'created',
    message: `Tarefa criada: ${input.title}`,
    payload: { targetAgent: input.targetAgent, executionType: input.executionType },
  });
  return task;
}

export function appendTaskEvent(input: {
  taskId: string;
  agentId: string;
  type: TaskEventType;
  message: string;
  payload?: Record<string, unknown>;
}) {
  const event: TaskEvent = {
    eventId: randomUUID(),
    taskId: input.taskId,
    timestamp: new Date().toISOString(),
    agentId: input.agentId,
    type: input.type,
    message: input.message,
    payload: input.payload,
  };
  appendJsonl(EVENTS_PATH, event);
  return event;
}

export function updateTaskExecution(taskId: string, patch: Partial<TaskExecution>) {
  const rows = listTaskExecutions();
  const index = rows.findIndex((row) => row.taskId === taskId);
  if (index === -1) {
    throw new Error(`Task not found: ${taskId}`);
  }
  rows[index] = {
    ...rows[index],
    ...patch,
    updatedAt: new Date().toISOString(),
  };
  overwriteExecutions(rows);
  return rows[index];
}

export function startTaskExecution(taskId: string, agentId: string) {
  const now = new Date().toISOString();
  const task = updateTaskExecution(taskId, { status: 'running', startedAt: now });
  appendTaskEvent({ taskId, agentId, type: 'started', message: 'Execução iniciada' });
  return task;
}

export function attachSessionToTask(taskId: string, patch: { sessionKey?: string | null; childSessionKey?: string | null }, agentId = 'main') {
  const task = updateTaskExecution(taskId, {
    sessionKey: patch.sessionKey ?? undefined,
    childSessionKey: patch.childSessionKey ?? undefined,
  });
  appendTaskEvent({
    taskId,
    agentId,
    type: 'note',
    message: 'Sessão vinculada à task',
    payload: patch,
  });
  return task;
}

export function blockTaskExecution(taskId: string, agentId: string, reason: string, waitingInput = false) {
  const status: TaskExecutionStatus = waitingInput ? 'waiting_input' : 'blocked';
  const eventType: TaskEventType = waitingInput ? 'waiting_input' : 'blocked';
  const task = updateTaskExecution(taskId, { status, blockingReason: reason });
  appendTaskEvent({ taskId, agentId, type: eventType, message: reason });
  return task;
}

export function failTaskExecution(taskId: string, agentId: string, reason: string) {
  const task = updateTaskExecution(taskId, { status: 'failed', failureReason: reason, finishedAt: new Date().toISOString() });
  appendTaskEvent({ taskId, agentId, type: 'failed', message: reason });
  return task;
}

export function completeTaskExecution(taskId: string, agentId: string, message?: string) {
  const task = updateTaskExecution(taskId, {
    status: 'completed_unvalidated',
    finishedAt: new Date().toISOString(),
  });
  appendTaskEvent({ taskId, agentId, type: 'completed_unvalidated', message: message ?? 'Execução concluída, aguardando validação' });
  return task;
}

export function validateTaskExecution(taskId: string, agentId: string) {
  const now = new Date().toISOString();
  const task = updateTaskExecution(taskId, {
    status: 'completed_validated',
    validatedAt: now,
    validatedBy: agentId,
    finishedAt: now,
  });
  appendTaskEvent({ taskId, agentId, type: 'validated', message: 'Execução validada' });
  return task;
}

export function getTaskTree(taskId: string) {
  const tasks = listTaskExecutions();
  const root = tasks.find((task) => task.taskId === taskId || task.rootTaskId === taskId);
  if (!root) return [];
  return tasks.filter((task) => task.rootTaskId === root.rootTaskId).sort((a, b) => a.createdAt.localeCompare(b.createdAt));
}

export function isTaskOpen(task: TaskExecution) {
  return ['queued', 'running', 'waiting_input', 'blocked'].includes(task.status);
}

export function isTaskSlaBreached(task: TaskExecution, now = new Date()) {
  return Boolean(task.dueAt && isTaskOpen(task) && new Date(task.dueAt).getTime() < now.getTime());
}

export function isTaskStale(task: TaskExecution, now = new Date()) {
  if (!isTaskOpen(task)) return false;
  const staleAfter = task.staleAfterMinutes ?? 30;
  const updatedAt = new Date(task.updatedAt).getTime();
  return now.getTime() - updatedAt > staleAfter * 60_000;
}

export function delegateTaskExecution(input: {
  parentTaskId: string;
  sourceAgent: string;
  targetAgent: string;
  title: string;
  objective: string;
  childSessionKey?: string | null;
  inputSummary?: string | null;
  expectedOutput?: string | null;
  successCriteria?: string | null;
  riskLevel?: TaskExecution['riskLevel'];
  slaMinutes?: number | null;
  staleAfterMinutes?: number | null;
  metadata?: Record<string, unknown>;
}) {
  const parent = getTaskExecution(input.parentTaskId);
  if (!parent) {
    throw new Error(`Parent task not found: ${input.parentTaskId}`);
  }

  const child = createTaskExecution({
    parentTaskId: parent.taskId,
    rootTaskId: parent.rootTaskId,
    sessionKey: parent.sessionKey ?? null,
    childSessionKey: input.childSessionKey ?? null,
    sourceAgent: input.sourceAgent,
    targetAgent: input.targetAgent,
    executionType: 'delegation',
    title: input.title,
    objective: input.objective,
    inputSummary: input.inputSummary ?? null,
    expectedOutput: input.expectedOutput ?? null,
    successCriteria: input.successCriteria ?? null,
    riskLevel: input.riskLevel ?? parent.riskLevel,
    slaMinutes: input.slaMinutes ?? parent.slaMinutes ?? null,
    staleAfterMinutes: input.staleAfterMinutes ?? parent.staleAfterMinutes ?? 30,
    validationRequired: true,
    handoffDepth: (parent.handoffDepth ?? 0) + 1,
    metadata: input.metadata ?? {},
  });

  appendTaskEvent({
    taskId: parent.taskId,
    agentId: input.sourceAgent,
    type: 'delegated',
    message: `Delegado para ${input.targetAgent}: ${input.title}`,
    payload: { childTaskId: child.taskId },
  });

  appendTaskEvent({
    taskId: child.taskId,
    agentId: input.sourceAgent,
    type: 'delegated',
    message: `Recebida delegação de ${input.sourceAgent}`,
    payload: { parentTaskId: parent.taskId },
  });

  return child;
}

export function reconcileTasksWithSessions(sessionKeys: string[]) {
  const tasks = listTaskExecutions();
  const sessionSet = new Set(sessionKeys);
  const now = new Date();
  const updates: TaskExecution[] = [];

  for (const task of tasks) {
    if (!isTaskOpen(task)) continue;

    const observedSession = task.childSessionKey || task.sessionKey;
    if (!observedSession) continue;

    if (sessionSet.has(observedSession)) {
      appendTaskEvent({
        taskId: task.taskId,
        agentId: task.targetAgent,
        type: 'session_observed',
        message: 'Sessão observada como ativa na reconciliação',
        payload: { sessionKey: observedSession },
      });
      updates.push(updateTaskExecution(task.taskId, { metadata: { ...(task.metadata || {}), lastObservedSessionAt: now.toISOString() } }));
      continue;
    }

    const ageMinutes = (now.getTime() - new Date(task.updatedAt).getTime()) / 60000;
    if (ageMinutes >= Math.max(task.staleAfterMinutes ?? 30, 15)) {
      const nextStatus = task.status === 'queued' ? 'blocked' : task.status;
      updates.push(updateTaskExecution(task.taskId, {
        status: nextStatus,
        blockingReason: `Sessão não encontrada na reconciliação (${observedSession})`,
        metadata: { ...(task.metadata || {}), orphaned: true, orphanedAt: now.toISOString() },
      }));
      appendTaskEvent({
        taskId: task.taskId,
        agentId: task.targetAgent,
        type: 'orphan_detected',
        message: `Task órfã detectada: sessão ${observedSession} não encontrada`,
        payload: { sessionKey: observedSession },
      });
    }
  }

  return updates;
}

export function getTaskAttention() {
  const tasks = listTaskExecutions();
  const now = new Date();

  return {
    slaBreached: tasks.filter((task) => isTaskSlaBreached(task, now)).slice(0, 10),
    stale: tasks.filter((task) => isTaskStale(task, now)).slice(0, 10),
    blocked: tasks.filter((task) => task.status === 'blocked' || task.status === 'waiting_input').slice(0, 10),
    unvalidated: tasks.filter((task) => task.status === 'completed_unvalidated').slice(0, 10),
    orphaned: tasks.filter((task) => Boolean(task.metadata?.orphaned)).slice(0, 10),
  };
}

export function getTaskMetrics() {
  const tasks = listTaskExecutions();
  const now = new Date();
  const byAgent: Record<string, { open: number; blocked: number; validated: number; failed: number; slaBreached: number; stale: number }> = {};

  for (const task of tasks) {
    if (!byAgent[task.targetAgent]) {
      byAgent[task.targetAgent] = { open: 0, blocked: 0, validated: 0, failed: 0, slaBreached: 0, stale: 0, orphaned: 0 } as any;
    }
    if (isTaskOpen(task)) byAgent[task.targetAgent].open += 1;
    if (task.status === 'blocked' || task.status === 'waiting_input') byAgent[task.targetAgent].blocked += 1;
    if (task.status === 'completed_validated') byAgent[task.targetAgent].validated += 1;
    if (task.status === 'failed') byAgent[task.targetAgent].failed += 1;
    if (isTaskSlaBreached(task, now)) byAgent[task.targetAgent].slaBreached += 1;
    if (isTaskStale(task, now)) byAgent[task.targetAgent].stale += 1;
    if (task.metadata?.orphaned) (byAgent[task.targetAgent] as any).orphaned += 1;
  }

  return {
    total: tasks.length,
    open: tasks.filter((task) => isTaskOpen(task)).length,
    blocked: tasks.filter((task) => task.status === 'blocked' || task.status === 'waiting_input').length,
    validated: tasks.filter((task) => task.status === 'completed_validated').length,
    failed: tasks.filter((task) => task.status === 'failed').length,
    slaBreached: tasks.filter((task) => isTaskSlaBreached(task, now)).length,
    stale: tasks.filter((task) => isTaskStale(task, now)).length,
    orphaned: tasks.filter((task) => Boolean(task.metadata?.orphaned)).length,
    byAgent,
  };
}
