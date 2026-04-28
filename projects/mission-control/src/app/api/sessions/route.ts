/**
 * Sessions API — READ ONLY (v1)
 * GET /api/sessions            → list sessions for agent (default: main)
 * GET /api/sessions?agent=rh   → list sessions for agent rh
 * GET /api/sessions?id=xxx     → get messages from a specific session
 */
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join } from 'path';

const execAsync = promisify(exec);
const OPENCLAW_DIR = process.env.OPENCLAW_DIR || '/root/.openclaw';

interface RawSession {
  key: string;
  kind: string;
  updatedAt: number;
  ageMs: number;
  sessionId?: string;
  systemSent?: boolean;
  abortedLastRun?: boolean;
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
  totalTokensFresh?: boolean;
  model?: string;
  modelProvider?: string;
  contextTokens?: number;
}

function parseSessionKey(key: string) {
  const parts = key.split(':');
  if (parts.includes('run')) {
    return { type: 'unknown' as const, typeLabel: 'Run Entry', typeEmoji: '🔁', isRunEntry: true };
  }
  if (parts[2] === 'main') return { type: 'main' as const, typeLabel: 'Main Session', typeEmoji: '🦞', isRunEntry: false };
  if (parts[2] === 'cron') return { type: 'cron' as const, typeLabel: 'Cron Job', typeEmoji: '🕐', cronJobId: parts[3], isRunEntry: false };
  if (parts[2] === 'subagent') return { type: 'subagent' as const, typeLabel: 'Sub-agent', typeEmoji: '🤖', subagentId: parts[3], isRunEntry: false };
  return {
    type: 'direct' as const,
    typeLabel: parts[2] ? `${parts[2].charAt(0).toUpperCase() + parts[2].slice(1)} Chat` : 'Direct Chat',
    typeEmoji: '💬',
    isRunEntry: false,
  };
}

function getValidAgentIds(): string[] {
  try {
    const config = JSON.parse(readFileSync(`${OPENCLAW_DIR}/openclaw.json`, 'utf-8'));
    return (config.agents?.list || []).map((a: { id: string }) => a.id);
  } catch {
    return ['main'];
  }
}

function sanitizeAgentId(agentId: string): string | null {
  if (!agentId || agentId.includes('/') || agentId.includes('..') || agentId.length > 64) return null;
  const valid = getValidAgentIds();
  return valid.includes(agentId) ? agentId : null;
}

function readSessionStore(agentId: string): RawSession[] {
  const storePath = join(OPENCLAW_DIR, 'agents', agentId, 'sessions', 'sessions.json');
  if (!existsSync(storePath)) return [];

  const parsed = JSON.parse(readFileSync(storePath, 'utf-8'));
  if (Array.isArray(parsed)) return parsed;

  if (parsed && typeof parsed === 'object') {
    const now = Date.now();
    return Object.entries(parsed).map(([key, value]) => {
      const session = value && typeof value === 'object' ? value as Partial<RawSession> : {};
      const updatedAt = typeof session.updatedAt === 'number' ? session.updatedAt : 0;
      return {
        ...session,
        key,
        kind: session.kind || 'session',
        updatedAt,
        ageMs: typeof session.ageMs === 'number' ? session.ageMs : now - updatedAt,
      };
    });
  }

  return [];
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('id');
  const rawAgent = searchParams.get('agent') || 'main';
  const agentId = sanitizeAgentId(rawAgent) || 'main';

  if (sessionId) return getSessionMessages(sessionId, agentId);
  return listSessions(agentId);
}

