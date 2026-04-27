# Portfolio Registry v0.1 — Cadastro mestre de projetos

_Atualizado em 2026-04-26_

## Objetivo

Criar uma camada estrutural para tratar projetos/obras como cadastro mestre, separada da leitura bruta de cronogramas.

Antes, as exclusões do relatório executivo estavam hardcoded no CLI. Agora passam a viver no banco, em `portfolio.project_registry`.

## Estrutura criada

Schema: `portfolio`

Tabelas:

- `portfolio.project_registry`
- `portfolio.project_aliases`

View:

- `portfolio.v_project_registry_current`

## Papel das tabelas

### `portfolio.project_registry`

Cadastro mestre por projeto canônico.

Campos principais:

- `company`
- `canonical_code`
- `canonical_name`
- `operational_status`
- `include_in_executive_report`
- `include_in_forecast`
- `source_system`
- `schedule_project_id`
- `canonical_project_id`
- `exclusion_reason`
- `notes`
- `metadata`

### `portfolio.project_aliases`

Mapa de nomes e códigos alternativos.

Exemplos:

- `P_G` → `P&G Louveira`
- `MELICITA_R1` → `Melicita`
- `CCSP_CASA_7` → `Casa 7`

## Seed inicial

Comando:

```bash
mensura-schedule portfolio-seed --json
```

Registros criados/atualizados: 12.

### Mensura

Incluídos no relatório executivo:

- `P_G`
- `MELICITA_R1`

Excluídos / duplicados:

- `MELICITA` — duplicado de `MELICITA_R1`
- `DOPPIO`
- `ELEV_ALTO_DO_IPIRANGA`
- `SOFITEL_DIRETOR`
- `CCN_BIOMA`
- `DF345_DIOGO_DE_FARIA`

### MIA

- `CCSP_CASA_7` — obra ativa, importada para o Supabase Schedule Control em 2026-04-26 via arquivo MPP.

### PCS

Candidatos, ainda sem confirmação por cronograma:

- `TEATRO_SUZANO`
- `PARANAPIACABA`
- `SPTRANS_1_OS`

## CLI

Novos comandos:

```bash
mensura-schedule portfolio-seed --json
mensura-schedule portfolio-registry --json
mensura-schedule portfolio-registry --company Mensura --json
mensura-schedule portfolio-registry --status ongoing --json
```

## Relatórios já migrados para o registry

- `mensura-schedule executive-risk-report`
- `mensura-schedule forecast-initial`
- `mensura-schedule analytics-universe --analytics-only`

Esses comandos agora usam `portfolio.project_registry` para decidir inclusão em vez de listas hardcoded no código.

## Validação atual

Resultado validado em 2026-04-26:

```text
analytics-universe --analytics-only → MELICITA_R1, P_G
executive-risk-report              → P_G, MELICITA_R1
forecast-initial                   → MELICITA_R1, P_G
```

## Próximos passos

1. Classificar PCS/Sienge entre obra ativa, encerrada, administrativo e ambíguo.
2. Productizar importação MPP em comando CLI (`import-mpp`) para não depender de script one-off.
3. Criar comando `portfolio-report` consolidando Mensura/MIA/PCS.
4. Remover hardcodes remanescentes de status auxiliar quando o registry cobrir 100% do universo.


## Importação CCSP Casa 7 — 2026-04-26

Arquivo recebido via Telegram e preservado em runtime ignorado pelo Git:

```text
projects/mensura-schedule-control/runtime/inbound/ccsp-casa7/CCSP_CASA_7_Cronograma_Executivo_r0.mpp
```

Snapshot criado no Supabase:

- projeto: `CCSP_CASA_7`
- empresa: `MIA`
- versão: `r0_mpp_2026-04-24_telegram_5684`
- data de status: `2026-04-24`
- início: `2026-03-23`
- término: `2026-05-22`
- atividades importadas: 93
- atividades críticas: 14
- avanço médio importado: 53,72%

O `portfolio.project_registry` foi atualizado para vincular `CCSP_CASA_7` ao `schedule.projects`.

## Classificação PCS/Sienge — 2026-04-26

Comando criado:

```bash
mensura-schedule portfolio-classify-pcs --json
mensura-schedule portfolio-classify-pcs --execute --json
```

Regra aplicada:

- registros PCS/Sienge não têm cronograma importável hoje;
- portanto, nenhum registro PCS/Sienge entra em forecast ou relatório executivo até haver cronograma;
- `TEATRO_SUZANO` permanece `candidate`, com cronograma em elaboração;
- registros administrativos (`ADM PCS`, `CUSTOS COM PESSOAL`, `ADM MIA ENGENHARIA`, `LOCAÇÃO SÃO CAETANO`) ficam como `administrative`.

Resultado da classificação:

- 22 registros PCS/Sienge classificados;
- 0 incluídos no relatório executivo;
- 0 incluídos no forecast.

## Portfolio Report transversal — 2026-04-26

Comando criado:

```bash
mensura-schedule portfolio-report --json
mensura-schedule portfolio-report --executive-only --json
mensura-schedule portfolio-report --company PCS --json
```

Validação atual:

```text
portfolio-report total: 32 registros
- Mensura: 8
- MIA: 1
- PCS: 23

portfolio-report --executive-only: 3 registros
- Mensura: P_G, MELICITA_R1
- MIA: CCSP_CASA_7
- PCS: nenhum
```

## Importação MPP productizada — 2026-04-26

Comando criado:

```bash
mensura-schedule import-mpp <arquivo.mpp> \
  --company MIA \
  --project-code CCSP_CASA_7 \
  --project-name "CCSP Casa 7" \
  --version-label r0_mpp_2026-04-24 \
  --include-executive \
  --include-forecast \
  --execute \
  --json
```

Comportamento:

- lê `.mpp` via MPXJ;
- valida assinatura CFB do arquivo;
- executa preview por padrão;
- só grava com `--execute`;
- cria `raw.import_jobs`;
- cria nova `schedule.schedule_versions`;
- insere `raw.source_rows`, `schedule.activity_identities` e `schedule.activity_versions`;
- atualiza `portfolio.project_registry`;
- bloqueia reimportação com o mesmo `version_label`, salvo com novo label/uso explícito de `--force-new`.

Validação com Casa 7:

```text
preview: 93 atividades, 14 críticas, início 2026-03-23, término 2026-05-22, avanço médio 53,72%.
reimportação do mesmo version_label: bloqueada corretamente.
```
