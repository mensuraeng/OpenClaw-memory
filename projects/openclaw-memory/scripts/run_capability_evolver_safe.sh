#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace/skills/capability-evolver-src
mkdir -p memory/evolution logs
export EVOLVE_STRATEGY=harden
export EVOLVE_ALLOW_SELF_MODIFY=false
export EVOLVER_ROLLBACK_MODE=stash
export EVOLVER_LLM_REVIEW=0
export EVOLVER_AUTO_ISSUE=0
export EVOLVE_BRIDGE=false
export WORKER_ENABLED=0
export A2A_HUB_URL=
export A2A_NODE_ID=
export A2A_NODE_SECRET=
export GITHUB_TOKEN=
export GH_TOKEN=
export GITHUB_PAT=
node index.js run
