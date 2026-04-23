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

export async function POST(request: NextRequest) {
  try {
    const { workspace, path: dirPath } = await request.json();
    if (!workspace || !dirPath) {
      return NextResponse.json({ error: 'workspace e path são obrigatórios' }, { status: 400 });
    }
    const workspacePath = getWorkspacePath(workspace);
    if (!workspacePath) return NextResponse.json({ error: 'Workspace inválido' }, { status: 400 });

    const safe = path.normalize(dirPath).replace(/^(\.\.[/\\])+/, '');
    const full = path.join(workspacePath, safe);
    if (!full.startsWith(workspacePath + path.sep)) {
      return NextResponse.json({ error: 'Caminho inválido' }, { status: 403 });
    }

    fs.mkdirSync(full, { recursive: true });
    return NextResponse.json({ ok: true, path: dirPath });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
