#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "uso: $0 <arquivo-backup.tar.gz> [--apply]" >&2
  exit 1
fi

ARCHIVE="$1"
APPLY="false"
if [[ "${2:-}" == "--apply" ]]; then
  APPLY="true"
fi

openclaw backup verify "$ARCHIVE" >/dev/null
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

tar -xzf "$ARCHIVE" -C "$TMP_DIR"
PAYLOAD_DIR="$(find "$TMP_DIR" -type d -path '*/payload/posix/root/.openclaw' | head -1)"
if [[ -z "$PAYLOAD_DIR" ]]; then
  echo "payload .openclaw não encontrado no backup" >&2
  exit 1
fi

if [[ "$APPLY" != "true" ]]; then
  echo "DRY RUN"
  echo "backup validado: $ARCHIVE"
  echo "origem restaurável: $PAYLOAD_DIR"
  echo "para aplicar: $0 '$ARCHIVE' --apply"
  exit 0
fi

rsync -a --delete "$PAYLOAD_DIR/" /root/.openclaw/
echo "Restore concluído a partir de $ARCHIVE"
