import { NextResponse } from "next/server";
import { readFileSync, statSync } from "fs";
import { join } from "path";
import { AGENT_OPERATIONAL_PROFILES, type AgentOperationalStatus, type AgentExecutionMode, type AgentValidationLevel, type AgentBlockerStatus } from "@/lib/agents-operational";
import { getAgentSignalSummary } from "@/lib/agents-signals";
import { buildCompanySummaries } from "@/lib/agents-company-summary";
import { getExecutiveMemorySummary } from "@/lib/memory-executive";
import { getExecutiveAttentionItems } from "@/lib/executive-attention";

export const dynamic = "force-dynamic";

interface Agent {
  id: string;
  name: string;
  emoji: string;
  color: string;
  model: string;
  workspace: string;
  status: "online" | "offline" | "unknown";
  lastActivity?: string;
  activeSessions: number;
  isAutopilot?: boolean;
  sessionsDirExists: boolean;
  allowAgents: string[];
  allowAgentsDetails: Array<{ id: string; name: string; emoji: string; color: string }>;
  dmPolicy?: string;
  empresa?: string;
  funcao?: string;
  papel?: string;
  quandoAcionar?: string[];
  saidaEsperada?: string[];
  quandoEscalar?: string[];
  quandoNaoUsar?: string[];
  statusOperacional?: AgentOperationalStatus;
  observacao?: string;
  modoExecucao?: AgentExecutionMode;
  validacaoPadrao?: AgentValidationLevel;
  estadoBloqueio?: AgentBlockerStatus;
  sinais?: {
    riscoNivel: "baixo" | "medio" | "alto";
    riscoLabel: string;
    pendenciasAbertas: number;
    decisoesPendentes: number;
    silencioHoras: number | null;
    ultimoSinal?: string;
    statusUtilidade: "tracionando" | "monitorar" | "inerte";
  };
}

const DEFAULT_AGENT_CONFIG: Record<string, { emoji: string; color: string; name?: string }> = {
  main:        { emoji: process.env.NEXT_PUBLIC_AGENT_EMOJI || "🤖", color: "#ff6b35", name: process.env.NEXT_PUBLIC_AGENT_NAME || "Main" },
  rh:          { emoji: "👥", color: "#8B5CF6", name: "RH" },
  marketing:   { emoji: "📣", color: "#EC4899", name: "Marketing" },
  producao:    { emoji: "🏗️", color: "#F59E0B", name: "Produção" },
  finance:     { emoji: "💰", color: "#10B981", name: "Finance" },
  mia:         { emoji: "🏛️", color: "#3B82F6", name: "Mia" },
  mensura:     { emoji: "📐", color: "#EF4444", name: "Mensura" },
  autopilot:   { emoji: "🤖", color: "#6B7280", name: "Autopilot" },
  juridico:    { emoji: "⚖️", color: "#6366F1", name: "Jurídico" },
  bi:          { emoji: "📊", color: "#06B6D4", name: "BI / Dados" },
  suprimentos: { emoji: "📦", color: "#D97706", name: "Suprimentos" },
  pcs:         { emoji: "🏢", color: "#7C3AED", name: "PCS" },
};

function getLastActivity(workspace: string): { lastActivity?: string; status: "online" | "offline" | "unknown" } {
  try {
    const today = new Date().toISOString().split("T")[0];
    const memoryFile = join(workspace, "memory", `${today}.md`);
    const stat = statSync(memoryFile);
    const lastActivity = stat.mtime.toISOString();
    const status = Date.now() - stat.mtime.getTime() < 5 * 60 * 1000 ? "online" : "offline";
    return { lastActivity, status };
  } catch {
    return { status: "unknown" };
  }
}

function sessionsDirExists(agentId: string): boolean {
  const dir = `${process.env.OPENCLAW_DIR || "/root/.openclaw"}/agents/${agentId}/sessions`;
  try { statSync(dir); return true; } catch { return false; }
}

export async function GET() {
  try {
    const configPath = (process.env.OPENCLAW_DIR || "/root/.openclaw") + "/openclaw.json";
    const config = JSON.parse(readFileSync(configPath, "utf-8"));

    const agents: Agent[] = config.agents.list.map((agent: Record<string, unknown>) => {
      const id = agent.id as string;
      const defaults = DEFAULT_AGENT_CONFIG[id] || {};
      const workspace = (agent.workspace as string) || 
        ((process.env.OPENCLAW_DIR || "/root/.openclaw") + "/workspace");
      const model = (config.agents?.defaults?.model?.primary as string) || "unknown";
      
      const { lastActivity, status } = getLastActivity(workspace);

      const operational = AGENT_OPERATIONAL_PROFILES[id];
      const sinais = getAgentSignalSummary(id, lastActivity);

      return {
        id,
        name: (agent.name as string) || defaults.name || id,
        emoji: defaults.emoji || "🤖",
        color: defaults.color || "#666666",
        model,
        workspace,
        status,
        lastActivity,
        activeSessions: 0,
        isAutopilot: id === "autopilot",
        sessionsDirExists: sessionsDirExists(id),
        allowAgents: (agent.allowAgents as string[]) || [],
        allowAgentsDetails: [],
        dmPolicy: (agent.dmPolicy as string) || undefined,
        empresa: operational?.empresa,
        funcao: operational?.funcao,
        papel: operational?.papel,
        quandoAcionar: operational?.quandoAcionar || [],
        saidaEsperada: operational?.saidaEsperada || [],
        quandoEscalar: operational?.quandoEscalar || [],
        quandoNaoUsar: operational?.quandoNaoUsar || [],
        statusOperacional: operational?.statusOperacional,
        observacao: operational?.observacao,
        modoExecucao: operational?.modoExecucao,
        validacaoPadrao: operational?.validacaoPadrao,
        estadoBloqueio: operational?.estadoBloqueio,
        sinais,
        // NOTE: botToken, auth.token, credentials INTENTIONALLY OMITTED (F16)
      };
    });

    const agentIndex = new Map(agents.map((agent) => [agent.id, agent]));

    for (const agent of agents) {
      agent.allowAgentsDetails = (agent.allowAgents || [])
        .map((subId) => agentIndex.get(subId))
        .filter((sub): sub is Agent => Boolean(sub))
        .map((sub) => ({
          id: sub.id,
          name: sub.name,
          emoji: sub.emoji,
          color: sub.color,
        }));
    }

    const companies = buildCompanySummaries(agents);
    const executive = getExecutiveMemorySummary();
    const attention = getExecutiveAttentionItems();

    return NextResponse.json({ agents, companies, executive, attention });
  } catch (error) {
    console.error("[agents] Error:", error);
    return NextResponse.json({ error: "Failed to fetch agents" }, { status: 500 });
  }
}
