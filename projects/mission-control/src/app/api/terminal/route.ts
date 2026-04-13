import { NextResponse } from 'next/server';

function disabled() {
  return NextResponse.json(
    {
      error: 'terminal disabled in mission control v1',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}

export async function GET() {
  return disabled();
}

export async function POST() {
  return disabled();
}
