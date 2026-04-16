import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

export const dynamic = 'force-dynamic';

const execAsync = promisify(exec);

// Comandos permitidos (blocklist de comandos perigosos)
const BLOCKED = [
  /rm\s+-rf\s+\/(?!\s|$)/,         // rm -rf /
  /mkfs/,                           // format disk
  /dd\s+.*of=\/dev/,                // dd to device
  />\s*\/dev\/s/,                   // write to /dev/sd*
  /chmod\s+777\s+\//,               // chmod 777 /
  /:\(\)\s*\{.*\}/,                 // fork bomb
];

function isCommandBlocked(cmd: string): boolean {
  return BLOCKED.some(pattern => pattern.test(cmd));
}

export async function POST(request: NextRequest) {
  try {
    const { command, cwd } = await request.json();

    if (!command || typeof command !== 'string') {
      return NextResponse.json({ error: 'command é obrigatório' }, { status: 400 });
    }

    if (command.trim().length > 2000) {
      return NextResponse.json({ error: 'Comando muito longo' }, { status: 400 });
    }

    if (isCommandBlocked(command)) {
      return NextResponse.json({
        error: 'Comando bloqueado por política de segurança',
        code: 'BLOCKED'
      }, { status: 403 });
    }

    const workingDir = cwd || '/root/.openclaw/workspace';

    try {
      const { stdout, stderr } = await execAsync(command, {
        timeout: 30000,
        cwd: workingDir,
        env: { ...process.env, TERM: 'xterm-256color' },
        maxBuffer: 1024 * 1024 * 2, // 2MB
      });

      return NextResponse.json({
        stdout: stdout || '',
        stderr: stderr || '',
        exitCode: 0,
        command,
      });
    } catch (execError: unknown) {
      const err = execError as { stdout?: string; stderr?: string; code?: number; signal?: string; message?: string };
      return NextResponse.json({
        stdout: err.stdout || '',
        stderr: err.stderr || err.message || 'Erro desconhecido',
        exitCode: err.code ?? 1,
        signal: err.signal,
        command,
      });
    }
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Terminal disponível',
    note: 'Use POST com { command, cwd } para executar comandos'
  });
}
