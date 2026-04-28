import { NextResponse } from 'next/server';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { appendTaskEvent, executeRetryQueue, getTaskAttention, getTaskMetrics, listTaskExecutions, reconcileTaskEvidence, reconcileTasksWithSessions } from '@/lib/task-tracking';

const OPENCLAW_DIR = process.env.OPENCLAW_DIR || '/root/.openclaw';

function getErrorSummary(error: unknown) {
  if (error && typeof error === 'object') {
    const maybeError = error as { code?: unknown; signal?: unknown; message?: unknown };
    return {
      code: maybeError.code,
      signal: maybeError.signal,
      message: typeof maybeError.message === 'string' ? maybeError.message.split('\n')[0] : undefined,
    };
  }
  return { message: String(error) };
}

function readSessionKeys(agentId = 'main') {
  const storePath = join(OPENCLAW_DIR, 'agents', agentId, 'sessions', 'sessions.json');
  if (!existsSync(storePath)) return [];

  const parsed = JSON.parse(readFileSync(storePath, 'utf-8'));
  if (Array.isArray(parsed)) {
    return parsed
      .map((session: { sessionKey?: string; key?: string }) => session.sessionKey || session.key)
      .filter((key): key is string => Boolean(key));
  }

  if (parsed && typeof parsed === 'object') {
    return Object.keys(parsed);
  }

  return [];
}

export async function POST() {
  try {
    let sessionKeys: string[] = [];
    try {
      sessionKeys = readSessionKeys();
    } catch (error) {
      console.warn('Task reconciliation session fetch skipped:', getErrorSummary(error));
    }

    const sessionUpdates = reconcileTasksWithSessions(sessionKeys);
    const evidenceUpdates = await reconcileTaskEvidence();
    const retryUpdates = await executeRetryQueue();
    const metrics = getTaskMetrics();
    const attention = getTaskAttention();
    const criticalTasks = listTaskExecutions().filter((task) => task.riskLevel === 'critical' && (task.status === 'blocked' || task.status === 'failed'));

    for (const task of criticalTasks) {
      appendTaskEvent({
        taskId: task.taskId,
        agentId: 'system',
        type: 'escalated',
        message: 'Task crítica exige atenção executiva imediata',
        payload: { riskLevel: task.riskLevel, status: task.status },
      });
    }

    const summary = {
      totalTasks: metrics.total,
      openTasks: metrics.open,
      criticalEscalations: metrics.criticalEscalations,
      retrying: metrics.retrying,
      evidenceValidated: evidenceUpdates.filter((item) => item.status === 'validated').length,
      retriesRestarted: retryUpdates.filter((item) => item.status === 'restarted').length,
      topAttention: {
        critical: attention.criticalEscalations.length,
        blocked: attention.blocked.length,
        orphaned: attention.orphaned.length,
      },
    };

    return NextResponse.json({
      ok: true,
      summary,
      sessionUpdates,
      evidenceUpdates,
      retryUpdates,
      metrics,
      attention,
    });
  } catch (error) {
    console.error('Failed to reconcile tasks:', error);
    return NextResponse.json({ error: 'Failed to reconcile tasks' }, { status: 500 });
  }
}
