import type { AgentOperationalStatus } from "@/lib/agents-operational";

export interface AgentApiShape {
  id: string;
  empresa?: string;
  funcao?: string;
  statusOperacional?: AgentOperationalStatus;
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

export interface CompanySummary {
  empresa: string;
  agentes: number;
  riscoAlto: number;
  pendencias: number;
  decisoes: number;
  inertes: number;
  tracionando: number;
  statusGeral: "estavel" | "atencao" | "critico";
  leitura: string;
}

export function buildCompanySummaries(agents: AgentApiShape[]): CompanySummary[] {
  const grouped = agents.reduce<Record<string, AgentApiShape[]>>((acc, agent) => {
    const key = agent.empresa || "SEM EMPRESA";
    acc[key] = acc[key] || [];
    acc[key].push(agent);
    return acc;
  }, {});

  return Object.entries(grouped).map(([empresa, grupo]) => {
    const riscoAlto = grupo.filter((a) => a.sinais?.riscoNivel === "alto").length;
    const pendencias = grupo.reduce((sum, a) => sum + (a.sinais?.pendenciasAbertas || 0), 0);
    const decisoes = grupo.reduce((sum, a) => sum + (a.sinais?.decisoesPendentes || 0), 0);
    const inertes = grupo.filter((a) => a.sinais?.statusUtilidade === "inerte").length;
    const tracionando = grupo.filter((a) => a.sinais?.statusUtilidade === "tracionando").length;

    let statusGeral: CompanySummary["statusGeral"] = "estavel";
    let leitura = "Base operacional estável";

    if (riscoAlto > 0 || decisoes >= 2) {
      statusGeral = "critico";
      leitura = "Há risco alto ou decisões acumuladas exigindo atenção";
    } else if (pendencias > 0 || inertes > 0) {
      statusGeral = "atencao";
      leitura = "Existe fila aberta ou baixa tração em parte da operação";
    } else if (tracionando > 0) {
      leitura = "Operação em tração recente";
    }

    return {
      empresa,
      agentes: grupo.length,
      riscoAlto,
      pendencias,
      decisoes,
      inertes,
      tracionando,
      statusGeral,
      leitura,
    };
  }).sort((a, b) => {
    const weight = { critico: 3, atencao: 2, estavel: 1 };
    return weight[b.statusGeral] - weight[a.statusGeral];
  });
}
