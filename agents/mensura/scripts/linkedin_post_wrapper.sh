#!/usr/bin/env bash
set -euo pipefail
set -a
source /root/.openclaw/workspace/config/linkedin-mensura.env
set +a
exec python3 /root/.openclaw/workspace/agents/mensura/scripts/linkedin_post.py "$@"
