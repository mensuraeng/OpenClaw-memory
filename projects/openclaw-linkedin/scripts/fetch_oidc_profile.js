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
const accessToken = process.argv[2] || env.LINKEDIN_ACCESS_TOKEN;

if (!accessToken) {
  console.error('Missing LINKEDIN_ACCESS_TOKEN or first CLI argument.');
  process.exit(1);
}

const response = await fetch('https://api.linkedin.com/v2/userinfo', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});

const text = await response.text();
console.log(text);
if (!response.ok) process.exit(1);
