import { NextRequest, NextResponse } from 'next/server';
import { getTaskExecution, getTaskTree } from '@/lib/task-tracking';

export async function GET(_request: NextRequest, context: { params: Promise<{ taskId: string }> }) {
  try {
    const { taskId } = await context.params;
    const task = getTaskExecution(taskId);
    if (!task) {
      return NextResponse.json({ error: 'Task not found' }, { status: 404 });
    }
    return NextResponse.json({ task, tree: getTaskTree(taskId) });
  } catch (error) {
    console.error('Failed to get task:', error);
    return NextResponse.json({ error: 'Failed to get task' }, { status: 500 });
  }
}
