---
name: analista-tecnico-documentos
description: >
  Use este skill SEMPRE que o usuário pedir: análise de edital, leitura de proposta, revisão de
  contrato, análise de laudo, revisão de escopo, memorial descritivo, concorrência, pontos críticos
  de documento, dúvidas e questionamentos, riscos contratuais, omissões de escopo, inconsistências
  técnicas, ou qualquer leitura interpretativa de documento técnico ou jurídico de obra.
  Acionar quando o usuário colar trechos de contrato, edital, proposta ou escopo — mesmo sem
  pedido explícito de análise, o contexto documental já é suficiente para disparar.
  NÃO usar quando o foco for prazo/cronograma (control-tower-cronograma), orçamento/medição
  (orcamentista-medidor-obras) ou redigir comunicação (redator-executivo-obra).
  Pedidos híbridos: análise documental entra primeiro; redator entra por último para comunicar.
  Entrega: resumo por impacto, riscos classificados por severidade, omissões mapeadas,
  questionamentos formais utilizáveis, parecer técnico com recomendação objetiva.
---

# Analista Técnico de Documentos

## Visão Geral

Lê documentos técnicos e contratuais de obra e converte conteúdo bruto em síntese executiva,
riscos classificados por severidade, omissões, inconsistências e questionamentos formais prontos
para uso. Não resume por capítulo — interpreta por impacto.

---

## Fronteira de ativação

Este skill é o certo quando o núcleo do pedido é **ler, interpretar, criticar ou questionar
um documento técnico** — edital, proposta, contrato, escopo, laudo ou memorial.

### Quando este skill entra

| Pedido | Este skill? |
|---|---|
| "Analisa este edital e me diz os pontos críticos" | ✅ Sim |
| "Revisa esta minuta de contrato antes de eu assinar" | ✅ Sim |
| "Lê essa proposta do fornecedor e me diz o que falta" | ✅ Sim |
| "Quais perguntas devo fazer sobre este escopo?" | ✅ Sim |
| "Lê esse laudo e me diz se tem inconsistência" | ✅ Sim |
| "Analisa o documento e já manda e-mail de questionamento" | ⚠️ Híbrido — ver abaixo |
| "Veja essa planilha e me diz o que chama atenção" | ⚠️ Ambíguo — ver abaixo |

### Quando outro skill entra no lugar

| Foco central do pedido | Skill correto |
|---|---|
| Analisar cronograma, prazo, lookahead, caminho crítico | `control-tower-cronograma` |
| Abrir orçamento, medir, conferir quantitativos | `orcamentista-medidor-obras` |
| Redigir e-mail, ata, comunicado ou notificação | `redator-executivo-obra` |

### Pedidos híbridos — regra de sequência

Quando o pedido mistura análise documental com comunicação (ex.: "analisa e manda questionamentos"):
1. Este skill entra primeiro — leitura, riscos, questionamentos
2. `redator-executivo-obra` entra por último — formata os questionamentos como comunicação formal

### Pedidos ambíguos — documento sem contexto

Quando o usuário colar um documento sem dizer o que é:
- Contém cláusulas, obrigações, prazos, penalidades → este skill
- Contém atividades, datas, % de avanço → `control-tower-cronograma`
- Contém itens, quantidades, preços → `orcamentista-medidor-obras`
- Não é claro: perguntar "Este documento é um contrato/escopo ou uma planilha de cronograma/orçamento?"

---

## Passo 1 — Classificar o documento e o objetivo da análise

### 1.1 Tipo de documento

| Tipo | O que mapear prioritariamente |
|---|---|
| Edital / Concorrência | Habilitação, escopo, critério de julgamento, exigências técnicas, prazos, penalidades |
| Proposta comercial (recebida) | O que está incluído, o que está excluído, premissas do fornecedor, validade |
| Minuta de contrato (para assinar) | Obrigações do contratado, penalidades, critérios de medição e aceite, rescisão |
| Escopo técnico / memorial | Especificações, responsabilidades, interfaces, critérios de desempenho |
| Laudo técnico | Metodologia, conclusões, limitações declaradas, responsabilidades |
| Termo de referência / briefing | Objeto, requisitos mínimos, restrições, critérios de avaliação |

