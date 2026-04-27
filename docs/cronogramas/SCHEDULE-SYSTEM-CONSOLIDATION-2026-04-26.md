# Consolidação operacional — Schedule Control, Portfolio Registry e Intake

_Atualizado em 2026-04-26_

## Estado consolidado

A base de cronogramas/obras agora está estruturada em quatro camadas separadas:

1. `intake` — recebimento de pacotes de cronogramas;
2. `portfolio` — cadastro mestre de projetos/obras;
3. `schedule` — cronogramas versionados e atividades;
4. `analytics` — métricas, forecasts e relatórios.

Essa separação evita misturar arquivo recebido, projeto canônico, cronograma importado e análise executiva.

## Supabase

Projeto: `mensura-schedule-control`  
Ref: `ckmuyvbacgdidmiccvif`  
Região: `sa-east-1`

Schemas operacionais:

- `raw`
- `schedule`
- `control`
- `analytics`
- `portfolio`
- `intake`

## Camada `intake`

Criada para controlar pacotes `.zip` por empresa/status/lote, respeitando limite operacional de 500 MB.

Tabelas:

- `intake.schedule_packages`
- `intake.schedule_package_items`

View:

- `intake.v_schedule_intake_dashboard`

Pacotes iniciais:

- `MENSURA_em_andamento_lote01`
- `MENSURA_concluidas_lote01`
- `MIA_em_andamento_lote01`
- `MIA_concluidas_lote01`
- `PCS_em_andamento_lote01`
- `PCS_concluidas_lote01`

Regra: pacote organiza recebimento; item importado vira `schedule.schedule_versions`.

## Camada `portfolio`

Cadastro mestre transversal Mensura/MIA/PCS.

Tabelas:

- `portfolio.project_registry`
- `portfolio.project_aliases`

View:

- `portfolio.v_project_registry_current`

Relatório executivo atual:

- Mensura: `P_G`, `MELICITA_R1`
- MIA: `CCSP_CASA_7`
- PCS: nenhum até cronograma do Teatro Suzano ou outra obra estar disponível

Regras registradas:

- `MELICITA` é duplicado de `MELICITA_R1`.
- `DOPPIO`, `ELEV_ALTO_DO_IPIRANGA`, `SOFITEL_DIRETOR`, `CCN_BIOMA`, `DF345_DIOGO_DE_FARIA` ficam fora do relatório executivo.
- PCS/Sienge não é fonte de cronograma; Teatro Suzano está com cronograma em elaboração.

## Camada `schedule`

Histórico versionado. Nunca sobrescrever cronograma existente.

Cada importação cria:

- `raw.import_jobs`
- `raw.source_rows`
- `schedule.schedule_versions`
- `schedule.activity_identities`
- `schedule.activity_versions`

## Casa 7

Importada com sucesso a partir de arquivo Microsoft Project `.mpp`.

Snapshot:

- projeto: `CCSP_CASA_7`
- empresa: `MIA`
- versão: `r0_mpp_2026-04-24_telegram_5684`
- data de status: `2026-04-24`
- início: `2026-03-23`
- término: `2026-05-22`
- atividades: 93
- críticas: 14
- avanço médio: 53,72%

## CLI oficial

Comandos centrais:

```bash
mensura-schedule import-mpp <arquivo.mpp> --company ... --project-code ... --project-name ... --execute --json
mensura-schedule portfolio-report --json
mensura-schedule portfolio-report --executive-only --json
mensura-schedule portfolio-classify-pcs --execute --json
mensura-schedule intake-packages --json
mensura-schedule intake-items --json
```

`import-mpp`:

- preview por padrão;
- grava apenas com `--execute`;
- valida assinatura `.mpp`/CFB;
- bloqueia duplicidade por `version_label`;
- atualiza `portfolio.project_registry`.

## Padrão de envio

Pacotes por empresa/status:

```text
MENSURA_em_andamento.zip
MENSURA_concluidas.zip
MIA_em_andamento.zip
MIA_concluidas.zip
PCS_em_andamento.zip
PCS_concluidas.zip
```

Se ultrapassar 500 MB:

```text
MENSURA_em_andamento_lote01.zip
MENSURA_em_andamento_lote02.zip
```

Regra: não dividir uma obra no meio. Cada `.mpp` deve conter uma obra completa.

## Tamanho atual do banco

Consulta em 2026-04-26:

- banco total: 829 MB
- `schedule`: 598 MB
- `raw`: 219 MB
- `analytics`: 320 kB
- `portfolio`: 192 kB
- `control`: 184 kB
- `intake`: 120 kB

Maiores tabelas:

- `schedule.activity_versions`: 546 MB
- `raw.source_rows`: 219 MB
- `schedule.activity_identities`: 52 MB

Regra de proteção: não limpar histórico sem relatório de impacto, backup/export e autorização explícita do Alê.

## Guardrails permanentes

- Não misturar Trade com Mensura/MIA/PCS.
- Não atualizar OpenClaw sem autorização explícita do Alê.
- Não apagar raw/histórico de cronograma sem autorização explícita.
- SharePoint/MS Project bruto fica em `runtime/`, fora do Git.
- Segredos ficam apenas em env local ignorado.
- Comunicação externa segue regra da Flávia: revisar/autorizar antes, salvo rotinas já explicitamente aprovadas.

## Próximos passos

1. Receber pacotes `.zip` por empresa/status.
2. Popular `intake.schedule_package_items` quando pacotes forem extraídos.
3. Importar cada `.mpp` por `mensura-schedule import-mpp`.
4. Criar `portfolio-risk-summary --executive-only` para consolidar risco, críticas e forecast de Mensura/MIA.
5. Quando Teatro Suzano ficar pronto, importar como primeiro cronograma PCS.

## Relatório de Diretoria — portfolio-risk-summary

Comando criado:

```bash
mensura-schedule portfolio-risk-summary --json
mensura-schedule portfolio-risk-summary
mensura-schedule portfolio-risk-summary --company Mensura
```

Objetivo: entregar uma visão sucinta de Diretoria, não um relatório técnico de cronograma.

Campos centrais:

- Baseline x término atual;
- % planejado x % real;
- gap em pontos percentuais;
- atividades totais e atrasadas;
- caminho crítico: críticas abertas e críticas atrasadas;
- forecast quando disponível;
- risco executivo;
- recomendação objetiva.

Critério de risco inicial:

- `CRITICO`: atraso esperado >= 60 dias, crítica atrasada, ou gap planejado x real <= -20 p.p.;
- `ALTO`: atraso esperado >= 30 dias, muitas críticas abertas, ou gap <= -10 p.p.;
- `MEDIO`: atraso esperado >= 15 dias ou gap <= -5 p.p.;
- `BAIXO`: acompanhamento normal.

Validação inicial em 2026-04-26:

```text
P_G           → CRITICO | baseline 2026-07-04 → atual 2026-08-02 | planejado 92,87% x real 40,39%
MELICITA_R1   → CRITICO | baseline 2026-07-15 → atual 2026-08-14 | planejado 22,88% x real 12,27%
CCSP_CASA_7   → CRITICO | baseline 2026-05-22 → atual 2026-05-22 | planejado 79,74% x real 53,72%
```

Observação: o cálculo de `% planejado` é heurístico por atividade, baseado na posição da data de status entre baseline_start e baseline_finish. É bom para visão executiva inicial, mas deve ser refinado depois com peso por duração/custo/frente.
