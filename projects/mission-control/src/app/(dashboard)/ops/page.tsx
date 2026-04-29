"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Activity, AlertTriangle, Archive, Database, KeyRound, RefreshCw, ShieldCheck, Workflow } from "lucide-react";
import { PageHeader, PageShell, SectionCard } from "@/components/PageShell";
import { MetricCard } from "@/components/TenacitOS/MetricCard";
import { fetchJson } from "@/lib/fetch";

type WorkingItem = {
  id: string;
  title: string;
  status: string;
  priority: string;
  domain: string;
  nextStep: string;
  evidence: string;
};

type OpsControl = {
  generatedAt: string;
  health: {
    overall: string;
    counts: Record<string, number>;
    checkedAt: string | null;
    checksCount: number;
  };
  working: {
    path: string;
    count: number;
    mtime: string | null;
    items: WorkingItem[];
  };
  backup: {
    status: string;
    processes: string[];
    tmpBytes: number;
    tmpFiles: Array<{ name: string; path: string; size: number; mtime: string }>;
    manifests: Array<{ name: string; path: string; size: number; mtime: string }>;
    latestManifest: { name: string; path: string; size: number; mtime: string } | null;
  };
  crm: {
    pipeline: {
      generatedAt: string | null;
      counts: Record<string, number>;
      verifiedContacts: number;
    };
    hubspot: {
      generatedAt: string | null;
      counts: Record<string, number>;
      gaps: Record<string, number>;
    };
  };
  artifacts: Record<string, { path: string; exists: boolean; size: number; mtime: string | null }>;
};

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function statusTone(status: string) {
  const lower = status.toLowerCase();
  if (["ok", "active", "healthy", "running", "manifest-present"].includes(lower)) return "positive" as const;
  if (["attention", "degraded", "pending", "monitorar"].includes(lower)) return "warning" as const;
  if (["critical", "down", "fail", "blocked", "bloqueado"].includes(lower)) return "negative" as const;
  return "secondary" as const;
}

function Pill({ children, tone = "secondary" }: { children: React.ReactNode; tone?: "positive" | "warning" | "negative" | "secondary" }) {
  const colors = {
    positive: "var(--positive)",
    warning: "var(--warning)",
    negative: "var(--negative)",
    secondary: "var(--text-secondary)",
  };
  return (
    <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={{ color: colors[tone], border: `1px solid ${colors[tone]}` }}>
      {children}
    </span>
  );
}

