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
const code = process.argv[2] || env.LINKEDIN_AUTH_CODE;
const required = ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET', 'LINKEDIN_REDIRECT_URI'];
const missing = required.filter((k) => !env[k]);
if (!code) missing.push('authorization code argument or LINKEDIN_AUTH_CODE');
if (missing.length) {
  console.error(`Missing required inputs: ${missing.join(', ')}`);
  process.exit(1);
}

const params = new URLSearchParams({
  grant_type: 'authorization_code',
  code,
  client_id: env.LINKEDIN_CLIENT_ID,
  client_secret: env.LINKEDIN_CLIENT_SECRET,
  redirect_uri: env.LINKEDIN_REDIRECT_URI,
});

const response = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: params.toString(),
});

const text = await response.text();
console.log(text);
if (!response.ok) process.exit(1);