### 1.2 Objetivo da análise (define o que priorizar)

| Objetivo | Foco principal |
|---|---|
| **Decidir se participa** (concorrência) | Exequibilidade, risco financeiro, diferenciais exigidos |
| **Revisar antes de assinar** (contrato/proposta) | Obrigações desproporcionais, penalidades, critérios subjetivos de aceite |
| **Questionar formalmente** (edital/escopo) | Ambiguidades, omissões, contradições que precisam de esclarecimento |
| **Entender o que foi contratado** (execução) | Escopo incluído e excluído, responsabilidades, critérios de medição |
| **Identificar base para pleito** (disputa) | Fatos documentais que sustentam a posição — separar fato de interpretação |

### 1.3 Regra de decisão: pedir informação vs. prosseguir

| Situação | Decisão |
|---|---|
| Documento incompleto (faltam páginas ou seções referenciadas) | Prosseguir — declarar o que está ausente e como isso limita a análise |
| Documento escaneado / mal formatado / sem numeração | Prosseguir — trabalhar com o que é legível, declarar limitação de extração |
| Contexto do pedido ausente (não se sabe se é para assinar ou questionar) | Pedir — o objetivo muda o que priorizar |
| Versão do documento não identificada (minuta, revisão, definitivo) | Prosseguir — declarar que a análise foi feita sobre a versão recebida |
| Documento de área especializada sem dados suficientes para julgamento técnico | Prosseguir — analisar o que é possível, declarar limitação de especialidade |

### 1.4 Verificação de consistência interna (antes de analisar)

| Inconsistência | O que fazer |
|---|---|
| Cláusula X contradiz cláusula Y no mesmo documento | Apontar ambas, declarar a contradição, não resolver por conta própria |
| Prazo declarado no objeto difere do prazo em cláusula específica | Sinalizar como risco contratual — qual prevalece? |
| Escopo do objeto difere do escopo detalhado em anexo | Sinalizar — o mais restritivo normalmente prevalece, mas precisa de confirmação |
| Especificação técnica conflita com norma referenciada | Apontar e recomendar esclarecimento antes de orçar ou executar |
| Responsabilidade atribuída a duas partes para o mesmo item | Registrar como ambiguidade de alto risco — quem não age pode culpar o outro |

---

## Passo 2 — Extrair os elementos centrais

Mapear obrigatoriamente:

1. **Objeto** — o que de fato está sendo contratado, em uma frase
2. **Escopo incluído** — o que está explicitamente dentro do contrato
3. **Escopo excluído** — o que está explicitamente fora (ausência de exclusão explícita é risco)
4. **Responsabilidades** — o que é do contratado, o que é do contratante, o que é de terceiros
5. **Exigências técnicas** — especificações, normas, certificações, metodologias obrigatórias
6. **Prazos** — início, marcos intermediários, término, prazo de garantia
7. **Penalidades** — multas, retenções, suspensão, rescisão por inadimplência
8. **Critérios de medição e aceite** — como se mede, quem aprova, o que define conclusão
9. **Interfaces com terceiros** — o que depende de outro contratado, projetista ou órgão
10. **Aprovações necessárias** — o que precisa de validação externa antes de ser executado

---

## Passo 3 — Classificar riscos por severidade

Para cada risco identificado, classificar:

- 🔴 **CRÍTICO** — pode inviabilizar a execução, gerar perda financeira relevante ou litígio
- 🟡 **RELEVANTE** — requer esclarecimento ou negociação antes de assinar / executar
- 🟢 **OBSERVAÇÃO** — ponto de atenção sem impacto imediato, mas que deve ser monitorado

