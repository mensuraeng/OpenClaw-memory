"use client";

import { useState, useEffect } from "react";
import { Brain, AlertTriangle, CheckCircle2, XCircle, RefreshCw, Database } from "lucide-react";

const HEALTH_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  healthy: { color: "#10b981", bg: "#10b98115", label: "Saudável" },
  warning: { color: "#f59e0b", bg: "#f59e0b15", label: "Atenção" },
  critical: { color: "#ef4444", bg: "#ef444415", label: "Crítico" },
  missing: { color: "#6b7280", bg: "#6b728015", label: "Sem memória" },
};

export default function MemoryHealthPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    setLoading(true);
    fetch("/api/memory-health").then(r => r.json()).then(d => { if (d.ok) setAgents(d.agents); }).finally(() => setLoading(false));
  };

  useEffect(refresh, []);

  const healthCounts = {
    healthy: agents.filter(a => a.health === "healthy").length,
    warning: agents.filter(a => a.health === "warning").length,
    critical: agents.filter(a => a.health === "critical").length,
    missing: agents.filter(a => a.health === "missing").length,
  };

  return (
    <div className="p-6 space-y-6 min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Brain className="w-7 h-7 text-purple-400" /> Memory Health Monitor
          </h1>
          <p className="text-sm text-gray-400 mt-1">Detecta drift, staleness e lacunas na memória dos agentes</p>
        </div>
        <button onClick={refresh} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition text-sm">
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Atualizar
        </button>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {Object.entries(healthCounts).map(([k, v]) => {
          const cfg = HEALTH_CONFIG[k];
          return (
            <div key={k} className="rounded-xl p-4 text-center border border-gray-700/40" style={{ backgroundColor: cfg.bg }}>
              <div className="text-3xl font-bold" style={{ color: cfg.color }}>{v}</div>
              <div className="text-xs mt-1" style={{ color: cfg.color }}>{cfg.label}</div>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        {agents.sort((a, b) => {
          const order = { critical: 0, warning: 1, missing: 2, healthy: 3 };
          return (order[a.health as keyof typeof order] ?? 4) - (order[b.health as keyof typeof order] ?? 4);
        }).map(agent => {
          const cfg = HEALTH_CONFIG[agent.health] || HEALTH_CONFIG.missing;
          return (
            <div key={agent.agent} className="bg-gray-800/40 border border-gray-700/40 rounded-xl p-4 flex items-center gap-4 hover:border-gray-600 transition">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: cfg.bg }}>
                {agent.health === "healthy" ? <CheckCircle2 className="w-5 h-5" style={{ color: cfg.color }} /> :
                 agent.health === "warning" ? <AlertTriangle className="w-5 h-5" style={{ color: cfg.color }} /> :
                 agent.health === "critical" ? <XCircle className="w-5 h-5" style={{ color: cfg.color }} /> :
                 <Database className="w-5 h-5" style={{ color: cfg.color }} />}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">{agent.agent}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ backgroundColor: cfg.bg, color: cfg.color }}>{cfg.label}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {agent.fileCount} arquivos • {agent.totalSizeKB} KB
                  {agent.staleDays >= 0 && ` • ${agent.staleDays === 0 ? "atualizado hoje" : `${agent.staleDays} dia${agent.staleDays > 1 ? "s" : ""} sem atualização`}`}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Última atualização</div>
                <div className="text-sm text-gray-300">{agent.lastUpdated ? new Date(agent.lastUpdated).toLocaleDateString("pt-BR") : "—"}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
