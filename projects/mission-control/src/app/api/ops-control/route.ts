import { NextResponse } from "next/server";
import { existsSync, readdirSync, readFileSync, statSync } from "fs";
import { join } from "path";
import { execFileSync } from "child_process";

export const dynamic = "force-dynamic";

const WORKSPACE = "/root/.openclaw/workspace";
const SECOND_BRAIN = "/root/2nd-brain";

function readJson(path: string): unknown | null {
  try {
    if (!existsSync(path)) return null;
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return null;
  }
}

function fileInfo(path: string) {
  try {
    const stat = statSync(path);
    return { path, exists: true, size: stat.size, mtime: stat.mtime.toISOString() };
  } catch {
    return { path, exists: false, size: 0, mtime: null };
  }
}

function listFiles(dir: string) {
  try {
    return readdirSync(dir).map((name) => {
      const path = join(dir, name);
      const stat = statSync(path);
      return { name, path, size: stat.size, mtime: stat.mtime.toISOString() };
    }).sort((a, b) => a.name.localeCompare(b.name));
  } catch {
    return [];
  }
}

function grepProcess(pattern: string) {
  try {
    const out = execFileSync("pgrep", ["-af", pattern], { encoding: "utf-8", timeout: 3000 });
    return out.trim().split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

function parseWorking() {
  const path = join(SECOND_BRAIN, "06-agents/flavia/WORKING.md");
  try {
    const text = readFileSync(path, "utf-8");
    const activeSection = text.split("## Ativas")[1]?.split("## Aguardando humano")[0] || "";
    const items = activeSection
      .split(/\n### /)
      .map((block) => block.trim())
      .filter(Boolean)
      .map((block) => {
        const lines = block.split("\n");
        const title = lines[0].replace(/^###\s*/, "").trim();
        const value = (key: string) => {
          const found = lines.find((line) => line.trim().startsWith(`- ${key}:`));
          return found ? found.split(":").slice(1).join(":").trim() : "";
        };
        return {
          id: title.split(" — ")[0] || title,
          title,
          status: value("status"),
          priority: value("prioridade"),
          domain: value("domínio"),
          nextStep: value("próximo passo"),
          evidence: value("evidência atual"),
        };
      });
    return { path, items, count: items.length, mtime: statSync(path).mtime.toISOString() };
  } catch {
    return { path, items: [], count: 0, mtime: null };
  }
}

function getBackupState() {
  const tmpDir = join(WORKSPACE, "runtime/backups/vps-full-stream-tmp");
  const manifestDir = join(WORKSPACE, "runtime/backups/vps-full-manifests");
  const tmpFiles = listFiles(tmpDir);
  const manifests = listFiles(manifestDir);
  const processes = grepProcess("backup_vps_full_b2_stream.py --run|openssl enc -aes-256-cbc|tar --warning=no-file-changed");
  const latestManifest = manifests[manifests.length - 1];
  return {
    status: processes.length > 0 ? "running" : latestManifest ? "manifest-present" : "not-running",
    processes,
    tmpFiles,
    tmpBytes: tmpFiles.reduce((sum, file) => sum + file.size, 0),
    manifests,
    latestManifest: latestManifest || null,
  };
}

export async function GET() {
  const health = readJson(join(WORKSPACE, "runtime/operational-health/latest.json"));
  const crmPipeline = readJson(join(WORKSPACE, "runtime/data-pipeline/crm/mensura-crm-pipeline-latest.json"));
  const hubspotReconciliation = readJson(join(WORKSPACE, "runtime/data-pipeline/crm/mensura-hubspot-reconciliation-latest.json"));
  const usageLedger = fileInfo(join(WORKSPACE, "runtime/usage-ledger/usage-ledger.jsonl"));
  const secretsProtocol = fileInfo(join(WORKSPACE, "docs/operacao/KEESPACE-SECRETS-PROTOCOL.md"));
  const crmDoc = fileInfo(join(WORKSPACE, "docs/operacao/MENSURA-CRM-CDP-PIPELINE.md"));
  const working = parseWorking();
  const backup = getBackupState();

  const healthRecord = (health && typeof health === "object" ? health : {}) as { overall?: string; counts?: Record<string, number>; checked_at_utc?: string; checks?: unknown[] };
  const crmRecord = (crmPipeline && typeof crmPipeline === "object" ? crmPipeline : {}) as { counts?: Record<string, number>; verified_contacts_count?: number; generated_at_utc?: string };
  const reconciliationRecord = (hubspotReconciliation && typeof hubspotReconciliation === "object" ? hubspotReconciliation : {}) as { counts?: Record<string, number>; gaps?: Record<string, number>; generated_at_utc?: string };

  return NextResponse.json({
    generatedAt: new Date().toISOString(),
    health: {
      overall: healthRecord.overall || "unknown",
      counts: healthRecord.counts || {},
      checkedAt: healthRecord.checked_at_utc || null,
      checksCount: Array.isArray(healthRecord.checks) ? healthRecord.checks.length : 0,
    },
    working,
    backup,
    crm: {
      pipeline: {
        generatedAt: crmRecord.generated_at_utc || null,
        counts: crmRecord.counts || {},
        verifiedContacts: crmRecord.verified_contacts_count || 0,
      },
      hubspot: {
        generatedAt: reconciliationRecord.generated_at_utc || null,
        counts: reconciliationRecord.counts || {},
        gaps: reconciliationRecord.gaps || {},
      },
    },
    artifacts: {
      usageLedger,
      secretsProtocol,
      crmDoc,
    },
  });
}
