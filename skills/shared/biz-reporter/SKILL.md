# Biz Reporter — Flávia Edition

Skill para relatórios executivos automáticos e snapshots operacionais, adaptado ao estágio atual da operação.

## Objetivo

Gerar relatórios úteis e enxutos usando apenas fontes realmente conectadas ou disponíveis.

## Princípio central

**Não inventar BI sem base.**

Se a fonte não está conectada ou confiável:
- declarar ausência
- propor próxima integração
- não fabricar dashboard ornamental

## Fontes prioritárias atuais

### Já plausíveis / parcialmente disponíveis
- Microsoft Graph (email, calendário)
- memória operacional (`memory/`)
- cron status / automações ativas
- clima, quando útil para agenda logística
- Notion, quando integração e páginas estiverem compartilhadas

### Futuras
- GA4
- Search Console
- LinkedIn
- Instagram
- CRM
- Stripe / receita

## Relatórios iniciais recomendados

### 1. Daily Briefing Executivo
Formato:
- agenda do dia
- pendências críticas
- riscos e follow-ups
- alertas operacionais
- próximos passos

### 2. Snapshot Operacional Semanal
Formato:
- automações ativas
- pendências abertas
- follow-ups sem resposta
- obras/rotinas com risco de atraso
- decisões necessárias do Alê

### 3. Report por integração conectada
Quando uma fonte entrar de verdade, adicionar seção específica.
Exemplo:
- calendário → compromissos e conflitos
- email → follow-ups críticos
- Notion → tarefas/reuniões recentes

## Regras

- Toda saída deve distinguir claramente:
  - dado real
  - inferência
  - ausência de fonte
- Não usar linguagem de dashboard corporativo vazio
- Priorizar utilidade executiva em vez de volume de métricas

## Entregas por estágio

### Estágio 1
Relatórios operacionais com base em memória, calendário, email e crons.

### Estágio 2
Relatórios híbridos com Notion e outras integrações.

### Estágio 3
BI mais completo com marketing/comercial/analytics.

## Fit operacional

Este skill existe para transformar sinais dispersos em leitura executiva acionável, sem fingir maturidade analítica que ainda não foi construída.
