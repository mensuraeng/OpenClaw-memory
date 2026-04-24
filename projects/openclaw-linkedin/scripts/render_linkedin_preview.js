import fs from 'fs';

const raw = process.argv[2] || '';

function normalizeLinkedInText(input) {
  return String(input)
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]+\n/g, '\n')
    .trim();
}

const text = normalizeLinkedInText(raw);
const paragraphs = text.split(/\n\n/);

console.log('--- LINKEDIN PREVIEW ---\n');
for (const p of paragraphs) {
  console.log(p);
  console.log('\n');
}
console.log('--- END PREVIEW ---');

if (process.env.WRITE_NORMALIZED_PATH) {
  fs.writeFileSync(process.env.WRITE_NORMALIZED_PATH, text + '\n');
}
