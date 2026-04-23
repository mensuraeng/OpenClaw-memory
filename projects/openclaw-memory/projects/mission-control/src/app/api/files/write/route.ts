import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

const OPENCLAW_DIR = process.env.OPENCLAW_DIR || '/root/.openclaw';

function getWorkspacePath(workspaceId: string): string | null {
  if (workspaceId === 'workspace') return path.join(OPENCLAW_DIR, 'workspace');
  if (/^workspace-[a-z0-9_-]+$/.test(workspaceId)) return path.join(OPENCLAW_DIR, workspaceId);
  return null;
}

function resolveSafePath(workspacePath: string, filePath: string): string | null {
  const safe = path.normalize(filePath).replace(/^(\.\.[/\\])+/, '');
  const full = path.join(workspacePath, safe);
  if (!full.startsWith(workspacePath + path.sep) && full !== workspacePath) return null;
  return full;
}

export async function POST(request: NextRequest) {
  try {
    const { workspace, path: filePath, content } = await request.json();
    if (!workspace || !filePath || content === undefined) {
      return NextResponse.json({ error: 'workspace, path e content são obrigatórios' }, { status: 400 });
    }
    const workspacePath = getWorkspacePath(workspace);
    if (!workspacePath) return NextResponse.json({ error: 'Workspace inválido' }, { status: 400 });

    const full = resolveSafePath(workspacePath, filePath);
    if (!full) return NextResponse.json({ error: 'Caminho inválido' }, { status: 403 });

    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, content, 'utf-8');
    return NextResponse.json({ ok: true, path: filePath });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  return POST(request);
}

export async function DELETE(request: NextRequest) {
  try {
    const { workspace, path: filePath } = await request.json();
    if (!workspace || !filePath) {
      return NextResponse.json({ error: 'workspace e path são obrigatórios' }, { status: 400 });
    }
    const workspacePath = getWorkspacePath(workspace);
    if (!workspacePath) return NextResponse.json({ error: 'Workspace inválido' }, { status: 400 });

    const full = resolveSafePath(workspacePath, filePath);
    if (!full) return NextResponse.json({ error: 'Caminho inválido' }, { status: 403 });

    if (!fs.existsSync(full)) return NextResponse.json({ error: 'Arquivo não encontrado' }, { status: 404 });

    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      fs.rmSync(full, { recursive: true });
    } else {
      fs.unlinkSync(full);
    }
    return NextResponse.json({ ok: true });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ error: 'Use POST/PUT para escrever, DELETE para deletar' }, { status: 405 });
}
