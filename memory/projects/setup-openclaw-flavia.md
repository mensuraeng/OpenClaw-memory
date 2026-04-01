# Setup OpenClaw + Flávia (VPS)

_Atualizado em 2026-04-01_

- **Status:** em andamento
- **Próximo passo:** configurar LinkedIn e Instagram
- **Bloqueios:**
  - LinkedIn: aguardando Client ID + Secret (app "James OpenClaw" criado no LinkedIn Developer)
  - Instagram: aguardando Meta Developer app (não iniciado)
  - OpenAI API key: Whisper + embeddings — no backlog
  - SSH hardening: confirmar chave SSH antes de `PermitRootLogin prohibit-password`

## Concluído neste projeto
- Gateway systemd ativo 24/7 (porta 18789)
- Security hardening: UFW, Fail2ban, dmPolicy=allowlist
- Identidade Flávia: SOUL.md, USER.md, IDENTITY.md, AGENTS.md, MEMORY.md
- Email próprio: flavia@mensuraengenharia.com.br
- Compaction + memory flush configurados
- Session init otimizado: boot ~8KB, resto via memory_search()
- Estrutura de memória com subpastas migrada
