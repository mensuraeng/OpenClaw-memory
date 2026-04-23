import { NextResponse } from 'next/server';
import { getTaskAttention } from '@/lib/task-tracking';

export async function GET() {
  try {
    return NextResponse.json(getTaskAttention());
  } catch (error) {
    console.error('Failed to get task attention:', error);
    return NextResponse.json({ error: 'Failed to get task attention' }, { status: 500 });
  }
}
