import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json(
    {
      error: 'service control disabled in mission control v1',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}
