import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      error: 'file download disabled in mission control v1',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}
