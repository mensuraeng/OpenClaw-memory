# MEMORY — Flávia

_Atualizado em 2026-04-29 22:00 BRT_

## Estado operacional
- Sistema Operacional 10/10 em implantação: WORKING, health unificado, usage ledger, backlog leve, pipeline de dados e AGENT-MAPs dos agentes principais alinhados.
- Mission Control `/cron` ganhou edição interna de crons pelo dashboard; build validado e rota externa protegida por login.
- Monitor executivo de e-mails 7h/14h cobre Mensura + MIA + PCS; PCS Graph foi destravado e validado sem `Mail.Send`.
- Diretriz de comunicação: direct do Alê recebe só retorno gerencial, bloqueio, risco, decisão ou entrega relevante; operação granular fica nos canais/agentes de domínio.
- Make.com integrado em modo controlado; leitura validada e execução de cenário continua exigindo aprovação quando houver side effect externo.
- LLM Context Pack implantado como helper interno para reduzir contexto em subagentes/auditorias sem substituir fonte de verdade.

## Riscos / bloqueios ativos
- Segredos ainda precisam saneamento: token LinkedIn em plaintext e migração gradual para KeeSpace.
- Backup full VPS B2: cap resolvido e dry-run OK; falta validar execução final, manifesto e restaurabilidade.
- LinkedIn institucional depende de aprovação da Community Management API na app dedicada `OpenClaw - Community API` (`77ke3c00urrpdv`).
- Meta Ads está preparado para campanha futura, mas depende de conta de anúncios vinculada e credenciais read-only seguras.
- Frente fiscal aberta: antes de qualquer emissão real, confirmar por empresa se é NFS-e, NF-e ou ambas, certificado, aprovador e destino PDF/XML.

## Prioridades curadas
1. Segurança: SSH key VPS, segredos expostos, KeeSpace e token LinkedIn.
2. Continuidade operacional: backup full VPS B2 com prova de restauração.
3. Governança 10/10: health, WORKING, usage ledger, backlog leve e Mission Control com validação real.
4. Fiscal: mapear escopo de emissão por empresa antes de automatizar qualquer transmissão.
5. Receita/marketing: campanha MENSURA só com base higienizada; Meta Ads somente diagnóstico/read-only até aprovação.

## Localizações-chave
- Pendências executivas: `memory/context/pending.md`
- Decisões permanentes: `memory/context/decisions.md`
- Lições: `memory/context/lessons.md`
- Diário consolidado de hoje: `memory/2026-04-29.md`
- 2nd-brain operacional Flávia: `/root/2nd-brain/06-agents/flavia/`
