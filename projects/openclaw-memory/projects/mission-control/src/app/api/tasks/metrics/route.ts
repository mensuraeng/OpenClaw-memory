import { NextResponse } from 'next/server';
import { getTaskMetrics } from '@/lib/task-tracking';

export async function GET() {
  try {
    return NextResponse.json(getTaskMetrics());
  } catch (error) {
    console.error('Failed to get task metrics:', error);
    return NextResponse.json({ error: 'Failed to get task metrics' }, { status: 500 });
  }
}
