# Padrão de envio de cronogramas — Schedule Control

_Atualizado em 2026-04-26_

## Objetivo

Organizar o recebimento de cronogramas por empresa, status e obra, respeitando limite de arquivo de até **500 MB** e mantendo cada obra íntegra para não quebrar caminho crítico, predecessoras, calendários ou baseline.

## Regra principal

**Nunca dividir uma mesma obra em pedaços**, salvo último caso e com identificação explícita de parcial.

Cada `.mpp` deve conter uma obra completa.

## Estrutura recomendada de pacotes

Enviar em lotes `.zip` por empresa e status:

```text
MENSURA_em_andamento.zip
MENSURA_concluidas.zip

MIA_em_andamento.zip
MIA_concluidas.zip

PCS_em_andamento.zip
PCS_concluidas.zip
```

Se algum pacote ultrapassar 500 MB, dividir em lotes mantendo obras inteiras:

```text
MENSURA_em_andamento_lote01.zip
MENSURA_em_andamento_lote02.zip
MENSURA_concluidas_lote01.zip
MENSURA_concluidas_lote02.zip
```

## Estrutura interna do ZIP

```text
MENSURA_em_andamento.zip
  /P_G/
    P_G_status_2026-04-26.mpp
    README.txt                 # opcional

  /MELICITA_R1/
    MELICITA_R1_status_2026-04-26.mpp
    README.txt                 # opcional
```

Para MIA:

```text
MIA_em_andamento.zip
  /CCSP_CASA_7/
    CCSP_CASA_7_r1_2026-04-28.mpp
```

Para PCS:

```text
PCS_em_andamento.zip
  /TEATRO_SUZANO/
    TEATRO_SUZANO_r0_2026-04-30.mpp
```

## Nome dos arquivos

Formato recomendado:

```text
<EMPRESA/OBRA>_<REVISAO ou STATUS>_<DATA>.mpp
```

Exemplos:

```text
P_G_status_2026-04-26.mpp
MELICITA_R1_r2_2026-04-26.mpp
CCSP_CASA_7_r1_2026-04-28.mpp
TEATRO_SUZANO_r0_2026-04-30.mpp
```

## Prioridade de envio

1. `MENSURA_em_andamento.zip`
2. `MIA_em_andamento.zip`
3. `PCS_em_andamento.zip`
4. concluídas depois, como histórico

Motivo: primeiro estabilizar portfólio vivo; obras concluídas entram depois para base histórica, comparação e treinamento de padrões de atraso.

## Como tratar obras concluídas

Obras concluídas devem ser importadas, mas não entram no relatório executivo atual.

Uso previsto:

- histórico de baseline versus realizado;
- aprendizado de padrões de atraso;
- calibração futura de forecast;
- benchmark por tipo de obra, cliente, frente e empresa.

## Manifest opcional por pacote

Se possível, incluir um arquivo `manifest.csv` no ZIP:

```csv
empresa,obra_codigo,obra_nome,status,arquivo,versao,data_status,observacao
MENSURA,P_G,P&G Louveira,em_andamento,P_G_status_2026-04-26.mpp,status,2026-04-26,
MIA,CCSP_CASA_7,CCSP Casa 7,em_andamento,CCSP_CASA_7_r1_2026-04-28.mpp,r1,2026-04-28,
PCS,TEATRO_SUZANO,Teatro Suzano,em_andamento,TEATRO_SUZANO_r0_2026-04-30.mpp,r0,2026-04-30,cronograma em elaboração
```

O manifest não é obrigatório, mas ajuda a reduzir ambiguidade e acelerar importação.

## Canal de envio

Preferência atual:

- Telegram: arquivos individuais ou pacotes menores;
- Email: pacotes grandes, histórico ou necessidade de trilha formal;
- SharePoint: acervo completo ou pacotes que ultrapassem limite do Telegram/email.

## Regra de importação

Todo arquivo recebido deve passar por:

```bash
mensura-schedule import-mpp <arquivo.mpp> --json
```

Preview primeiro. Só depois:

```bash
mensura-schedule import-mpp <arquivo.mpp> ... --execute --json
```

Nada deve sobrescrever histórico. Cada revisão entra como nova `schedule.schedule_versions`.

## Estrutura Supabase — Intake de pacotes

Criado schema `intake` no Supabase para controlar recebimento dos pacotes antes da importação final.

Tabelas:

- `intake.schedule_packages`
- `intake.schedule_package_items`

View:

- `intake.v_schedule_intake_dashboard`

Pacotes planejados inicialmente:

```text
MENSURA_em_andamento_lote01
MENSURA_concluidas_lote01
MIA_em_andamento_lote01
MIA_concluidas_lote01
PCS_em_andamento_lote01
PCS_concluidas_lote01
```

Comandos CLI:

```bash
mensura-schedule intake-packages --json
mensura-schedule intake-packages --company Mensura --json
mensura-schedule intake-items --json
```

Uso operacional:

1. pacote recebido entra em `intake.schedule_packages`;
2. arquivos extraídos entram em `intake.schedule_package_items`;
3. cada item importado via `import-mpp` recebe vínculo com `schedule.schedule_versions`;
4. portfólio final segue em `portfolio.project_registry`.
