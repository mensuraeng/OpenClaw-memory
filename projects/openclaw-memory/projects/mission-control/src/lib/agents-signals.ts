import { getActivities } from "@/lib/activities-db";

export interface AgentSignalSummary {
  riscoNivel: "baixo" | "medio" | "alto";
  riscoLabel: string;
  pendenciasAbertas: number;
  decisoesPendentes: number;
  silencioHoras: number | null;
  ultimoSinal?: string;
  statusUtilidade: "tracionando" | "monitorar" | "inerte";
}

function hoursSince(timestamp?: string): number | null {
  if (!timestamp) return null;
  const diff = Date.now() - new Date(timestamp).getTime();
  return Math.max(0, Math.floor(diff / (1000 * 60 * 60)));
}

export function getAgentSignalSummary(agentId: string, lastActivity?: string): AgentSignalSummary {
  const now = new Date();
  const startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
  const result = getActivities({ agent: agentId, startDate, limit: 100, sort: "newest" });

  const pendenciasAbertas = result.activities.filter((a) => a.status === "pending" || a.status === "running").length;
  const decisoesPendentes = result.activities.filter((a) => {
    const d = `${a.description || ""}`.toLowerCase();
    return (d.includes("decis") || d.includes("approval") || d.includes("aprova")) && a.status !== "success";
  }).length;

  const ultimoSinal = result.activities[0]?.timestamp || lastActivity;
  const silencioHoras = hoursSince(ultimoSinal);

  let riscoNivel: AgentSignalSummary["riscoNivel"] = "baixo";
  let riscoLabel = "Operação estável";
  let statusUtilidade: AgentSignalSummary["statusUtilidade"] = "monitorar";

  if (silencioHoras !== null && silencioHoras >= 72) {
    riscoNivel = "alto";
    riscoLabel = "Silêncio operacional prolongado";
    statusUtilidade = "inerte";
  } else if (silencioHoras !== null && silencioHoras >= 24) {
    riscoNivel = "medio";
    riscoLabel = "Baixo sinal recente";
    statusUtilidade = "monitorar";
  }

  if (pendenciasAbertas >= 3 || decisoesPendentes >= 2) {
    riscoNivel = "alto";
    riscoLabel = "Acúmulo de pendências ou decisões";
    statusUtilidade = "monitorar";
  } else if (pendenciasAbertas > 0 || decisoesPendentes > 0) {
    if (riscoNivel === "baixo") {
      riscoNivel = "medio";
      riscoLabel = "Fila operacional aberta";
    }
  }

  if ((silencioHoras !== null && silencioHoras < 24) || result.activities.length >= 3) {
    statusUtilidade = "tracionando";
    if (riscoNivel === "baixo") {
      riscoLabel = "Em tração recente";
    }
  }

  return {
    riscoNivel,
    riscoLabel,
    pendenciasAbertas,
    decisoesPendentes,
    silencioHoras,
    ultimoSinal,
    statusUtilidade,
  };
}
