/**
 * Policy layer for Mission Control v1
 * Defines allowlists and sanitization functions for all data access
 */
import path from 'path';

const DOCS_PREFIXES = ['docs/'];
const MEMORY_PREFIXES = ['memory/', 'memory/context/', 'memory/projects/'];

// Files NEVER accessible through any browser
const BLOCKED_FILES = new Set([
  'SOUL.md', 'AGENTS.md', 'USER.md', 'IDENTITY.md', 'TOOLS.md',
  'BOOT.md', 'BOOTSTRAP.md', 'ROLLBACK.md', '.env', '.env.local',
  'openclaw.json',
]);

// MEMORY.md allowed for read (in memory browser context only)
const MEMORY_MD_READABLE = new Set(['MEMORY.md', 'HEARTBEAT.md']);

export function isAllowedDocsPath(input: string): boolean {
  if (!input || input.includes('..')) return false;
  const normalized = path.normalize(input).replace(/^\/+/, '');
  if (BLOCKED_FILES.has(path.basename(normalized))) return false;
  return DOCS_PREFIXES.some(p => normalized.startsWith(p));
}

export function isAllowedMemoryPath(input: string): boolean {
  if (!input || input.includes('..')) return false;
  const normalized = path.normalize(input).replace(/^\/+/, '');
  if (BLOCKED_FILES.has(normalized)) return false;
  if (MEMORY_MD_READABLE.has(normalized)) return true;
  return MEMORY_PREFIXES.some(p => normalized.startsWith(p));
}

export function sanitizeWorkspace(workspace: string, openclawDir: string): string | null {
  if (!workspace) return null;
  const normalized = path.normalize(workspace);
  if (normalized.includes('..') || path.isAbsolute(normalized)) return null;
  if (!normalized.startsWith('workspace')) return null;
  const resolved = path.resolve(path.join(openclawDir, normalized));
  if (!resolved.startsWith(path.resolve(openclawDir))) return null;
  return normalized;
}

/**
 * Sanitize openclaw.json before sending to browser (F16)
 * Removes all tokens, auth credentials, secrets
 */
export function sanitizeOpenClawConfig(config: Record<string, unknown>): Record<string, unknown> {
  const sanitized = JSON.parse(JSON.stringify(config));

  // Remove gateway auth token
  if (sanitized.gateway?.auth) {
    sanitized.gateway.auth = { mode: sanitized.gateway.auth.mode || 'token' };
  }

  // Remove channel tokens
  if (sanitized.channels) {
    for (const channelKey of Object.keys(sanitized.channels)) {
      const channel = sanitized.channels[channelKey] as Record<string, unknown>;
      if (channel.botToken) channel.botToken = '[REDACTED]';
      if (channel.accounts) {
        for (const accKey of Object.keys(channel.accounts as object)) {
          const acc = (channel.accounts as Record<string, Record<string, unknown>>)[accKey];
          if (acc.botToken) acc.botToken = '[REDACTED]';
          if (acc.token) acc.token = '[REDACTED]';
          if (acc.authDir) delete acc.authDir;
        }
      }
    }
  }

  // Remove credentials and env (contains API keys)
  if (sanitized.credentials) delete sanitized.credentials;
  if (sanitized.env) delete sanitized.env;

  // Remove auth profiles details
  if (sanitized.auth?.profiles) {
    for (const k of Object.keys(sanitized.auth.profiles)) {
      const p = sanitized.auth.profiles[k] as Record<string, unknown>;
      delete p.apiKey;
      delete p.token;
      delete p.secret;
    }
  }

  return sanitized;
}
