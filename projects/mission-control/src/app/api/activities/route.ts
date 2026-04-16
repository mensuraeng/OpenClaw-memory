import { NextRequest, NextResponse } from 'next/server';
import { getActivities } from '@/lib/activities-db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type') || undefined;
    const status = searchParams.get('status') || undefined;
    const agent = searchParams.get('agent') || undefined;
    const startDate = searchParams.get('startDate') || undefined;
    const endDate = searchParams.get('endDate') || undefined;
    const sort = (searchParams.get('sort') || 'newest') as 'newest' | 'oldest';
    const format = searchParams.get('format') || 'json';
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), format === 'csv' ? 10000 : 100);
    const offset = parseInt(searchParams.get('offset') || '0');

    const result = getActivities({ type, status, agent, startDate, endDate, sort, limit, offset });

    if (format === 'csv') {
      const header = 'id,timestamp,type,description,status,duration_ms,tokens_used,agent\n';
      const rows = result.activities.map((a) => [
        a.id, a.timestamp, a.type,
        `"${String(a.description || '').replace(/"/g, '""')}"`,
        a.status, a.duration_ms ?? '', a.tokens_used ?? '', a.agent ?? '',
      ].join(',')).join('\n');
      return new NextResponse(header + rows, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="activities-${new Date().toISOString().split('T')[0]}.csv"`,
        },
      });
    }

    return NextResponse.json({
      activities: result.activities,
      total: result.total,
      limit,
      offset,
      hasMore: offset + limit < result.total,
    });
  } catch (error) {
    console.error('Failed to get activities:', error);
    return NextResponse.json({ error: 'Failed to get activities' }, { status: 500 });
  }
}

// POST disabled in v1
export async function POST() {
  return NextResponse.json(
    { error: 'activity injection disabled in mission control v1', code: 'DISABLED_IN_V1' },
    { status: 403 }
  );
}
