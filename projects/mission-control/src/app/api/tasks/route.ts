import { NextRequest, NextResponse } from "next/server";
import { readFileSync, writeFileSync, existsSync } from "fs";
import path from "path";

const DB_PATH = path.join(process.cwd(), "data", "tasks.json");

function readDB() {
  if (!existsSync(DB_PATH)) {
    const init = { tasks: [], nextId: 1 };
    writeFileSync(DB_PATH, JSON.stringify(init, null, 2));
    return init;
  }
  return JSON.parse(readFileSync(DB_PATH, "utf-8"));
}

function writeDB(data: any) {
  writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const company = searchParams.get("company");
  const db = readDB();
  const filtered = company && company !== "all"
    ? db.tasks.filter((t: any) => t.company === company)
    : db.tasks;
  return NextResponse.json({ ok: true, tasks: filtered });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const db = readDB();
  const task = {
    id: db.nextId++,
    title: body.title || "Nova tarefa",
    description: body.description || "",
    company: body.company || "mensura",
    agent: body.agent || "main",
    status: body.status || "todo",
    priority: body.priority || "medium",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  db.tasks.push(task);
  writeDB(db);
  return NextResponse.json({ ok: true, task });
}

export async function PUT(req: NextRequest) {
  const body = await req.json();
  const db = readDB();
  const idx = db.tasks.findIndex((t: any) => t.id === body.id);
  if (idx === -1) return NextResponse.json({ ok: false, error: "Not found" }, { status: 404 });
  db.tasks[idx] = { ...db.tasks[idx], ...body, updatedAt: new Date().toISOString() };
  writeDB(db);
  return NextResponse.json({ ok: true, task: db.tasks[idx] });
}

export async function DELETE(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const id = Number(searchParams.get("id"));
  const db = readDB();
  db.tasks = db.tasks.filter((t: any) => t.id !== id);
  writeDB(db);
  return NextResponse.json({ ok: true });
}
