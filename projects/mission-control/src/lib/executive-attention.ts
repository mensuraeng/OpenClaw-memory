import { getActivities, type Activity } from "@/lib/activities-db";

export interface ExecutiveAttentionItem {
  tipo: "sem_resposta" | "silencio_alto" | "decisao_acumulada" | "pendencia_critica";
  titulo: string;
  detalhe: string;
  severidade: "critico" | "atencao";
  empresa?: string;
  agente?: string;
  timestamp?: string;
}

function inferEmpresa(activity: Activity): string | undefined {
  const text = `${activity.agent || ""} ${activity.description || ""}`.toLowerCase();
  if (text.includes("mensura")) return "MENSURA";
  if (text.includes("mia")) return "MIA";
  if (text.includes("pcs")) return "PCS";
  return undefined;
}

function hoursSince(timestamp?: string): number | null {
  if (!timestamp) return null;
  const diff = Date.now() - new Date(timestamp).getTime();
  if (Number.isNaN(diff)) return null;
  return Math.floor(diff / (1000 * 60 * 60));
}

export function getExecutiveAttentionItems(): ExecutiveAttentionItem[] {
  const since48h = new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString();
  const since7d = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

  const recent = getActivities({ startDate: since48h, limit: 200, sort: "newest" }).activities;
  const week = getActivities({ startDate: since7d, limit: 400, sort: "newest" }).activities;

  const items: ExecutiveAttentionItem[] = [];

  const pendingOld = recent.filter((a) => ["pending", "running"].includes(a.status));
  for (const activity of pendingOld.slice(0, 4)) {
    const h = hoursSince(activity.timestamp);
    if (h !== null && h >= 6) {
      items.push({
        tipo: "sem_resposta",
        titulo: "Item sem resposta ou conclusão",
        detalhe: activity.description,
        severidade: h >= 24 ? "critico" : "atencao",
        empresa: inferEmpresa(activity),
        agente: activity.agent || undefined,
        timestamp: activity.timestamp,
      });
    }
  }

  const byAgentLatest = new Map<string, Activity>();
  for (const activity of week) {
    if (!activity.agent) continue;
    if (!byAgentLatest.has(activity.agent)) {
      byAgentLatest.set(activity.agent, activity);
    }
  }
  for (const [agent, activity] of Array.from(byAgentLatest.entries()).slice(0, 8)) {
    const h = hoursSince(activity.timestamp);
    if (h !== null && h >= 48) {
      items.push({
        tipo: "silencio_alto",
        titulo: "Agente com silêncio elevado",
        detalhe: `${agent} sem sinal recente há ${h}h`,
        severidade: h >= 96 ? "critico" : "atencao",
        empresa: inferEmpresa(activity),
        agente: agent,
        timestamp: activity.timestamp,
      });
    }
  }

  const decisionKeywords = ["decisão", "aprovação", "aprovar", "validar", "aguarda", "alinhamento"];
  const decisionLike = recent.filter((a) => decisionKeywords.some((k) => a.description.toLowerCase().includes(k)));
  const decisionCountByEmpresa = new Map<string, number>();
  for (const activity of decisionLike) {
    const empresa = inferEmpresa(activity) || "GERAL";
    decisionCountByEmpresa.set(empresa, (decisionCountByEmpresa.get(empresa) || 0) + 1);
  }
  for (const [empresa, count] of decisionCountByEmpresa.entries()) {
    if (count >= 2) {
      items.push({
        tipo: "decisao_acumulada",
        titulo: "Acúmulo de decisões pendentes",
        detalhe: `${empresa} com ${count} sinais recentes de decisão/validação pendente`,
        severidade: count >= 4 ? "critico" : "atencao",
        empresa,
      });
    }
  }

  const criticalKeywords = ["urgente", "crítico", "critico", "bloqueio", "erro", "falha", "atraso"];
  const criticalEvents = recent.filter((a) => criticalKeywords.some((k) => a.description.toLowerCase().includes(k)) || a.status === "error");
  for (const activity of criticalEvents.slice(0, 5)) {
    items.push({
      tipo: "pendencia_critica",
      titulo: "Sinal crítico recente",
      detalhe: activity.description,
      severidade: activity.status === "error" ? "critico" : "atencao",
      empresa: inferEmpresa(activity),
      agente: activity.agent || undefined,
      timestamp: activity.timestamp,
    });
  }

  const unique = new Map<string, ExecutiveAttentionItem>();
  for (const item of items) {
    const key = `${item.tipo}:${item.detalhe}`;
    if (!unique.has(key)) unique.set(key, item);
  }

  const severityWeight = { critico: 2, atencao: 1 };
  return Array.from(unique.values())
    .sort((a, b) => severityWeight[b.severidade] - severityWeight[a.severidade])
    .slice(0, 8);
}
