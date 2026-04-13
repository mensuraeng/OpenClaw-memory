# Automações Microsoft Graph

_Atualizado em 2026-04-13_

- **Status:** base operacional ativa
- **Próximo passo:** usar flavia@mensuraengenharia.com.br como remetente nos scripts de automação
- **Bloqueios:** nenhum

## Ajuste recente
- Corrigido bug nos scripts `msgraph_email.py` e `msgraph_calendar.py`: o usuário padrão estava hardcoded como `alexandre@mensuraengenharia.com.br`.
- Agora cada conta usa `defaultUser` do respectivo JSON de configuração, com `--user` opcional para override.
- Os scripts também passaram a falhar explicitamente quando `defaultUser` não existir, em vez de cair para fallback silencioso.
- `config/ms-graph.json` recebeu `defaultUser` da Mensura para padronizar o comportamento entre contas.
- Validação concluída em Mensura e MIA: email e calendário responderam corretamente após o ajuste.

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
