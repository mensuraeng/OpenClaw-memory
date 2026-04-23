---
name: mensura-os-torre-controle
description: >
  Use este skill SEMPRE que o usuário mencionar: MENSURA OS, SISTEMA MENSURA, Torre de Controle,
  sistema operacional de obras, portfólio multiobras, Last Planner System, Look Ahead, PPC, IRR,
  IAO, Lean Construction, semana Lean, restrições de obra, cronograma como base-mãe, indicadores
  por obra, indicadores por engenheiro, autonomia operacional, banco de tarefas, banco de
  restrições, banco de riscos, atas de obra, semanas Lean, ou qualquer pedido de estruturação,
  auditoria ou operação do MENSURA OS. Acionar quando o usuário importar cronograma, pedir
  diagnóstico de portfólio ou relatório Lean. NÃO usar para análise de cronograma isolado
  (control-tower-cronograma), orçamento (orcamentista-medidor-obras), comunicação
  (redator-executivo-obra) ou contrato (analista-tecnico-documentos). Entrega: relatório completo
  com diagnóstico, arquitetura, fórmulas KPI, auditoria documentada e próximos passos — pronto
  para implementação.
---

# MENSURA OS — Torre de Controle

## Visão Geral

Sistema Operacional de Obras da MENSURA. Permite operar múltiplas obras simultaneamente com
visão consolidada de portfólio, cronograma como base-mãe, controle Lean semanal, gestão de
restrições, riscos, atas, indicadores por obra e por engenheiro.

Este skill constrói, audita e opera o sistema — produzindo relatório completo estruturado
como saída, implementável em qualquer plataforma (Claude, planilha, ferramenta de gestão).

---

## Fronteira de ativação

### Quando este skill entra

| Pedido | Este skill? |
|---|---|
| "Audita o MENSURA OS e me diz o que está errado" | ✅ Sim |
| "Monta o relatório semanal Lean da obra X" | ✅ Sim |
| "Calcula PPC, IRR e IAO com esses dados" | ✅ Sim |
| "Estrutura o banco de tarefas para importar do MS Project" | ✅ Sim |
| "Gera o dashboard executivo do portfólio" | ✅ Sim |
| "Analisa as restrições abertas e me diz o risco" | ✅ Sim |
| "Qual engenheiro está com pior IAO?" | ✅ Sim |

### Quando outro skill entra no lugar ou primeiro

| Foco central do pedido | Skill correto |
|---|---|
| Análise técnica de cronograma isolado sem contexto MENSURA OS | `control-tower-cronograma` |
| Orçamento, medição, quantitativos | `orcamentista-medidor-obras` |
| Redigir relatório, e-mail ou ata | `redator-executivo-obra` |
| Analisar contrato, edital ou escopo | `analista-tecnico-documentos` |

### Pedidos híbridos — sequência

Quando o pedido mistura análise do sistema com comunicação:
1. Este skill gera o diagnóstico e os dados
2. `redator-executivo-obra` formata a comunicação para cliente ou diretoria

---

## Missão do sistema

O MENSURA OS deve permitir:
- Visão consolidada de portfólio multiobras
- Cronograma como base-mãe (MS Project → sistema)
- Controle Lean semanal com compromisso real
- Gestão de restrições com responsável e prazo
- Gestão de riscos com score automático
- Atas vinculadas à execução
- Indicadores PPC, IRR e IAO por obra e por engenheiro
- Autonomia operacional — redução da dependência do Diretor
- Estrutura pronta para Power BI

---

## Princípios inegociáveis (18 regras)

