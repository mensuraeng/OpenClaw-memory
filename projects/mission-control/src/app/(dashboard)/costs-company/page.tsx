"use client";

import { useState, useEffect } from "react";
import { DollarSign, Building2, PieChart } from "lucide-react";

interface CompanyMeta {
  name: string;
  color: string;
}

interface CompanyData {
  agents?: string[];
}

interface CostsCompanyResponse {
  companies?: Record<string, CompanyData>;
}

const COMPANY_META: Record<string, CompanyMeta> = {
  mensura: { name: "Mensura Engenharia", color: "#3b82f6" },
  mia: { name: "MIA Engenharia", color: "#10b981" },
  pcs: { name: "PCS Engenharia", color: "#f59e0b" },
  corporativo: { name: "Corporativo", color: "#8b5cf6" },
};

export default function CostsCompanyPage() {
  const [data, setData] = useState<CostsCompanyResponse | null>(null);

  useEffect(() => {
    fetch("/api/costs-company")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-6 min-h-screen" style={{ backgroundColor: "var(--background)" }}>
      <div>
        <h1
          className="text-2xl font-bold flex items-center gap-2"
          style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}
        >
          <DollarSign className="w-7 h-7" style={{ color: "var(--positive)" }} />
          Custos por Empresa
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Visão consolidada de gastos com IA por empresa
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(COMPANY_META).map(([id, meta]) => {
          const companyData = data?.companies?.[id];
          const agentCount = companyData?.agents?.length ?? 0;
          return (
            <div
              key={id}
              className="rounded-xl p-5 transition-all"
              style={{
                backgroundColor: "var(--surface)",
                border: "1px solid var(--border)",
              }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: meta.color + "20" }}
                >
                  <Building2 className="w-5 h-5" style={{ color: meta.color }} />
                </div>
                <div>
                  <h3
                    className="text-sm font-semibold"
                    style={{ color: "var(--text-primary)", fontFamily: "var(--font-body)" }}
                  >
                    {meta.name}
                  </h3>
                  <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {agentCount} agente{agentCount !== 1 ? "s" : ""}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span style={{ color: "var(--text-muted)" }}>Agentes</span>
                  <span style={{ color: "var(--text-secondary)" }}>
                    {companyData?.agents?.join(", ") || "—"}
                  </span>
                </div>
              </div>
              <div
                className="mt-4 pt-3"
                style={{ borderTop: "1px solid var(--border)" }}
              >
                <div className="text-xs" style={{ color: "var(--text-muted)" }}>
                  Conecte o token tracking para ver custos reais
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div
        className="rounded-xl p-6"
        style={{
          backgroundColor: "var(--surface)",
          border: "1px solid var(--border)",
        }}
      >
        <h2
          className="text-lg font-semibold mb-2 flex items-center gap-2"
          style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}
        >
          <PieChart className="w-5 h-5" style={{ color: "var(--info)" }} />
          Próximos Passos
        </h2>
        <div className="text-sm space-y-1" style={{ color: "var(--text-secondary)" }}>
          <p>• Token tracking por agente será ativado quando os heartbeats confirmarem uso real</p>
          <p>• Custos serão calculados automaticamente por provider (Anthropic, DeepSeek, Gemini)</p>
          <p>• Budget caps por empresa podem ser definidos na aba Configurações</p>
        </div>
      </div>
    </div>
  );
}
