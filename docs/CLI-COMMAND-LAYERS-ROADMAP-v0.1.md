# CLI Command Layers — Roadmap v0.1

_Atualizado em 2026-04-26_

## Objetivo

Transformar fluxos operacionais repetíveis em CLIs internas **agent-native**, para reduzir improviso, padronizar validação e permitir que agentes operem sistemas por comandos previsíveis.

Regra central: CLI é camada de operação estruturada. Não é autorização para side effect externo.

## Padrão obrigatório

Toda CLI nova deve ter:

- `status` ou `health`;
- `validate` quando houver dados estruturados;
- saída humana e `--json` nos comandos principais;
- logs claros quando houver execução longa;
- `--dry-run` para qualquer comando que possa mudar estado;
- guardrails explícitos;
- nenhuma credencial impressa;
- nenhuma mensagem externa sem confirmação/fluxo aprovado;
- nenhuma deleção, pagamento, publicação, upload crítico ou alteração irreversível sem confirmação explícita.

## CLIs já implantadas

### 1. `mensura-schedule`

Local:
- `/root/.openclaw/workspace/projects/mensura-schedule-control/bin/mensura-schedule`

Domínio:
- cronogramas SharePoint/Excel;
- Supabase Mensura Schedule Control;
- analytics de caminho crítico.

Estado:
- implantada e validada.

Próximos comandos úteis:
- `quality-report` — qualidade dos dados importados;
- `baseline-compare` — baseline x atual;
- `weekly-metrics build` — popular `analytics.project_weekly_metrics`;
- `risk-ranking` — WBS/frente por risco;
- `audit-orphans` — listar `raw.import_jobs` órfãos;
- `cleanup-orphans --dry-run` — somente simular limpeza; execução real exige autorização.

### 2. `trade`

Local:
- `/root/.openclaw/workspace/projects/trade/bin/trade`

Domínio:
- Market Radar;
- Gold Monitor;
- News Radar checklist;
- Supabase Trade;
- relatórios read-only.

Estado:
- implantada e validada.

Próximos comandos úteis:
- `news-radar run --dry-run` — runner durável sem depender só do agente;
- `portfolio ingest-xp-export --dry-run` — importação manual XP;
- `portfolio status`;
- `macro bcb`;
- `tesouro snapshot`;
- `wealth report`;
- `prediction baseline`.

Guardrail permanente:
- sem compra, venda, ordem, corretora, resgate ou aplicação automática.

### 3. `finance`

Local:
- `/root/.openclaw/workspace/finance/bin/finance`

Domínio:
- contas a pagar;
- relatórios financeiros locais;
- validação de `memory/contas_pagar.json`.

Estado:
- implantada e validada como read-only.

Próximos comandos úteis:
- `scan-emails --dry-run` — encapsular leitura de emails sem criar agenda por padrão;
- `dedupe-contas --dry-run` — detectar duplicidades;
- `classify-false-positives`;
- `cashflow forecast`;
- `cost tokens`;
- `actual status` — integração com Actual Budget;
- `fiscal inventory` — integração br-docs-fiscais;
- `fiscal reconcile --dry-run`.

Guardrail permanente:
- sem pagamento, PIX, transferência, baixa, agenda ou envio externo por padrão.

## Próximas CLIs prioritárias

### P0 — `ops` ou `openclaw-ops`

Por quê:
- há muitos fluxos recorrentes de saúde, crons, custo, backups, limpeza, memory health e task health;
- parte dos crons falha por harness/config ou timeout;
- hoje a operação está espalhada em scripts e payloads de cron.

Fontes atuais:
- `scripts/cost_report.py`;
- `scripts/backup_workspace.sh`;
- `scripts/backup_before_change.sh`;
- `scripts/restore_openclaw_backup.sh`;
- `scripts/msgraph_healthcheck.py`;
- `projects/mission-control/scripts/collect-usage.ts`;
- crons `task-health`, `cost:guard-daily`, `security:audit-daily`, `vps-limpeza-diaria`, `notion-sync-nightly`, `notebooklm-nightly-sync`.

