import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { appendTaskEvent, executeRetryQueue, getTaskAttention, getTaskMetrics, listTaskExecutions, reconcileTaskEvidence, reconcileTasksWithSessions } from '@/lib/task-tracking';

const execAsync = promisify(exec);

export async function POST() {
  try {
    let sessionKeys: string[] = [];
    try {
      const { stdout } = await execAsync('openclaw sessions list --json 2>/dev/null', { timeout: 10000 });
      const parsed = JSON.parse(stdout || '[]');
      const sessions = Array.isArray(parsed) ? parsed : (parsed.sessions || []);
      sessionKeys = sessions
        .map((session: any) => session.sessionKey || session.key)
        .filter(Boolean);
    } catch (error) {
      console.warn('Task reconciliation session fetch skipped:', error);
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
