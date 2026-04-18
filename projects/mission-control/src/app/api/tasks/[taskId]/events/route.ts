import { NextRequest, NextResponse } from 'next/server';
import { getTaskExecution, listTaskEvents } from '@/lib/task-tracking';

export async function GET(_request: NextRequest, context: { params: Promise<{ taskId: string }> }) {
  try {
    const { taskId } = await context.params;
    const task = getTaskExecution(taskId);
    if (!task) {
      return NextResponse.json({ error: 'Task not found' }, { status: 404 });
    }
    return NextResponse.json({ events: listTaskEvents(taskId) });
  } catch (error) {
    console.error('Failed to get task events:', error);
    return NextResponse.json({ error: 'Failed to get task events' }, { status: 500 });
  }
}
