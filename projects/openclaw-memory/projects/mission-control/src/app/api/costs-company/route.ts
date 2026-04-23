import { NextRequest, NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";
import path from "path";

const OPENCLAW_HOME = process.env.OPENCLAW_HOME || `${process.env.HOME}/.openclaw`;

const AGENT_COMPANY_MAP: Record<string, string> = {
  mensura: "mensura", mia: "mia", pcs: "pcs",
  finance: "corporativo", rh: "corporativo", marketing: "corporativo",
  producao: "corporativo", juridico: "corporativo", bi: "corporativo",
  suprimentos: "corporativo", main: "corporativo", autopilot: "corporativo",
};

export async function GET() {
  try {
    const configPath = path.join(OPENCLAW_HOME, "openclaw.json");
    if (!existsSync(configPath)) return NextResponse.json({ ok: false, error: "Config not found" });
    const config = JSON.parse(readFileSync(configPath, "utf-8"));
    const agents = config.agents?.list || [];

    const companies: Record<string, { agents: string[]; totalSessions: number }> = {};

    for (const agent of agents) {
      const agentId = agent.id || agent.agentId || "unknown";
      const company = AGENT_COMPANY_MAP[agentId] || "corporativo";
      if (!companies[company]) companies[company] = { agents: [], totalSessions: 0 };
      companies[company].agents.push(agentId);
    }

    return NextResponse.json({
      ok: true,
      companies,
      agentMap: AGENT_COMPANY_MAP,
      totalAgents: agents.length,
      timestamp: new Date().toISOString(),
    });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e.message });
  }
}
