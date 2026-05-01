#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="/root/.openclaw/.env"
NODE24_DIR="${HOSTINGER_NODE24_DIR:-/root/.openclaw/tools/node-v24.15.0-linux-x64}"
MCP_DIR="${HOSTINGER_MCP_DIR:-/root/.openclaw/mcp/hostinger-api-mcp}"
MCP_BIN="$MCP_DIR/node_modules/.bin/hostinger-api-mcp"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ ! -x "$NODE24_DIR/bin/node" ]]; then
  echo "Node 24 runtime not found at $NODE24_DIR/bin/node" >&2
  exit 3
fi

if [[ ! -x "$MCP_BIN" ]]; then
  echo "Hostinger MCP binary not found at $MCP_BIN" >&2
  exit 4
fi

if [[ -z "${HOSTINGER_API_TOKEN:-}" ]]; then
  echo "HOSTINGER_API_TOKEN not configured" >&2
  exit 2
fi

export API_TOKEN="$HOSTINGER_API_TOKEN"
export PATH="$NODE24_DIR/bin:$MCP_DIR/node_modules/.bin:$PATH"
exec "$MCP_BIN" "$@"
