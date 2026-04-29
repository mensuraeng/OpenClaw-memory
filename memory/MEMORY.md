# MEMORY — Flávia

_Atualizado em 2026-04-28 22:00 BRT_

## Estado operacional
- Sistema Operacional 10/10 em implantação: WORKING, health unificado, usage ledger, backlog leve, pipeline de dados e AGENT-MAPs dos agentes principais alinhados.
- Monitor executivo de e-mails 7h/14h cobre Mensura + MIA + PCS; PCS Graph foi destravado e validado sem `Mail.Send`.
- Diretriz de comunicação: direct do Alê recebe só retorno gerencial, bloqueio, risco, decisão ou entrega relevante; operação granular fica nos canais/agentes de domínio.

## Riscos / bloqueios ativos
- Segredos ainda precisam saneamento: token LinkedIn em plaintext e migração gradual para KeeSpace.
- Backup full VPS B2: cap resolvido e dry-run OK; falta validar execução final, manifesto e restaurabilidade.
- LinkedIn institucional depende de aprovação da Community Management API na app dedicada `OpenClaw - Community API` (`77ke3c00urrpdv`).
- Meta Ads está preparado para campanha futura, mas depende de conta de anúncios vinculada e credenciais read-only seguras.

## Prioridades curadas
1. Segurança: SSH key VPS, segredos expostos, KeeSpace e token LinkedIn.
2. Continuidade operacional: backup full VPS B2 com prova de restauração.
3. Governança 10/10: health, WORKING, usage ledger e backlog leve com validação real.
4. Receita/marketing: campanha MENSURA só com base higienizada; Meta Ads somente diagnóstico/read-only até aprovação.

## Localizações-chave
- Pendências executivas: `memory/context/pending.md`
- Decisões permanentes: `memory/context/decisions.md`
- Lições: `memory/context/lessons.md`
- Diário consolidado de hoje: `memory/2026-04-28.md`
- 2nd-brain operacional Flávia: `/root/2nd-brain/06-agents/flavia/`
