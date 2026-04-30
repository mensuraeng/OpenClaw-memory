"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, BookOpen, Building2, FileText, FolderOpen, ShieldCheck } from "lucide-react";
import { PageHeader, PageShell, SectionCard } from "@/components/PageShell";
import { MetricCard } from "@/components/TenacitOS/MetricCard";
import { fetchJson } from "@/lib/fetch";

type DocumentItem = {
  id: string;
  title: string;
  path: string;
  source: "2nd-brain" | "workspace";
  category: string;
  company: string;
  projectId?: string;
  status: string;
  sensitivity: string;
  modified: string | null;
  size: number;
};

type DocsPayload = {
  generatedAt: string;
  roots: { secondBrain: string; workspace: string; runtime: string };
  documents: DocumentItem[];
  guardrails: string[];
};

function Pill({ children, tone = "secondary" }: { children: React.ReactNode; tone?: "positive" | "warning" | "negative" | "secondary" }) {
  const color = { positive: "var(--positive)", warning: "var(--warning)", negative: "var(--negative)", secondary: "var(--text-secondary)" }[tone];
  return <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={{ color, border: `1px solid ${color}` }}>{children}</span>;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString("pt-BR") : "—";
}

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function sensitivityTone(value: string) {
  if (value === "sensível") return "warning" as const;
  if (value === "interno") return "secondary" as const;
  return "positive" as const;
}

export default function DocsPage() {
  const [payload, setPayload] = useState<DocsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [company, setCompany] = useState("all");

  useEffect(() => {
    fetchJson<DocsPayload>("/api/executive-graph?mode=documents")
      .then(setPayload)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  const categories = useMemo(() => ["all", ...Array.from(new Set((payload?.documents || []).map((doc) => doc.category))).sort()], [payload]);
  const companies = useMemo(() => ["all", ...Array.from(new Set((payload?.documents || []).map((doc) => doc.company))).sort()], [payload]);
  const documents = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (payload?.documents || []).filter((doc) => {
      if (category !== "all" && doc.category !== category) return false;
      if (company !== "all" && doc.company !== company) return false;
      if (!q) return true;
      return `${doc.title} ${doc.path} ${doc.category} ${doc.company} ${doc.status}`.toLowerCase().includes(q);
    });
  }, [payload, query, category, company]);

  const sensitiveCount = useMemo(() => (payload?.documents || []).filter((doc) => doc.sensitivity === "sensível").length, [payload]);
  const institutionalCount = useMemo(() => (payload?.documents || []).filter((doc) => doc.category === "Institucional").length, [payload]);

  if (error) {
    return <PageShell><PageHeader title="Docs Executive Library" subtitle="Falha ao carregar biblioteca" icon="📚 " /><SectionCard title="Erro" icon={<AlertTriangle className="h-4 w-4" />}><p style={{ color: "var(--negative)" }}>{error}</p></SectionCard></PageShell>;
  }

  if (!payload) {
    return <PageShell><PageHeader title="Docs Executive Library" subtitle="Indexando documentos institucionais, PRDs, runbooks e evidências..." icon="📚 " /></PageShell>;
  }

  return (
    <PageShell>
      <PageHeader
        title="Docs Executive Library"
        subtitle="Biblioteca read-only de documentos por empresa, categoria, projeto, status e sensibilidade."
        icon="📚 "
        actions={<Link href="/projects" className="text-sm underline" style={{ color: "var(--text-secondary)" }}>Projects Graph</Link>}
      />

      <SectionCard title="Especificação v1" icon={<ShieldCheck className="h-4 w-4" />} right={<Pill tone="warning">sem editor / sem delete</Pill>}>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          <div><strong style={{ color: "var(--text-primary)" }}>Categorias</strong><p>PRD, ADR, runbook, comercial, fiscal, institucional e evidência.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Empresas</strong><p>MENSURA, MIA, PCS e trilhas transversais.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Rastreio</strong><p>Mostra fonte, status, tamanho, data e sensibilidade.</p></div>
          <div><strong style={{ color: "var(--text-primary)" }}>Guardrail</strong><p>Não expõe conteúdo sensível; só metadados e caminhos internos.</p></div>
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5 my-5">
        <MetricCard icon={FileText} value={payload.documents.length} label="Documentos" change="indexados" changeColor="positive" />
        <MetricCard icon={BookOpen} value={categories.length - 1} label="Categorias" change="classificação" changeColor="positive" />
        <MetricCard icon={Building2} value={companies.length - 1} label="Empresas/domínios" change="escopo" changeColor="positive" />
        <MetricCard icon={ShieldCheck} value={sensitiveCount} label="Sensíveis" change="metadados apenas" changeColor={sensitiveCount ? "warning" : "positive"} />
        <MetricCard icon={FolderOpen} value={institutionalCount} label="Institucionais" change="MIA/MENSURA/PCS" changeColor="positive" />
      </div>

      <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-5">
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por documento, caminho, status..." className="rounded-lg px-4 py-3 text-sm outline-none md:col-span-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
        <select value={category} onChange={(event) => setCategory(event.target.value)} className="rounded-lg px-4 py-3 text-sm outline-none" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
          {categories.map((item) => <option key={item} value={item}>{item === "all" ? "Todas categorias" : item}</option>)}
        </select>
        <select value={company} onChange={(event) => setCompany(event.target.value)} className="rounded-lg px-4 py-3 text-sm outline-none" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
          {companies.map((item) => <option key={item} value={item}>{item === "all" ? "Todas empresas" : item}</option>)}
        </select>
      </div>

      <SectionCard title="Documentos" icon={<FileText className="h-4 w-4" />} right={<Pill>{documents.length} filtrados</Pill>}>
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="rounded-lg p-4" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 className="font-semibold" style={{ color: "var(--text-primary)" }}>{doc.title}</h3>
                  <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>{doc.path}</p>
                </div>
                <div className="flex flex-wrap gap-2 md:justify-end">
                  <Pill>{doc.company}</Pill>
                  <Pill>{doc.category}</Pill>
                  <Pill tone={sensitivityTone(doc.sensitivity)}>{doc.sensitivity}</Pill>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-3 text-xs" style={{ color: "var(--text-muted)" }}>
                <span>Fonte: {doc.source}</span>
                <span>Status: {doc.status}</span>
                {doc.projectId ? <span>Projeto: {doc.projectId}</span> : null}
                <span>{formatBytes(doc.size)}</span>
                <span>Modificado: {formatDate(doc.modified)}</span>
              </div>
            </div>
          ))}
          {documents.length === 0 ? <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Nenhum documento encontrado para o filtro atual.</p> : null}
        </div>
      </SectionCard>

      <div className="mt-5 text-xs" style={{ color: "var(--text-muted)" }}>Atualizado em {formatDate(payload.generatedAt)} · {payload.guardrails.join(" · ")}</div>
    </PageShell>
  );
}
