import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      error: 'file tree endpoint disabled during mission control v1 hardening',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}

export async function PUT() {
  return NextResponse.json(
    {
      error: 'file save endpoint disabled during mission control v1 hardening',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}