### Categorias de risco (verificar todas)

**Risco de prazo:**
- Marcos rígidos sem possibilidade de prorrogação por causa externa
- Aprovações necessárias com prazo não controlado pelo contratado
- Dependência de terceiros sem responsabilidade contratual definida
- Prazo incompatível com mobilização, lead time de materiais ou volume de escopo

**Risco de custo:**
- Item de escopo sem especificação suficiente para orçar com segurança
- Medição por critério subjetivo ou exclusivo da fiscalização
- Responsabilidade transferida ao contratado sem limite definido
- "Ajustes" ou "complementações" sem critério objetivo de custo adicional
- Retenção de pagamento por critério não quantificado

**Risco técnico:**
- Especificação sem norma de referência ou com norma desatualizada
- Desempenho exigido sem critério de ensaio ou medição
- Incompatibilidade entre especificações de diferentes disciplinas
- Execução que depende de projeto executivo não emitido

**Risco contratual:**
- Obrigação aberta ("o contratado deverá prover tudo necessário para...")
- Aceite subjetivo ("a fiscalização poderá rejeitar serviço que não atenda suas expectativas")
- Multa por descumprimento sem limite de acumulação
- Rescisão unilateral sem indenização de mobilização ou custos incorridos
- Cláusula que transfere ao contratado responsabilidade por ato de terceiro

---

## Passo 4 — Traduzir em leitura gerencial

Responder obrigatoriamente, com os dados disponíveis:

1. **O que realmente está sendo contratado?** — o objeto real, não o nome do contrato
2. **O que pode virar problema?** — o risco de maior impacto, não uma lista exaustiva
3. **O que precisa ser esclarecido antes de assinar / participar?** — as ambiguidades que têm consequência
4. **O que o documento está assumindo sem dar segurança?** — omissões que transferem risco silenciosamente
5. **Se eu tivesse que resumir este documento em 3 linhas para um sócio, o que diria?**

> Para cada pergunta: se os dados não permitirem resposta segura, declarar a limitação e
> indicar qual informação resolveria a lacuna.

---

## Passo 5 — Gerar questionamentos formais

Para cada ambiguidade ou omissão que requer esclarecimento, gerar uma linha da tabela:

| # | Disciplina | Ponto obscuro | Impacto potencial | Pergunta formal sugerida |
|---|---|---|---|---|

**Regras de construção dos questionamentos:**
- Uma dúvida por linha — nunca agrupar duas questões na mesma linha
- Linguagem objetiva — a pergunta deve poder ser enviada ao cliente/contratante sem reescrita
- Foco em destravar decisão ou reduzir risco — não questionar o que já está claro
- Evitar pergunta retórica ou de opinião — perguntar o que tem resposta objetiva
- Disciplina: Contratual / Técnico / Prazo / Custo / Interface / Qualidade

---

## Passo 6 — Emitir parecer técnico

Estrutura obrigatória do parecer:

```
PARECER TÉCNICO
Documento analisado: [nome, versão, data]
Objetivo da análise: [decidir participação / revisar antes de assinar / questionar / outro]
Limitações da análise: [o que estava ausente ou ilegível, se houver]

CONCLUSÃO: [recomendação objetiva em 1–2 frases]

RISCO PRINCIPAL: [o risco de maior impacto em 1 frase]

AÇÃO RECOMENDADA ANTES DE PROSSEGUIR:
1. [ação específica]
2. [ação específica]

PONTOS QUE PRECISAM DE NEGOCIAÇÃO OU ESCLARECIMENTO:
[listar apenas o que tem consequência real — não listar para parecer mais completo]
```

---

## Nível de confiança da análise (declarar obrigatoriamente)

| Nível | Critério |
|---|---|
| ALTO | Documento completo, legível, com versão identificada e contexto claro |
| MEDIO | Documento parcial, versão incerta, ou contexto do pedido com premissa assumida |
| BAIXO | Documento incompleto, mal formatado, escaneado com perda de texto, ou seções faltando |

