import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

const OPENCLAW_DIR = process.env.OPENCLAW_DIR || "/root/.openclaw";

function getWorkspacePath(workspaceId: string): string | null {
  if (workspaceId === "workspace") return path.join(OPENCLAW_DIR, "workspace");
  if (/^workspace-[a-z0-9_-]+$/.test(workspaceId)) return path.join(OPENCLAW_DIR, workspaceId);
  return null;
}

interface FileNode {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
  size?: number;
  modified?: string;
}

function buildFileTree(dir: string, basePath: string = "", depth = 0): FileNode[] {
  if (depth > 4) return [];
  const nodes: FileNode[] = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue;
      const relativePath = basePath ? `${basePath}/${entry.name}` : entry.name;
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        nodes.push({
          name: entry.name,
          path: relativePath,
          type: "directory",
          children: buildFileTree(fullPath, relativePath, depth + 1),
        });
      } else {
        const stat = fs.statSync(fullPath);
        nodes.push({
          name: entry.name,
          path: relativePath,
          type: "file",
          size: stat.size,
          modified: stat.mtime.toISOString(),
        });
      }
    }
  } catch {}
  return nodes.sort((a, b) => {
    if (a.type !== b.type) return a.type === "directory" ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const workspaceId = searchParams.get("workspace");
  const filePath = searchParams.get("path");

  if (!workspaceId) {
    return NextResponse.json({ error: "workspace parameter required" }, { status: 400 });
  }

  const workspacePath = getWorkspacePath(workspaceId);
  if (!workspacePath || !fs.existsSync(workspacePath)) {
    return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
  }

  if (filePath) {
    const safePath = path.normalize(filePath).replace(/^(\.\.[/\\])+/, "");
    const fullPath = path.join(workspacePath, safePath);
    if (!fullPath.startsWith(workspacePath + path.sep) && fullPath !== workspacePath) {
      return NextResponse.json({ error: "Acesso negado" }, { status: 403 });
    }
    try {
      const content = fs.readFileSync(fullPath, "utf-8");
      return NextResponse.json({ content, path: safePath });
    } catch {
      return NextResponse.json({ error: "Arquivo não encontrado" }, { status: 404 });
    }
  }

  const tree = buildFileTree(workspacePath);
  return NextResponse.json(tree);
}

export async function PUT(request: NextRequest) {
  try {
    const { workspace, path: filePath, content } = await request.json();
    if (!workspace || !filePath || content === undefined) {
      return NextResponse.json({ error: "workspace, path e content são obrigatórios" }, { status: 400 });
    }
    const workspacePath = getWorkspacePath(workspace);
    if (!workspacePath || !fs.existsSync(workspacePath)) {
      return NextResponse.json({ error: "Workspace não encontrado" }, { status: 404 });
    }
    const safePath = path.normalize(filePath).replace(/^(\.\.[/\\])+/, "");
    const full = path.join(workspacePath, safePath);
    if (!full.startsWith(workspacePath + path.sep) && full !== workspacePath) {
      return NextResponse.json({ error: "Caminho inválido" }, { status: 403 });
    }
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, content, "utf-8");
    return NextResponse.json({ ok: true, path: safePath });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

