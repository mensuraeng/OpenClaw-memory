import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json(
    {
      error: 'generic file write disabled in mission control v1',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}
