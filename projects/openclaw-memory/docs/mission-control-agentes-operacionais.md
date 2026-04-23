# Mission Control — Agentes Operacionais

_Atualizado em 2026-04-15_

## Objetivo

Levar a lógica operacional dos 12 agentes para dentro do Mission Control, de forma que o painel mostre utilidade real, e não apenas presença estrutural.

A tela de agentes deve ajudar a responder:
- quem faz o quê
- quando acionar cada agente
- qual entrega esperar
- quais agentes estão úteis
- quais estão ociosos, sobrepostos ou em revisão

---

## Princípio central

A tela de agentes não deve ser organograma decorativo.

Ela deve funcionar como um painel de gestão dos agentes, permitindo leitura rápida sobre:
- papel
- status
- utilidade
- fronteira
- necessidade de ajuste

---

## Estrutura recomendada da tela

### 1. Resumo executivo no topo
Mostrar:
- total de agentes
- quantos estão ativos
- quantos estão em revisão
- quantos estão sem entrega recente
- quantos estão com fronteira clara

**Objetivo:** leitura instantânea da saúde da malha de agentes.

### 2. Visão por empresa
Separar agentes que servem principalmente:
- MENSURA
- MIA
- PCS
- transversal/consolidado

**Objetivo:** leitura por frente de negócio.

### 3. Visão por função
Separar agentes por área:
- operação técnica
- financeiro
- jurídico
- marketing
- produção
- BI/dados
- suprimentos
- RH
- monitoramento
- orçamento

**Objetivo:** leitura transversal da estrutura.

### 4. Cards individuais por agente
Cada card deve mostrar pelo menos:
- nome do agente
- papel principal
- quando acionar
- saída esperada
- status atual
- última entrega relevante
- flag de revisão se necessário

---

## Campos mínimos por agente

### Identidade
- id
- nome visível
- empresa/função principal

### Utilidade
- papel principal
- tipo de problema que resolve
- tipo de entrega que produz

### Operação
- quando acionar
- quando não usar
- quando escalar

### Estado
- ativo
- útil
- ocioso
- em revisão
- fronteira sobreposta

### Evidência
- última entrega útil
- última atividade percebida
- observação curta

---

## Status recomendados

### Ativo
Está sendo usado e gera valor claro.

### Útil
Ainda que não esteja em uso agora, tem fronteira e entrega claras.

### Ocioso
Existe, mas está sem uso ou sem sinal relevante recente.

### Em revisão
Fronteira, papel ou entrega ainda estão mal definidos.

### Sobreposto
Está colidindo com outro agente e precisa de ajuste.

---

## Filtros úteis

### Filtro por empresa
- MENSURA
- MIA
- PCS
- consolidado

### Filtro por função
- técnico
- financeiro
- jurídico
- marketing
- produção
- dados
- suprimentos
- RH
- monitoramento
- custos

### Filtro por estado
- ativos
- úteis
- ociosos
- revisão
- sobrepostos

---

## Perguntas que a tela precisa responder bem

1. Qual agente devo usar neste tipo de problema?
2. O que eu devo esperar de resposta dele?
3. Esse agente está gerando valor ou só existe?
4. Existe sobreposição entre agentes?
5. Quais agentes precisam de ajuste agora?

---

## Regras de qualidade

### Tela boa
- simples
- clara
- mostra fronteira
- mostra utilidade
- mostra status real
- ajuda a tomar decisão de uso

### Tela ruim
- só lista nome e descrição bonita
- não mostra quando usar
- não mostra saída esperada
- não mostra estado real
- não ajuda gestão

---

## Implementação recomendada

### Fase 1
Usar as fichas operacionais já criadas como fonte-base.

Mostrar para cada agente:
- papel
- acionamento
- saída
- escalonamento
- status manual inicial

### Fase 2
Conectar com atividade real.

Mostrar:
- última sessão
- última entrega útil
- uso recente

### Fase 3
Adicionar leitura de saúde da malha.

Mostrar:
- agentes pouco usados
- agentes sobrepostos
- áreas sem cobertura
- frentes com dependência excessiva

---

## Critério de pronto desta etapa

A etapa está pronta quando:
- a lógica dos 12 agentes pode ser refletida na UI
- a tela deixa de ser decorativa
- o Mission Control passa a suportar gestão real dos agentes