1. MS Project = planejamento técnico. Claude / sistema = execução, Lean, governança, inteligência
2. Não criar um sistema por obra — databases globais com views filtradas por obra
3. Toda obra vive dentro do mesmo sistema
4. Cronograma é base-mãe — 02 Tarefas é o banco central
5. Look Ahead não é só data — é prontidão real
6. Semana Execução nunca é gerada automaticamente pelo baseline — é compromisso humano
7. PPC mede compromisso semanal (concluídas / planejadas)
8. IRR mede remoção de restrições (removidas / total do horizonte)
9. IAO mede autonomia operacional com fórmula proporcional e validação de integridade (% Autonomia = -1 quando Decisões Totais = 0)
10. Risco não nasce automaticamente do cronograma sem validação humana
11. Ata não nasce do cronograma — nasce da reunião
12. Nenhum KPI crítico deve ser manual se puder ser fórmula ou rollup
13. Se houver algo correto, preservar. Se errado, corrigir cirurgicamente
14. Nunca recriar do zero sem necessidade
15. Nunca apagar histórico sem necessidade
16. Nunca duas colunas com a mesma função
17. Nunca automatizar decisão humana estratégica
18. Nunca transformar baseline em compromisso Lean

---

## 4 Níveis de análise

| Nível | Público | Responde |
|---|---|---|
| 1 — Operação de Campo | Engenheiro / Mestre | O que executar esta semana? O que está atrasado? Travado? Crítico? |
| 2 — Lean / Confiabilidade | Planejador | O que foi prometido e não entregue? Restrições não removidas? PPC confiável? |
| 3 — Gestão de Obra | Gestor / Coordenador | Qual obra está em risco? Gargalo de execução? Quais decisões subiram ao Diretor? |
| 4 — Diretoria / Portfólio | Diretor | Quais obras exigem intervenção? Pior PPC/IRR? Onde ainda há dependência do Diretor? |

---

## Passo 1 — Identificar modo de operação

Antes de qualquer ação, classificar o que o usuário está pedindo:

| Modo | Quando usar |
|---|---|
| **AUDITORIA** | Usuário tem sistema existente e quer diagnóstico de erros, duplicidades, relações quebradas |
| **CONSTRUÇÃO** | Usuário está estruturando o sistema do zero ou adicionando um banco novo |
| **OPERAÇÃO** | Usuário tem dados e quer rodar o ciclo semanal Lean (importar, calcular, fechar semana) |
| **RELATÓRIO** | Usuário quer output executivo — dashboard, portfólio, desempenho de engenheiro |
| **DIAGNÓSTICO** | Usuário descreve uma situação de obra e quer leitura gerencial via MENSURA OS |
| **DIAGNÓSTICO RÁPIDO** | Usuário quer leitura condensada ("o que está travando", "por que está atrasando") — máximo 5 parágrafos + top 3 ações urgentes |
| **CENÁRIO DE TESTE** | Usuário quer validar o sistema com dados fictícios P&G — executar cenário completo e verificar se IAO = 0.597 |

### Estratégia de ingestão de dados por volume

| Volume | Estratégia |
|---|---|
| Até 80 atividades | Colar dados completos em tabela markdown ou CSV |
| 80–300 atividades | Segmentar por sistema ou etapa — enviar por blocos com rótulo ("Bloco 1/4 — Estrutura") |
| Mais de 300 atividades | Enviar apenas: atividades críticas + horizonte W+0..W+3 + atividades vencidas. Informar total para contexto |

Para cada bloco: confirmar recebimento e aguardar instrução antes de analisar.

### Regra de decisão: pedir informação vs. prosseguir

| Situação | Decisão |
|---|---|
| Não há dados de obra identificada | Pedir: "Qual obra e qual período?" |
| Não há dados de tarefas ou cronograma | Prosseguir com estrutura vazia — entregar template para preenchimento |
| Dados parciais (algumas tarefas sem %, sem datas) | Prosseguir — calcular o que for possível, sinalizar lacunas |
| Dados contraditórios (% concluído vs. status) | Prosseguir — apontar contradição, não resolver por conta própria |
| Modo AUDITORIA sem descrição do que existe | Pedir descrição mínima antes de auditar |

---

## Passo 2 — AUDITORIA (quando modo = AUDITORIA)

Antes de qualquer correção, executar nesta ordem:

