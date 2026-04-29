# Trade — Predictive Base Runbook v0.1

Objetivo: criar e manter a base histórica que alimenta análise preditiva no Supabase/Postgres do Trade.

## Princípio operacional

A base preditiva não é uma lista de palpites. Ela é um histórico auditável de:

- preços/OHLCV por ativo e timeframe;
- features derivadas;
- eventos macro e notícias relevantes;
- teses, sinais hipotéticos e invalidações;
- previsões probabilísticas e métricas de modelo;
- journal e revisões.

Nada aqui executa ordem real.

## Comandos principais

Criar arquivo JSONL validado, sem gravar no banco:

```bash
./bin/trade predictive-base --range 5y
```

Criar e gravar no Supabase/Postgres:

```bash
./bin/trade predictive-base --range 5y --db
```

Criar base menor para teste:

```bash
./bin/trade predictive-base --symbols SPY AAPL BOVA11 --range 1y --db
```

Incluir relatórios antigos do runtime como journal:

```bash
./bin/trade predictive-base --range 5y --include-runtime-reports --db
```

Validar qualquer arquivo antes da ingestão:

```bash
./bin/trade validate-payload runtime/datasets/predictive-base-latest.jsonl
```

Ingerir séries macro públicas do Banco Central/SGS:

```bash
./bin/trade macro-bcb --years 10
```

Calcular features técnicas preditivas sobre o OHLCV carregado:

```bash
./bin/trade predictive-features
```

## Fontes v0.1

### Yahoo Chart API

Uso: histórico OHLCV público para ativos do universo inicial.

Destino:

- `trade.assets`
- `trade.market_bars`
- `trade.asset_features`

Features iniciais:

- `change_pct`
- `day_range_pct`
- `history_range`
- `market`
- `is_benchmark`

### Banco Central do Brasil — SGS

Uso: séries macro Brasil para contexto de juros, inflação e câmbio.

Destino:

- `trade.macro_observations`

Séries v0.1:

- `selic_meta`
- `selic_over`
- `cdi`
- `ipca`
- `usd_brl_ptax_buy`
- `usd_brl_ptax_sell`

### Relatórios locais antigos

Uso: preservar contexto gerado anteriormente pelo agente.

Destino:

- `trade.journal_entries`

Arquivos considerados:

- `runtime/reports/*.md`

## Features técnicas v0.1

Feature set: `predictive_technical_daily`.

Campos:

- `ret_1d`
- `ret_5d`
- `ret_20d`
- `vol_20d_ann`
- `ma_20_ratio`
- `ma_50_ratio`
- `drawdown_252d`
- `volume_z_20d`
- `range_pct`

## Arquivos gerados

Padrão:

```text
runtime/datasets/predictive-base-latest.jsonl
```

Cada linha é um envelope `trade.ingestion.v0.1` validável.

## Guardrails

- `safety.read_only = true`
- `safety.execution_allowed = false`
- `safety.real_money = false`
- `safety.broker_connected = false`
- sem credenciais de corretora;
- sem ordem real;
- sem recomendação de compra/venda como output de modelo.

## Próximas expansões

1. Incluir BCB SGS para Selic, IPCA, CDI e câmbio PTAX.
2. Incluir calendário macro: Fed, Copom, CPI, payroll, earnings.
3. Criar tabela dedicada para notícias se o volume justificar.
4. Criar pipeline determinístico de features: médias móveis, volatilidade, drawdown, momentum, correlação com benchmark.
5. Criar baseline model para `forecast` com probabilidade histórica por ativo/horizonte.
