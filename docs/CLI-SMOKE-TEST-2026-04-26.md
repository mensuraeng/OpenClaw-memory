# CLI Smoke Test — 2026-04-26

## Resultado

Status: **APROVADO** para uso operacional interno read-only/preview/dry-run.

Todas as 10 CLIs responderam ao comando de status e os guardrails bloquearam comandos perigosos.

## CLIs testadas

| # | CLI | Status | Guardrail |
|---|---|---|---|
| 1 | `openclaw-ops` | OK | `restart` bloqueado |
| 2 | `msgraph` | OK | `send` bloqueado |
| 3 | `finance` | OK | `pix` bloqueado |
| 4 | `mensura-schedule` | OK | read-only analytics validado |
| 5 | `commercial` | OK | `publish` bloqueado |
| 6 | `pcs-licita` | OK | `email` bloqueado |
| 7 | `mia-obra` | OK | `email` bloqueado |
| 8 | `knowledge` | OK | `sync` bloqueado |
| 9 | `sienge` | OK | `upload` bloqueado |
| 10 | `reports` | OK | `send` bloqueado |

## Evidências principais

### `openclaw-ops`

- Disco: 17.98 GB livres, 81.2% usado.
- Backups: 6 `.tar.gz`, 0 `.tmp`, 14.39 GB.
- Repositórios principais limpos.

### `msgraph`

- Configs Mensura, MIA e PCS presentes.
- Default users resolvidos.

### `finance`

- 15 contas registradas.
- 15 pendentes.
- 4 vencidas.
- 2 vencem em 7 dias.
- Guardrail financeiro funcionando.

### `mensura-schedule`

- 37 projetos.
- 39 versões de cronograma.
- 107.145 activity versions.
- 4.488 atividades críticas atuais.

### `commercial`

- Configs HubSpot, Phantombuster, LinkedIn scaffold e GA4 presentes.
- Publicação externa bloqueada.

### `pcs-licita`

- Scripts PNCP e relatório semanal detectados.
- Envio externo bloqueado.

### `mia-obra`

- Scripts CCSP detectados.
- Guardrail CCSP operacional.

### `knowledge`

- Scripts Docling, RAG, Notion, NotebookLM e sync detectados.
- Sync real bloqueado.

### `sienge`

- Scripts Sienge detectados.
- Upload real bloqueado.

### `reports`

- Scripts de relatório detectados.
- Entrega externa bloqueada.

## Conclusão

A camada CLI é superior ao padrão anterior porque:

1. cria uma interface única por domínio;
2. torna comandos repetíveis;
3. permite teste automático;
4. reduz risco de scripts com side effects escondidos;
5. expõe guardrails explicitamente;
6. facilita migração gradual de crons;
7. melhora operação por agentes sem depender de improviso.

## Próxima fase: implantação em produção

Não trocar todos os crons de uma vez.

Ordem recomendada:

1. Substituir crons puramente diagnósticos por CLIs:
   - `openclaw-ops status/health`;
   - `openclaw-ops backup status`;
   - `finance status/report` read-only;
   - `mensura-schedule critical-summary/quality-report`.

2. Manter em preview os fluxos com envio externo:
   - `commercial`;
   - `pcs-licita weekly`;
   - `mia-obra`;
   - `reports`.

3. Refatorar scripts antigos antes de ativar execução real:
   - separar coleta read-only de envio/mutação;
   - adicionar `--json` e `--dry-run` real;
   - usar CLI como entry point do cron.

## Decisão recomendada

Autorizar uma **fase de deploy seguro** apenas para crons/read-only primeiro.

Mudanças em crons com email, Telegram, upload, pagamento, agenda, delete, update ou restart devem continuar exigindo autorização explícita caso a caso.
