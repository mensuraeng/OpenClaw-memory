---
name: control-tower-cronograma
description: >
  Use este skill SEMPRE que o usuário mencionar: cronograma, lookahead, atraso, baseline x realizado,
  caminho crítico, avanço físico, recuperação de prazo, planejamento de obra, atividades da semana,
  frentes de serviço, marcos contratuais, SPI, desvio de prazo, gargalo, efeito cascata, ou qualquer
  análise de prazo em construção civil. Acionar quando o usuário colar tabelas, MS Project ou listas
  de atividades — contexto de prazo já é suficiente para disparar. NÃO usar quando o foco for redigir
  e-mail/ata (redator-executivo-obra) ou abrir orçamento (orcamentista-medidor-obras). Em pedidos
  híbridos análise+comunicação: este skill entra primeiro; redator entra por último. Planilha ambígua:
  datas+atividades = este skill; preços+quantidades = orcamentista. Entrega: diagnóstico com semáforo,
  threshold relativo, plano de ação com responsável em dois níveis, nível de confiança declarado.
---

# Control Tower de Cronograma

## Visão Geral

Transforma dados brutos de planejamento em diagnóstico executivo, mapa de riscos e plano de ação
acionável. Não descreve o cronograma — interpreta, classifica e recomenda.

---

## Fronteira de ativação

Este skill é o certo quando o núcleo do pedido é **analisar prazo, classificar criticidade ou definir recuperação de cronograma** — e o dado disponível é um cronograma, lookahead, lista de atividades ou relato de obra.

### Quando este skill entra

| Pedido | Este skill? |
|---|---|
| "Analisa esse cronograma e me diz o que está atrasado" | ✅ Sim |
| "Monta o lookahead das próximas 3 semanas" | ✅ Sim |
| "Onde está o caminho crítico da obra?" | ✅ Sim |
| "O que precisa acontecer essa semana para não atrasar?" | ✅ Sim |
| "Analisa o cronograma e já manda e-mail para o cliente" | ⚠️ Híbrido — ver abaixo |
| "Lê essa planilha e me diz os principais problemas" | ⚠️ Ambíguo — ver abaixo |

### Quando outro skill entra primeiro ou no lugar

| Foco central do pedido | Skill correto |
|---|---|
| Redigir e-mail, ata, comunicado ou cobrança | `redator-executivo-obra` |
| Abrir orçamento, medir, conferir quantitativos | `orcamentista-medidor-obras` |

### Pedidos híbridos — regra de sequência

Quando o pedido mistura análise de cronograma com comunicação (ex.: "analisa e manda e-mail para o cliente"):
1. Este skill entra primeiro — diagnóstico, classificação, plano de ação
2. `redator-executivo-obra` entra por último — transforma o diagnóstico em mensagem pronta

### Pedidos ambíguos — planilha sem contexto

Quando o usuário colar uma planilha sem dizer o que é:
- Se tiver colunas de data, atividade, % concluído, predecessor → este skill
- Se tiver colunas de item, unidade, preço, quantidade → `orcamentista-medidor-obras`
- Se não for claro: perguntar "Esta planilha é de cronograma ou de orçamento?"

---

## Passo 1 — Identificar, qualificar e validar a entrada

### 1.1 Qual material foi recebido?

| Tipo de entrada | O que extrair |
|---|---|
| Tabela estruturada (Excel, CSV) | Atividade, início, fim, % concluído, predecessor, responsável |
| Texto colado do MS Project | ID, nome, duração, início, fim, predecessores, % concluído, folga |
| Lista de atividades com datas | Montar linha do tempo implícita; inferir predecessoras por lógica construtiva |
| Relato verbal / narrativa | Extrair fatos declarados; classificar tudo como baixa confiança |
| Sem dados | Solicitar: lista de atividades + data de término contratual |

### 1.2 Regra de decisão: pedir dados vs. prosseguir

| Situação | Decisão |
|---|---|
| Falta data de término contratual | Pedir — sem ela não há desvio calculável |
| Falta lista de atividades | Pedir — sem ela não há cronograma, apenas relato |
| Faltam predecessoras | Prosseguir — declarar que caminho crítico não pode ser confirmado |
| Falta % de avanço em parte das atividades | Prosseguir — usar as que existem, sinalizar lacunas |
| Falta responsável por restrições | Prosseguir — registrar "responsável não identificado" como risco |
| Nenhum dado estruturado, só narrativa | Prosseguir — extrair o que for possível, classificar saída como estimativa de baixa confiança |

