# Mapa de Crons — Ecossistema OpenClaw/Flávia

_Atualizado: 2026-04-25 | Consultar antes de criar/editar automações_

---

## Visão geral por horário (BRT)

| Horário BRT | Frequência | Script / Tarefa | Propósito |
|---|---|---|---|
| 00:00 | Cada 2h (par) | `sync-2nd-brain.sh` | Sincroniza 2nd Brain com GitHub |
| 01:00 | Diário | `nightly_consolidate.py` (openclaw-memory) | Consolida memória noturna |
| 03:00 | Domingo | `cleanup.sh` | Limpeza semanal do servidor |
| 05:00 | Diário | `inbox_triage.py` (PCS) | Triagem de inbox PCS (50 emails) |
| 07:00 | Seg-sex | `sync_knowledge.py` | Sincronização de base de conhecimento |
| 08:00 | Seg-sex | `monitoramento_comercial_mensura.py` | **Relatório CFO — Máquina de Vendas MENSURA** (HTML → Telegram MKT) |
| 08:10 | Segunda | `monitor_semanal.py` | Monitor semanal geral |
| 08:30 | Seg + Qui | `revisao_tecnica_mensura.py` | Revisão técnico-comercial MENSURA → prompt agente |
| 08:00 | Seg-sex | `ccsp_manha_victor.py` | Check matinal CCSP Casa 7 / Victor |
| 09:00 | Segunda | `licitacoes_email.py` | Verificação de licitações — email |
| 10:00 | Segunda | `contas_pagar_telegram.py` | Relatório contas a pagar → Telegram |
| 09:00 | Seg-sex | `operacional_marketing_mensura.py` | Prompt operacional → agente Marketing |
| 13:00 | Sexta | `relatorio_cursos_telegram.py` | Relatório de cursos → Telegram |
| 13:30 | Seg-sex | `ccsp_rdo_cobranca.py` | Cobrança RDO CCSP → Victor |
| 18:50 | Diário | `compact-daily-memory.sh` | Compacta memória diária |
| 19:00 | Diário | `nightly_consolidate.py` (workspace) | Consolidação noturna do workspace |
| 19:30 | Diário | git commit memory snapshot | Auto-commit memória diária |
| Cada hora | Cada hora | `monitor_steal.sh` | Monitor de segurança do servidor |
| 12/14/16/18/20/22/00/02h UTC | 8x/dia | `openclaw-git-sync.sh` | Sync GitHub do OpenClaw |

---

## Agrupamento por função

### Comercial MENSURA
| Cron | Horário | Destino |
|---|---|---|
| Monitoramento comercial (HubSpot + Phantombuster) | 08:00 seg-sex | Telegram grupo Mensura, tópico MKT (thread 43) |
| Operação Marketing (prompt agente) | 09:00 seg-sex | Agente Marketing |
| Revisão técnico-comercial | 08:30 seg+qui | Agente MENSURA |

### Obras (CCSP Casa 7)
| Cron | Horário | Destino |
|---|---|---|
| Check matinal Victor | 08:00 seg-sex | Telegram |
| Cobrança RDO | 13:30 seg-sex | Telegram |
| Monitor semanal | 08:10 segunda | Log |

### Financeiro / Administrativo
| Cron | Horário | Destino |
|---|---|---|
| Contas a pagar | 10:00 segunda | Telegram |
| Licitações | 09:00 segunda | Email |
| Relatório cursos | 13:00 sexta | Telegram |

### Memória / Infraestrutura
| Cron | Horário | Ação |
|---|---|---|
| Sync 2nd Brain | Cada 2h | Push GitHub `mensuraeng/OpenClaw-memory` |
| Git sync OpenClaw | 8x/dia | Push OpenClaw state |
| Nightly consolidate | 19:00 + 01:00 | Consolida memória operacional |
| Compact daily memory | 18:50 | Compacta diários |
| Cleanup | Domingo 03:00 | Limpeza de logs/temp |
| Monitor steal | Cada hora | Segurança do servidor |

---

## Regras
- Todos os scripts estão em `/root/.openclaw/workspace/scripts/`
- Logs em `/root/.openclaw/workspace/logs/cron/` ou `/tmp/`
- Skip automático de feriados: apenas `monitoramento_comercial_mensura.py`
- Para adicionar cron novo: usar `crontab -e`, sempre com horário em UTC
- BRT = UTC-3 (horário de Brasília padrão; sem horário de verão desde 2019)