Comandos propostos:
- `ops health` — doctor, gateway, canais, memory_search, msgraph, supabase refs conhecidos;
- `ops crons status` — listar jobs, erros consecutivos, delivery quebrado, harness inválido;
- `ops crons report --json`;
- `ops cost daily --json`;
- `ops backup status`;
- `ops backup run --dry-run` / `ops backup run` com confirmação;
- `ops cleanup --dry-run`;
- `ops tasks audit`;
- `ops memory-health`.

Risco:
- alto se permitir restart/update/delete. v0.1 deve ser diagnóstico/read-only, exceto `backup run` com confirmação explícita.

### P1 — `msgraph`

Por quê:
- email, calendário e saúde Microsoft Graph são base de vários fluxos;
- scripts atuais existem, mas estão separados e alguns têm side effects;
- agentes precisam consultar inbox/agenda de forma uniforme e segura.

Fontes atuais:
- `scripts/msgraph_email.py`;
- `scripts/msgraph_calendar.py`;
- `scripts/msgraph_healthcheck.py`;
- `scripts/contas_pagar.py`;
- `scripts/monitor_semanal.py`;
- `scripts/ccsp_*`.

Comandos propostos:
- `msgraph health`;
- `msgraph inbox list --account ... --since ... --json`;
- `msgraph inbox search --query ...`;
- `msgraph calendar today --account ...`;
- `msgraph calendar upcoming --days N`;
- `msgraph attachments list/download --dry-run`;
- `msgraph send` deve ficar bloqueado no v0.1 ou exigir aprovação explícita.

Risco:
- alto por email/calendário. v0.1 deve ser read-only.

### P1 — `commercial` / `mensura-commercial`

Por quê:
- há rotinas de marketing/comercial Mensura e LinkedIn;
- hoje estão em scripts e crons dispersos;
- publicação externa é sensível e precisa preview/approval.

Fontes atuais:
- `scripts/monitoramento_comercial_mensura.py`;
- `scripts/operacional_marketing_mensura.py`;
- `scripts/revisao_tecnica_mensura.py`;
- `projects/openclaw-linkedin/scripts/*`;
- crons de LinkedIn pessoal terça/quinta;
- Mission Control GA4/analytics.

Comandos propostos:
- `commercial status`;
- `commercial pipeline report`;
- `commercial linkedin preview --text file.md`;
- `commercial linkedin auth-status`;
- `commercial linkedin publish --dry-run`;
- `commercial ga4 summary`;
- `commercial campaign checklist`.

Guardrail:
- publicação externa sempre preview + aprovação humana, salvo exceção formal já documentada.

### P1 — `pcs-licita`

Por quê:
- licitações e prazos são recorrentes e críticos;
- PCS depende de previsibilidade documental;
- PNCP, email e certidões precisam rotina rastreável.

Fontes atuais:
- `scripts/monitor_licitacoes.py`;
- `scripts/licitacoes_email.py`;
- crons `pcs-prazos-diario`, `pcs-restauro-licencas`, `pcs-status-semanal`.

Comandos propostos:
- `pcs-licita search --query ... --uf ... --json`;
- `pcs-licita monitor --dry-run`;
- `pcs-licita deadlines`;
- `pcs-licita certidoes`;
- `pcs-licita report weekly`;
- `pcs-licita email-draft`.

Guardrail:
- nunca enviar email/proposta automaticamente.

### P2 — `mia-obra`

Por quê:
- MIA tem CCSP Casa 7 e relatórios semanais com fluxo específico;
- risco de mistura entre alinhamento operacional e status executivo já foi identificado.

Fontes atuais:
- `scripts/ccsp_relatorio_semanal.py`;
- `scripts/ccsp_manha_victor.py`;
- `scripts/ccsp_rdo_cobranca.py`;
- `scripts/ccsp_status_guard.py`.

Comandos propostos:
- `mia-obra ccsp status-guard`;
- `mia-obra ccsp weekly-payload`;
- `mia-obra ccsp rdo-check`;
- `mia-obra ccsp draft-message`;
- `mia-obra report validate`.

Guardrail:
- comunicação externa com cliente/proprietário passa por validação da Flávia/Alê.

### P2 — `knowledge`

Por quê:
- docling, RAG, Notion sync, NotebookLM e 2nd-brain são infraestrutura de memória;
- há muitos scripts com funções parecidas.

