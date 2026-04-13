import { NextRequest, NextResponse } from 'next/server';

const ALLOWED_ACTIONS = new Set(['refresh', 'ack-alert', 'copy-command', 'open-link', 'rerun-safe-check']);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action } = body;

    if (!action) {
      return NextResponse.json({ error: 'Missing action' }, { status: 400 });
    }

    if (!ALLOWED_ACTIONS.has(action)) {
      return NextResponse.json(
        {
          error: `action not allowed in mission control v1: ${action}`,
          code: 'ACTION_NOT_ALLOWED_IN_V1',
          allowedActions: Array.from(ALLOWED_ACTIONS),
        },
        { status: 403 }
      );
    }

    return NextResponse.json({
      success: true,
      action,
      status: 'accepted',
      mode: 'placeholder',
      message: 'light action allowlisted but not yet implemented in v1',
    });
  } catch (error) {
    console.error('[actions] Error:', error);
    return NextResponse.json({ error: 'Action failed' }, { status: 500 });
  }
}
