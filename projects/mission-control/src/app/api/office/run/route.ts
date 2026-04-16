import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { readFileSync, existsSync, appendFileSync, writeFileSync, mkdirSync } from "fs";

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

    writeFileSync(statusFile, "running");
    writeFileSync(logFile, "");

    const child = spawn("openclaw", ["agent", "--agent", agentId, "-m", message], {
      detached: true,
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env },
    });

    child.stdout.on("data", (d: Buffer) => { try { appendFileSync(logFile, d.toString()); } catch {} });
    child.stderr.on("data", (d: Buffer) => { try { appendFileSync(logFile, d.toString()); } catch {} });
    child.on("close", (code: number) => {
      try { writeFileSync(statusFile, code === 0 ? "done" : "error:" + code); } catch {}
    });
    child.on("error", (err: Error) => {
      try { appendFileSync(logFile, "\nERROR: " + err.message); writeFileSync(statusFile, "error"); } catch {}
    });
    child.unref();

    return NextResponse.json({ jobId, status: "running" });
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
    const status = existsSync(statusFile) ? readFileSync(statusFile, "utf-8").trim() : "unknown";
    const output = existsSync(logFile) ? readFileSync(logFile, "utf-8") : "";
    return NextResponse.json({ jobId, status, output, outputLen: output.length });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
