module.exports = {
  apps: [{
    name: "mission-control",
    cwd: "/root/.openclaw/workspace/projects/mission-control",
    script: "node_modules/.bin/next",
    args: "start -H 0.0.0.0 -p 3001",
    env: {
      NODE_ENV: "production",
      PORT: "3001",
    },
    max_memory_restart: "512M",
    restart_delay: 3000,
    autorestart: true,
    watch: false,
    log_date_format: "YYYY-MM-DD HH:mm:ss",
  }],
};
