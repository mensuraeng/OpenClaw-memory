# Arquitetura Operacional dos Agentes

_Atualizado em 2026-04-13_

## Estrutura recomendada

### 1. main
**Papel:** coordenação central, memória, triagem, execução transversal.

**Responsabilidades:**
- centralizar contexto executivo
- distribuir demandas
- manter continuidade operacional
- consolidar memória e prioridades

**Não deve virar:** agente especialista de uma frente específica.

---

### 2. mensura
**Papel:** operação técnica e executiva da MENSURA.

**Responsabilidades:**
- cronogramas
- risco de obra
- governança de execução
- acompanhamento técnico-executivo

**Fronteira:** tudo que é operação MENSURA.

---

### 3. mia
**Papel:** operação premium da MIA.

**Responsabilidades:**
- experiência do cliente
- pré-construção
- precisão técnica
- comunicação e gestão premium

**Fronteira:** tudo que exige linguagem, cadência e padrão MIA.

---

### 4. pcs
**Papel:** operação, comercial e institucional da PCS.

**Responsabilidades:**
- posicionamento institucional
- propostas e narrativa comercial
- estrutura operacional para obras públicas
- governança de capacidade de entrega

**Fronteira:** tudo ligado à PCS como unidade própria.

---

### 5. finance
**Papel:** frente principal de finanças.

**Responsabilidades:**
- contas a pagar e a receber
- fluxo de caixa
- cobranças
- organização financeira recorrente
- operação financeira especializada

**Fronteira:** toda a operação financeira como agente principal.

---

### 6. juridico
**Papel:** jurídico e risco contratual.

**Responsabilidades:**
- contratos
- minutas
- revisão documental
- risco jurídico
- cláusulas e alertas

**Fronteira:** tudo que exige lente contratual/jurídica.

---

### 7. marketing
**Papel:** posicionamento e comunicação.

**Responsabilidades:**
- conteúdo
- marca
- presença digital
- campanhas
- materiais de comunicação

**Fronteira:** geração e coordenação de comunicação e presença.

---

### 8. producao
**Papel:** produção e execução operacional de entregáveis.

**Responsabilidades:**
- montar materiais
- organizar entregas
- transformar direcionamento em peça executável
- apoiar cadência de produção

**Fronteira:** execução de produção, não estratégia final.

---

### 9. bi
**Papel:** dados, indicadores e inteligência analítica.

**Responsabilidades:**
- dashboards
- indicadores
- estruturação analítica
- automações orientadas a dados
- leitura de performance

**Fronteira:** tudo que depende de dado estruturado e análise.

---

### 10. suprimentos
**Papel:** compras e cadeia de suprimentos.

**Responsabilidades:**
- fornecedores
- cotações
- abastecimento
- racionalização de compras
- acompanhamento de insumos

**Fronteira:** aquisição e suprimento.

---

### 11. rh
**Papel:** pessoas e estrutura interna.

**Responsabilidades:**
- recrutamento
- organização de time
- rotina de pessoas
- documentação e apoio interno

**Fronteira:** operação de pessoas.

---

## Agentes a revisar

### finance
**Status:** mantido como agente principal de finanças.

**Decisão:** consolidado como frente oficial de finanças.

**Motivo:** o agente tem workspace próprio, skills próprias, sessões reais e bindings ativos para contas `miafinance` em Telegram e WhatsApp. Faz mais sentido promovê-lo a agente principal do que manter duplicidade com `financeiro`.

---

### autopilot
**Status:** nome genérico demais.

**Recomendação:** absorver em `mensura` ou renomear apenas se houver função realmente autônoma e permanente.

**Motivo:** hoje parece mais um modo operacional do que uma unidade clara.

---

## Estrutura final recomendada

### Manter
- main
- mensura
- mia
- pcs
- finance
- juridico
- marketing
- producao
- bi
- suprimentos
- rh

### Fundir ou remover
- autopilot

## Regra de desenho

Um agente só deve existir se tiver:
- função própria
- fronteira clara
- demanda recorrente
- baixo overlap com outro agente

Se não tiver isso, vira ruído operacional.
