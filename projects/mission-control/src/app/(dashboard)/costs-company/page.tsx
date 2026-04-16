"use client";

import { useState, useEffect } from "react";
import { DollarSign, Building2, TrendingUp, PieChart, Users } from "lucide-react";

const COMPANY_META: Record<string, { name: string; color: string }> = {
  mensura: { name: "Mensura Engenharia", color: "#3b82f6" },
  mia: { name: "MIA Engenharia", color: "#10b981" },
  pcs: { name: "PCS Engenharia", color: "#f59e0b" },
  corporativo: { name: "Corporativo", color: "#8b5cf6" },
};

export default function CostsCompanyPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch("/api/costs-company").then(r => r.json()).then(setData).catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-6 min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <DollarSign className="w-7 h-7 text-emerald-400" /> Custos por Empresa
        </h1>
        <p className="text-sm text-gray-400 mt-1">Visão consolidada de gastos com IA por empresa</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {Object.entries(COMPANY_META).map(([id, meta]) => {
          const companyData = data?.companies?.[id];
          const agentCount = companyData?.agents?.length || 0;
          return (
            <div key={id} className="bg-gray-800/40 border border-gray-700/50 rounded-xl p-5 hover:border-gray-600 transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: meta.color + "20" }}>
                  <Building2 className="w-5 h-5" style={{ color: meta.color }} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{meta.name}</h3>
                  <p className="text-xs text-gray-500">{agentCount} agente{agentCount !== 1 ? "s" : ""}</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Agentes</span>
                  <span className="text-gray-300">{companyData?.agents?.join(", ") || "—"}</span>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-gray-700/40">
                <div className="text-xs text-gray-500">Conecte o token tracking para ver custos reais</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-gray-800/30 border border-gray-700/40 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <PieChart className="w-5 h-5 text-indigo-400" /> Próximos Passos
        </h2>
        <div className="text-sm text-gray-400 space-y-1">
          <p>• Token tracking por agente será ativado quando os heartbeats confirmarem uso real</p>
          <p>• Custos serão calculados automaticamente por provider (Anthropic, DeepSeek, Gemini)</p>
          <p>• Budget caps por empresa podem ser definidos na aba Configurações</p>
        </div>
      </div>
    </div>
  );
}
