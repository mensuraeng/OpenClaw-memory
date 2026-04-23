import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const envPath = path.join(root, '.env');

function loadEnv(file) {
  if (!fs.existsSync(file)) return {};
  const out = {};
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    if (!line || line.trim().startsWith('#')) continue;
    const idx = line.indexOf('=');
    if (idx === -1) continue;
    out[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
  }
  return out;
}

const env = { ...loadEnv(envPath), ...process.env };
const required = ['LINKEDIN_CLIENT_ID', 'LINKEDIN_REDIRECT_URI'];
const missing = required.filter(k => !env[k]);
if (missing.length) {
  console.error(`Missing required env vars: ${missing.join(', ')}`);
  process.exit(1);
}
const state = env.LINKEDIN_STATE || 'openclaw-linkedin-state';
const scope = encodeURIComponent(env.LINKEDIN_SCOPES || 'openid profile w_member_social');
const redirect = encodeURIComponent(env.LINKEDIN_REDIRECT_URI);
const clientId = encodeURIComponent(env.LINKEDIN_CLIENT_ID);
const url = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${redirect}&state=${encodeURIComponent(state)}&scope=${scope}`;
console.log(url);
