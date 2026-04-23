import { NextResponse } from "next/server";
import { readdirSync, statSync } from "fs";
import path from "path";

const OPENCLAW_HOME = process.env.OPENCLAW_HOME || `${process.env.HOME}/.openclaw`;

function analyzeMemory() {
  const agents = ["main","mensura","mia","pcs","finance","rh","marketing","producao","juridico","bi","suprimentos","autopilot"];
  const results: Array<{ agent: string; fileCount: number; totalSizeKB: number; lastUpdated: string | null; staleDays: number; health: string }> = [];
  const now = Date.now();

  for (const agent of agents) {
    const memDir = path.join(OPENCLAW_HOME, "agents", agent, "memory");
    try {
      const files = readdirSync(memDir).filter((f: string) => f.endsWith(".md") || f.endsWith(".json"));
      let totalSize = 0;
      let oldestMs = now;
      let newestMs = 0;

      for (const f of files) {
        const stat = statSync(path.join(memDir, f));
        totalSize += stat.size;
        if (stat.mtimeMs < oldestMs) oldestMs = stat.mtimeMs;
        if (stat.mtimeMs > newestMs) newestMs = stat.mtimeMs;
      }

      const staleDays = Math.floor((now - newestMs) / 86400000);
      const health = staleDays > 7 ? "critical" : staleDays > 3 ? "warning" : "healthy";

      results.push({
        agent,
        fileCount: files.length,
        totalSizeKB: Math.round(totalSize / 1024),
        lastUpdated: new Date(newestMs).toISOString(),
        staleDays,
        health,
      });
    } catch {
      results.push({
        agent,
        fileCount: 0,
        totalSizeKB: 0,
        lastUpdated: null,
        staleDays: -1,
        health: "missing",
      });
    }
  }
  return results;
}

export async function GET() {
  try {
    return NextResponse.json({ ok: true, agents: analyzeMemory(), timestamp: new Date().toISOString() });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e.message });
  }
}
