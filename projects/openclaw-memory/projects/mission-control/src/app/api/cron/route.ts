import { NextRequest, NextResponse } from "next/server";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { exec } from "child_process";
import { promisify } from "util";

export const dynamic = "force-dynamic";

const execAsync = promisify(exec);
const OPENCLAW_DIR = process.env.OPENCLAW_DIR || "/root/.openclaw";
const CRON_JOBS_FILE = OPENCLAW_DIR + "/cron/jobs.json";
const CRON_STATE_FILE = OPENCLAW_DIR + "/cron/state.json";

interface RawJob {
  id: string;
  agentId?: string;
  name?: string;
  enabled?: boolean;
  createdAtMs?: number;
  updatedAtMs?: number;
  schedule?: { kind: string; expr?: string; tz?: string; everyMs?: number; at?: string };
  sessionTarget?: string;
  payload?: { kind?: string; message?: string; text?: string };
  wakeMode?: string;
}

interface JobState {
  nextRunAtMs?: number;
  lastRunAtMs?: number;
  lastStatus?: string;
}

function readJobsFile(): { jobs: RawJob[] } {
  try {
    if (existsSync(CRON_JOBS_FILE)) {
      const d = JSON.parse(readFileSync(CRON_JOBS_FILE, "utf-8"));
      return { jobs: d.jobs || [] };
    }
  } catch { /* ignore */ }
  return { jobs: [] };
}

function readStateFile(): Record<string, JobState> {
  try {
    if (existsSync(CRON_STATE_FILE)) {
      const d = JSON.parse(readFileSync(CRON_STATE_FILE, "utf-8"));
      return d.states || d || {};
    }
  } catch { /* ignore */ }
  return {};
}

function formatSchedule(schedule: RawJob["schedule"]): string {
  if (!schedule) return "Desconhecido";
  switch (schedule.kind) {
    case "cron": return `${schedule.expr}${schedule.tz ? ` (${schedule.tz})` : ""}`;
    case "every": {
      const ms = schedule.everyMs || 0;
      if (ms >= 3600000) return `A cada ${ms / 3600000}h`;
      if (ms >= 60000) return `A cada ${ms / 60000}min`;
      return `A cada ${ms / 1000}s`;
    }
    case "at": return `Uma vez em ${schedule.at}`;
    default: return String(schedule.kind || "Desconhecido");
  }
}

function formatDescription(job: RawJob): string {
  const p = job.payload;
  if (!p) return "";
  const msg = (p.message || p.text || "") as string;
  return msg.length > 120 ? msg.substring(0, 120) + "..." : msg;
}

function mapJob(job: RawJob, states: Record<string, JobState>) {
  const state = states[job.id] || {};
  return {
    id: job.id,
    agentId: job.agentId || "main",
    name: job.name || "Sem nome",
    enabled: job.enabled ?? true,
    createdAtMs: job.createdAtMs,
    updatedAtMs: job.updatedAtMs,
    schedule: job.schedule,
    sessionTarget: job.sessionTarget,
    description: formatDescription(job),
    scheduleDisplay: formatSchedule(job.schedule),
    timezone: job.schedule?.tz || "UTC",
    nextRun: state.nextRunAtMs ? new Date(state.nextRunAtMs).toISOString() : null,
    lastRun: state.lastRunAtMs ? new Date(state.lastRunAtMs).toISOString() : null,
    lastStatus: state.lastStatus || "idle",
    state,
  };
}

// GET: List all cron jobs — reads file directly (fast, no CLI)
export async function GET() {
  try {
    const { jobs } = readJobsFile();
    const states = readStateFile();
    return NextResponse.json(jobs.map(j => mapJob(j, states)));
  } catch (error) {
    console.error("Erro ao buscar cron jobs:", error);
    return NextResponse.json({ error: "Falha ao buscar tarefas", jobs: [] }, { status: 500 });
  }
}

// PUT: Enable/disable or edit a cron job
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, enabled, expr, tz, name, agentId, message } = body;

    if (!id || typeof id !== "string" || !/^[a-z0-9-]+$/i.test(id)) {
      return NextResponse.json({ error: "ID inválido" }, { status: 400 });
    }

    // Update directly in file if possible
    const { jobs } = readJobsFile();
    const job = jobs.find(j => j.id === id);
    if (!job) return NextResponse.json({ error: "Job não encontrado" }, { status: 404 });

    if (typeof enabled === "boolean") {
      job.enabled = enabled;
      job.updatedAtMs = Date.now();
      writeFileSync(CRON_JOBS_FILE, JSON.stringify({ version: 1, jobs }, null, 2));
      return NextResponse.json({ success: true, enabled });
    }

    if (expr) {
      if (!job.schedule) job.schedule = { kind: "cron" };
      job.schedule.expr = expr;
      if (tz) job.schedule.tz = tz;
      job.updatedAtMs = Date.now();
      writeFileSync(CRON_JOBS_FILE, JSON.stringify({ version: 1, jobs }, null, 2));
      return NextResponse.json({ success: true });
    }

    if (name || agentId || message !== undefined) {
      if (name) job.name = name.trim();
      if (agentId) job.agentId = agentId.trim();
      if (message !== undefined) {
        if (!job.payload) job.payload = { kind: "message" };
        job.payload.message = message;
        job.payload.text = message;
      }
      job.updatedAtMs = Date.now();
      const { writeFileSync } = require("fs");
      writeFileSync(CRON_JOBS_FILE, JSON.stringify({ version: 1, jobs }, null, 2));
      return NextResponse.json({ success: true });
    }
    return NextResponse.json({ error: "Nenhuma alteração fornecida" }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

// DELETE: Remove a cron job
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");
    if (!id || !/^[a-z0-9-]+$/i.test(id)) {
      return NextResponse.json({ error: "ID inválido" }, { status: 400 });
    }

    // Remove from file
    const data = readJobsFile();
    const before = data.jobs.length;
    data.jobs = data.jobs.filter(j => j.id !== id);
    if (data.jobs.length === before) return NextResponse.json({ error: "Job não encontrado" }, { status: 404 });
    writeFileSync(CRON_JOBS_FILE, JSON.stringify({ version: 1, jobs: data.jobs }, null, 2));

    // Also try CLI (best-effort)
    try {
      await execAsync(`openclaw cron rm ${id} --yes 2>/dev/null || openclaw cron rm ${id} 2>/dev/null`, { timeout: 8000 });
    } catch { /* ignore */ }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

// POST: Create a new cron job
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, agentId, expr, tz, message } = body;

    if (!name || !expr || !agentId) {
      return NextResponse.json({ error: "name, agentId e expr são obrigatórios" }, { status: 400 });
    }

    const safeExpr = expr.replace(/[^0-9*,\-\/\s]/g, "").trim();
    const safeName = name.trim().replace(/"/g, "'");
    const safeAgent = agentId.replace(/[^a-z0-9\-]/gi, "").trim();
    const safeMessage = (message || `Workflow: ${safeName}`).replace(/"/g, "'");
    const tzFlag = tz ? `--tz "${tz.replace(/[^A-Za-z/_]/g, "")}"` : '--tz "America/Sao_Paulo"';

    const cmd = `openclaw cron add --name "${safeName}" --agent ${safeAgent} --cron "${safeExpr}" ${tzFlag} --message "${safeMessage}" 2>&1`;
    const { stdout } = await execAsync(cmd, { timeout: 20000 });
    return NextResponse.json({ success: true, message: stdout.trim() || "Workflow criado!" });
  } catch (error) {
    console.error("Erro ao criar cron:", error);
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
