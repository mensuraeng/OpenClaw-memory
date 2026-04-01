# Monitor Semanal + Cronogramas

_Atualizado em 2026-04-01_

- **Status:** ativo
- **Próximo passo:** adicionar novas obras conforme iniciarem
- **Bloqueios:** nenhum

## O que monitora
1. **Emails urgentes** — palavras: atraso, urgente, pendente, relatório, pleito (Mensura + MIA)
2. **Agenda da semana** — próximos 7 dias (Mensura + MIA)
3. **Cronogramas .mpp** — SharePoint, obras ativas

## Obras monitoradas
| Obra | Empresa | SharePoint Site | Última atualização |
|------|---------|----------------|-------------------|
| P&G Louveira | Mensura | SUMEngenhariaPGLouveira | 1 dia (2026-03-30) |
| CCSP Casa 3 | MIA | CCSP-CasaCapela3 | 5 dias (2026-03-26) |

## Regra de alerta
- > 10 dias sem atualização → 🔴 OBRA ENCERRADA?
- > 7 dias → ⚠️ atraso de controle
- ≤ 7 dias → ✅ ok

## Cron
`0 11 * * 1` → toda segunda 11h UTC (8h BRT)
