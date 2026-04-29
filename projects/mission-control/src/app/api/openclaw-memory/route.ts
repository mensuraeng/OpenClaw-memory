import { NextRequest, NextResponse } from "next/server";
import { getOpenClawMemoryControl, searchSecondBrain } from "@/lib/openclaw-memory";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get("q")?.trim();
    if (q) {
      return NextResponse.json({ ok: true, query: q, results: searchSecondBrain(q), generatedAt: new Date().toISOString() });
    }
    return NextResponse.json({ ok: true, ...getOpenClawMemoryControl() });
  } catch (error) {
    return NextResponse.json({ ok: false, error: error instanceof Error ? error.message : String(error) }, { status: 500 });
  }
}
