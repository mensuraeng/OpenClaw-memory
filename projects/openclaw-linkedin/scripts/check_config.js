import fs from 'fs';
import path from 'path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const files = [
  '.env.example',
  'config/pages.example.json',
  'docs/ARCHITECTURE.md',
  'docs/OPERATING-MODEL.md',
  'docs/PERMISSIONS.md'
];
let ok = true;
for (const rel of files) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) {
    console.error(`Missing: ${rel}`);
    ok = false;
  }
}
if (!ok) process.exit(1);
console.log('OpenClaw LinkedIn config scaffold OK');