async function listSessions(agentId: string): Promise<NextResponse> {
  try {
    let sessions: RawSession[] = readSessionStore(agentId);
    try {
      if (!sessions.length) {
        const { stdout } = await execAsync(
          `openclaw sessions --json --agent ${agentId} 2>/dev/null`,
          { timeout: 10000 }
        );
        const data = JSON.parse(stdout);
        sessions = Array.isArray(data) ? data : (data.sessions || []);
      }
    } catch {
      const sessionsDir = join(OPENCLAW_DIR, 'agents', agentId, 'sessions');
      if (existsSync(sessionsDir)) {
        try {
          const files = readdirSync(sessionsDir)
            .filter(f => f.endsWith('.jsonl') && !f.includes('.deleted'))
            .map(f => ({ file: f, stat: statSync(join(sessionsDir, f)) }))
            .sort((a, b) => b.stat.mtime.getTime() - a.stat.mtime.getTime())
            .slice(0, 50);
          sessions = files.map(({ file, stat }) => ({
            key: `agent:${agentId}:main`,
            kind: 'session',
            updatedAt: stat.mtime.getTime(),
            ageMs: Date.now() - stat.mtime.getTime(),
            sessionId: file.replace('.jsonl', ''),
          }));
        } catch { /* no sessions dir */ }
      }
    }

    const parsed = sessions
      .map((s: RawSession) => {
        const keyInfo = parseSessionKey(s.key || '');
        if (keyInfo.isRunEntry) return null;
        const contextPct = s.contextTokens && s.totalTokens
          ? Math.round((s.totalTokens / s.contextTokens) * 100)
          : null;
        return {
          id: s.sessionId || s.key,
          key: s.key,
          agentId,
          ...keyInfo,
          updatedAt: s.updatedAt,
          ageMs: s.ageMs,
          model: s.model || 'unknown',
          modelProvider: s.modelProvider || 'unknown',
          inputTokens: s.inputTokens || 0,
          outputTokens: s.outputTokens || 0,
          totalTokens: s.totalTokens || 0,
          contextTokens: s.contextTokens || 0,
          contextUsedPercent: contextPct,
          aborted: s.abortedLastRun || false,
        };
      })
      .filter(Boolean)
      .sort((a, b) => ((b?.updatedAt || 0) - (a?.updatedAt || 0)))
      .slice(0, 50);

    return NextResponse.json(parsed);
  } catch (error) {
    console.error('[sessions] Error listing sessions:', error);
    return NextResponse.json({ error: 'Failed to fetch sessions' }, { status: 500 });
  }
}

async function getSessionMessages(sessionId: string, agentId: string): Promise<NextResponse> {
  // Sanitize sessionId
  if (!sessionId || sessionId.includes('/') || sessionId.includes('..') || sessionId.length > 64) {
    return NextResponse.json({ error: 'Invalid session id' }, { status: 400 });
  }

  try {
    const sessionsDir = join(OPENCLAW_DIR, 'agents', agentId, 'sessions');
    const filePath = join(sessionsDir, `${sessionId}.jsonl`);

    // Verify path stays within sessions dir
    const { resolve } = await import('path');
    if (!resolve(filePath).startsWith(resolve(sessionsDir))) {
      return NextResponse.json({ error: 'Invalid session path' }, { status: 400 });
    }

    if (!existsSync(filePath)) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    const content = readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(Boolean);
    const messages = lines
      .map((line) => {
        try { return JSON.parse(line); } catch { return null; }
      })
      .filter(Boolean)
      .map((msg: Record<string, unknown>) => {
        // Sanitize: truncate content, omit tool_use payloads
        const sanitized: Record<string, unknown> = {
          id: msg.id,
          role: msg.role,
          timestamp: msg.timestamp,
          model: msg.model,
        };
        if (msg.content) {
          if (typeof msg.content === 'string') {
            sanitized.content = msg.content.substring(0, 500);
          } else if (Array.isArray(msg.content)) {
            sanitized.content = (msg.content as Array<Record<string, unknown>>)
              .filter((c) => c.type === 'text')
              .map((c) => ({ type: 'text', text: String(c.text || '').substring(0, 500) }));
          }
        }
        return sanitized;
      });

    return NextResponse.json({ sessionId, agentId, messages, count: messages.length });
  } catch (error) {
    console.error('[sessions] Error reading session:', error);
    return NextResponse.json({ error: 'Failed to read session' }, { status: 500 });
  }
}



// DELETE: Kill/remove a session
export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const rawAgent = searchParams.get('agent') || 'main';
  const sessionId = searchParams.get('id');
  const agentId = sanitizeAgentId(rawAgent) || 'main';

  try {
    const sessionsDir = join(OPENCLAW_DIR, 'agents', agentId, 'sessions');
    if (sessionId) {
      const f1 = join(sessionsDir, `${sessionId}.jsonl`);
      if (existsSync(f1)) {
        const fsMod = await import('fs');
        fsMod.unlinkSync(f1);
        return NextResponse.json({ ok: true, message: 'Sessao removida.' });
      }
      try {
        const { stdout: out } = await execAsync(
          `openclaw sessions kill --agent ${agentId} --id ${sessionId} 2>&1`,
          { timeout: 8000 }
        );
        return NextResponse.json({ ok: true, message: out.trim() || 'Sessao encerrada.' });
      } catch { /* ignore */ }
      return NextResponse.json({ error: 'Sessao nao encontrada' }, { status: 404 });
    } else {
      if (existsSync(sessionsDir)) {
        const fsMod = await import('fs');
        const files = fsMod.readdirSync(sessionsDir).filter((f: string) => f.endsWith('.jsonl'));
        files.forEach((f: string) => { try { fsMod.unlinkSync(join(sessionsDir, f)); } catch { /* ignore */ } });
        return NextResponse.json({ ok: true, message: `${files.length} sessao(oes) removida(s).` });
      }
      return NextResponse.json({ ok: true, message: 'Nenhuma sessao para remover.' });
    }
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
