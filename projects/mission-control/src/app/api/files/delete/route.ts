import { NextResponse } from 'next/server';

export async function DELETE() {
  return NextResponse.json(
    {
      error: 'generic file delete disabled in mission control v1',
      code: 'DISABLED_IN_V1',
    },
    { status: 403 }
  );
}
