"use client";

import { useState, useEffect } from "react";
import { Brain, AlertTriangle, CheckCircle2, XCircle, RefreshCw, Database } from "lucide-react";
import { fetchJson } from "@/lib/fetch";

interface AgentHealth {
  agent: string;
  health: "healthy" | "warning" | "critical" | "missing";
  fileCount: number;
  totalSizeKB: number;
  staleDays: number;
  lastUpdated: string | null;
}

const HEALTH_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  healthy:  { color: "var(--positive)",  bg: "rgba(47,107,73,0.10)",  label: "Saudável"    },
  warning:  { color: "var(--warning)",   bg: "rgba(217,119,6,0.10)",  label: "Atenção"     },
  critical: { color: "var(--negative)",  bg: "rgba(185,28,28,0.10)",  label: "Crítico"     },
  missing:  { color: "var(--text-muted)",bg: "var(--surface-elevated)",label: "Sem memória" },
};

export default function MemoryHealthPage() {
  const [agents, setAgents] = useState<AgentHealth[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    setLoading(true);
    fetchJson<{ ok: boolean; agents: AgentHealth[] }>("/api/memory-health")
      .then((d) => { if (d.ok) setAgents(d.agents); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(refresh, []);

  const healthCounts = {
    healthy:  agents.filter((a) => a.health === "healthy").length,
    warning:  agents.filter((a) => a.health === "warning").length,
    critical: agents.filter((a) => a.health === "critical").length,
    missing:  agents.filter((a) => a.health === "missing").length,
  };

  return (
    <div className="p-6 space-y-6" style={{ backgroundColor: "var(--background)" }}>
      <div className="flex items-center justify-between">
        <div>
          <h1
            className="text-2xl font-bold flex items-center gap-2"
            style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}
          >
            <Brain className="w-7 h-7" style={{ color: "var(--info)" }} />
            Memory Health Monitor
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            Detecta drift, staleness e lacunas na memória dos agentes
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition text-sm"
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text-secondary)",
          }}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Atualizar
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(healthCounts).map(([k, v]) => {
          const cfg = HEALTH_CONFIG[k];
          return (
            <div
              key={k}
              className="rounded-xl p-4 text-center"
              style={{ backgroundColor: cfg.bg, border: "1px solid var(--border)" }}
            >
              <div className="text-3xl font-bold" style={{ color: cfg.color }}>{v}</div>
              <div className="text-xs mt-1" style={{ color: cfg.color }}>{cfg.label}</div>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        {[...agents]
          .sort((a, b) => {
            const order: Record<string, number> = { critical: 0, warning: 1, missing: 2, healthy: 3 };
            return (order[a.health] ?? 4) - (order[b.health] ?? 4);
          })
          .map((agent) => {
            const cfg = HEALTH_CONFIG[agent.health] || HEALTH_CONFIG.missing;
            return (
              <div
                key={agent.agent}
                className="rounded-xl p-4 flex items-center gap-4 transition-all"
                style={{
                  backgroundColor: "var(--surface)",
                  border: "1px solid var(--border)",
                }}
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: cfg.bg }}
                >
                  {agent.health === "healthy"  ? <CheckCircle2 className="w-5 h-5" style={{ color: cfg.color }} /> :
                   agent.health === "warning"  ? <AlertTriangle className="w-5 h-5" style={{ color: cfg.color }} /> :
                   agent.health === "critical" ? <XCircle      className="w-5 h-5" style={{ color: cfg.color }} /> :
                                                 <Database     className="w-5 h-5" style={{ color: cfg.color }} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                      {agent.agent}
                    </span>
                    <span
                      className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                      style={{ backgroundColor: cfg.bg, color: cfg.color }}
                    >
                      {cfg.label}
                    </span>
                  </div>
                  <div className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    {agent.fileCount} arquivos • {agent.totalSizeKB} KB
                    {agent.staleDays >= 0 && ` • ${agent.staleDays === 0 ? "atualizado hoje" : `${agent.staleDays} dia${agent.staleDays > 1 ? "s" : ""} sem atualização`}`}
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-xs" style={{ color: "var(--text-muted)" }}>Última atualização</div>
                  <div className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    {agent.lastUpdated ? new Date(agent.lastUpdated).toLocaleDateString("pt-BR") : "—"}
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}
