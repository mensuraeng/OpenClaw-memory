#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_ACCESS_TOKEN:?Set SUPABASE_ACCESS_TOKEN first}"
: "${SUPABASE_PROJECT_REF:?Set SUPABASE_PROJECT_REF first}"
: "${SUPABASE_DB_PASSWORD:?Set SUPABASE_DB_PASSWORD first}"

SUPABASE_BIN="${SUPABASE_BIN:-/root/.local/bin/supabase}"

"$SUPABASE_BIN" link --project-ref "$SUPABASE_PROJECT_REF" --password "$SUPABASE_DB_PASSWORD"
"$SUPABASE_BIN" db push --password "$SUPABASE_DB_PASSWORD"
