# Trade — Data Ingestion Contract v0.1

Objetivo: padronizar qualquer informação antes de alimentar o Supabase/Postgres do Trade, preservando rastreabilidade, fonte, risco e uso apenas analítico/preditivo.

Regra central: nada neste contrato representa ordem real. Todo payload deve ser `read_only: true` e `execution_allowed: false`.

## 1. Envelope obrigatório

Todo dado que entrar no banco deve ter um envelope comum:

```json
{
  "schema_version": "trade.ingestion.v0.1",
  "event_id": "uuid-or-deterministic-id",
  "generated_at": "2026-04-29T15:12:00Z",
  "source": {
    "name": "yahoo_chart_api|brapi|manual|news_radar|model|agent",
    "type": "api|scrape|manual|file|computed",
    "url": null,
    "reliability_score": 0.7
  },
  "safety": {
    "read_only": true,
    "execution_allowed": false,
    "real_money": false,
    "broker_connected": false
  },
  "payload_type": "market_snapshot|macro_event|news_item|thesis|signal|forecast|risk_event|journal_entry|strategy_run|simulated_trade",
  "payload": {}
}
```

## 2. Tipos de payload e destino no banco

| Payload | Tabela principal | Uso |
|---|---|---|
| `market_snapshot` | `trade.assets`, `trade.market_bars`, `trade.asset_features` | Preço, volume, variação e features por ativo. |
| `macro_event` | `trade.events_calendar`, `trade.macro_observations` | Copom, Fed, CPI, Selic, dólar, yields etc. |
| `news_item` | `trade.journal_entries` ou futura tabela de notícias | Contexto qualitativo com fonte e impacto esperado. |
| `thesis` | `trade.journal_entries` | Tese estruturada com risco e invalidação. |
| `signal` | `trade.journal_entries` ou `trade.simulated_trades` quando houver paper/shadow | Sinal hipotético; nunca ordem real. |
| `forecast` | `trade.models`, `trade.forecasts` | Previsão probabilística versionada. |
| `risk_event` | `trade.risk_events` | Bloqueio, alerta, violação de guardrail. |
| `strategy_run` | `trade.strategies`, `trade.strategy_runs` | Backtest, forward test, paper/shadow. |
| `simulated_trade` | `trade.simulated_trades` | Trade simulado com tese, custo, slippage e resultado. |

## 3. Formato: Market Snapshot

```json
{
  "payload_type": "market_snapshot",
  "payload": {
    "market": "US|BR|GLOBAL",
    "timeframe": "1d",
    "assets": [
      {
        "symbol": "SPY",
        "source_symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "asset_type": "etf",
        "currency": "USD",
        "exchange": "NYSEARCA",
        "is_benchmark": true,
        "ts": "2026-04-29T15:00:00Z",
        "open": 0,
        "high": 0,
        "low": 0,
        "close": 0,
        "adjusted_close": 0,
        "volume": 0,
        "features": {
          "change_pct": 0,
          "day_range_pct": 0,
          "relative_to_benchmark_pct": null,
          "regime_hint": "risk_on|risk_off|neutral|unknown"
        },
        "raw": {}
      }
    ]
  }
}
```

## 4. Formato: Tese / Journal

Toda tese precisa de risco, invalidação e fonte.

```json
{
  "payload_type": "thesis",
  "payload": {
    "entry_type": "thesis",
    "title": "Tese sobre SPY após CPI",
    "body": "Resumo objetivo da tese.",
    "assets": ["SPY"],
    "tags": ["macro", "us", "cpi"],
    "thesis": {
      "directional_bias": "bullish|bearish|neutral|none",
      "horizon": "5d|1mo|3mo|12mo",
      "base_case": "Cenário base.",
      "bull_case": "Cenário positivo.",
      "bear_case": "Cenário negativo.",
      "risk": "Principal risco.",
      "invalidation": "O que invalida a tese.",
      "data_sources": [
        {"name": "fonte", "url": "https://...", "observed_at": "2026-04-29T15:12:00Z"}
      ],
      "confidence": "low|medium|high"
    }
  }
}
```

## 5. Formato: Forecast preditivo

Modelos não retornam comprar/vender. Retornam probabilidade, horizonte, confiança e risco.

```json
{
  "payload_type": "forecast",
  "payload": {
    "model": {
      "name": "baseline_market_regime",
      "version": "0.1",
      "model_type": "baseline",
      "target": "positive_return",
      "horizon": "5d"
    },
    "asset": "SPY",
    "as_of_ts": "2026-04-29T15:12:00Z",
    "horizon": "5d",
    "target": "positive_return",
    "probability_up": 0.57,
    "expected_return": 0.0042,
    "expected_drawdown": -0.011,
    "confidence": "low",
    "regime": "neutral",
    "base_rate": {
      "sample_window": "2015-01-01/2026-04-29",
      "observations": 0
    },
    "explanation": {
      "pros": [],
      "cons": [],
      "invalidation": "",
      "sources": []
    },
    "risk_gate_status": "not_evaluated|pass|warn|block"
  }
}
```

## 6. Formato: Sinal hipotético / Paper

```json
{
  "payload_type": "signal",
  "payload": {
    "strategy": "market_radar_baseline",
    "stage": "research_only|forward_test|paper|shadow",
    "asset": "SPY",
    "side": "long|flat",
    "signal_ts": "2026-04-29T15:12:00Z",
    "expected_entry": 0,
    "quantity": null,
    "thesis": "Por que o sinal existe.",
    "invalidation": "O que cancela o sinal.",
    "risk": {
      "max_loss_pct": null,
      "estimated_cost": 0,
      "estimated_slippage": 0,
      "risk_gate_status": "pass|warn|block"
    },
    "metadata": {
      "real_order": false,
      "execution_allowed": false
    }
  }
}
```

## 7. Validações antes de inserir

1. `safety.read_only` deve ser `true`.
2. `safety.execution_allowed` deve ser `false` no MVP.
3. Todo payload qualitativo precisa de `source` ou `data_sources`.
4. Toda tese/sinal precisa de `risk` e `invalidation`.
5. Forecast precisa de `model.name`, `model.version`, `asset`, `horizon`, `target` e pelo menos uma métrica probabilística.
6. Não inserir credenciais, tokens, CPF, conta de corretora ou qualquer dado sensível.
7. Não criar tabela ou campo de ordem real nesta fase.

## 8. Próximo passo técnico

Criar um validador `scripts/validate_ingestion_payload.py` e adaptar os scripts de radar/news/journal para emitirem esse envelope antes de gravar no Supabase.