Fontes atuais:
- `scripts/docling_converter.py`;
- `scripts/docling_ingest.py`;
- `scripts/rag_query.py`;
- `scripts/notion_sync.py`;
- `scripts/nblm_sync.py`;
- `scripts/sync_knowledge.py`;
- projeto `openclaw-memory`.

Comandos propostos:
- `knowledge ingest --dry-run`;
- `knowledge docling convert`;
- `knowledge rag query`;
- `knowledge notion sync --dry-run`;
- `knowledge notebooklm status`;
- `knowledge memory consolidate --dry-run`;
- `knowledge diff daily`.

Guardrail:
- não promover memória automaticamente sem regras de destino; não versionar segredo.

### P2 — `sienge`

Por quê:
- integração Sienge envolve upload e orçamento, com alto risco operacional;
- precisa guardrail forte antes de virar CLI.

Fontes atuais:
- `scripts/sienge_upload_orcamento_teatro_suzano.py`;
- `scripts/sienge_monitor_lock_teatro.py`;
- `projects/pcs-sienge-integration/scripts/upload_budget.py`;
- `projects/pcs-sienge-integration/scripts/upload_budget_teatro.py`.

Comandos propostos:
- `sienge status`;
- `sienge budget validate`;
- `sienge budget diff`;
- `sienge upload --dry-run`;
- `sienge monitor-lock`.

Guardrail:
- upload real exige confirmação explícita e backup/rollback do payload.

### P3 — `reports`

Por quê:
- vários relatórios existem, mas cada um com padrão diferente;
- pode virar CLI agregadora, mas só depois dos domínios P0/P1.

Fontes atuais:
- `scripts/gerar_relatorio.py`;
- `scripts/relatorio_analytics.py`;
- `scripts/relatorio_cursos.py`;
- `scripts/relatorio_cursos_telegram.py`;
- `scripts/send_relatorio_cursos.sh`.

Comandos propostos:
- `reports list`;
- `reports build <tipo>`;
- `reports preview <arquivo>`;
- `reports deliver --dry-run`.

Guardrail:
- entrega externa sempre bloqueada por padrão.

## Fluxos que NÃO devem virar CLI agora

### Capability Evolver / core skills

Motivo:
- baixo acoplamento direto com rotina operacional do Alê;
- risco de mexer em mecanismo interno demais;
- melhor tratar como subsistema do OpenClaw, não CLI operacional de negócio.

### Scripts de teste/scaffold de skills

Motivo:
- utilidade pontual;
- não há rotina repetível nem dado sensível operacional.

### Publicação externa direta isolada

Exemplos:
- `instagram_post.py`;
- `linkedin_post.py`;
- YouTube upload.

Motivo:
- publicação é externa e reputacional;
- só devem entrar como subcomandos com preview/dry-run/aprovação, nunca como execução solta.

## Ordem recomendada de implementação

1. `ops` — primeiro, porque estabiliza a própria operação e os crons.
2. `msgraph` — base segura para email/agenda/anexos.
3. Expandir `finance` — scanner dry-run, dedupe e fiscal/Actual Budget.
4. Expandir `mensura-schedule` — analytics e forecast.
5. `commercial` — marketing/LinkedIn/GA4 com preview.
6. `pcs-licita` — licitações, prazos, certidões.
7. `mia-obra` — CCSP e relatórios MIA.
8. `knowledge` — Notion/Docling/RAG/NotebookLM.
9. `sienge` — só depois de especificar rollback e autorização.
10. `reports` — agregadora final.

## Decisão de arquitetura

Adotar CLIs por domínio, não uma CLI monolítica única.

Motivo:
- domínios têm riscos diferentes;
- facilita permissão por agente;
- evita que uma CLI ganhe poderes demais;
- melhora teste e auditoria.

Padrão de localização:

- Projeto próprio existente: `projects/<dominio>/bin/<cli>`;
- Workspace de agente existente: `<workspace-agente>/bin/<cli>`;
- Fluxo transversal: `projects/ops-cli/` ou `projects/openclaw-ops/`.

## Pendências abertas

- Definir nome final da CLI operacional: `ops`, `flavia-ops` ou `openclaw-ops`.
- Decidir se `msgraph` fica como CLI própria ou módulo dentro de `ops`.
- Mapear quais crons quebrados devem ser migrados para CLI antes de corrigir o cron.
- Criar matriz de permissões por CLI/agente.
