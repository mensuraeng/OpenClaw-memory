---
name: mia-finance
description: Ferramentas de análise financeira para PCS Engenharia, MENSURA Engenharia, MIA Engenharia e finanças pessoais. Conecta ao PostgreSQL mia_finance, scripts em /root/.openclaw/mia-finance/. Use para análises de caixa, margem, forecast, importação de extratos. Ativa em pedidos como "analisa finanças", "importa extrato", "fluxo de caixa", "margem por projeto", "relatório financeiro".
---

# MIA Finance Tools — Financial Analysis

Ferramentas integradas de análise financeira para as empresas do Alexandre Aguiar.

## Configuração

- **Scripts:** `/root/.openclaw/mia-finance/`
- **DB:** PostgreSQL `mia_finance` (via container firecrawl-postgres, porta 5432)
- **Workspace finance:** `/root/.openclaw/workspace/finance/`
- **Heartbeat:** agente `finance` configurado com 30m

## Scripts disponíveis

| Script | Uso |
|--------|-----|
| `ingest.py` | Importar dados financeiros (extratos, lançamentos) |
| `xp_export_automation.js` | Automatizar exportação da XP Investimentos |

## Banco de dados

```bash
# Conectar ao banco mia_finance
docker exec firecrawl-postgres psql -U firecrawl -d mia_finance
```

## Entidades financeiras

```
PCS Engenharia   → caixa operacional, contratos, capital de giro
MENSURA          → margem consultiva, previsibilidade de receita
MIA Engenharia   → margem premium por projeto, custo de atendimento
Alexandre pessoal → liquidez, investimentos, caixa pessoal
```

## Quando usar

- Importar extratos bancários e de cartão
- Analisar fluxo de caixa por empresa
- Calcular margem por contrato/projeto
- Forecast financeiro mensal/trimestral
- Conciliar lançamentos

## Exemplos

```bash
# Ingest de dados
cd /root/.openclaw/mia-finance
python3 ingest.py --source extrato.csv --entity pcs

# Query manual
docker exec firecrawl-postgres psql -U firecrawl -d mia_finance \
  -c "SELECT * FROM lancamentos WHERE empresa='PCS' ORDER BY data DESC LIMIT 10;"

# Automação XP
node xp_export_automation.js
```

## Boas práticas

- Validar totais após ingestão (conciliar com extrato original)
- Separar claramente lançamentos por entidade
- Para análises críticas, usar skill `cfo-finance-adapter` para contextualizar
- Manter backup do banco antes de operações de ingestão em massa
