# Trade Charter v0.1

_Projeto pessoal do Alê — separado de Mensura, MIA, PCS e demais frentes empresariais._

## 1. Objetivo

Construir um sistema pessoal de inteligência, pesquisa, teste e operação assistida para investimentos/trading, com foco inicial em:

- monitorar mercado brasileiro e americano;
- testar estratégias com disciplina;
- rodar paper/shadow trading antes de qualquer execução real;
- comparar performance contra benchmarks;
- reduzir custo recorrente;
- evitar automação perigosa sem governança.

O objetivo não é criar um bot agressivo. O objetivo é criar uma **máquina de decisão com memória, risco e validação**.

## 2. Princípio central

**Nenhuma estratégia vai para dinheiro real antes de sobreviver a backtest, forward test e paper/shadow com métricas claras.**

Backtest não aprova estratégia. Backtest só dá direito a forward test.

## 3. Escopo inicial

### Incluído no MVP

- Radar de mercado EUA;
- Radar de mercado Brasil;
- paper trading EUA via Alpaca;
- carteira simulada Brasil;
- Strategy Lab para backtesting;
- Journal diário/semanal;
- Risk Gate central;
- relatórios de performance;
- notificações/resumos via Telegram para o Alê.

### Fora do MVP

- dinheiro real;
- cripto;
- alavancagem;
- opções;
- short;
- day trade;
- TradingView webhook direto para corretora;
- OKX/Freqtrade como frente principal.

## 4. Benchmarks

### EUA

- S&P 500: SPY / VOO / IVV
- Opcional: Nasdaq 100 via QQQ

### Brasil

- Ibovespa: BOVA11 ou índice equivalente
- CDI como benchmark de oportunidade
- Dólar e juros como contexto macro

## 5. Arquitetura funcional

### 5.1 Market Radar

Responsável por coletar e normalizar dados:

- preços;
- volume;
- variação diária/semanal;
- volatilidade;
- calendário macro;
- notícias relevantes;
- benchmarks;
- contexto de dólar, juros e commodities.

Fontes iniciais:

- EUA: Alpaca;
- Brasil: Brapi + yfinance + BCB quando necessário;
- notícias/pesquisa: web search / Firecrawl / Perplexity se configurado.

### 5.2 Strategy Lab

Responsável por testar estratégias:

- backtesting.py para MVP;
- vectorbt para varredura de parâmetros e robustez;
- TradingView/Pine Script como laboratório complementar;
- registro de parâmetros, janela, ativo, timeframe e resultado.

Critérios mínimos:

- múltiplas janelas;
- comparação contra buy-and-hold;
- custo e slippage estimados;
- número suficiente de trades;
- drawdown compatível;
- tese explícita de quando funciona e quando falha.

### 5.3 Research Desk

Inspirado em TradingAgents/FinRobot, mas simplificado.

Papéis lógicos:

- analista macro;
- analista fundamentalista;
- analista técnico;
- analista de sentimento/notícias;
- sintetizador de tese.

Saída esperada:

- tese;
- catalisadores;
- riscos;
- invalidação;
- horizonte;
- convicção;
- sugestão de ação.

### 5.4 Portfolio Agent

Responsável por propor alocação:

- posição máxima por ativo;
- exposição máxima por mercado/setor;
- caixa mínimo;
- otimização futura com PyPortfolioOpt;
- sem execução direta.

### 5.5 Risk Gate

Camada obrigatória antes de qualquer ordem simulada ou real.

Bloqueios iniciais:

- ativo fora da whitelist;
- tamanho acima do limite;
- perda diária/semanal acima do limite;
- tese ausente;
- stop/invalidação ausente;
- concentração excessiva;
- tentativa de alavancagem, opção, short ou cripto no MVP;
- qualquer ordem real sem confirmação humana.

### 5.6 Journal & Reports

Responsável por memória operacional:

- decisões;
- trades simulados;
- ordens propostas;
- resultado;
- lições;
- revisões semanais;
- relatórios QuantStats.

## 6. Rotinas propostas

### Domingo à noite

- preparar watchlist semanal;
- calendário macro;
- earnings relevantes;
- regimes prováveis de mercado.

### Pré-mercado Brasil

- Ibovespa/BOVA11;
- dólar;
- juros/CDI/Selic;
- commodities;
- notícias locais;
- ações prioritárias.

### Pré-mercado EUA

- futures;
- yields;
- calendário macro;
- earnings;
- notícias de setores prioritários.

### Meio do pregão

- risco;
- variações anormais;
- alertas de tese;
- sem overtrading.

### Fechamento

- P&L;
- decisões;
- carteira;
- benchmark;
- lições.

### Sexta

- revisão semanal;
- performance vs benchmarks;
- drawdown;
- aderência à tese;
- ajustes permitidos.

## 7. Guardrails iniciais

- Paper/shadow por padrão;
- execução real bloqueada;
- máximo 5% por posição no paper inicial;
- máximo 20% de novas posições por semana;
- perda diária simulada > 2% congela novas entradas;
- perda semanal simulada > 5% congela a estratégia;
- sem ordem sem tese;
- sem ordem sem stop ou regra de invalidação;
- sem cripto, opções, short, margem ou alavancagem no MVP.

## 8. Stack recomendado

### MVP

- Python;
- alpaca-py;
- brapi/yfinance/BCB;
- backtesting.py;
- quantstats;
- pandas/numpy;
- arquivos markdown/json como memória;
- OpenClaw cron para rotinas.

### Fase 1.5

- vectorbt;
- PyPortfolioOpt;
- dashboard simples;
- cache persistente;
- Strategy Lab com múltiplas estratégias.

### Fase 2

- Riskfolio-Lib;
- TradingView/Pine integration assistida;
- Lean/QuantConnect se fizer sentido;
- execução real assistida.

## 9. Fases de implantação

### Fase 0 — Fundação

- criar estrutura do projeto;
- definir configuração sem segredos;
- criar universe inicial;
- criar journal;
- criar README operacional.

### Fase 1 — Radar sem execução

- coletar dados EUA/Brasil;
- gerar snapshot diário;
- registrar em journal;
- zero ordens.

### Fase 2 — Strategy Lab

- implementar backtest MVP;
- criar relatório de métricas;
- rodar primeira estratégia simples;
- validar custo/slippage.

### Fase 3 — Paper/Shadow

- Alpaca paper nos EUA;
- carteira simulada B3;
- comparação semanal com benchmarks;
- nenhuma ordem real.

### Fase 4 — Execução assistida

- ordem real pequena;
- aprovação humana obrigatória;
- logs completos;
- kill switch.

### Fase 5 — Autonomia limitada

Só se as fases anteriores provarem valor.

## 10. Decisões pendentes do Alê

- capital simulado inicial;
- universo inicial de ativos EUA;
- universo inicial de ativos Brasil;
- tolerância máxima de drawdown no paper;
- preferência de horizonte: swing, carteira tática, longo prazo;
- corretora brasileira atual, se quisermos avaliar API no futuro.
