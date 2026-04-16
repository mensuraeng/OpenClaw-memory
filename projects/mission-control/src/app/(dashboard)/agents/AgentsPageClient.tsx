"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Bot, Circle, MessageSquare, HardDrive, Shield, Users,
  Activity, GitBranch, LayoutGrid, RefreshCw, AlertTriangle, Clock3, Building2, Briefcase,
} from "lucide-react";
import { AgentOrganigrama } from "@/components/AgentOrganigrama";

interface Agent {
  id: string;
  name: string;
  emoji: string;
  color: string;
  model: string;
  workspace: string;
  dmPolicy?: string;
  allowAgents: string[];
  allowAgentsDetails?: Array<{ id: string; name: string; emoji: string; color: string }>;
  botToken?: string;
  status: "online" | "offline" | "unknown";
  lastActivity?: string;
  activeSessions: number;
  empresa?: string;
  funcao?: string;
  papel?: string;
  quandoAcionar?: string[];
  saidaEsperada?: string[];
  quandoEscalar?: string[];
  quandoNaoUsar?: string[];
  statusOperacional?: "ativo" | "util" | "ocioso" | "revisao" | "sobreposto";
  modoExecucao?: "direto" | "planejado" | "monitoramento";
  validacaoPadrao?: "leve" | "padrao" | "forte";
  estadoBloqueio?: "livre" | "monitorar" | "bloqueado";
  observacao?: string;
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

interface CompanySummary {
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

interface ExecutiveMemorySummary {
  pendingCritical: string[];
  pendingWaitingAle: string[];
  recentDecisions: string[];
}

export default function AgentsPage() {
  const searchParams = useSearchParams();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [executive, setExecutive] = useState<ExecutiveMemorySummary>({ pendingCritical: [], pendingWaitingAle: [], recentDecisions: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"cards" | "organigrama">("cards");
  const [empresaFiltro, setEmpresaFiltro] = useState<string>(searchParams.get("empresa") || "TODAS");

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch("/api/agents");
      const data = await res.json();
      setAgents(data.agents || []);
      setCompanies(data.companies || []);
      setExecutive(data.executive || { pendingCritical: [], pendingWaitingAle: [], recentDecisions: [] });
    } catch (error) {
      console.error("Erro ao buscar agentes:", error);
    } finally {
      setLoading(false);
    }
  };

  const empresas = useMemo(() => {
    const base = Array.from(new Set(agents.map((a) => a.empresa).filter(Boolean))) as string[];
    return ["TODAS", ...base];
  }, [agents]);

  const agentsFiltrados = useMemo(() => {
    if (empresaFiltro === "TODAS") return agents;
    return agents.filter((a) => a.empresa === empresaFiltro);
  }, [agents, empresaFiltro]);

  const companiesFiltradas = useMemo(() => {
    if (empresaFiltro === "TODAS") return companies;
    return companies.filter((c) => c.empresa === empresaFiltro);
  }, [companies, empresaFiltro]);

  const agrupadosPorEmpresa = useMemo(() => {
    return agentsFiltrados.reduce<Record<string, Agent[]>>((acc, agent) => {
      const key = agent.empresa || "SEM EMPRESA";
      acc[key] = acc[key] || [];
      acc[key].push(agent);
      return acc;
    }, {});
  }, [agentsFiltrados]);

  const tempoDecorrido = (timestamp?: string) => {
    if (!timestamp) return "Nunca";
    const diff = Date.now() - new Date(timestamp).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "agora";
    if (mins < 60) return `${mins}m atrás`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h atrás`;
    return `${Math.floor(hrs / 24)}d atrás`;
  };

  const statusLabel = (s: string) => s === "online" ? "Online" : s === "offline" ? "Offline" : "Desconhecido";
  const statusColor = (s: string) => s === "online" ? "#4ade80" : s === "offline" ? "#6b7280" : "#f59e0b";
  const statusOperacionalLabel = (s?: string) => {
    switch (s) {
      case "ativo": return "Ativo";
      case "util": return "Útil";
      case "ocioso": return "Ocioso";
      case "revisao": return "Em revisão";
      case "sobreposto": return "Sobreposto";
      default: return "Não classificado";
    }
  };
  const statusOperacionalColor = (s?: string) => {
    switch (s) {
      case "ativo": return "#22c55e";
      case "util": return "#3b82f6";
      case "ocioso": return "#94a3b8";
      case "revisao": return "#f59e0b";
      case "sobreposto": return "#ef4444";
      default: return "#6b7280";
    }
  };
  const riscoColor = (s?: string) => s === "alto" ? "#ef4444" : s === "medio" ? "#f59e0b" : "#22c55e";
  const utilidadeLabel = (s?: string) => s === "tracionando" ? "Tracionando" : s === "inerte" ? "Inerte" : "Monitorar";
  const modoExecucaoLabel = (s?: string) => s === "direto" ? "Execução direta" : s === "monitoramento" ? "Monitoramento" : "Execução planejada";
  const validacaoLabel = (s?: string) => s === "leve" ? "Validação leve" : s === "forte" ? "Validação forte" : "Validação padrão";
  const bloqueioLabel = (s?: string) => s === "bloqueado" ? "Bloqueado" : s === "monitorar" ? "Monitorar bloqueios" : "Sem bloqueio";
  const bloqueioColor = (s?: string) => s === "bloqueado" ? "#ef4444" : s === "monitorar" ? "#f59e0b" : "#22c55e";

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <RefreshCw className="animate-spin w-8 h-8" style={{ color: "var(--accent)" }} />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2"
            style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary)", letterSpacing: "-1.5px" }}>
            <Users className="inline-block w-8 h-8 mr-2 mb-1" />
            Agentes
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>
            Superfície operacional dos agentes, com risco, utilidade, silêncio e exceções executivas
          </p>
        </div>
        <button onClick={fetchAgents}
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 14px", backgroundColor: "var(--surface-elevated)", borderRadius: 6, border: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 13, cursor: "pointer" }}>
          <RefreshCw style={{ width: 14, height: 14 }} /> Atualizar
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-4">
          {companiesFiltradas.map((company) => {
            const companyColor = company.statusGeral === "critico" ? "#ef4444" : company.statusGeral === "atencao" ? "#f59e0b" : "#22c55e";
            return (
              <div key={company.empresa} className="rounded-xl p-4" style={{ backgroundColor: "var(--card)", border: `1px solid ${companyColor}40` }}>
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold" style={{ color: "var(--text-primary)" }}>{company.empresa}</div>
                  <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: `${companyColor}20`, color: companyColor, border: `1px solid ${companyColor}40` }}>
                    {company.statusGeral}
                  </span>
                </div>
                <div className="text-xs mb-3" style={{ color: "var(--text-secondary)" }}>{company.leitura}</div>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div><div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Agentes</div><div className="font-bold" style={{ color: "var(--text-primary)" }}>{company.agentes}</div></div>
                  <div><div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Risco</div><div className="font-bold" style={{ color: companyColor }}>{company.riscoAlto}</div></div>
                  <div><div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Pend.</div><div className="font-bold" style={{ color: "var(--text-primary)" }}>{company.pendencias}</div></div>
                  <div><div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Dec.</div><div className="font-bold" style={{ color: "var(--text-primary)" }}>{company.decisoes}</div></div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="rounded-xl p-4" style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>
          <div className="font-semibold mb-3" style={{ color: "var(--text-primary)" }}>Exceções executivas</div>
          <div className="space-y-3">
            <div>
              <div className="text-xs font-medium mb-2" style={{ color: "#ef4444" }}>Pendências críticas</div>
              <div className="space-y-2">
                {(executive.pendingCritical.length > 0 ? executive.pendingCritical : ["Nenhuma pendência crítica destacada"]).slice(0, 3).map((item) => (
                  <div key={item} className="text-xs rounded-lg p-2.5" style={{ backgroundColor: "#ef444412", border: "1px solid #ef444430", color: "var(--text-primary)" }}>{item}</div>
                ))}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium mb-2" style={{ color: "#f59e0b" }}>Aguardando Alê</div>
              <div className="space-y-2">
                {(executive.pendingWaitingAle.length > 0 ? executive.pendingWaitingAle : ["Nada explícito aguardando input agora"]).slice(0, 2).map((item) => (
                  <div key={item} className="text-xs rounded-lg p-2.5" style={{ backgroundColor: "#f59e0b12", border: "1px solid #f59e0b30", color: "var(--text-primary)" }}>{item}</div>
                ))}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium mb-2" style={{ color: "#3b82f6" }}>Decisões permanentes recentes</div>
              <div className="space-y-2">
                {(executive.recentDecisions.length > 0 ? executive.recentDecisions : ["Nenhuma decisão carregada"]).slice(0, 3).map((item) => (
                  <div key={item} className="text-xs rounded-lg p-2.5" style={{ backgroundColor: "#3b82f612", border: "1px solid #3b82f630", color: "var(--text-primary)" }}>{item}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-6">
        {empresas.map((empresa) => (
          <button
            key={empresa}
            onClick={() => setEmpresaFiltro(empresa)}
            className="text-xs px-3 py-1.5 rounded-full"
            style={{
              backgroundColor: empresaFiltro === empresa ? "var(--accent)" : "var(--surface-elevated)",
              color: empresaFiltro === empresa ? "white" : "var(--text-secondary)",
              border: empresaFiltro === empresa ? "1px solid var(--accent)" : "1px solid var(--border)",
            }}
          >
            {empresa}
          </button>
        ))}
      </div>

      <div className="flex gap-2 mb-6 border-b" style={{ borderColor: "var(--border)" }}>
        {[
          { id: "cards" as const, label: "Painel Operacional", icon: LayoutGrid },
          { id: "organigrama" as const, label: "Organigrama", icon: GitBranch },
        ].map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className="flex items-center gap-2 px-4 py-2 font-medium transition-all"
            style={{
              color: activeTab === id ? "var(--accent)" : "var(--text-secondary)",
              background: "none", border: "none", cursor: "pointer",
              borderBottom: activeTab === id ? "2px solid var(--accent)" : "2px solid transparent",
              paddingBottom: "0.5rem",
            }}>
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {activeTab === "organigrama" && (
        <div className="rounded-xl" style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>
          <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--border)" }}>
            <h2 className="font-semibold" style={{ color: "var(--text-primary)" }}>Hierarquia de Agentes</h2>
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>
              Visualização das permissões de comunicação entre agentes
            </p>
          </div>
          <AgentOrganigrama agents={agentsFiltrados.map(a => ({ ...a, status: (a.status === "online" ? "online" : "offline") as "online" | "offline" }))} />
        </div>
      )}

      {activeTab === "cards" && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
            {[
              { label: "Agentes", value: agentsFiltrados.length, color: "var(--accent)" },
              { label: "Risco alto", value: agentsFiltrados.filter(a => a.sinais?.riscoNivel === "alto").length, color: "#ef4444" },
              { label: "Planejados", value: agentsFiltrados.filter(a => a.modoExecucao === "planejado").length, color: "#8b5cf6" },
              { label: "Bloqueios", value: agentsFiltrados.filter(a => a.estadoBloqueio === "bloqueado").length, color: "#ef4444" },
              { label: "Pendências abertas", value: agentsFiltrados.reduce((acc, a) => acc + (a.sinais?.pendenciasAbertas || 0), 0), color: "#f59e0b" },
              { label: "Decisões pendentes", value: agentsFiltrados.reduce((acc, a) => acc + (a.sinais?.decisoesPendentes || 0), 0), color: "#3b82f6" },
            ].map((item) => (
              <div key={item.label} className="rounded-xl p-4" style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>
                <div className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>{item.label}</div>
                <div className="text-2xl font-bold" style={{ color: item.color }}>{item.value}</div>
              </div>
            ))}
          </div>

          <div className="space-y-8">
            {Object.entries(agrupadosPorEmpresa).map(([empresa, grupo]) => (
              <section key={empresa}>
                <div className="flex items-center gap-2 mb-4">
                  <Building2 className="w-4 h-4" style={{ color: "var(--text-secondary)" }} />
                  <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>{empresa}</h2>
                  <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
                    {grupo.length} agente{grupo.length !== 1 ? "s" : ""}
                  </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {grupo.map((agent) => (
                    <div key={agent.id} className="rounded-xl overflow-hidden"
                      style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>

                      <div className="px-5 py-4 flex items-center justify-between"
                        style={{
                          borderBottom: "1px solid var(--border)",
                          background: `linear-gradient(135deg, ${agent.color}15, transparent)`,
                        }}>
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                            style={{ backgroundColor: `${agent.color}20`, border: `2px solid ${agent.color}` }}>
                            {agent.emoji}
                          </div>
                          <div>
                            <h3 className="text-lg font-bold"
                              style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary)" }}>
                              {agent.name}
                            </h3>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              <Circle className="w-2 h-2"
                                style={{ fill: statusColor(agent.status), color: statusColor(agent.status) }} />
                              <span className="text-xs font-medium" style={{ color: statusColor(agent.status) }}>
                                {statusLabel(agent.status)}
                              </span>
                              {agent.funcao && (
                                <span className="text-xs" style={{ color: "var(--text-muted)" }}>• {agent.funcao}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        {agent.botToken && (
                          <div title="Bot Telegram conectado">
                            <MessageSquare className="w-5 h-5" style={{ color: "#0088cc" }} />
                          </div>
                        )}
                      </div>

                      <div className="p-5 space-y-4">
                        <div className="flex flex-wrap gap-2">
                          {agent.statusOperacional && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: `${statusOperacionalColor(agent.statusOperacional)}20`, color: statusOperacionalColor(agent.statusOperacional), border: `1px solid ${statusOperacionalColor(agent.statusOperacional)}40` }}>
                              {statusOperacionalLabel(agent.statusOperacional)}
                            </span>
                          )}
                          {agent.sinais?.statusUtilidade && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                              {utilidadeLabel(agent.sinais.statusUtilidade)}
                            </span>
                          )}
                          {agent.sinais?.riscoNivel && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: `${riscoColor(agent.sinais.riscoNivel)}20`, color: riscoColor(agent.sinais.riscoNivel), border: `1px solid ${riscoColor(agent.sinais.riscoNivel)}40` }}>
                              Risco {agent.sinais.riscoNivel}
                            </span>
                          )}
                          {agent.modoExecucao && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: "#8b5cf620", color: "#8b5cf6", border: "1px solid #8b5cf640" }}>
                              {modoExecucaoLabel(agent.modoExecucao)}
                            </span>
                          )}
                          {agent.validacaoPadrao && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: "#06b6d420", color: "#06b6d4", border: "1px solid #06b6d440" }}>
                              {validacaoLabel(agent.validacaoPadrao)}
                            </span>
                          )}
                          {agent.estadoBloqueio && (
                            <span className="text-xs px-2.5 py-1 rounded-full" style={{ backgroundColor: `${bloqueioColor(agent.estadoBloqueio)}20`, color: bloqueioColor(agent.estadoBloqueio), border: `1px solid ${bloqueioColor(agent.estadoBloqueio)}40` }}>
                              {bloqueioLabel(agent.estadoBloqueio)}
                            </span>
                          )}
                        </div>

                        {agent.papel && (
                          <div>
                            <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>Papel principal</div>
                            <div className="text-sm" style={{ color: "var(--text-primary)", lineHeight: 1.5 }}>{agent.papel}</div>
                          </div>
                        )}

                        <div className="grid grid-cols-3 gap-3">
                          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface-elevated)", border: "1px solid var(--border)" }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Pendências</div>
                            <div className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>{agent.sinais?.pendenciasAbertas || 0}</div>
                          </div>
                          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface-elevated)", border: "1px solid var(--border)" }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Decisões</div>
                            <div className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>{agent.sinais?.decisoesPendentes || 0}</div>
                          </div>
                          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface-elevated)", border: "1px solid var(--border)" }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Silêncio</div>
                            <div className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>{agent.sinais?.silencioHoras ?? 0}h</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          <div className="rounded-lg p-3" style={{ backgroundColor: "#8b5cf612", border: "1px solid #8b5cf630" }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Plano</div>
                            <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{modoExecucaoLabel(agent.modoExecucao)}</div>
                          </div>
                          <div className="rounded-lg p-3" style={{ backgroundColor: "#06b6d412", border: "1px solid #06b6d430" }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Validação</div>
                            <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{validacaoLabel(agent.validacaoPadrao)}</div>
                          </div>
                          <div className="rounded-lg p-3" style={{ backgroundColor: `${bloqueioColor(agent.estadoBloqueio)}12`, border: `1px solid ${bloqueioColor(agent.estadoBloqueio)}30` }}>
                            <div className="text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>Bloqueio</div>
                            <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{bloqueioLabel(agent.estadoBloqueio)}</div>
                          </div>
                        </div>

                        {agent.sinais?.riscoLabel && (
                          <div className="flex items-start gap-2 rounded-lg p-3" style={{ backgroundColor: `${riscoColor(agent.sinais.riscoNivel)}12`, border: `1px solid ${riscoColor(agent.sinais.riscoNivel)}30` }}>
                            <AlertTriangle className="w-4 h-4 mt-0.5" style={{ color: riscoColor(agent.sinais.riscoNivel) }} />
                            <div>
                              <div className="text-xs font-medium" style={{ color: riscoColor(agent.sinais.riscoNivel) }}>Leitura operacional</div>
                              <div className="text-sm" style={{ color: "var(--text-primary)" }}>{agent.sinais.riscoLabel}</div>
                            </div>
                          </div>
                        )}

                        {agent.quandoAcionar && agent.quandoAcionar.length > 0 && (
                          <div>
                            <div className="text-xs font-medium mb-2 flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
                              <Briefcase className="w-3 h-3" /> Quando acionar
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {agent.quandoAcionar.slice(0, 4).map((item) => (
                                <span key={item} className="text-xs px-2 py-1 rounded" style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                                  {item}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {agent.saidaEsperada && agent.saidaEsperada.length > 0 && (
                          <div>
                            <div className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>Saída esperada</div>
                            <div className="flex flex-wrap gap-2">
                              {agent.saidaEsperada.slice(0, 4).map((item) => (
                                <span key={item} className="text-xs px-2 py-1 rounded" style={{ backgroundColor: `${agent.color}12`, color: "var(--text-primary)", border: `1px solid ${agent.color}30` }}>
                                  {item}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div className="flex items-start gap-3">
                            <Bot className="w-4 h-4 mt-0.5" style={{ color: agent.color }} />
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>Modelo</div>
                              <div className="text-sm font-mono truncate" style={{ color: "var(--text-primary)" }}>
                                {agent.model}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-start gap-3">
                            <Clock3 className="w-4 h-4 mt-0.5" style={{ color: agent.color }} />
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>Último sinal</div>
                              <div className="text-sm" style={{ color: "var(--text-primary)" }}>
                                {tempoDecorrido(agent.sinais?.ultimoSinal || agent.lastActivity)}
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-start gap-3">
                          <HardDrive className="w-4 h-4 mt-0.5" style={{ color: agent.color }} />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>Workspace</div>
                            <div className="text-sm font-mono truncate" style={{ color: "var(--text-primary)" }} title={agent.workspace}>
                              {agent.workspace}
                            </div>
                          </div>
                        </div>

                        {agent.dmPolicy && (
                          <div className="flex items-start gap-3">
                            <Shield className="w-4 h-4 mt-0.5" style={{ color: agent.color }} />
                            <div className="flex-1">
                              <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>Política DM</div>
                              <div className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                                {agent.dmPolicy}
                              </div>
                            </div>
                          </div>
                        )}

                        {(agent.allowAgents?.length ?? 0) > 0 && (
                          <div className="flex items-start gap-3">
                            <Users className="w-4 h-4 mt-0.5" style={{ color: agent.color }} />
                            <div className="flex-1">
                              <div className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>
                                Pode invocar sub-agentes ({agent.allowAgents?.length ?? 0})
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {(agent.allowAgentsDetails?.length ?? 0) > 0 ? (
                                  agent.allowAgentsDetails!.map((sub) => (
                                    <div key={sub.id} className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg"
                                      style={{ backgroundColor: `${sub.color}15`, border: `1px solid ${sub.color}40` }}>
                                      <span>{sub.emoji}</span>
                                      <span style={{ color: sub.color, fontWeight: 600 }}>{sub.name}</span>
                                    </div>
                                  ))
                                ) : (
                                  agent.allowAgents?.map((sub) => (
                                    <span key={sub} className="text-xs px-2 py-1 rounded"
                                      style={{ backgroundColor: `${agent.color}20`, color: agent.color, fontWeight: 500 }}>
                                      {sub}
                                    </span>
                                  ))
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        {agent.observacao && (
                          <div className="text-xs rounded-lg p-3" style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                            {agent.observacao}
                          </div>
                        )}

                        <div className="flex items-center justify-between pt-3 border-t border-[var(--border)]">
                          <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
                            <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                              Última atividade: {tempoDecorrido(agent.lastActivity)}
                            </span>
                          </div>
                          {agent.activeSessions > 0 && (
                            <span className="text-xs font-medium px-2 py-1 rounded"
                              style={{ backgroundColor: "var(--success)20", color: "var(--success)" }}>
                              {agent.activeSessions} sessão{agent.activeSessions !== 1 ? "ões" : ""} ativa{agent.activeSessions !== 1 ? "s" : ""}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))}

            {agentsFiltrados.length === 0 && (
              <div className="col-span-2 flex flex-col items-center justify-center py-24"
                style={{ color: "var(--text-muted)" }}>
                <Users style={{ width: 48, height: 48, marginBottom: 16, opacity: 0.4 }} />
                <p style={{ fontSize: 14 }}>Nenhum agente no filtro selecionado</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