Critério geral: pedir quando a ausência torna o output enganoso. Prosseguir quando a ausência
apenas reduz precisão — nesse caso, declarar o nível de confiança.

### 1.3 Verificação de inconsistência interna (obrigatória antes de analisar)

Antes de qualquer análise, verificar se os dados são internamente coerentes:

| Inconsistência | Como identificar | O que fazer |
|---|---|---|
| % avanço > planejado mas término atrasado | Avanço real > baseline mas data de conclusão posterior ao contratual | Apontar contradição — pode indicar baseline manipulada ou medição errada |
| Soma de durações incompatível com prazo total | Sequência lógica excede o prazo contratual mesmo sem atrasos | Declarar: "A estrutura do cronograma não permite cumprir o prazo contratual mesmo sem atrasos adicionais" |
| Atividade 100% concluída com data de início no futuro | % = 100 mas início > data de referência | Sinalizar como erro de lançamento — dado inválido |
| Predecessora com início posterior à sucessora | B começa antes de A terminar sem justificativa | Questionar lógica ou declarar fast-tracking não declarado |
| Baseline alterada sem registro de aditivo | Baseline "atual" diferente de versão anterior sem justificativa formal | Sinalizar possível baseline flutuante — ver seção 8 de references/regras-analise.md |

Se houver inconsistência: não corrigir por conta própria. Apontar explicitamente, continuar
a análise com os dados que fazem sentido, declarar o que foi desconsiderado e por quê.

---

## Passo 2 — Ler a lógica do cronograma

Identificar obrigatoriamente:

1. Prazo total e tipo — obra nova / reforma / ampliação / entrega parcial
2. Data de início e término — contratual, baseline atual, e projeção real se diferente
3. Atividades em andamento — com % avanço real vs. planejado e desvio de ritmo
4. Atividades atrasadas — com desvio em dias e causa identificada ou suspeita
5. Atividades no caminho crítico — folga zero ou negativa; se não identificável, declarar
6. Predecessoras bloqueantes — o que está impedindo o avanço de quê
7. Marcos contratuais — datas com consequência contratual (multa, entrega parcial, vistoria)
8. Frentes liberadas x travadas — o que pode avançar hoje e o que não pode
9. Concentração de risco — frentes ou equipes com múltiplos atrasos simultâneos

REGRA: atividade importante não é atividade crítica.
Crítica = folga zero ou negativa. Qualquer atraso nela atrasa o término na mesma proporção.

REGRA: obra "no prazo" hoje pode ser obra impossível de concluir no prazo.
Verificar sempre se há compressão futura que tornará o prazo inviável mesmo com avanço atual ok.

---

## Passo 3 — Classificar o estado da obra

### Threshold relativo por duração total do projeto

Não usar threshold fixo de dias — usar percentual da duração total:

| Duração total da obra | Desvio para Atenção | Desvio para Crítico |
|---|---|---|
| Até 60 dias | 3+ dias | 7+ dias |
| 61 a 180 dias | 5+ dias | 10+ dias |
| 181 a 365 dias | 7+ dias | 15+ dias |
| Acima de 365 dias | 10+ dias | 20+ dias |

Se não houver dado de duração total: usar o critério 181–365 dias como padrão conservador.

### Classificação por frente/atividade

- SAUDAVEL — dentro do threshold, sem restrição relevante, predecessoras concluídas
- ATENCAO — desvio no threshold de atenção, dependência pendente, ou risco emergente identificado
- CRITICO — desvio no threshold crítico, impacto direto no caminho crítico, ou dependência externa bloqueante sem prazo de resolução

### Critérios para elevar criticidade independentemente do desvio

- Atividade com múltiplas predecessoras não concluídas (gargalo de convergência)
- Risco de efeito cascata ativo (o atraso já contaminou sucessoras)
- Dependência externa sem responsável identificado ou sem prazo de resolução
- Concentração de atividades críticas em mesma frente, equipe ou fornecedor
- Marco contratual a menos de 14 dias com qualquer pendência não resolvida

---

## Passo 4 — Gerar leitura gerencial

