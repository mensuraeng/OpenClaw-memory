#!/usr/bin/env bash
set -euo pipefail
PGPASSWORD="${TRADE_LOCAL_DB_PASSWORD:-postgres}" psql \
  -h "${TRADE_LOCAL_DB_HOST:-127.0.0.1}" \
  -p "${TRADE_LOCAL_DB_PORT:-54322}" \
  -U "${TRADE_LOCAL_DB_USER:-postgres}" \
  -d "${TRADE_LOCAL_DB_NAME:-postgres}" \
  -v ON_ERROR_STOP=1 \
  -c "select count(*) as assets from trade.assets;" \
  -c "select count(*) as market_bars from trade.market_bars;" \
  -c "select count(*) as asset_features from trade.asset_features;" \
  -c "select count(*) as forecasts from trade.forecasts;"
