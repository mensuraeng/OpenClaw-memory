import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const runtimePath = path.join(root, 'runtime', 'oauth-success.json');

let accessToken = process.env.LINKEDIN_ACCESS_TOKEN || null;
if (!accessToken && fs.existsSync(runtimePath)) {
  const data = JSON.parse(fs.readFileSync(runtimePath, 'utf8'));
  accessToken = data.access_token || null;
}

if (!accessToken) {
  console.error(JSON.stringify({ ok: false, error: 'Missing access token' }, null, 2));
  process.exit(1);
}

const url = 'https://api.linkedin.com/rest/organizationAcls?q=roleAssignee';

const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${accessToken}`,
    'X-Restli-Protocol-Version': '2.0.0',
    'Linkedin-Version': '202604',
  },
});

const bodyText = await response.text();
console.log(JSON.stringify({
  ok: response.ok,
  status: response.status,
  url,
  bodyText,
}, null, 2));

if (!response.ok) process.exit(1);
