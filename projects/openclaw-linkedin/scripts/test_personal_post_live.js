import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const runtimePath = path.join(root, 'runtime', 'oauth-success.json');

const text = process.argv[2] || 'Teste técnico de integração LinkedIn via Mission Control.';
const personId = process.argv[3] || 'JYAsCudAAE';

let accessToken = process.env.LINKEDIN_ACCESS_TOKEN || null;
if (!accessToken && fs.existsSync(runtimePath)) {
  const data = JSON.parse(fs.readFileSync(runtimePath, 'utf8'));
  accessToken = data.access_token || null;
}

if (!accessToken) {
  console.error(JSON.stringify({ ok: false, error: 'Missing access token' }, null, 2));
  process.exit(1);
}

const payload = {
  author: `urn:li:person:${personId}`,
  commentary: text,
  visibility: 'PUBLIC',
  distribution: {
    feedDistribution: 'MAIN_FEED',
    targetEntities: [],
    thirdPartyDistributionChannels: [],
  },
  lifecycleState: 'PUBLISHED',
  isReshareDisabledByAuthor: false,
};

const response = await fetch('https://api.linkedin.com/rest/posts', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${accessToken}`,
    'X-Restli-Protocol-Version': '2.0.0',
    'Linkedin-Version': '202604',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(payload),
});

const bodyText = await response.text();
console.log(JSON.stringify({
  ok: response.ok,
  status: response.status,
  headers: Object.fromEntries(response.headers.entries()),
  payload,
  bodyText,
}, null, 2));

if (!response.ok) process.exit(1);
