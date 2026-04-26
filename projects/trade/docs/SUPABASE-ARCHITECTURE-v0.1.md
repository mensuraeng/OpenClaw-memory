# Trade — Supabase Architecture v0.1

## Objetivo

Usar Supabase/Postgres como infraestrutura operacional do Trade para armazenar dados históricos, features, sinais, backtests, previsões, journal e auditoria.

A função do banco não é gerar ordem. A função é criar uma base confiável para análise probabilística e validação de estratégias.

## Princípios

- Read-only/analytics primeiro.
- Sem dinheiro real no MVP.
- Sem execução automática.
- Sem corretora conectada nesta fase.
- Toda previsão deve ser probabilística, versionada e auditável.
- Risk Gate prevalece sobre qualquer modelo.
- Separar dado bruto, feature, sinal, previsão e decisão.

## Camadas

### 1. Reference Data
- `assets` — cadastro de ativos, benchmarks, mercados e moedas.
- `data_sources` — fontes de dados e confiabilidade.

### 2. Market Data
- `market_bars` — OHLCV por ativo/timeframe.
- `macro_observations` — séries macro: juros, inflação, dólar, yields, VIX, etc.
- `events_calendar` — Copom, Fed, payroll, CPI, earnings e eventos relevantes.

### 3. Feature Store
- `feature_sets` — versão e definição de grupos de features.
- `asset_features` — features calculadas por ativo/data/timeframe.

### 4. Strategy Lab
- `strategies` — cadastro de hipóteses/estratégias.
- `strategy_runs` — backtests, forward tests e paper/shadow runs.
- `simulated_trades` — trades simulados com custo, slippage e resultado.

### 5. Predictive Lab
- `models` — registry de modelos/versionamento.
- `forecasts` — previsões probabilísticas por ativo/horizonte.
- `model_metrics` — métricas out-of-sample, calibração, Brier score, precision/recall etc.

### 6. Risk & Journal
- `risk_events` — bloqueios, violações, alertas e decisões do Risk Gate.
- `journal_entries` — teses, decisões, aprendizados e auditoria operacional.

## Saída esperada dos modelos

Modelos não devem produzir “comprar/vender”. Devem produzir:

- probabilidade;
- horizonte;
- cenário/base rate;
- retorno esperado;
- intervalo de confiança;
- regime de mercado;
- razões pró/contra;
- invalidação;
- status do Risk Gate.

Exemplo:

> SPY, horizonte 5d: probabilidade histórica/modelada de retorno positivo 57%, retorno esperado 0,42%, drawdown esperado -1,1%, regime neutro, confiança baixa/média. Sem recomendação de ordem.

## Roadmap técnico

1. Criar projeto Supabase.
2. Aplicar migration inicial.
3. Criar script de ingestão `market_radar` → Supabase.
4. Criar primeira tabela de snapshots diários.
5. Criar feature pipeline determinístico.
6. Criar primeiros relatórios probabilísticos.
7. Só depois integrar Strategy Lab/Backtest Store.

## Guardrails

- Nenhuma tabela de ordem real nesta fase.
- Nenhuma credencial de corretora no banco.
- Nenhuma chave secreta em arquivo versionável.
- RLS habilitado nas tabelas principais.
- Escrita por service role apenas em backend controlado.
