# Mapa — Área Financeiro

_Atualizado: 2026-04-25_

## Propósito
Contas a pagar, fluxo de caixa, relatórios financeiros e governança do ecossistema (MENSURA, MIA, PCS, pessoal).

## Referências
| Recurso | Onde |
|---|---|
| Contas a pagar | `memory/contas_pagar.json` |
| Decisões financeiras | `memory/context/decisions.md` |

## Automações
| Cron | Horário | Script |
|---|---|---|
| Relatório contas a pagar | 10:00 segunda | `scripts/contas_pagar_telegram.py` |
| Licitações | 09:00 segunda | `scripts/licitacoes_email.py` |
| Monitor semanal | 08:10 segunda | `scripts/monitor_semanal.py` |
| Relatório cursos | 13:00 sexta | `scripts/relatorio_cursos_telegram.py` |

## Canal Telegram
Grupo Finance · tópico 13 · agente `finance` ativo

## Regras
- Fatura Itaú: vence dia 27 — alertar com 5 dias de antecedência
- Relatório de contas gerado automaticamente toda segunda