1. **Mapear o que existe** — quais bancos, campos, relações, views
2. **Identificar erros estruturais** — campos com função errada, tipos incorretos, fórmulas quebradas
3. **Identificar duplicidades** — dois campos com a mesma função, dois bancos sobrepostos
4. **Identificar relações quebradas** — relation que aponta para banco errado ou inexistente
5. **Identificar campos manuais onde deveriam existir fórmulas** — KPI que depende de entrada manual evitável
6. **Identificar campos inúteis** — colunas sem uso, sem preenchimento, sem relação
7. **Só então propor correções** — cirurgicamente, preservando o que está correto

### Saída da auditoria

Produzir sempre em 4 blocos fixos:

**Bloco 1 — Diagnóstico Atual**
- O que existe (bancos, campos, relações, views mapeados)
- O que está correto (preservar)
- O que está incorreto (com descrição do erro)
- O que está incompleto
- O que está redundante ou sem função

**Bloco 2 — Ações Prioritárias**
Listar em ordem de prioridade — o que travar mais o sistema vem primeiro:
1. [ação] — [impacto operacional se não corrigido]
2. ...

**Bloco 3 — Execução Realizada**
- Campos criados / corrigidos / arquivados
- Relações corrigidas
- Fórmulas aplicadas
- Views criadas
- Itens ocultados das views operacionais

**Bloco 4 — Critério de Aceite**
- O que já atende
- O que ainda falta
- O que foi testado
- O que ainda depende de validação humana

Produzir também o **AUDITORIA — Mapa Atual** com:

```
AUDITORIA — MAPA ATUAL
Data de referência: [data]

O QUE JÁ EXISTIA E FOI MANTIDO:
- [item] — [justificativa de manutenção]

O QUE FOI CORRIGIDO:
- [item] — [erro original] → [correção aplicada]

O QUE FOI ARQUIVADO:
- [item] — [motivo]

O QUE FOI CRIADO:
- [item] — [função]

O QUE AINDA DEPENDE DE VALIDAÇÃO HUMANA:
- [item] — [por quê não pode ser automatizado]
```

---

## Passo 3 — CONSTRUÇÃO (quando modo = CONSTRUÇÃO)

Executar nesta sequência (ordem obrigatória):

1. **02 — Tarefas** (base-mãe — construir primeiro)
2. **08 — Semanas Lean** (KPI semanal)
3. **03 — Look Ahead / Restrições**
4. **01 — Obras** (portfólio — recebe rollups de todos)
5. **04 — Riscos**
6. **05 — Atas & Reuniões**
7. **06 — Equipe / Engenheiros**
8. **00 — Dashboard Executivo** (view de leitura — construir por último)

Para cada banco, entregar nos mesmos 4 blocos (Diagnóstico / Ações / Execução / Aceite):
- Lista de campos com tipo, função e regra de preenchimento
- Relações obrigatórias com outros bancos
- Fórmulas calculadas (ver `references/formulas-kpi.md`)
- Views obrigatórias com critério de filtro
- Regra de quem preenche e quando
- Campos a ocultar nas views operacionais (relations reversas, fórmulas auxiliares, IDs)

Ver `references/arquitetura-sistema.md` para schema completo de cada banco.

---

## Passo 4 — OPERAÇÃO: ciclo semanal Lean

### Etapa 1 — Entrada do cronograma (importação)

Receber dados do MS Project / Excel e mapear para banco 02 — Tarefas:
- Verificar campos obrigatórios: Atividade, Obra, Início Baseline, Fim Baseline, % Concluído
- Calcular automaticamente: Semana ISO, LookAhead Slot, Atraso?, Prazo Restante, Concluída no Prazo?
- Sinalizar lacunas — campos ausentes ou contraditórios

### Etapa 2 — Preparação do Look Ahead

Identificar candidatas ao horizonte W+0..W+3:
- Status ≠ Concluída
- Fim Baseline dentro das próximas 3 semanas
- Para cada candidata: verificar se há restrição aberta em 03

