"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Brain, CheckCircle2, Database, FileSearch, GitBranch, LockKeyhole, RefreshCw, Search, ShieldCheck, Workflow } from "lucide-react";
import { PageHeader, PageShell, SectionCard } from "@/components/PageShell";
import { MetricCard } from "@/components/TenacitOS/MetricCard";
import { fetchJson } from "@/lib/fetch";

type ValidatorIssue = {
  id: string;
  severity: "ok" | "attention" | "risk";
  title: string;
  detail: string;
  path?: string;
};

type MemoryControl = {
  generatedAt: string;
  root: string;
  score: number;
  tone: "ok" | "attention" | "risk";
  routeRecommendation: { preferred: string; alternative: string; guardrail: string };
  metrics: Record<string, number>;
  recent: { decisions: string[]; lessons: string[]; working: string[] };
  validators: ValidatorIssue[];
  paths: Array<{ key: string; path: string; exists: boolean; size: number; modified: string | null }>;
};

type SearchResult = {
  title: string;
  path: string;
  line: number;
  score: number;
  snippet: string;
  authority: string;
};

function toneColor(tone: string) {
  if (["ok", "healthy", "success"].includes(tone)) return "positive" as const;
  if (["attention", "pending", "warning"].includes(tone)) return "warning" as const;
  if (["risk", "fail", "blocked", "critical"].includes(tone)) return "negative" as const;
  return "secondary" as const;
}