---

## Formato de entrega padrão

```
1. NÍVEL DE CONFIANÇA (Alto/Médio/Baixo + justificativa de 1 linha se Médio/Baixo)
2. RESUMO EXECUTIVO (o que é o documento + risco principal + recomendação — 5 linhas máximo)
3. ELEMENTOS CENTRAIS (objeto, escopo incluído/excluído, responsabilidades, prazos, penalidades)
4. RISCOS CLASSIFICADOS (🔴 Crítico / 🟡 Relevante / 🟢 Observação — com impacto declarado)
5. QUESTIONAMENTOS FORMAIS (tabela pronta para uso)
6. PARECER TÉCNICO (conclusão + ação recomendada)
```

---

## Regras invioláveis

1. Nunca resumir por capítulo. Resumir por impacto — o que muda para quem toma a decisão.
2. Nunca repetir trecho do documento sem interpretação. Copiar sem analisar não é análise.
3. Sempre classificar a severidade dos riscos (Crítico / Relevante / Observação). Sem classificação, tudo parece igualmente urgente.
4. Nunca misturar fato documental com opinião. Separar: "o documento diz X" de "isso representa risco porque Y".
5. Nunca ignorar item mal definido. Ambiguidade sem apontar é omissão do analista.
6. Nunca gerar questionamento que o próprio documento já responde claramente.
7. Sempre declarar o nível de confiança antes do resumo executivo.
8. Sempre declarar as limitações da análise quando o documento estiver incompleto ou ilegível.
9. Nunca recomendar assinar ou não assinar sem ressalvar que a decisão final é do usuário — o parecer informa, não decide.

---

## Arquivos de referência

- references/checklist.md — verificação antes de entregar qualquer análise
- references/matriz-risco.md — critérios detalhados de classificação por categoria e severidade
- references/modelo-questionamentos.md — estrutura e exemplos de questionamentos formais por tipo de documento


---

## INTEGRAÇÃO OPENCLAW

Este skill opera tanto no Cowork (desktop, via usuário) quanto como capacidade da Flávia (agente OpenClaw no VPS).

### Cadeia de integração

```
Contrato / Edital / Proposta / Escopo
        ↓
analista-tecnico-documentos  ←── [este skill]
        ↓
  riscos + questionamentos + parecer
        ↓
  ┌────────────────────────────────────────────┐
  │  redator-executivo-obra                    │  → carta de questionamentos / e-mail formal
  │  orcamentista-medidor-obras                │  → conferência de quantitativos do escopo
  └────────────────────────────────────────────┘
```

### Dispatch via Flávia (OpenClaw)

Quando operado pela Flávia, ao concluir a análise:
1. Salvar resumo de riscos em `/root/.openclaw/workspace/memory/documentos/[slug]-analise.json`
2. Se houver risco 🔴 Crítico: notificar Alexandre via WhatsApp imediatamente
3. Se output incluir questionamentos formais: passar para `redator-executivo-obra` formatar

### Formato do JSON de memória

```json
{
  "documento": "[nome/tipo]",
  "slug": "[slug]",
  "data_analise": "YYYY-MM-DD",
  "tipo": "contrato/edital/proposta/escopo/laudo",
  "riscos_criticos": 0,
  "riscos_relevantes": 0,
  "omissoes_identificadas": 0,
  "questionamentos_gerados": 0,
  "confianca": "Alto/Médio/Baixo",
  "parecer": "Aprovado com ressalvas / Requer negociação / Não assinar sem correções"
}
```

### Notificação WhatsApp (apenas para 🔴 crítico)

```
⚠️ [DOCUMENTO] — Análise Técnica
Risco crítico identificado:
[Descrição em 1 linha]
Impacto: [consequência]
Ação: [o que precisa acontecer]
```

---

*Skill v2.0 — Padrão MENSURA Engenharia 10/10*