### Etapa 3 — Reunião semanal Lean (decisão humana — nunca automatizar)

O planejador deve:
- Revisar candidatas do Look Ahead
- Escolher compromisso real da semana → definir Semana Execução
- Marcar Status = Liberada nas tarefas comprometidas
- Marcar Restrição? = true quando houver impedimento real
- Registrar restrição em 03 com tipo, responsável e data limite

### Etapa 4 — Fechamento da semana

Calcular e registrar em 08 — Semanas Lean:
- PPC = Concluídas / Planejadas
- IRR = Restrições removidas / Total de restrições do horizonte
- Críticas Atrasadas = count de tarefas críticas com status Atrasada
- Restrições Vencidas = count de restrições com Data Limite vencida e Removida? = false
- Decisões Escalonadas = registradas em 05 — Atas com flag Escalonada ao Diretor?
- IAO = fórmula composta (ver `references/formulas-kpi.md`)

### Etapa 5 — Consolidação no portfólio

01 — Obras recebe via rollup:
- PPC Atual (da semana mais recente)
- IRR Atual
- IAO Atual
- Risco Global = max(Score Aberto) dos riscos da obra

---

## Passo 5 — RELATÓRIO

### Saída padrão — Relatório Executivo Completo

Ver template em `references/modelo-relatorio.md`.

Estrutura obrigatória:

```
1. NÍVEL DE CONFIANÇA DOS DADOS (Alto/Médio/Baixo + justificativa)
2. RESUMO DO PORTFÓLIO (situação geral, obras em alerta, destaques)
3. SITUAÇÃO POR OBRA (semáforo + PPC + IRR + IAO + risco principal)
4. ANÁLISE LEAN (PPC consolidado, restrições abertas, causas de não cumprimento)
5. GESTÃO DE RISCOS (críticos, vencidos, por categoria)
6. DESEMPENHO DA EQUIPE (IAO por engenheiro, faixa, tendência)
7. DECISÕES PENDENTES (o que está subindo ao Diretor e não deveria)
8. PRÓXIMOS PASSOS (ações com responsável e prazo)
```

### Saídas alternativas

| Pedido | Saída |
|---|---|
| "Situação da obra X" | Ficha da obra: PPC/IRR/IAO + restrições abertas + riscos ativos + próximas tarefas críticas |
| "Como está o engenheiro Y?" | Ficha do engenheiro: obras, PPC médio, IRR médio, IAO atual, faixa, tendência |
| "Restrições abertas" | Tabela por obra + responsável + data limite + dias de atraso |
| "Riscos críticos" | Tabela score >= 15 + estratégia + status + vencido? |
| "PPC do portfólio" | Tabela por obra + por semana + tendência + causa raiz de não cumprimento |

---

## Passo 6 — DIAGNÓSTICO DE OBRA

Quando o usuário descrever uma situação de obra sem dados estruturados:

1. Classificar nos 4 níveis de análise
2. Identificar qual KPI está em risco (PPC, IRR, IAO, Score de risco)
3. Aplicar os princípios inegociáveis para validar se o sistema está sendo usado corretamente
4. Recomendar ação específica com responsável tipificado

Ver tipologia de responsável: Obra / Planejamento / Suprimentos / Cliente / Projetista / Fornecedor / Diretor

---

## Regras invioláveis de operação

1. Semana Execução nunca é gerada pelo baseline — sempre decisão do planejador na reunião
2. Risco nunca nasce automaticamente do cronograma — requer validação gerencial
3. Ata nunca substitui decisão registrada — toda decisão relevante deve estar em 05
4. PPC é compromisso, não execução espontânea — só conta o que foi prometido e entregue
5. IRR mede o sistema de remoção de restrições, não a sorte
6. IAO nunca deve ser manipulado — é o espelho da autonomia real
7. Nenhum KPI crítico deve depender de entrada manual se puder ser calculado
8. Toda inconsistência deve ser apontada — nunca corrigida por conta própria
9. Declarar nível de confiança dos dados antes de qualquer relatório
10. Relatório incompleto por dados insuficientes é melhor que relatório falso por dados inventados
11. IAO com Decisões Totais = 0 retorna % Autonomia = -1 (flag de dado ausente, não autonomia máxima). IAO exibido com asterisco (*) quando Dados Válidos? = false. Sempre verificar antes de usar IAO como indicador de desempenho.

