# Classificação de risco dos crons

_Atualizado em 2026-04-14_

## Regra operacional

O watchdog e qualquer rotina automática de supervisão **não podem** reexecutar cegamente jobs com side effect externo.

Classificação padrão:
- `read_only` → só leitura/inspeção, sem envio externo, sem mutação crítica
- `internal_mutation` → altera estado interno, arquivos, memória, config leve ou manutenção local
- `external_side_effect` → envia mensagem, email, webhook, postagem, update, ação operacional externa ou execução ambígua com efeito fora da leitura

## Política de retry

- `read_only` → retry automático pode ser considerado, se a falha parecer transitória e segura
- `internal_mutation` → sem retry cego por padrão, só com critério explícito e baixo risco
- `external_side_effect` → **nunca retry cego**

## Inventário atual

| Job | Classificação | Motivo | Retry automático |
|---|---|---|---|
| Monitor Semanal — segunda 8h BRT | external_side_effect | Consolida e envia via Telegram | NÃO |
| Relatório de Cursos — sexta 16h BRT | external_side_effect | Envia via Telegram | NÃO |
| CCSP Casa 7 — Relatório 9h BRT | external_side_effect | Envia Telegram + email | NÃO |
| CCSP Casa 7 — Relatório 16:30 BRT | external_side_effect | Envia Telegram + email | NÃO |
| Daily Briefing \| General | external_side_effect | Entrega em canal Telegram | NÃO |
| Review e Carry \| General | external_side_effect | Entrega em canal Telegram | NÃO |
| mensura-autopilot-daily-8h-draft | external_side_effect | Entrega rascunho por Telegram | NÃO |
| clawflows-scheduler | internal_mutation | Executa scheduler interno e pode disparar workflows | NÃO |
| heartbeat:briefing-semanal | external_side_effect | Anúncio ao usuário | NÃO |
| heartbeat:pulso-matinal | external_side_effect | Anúncio ao usuário | NÃO |
| heartbeat:check-tatico | external_side_effect | Anúncio ao usuário | NÃO |
| heartbeat:fechamento-tatico | external_side_effect | Anúncio ao usuário | NÃO |
| heartbeat:retrospectiva-semanal | external_side_effect | Anúncio ao usuário | NÃO |
| flavia:manutencao-memoria-22h | internal_mutation | Consolida memória e arquivos internos | NÃO |
| flavia:healthcheck-operacional-06h | read_only | Doctor, health checks e inspeção | PODE, com critério |
| flavia:revisao-estrategica-semanal | read_only | Observação e síntese sem ação externa por padrão | PODE, com critério |
| selfupdate:openclaw-core | external_side_effect | Auto-update + restart | NÃO |
| healthcheck:security-audit | read_only | Auditoria/inspeção, job hoje desabilitado | PODE, com critério |
| skills:provenance-audit | external_side_effect | Anúncio em Telegram | NÃO |
| Watchdog - Monitor de Crons | read_only | Supervisão; não deve reexecutar jobs externos | PODE, com critério restrito |
| Security Audit - Semanal | external_side_effect | Auditoria com anúncio ao canal | NÃO |
| backup-workspace-git-diario | internal_mutation | Backup/commit local | NÃO |
| cost:guard-daily | external_side_effect | Alerta em Telegram quando limiar estoura | NÃO |
| cobranca-rdo | external_side_effect | Cobrança operacional | NÃO |

## Regra prática para o watchdog

Se houver dúvida entre categorias, tratar como `external_side_effect`.

Ou seja:
- dúvida = não retentar
- envio externo = não retentar
- delivery ambíguo = não retentar
- update/restart = não retentar
- mutação interna relevante = não retentar por padrão

Retry automático deve ficar restrito a jobs nitidamente de leitura, diagnóstico ou auditoria silenciosa.
