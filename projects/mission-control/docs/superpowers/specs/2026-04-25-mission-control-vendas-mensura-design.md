# Design: Mission Control — Página Vendas MENSURA

_Data: 2026-04-25_

---

## Contexto

A Máquina de Vendas MENSURA já está operacional: HubSpot CRM (pipeline de 10 etapas), Phantombuster (prospecção LinkedIn 15/dia) e 3 scripts cron (`monitoramento_comercial_mensura.py`, `operacional_marketing_mensura.py`, `revisao_tecnica_mensura.py`). O Mission Control precisa de uma página dedicada que exiba esses dados ao vivo, reutilizando a mesma lógica dos scripts existentes.

Referência completa da máquina: `memory/context/mapa-maquina-vendas-mensura.md`

---

## Arquitetura

**Rota frontend:** `/mensura/vendas` (nova página no dashboard)
**API route:** `/api/vendas` — chama HubSpot e Phantombuster ao vivo, retorna JSON unificado
**Dados secundários:** arquivo de saída do script cron (último relatório salvo em disco) para exibição do resumo CFO

### Fluxo de dados

```
Browser → GET /api/vendas
          ├── HubSpot /crm/v3/objects/contacts (total + novos 24h)
          ├── HubSpot /crm/v3/objects/companies (total)
          ├── HubSpot /crm/v3/objects/deals/search (pipeline por etapa + deals paradas 7d+)
          └── Phantombuster /api/v2/agents (status dos 3 agentes)
          → JSON { kpis, pipeline, oportunidades, linkedin }
```

Credenciais lidas de `config/hubspot-mensura.json` e `config/phantombuster-mensura.json` — nunca hardcoded.

---

## Componentes da Página

### 1. KPIs do Dia (cards no topo)
7 cards em linha horizontal:
- Leads novos (24h)
- Conexões aceitas
- Abordagens enviadas
- Respostas recebidas
- Reuniões agendadas
- Propostas enviadas
- Fechados (ganho/perdido)

Fonte: HubSpot deals filtradas por `createdate` últimas 24h e por stage.

### 2. Pipeline Visual (10 etapas)
Funil horizontal com bolhas ou colunas por etapa. Cada etapa mostra:
- Nome em português
- Contagem de deals
- Destaque visual se etapa estiver vazia

Ordem: Lead → Abordagem → Conexão → Resposta → Reunião → Diagnóstico → Proposta → Negociação → Ganho/Perdido

### 3. Oportunidades Ativas (tabela)
Tabela com deals em aberto (exceto closedwon/closedlost):

| Empresa | Decisor | Etapa | Dias sem ação | Alerta |
|---|---|---|---|---|

- Alerta vermelho: ≥7 dias sem ação
- Alerta amarelo: 4–6 dias sem ação
- Ordenado por dias sem ação (maior primeiro)

### 4. Radar LinkedIn / Phantombuster
3 cards compactos — um por agente Phantombuster:
- `linkedin_outreach`: último run, convites enviados, status
- `hubspot_contact_sender`: último run, contatos enviados, status
- `linkedin_search_export`: último run, leads exportados, status

### 5. Último Relatório CFO (colapsável)
Exibe o texto do último relatório gerado pelo script cron (arquivo em disco ou stdout capturado). Colapsado por padrão, expansível com botão.

---

## API Route — `/api/vendas/route.ts`

```typescript
// GET /api/vendas
// Retorna: { kpis, pipeline, oportunidades, linkedin, generatedAt }
```

Lê credenciais dos JSONs de config. Paraleliza chamadas HubSpot + Phantombuster com `Promise.all`. Timeout de 15s por chamada. Em erro parcial, retorna dados disponíveis + flag `partial: true`.

---

## Navegação

Adicionar "Vendas" no sidebar do Mission Control, na seção MENSURA, com ícone `TrendingUp` (Lucide).

---

## Fora do escopo (v1)

- Escrita no HubSpot (mover deals, atualizar contatos) — página é read-only
- Histórico de KPIs ao longo do tempo (gráficos de tendência)
- Integração Make.com webhooks
- Filtros por período customizado

---

## Checklist de implementação

- [ ] API route `/api/vendas/route.ts` com HubSpot + Phantombuster
- [ ] Página `/mensura/vendas/page.tsx` com 5 seções
- [ ] Componente `KpiCards` (7 cards)
- [ ] Componente `PipelineVisual` (10 etapas)
- [ ] Componente `OportunidadesTable` (com alertas)
- [ ] Componente `LinkedinRadar` (3 agentes)
- [ ] Componente `RelatorioCFO` (colapsável)
- [ ] Entrada no sidebar (ícone TrendingUp, seção MENSURA)
- [ ] Testes manuais com dados reais do HubSpot
