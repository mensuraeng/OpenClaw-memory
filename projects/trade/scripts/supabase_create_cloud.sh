#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_ACCESS_TOKEN:?Set SUPABASE_ACCESS_TOKEN first}"
: "${SUPABASE_ORG_ID:?Set SUPABASE_ORG_ID first}"
: "${SUPABASE_DB_PASSWORD:?Set SUPABASE_DB_PASSWORD first}"

PROJECT_NAME="${SUPABASE_PROJECT_NAME:-trade-lab}"
REGION="${SUPABASE_REGION:-sa-east-1}"
SIZE="${SUPABASE_SIZE:-nano}"
SUPABASE_BIN="${SUPABASE_BIN:-/root/.local/bin/supabase}"

"$SUPABASE_BIN" projects create "$PROJECT_NAME" \
  --org-id "$SUPABASE_ORG_ID" \
  --db-password "$SUPABASE_DB_PASSWORD" \
  --region "$REGION" \
  --size "$SIZE" \
  --output json
