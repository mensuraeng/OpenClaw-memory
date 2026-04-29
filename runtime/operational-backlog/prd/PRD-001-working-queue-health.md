# PRD-001 — Working Queue + Operational Health

- ID: PRD-001
- Data: 2026-04-28
- Owner: Flávia
- Domínio: arquitetura / openclaw
- Prioridade: alta
- Status: em execução

## Problema

O ecossistema OpenClaw já possui crons, memória, integrações e agentes, mas parte da operação ainda depende de comandos manuais e não há uma fila viva padronizada nem um health unificado com evidência.

## Evidência

- Existem crons e monitores reais, mas espalhados.
- Monitor executivo de e-mail funciona, mas era isolado.
- Backup B2, LinkedIn, Meta Ads e campanha MENSURA tinham estados em arquivos diferentes.
- Subagentes de auditoria falharam quando acionados em paralelo, reforçando necessidade de escopo menor e observabilidade.

## Impacto

Sem fila e health unificados, o sistema parece proativo, mas pode virar apenas um conjunto de relatórios soltos.

## Solução proposta

Implantar:
1. `WORKING.md` como fila operacional viva.
2. Matriz de autoridade por integração.
3. Regras de dados e confiança.
4. Operating loops.
5. `scripts/operational_health.py` com JSON read-only.
6. Crons para revisão de working queue e health.

## Escopo

- Flávia/main primeiro.
- Read-only/baixo risco.
- Sem publicação externa, alteração de ERP, campanha, e-mail ou dados críticos.

## Fora de escopo

- Dashboard visual.
- Migração completa para KeeSpace.
- Automação write em HubSpot/Sienge/Meta Ads.
- Subagente com merge/deploy autônomo.

## Critérios de aceite

- WORKING criado com tarefas ativas reais.
- Health unificado gera `runtime/operational-health/latest.json`.
- Cron de revisão da fila ativo.
- Cron de health ativo.
- Matriz de autoridade e regras de confiança documentadas.
- Alerta ao Alê só quando houver decisão, risco, bloqueio ou conclusão relevante.

## Dados/integrações afetadas

- Microsoft Graph
- B2
- LinkedIn monitor
- crons OpenClaw
- arquivos workspace/2nd-brain

## Riscos

- Criar burocracia sem execução.
- Alertas demais no direct do Alê.
- Health lento por carga do servidor.
- Dado parcial virar conclusão executiva.

## Autoridade necessária

Autorizado pelo Alê em 2026-04-28: “vamos implantar para deixar o sistema 10/10”.

## Plano de execução

1. Criar artefatos base.
2. Rodar health.
3. Ativar crons.
4. Usar WORKING no próximo heartbeat.
5. Fechar primeiro loop real: backup VPS full ou LinkedIn API approval.

## QA obrigatório

- Rodar `python3 scripts/operational_health.py`.
- Conferir crons criados.
- Conferir que nenhum side effect externo foi feito.
- Conferir que arquivos de bootstrap não foram alterados.

## Rollback / contenção

- Desabilitar crons `flavia-working-queue-review-hourly` e `operational-health-8h-14h-18h`.
- Manter documentos como referência sem uso ativo.
- Remover/arquivar script `scripts/operational_health.py` se gerar ruído.

## Registro final

Em execução. Núcleo implantado em 2026-04-28.
