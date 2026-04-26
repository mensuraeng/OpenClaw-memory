# Trade — Wealth Monitor v0.1

## Objetivo

Criar no agente Trade uma frente de monitoramento de investimentos para otimizar aplicações do Alê com visão consolidada de:

- CDBs;
- Renda Fixa bancária;
- Tesouro Direto;
- LCI/LCA;
- CRI/CRA;
- debêntures;
- estruturados;
- fundos de investimento abertos;
- fundos listados: FIIs, ETFs, FI-Infra e similares;
- fundos/cotas cetipadas quando houver dado disponível;
- bolsas mundiais;
- commodities: ouro, prata, petróleo, minério, soja e outras relevantes;
- câmbio, juros, inflação e cenário macro.

A finalidade é **monitorar, comparar e ranquear alternativas**, não executar aplicações automaticamente.

## Princípio

O Trade deve ajudar a responder:

> “Dado meu perfil, liquidez, risco, prazo, tributação e cenário de mercado, essa aplicação é melhor que as alternativas disponíveis?”

Não basta olhar rentabilidade nominal. Toda oportunidade precisa ser comparada contra:

- CDI/Selic;
- IPCA+;
- Tesouro Direto equivalente;
- benchmark de risco;
- liquidez;
- prazo;
- tributação;
- risco de crédito;
- risco de mercado;
- concentração na carteira;
- custo/oportunidade.

## Camadas do módulo

### 1. Cadastro de produtos
Catálogo de instrumentos monitoráveis:

- emissor/gestor;
- classe;
- indexador;
- taxa;
- vencimento;
- liquidez;
- rating quando disponível;
- garantia FGC quando aplicável;
- fonte dos dados;
- status: monitorado, elegível, bloqueado, vencido.

### 2. Curvas e benchmarks
Base para comparação:

- CDI/Selic;
- IPCA;
- curvas DI/pre;
- Tesouro Selic;
- Tesouro IPCA+;
- dólar;
- S&P 500, Nasdaq, Ibovespa;
- ouro/prata/commodities relevantes.

### 3. Portfolio atual
Posições atuais, inicialmente por input manual/exportação:

- produto;
- quantidade/valor;
- data de aplicação;
- vencimento;
- taxa contratada;
- marcação a mercado quando aplicável;
- liquidez;
- concentração por emissor/classe/indexador.

### 4. Opportunity Monitor
Comparador de oportunidades novas:

- CDB x Tesouro x LCI/LCA líquido de imposto;
- CRI/CRA x debênture x fundo equivalente;
- fundo aberto x benchmark/categoria;
- FII/ETF x índice/setor;
- commodity/bolsa mundial como contexto, não recomendação automática.

### 5. Scoring
Score recomendado por oportunidade:

- retorno esperado líquido;
- spread sobre benchmark;
- liquidez;
- risco de crédito;
- duration/vencimento;
- volatilidade/marcação;
- concentração incremental;
- aderência ao objetivo;
- qualidade/fonte do dado;
- confiança.

## Fontes iniciais possíveis

### Gratuitas/baixo custo

- Banco Central SGS: Selic, CDI proxies, IPCA e séries macro;
- Tesouro Direto: taxas e preços públicos;
- CVM dados abertos: fundos, informes, PL/cota quando disponível;
- B3/yfinance/brapi: ETFs, FIIs, ações, índices e alguns recibos/listados;
- ANBIMA dados públicos quando disponível;
- Yahoo/Stooq/FRED para bolsas mundiais, dólar, yields, ouro/prata e commodities;
- extratos/exportações manuais da corretora para CDB, LCI/LCA, CRI/CRA e estruturados.

### Observação crítica
Muitos produtos de renda fixa privada não têm feed público completo e padronizado. O MVP deve aceitar:

1. ingestão manual/CSV da corretora;
2. cadastro de ofertas encontradas;
3. comparação contra benchmarks;
4. alerta de oportunidade, sem execução.

## Guardrails

- O Trade não aplica dinheiro automaticamente.
- O Trade não acessa corretora sem autorização específica.
- O Trade não recomenda produto sem fonte, prazo, liquidez, risco e benchmark.
- Produtos estruturados exigem análise separada de payoff, cenário, barreiras, emissor e liquidez.
- CRI/CRA/debêntures exigem risco de crédito e documentação mínima antes de qualquer sugestão.
- Fundos exigem comparação contra benchmark, taxa, drawdown, volatilidade, liquidez de resgate e histórico mínimo.
- Fundos listados exigem análise de preço, liquidez, desconto/prêmio, dividend yield histórico e risco de mercado.

## Saída esperada

Exemplo de saída do Trade:

```text
Oportunidade: CDB Banco X 112% CDI, venc. 2028, liquidez no vencimento
Benchmark: Tesouro Selic + CDBs comparáveis
Retorno esperado líquido: Y
Risco: crédito médio, FGC sim/não, concentração pós-aplicação Z%
Liquidez: baixa/média/alta
Conclusão: monitorar / elegível / bloquear
Motivo: spread compensa/não compensa prazo e concentração
```

## Fases

### Fase A — Monitoramento e banco
- Criar schema no Supabase.
- Cadastrar classes de produtos.
- Importar benchmarks macro.
- Permitir cadastro manual/CSV de oportunidades e posições.

### Fase B — Ranking e alertas
- Score por produto.
- Comparação líquida de imposto.
- Alertas de vencimento, concentração e oportunidade.

### Fase C — Otimização de carteira
- Rebalanceamento sugerido.
- Cenários de CDI/IPCA/dólar.
- Fronteira risco-retorno para classes permitidas.

### Fase D — Execução assistida futura
- Só com confirmação humana.
- Sem automação de aplicação.
