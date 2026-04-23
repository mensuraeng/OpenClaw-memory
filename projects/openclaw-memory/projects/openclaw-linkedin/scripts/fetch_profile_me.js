import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const runtimePath = path.join(root, 'runtime', 'oauth-success.json');

function getAccessToken() {
  if (process.argv[2]) return process.argv[2];
  if (process.env.LINKEDIN_ACCESS_TOKEN) return process.env.LINKEDIN_ACCESS_TOKEN;
  if (fs.existsSync(runtimePath)) {
    const data = JSON.parse(fs.readFileSync(runtimePath, 'utf8'));
    if (data.access_token) return data.access_token;
  }
  return null;
}

const accessToken = getAccessToken();
if (!accessToken) {
  console.error('Missing access token.');
  process.exit(1);
}

const response = await fetch('https://api.linkedin.com/v2/me', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
    'X-Restli-Protocol-Version': '2.0.0',
  },
});

const text = await response.text();
console.log(text);
if (!response.ok) process.exit(1);
