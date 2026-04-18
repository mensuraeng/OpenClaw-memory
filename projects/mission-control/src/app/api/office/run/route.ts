import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { readFileSync, existsSync, appendFileSync, writeFileSync, mkdirSync } from "fs";
import {
  appendTaskEvent,
  completeTaskExecution,
  createTaskExecution,
  failTaskExecution,
  startTaskExecution,
} from "@/lib/task-tracking";

export const dynamic = "force-dynamic";
const JOB_DIR = "/tmp/mc-jobs";

function ensureDir() { try { mkdirSync(JOB_DIR, { recursive: true }); } catch {} }

export async function POST(request: NextRequest) {
  try {
    const { agentId, message } = await request.json();
    if (!agentId || !message?.trim()) {
      return NextResponse.json({ error: "agentId e message são obrigatórios" }, { status: 400 });
    }
    ensureDir();
    const jobId = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    const logFile = JOB_DIR + "/" + jobId + ".log";
    const statusFile = JOB_DIR + "/" + jobId + ".status";

    const task = createTaskExecution({
      sourceAgent: "main",
      targetAgent: agentId,
      executionType: "delegation",
      title: `Office run · ${agentId}`,
      objective: message.trim(),
      inputSummary: message.trim(),
      expectedOutput: "Resposta do agente e fechamento do job",
      successCriteria: "Job finalizado com retorno útil",
      riskLevel: "medium",
      slaMinutes: 20,
      staleAfterMinutes: 10,
      validationRequired: true,
      metadata: { channel: "office", jobId },
    });

    writeFileSync(statusFile, JSON.stringify({ status: "running", taskId: task.taskId }));
    writeFileSync(logFile, "");
    startTaskExecution(task.taskId, "main");

    const child = spawn("openclaw", ["agent", "--agent", agentId, "-m", message], {
      detached: true,
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env },
    });

    child.stdout.on("data", (d: Buffer) => { try { appendFileSync(logFile, d.toString()); } catch {} });
    child.stderr.on("data", (d: Buffer) => { try { appendFileSync(logFile, d.toString()); } catch {} });
    child.on("close", (code: number) => {
      try {
        const success = code === 0;
        if (success) {
          completeTaskExecution(task.taskId, agentId, "Job do Office concluído, aguardando validação");
          appendTaskEvent({ taskId: task.taskId, agentId: "main", type: "validated", message: "Office run fechado com sucesso" });
        } else {
          failTaskExecution(task.taskId, agentId, `Job do Office encerrou com código ${code}`);
        }
        writeFileSync(statusFile, JSON.stringify({ status: success ? "done" : `error:${code}`, taskId: task.taskId }));
      } catch {}
    });
    child.on("error", (err: Error) => {
      try {
        appendFileSync(logFile, "\nERROR: " + err.message);
        failTaskExecution(task.taskId, agentId, err.message);
        writeFileSync(statusFile, JSON.stringify({ status: "error", taskId: task.taskId }));
      } catch {}
    });
    child.unref();

    return NextResponse.json({ jobId, status: "running", taskId: task.taskId });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    const jobId = new URL(request.url).searchParams.get("jobId");
    if (!jobId || !/^[a-z0-9]+$/i.test(jobId)) {
      return NextResponse.json({ error: "jobId inválido" }, { status: 400 });
    }
    const logFile = JOB_DIR + "/" + jobId + ".log";
    const statusFile = JOB_DIR + "/" + jobId + ".status";
    const rawStatus = existsSync(statusFile) ? readFileSync(statusFile, "utf-8").trim() : "unknown";
    const parsedStatus = rawStatus.startsWith("{") ? JSON.parse(rawStatus) : { status: rawStatus };
    const output = existsSync(logFile) ? readFileSync(logFile, "utf-8") : "";
    return NextResponse.json({ jobId, status: parsedStatus.status, taskId: parsedStatus.taskId, output, outputLen: output.length });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