export default function OpsPage() {
  const [data, setData] = useState<OpsControl | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchJson<OpsControl>("/api/ops-control")
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  const criticalItems = useMemo(() => {
    return (data?.working.items || []).filter((item) => item.priority.includes("crítica") || item.priority.includes("alta"));
  }, [data]);

  if (error) {
    return (
      <PageShell>
        <PageHeader title="Mission Control 360" subtitle="Falha ao carregar estado operacional" icon="🦞 " />
        <SectionCard title="Erro" icon={<AlertTriangle className="h-4 w-4" />}>
          <p style={{ color: "var(--negative)" }}>{error}</p>
        </SectionCard>
      </PageShell>
    );
  }

  if (!data) {
    return (
      <PageShell>
        <PageHeader title="Mission Control 360" subtitle="Carregando estado operacional real..." icon="🦞 " />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title="Mission Control 360"
        subtitle="Estado operacional real: health, WORKING, backup, CRM/CDP, segredos e evidências"
        icon="🦞 "
        actions={
          <Link href="/" className="text-sm underline" style={{ color: "var(--text-secondary)" }}>
            Voltar ao dashboard
          </Link>
        }
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4 mb-5">
        <MetricCard icon={Activity} value={data.health.overall} label="Health operacional" change={`${data.health.checksCount} checks`} changeColor={statusTone(data.health.overall)} />
        <MetricCard icon={Workflow} value={data.working.count} label="WORKING aberto" change={`${criticalItems.length} alta/crítica`} changeColor={criticalItems.length ? "warning" : "positive"} />
        <MetricCard icon={Archive} value={data.backup.status} label="Backup full VPS" change={formatBytes(data.backup.tmpBytes)} changeColor={statusTone(data.backup.status)} />
        <MetricCard icon={Database} value={data.crm.pipeline.verifiedContacts} label="CRM candidatos verificados" change={`${data.crm.hubspot.gaps.valid_local_emails_missing_in_hubspot || 0} emails fora HubSpot`} changeColor="warning" />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <SectionCard title="Fila viva da Flávia" icon={<Workflow className="h-4 w-4" />} right={<Pill tone="secondary">{data.working.path}</Pill>}>
          <div className="space-y-3">
            {data.working.items.map((item) => (
              <div key={item.id} className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <strong style={{ color: "var(--text-primary)" }}>{item.title}</strong>
                  <div className="flex gap-2">
                    <Pill tone={statusTone(item.status)}>{item.status || "sem status"}</Pill>
                    <Pill tone={statusTone(item.priority)}>{item.priority || "sem prioridade"}</Pill>
                  </div>
                </div>
                <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>{item.nextStep}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Backup full VPS" icon={<Archive className="h-4 w-4" />} right={<Pill tone={statusTone(data.backup.status)}>{data.backup.status}</Pill>}>
          <div className="space-y-3 text-sm" style={{ color: "var(--text-secondary)" }}>
            <p><strong style={{ color: "var(--text-primary)" }}>Processos:</strong> {data.backup.processes.length}</p>
            <p><strong style={{ color: "var(--text-primary)" }}>Temporário local:</strong> {formatBytes(data.backup.tmpBytes)} em {data.backup.tmpFiles.length} arquivo(s)</p>
            <p><strong style={{ color: "var(--text-primary)" }}>Manifestos locais:</strong> {data.backup.manifests.length}</p>
            {data.backup.latestManifest ? <p><strong style={{ color: "var(--text-primary)" }}>Último manifesto:</strong> {data.backup.latestManifest.name}</p> : <p>Manifesto final ainda não encontrado.</p>}
          </div>
        </SectionCard>

        <SectionCard title="Segredos / KeeSpace" icon={<KeyRound className="h-4 w-4" />} right={<Pill tone={data.artifacts.secretsProtocol.exists ? "positive" : "negative"}>protocolo</Pill>}>
          <div className="space-y-3 text-sm" style={{ color: "var(--text-secondary)" }}>
            <p><strong style={{ color: "var(--text-primary)" }}>Protocolo:</strong> {data.artifacts.secretsProtocol.path}</p>
            <p><strong style={{ color: "var(--text-primary)" }}>Resolver:</strong> scripts/secret_config.py</p>
            <p><strong style={{ color: "var(--text-primary)" }}>Regra:</strong> agentes não pedem nem imprimem token; resolvem por referência/env/KeeSpace.</p>
          </div>
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2 mt-5">
        <SectionCard title="CRM/CDP Mensura" icon={<Database className="h-4 w-4" />} right={<Pill tone="positive">read-only</Pill>}>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
              <div style={{ color: "var(--text-secondary)" }}>SQLite contatos</div>
              <strong style={{ color: "var(--text-primary)", fontSize: 22 }}>{data.crm.pipeline.counts.contacts || 0}</strong>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
              <div style={{ color: "var(--text-secondary)" }}>HubSpot contatos</div>
              <strong style={{ color: "var(--text-primary)", fontSize: 22 }}>{data.crm.hubspot.counts.hubspot_contacts_with_email || 0}</strong>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
              <div style={{ color: "var(--text-secondary)" }}>Suppressions</div>
              <strong style={{ color: "var(--text-primary)", fontSize: 22 }}>{data.crm.pipeline.counts.suppression_list || 0}</strong>
            </div>
            <div className="rounded-lg p-3" style={{ backgroundColor: "var(--surface)" }}>
              <div style={{ color: "var(--text-secondary)" }}>Domínios fora HubSpot</div>
              <strong style={{ color: "var(--text-primary)", fontSize: 22 }}>{data.crm.hubspot.gaps.local_domains_missing_in_hubspot || 0}</strong>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Artefatos 10/10" icon={<ShieldCheck className="h-4 w-4" />} right={<Pill tone="secondary">evidência</Pill>}>
          <div className="space-y-2 text-sm">
            {Object.entries(data.artifacts).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between gap-3 rounded-lg px-3 py-2" style={{ backgroundColor: "var(--surface)", color: "var(--text-secondary)" }}>
                <span>{key}</span>
                <Pill tone={value.exists ? "positive" : "negative"}>{value.exists ? "existe" : "ausente"}</Pill>
              </div>
            ))}
            <div className="flex items-center gap-2 pt-2 text-xs" style={{ color: "var(--text-muted)" }}>
              <RefreshCw className="h-3.5 w-3.5" /> Atualizado em {new Date(data.generatedAt).toLocaleString("pt-BR")}
            </div>
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
