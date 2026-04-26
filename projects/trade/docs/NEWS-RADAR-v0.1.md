# Trade — News Radar v0.1

## Objetivo

Criar uma rotina do agente Trade para buscar, filtrar e resumir notícias do mercado financeiro que possam impactar decisões de investimento, Wealth Monitor, Market Radar, Gold Monitor, Strategy Lab e risco de carteira.

## Frequência

### Dias úteis

1. **Pré-mercado** — antes da abertura
   - Brasil: antes da B3.
   - EUA: futures, yields, dólar, commodities e agenda.
   - Objetivo: preparar o dia.

2. **Almoço**
   - Checar mudanças relevantes desde a abertura.
   - Objetivo: correção de rota.

3. **Fechamento/fim do dia**
   - Consolidar o que mexeu mercado e o que deve entrar na tese.
   - Objetivo: journal e preparação do próximo dia.

### Fim de semana

- Apenas domingo.
- Resumo das notícias financeiras do fim de semana.
- Objetivo: preparação da semana.

## Destino

Enviar no grupo **Investimento**, tópico **Notícias**, quando o identificador do grupo/tópico estiver disponível.

Enquanto o identificador técnico do tópico não estiver confirmado, a rotina fica preparada e pode postar quando o `target`/`threadId` forem configurados.

## O que buscar

### Macro global
- Fed, juros dos EUA, yields, inflação, payroll, CPI/PCE.
- DXY, dólar/real, bancos centrais.
- Geopolítica que afete risco, commodities ou dólar.

### Brasil
- Copom, Selic, IPCA, fiscal, câmbio, Ibovespa.
- BCB, Tesouro, curva DI.
- Notícias que afetem bancos, Petrobras, Vale, energia, varejo, infraestrutura.

### EUA e bolsas globais
- S&P 500, Nasdaq, Dow, earnings relevantes.
- Big Tech, bancos, semicondutores.
- Fluxo de risco global.

### Renda fixa, fundos e Wealth Monitor
- CDI/Selic/IPCA.
- CRI/CRA, debêntures, crédito privado.
- Fundos, FIIs, ETFs e liquidez.
- Mudanças regulatórias ou tributárias.

### Commodities
- Ouro como prioridade alta.
- Prata, petróleo, minério, soja, cobre.
- Dólar e juros reais como contexto para ouro.

## Critério de relevância

Só entra no resumo se afetar pelo menos um destes pontos:

- alocação;
- risco de carteira;
- juros/inflação/câmbio;
- ouro/commodities;
- fundos ou renda fixa;
- ações/ETFs monitorados;
- tese de mercado;
- decisão de manter, reduzir, esperar ou investigar;
- necessidade de alerta ou estudo.

## Formato de saída

```text
TRADE NEWS RADAR — [Pré-mercado / Almoço / Fechamento / Domingo]

1. Macro & Juros
- [notícia] → impacto provável → ação no Trade

2. Brasil
- ...

3. EUA/Global
- ...

4. Ouro & Commodities
- ...

5. Carteira/Wealth Monitor
- ...

Sinais para acompanhar:
- ...

Status: sem recomendação automática; insumo para decisão.
```

## Guardrails

- Não transformar notícia em ordem.
- Não recomendar compra/venda sem tese, risco, benchmark e confirmação humana.
- Citar fonte/veículo quando possível.
- Não postar ruído.
- Se não houver notícia relevante, não enviar relatório vazio.
- Separar fato, impacto provável e incerteza.

## Skills/ferramentas

Não há necessidade inicial de skill GitHub específica. O fluxo pode usar busca web, Firecrawl/search e fontes públicas. Uma skill própria `trade-news-radar` pode ser criada depois se o processo ganhar complexidade, mas agora a melhor implementação é script + cron + curadoria do agente.
