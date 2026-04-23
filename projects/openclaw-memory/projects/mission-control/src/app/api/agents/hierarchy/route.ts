import { NextResponse } from "next/server";
import { readFileSync, writeFileSync, existsSync } from "fs";

export const dynamic = "force-dynamic";

const OPENCLAW_DIR = process.env.OPENCLAW_DIR || "/root/.openclaw";
const MC_CONFIG_PATH = OPENCLAW_DIR + "/mission-control-config.json";

function readMcConfig(): Record<string, unknown> {
  try {
    if (existsSync(MC_CONFIG_PATH)) {
      return JSON.parse(readFileSync(MC_CONFIG_PATH, "utf-8"));
    }
  } catch { /* ignore */ }
  return {};
}

function writeMcConfig(data: Record<string, unknown>): void {
  writeFileSync(MC_CONFIG_PATH, JSON.stringify(data, null, 2));
}

// PUT /api/agents/hierarchy — salva conexões no mission-control-config.json (não toca no openclaw.json)
export async function PUT(req: Request) {
  try {
    const body = await req.json();
    const { connections } = body as { connections: Record<string, string[]> };

    if (!connections || typeof connections !== "object") {
      return NextResponse.json({ error: "connections object required" }, { status: 400 });
    }

    const mcConfig = readMcConfig();
    mcConfig.agentConnections = connections;
    mcConfig.updatedAt = new Date().toISOString();
    writeMcConfig(mcConfig);

    return NextResponse.json({ ok: true, message: "Hierarquia salva no Mission Control config." });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

// GET /api/agents/hierarchy — lê conexões do mission-control-config.json
export async function GET() {
  try {
    const mcConfig = readMcConfig();
    const connections = (mcConfig.agentConnections as Record<string, string[]>) || {};
    return NextResponse.json({ connections });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