Responder obrigatoriamente às 5 perguntas-chave. Para cada uma, se não for possível responder
com os dados disponíveis, declarar qual dado está faltando e qual o impacto dessa lacuna.

1. Onde está o atraso real? — causa raiz, não sintoma. "Estrutura atrasada" é sintoma. "Projeto executivo não emitido" é causa.
2. O que impacta o caminho crítico hoje? — se não identificável formalmente, qual é o gargalo mais provável?
3. O que precisa acontecer nos próximos 7, 14 e 30 dias? — ações concretas, não intenções
4. Quais restrições precisam ser removidas? Por quem? Até quando? — tipificar responsável e dar prazo específico
5. Qual ação de recuperação tem maior relação custo-benefício? — ver estratégias em references/regras-analise.md seção 4

### Nível de confiança da análise (declarar obrigatoriamente na saída)

| Nível | Critério |
|---|---|
| ALTO | Dados estruturados completos, predecessoras identificadas, baseline e real disponíveis |
| MEDIO | Dados parciais, sem predecessoras formais, ou baseline sem histórico de revisões |
| BAIXO | Apenas narrativa, dados contraditórios não resolvidos, ou cronograma sem datas reais |

---

## Passo 5 — Montar plano de ação

### Priorização quando há múltiplos pontos críticos

Se houver mais de um ponto CRITICO, priorizar nesta ordem:
1. O que afeta o próximo marco contratual mais próximo
2. O que tem mais sucessoras bloqueadas (maior efeito cascata)
3. O que depende de agente externo (menor controle = maior urgência de acionamento)
4. O que tem maior desvio acumulado

### Campos obrigatórios por item do plano

| Campo | Critério de preenchimento |
|---|---|
| Problema | Fato objetivável — o que está acontecendo, não julgamento |
| Impacto | Dias de desvio + qual marco é afetado |
| Ação imediata | Verbo específico: "emitir", "convocar", "solicitar", "aprovar" — nunca "acompanhar" |
| Tipo de responsável | Ver tipologia abaixo |
| Responsável sugerido | Cargo, empresa ou nome quando identificável |
| Prazo | Data específica — nunca "em breve", "urgente" ou "o quanto antes" |
| Dependência | O que precisa estar resolvido antes desta ação ter efeito |
| Critério de conclusão | Como saber que esta ação foi cumprida — entregável ou estado verificável |

### Tipologia de responsável (dois níveis)

**Nível 1 — Tipo (obrigatório sempre):**

| Tipo | Quando usar |
|---|---|
| **Obra** | Equipe de execução, encarregados, mestre, frentes de serviço |
| **Cliente** | Aprovações, decisões, pagamentos, mudanças de escopo |
| **Projetista** | Emissão de projeto, resposta a RFI, revisão técnica |
| **Fornecedor** | Entrega de material, equipamento, serviço especializado |
| **Terceiro contratado** | Subempreiteiro, concessionária, órgão público |

**Nível 2 — Subfunção interna da Obra (usar quando a obra tem equipes separadas e a precisão importa):**

| Subfunção | Quando especificar |
|---|---|
| Obra / Planejamento | Quando a ação é de reprogramação, lookahead ou controle de prazo |
| Obra / Suprimentos | Quando a ação é de compra, cotação ou gestão de estoque |
| Obra / Contratos | Quando a ação envolve aditivo, notificação formal ou gestão contratual |
| Obra / Segurança | Quando a ação é de liberação de frente por condição de segurança |

> Regra: em obras pequenas ou sem segregação de funções, usar apenas o Nível 1.
> Em obras com equipes especializadas, adicionar a subfunção quando ela identifica quem age.

---

## Formato de entrega

### Saída padrão (diagnóstico completo)

Entregar nesta sequência:

1. NIVEL DE CONFIANÇA DA ANALISE (Alto/Médio/Baixo + justificativa de 1 linha)
2. RESUMO EXECUTIVO (5 linhas máximo: situação, desvio, risco principal, ação urgente)
3. DIAGNÓSTICO POR FRENTE (semáforo com desvio, causa e impacto por frente)
4. ATIVIDADES CRÍTICAS E ATRASOS (tabela: atividade / planejado / real / desvio / marco afetado)
5. RESTRIÇÕES E RISCOS (tipificadas, com responsável e prazo de remoção)
6. PLANO DE AÇÃO (tabela completa com todos os campos do Passo 5)
7. PRÓXIMOS PASSOS DA SEMANA (máximo 7 itens priorizados com responsável e data)

