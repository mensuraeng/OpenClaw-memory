# Portfólio — Obras em andamento cruzadas Mensura / MIA / PCS

_Atualizado em 2026-04-26_

## Critério aplicado

Entram como **em andamento**:

1. Projetos do Mensura Schedule Control cujo `current_finish >= current_date`.
2. Projetos MIA/PCS com evidência operacional no 2nd-brain indicando obra ativa ou prazo futuro.
3. Projetos PCS de Sienge são tratados como **candidatos** quando a base só informa “obra e centro de custo”, pois nem todo centro de custo representa obra física ativa.

Não entram no relatório executivo:

- projetos com `current_finish` anterior à data atual;
- modelos, testes ou arquivos auxiliares;
- centros administrativos;
- registros PCS sem confirmação de obra física ativa.

---

## 1. Mensura — confirmados pelo banco de cronogramas

Fonte: Supabase `mensura-schedule-control`, comando `mensura-schedule executive-risk-report` com filtro `max_current_finish >= current_date`.

| Projeto | Empresa | Risco | Término atual | Atraso esperado | Críticas abertas | Status |
|---|---|---:|---:|---:|---:|---|
| MELICITA | Mensura | CRÍTICO | 2026-08-14 | 30 dias | 112 | Em andamento |
| DOPPIO | Mensura | CRÍTICO | 2026-06-12 | 14 dias | 142 | Em andamento |
| DF345_DIOGO_DE_FARIA | Mensura | CRÍTICO | 2026-09-15 | 95 dias | 56 | Em andamento |
| P_G | Mensura | CRÍTICO | 2026-08-02 | 63 dias | 36 | Em andamento |
| MELICITA_R1 | Mensura | CRÍTICO | 2026-08-14 | 30 dias | 103 | Em andamento / possível versão duplicada de MELICITA |
| ELEV_ALTO_DO_IPIRANGA | Mensura | MÉDIO | 2026-06-15 | 0 dias | 66 | Em andamento |
| SOFITEL_DIRETOR | Mensura | MÉDIO | 2026-10-30 | 0 dias | 86 | Em andamento |
| CCN_BIOMA | Mensura | MÉDIO | 2027-07-27 | 0 dias | 56 | Em andamento |

### Observações Mensura

- `P_G` corresponde a **P&G Louveira** e tem status jurídico sensível já registrado: comunicação externa exige dupla revisão do Alê.
- `MELICITA` e `MELICITA_R1` provavelmente representam versões do mesmo projeto; manter ambos até reconciliação de identidade/versão.
- `TESTE_1` foi excluído por regra de modelo/teste.

---

## 2. MIA — confirmado pelo 2nd-brain

Fonte: `/root/2nd-brain/06-agents/flavia/memory/projects/ccsp-casa7.md` e `/root/2nd-brain/02-context/pending.md`.

| Projeto | Empresa | Evidência | Término / prazo | Status |
|---|---|---|---:|---|
| CCSP Casa 7 | MIA | Cronograma baseline e rotina operacional ativa | 2026-05-22 | Em andamento |

### Observações MIA

- CCSP Casa 7 ainda **não está no Supabase Mensura Schedule Control**.
- Já existe cronograma estruturado em memória, mas precisa entrar no pipeline de importação para virar dado comparável no banco.
- O projeto tem rotinas automáticas MIA Obra ativas: manhã Victor, RDO e relatório semanal.

---

## 3. PCS — candidatos / requer validação

Fontes:

- `/root/2nd-brain/02-context/pcs-sienge-obras-centros-de-custo.md`
- `/root/2nd-brain/02-context/pending.md`

### Confirmado como frente operacional/prazo pendente

| Projeto / frente | Empresa | Evidência | Status |
|---|---|---|---|
| Teatro Município de Suzano | PCS | Pendência: lançar orçamento real no Sienge | Candidato a obra ativa / validar execução |
| Paranapiacaba / Pavimentação Paranapiacaba | PCS | Status especial patrimonial + registros Sienge | Candidato ativo / exige validação |
| SPTrans — 1ª OS | PCS | Aguardando recebimento da OS; criar alertas D+10/D+30 quando chegar | Ainda não iniciado / pendente OS |

### Registros Sienge classificados apenas como “obra e centro de custo”

Estes registros existem na base PCS/Sienge, mas **não devem entrar automaticamente como obra em andamento** sem validação:

- Faculdade de Direito de SBC — Centro Jurídico
- Retrofit Faculdade de Direito de SBC
- Manutenção Paranapiacaba 2024
- SmartJampa
- Rua Laura 181
- Teatro Município de Suzano
- Reforma e Man. de Escolas SP — Lote 180
- EMEI Eduardo Carlos Pereira
- EMEI Cidade Fernão Dias
- EMEI Aviador Edu Chaves
- EMEF Profa. Esmeralda Salles Pereira
- EMEI Prof. Ênio Correa
- Gerencial Pavimentação Paranapicaba PCS
- Av. Nove de Julho 4428
- ATA Calçadas
- MP Auditório Riachuelo
- Pavimentação Paranapiacaba

### Observações PCS

- A base PCS atual é de **centros de custo/obras Sienge**, não cronograma executivo.
- Próximo passo PCS é classificar cada registro em:
  1. obra executável ativa;
  2. obra encerrada;
  3. centro administrativo;
  4. ambíguo/validar.

---

## 4. Consolidação executiva

| Empresa | Confirmados em andamento | Candidatos / validar | Observação |
|---|---:|---:|---|
| Mensura | 8 | 0 | Coberto pelo Supabase Schedule Control |
| MIA | 1 | 0 | CCSP Casa 7 ativo, ainda fora do Supabase |
| PCS | 0 confirmado | 3+ candidatos | Requer classificação Sienge/obra ativa |

## Próximo passo recomendado

1. Criar uma tabela/camada `portfolio.project_registry` ou equivalente no Supabase para cruzar empresa, projeto, fonte, status e sistema de origem.
2. Importar/registrar CCSP Casa 7 no Mensura Schedule Control ou em camada multiempresa equivalente.
3. Classificar os registros PCS/Sienge em obra ativa, encerrada, administrativo ou ambíguo.
4. Atualizar `executive-risk-report` para aceitar filtro por empresa e incluir fontes externas ao cronograma quando não houver MS Project importado.