function Pill({ children, tone = "secondary" }: { children: React.ReactNode; tone?: "positive" | "warning" | "negative" | "secondary" }) {
  const colors = {
    positive: "var(--positive)",
    warning: "var(--warning)",
    negative: "var(--negative)",
    secondary: "var(--text-secondary)",
  };
  return <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={{ color: colors[tone], border: `1px solid ${colors[tone]}` }}>{children}</span>;
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("pt-BR");
}

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export default function OpenClawMemoryPage() {
  const [data, setData] = useState<MemoryControl | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetchJson<MemoryControl>("/api/openclaw-memory")
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 3) {
      setResults([]);
      return;
    }
    const t = setTimeout(() => {
      setSearching(true);
      fetchJson<{ results: SearchResult[] }>(`/api/openclaw-memory?q=${encodeURIComponent(q)}`)
        .then((payload) => setResults(payload.results || []))
        .catch(() => setResults([]))
        .finally(() => setSearching(false));
    }, 250);
    return () => clearTimeout(t);
  }, [query]);

  const riskCount = useMemo(() => data?.validators.filter((v) => v.severity === "risk").length || 0, [data]);
  const attentionCount = useMemo(() => data?.validators.filter((v) => v.severity === "attention").length || 0, [data]);

  if (error) {
    return (
      <PageShell>
        <PageHeader title="OpenClaw Memory Control" subtitle="Falha ao carregar memória operacional" icon="🧠 " />
        <SectionCard title="Erro" icon={<AlertTriangle className="h-4 w-4" />}>
          <p style={{ color: "var(--negative)" }}>{error}</p>
        </SectionCard>
      </PageShell>
    );
  }

  if (!data) {
    return (
      <PageShell>
        <PageHeader title="OpenClaw Memory Control" subtitle="Carregando 2nd-brain, validadores e busca..." icon="🧠 " />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title="OpenClaw Memory Control"
        subtitle="Cockpit read-only do 2nd-brain: decisões, pendências, validação de qualidade e busca com fonte."
        icon="🧠 "
        actions={<Link href="/ops" className="text-sm underline" style={{ color: "var(--text-secondary)" }}>Ops 360</Link>}
      />

      <SectionCard title="Decisão de arquitetura" icon={<ShieldCheck className="h-4 w-4" />} right={<Pill tone="warning">read-only protegido</Pill>}>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3 text-sm" style={{ color: "var(--text-secondary)" }}>
          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
            <strong style={{ color: "var(--text-primary)" }}>Fonte de verdade</strong>
            <p className="mt-1">GitHub + <code>{data.root}</code></p>
          </div>
          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
            <strong style={{ color: "var(--text-primary)" }}>Rota recomendada</strong>
            <p className="mt-1">{data.routeRecommendation.preferred}</p>
          </div>
          <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
            <strong style={{ color: "var(--text-primary)" }}>Guardrail</strong>
            <p className="mt-1">{data.routeRecommendation.guardrail}</p>
          </div>
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4 my-5">
        <MetricCard icon={Brain} value={`${data.score}/10`} label="Qualidade da memória" change={`${riskCount} risco / ${attentionCount} atenção`} changeColor={toneColor(data.tone)} />
        <MetricCard icon={Workflow} value={data.metrics.workingItems} label="WORKING aberto" change={`${data.metrics.pendingItems} pendências`} changeColor="warning" />
        <MetricCard icon={GitBranch} value={data.metrics.decisions} label="Decisões mapeadas" change={`${data.metrics.lessons} lições`} changeColor="positive" />
        <MetricCard icon={Database} value={data.metrics.agentMemoryFiles} label="Arquivos agentes" change={`${data.metrics.inboxCaptures} capturas inbox`} changeColor={data.metrics.inboxCaptures ? "warning" : "positive"} />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <SectionCard title="Validadores de qualidade" icon={<CheckCircle2 className="h-4 w-4" />} right={<Pill tone={riskCount ? "negative" : attentionCount ? "warning" : "positive"}>{riskCount ? "risco" : attentionCount ? "atenção" : "limpo"}</Pill>}>
          <div className="space-y-3">
            {data.validators.map((issue) => (
              <div key={issue.id} className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}>
                <div className="flex items-center justify-between gap-3">
                  <strong style={{ color: "var(--text-primary)" }}>{issue.title}</strong>
                  <Pill tone={toneColor(issue.severity)}>{issue.severity}</Pill>
                </div>
                <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>{issue.detail}</p>
                {issue.path ? <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>{issue.path}</p> : null}
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Recentes canônicos" icon={<FileSearch className="h-4 w-4" />}>
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="mb-2 font-semibold" style={{ color: "var(--text-primary)" }}>Decisões</h3>
              <ul className="space-y-2" style={{ color: "var(--text-secondary)" }}>{data.recent.decisions.map((item) => <li key={item}>• {item}</li>)}</ul>
            </div>
            <div>
              <h3 className="mb-2 font-semibold" style={{ color: "var(--text-primary)" }}>WORKING</h3>
              <ul className="space-y-2" style={{ color: "var(--text-secondary)" }}>{data.recent.working.map((item) => <li key={item}>• {item}</li>)}</ul>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Entradas canônicas" icon={<LockKeyhole className="h-4 w-4" />}>
          <div className="space-y-2 text-sm">
            {data.paths.map((item) => (
              <div key={item.key} className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)", color: "var(--text-secondary)" }}>
                <div className="flex items-center justify-between gap-3">
                  <strong style={{ color: "var(--text-primary)" }}>{item.key}</strong>
                  <Pill tone={item.exists ? "positive" : "negative"}>{item.exists ? "existe" : "ausente"}</Pill>
                </div>
                <p className="mt-1 truncate">{item.path}</p>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>{formatBytes(item.size)} · {formatDate(item.modified)}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Busca no 2nd-brain" icon={<Search className="h-4 w-4" />} right={<Pill tone="secondary">fonte + linha</Pill>}>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Busque por projeto, decisão, pessoa, risco ou regra..."
          className="w-full rounded-lg px-4 py-3 text-sm outline-none"
          style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
        />
        <div className="mt-4 space-y-3">
          {searching ? <p style={{ color: "var(--text-secondary)" }}>Buscando...</p> : null}
          {results.map((result) => (
            <div key={`${result.path}:${result.line}:${result.score}`} className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <strong style={{ color: "var(--text-primary)" }}>{result.title}</strong>
                <div className="flex gap-2"><Pill>{result.authority}</Pill><Pill tone="secondary">score {result.score}</Pill></div>
              </div>
              <pre className="mt-2 whitespace-pre-wrap text-xs" style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono, monospace)" }}>{result.snippet}</pre>
              <p className="mt-2 text-xs" style={{ color: "var(--text-muted)" }}>{result.path}#{result.line}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
          <RefreshCw className="h-3.5 w-3.5" /> Atualizado em {new Date(data.generatedAt).toLocaleString("pt-BR")}
        </div>
      </SectionCard>
    </PageShell>
  );
}
