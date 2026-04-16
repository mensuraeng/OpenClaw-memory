/**
 * Git Dashboard API — READ ONLY (v1)
 * GET /api/git - List all repos with status
 * POST: DISABLED in v1 (git pull/push would introduce remote code)
 */
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { promises as fs } from 'fs';
import path from 'path';

const execAsync = promisify(exec);
const WORKSPACE = process.env.OPENCLAW_DIR ? `${process.env.OPENCLAW_DIR}/workspace` : '/root/.openclaw/workspace';

interface RepoStatus {
  name: string;
  path: string;
  branch: string;
  ahead: number;
  behind: number;
  staged: string[];
  unstaged: string[];
  untracked: string[];
  lastCommit: { hash: string; message: string; author: string; date: string } | null;
  remoteUrl: string;
  isDirty: boolean;
}

async function getRepos(): Promise<string[]> {
  try {
    const { stdout } = await execAsync(`find "${WORKSPACE}" -maxdepth 2 -name ".git" -type d 2>/dev/null`);
    return stdout.trim().split('\n').filter(Boolean).map((d) => d.replace('/.git', ''));
  } catch {
    return [];
  }
}

async function getRepoStatus(repoPath: string): Promise<RepoStatus> {
  const name = repoPath.split('/').pop() || repoPath;

  try {
    const { stdout: branch } = await execAsync(`cd "${repoPath}" && git rev-parse --abbrev-ref HEAD 2>/dev/null`).catch(() => ({ stdout: 'unknown' }));

    let ahead = 0, behind = 0;
    try {
      const { stdout: abStr } = await execAsync(`cd "${repoPath}" && git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null`).catch(() => ({ stdout: '0\t0' }));
      const parts = abStr.trim().split('\t');
      ahead = parseInt(parts[0]) || 0;
      behind = parseInt(parts[1]) || 0;
    } catch {}

    const { stdout: statusOut } = await execAsync(`cd "${repoPath}" && git status --porcelain 2>/dev/null`).catch(() => ({ stdout: '' }));
    const lines = statusOut.trim().split('\n').filter(Boolean);

    const staged: string[] = [];
    const unstaged: string[] = [];
    const untracked: string[] = [];

    for (const line of lines) {
      const xy = line.slice(0, 2);
      const file = line.slice(3);
      const x = xy[0];
      const y = xy[1];
      if (x !== ' ' && x !== '?') staged.push(file);
      if (y !== ' ' && y !== '?') unstaged.push(file);
      if (xy === '??') untracked.push(file);
    }

    let lastCommit = null;
    try {
      const { stdout: commitOut } = await execAsync(`cd "${repoPath}" && git log -1 --format="%H|%s|%an|%ar" 2>/dev/null`);
      const parts = commitOut.trim().split('|');
      if (parts.length >= 4) {
        lastCommit = { hash: parts[0].slice(0, 8), message: parts[1], author: parts[2], date: parts[3] };
      }
    } catch {}

    // Sanitize remoteUrl — strip any embedded credentials
    let remoteUrl = '';
    try {
      const { stdout: remote } = await execAsync(`cd "${repoPath}" && git remote get-url origin 2>/dev/null`);
      remoteUrl = remote.trim().replace(/:[^@/]+@/, ':***@');
    } catch {}

    return {
      name,
      path: repoPath,
      branch: branch.trim(),
      ahead,
      behind,
      staged,
      unstaged,
      untracked,
      lastCommit,
      remoteUrl,
      isDirty: staged.length > 0 || unstaged.length > 0,
    };
  } catch {
    return { name, path: repoPath, branch: 'unknown', ahead: 0, behind: 0, staged: [], unstaged: [], untracked: [], lastCommit: null, remoteUrl: '', isDirty: false };
  }
}

export async function GET() {
  try {
    const repos = await getRepos();
    const statuses = await Promise.all(repos.map(getRepoStatus));
    return NextResponse.json(statuses);
  } catch (error) {
    console.error('[git] Error fetching repos:', error);
    return NextResponse.json({ error: 'Failed to fetch git status' }, { status: 500 });
  }
}

// POST disabled in v1 — git pull/commit via browser would introduce remote code
export async function POST() {
  return NextResponse.json(
    { error: 'git write operations disabled in mission control v1', code: 'DISABLED_IN_V1' },
    { status: 403 }
  );
}