### Saídas operacionais alternativas

| Pedido | Formato de saída |
|---|---|
| "lookahead", "próximas semanas" | Tabela S1/S2/S3: atividade, frente, % previsto, responsável, pré-requisito, restrição |
| "atividades da semana", "o que vence" | Lista priorizada: status atual + ação necessária + responsável |
| "e-mail de cobrança", "cobrar cliente/projetista/fornecedor" | E-mail executivo: pendências, impacto em dias, prazo-limite, referência contratual |
| "pauta", "reunião de produção" | Pauta com tempo estimado, perguntas por item, tabela de encaminhamentos |
| "resumo para diretoria" | 1 página: situação / risco / decisão necessária / prazo da decisão |

---

## Regras invioláveis

1. Nunca listar atividades sem interpretar impacto. Tabela sem análise não é diagnóstico.
2. Nunca assumir caminho crítico sem evidência. Sem predecessoras, declarar explicitamente.
3. Nunca usar threshold fixo de dias sem considerar o prazo total da obra.
4. Nunca usar linguagem vaga: "acompanhar", "monitorar", "verificar" proibidos sem especificar o quê, quando e com qual critério de conclusão.
5. Sempre tipificar o responsável em Nível 1 (Obra / Cliente / Projetista / Fornecedor / Terceiro). Adicionar subfunção de Nível 2 quando a obra tiver equipes segregadas e a precisão importar.
6. Sempre declarar o nível de confiança da análise antes do resumo executivo.
7. Nunca corrigir inconsistência interna por conta própria — apontar e prosseguir com o que é coerente.
8. Dependências externas são sempre destacadas — principal vetor de atraso fora do controle da obra.
9. Nunca omitir risco para evitar má notícia — o papel do control tower é antecipar, não confirmar.

---

## Arquivos de referência

- references/checklist.md — checklist de validação antes de entregar qualquer saída
- references/output-modelos.md — modelos prontos para cada tipo de saída
- references/regras-analise.md — caminho crítico, efeito cascata, recuperação, restrições, indicadores, baseline manipulada


---

## INTEGRAÇÃO OPENCLAW

Este skill opera tanto no Cowork (desktop, via usuário) quanto como capacidade da Flávia (agente OpenClaw no VPS).

### Cadeia de integração

```
MS Project / Excel / Relato
        ↓
control-tower-cronograma  ←── [este skill]
        ↓
  diagnóstico + plano de ação
        ↓
  ┌─────────────────────────────────────────┐
  │  opção A: redator-executivo-obra        │  → e-mail / ata / WhatsApp para cliente
  │  opção B: relatorio-preditivo-obras     │  → relatório preditivo completo
  │  opção C: mensura-os-torre-controle     │  → atualização no MENSURA OS
  └─────────────────────────────────────────┘
```

### Dispatch via Flávia (OpenClaw)

Quando operado pela Flávia, ao concluir o diagnóstico:
1. Salvar KPIs calculados em `/root/.openclaw/workspace/memory/obras/[slug]-cronograma.json`
2. Se houver desvio crítico (🔴): notificar Alexandre via WhatsApp com resumo de 3 linhas
3. Se output for para cliente: passar para `redator-executivo-obra` formatar a comunicação

### Formato do JSON de memória (KPIs)

```json
{
  "obra": "[nome]",
  "slug": "[slug]",
  "data_analise": "YYYY-MM-DD",
  "avanco_fisico": 0.0,
  "avanco_tempo": 0.0,
  "desvio_dias": 0,
  "spi": 0.0,
  "bei": 0.0,
  "status_semaforo": "🔴/🟡/🟢",
  "criticos": ["atividade1", "atividade2"],
  "confianca": "Alto/Médio/Baixo"
}
```

### Notificação WhatsApp (apenas para 🔴 crítico)

```
⚠️ [OBRA] — Torre de Controle
Situação: 🔴 CRÍTICO
Avanço: [X]% / Previsto: [Y]%
Desvio: [Z] dias | SPI: [valor]
Ação urgente: [1 linha]
```

---

*Skill v2.0 — Padrão MENSURA Engenharia 10/10*
