# OpenClaw Health

- Status: `critical`
- Timestamp UTC: `2026-05-01T09:50:07.684807+00:00`

## Checks

- `pm2`: `ok` - mission-control online, restarts=22, unstable=0
- `mission_http`: `ok` - HTTP 200
- `systemd`: `ok` - 0 failed units
- `docker`: `ok` - 0 unhealthy containers
- `disk`: `critical` - root disk 99.4% used
- `logs`: `ok` - 0 log files >50MB
- `backups`: `ok` - backup retention policy satisfied
