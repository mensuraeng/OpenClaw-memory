# Automações Microsoft Graph

_Atualizado em 2026-04-01_

- **Status:** base operacional ativa
- **Próximo passo:** usar flavia@mensuraengenharia.com.br como remetente nos scripts de automação
- **Bloqueios:** nenhum

## Integrações ativas
- Email Mensura (`alexandre@mensuraengenharia.com.br`) — ✅
- Email MIA (`alexandre@miaengenharia.com.br`) — ✅
- Email Flávia (`flavia@mensuraengenharia.com.br`) — ✅
- Calendário Mensura + MIA — ✅
- SharePoint Mensura + MIA — ✅

## Scripts
- `scripts/msgraph_email.py` — listar, ler, mover emails
- `scripts/msgraph_calendar.py` — listar, criar, deletar eventos
- `scripts/monitor_semanal.py` — monitor toda segunda 8h BRT
- `scripts/relatorio_cursos_telegram.py` — relatório toda sexta 16h BRT

## Config
- Mensura: `config/ms-graph.json`
- MIA: `config/ms-graph-mia.json`
- Flávia identity: `config/flavia-identity.json`
