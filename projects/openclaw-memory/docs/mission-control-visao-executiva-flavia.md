# Mission Control — Visão Executiva da Flávia

_Atualizado em 2026-04-15_

## Objetivo

Transformar o Mission Control em um painel de gestão realmente útil para leitura executiva, priorização e operação por exceção.

O painel não deve ser vitrine de dados. Deve ser ferramenta para responder rapidamente:
- onde está o risco
- o que exige decisão
- o que travou
- o que avançou
- o que precisa da atenção do Alê
- o que segue sem interrupção

---

## Princípio central

O Mission Control deve refletir a lógica da Flávia:
- triagem
- consolidação
- coordenação dos 12 agentes
- leitura por empresa
- leitura por função
- operação por exceção

---

## Camadas de leitura do painel

### 1. Camada executiva geral
Deve mostrar:
- decisões pendentes
- alertas críticos
- pendências abertas
- follow-ups vencidos
- exceções do dia
- visão rápida do estado geral

**Objetivo:** permitir leitura de 2 minutos do que realmente importa.

### 2. Camada por empresa
Separar pelo menos:
- MENSURA
- MIA
- PCS
- consolidado/finance

Cada empresa deve mostrar:
- status geral
- riscos ativos
- marcos próximos
- pendências críticas
- agente principal relacionado

**Objetivo:** leitura de gestão por frente de negócio.

### 3. Camada por função
Separar pelo menos:
- financeiro
- marketing
- produção
- jurídico
- BI/dados
- suprimentos
- RH
- autopilot
- orçamentista

Cada função deve mostrar:
- o que está ativo
- onde há bloqueio
- o que depende de decisão
- o que está sem dono claro

**Objetivo:** leitura transversal da operação.

### 4. Camada dos agentes
Mostrar:
- agente
- papel
- status
- últimas entregas úteis
- sinais relevantes
- necessidade de ajuste ou revisão

**Objetivo:** fazer os agentes serem geridos como estrutura real, não ícones bonitos.

---

## Blocos prioritários do painel

### Bloco 1 — Decisões pendentes
Fonte lógica: fila de decisões executivas.

Mostrar:
- prioridade
- assunto
- prazo
- recomendação
- dono após decisão

### Bloco 2 — Riscos e silêncio operacional
Fonte lógica: radar de silêncio.

Mostrar:
- item
- tipo de risco
- faixa
- impacto
- ação sugerida

### Bloco 3 — Follow-ups vencidos
Fonte lógica: rotina de follow-up.

Mostrar:
- parte
- assunto
- atraso
- intensidade atual
- próxima ação

### Bloco 4 — Alertas por empresa
Mostrar por empresa:
- principal alerta
- principal bloqueio
- principal próximo passo

### Bloco 5 — Estado dos 12 agentes
Mostrar:
- agente
- utilidade atual
- última entrega relevante
- status: ativo / ocioso / revisão

### Bloco 6 — Memória viva da operação
Mostrar:
- decisões recentes
- pendências críticas
- lições novas

---

## Regra de qualidade do painel

### Bom painel
- pouca leitura para alto valor
- visualiza exceção e decisão
- separa empresa e função
- mostra dono e próximo passo
- ajuda a escolher onde entrar

### Painel ruim
- dashboard bonito e inútil
- excesso de card sem consequência
- muito status sem decisão
- muita métrica sem prioridade
- pouca clareza sobre ação

---

## Ordem recomendada de implementação

### Fase 1
- decisões pendentes
- riscos/silêncio
- follow-ups vencidos
- alertas por empresa

### Fase 2
- visão funcional por área
- estado dos 12 agentes
- memória viva da operação

### Fase 3
- refinamento visual
- filtros por prioridade
- leitura histórica e tendência

---

## Regras de exibição

### Sempre mostrar
- risco
- decisão
- bloqueio
- dono
- próximo passo

### Nunca priorizar no topo
- métrica sem consequência
- card ornamental
- status repetido
- volume de informação sem hierarquia

---

## Critério de pronto do Dia 8

A visão executiva está pronta quando:
- o painel já tem lógica clara de leitura
- existe separação por empresa e função
- existe superfície explícita para decisão, risco, follow-up e agentes
- a prioridade do painel é gestão, não decoração
