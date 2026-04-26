# Trade

Projeto pessoal do Alê para radar de mercado, laboratório de estratégias, paper/shadow trading e governança de risco.

## Status

MVP em fundação. Sem credenciais, sem dinheiro real e sem execução externa.

## Documentos

- `docs/TRADE-CHARTER-v0.1.md` — arquitetura, fases, guardrails e stack.

## Estrutura

- `src/trade/data` — conectores de dados de mercado.
- `src/trade/research` — pesquisa e síntese.
- `src/trade/strategy_lab` — backtests e validação de estratégias.
- `src/trade/portfolio` — carteira e alocação.
- `src/trade/risk` — Risk Gate.
- `src/trade/journal` — memória operacional.
- `src/trade/execution` — paper/execução futura.
- `src/trade/alerts` — notificações e resumos.
- `runtime/` — cache, logs e relatórios locais.

## Regra de segurança

Execução real é bloqueada por padrão. Qualquer ordem real exigirá confirmação explícita do Alê em fase futura.

## Supabase / Predictive Lab

Supabase/Postgres foi adicionado como infraestrutura operacional do Trade.

Arquivos principais:

- `docs/SUPABASE-ARCHITECTURE-v0.1.md` — arquitetura do banco operacional.
- `supabase/migrations/20260426152300_trade_foundation.sql` — schema inicial `trade`.
- `scripts/ingest_market_radar_supabase.py` — ingere o Market Radar no Postgres/Supabase.
- `scripts/supabase_create_cloud.sh` — cria projeto cloud quando token/org/senha estiverem disponíveis.
- `scripts/supabase_link_and_push.sh` — vincula projeto cloud e aplica migrations.
- `scripts/supabase_local_verify.sh` — verifica contagens locais.

Estado validado localmente:

- Supabase CLI v2.90.0 instalado.
- Supabase local iniciado.
- Migration aplicada.
- Lint do schema sem erros.
- Snapshot do Market Radar ingerido localmente.

Regra: Supabase é analytics/predictive/journal. Não há tabela de ordem real nem execução de corretora no MVP.

## Wealth Monitor

Módulo para monitorar aplicações e oportunidades fora do trading direcional:

- CDB, LCI, LCA, CRI, CRA, debêntures e Tesouro Direto;
- produtos estruturados;
- fundos abertos;
- fundos listados/FIIs/ETFs/FI-Infra;
- bolsas mundiais;
- commodities como ouro, prata, petróleo, minério, soja e cobre.

Arquivos:

- `docs/WEALTH-MONITOR-v0.1.md`
- `config/wealth_universe.example.json`
- `supabase/migrations/20260426155300_wealth_monitor.sql`

Regra: monitoramento, comparação e ranking. Sem execução automática e sem acesso a corretora no MVP.

