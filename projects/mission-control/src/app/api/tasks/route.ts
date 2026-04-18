import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { createTaskExecution, executeRetryQueue, getTaskMetrics, listTaskExecutions, reconcileTaskEvidence, reconcileTasksWithSessions } from '@/lib/task-tracking';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const agent = searchParams.get('agent');

    try {
      const { stdout } = await execAsync('openclaw sessions list --json 2>/dev/null', { timeout: 10000 });
      const parsed = JSON.parse(stdout || '[]');
      const sessions = Array.isArray(parsed) ? parsed : (parsed.sessions || []);
      const sessionKeys = sessions
        .map((session: any) => session.sessionKey || session.key)
        .filter(Boolean);
      reconcileTasksWithSessions(sessionKeys);
      await reconcileTaskEvidence();
    } catch (error) {
      console.warn('Task reconciliation skipped:', error);
    }

    let tasks = listTaskExecutions();
    if (status && status !== 'all') {
      tasks = tasks.filter((task) => task.status === status);
    }
    if (agent && agent !== 'all') {
      tasks = tasks.filter((task) => task.targetAgent === agent || task.sourceAgent === agent);
    }

    return NextResponse.json({
      tasks,
      metrics: getTaskMetrics(),
    });
  } catch (error) {
    console.error('Failed to list tasks:', error);
    return NextResponse.json({ error: 'Failed to list tasks' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const task = createTaskExecution({
      sourceAgent: body.sourceAgent || 'main',
      targetAgent: body.targetAgent || 'main',
      executionType: body.executionType || 'direct',
      title: body.title || 'Nova tarefa',
      objective: body.objective || body.title || 'Sem objetivo informado',
      inputSummary: body.inputSummary || null,
      expectedOutput: body.expectedOutput || null,
      successCriteria: body.successCriteria || null,
      riskLevel: body.riskLevel || 'medium',
      slaMinutes: body.slaMinutes || null,
      validationRequired: body.validationRequired ?? true,
      parentTaskId: body.parentTaskId || null,
      rootTaskId: body.rootTaskId || undefined,
      handoffDepth: body.handoffDepth || 0,
      tags: Array.isArray(body.tags) ? body.tags : [],
      metadata: { ...(body.metadata || {}), jobMessage: body.message || body.objective || body.title || '' },
    });

    return NextResponse.json({ task }, { status: 201 });
  } catch (error) {
    console.error('Failed to create task:', error);
    return NextResponse.json({ error: 'Failed to create task' }, { status: 500 });
  }
}
