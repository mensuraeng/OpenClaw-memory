import { NextRequest, NextResponse } from 'next/server';
import { createTaskExecution, getTaskMetrics, listTaskExecutions } from '@/lib/task-tracking';

function compareTasks(a: { status: string; riskLevel?: string; updatedAt: string }, b: { status: string; riskLevel?: string; updatedAt: string }) {
  const statusWeight = (task: { status: string; riskLevel?: string }) => {
    if (task.riskLevel === 'critical') return 500;
    if (task.status === 'blocked' || task.status === 'waiting_input') return 400;
    if (task.riskLevel === 'high') return 300;
    if (task.status === 'running') return 200;
    if (task.status === 'queued') return 100;
    return 0;
  };

  return statusWeight(b) - statusWeight(a) || b.updatedAt.localeCompare(a.updatedAt);
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const agent = searchParams.get('agent');

    let tasks = listTaskExecutions();
    if (status && status !== 'all') {
      tasks = tasks.filter((task) => task.status === status);
    }
    if (agent && agent !== 'all') {
      tasks = tasks.filter((task) => task.targetAgent === agent || task.sourceAgent === agent);
    }

    return NextResponse.json({
      tasks: tasks.sort(compareTasks),
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
