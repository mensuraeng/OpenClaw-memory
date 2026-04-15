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
  console.error('Missing access token.');
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

console.log('DRY RUN PAYLOAD');
console.log(JSON.stringify(payload, null, 2));
console.log('---');
console.log('HEADERS');
console.log(JSON.stringify({
  Authorization: 'Bearer ***REDACTED***',
  'X-Restli-Protocol-Version': '2.0.0',
  'Linkedin-Version': '202604',
  'Content-Type': 'application/json',
}, null, 2));
