import { request } from 'http';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Read AUTH_SECRET from .env.local — falls back to env var
function loadAuthSecret() {
  if (process.env.AUTH_SECRET) return process.env.AUTH_SECRET;
  for (const file of ['.env.local', '.env']) {
    try {
      const content = readFileSync(resolve(__dirname, '..', file), 'utf8');
      const match = content.match(/^AUTH_SECRET=(.+)$/m);
      if (match) return match[1].trim();
    } catch {
      // file not found — try next
    }
  }
  return null;
}

const port = process.env.PORT || '3001';
const host = process.env.MISSION_CONTROL_HOST || '127.0.0.1';
const path = '/api/tasks/reconcile';
const authSecret = loadAuthSecret();

const headers = {
  'Content-Type': 'application/json',
  'Content-Length': '0',
  ...(authSecret ? { Cookie: `mc_auth=${authSecret}` } : {}),
};

const req = request(
  { host, port: Number(port), path, method: 'POST', headers, timeout: 15000 },
  (res) => {
    let body = '';
    res.on('data', (chunk) => { body += chunk; });
    res.on('end', () => {
      if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
        console.log(body || '{"ok":true}');
        process.exit(0);
      }
      console.error(body || `HTTP ${res.statusCode}`);
      process.exit(1);
    });
  }
);

req.on('timeout', () => {
  console.error('Timeout running /api/tasks/reconcile');
  req.destroy();
  process.exit(1);
});

req.on('error', (error) => {
  console.error(String(error));
  process.exit(1);
});

req.end();
