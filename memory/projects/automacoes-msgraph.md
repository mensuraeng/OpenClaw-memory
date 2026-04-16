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
- Email PCS (`alexandre@pcsengenharia.com.br`) — ✅
- Email Flávia (`flavia@mensuraengenharia.com.br`) — ✅
- Calendário Mensura + MIA + PCS — ✅
- SharePoint Mensura + MIA — ✅

## Scripts
- `scripts/msgraph_email.py` — listar, ler, mover emails
- `scripts/msgraph_calendar.py` — listar, criar, deletar eventos
- `scripts/msgraph_healthcheck.py` — valida email e calendário de Mensura, MIA e caixa da Flávia
- `scripts/monitor_semanal.py` — monitor toda segunda 8h BRT
- `scripts/relatorio_cursos_telegram.py` — relatório toda sexta 16h BRT

## Healthcheck operacional
- Script criado para detectar quebra de token, resolução de usuário e acesso a inbox/calendário antes de impactar a rotina.
- Cobertura atual: Mensura email, Mensura calendário, MIA email, MIA calendário e inbox da Flávia.
- Saída é resumida e com exit code 1 em caso de falha, pronta para cron ou monitoramento posterior.
- Validação manual executada em 2026-04-13 com todos os checks em `OK`.

## Config
- Mensura: `config/ms-graph.json`
- MIA: `config/ms-graph-mia.json`
- PCS: `config/ms-graph-pcs.json`
- Flávia identity: `config/flavia-identity.json`

## PCS habilitado em 2026-04-16
- Criado `config/ms-graph-pcs.json` com `defaultUser=alexandre@pcsengenharia.com.br`.
- `scripts/msgraph_email.py` e `scripts/msgraph_calendar.py` passaram a aceitar `--account pcs`.
- Validação concluída com sucesso:
  - inbox PCS respondeu normalmente
  - calendário PCS respondeu normalmente
- Evidência operacional relevante da inbox:
  - email de `dyonisiojpf@spobras.sp.gov.br` com assunto `ENC: INSTALAÇÃO ELÉTRICA`, incluindo uma ocorrência marcada como urgente em 15/04/2026.
