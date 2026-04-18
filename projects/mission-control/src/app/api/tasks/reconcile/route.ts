import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { executeRetryQueue, reconcileTaskEvidence, reconcileTasksWithSessions } from '@/lib/task-tracking';

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

    return NextResponse.json({
      ok: true,
      sessionUpdates,
      evidenceUpdates,
      retryUpdates,
    });
  } catch (error) {
    console.error('Failed to reconcile tasks:', error);
    return NextResponse.json({ error: 'Failed to reconcile tasks' }, { status: 500 });
  }
}
