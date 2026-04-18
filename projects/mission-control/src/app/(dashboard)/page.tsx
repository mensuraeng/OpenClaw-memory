"use client";

import { useEffect, useState } from "react";
import { StatsCard } from "@/components/StatsCard";
import { ActivityFeed } from "@/components/ActivityFeed";
import { WeatherWidget } from "@/components/WeatherWidget";
import { Notepad } from "@/components/Notepad";
import { ExecutiveExceptionsCard } from "@/components/ExecutiveExceptionsCard";
import {
  Activity,
  CheckCircle,
  XCircle,
  Calendar,
  Circle,
  Bot,
  MessageSquare,
  Users,
  Gamepad2,
  Brain,
  Puzzle,
  Zap,
  Server,
  Terminal,
  AlertTriangle,
  ArrowUpRight,
  Landmark,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { buildAnalyticsInsights, buildOperationalAlerts, summarizePayablesRisk, type AnalyticsInsight, type OperationalAlert } from "@/lib/executive-alerts";

interface Stats {
  total: number;
  today: number;
  success: number;
  error: number;
  byType: Record<string, number>;
}

interface Agent {
  id: string;
  name: string;
  emoji: string;
  color: string;
  model: string;
  status: "online" | "offline";
  lastActivity?: string;
  botToken?: string;
  empresa?: string;
  modoExecucao?: "direto" | "planejado" | "monitoramento";
  validacaoPadrao?: "leve" | "padrao" | "forte";
  estadoBloqueio?: "livre" | "monitorar" | "bloqueado";
  sinais?: {
    riscoNivel: "baixo" | "medio" | "alto";
    pendenciasAbertas: number;
    decisoesPendentes: number;
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

interface ExecutiveAttentionItem {
  tipo: "sem_resposta" | "silencio_alto" | "decisao_acumulada" | "pendencia_critica";
  titulo: string;
  detalhe: string;
  severidade: "critico" | "atencao";
  empresa?: string;
  agente?: string;
  timestamp?: string;
}

interface TaskAttentionItem {
  taskId: string;
  title: string;
  targetAgent: string;
  status: string;
}

function getCompanyStatusWeight(status: CompanySummary["statusGeral"]) {
  if (status === "critico") return 3;
  if (status === "atencao") return 2;
  return 1;
}

function getCompanyAttentionScore(company: CompanySummary) {
  return (
    getCompanyStatusWeight(company.statusGeral) * 100 +
    company.riscoAlto * 25 +
    company.decisoes * 10 +
    company.pendencias * 4 +
    company.inertes * 3 -
    company.tracionando * 2
  );
}

function buildActivityDrilldownQuery(item: ExecutiveAttentionItem) {
  const params = new URLSearchParams();
  params.set("sort", "newest");
  params.set("limit", "20");

  if (item.agente) {
    params.set("agent", item.agente);
  }

  if (item.tipo === "sem_resposta") {
    params.set("status", "pending");
  }

  if (item.tipo === "pendencia_critica") {
    params.set("status", "error");
  }

  return `/activity?${params.toString()}`;
}

function buildSuggestedAction(item: ExecutiveAttentionItem) {
  switch (item.tipo) {
    case "sem_resposta":
      return "Revisar pendência e cobrar fechamento";
    case "silencio_alto":
      return "Checar agente e validar se perdeu tração";
    case "decisao_acumulada":
      return "Consolidar decisão pendente e destravar";
    case "pendencia_critica":
      return "Abrir detalhe e atacar causa raiz";
    default:
      return "Abrir drill-down";
  }
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats>({ total: 0, today: 0, success: 0, error: 0, byType: {} });
  const [agents, setAgents] = useState<Agent[]>([]);
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [executive, setExecutive] = useState<ExecutiveMemorySummary>({ pendingCritical: [], pendingWaitingAle: [], recentDecisions: [] });
  const [attention, setAttention] = useState<ExecutiveAttentionItem[]>([]);
  const [taskAttention, setTaskAttention] = useState<{ slaBreached: TaskAttentionItem[]; stale: TaskAttentionItem[]; blocked: TaskAttentionItem[]; unvalidated: TaskAttentionItem[]; orphaned: TaskAttentionItem[]; retryQueue: TaskAttentionItem[] }>({ slaBreached: [], stale: [], blocked: [], unvalidated: [], orphaned: [], retryQueue: [] });

  const rankedCompanies = [...companies].sort((a, b) => getCompanyAttentionScore(b) - getCompanyAttentionScore(a));
  const topCompany = rankedCompanies[0];
  const operationalAlerts: OperationalAlert[] = buildOperationalAlerts();
  const analyticsInsights: AnalyticsInsight[] = buildAnalyticsInsights();
  const payablesRisk = summarizePayablesRisk();

  useEffect(() => {
    Promise.all([
      fetch("/api/activities/stats").then(r => r.json()),
      fetch("/api/agents").then(r => r.json()),
      fetch("/api/tasks/attention").then(r => r.json()),
    ]).then(([actStats, agentsData, taskAttentionData]) => {
      setStats({
        total: actStats.total || 0,
        today: actStats.today || 0,
        success: actStats.byStatus?.success || 0,
        error: actStats.byStatus?.error || 0,
        byType: actStats.byType || {},
      });
      setAgents(agentsData.agents || []);
      setCompanies(agentsData.companies || []);
      setExecutive(agentsData.executive || { pendingCritical: [], pendingWaitingAle: [], recentDecisions: [] });
      setAttention(agentsData.attention || []);
      setTaskAttention(taskAttentionData || { slaBreached: [], stale: [], blocked: [], unvalidated: [], orphaned: [], retryQueue: [] });
    }).catch(console.error);
  }, []);

  return (
    <div className="p-4 md:p-8">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 
          className="text-2xl md:text-3xl font-bold mb-1"
          style={{ 
            fontFamily: 'var(--font-heading)',
            color: 'var(--text-primary)',
            letterSpacing: '-1.5px'
          }}
        >
          🦞 Mission Control
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Visão geral da atividade dos agentes MENSURA
        </p>
      </div>

      {/* Stats Grid + Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4 md:mb-6">
        {/* Stats */}
        <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatsCard
            title="Total de Atividades"
            value={stats.total.toLocaleString()}
            icon={<Activity className="w-5 h-5" />}
            iconColor="var(--info)"
          />
          <StatsCard
            title="Hoje"
            value={stats.today.toLocaleString()}
            icon={<Zap className="w-5 h-5" />}
            iconColor="var(--accent)"
          />
          <StatsCard
            title="Bem-sucedidas"
            value={stats.success.toLocaleString()}
            icon={<CheckCircle className="w-5 h-5" />}
            iconColor="var(--success)"
          />
          <StatsCard
            title="Erros"
            value={stats.error.toLocaleString()}
            icon={<XCircle className="w-5 h-5" />}
            iconColor="var(--error)"
          />
        </div>

        {/* Weather Widget */}
        <div className="lg:col-span-1">
          <WeatherWidget />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-6">
        <div className="xl:col-span-3 rounded-xl overflow-hidden"
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--border)',
          }}
        >
        <div 
          className="flex items-center justify-between px-5 py-4"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <div className="flex items-center gap-3">
            <div className="accent-line" />
            <h2 
              className="text-base font-semibold"
              style={{ 
                fontFamily: 'var(--font-heading)',
                color: 'var(--text-primary)'
              }}
            >
              <Users className="inline-block w-5 h-5 mr-2 mb-1" />
              Sistema Multi-Agente
            </h2>
          </div>
          <div className="flex gap-2">
            <Link
              href="/office"
              className="text-sm font-medium px-3 py-1.5 rounded-lg transition-all"
              style={{ 
                backgroundColor: 'var(--accent)',
                color: 'var(--text-primary)',
              }}
            >
              <Gamepad2 className="inline-block w-4 h-4 mr-1 mb-0.5" />
              Ver Office
            </Link>
            <Link
              href="/agents"
              className="text-sm font-medium"
              style={{ color: 'var(--accent)' }}
            >
              Ver tudo →
            </Link>
          </div>
        </div>
        <div className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="p-3 rounded-lg transition-all hover:scale-105"
                style={{
                  backgroundColor: 'var(--card-elevated)',
                  border: `2px solid ${agent.color}`,
                  cursor: 'pointer',
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="text-2xl">{agent.emoji}</div>
                  <Circle
                    className="w-2 h-2"
                    style={{
                      fill: agent.status === "online" ? "#4ade80" : "#6b7280",
                      color: agent.status === "online" ? "#4ade80" : "#6b7280",
                    }}
                  />
                </div>
                <div 
                  className="text-sm font-bold mb-1"
                  style={{ 
                    fontFamily: 'var(--font-heading)',
                    color: 'var(--text-primary)',
                  }}
                >
                  {agent.name}
                </div>
                <div 
                  className="text-xs truncate mb-2"
                  style={{ color: 'var(--text-muted)' }}
                  title={agent.model}
                >
                  <Bot className="inline-block w-3 h-3 mr-1" />
                  {agent.model.split('/').pop()}
                </div>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {agent.modoExecucao && (
                    <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: '#8b5cf620', color: '#8b5cf6', border: '1px solid #8b5cf640' }}>
                      {agent.modoExecucao === 'direto' ? 'Direto' : agent.modoExecucao === 'monitoramento' ? 'Monitor' : 'Planejado'}
                    </span>
                  )}
                  {agent.validacaoPadrao && (
                    <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: '#06b6d420', color: '#06b6d4', border: '1px solid #06b6d440' }}>
                      {agent.validacaoPadrao === 'forte' ? 'Validação forte' : agent.validacaoPadrao === 'leve' ? 'Validação leve' : 'Validação padrão'}
                    </span>
                  )}
                  {agent.estadoBloqueio && agent.estadoBloqueio !== 'livre' && (
                    <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: agent.estadoBloqueio === 'bloqueado' ? '#ef444420' : '#f59e0b20', color: agent.estadoBloqueio === 'bloqueado' ? '#ef4444' : '#f59e0b', border: `1px solid ${agent.estadoBloqueio === 'bloqueado' ? '#ef444440' : '#f59e0b40'}` }}>
                      {agent.estadoBloqueio === 'bloqueado' ? 'Bloqueado' : 'Monitorar'}
                    </span>
                  )}
                </div>
                {agent.botToken && (
                  <div 
                    className="text-xs mt-1 flex items-center gap-1"
                    style={{ color: '#0088cc' }}
                  >
                    <MessageSquare className="w-3 h-3" />
                    Connected
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        </div>

        <ExecutiveExceptionsCard executive={executive} />
      </div>

      <div className="mb-6 grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 rounded-xl p-5" style={{ backgroundColor: 'var(--card)', border: '1px solid #ef444440' }}>
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <div className="text-xs font-semibold mb-2" style={{ color: '#ef4444' }}>RADAR EXECUTIVO IMEDIATO</div>
              <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>O que merece atenção agora</div>
            </div>
            <AlertTriangle className="w-5 h-5" style={{ color: '#ef4444' }} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {operationalAlerts.map((item) => {
              const color = item.severidade === 'critico' ? '#ef4444' : item.severidade === 'atencao' ? '#f59e0b' : '#60a5fa';
              return (
                <div key={item.id} className="rounded-lg p-4" style={{ backgroundColor: `${color}10`, border: `1px solid ${color}30` }}>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: `${color}20`, color, border: `1px solid ${color}30` }}>{item.categoria}</span>
                    <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.empresa}</span>
                  </div>
                  <div className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>{item.titulo}</div>
                  <div className="text-xs mb-2" style={{ color: 'var(--text-secondary)' }}>{item.detalhe}</div>
                  <div className="flex items-center justify-between gap-3 text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    <span>{item.prazoLabel || item.origem}</span>
                    <span style={{ color }}>{item.acao}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <div className="text-xs font-semibold mb-2" style={{ color: 'var(--accent)' }}>PRESSÃO FINANCEIRA</div>
              <div className="text-xl font-bold" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>Contas e triagem</div>
            </div>
            <Landmark className="w-5 h-5" style={{ color: 'var(--accent)' }} />
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}>
              <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Pendentes</div>
              <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{payablesRisk.pendentes}</div>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}>
              <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Valor conhecido</div>
              <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>R$ {payablesRisk.valorConhecido.toFixed(2)}</div>
            </div>
          </div>
          <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{payablesRisk.leitura}</div>
        </div>
      </div>

      {(taskAttention.slaBreached.length > 0 || taskAttention.stale.length > 0 || taskAttention.blocked.length > 0 || taskAttention.unvalidated.length > 0 || taskAttention.orphaned.length > 0 || taskAttention.retryQueue.length > 0) && (
        <div className="mb-6 rounded-xl p-5" style={{ backgroundColor: 'var(--card)', border: '1px solid #f59e0b40' }}>
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <div className="text-xs font-semibold mb-2" style={{ color: '#f59e0b' }}>EXCEÇÕES DE TASK TRACKING</div>
              <div className="text-2xl font-bold" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>Delegações que merecem atenção</div>
            </div>
            <Link href="/tasks" className="text-sm font-medium" style={{ color: 'var(--accent)' }}>Abrir tasks →</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
            {[
              { label: 'SLA vencido', items: taskAttention.slaBreached, color: '#ef4444' },
              { label: 'Paradas', items: taskAttention.stale, color: '#f59e0b' },
              { label: 'Bloqueadas', items: taskAttention.blocked, color: '#f97316' },
              { label: 'Sem validação', items: taskAttention.unvalidated, color: '#a855f7' },
              { label: 'Órfãs', items: taskAttention.orphaned, color: '#dc2626' },
              { label: 'Em retry', items: taskAttention.retryQueue, color: '#2563eb' },
            ].map((group) => (
              <div key={group.label} className="rounded-lg p-4" style={{ backgroundColor: `${group.color}10`, border: `1px solid ${group.color}30` }}>
                <div className="text-xs font-semibold mb-3" style={{ color: group.color }}>{group.label}</div>
                <div className="space-y-2">
                  {group.items.slice(0, 4).map((item) => (
                    <Link key={item.taskId} href={`/tasks/${item.taskId}`} className="block text-sm" style={{ color: 'var(--text-primary)' }}>
                      <strong>{item.title}</strong>
                      <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{item.targetAgent} · {item.status}</div>
                    </Link>
                  ))}
                  {group.items.length === 0 && <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Nenhuma agora.</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {topCompany && (
        <div className="mb-6 rounded-xl p-5" style={{ backgroundColor: 'var(--card)', border: `1px solid ${topCompany.statusGeral === 'critico' ? '#ef444440' : topCompany.statusGeral === 'atencao' ? '#f59e0b40' : '#22c55e40'}` }}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="text-xs font-semibold mb-2" style={{ color: topCompany.statusGeral === 'critico' ? '#ef4444' : topCompany.statusGeral === 'atencao' ? '#f59e0b' : '#22c55e' }}>
                EMPRESA MAIS CRÍTICA AGORA
              </div>
              <div className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
                {topCompany.empresa}
              </div>
              <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{topCompany.leitura}</div>
            </div>
            <div className="grid grid-cols-4 gap-3 min-w-full md:min-w-[360px]">
              <div className="rounded-lg p-3 text-center" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Risco</div><div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{topCompany.riscoAlto}</div></div>
              <div className="rounded-lg p-3 text-center" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Pend.</div><div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{topCompany.pendencias}</div></div>
              <div className="rounded-lg p-3 text-center" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Dec.</div><div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{topCompany.decisoes}</div></div>
              <div className="rounded-lg p-3 text-center" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Inertes</div><div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{topCompany.inertes}</div></div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-6">
        <div className="xl:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
        {companies.map((company) => {
          const color = company.statusGeral === 'critico' ? '#ef4444' : company.statusGeral === 'atencao' ? '#f59e0b' : '#22c55e';
          return (
            <button key={company.empresa} type="button" onClick={() => router.push(`/agents?empresa=${encodeURIComponent(company.empresa)}`)} className="rounded-xl p-4 text-left transition-all hover:scale-[1.01]" style={{ backgroundColor: 'var(--card)', border: `1px solid ${color}40`, cursor: 'pointer' }}>
              <div className="flex items-center justify-between mb-2">
                <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>{company.empresa}</div>
                <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: `${color}20`, color, border: `1px solid ${color}40` }}>
                  {company.statusGeral}
                </span>
              </div>
              <div className="text-xs mb-3" style={{ color: 'var(--text-secondary)' }}>{company.leitura}</div>
              <div className="grid grid-cols-4 gap-2 text-center">
                <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Agentes</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{company.agentes}</div></div>
                <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Risco</div><div className="font-bold" style={{ color }}>{company.riscoAlto}</div></div>
                <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Pend.</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{company.pendencias}</div></div>
                <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Dec.</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{company.decisoes}</div></div>
              </div>
              <div className="text-[11px] font-medium mt-3" style={{ color }}>Abrir agentes da empresa →</div>
            </button>
          );
        })}
        </div>

        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <div className="px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
            <h2 className="text-base font-semibold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
              Ranking de atenção
            </h2>
          </div>
          <div className="p-3 space-y-2">
            {rankedCompanies.slice(0, 5).map((company, index) => {
              const color = company.statusGeral === 'critico' ? '#ef4444' : company.statusGeral === 'atencao' ? '#f59e0b' : '#22c55e';
              return (
                <div key={company.empresa} className="rounded-lg p-3" style={{ backgroundColor: 'var(--surface-elevated)', border: `1px solid ${color}30` }}>
                  <div className="flex items-center justify-between gap-3 mb-1">
                    <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{index + 1}. {company.empresa}</div>
                    <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: `${color}20`, color, border: `1px solid ${color}30` }}>{company.statusGeral}</span>
                  </div>
                  <div className="text-xs mb-2" style={{ color: 'var(--text-secondary)' }}>{company.leitura}</div>
                  <div className="flex items-center gap-3 text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    <span>Risco {company.riscoAlto}</span>
                    <span>Pend. {company.pendencias}</span>
                    <span>Dec. {company.decisoes}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2 rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <div className="px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
            <h2 className="text-base font-semibold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
              Sinais explícitos de exceção
            </h2>
          </div>
          <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          {attention.length > 0 ? attention.map((item, index) => {
            const color = item.severidade === 'critico' ? '#ef4444' : '#f59e0b';
            return (
              <button
                key={`${item.tipo}-${index}`}
                type="button"
                onClick={() => router.push(buildActivityDrilldownQuery(item))}
                className="rounded-lg p-3 text-left transition-all hover:scale-[1.01]"
                style={{ backgroundColor: `${color}10`, border: `1px solid ${color}30`, cursor: 'pointer' }}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: `${color}20`, color, border: `1px solid ${color}30` }}>{item.severidade}</span>
                  {item.empresa && <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.empresa}</span>}
                </div>
                <div className="text-sm font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>{item.titulo}</div>
                <div className="text-xs mb-2" style={{ color: 'var(--text-secondary)' }}>{item.detalhe}</div>
                <div className="text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>{buildSuggestedAction(item)}</div>
                <div className="text-[11px] font-medium mt-1" style={{ color: color }}>Abrir drill-down →</div>
              </button>
            );
          }) : (
            <div className="text-sm" style={{ color: 'var(--text-muted)' }}>Nenhum sinal explícito destacado agora.</div>
          )}
          </div>
        </div>

        <div className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid var(--border)' }}>
            <h2 className="text-base font-semibold" style={{ fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
              Leitura web da semana
            </h2>
            <ArrowUpRight className="w-4 h-4" style={{ color: 'var(--accent)' }} />
          </div>
          <div className="p-4 space-y-3">
            {analyticsInsights.map((item) => (
              <div key={item.empresa} className="rounded-lg p-3" style={{ backgroundColor: 'var(--surface-elevated)', border: '1px solid var(--border)' }}>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="font-semibold" style={{ color: 'var(--text-primary)' }}>{item.empresa}</div>
                  <span className="text-[10px] px-2 py-1 rounded-full" style={{ backgroundColor: item.bouncePct >= 60 ? '#ef444420' : '#22c55e20', color: item.bouncePct >= 60 ? '#ef4444' : '#22c55e', border: `1px solid ${item.bouncePct >= 60 ? '#ef444430' : '#22c55e30'}` }}>
                    Bounce {item.bouncePct.toFixed(1)}%
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center mb-2">
                  <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Sessões</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{item.sessoes}</div></div>
                  <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Usuários</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{item.usuarios}</div></div>
                  <div><div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Novos</div><div className="font-bold" style={{ color: 'var(--text-primary)' }}>{item.novos}</div></div>
                </div>
                <div className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>{item.leitura}</div>
                <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Origem: {item.principalOrigem} • Página: {item.paginaTop}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Activity Feed */}
        <div 
          className="lg:col-span-2 rounded-xl overflow-hidden"
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--border)',
          }}
        >
          <div 
            className="flex items-center justify-between px-5 py-4"
            style={{ borderBottom: '1px solid var(--border)' }}
          >
            <div className="flex items-center gap-3">
              <div className="accent-line" />
              <h2 
                className="text-base font-semibold"
                style={{ 
                  fontFamily: 'var(--font-heading)',
                  color: 'var(--text-primary)'
                }}
              >
                Atividade Recente
              </h2>
            </div>
            <a
              href="/activity"
              className="text-sm font-medium"
              style={{ color: 'var(--accent)' }}
            >
              Ver tudo →
            </a>
          </div>
          <div className="p-0">
            <ActivityFeed limit={5} />
          </div>
        </div>

        {/* Acesso Rápido */}
        <div 
          className="rounded-xl overflow-hidden"
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--border)',
          }}
        >
          <div 
            className="flex items-center justify-between px-5 py-4"
            style={{ borderBottom: '1px solid var(--border)' }}
          >
            <div className="flex items-center gap-3">
              <div className="accent-line" />
              <h2 
                className="text-base font-semibold"
                style={{ 
                  fontFamily: 'var(--font-heading)',
                  color: 'var(--text-primary)'
                }}
              >
                Acesso Rápido
              </h2>
            </div>
          </div>
          <div className="p-4 grid grid-cols-2 gap-2">
            {[
              { href: "/cron", icon: Calendar, label: "Tarefas Agendadas", color: "#a78bfa" },
              { href: "/actions", icon: Zap, label: "Ações Rápidas", color: "var(--accent)" },
              { href: "/system", icon: Server, label: "Sistema", color: "var(--success)" },
              { href: "/logs", icon: Terminal, label: "Logs ao Vivo", color: "#60a5fa" },
              { href: "/memory", icon: Brain, label: "Memória", color: "#f59e0b" },
              { href: "/skills", icon: Puzzle, label: "Skills", color: "#4ade80" },
            ].map(({ href, icon: Icon, label, color }) => (
              <Link
                key={href}
                href={href}
                className="p-3 rounded-lg transition-all hover:scale-[1.02]"
                style={{ backgroundColor: 'var(--card-elevated)', border: '1px solid var(--border)' }}
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4" style={{ color }} />
                  <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{label}</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Notepad */}
          <div style={{ margin: "1rem", marginTop: "0.5rem" }}>
            <Notepad />
          </div>
        </div>
      </div>
    </div>
  );
}
