#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TODAY="${1:-$(date +%F)}"

for agent in main mensura mia pcs finance; do
  mkdir -p "$ROOT/memory/inbox/$TODAY/$agent"
  [[ -f "$ROOT/memory/inbox/$TODAY/$agent/notes.md" ]] || cp "$ROOT/templates/inbox-notes.md" "$ROOT/memory/inbox/$TODAY/$agent/notes.md"
  [[ -f "$ROOT/memory/inbox/$TODAY/$agent/events.jsonl" ]] || : > "$ROOT/memory/inbox/$TODAY/$agent/events.jsonl"
done

mkdir -p "$ROOT/memory/consolidation/$TODAY"
[[ -f "$ROOT/memory/consolidation/$TODAY/summary.md" ]] || cp "$ROOT/templates/consolidation-summary.md" "$ROOT/memory/consolidation/$TODAY/summary.md"

echo "OpenClaw Memory bootstrap ok: $ROOT ($TODAY)"
