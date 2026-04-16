import { NextResponse } from 'next/server';

const BLOCKED = { error: 'file delete disabled in mission control v1', code: 'DISABLED_IN_V1' };

export async function GET() { return NextResponse.json(BLOCKED, { status: 403 }); }
export async function POST() { return NextResponse.json(BLOCKED, { status: 403 }); }
export async function PUT() { return NextResponse.json(BLOCKED, { status: 403 }); }
export async function DELETE() { return NextResponse.json(BLOCKED, { status: 403 }); }
