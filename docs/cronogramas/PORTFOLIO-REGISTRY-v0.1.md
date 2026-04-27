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

- `CCSP_CASA_7` — obra ativa, ainda fora do Supabase Schedule Control.

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
2. Importar/registrar CCSP Casa 7 em camada de schedule ou manter como fonte externa até haver XLSX/MS Project.
3. Criar comando `portfolio-report` consolidando Mensura/MIA/PCS.
4. Remover hardcodes remanescentes de status auxiliar quando o registry cobrir 100% do universo.