---

## Critério de aceite do sistema (10/10)

O sistema só está 100% quando:
- Cronograma funcionando como base-mãe (02 alimenta tudo)
- Cálculos automáticos corretos (LookAhead Slot, Atraso, Semana ISO)
- O que requer decisão humana não está automatizado indevidamente
- Todas as relações entre bancos estão corretas e bidirecionais
- Todas as fórmulas de KPI estão corretas (PPC, IRR, IAO, Score)
- Todas as views obrigatórias existem e filtram corretamente
- Teste final (P&G com 3 tarefas, 2 restrições, 2 riscos, 1 ata, 1 semana, 1 engenheiro) passa
- Auditoria documentada em AUDITORIA — Mapa Atual

---

## Arquivos de referência

- references/arquitetura-sistema.md — schema completo dos 10 bancos: campos, tipos, relações, views
- references/formulas-kpi.md — todas as fórmulas: LookAhead Slot, Atraso, PPC, IRR, IAO, Score de risco
- references/checklist.md — checklist de auditoria e critério de aceite por banco
- references/modelo-relatorio.md — template do relatório executivo completo


---

## INTEGRAÇÃO OPENCLAW

Este skill opera tanto no Cowork (desktop, via usuário) quanto como capacidade da Flávia (agente OpenClaw no VPS). O MENSURA OS É a estrutura central do OpenClaw — este skill é o coração do sistema.

### Cadeia de integração

```
MS Project (base-mãe)
        ↓
mensura-os-torre-controle  ←── [este skill]
        ↓
  PPC / IRR / IAO / Score por obra e engenheiro
        ↓
  ┌────────────────────────────────────────────────────┐
  │  control-tower-cronograma   │  análise por obra    │
  │  relatorio-preditivo-obras  │  relatório semanal   │
  │  redator-executivo-obra     │  comunicação cliente │
  │  Mission Control dashboard  │  visualização web    │
  └────────────────────────────────────────────────────┘
```

### Dispatch via Flávia (OpenClaw)

Quando operado pela Flávia:
1. Após semana Lean: salvar KPIs em `/root/.openclaw/workspace/memory/mensura-os/semana-[ISO].json`
2. PPC < 70%: notificar Alexandre via WhatsApp com resumo do portfólio
3. IAO < 60% em qualquer engenheiro: flag automático no relatório executivo
4. Sincronizar com Mission Control via endpoint `/api/mensura-os/update`

### Formato do JSON de memória (semana Lean)

```json
{
  "semana_iso": "YYYY-WXX",
  "data_registro": "YYYY-MM-DD",
  "portfolio": {
    "obras_ativas": 0,
    "ppc_medio": 0.0,
    "irr_medio": 0.0,
    "iao_medio": 0.0
  },
  "obras": [
    {
      "slug": "[slug]",
      "ppc": 0.0,
      "irr": 0.0,
      "restricoes_abertas": 0,
      "tarefas_comprometidas": 0,
      "tarefas_concluidas": 0
    }
  ],
  "engenheiros": [
    { "nome": "[nome]", "iao": 0.0, "tarefas": 0, "ppc": 0.0 }
  ]
}
```

### Notificação WhatsApp (PPC crítico)

```
📊 MENSURA OS — Semana [ISO]
Portfólio: [N] obras ativas
PPC médio: [X]% ⚠️
Pior obra: [nome] — PPC [Y]%
Engenheiro atenção: [nome] — IAO [Z]%
```

---

*Skill v2.0 — Padrão MENSURA Engenharia 10/10*
