# Projetos

_Atualizado em 2026-04-01_

## 🚀 Ativos

### Setup OpenClaw + Flávia (VPS)
- **Status:** em andamento
- **Próximo passo:** receber templates de lessons.md, decisions.md, pending.md; configurar LinkedIn e Instagram
- **Bloqueios:** LinkedIn (aguardando Client ID + Secret); Instagram (aguardando Meta Developer app); OpenAI API key (Whisper + embeddings)

### Automações Microsoft Graph
- **Status:** em andamento — base operacional pronta
- **Próximo passo:** envio de emails em nome da Flávia; configurar email flavia@mensuraengenharia.com.br como remetente nos scripts
- **Bloqueios:** nenhum

### Monitor Semanal (toda segunda 8h BRT)
- **Status:** ativo
- **Cobre:** emails urgentes (Mensura + MIA), agenda semanal, cronogramas de obra (.mpp)
- **Próximo passo:** nenhum — funcionando

### Relatório de Cursos (toda sexta 16h BRT)
- **Status:** ativo
- **Cobre:** cursos curtos, workshops, certificações, eventos de construção civil
- **Próximo passo:** nenhum — funcionando

### Monitoramento de Cronogramas SharePoint
- **Status:** ativo
- **Obras:** P&G Louveira (Mensura), CCSP Casa 3 (MIA)
- **Regra:** >10 dias sem atualização → alerta 🔴 OBRA ENCERRADA?
- **Próximo passo:** adicionar novas obras conforme iniciarem

## ✅ Concluídos

- **Gateway VPS** — 2026-04-01 — gateway systemd ativo 24/7 na porta 18789
- **Security hardening** — 2026-04-01 — UFW ativo, Fail2ban ativo, dmPolicy=allowlist
- **Microsoft Graph Mensura** — 2026-04-01 — email + calendário + SharePoint conectados
- **Microsoft Graph MIA** — 2026-04-01 — email + calendário + SharePoint conectados
- **Identidade Flávia** — 2026-04-01 — SOUL.md, USER.md, IDENTITY.md, AGENTS.md criados
- **Email flavia@mensuraengenharia.com.br** — 2026-04-01 — conta criada e acessível via Graph
- **ATHIE WPP removida do monitoramento** — 2026-04-01 — obra encerrada (187 dias sem atualização)

## 💡 Backlog

- LinkedIn integration (app "James OpenClaw" criado, aguardando Client ID + Secret)
- Instagram integration (aguardando Meta Developer app)
- OpenAI API key (Whisper para áudio + embeddings para memory_search)
- SSH hardening (PermitRootLogin → prohibit-password, confirmar que Alê tem chave SSH)
- Cloudflare Tunnel (opcional — para expor web apps)
- Email próprio da Flávia como remetente nos scripts de automação
