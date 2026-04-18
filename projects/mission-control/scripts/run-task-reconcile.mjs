import { request } from 'http';

const port = process.env.PORT || '3000';
const host = process.env.MISSION_CONTROL_HOST || '127.0.0.1';
const path = '/api/tasks/reconcile';

const req = request(
  {
    host,
    port: Number(port),
    path,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': '0',
    },
    timeout: 15000,
  },
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
