"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Archive, CheckSquare, Database, FileText, GitBranch, ShieldCheck, Workflow } from "lucide-react";
import { PageHeader, PageShell, SectionCard } from "@/components/PageShell";
import { MetricCard } from "@/components/TenacitOS/MetricCard";
import { fetchJson } from "@/lib/fetch";

type Tone = "ok" | "attention" | "risk";

type Project = {
  id: string;
  name: string;
  domain: string;
  sourcePath: string;
  status: string;
  priority: "critical" | "high" | "medium" | "low";
  risk: Tone;
  ownerAgent: string;
  summary: string;
  nextStep: string;
  lastMovement: string | null;
  metrics: { openTasks: number; blockedTasks: number; documents: number; evidences: number; decisions: number };
  tasks: Array<{ taskId: string; title: string; status: string; targetAgent: string; riskLevel: string; updatedAt: string }>;
  documents: Array<{ id: string; title: string; path: string; category: string; status: string; sensitivity: string; modified: string | null }>;
  evidences: Array<{ id: string; title: string; path: string; kind: string; modified: string | null }>;
  decisions: Array<{ title: string; path: string; line: number }>;
};

type Graph = {
  generatedAt: string;
  roots: { secondBrain: string; workspace: string; runtime: string };
  metrics: { projects: number; documents: number; openTasksLinked: number; evidences: number; decisionsLinked: number; risks: number };
  projects: Project[];
  guardrails: string[];
};

const priorityLabel = { critical: "crítica", high: "alta", medium: "média", low: "baixa" };

function toneColor(tone: Tone | string) {
  if (tone === "risk") return "negative" as const;
  if (tone === "attention") return "warning" as const;
  return "positive" as const;
}

function pillStyle(tone: "positive" | "warning" | "negative" | "secondary") {
  const color = {
    positive: "var(--positive)",
    warning: "var(--warning)",
    negative: "var(--negative)",
    secondary: "var(--text-secondary)",
  }[tone];
  return { color, border: `1px solid ${color}` };
}

function Pill({ children, tone = "secondary" }: { children: React.ReactNode; tone?: "positive" | "warning" | "negative" | "secondary" }) {
  return <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={pillStyle(tone)}>{children}</span>;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString("pt-BR") : "—";
}

