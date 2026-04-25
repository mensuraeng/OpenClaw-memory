# Mapa — Área Operação

_Atualizado: 2026-04-25_

## Propósito
Obras em execução, RDOs, MAPs, cronogramas, fornecedores e controle de campo.

## Obras em andamento
| Obra | Status | Prazo | Referência |
|---|---|---|---|
| **CCSP Casa 7** | 59% (24/04) | 22/05/2026 | `memory/obras/ccsp-casa7/` |

## Automações
| Cron | Horário | Script |
|---|---|---|
| Check matinal Victor | 08:00 seg-sex | `scripts/ccsp_manha_victor.py` |
| Cobrança RDO | 13:30 seg-sex | `scripts/ccsp_rdo_cobranca.py` |
| Relatório semanal | Segunda | `scripts/ccsp_relatorio_semanal.py` |

## Contatos chave (CCSP Casa 7)
- **Victor Evangelista** — RDOs e MAPs diários
- **Felipe Oliveira** (Tools) — aprovação MAPs
- **Gustavo Brancato** (Tools) — visitas de obra