export default function ProjectsPage() {
  const [graph, setGraph] = useState<Graph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("all");

  useEffect(() => {
    fetchJson<Graph>("/api/executive-graph")
      .then(setGraph)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  const domains = useMemo(() => ["all", ...Array.from(new Set((graph?.projects || []).map((project) => project.domain))).sort()], [graph]);
  const projects = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (graph?.projects || []).filter((project) => {
      if (domain !== "all" && project.domain !== domain) return false;
      if (!q) return true;
      return `${project.name} ${project.domain} ${project.summary} ${project.nextStep} ${project.ownerAgent}`.toLowerCase().includes(q);
    });
  }, [graph, query, domain]);

  if (error) {
    return <PageShell><PageHeader title="Projects Executive Graph" subtitle="Falha ao carregar grafo operacional" icon="🧭 " /><SectionCard title="Erro" icon={<AlertTriangle className="h-4 w-4" />}><p style={{ color: "var(--negative)" }}>{error}</p></SectionCard></PageShell>;
  }

  if (!graph) {
    return <PageShell><PageHeader title="Projects Executive Graph" subtitle="Carregando projetos, tarefas, documentos e evidências..." icon="🧭 " /></PageShell>;
  }

  return (
    <PageShell>
      <PageHeader
        title="Projects Executive Graph"
        subtitle="Cockpit read-only: projetos conectados a tarefas, documentos, decisões e evidências."
        icon="🧭 "
        actions={<div className="flex gap-2"><Link href="/docs" className="text-sm underline" style={{ color: "var(--text-secondary)" }}>Docs</Link><Link href="/openclaw" className="text-sm underline" style={{ color: "var(--text-secondary)" }}>OpenClaw</Link></div>}
      />

      <SectionCard title="Especificação v1" icon={<ShieldCheck className="h-4 w-4" />} right={<Pill tone="warning">read-only protegido</Pill>}>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          <div><strong style={{ color: "var(--text-primary)" }}>Fonte</strong><p>2nd-brain + runtime + workspace docs.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Objetivo</strong><p>Responder o que está ativo, parado, documentado e evidenciado.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Sem escrita</strong><p>Não altera tarefa, arquivo, cron, cliente ou sistema externo.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Critério 10/10</strong><p>Projeto → tarefa → agente → docs → evidência → decisão.</p></div>
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-6 my-5">
        <MetricCard icon={Workflow} value={graph.metrics.projects} label="Projetos" change="fontes canônicas" changeColor="positive" />
        <MetricCard icon={CheckSquare} value={graph.metrics.openTasksLinked} label="Tarefas ligadas" change="abertas" changeColor={graph.metrics.openTasksLinked ? "warning" : "positive"} />
        <MetricCard icon={FileText} value={graph.metrics.documents} label="Docs indexados" change="biblioteca" changeColor="positive" />
        <MetricCard icon={Archive} value={graph.metrics.evidences} label="Evidências" change="runtime" changeColor="positive" />
        <MetricCard icon={GitBranch} value={graph.metrics.decisionsLinked} label="Decisões" change="ligadas" changeColor="positive" />
        <MetricCard icon={AlertTriangle} value={graph.metrics.risks} label="Riscos" change="atenção" changeColor={graph.metrics.risks ? "negative" : "positive"} />
      </div>

      <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-4">
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filtrar por projeto, agente, próximo passo..." className="rounded-lg px-4 py-3 text-sm outline-none md:col-span-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
        <select value={domain} onChange={(event) => setDomain(event.target.value)} className="rounded-lg px-4 py-3 text-sm outline-none" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
          {domains.map((item) => <option key={item} value={item}>{item === "all" ? "Todos os domínios" : item}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        {projects.map((project) => (
          <SectionCard key={project.id} title={project.name} icon={<Database className="h-4 w-4" />} right={<div className="flex gap-2"><Pill tone={toneColor(project.risk)}>{project.risk}</Pill><Pill>{priorityLabel[project.priority]}</Pill></div>}>
            <div className="space-y-4 text-sm">
              <div className="flex flex-wrap gap-2">
                <Pill>{project.domain}</Pill><Pill>{project.ownerAgent}</Pill><Pill>{project.status}</Pill>
              </div>
              <p style={{ color: "var(--text-secondary)" }}>{project.summary}</p>
              <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}>
                <strong style={{ color: "var(--text-primary)" }}>Próximo passo</strong>
                <p className="mt-1" style={{ color: "var(--text-secondary)" }}>{project.nextStep}</p>
              </div>
              <div className="grid grid-cols-5 gap-2 text-center">
                {[["Tasks", project.metrics.openTasks], ["Bloq.", project.metrics.blockedTasks], ["Docs", project.metrics.documents], ["Evid.", project.metrics.evidences], ["Dec.", project.metrics.decisions]].map(([label, value]) => (
                  <div key={String(label)} className="rounded-lg p-2" style={{ backgroundColor: "var(--surface)" }}><div className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>{value}</div><div className="text-xs" style={{ color: "var(--text-muted)" }}>{label}</div></div>
                ))}
              </div>
              <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                <div>
                  <h3 className="mb-2 font-semibold" style={{ color: "var(--text-primary)" }}>Tarefas</h3>
                  <div className="space-y-2">
                    {project.tasks.slice(0, 3).map((task) => <Link key={task.taskId} href={`/tasks/${task.taskId}`} className="block rounded-lg p-2" style={{ backgroundColor: "var(--surface)", color: "var(--text-secondary)" }}>{task.title}<br /><span className="text-xs">{task.status} · {task.targetAgent}</span></Link>)}
                    {project.tasks.length === 0 ? <p style={{ color: "var(--text-muted)" }}>Sem tarefa vinculada.</p> : null}
                  </div>
                </div>
                <div>
                  <h3 className="mb-2 font-semibold" style={{ color: "var(--text-primary)" }}>Docs / evidências</h3>
                  <div className="space-y-2">
                    {[...project.documents.slice(0, 2).map((doc) => ({ key: doc.id, title: doc.title, meta: `${doc.category} · ${doc.sensitivity}` })), ...project.evidences.slice(0, 2).map((evidence) => ({ key: evidence.id, title: evidence.title, meta: `runtime · ${evidence.kind}` }))].map((item) => <div key={item.key} className="rounded-lg p-2" style={{ backgroundColor: "var(--surface)", color: "var(--text-secondary)" }}>{item.title}<br /><span className="text-xs">{item.meta}</span></div>)}
                    {project.documents.length + project.evidences.length === 0 ? <p style={{ color: "var(--text-muted)" }}>Sem doc/evidência vinculada.</p> : null}
                  </div>
                </div>
              </div>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>Fonte: {project.sourcePath} · última movimentação {formatDate(project.lastMovement)}</p>
            </div>
          </SectionCard>
        ))}
      </div>

      <div className="mt-5 text-xs" style={{ color: "var(--text-muted)" }}>Atualizado em {formatDate(graph.generatedAt)} · {graph.guardrails.join(" · ")}</div>
    </PageShell>
  );
}
