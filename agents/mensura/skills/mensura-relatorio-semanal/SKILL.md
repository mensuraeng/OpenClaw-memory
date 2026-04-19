---
name: mensura-relatorio-semanal
description: Gera relatórios semanais de obra no padrão MENSURA. Use quando o usuário pedir: relatório semanal, fechamento da semana, semanal da obra, como foi a semana, monta o semanal, fecha o relatório, diagnóstico rápido, o que está travando, por que está atrasando, compara essa semana com a passada, calcula PPC, calcula IRR, consolidação de ações com responsável e prazo, ou um resumo executivo acionável da semana da obra. Também acione quando o pedido vier em linguagem informal com o mesmo sentido.
---

# mensura-relatorio-semanal

Use esta skill para transformar dados semanais de **uma obra por vez** em relatório executivo padronizado, rastreável e acionável.

## Objetivo do MVP

Entregar rapidamente um relatório semanal útil e confiável, sem depender ainda do sistema operacional completo multiobras.

O foco do MVP é:
- ler dados da semana
- validar suficiência e consistência mínimas
- calcular PPC
- calcular IRR quando houver base suficiente
- destacar travas, riscos e decisões pendentes
- gerar ações com responsável e prazo

## Escopo desta skill

### Faz no MVP
- Relatório semanal completo de uma obra
- Diagnóstico rápido da semana
- Comparativo simples entre semana atual e anterior
- Cálculo de PPC
- Cálculo de IRR quando houver base mínima
- Leitura executiva de travas, atrasos de decisão e risco operacional

### Não faz no MVP
- Portfólio multiobras completo
- Auditoria estrutural de bancos e relações
- Construção do sistema completo MENSURA OS
- Importação automática de MS Project
- Motor preditivo completo com DCMA/EVM avançado
- Ranking consolidado por engenheiro em múltiplas obras

Se o pedido depender fortemente desses itens, responda com a limitação e entregue a melhor versão parcial possível.

## Demarcação com outras skills

| Pedido | Skill correta |
|---|---|
| Relatório semanal, fechamento Lean | mensura-relatorio-semanal (esta skill) |
| Diagnóstico rápido da semana | mensura-relatorio-semanal (esta skill) |
| Comparativo semanal | mensura-relatorio-semanal (esta skill) |
| Monitoramento proativo diário de obras | mensura-autopilot |
| Checklist diário executivo | mensura-autopilot |

Dúvida: se o pedido for sobre o dia a dia ou monitoramento contínuo, usar `mensura-autopilot`. Se for sobre fechamento, relatório ou diagnóstico da semana, usar esta skill.

## Ordem de operação

### Etapa 1 — Classificar o pedido

Classificar antes de qualquer saída:
- RELATÓRIO SEMANAL
- DIAGNÓSTICO RÁPIDO
- COMPARATIVO SEMANAL

### Etapa 2 — Inventariar os dados recebidos

Responder internamente antes de qualquer cálculo:
- o que veio solto ou incompleto
- o que está ausente e é crítico
- restrições vencidas sem remoção
- decisões sem resposta há mais de uma semana
- risco crítico sem ação de contenção definida

| Situação | Ação |
|---|---|
| Bloco A ausente (identificação) | Perguntar: qual obra? qual período? |
| Bloco B ausente (tarefas) | Perguntar: quais atividades foram prometidas? quais foram concluídas? |
| Bloco C ausente (restrições) | Prosseguir sem IRR. Declarar ausência. |
| Bloco D ausente (riscos) | Prosseguir. Omitir seção de riscos ou indicar "não informado". |
| Bloco E ausente (decisões) | Prosseguir. Indicar "decisões não informadas". |
| Dados contraditórios | Apontar contradição. Não corrigir por conta própria. Seguir com ressalva. |

### Etapa 3 — Declarar nível de confiança

Antes de calcular qualquer KPI ou concluir leitura executiva, declarar o nível de confiança da base.

### Etapa 4 — Calcular somente os KPIs defensáveis

### Etapa 5 — Identificar travas, riscos e decisões pendentes

### Etapa 6 — Gerar a saída no template adequado

Ver `references/output-template.md`.

## Modos

### 1. RELATÓRIO SEMANAL
Use quando o usuário pedir o fechamento semanal da obra.

Entrega:
- nível de confiança
- resumo da semana
- KPIs disponíveis
- travas principais
- riscos ativos
- decisões pendentes
- próximos passos

### 2. DIAGNÓSTICO RÁPIDO
Use quando o usuário pedir leitura curta do que está travando a obra ou por que a semana degradou.

Entrega:
- máximo 5 parágrafos curtos ou bullets densos
- top 3 travas
- impacto operacional
- top 3 ações urgentes

### 3. COMPARATIVO SEMANAL
Use quando o usuário trouxer dados da semana atual e da anterior.

Entrega:
- melhorou, estabilizou ou piorou
- o que avançou
- o que travou
- ações não executadas
- decisão crítica para a próxima semana

## Entradas mínimas

Leia `references/input-template.md` quando precisar orientar o usuário ou estruturar a entrada.

### Obrigatórias para relatório minimamente útil
- nome da obra
- data do relatório
- período analisado
- responsável pela obra ou engenheiro
- lista de atividades planejadas na semana
- lista de atividades concluídas na semana ou marcação equivalente
- lista de atividades não concluídas ou bloqueadas

### Recomendadas
- restrições abertas e removidas
- riscos ativos
- decisões pendentes
- status da semana anterior

## Regras de decisão

### Se faltarem dados essenciais
Peça somente o mínimo necessário.

Perguntas prioritárias:
- qual obra?
- qual período?
- quais atividades foram prometidas para a semana?
- quais foram concluídas?
- o que travou?

### Se os dados vierem parciais
Prossiga com análise parcial.

- não trave sem necessidade
- calcule apenas o que for defensável
- declare explicitamente o que ficou fora

### Se houver contradição
Não corrija por conta própria.

Exemplos:
- atividade marcada como concluída e bloqueada ao mesmo tempo
- atividade fora da semana entrando no PPC
- restrição sem data e tratada como vencida

Aponte a contradição, preserve o dado original e siga com ressalva.

## KPIs

Leia `references/kpis.md` para as fórmulas e critérios.

### PPC
Calcule sempre que houver base mínima.

### IRR
Calcule somente se houver lista de restrições com status de remoção.

### IAO
Não calcular no MVP, salvo se o usuário trouxer base específica e pedir explicitamente. Nesse caso, classifique como leitura experimental e explique a limitação.

## Saídas

Leia `references/output-template.md` antes de montar a resposta final.

Sempre devolver:
- fatos relevantes da semana
- leitura executiva honesta
- itens críticos com responsável
- prazo ou ausência de prazo
- recomendação prática da próxima ação

## Regras invioláveis

Leia `references/rules.md` e siga sem exceção.

## Estilo de escrita

Escrever no padrão MENSURA:
- direto
- técnico
- sem floreio
- sem linguagem de consultoria genérica
- sem suavizar atraso, omissão ou risco

Exemplos corretos:
- Item sem definição após três cobranças. Risco direto de travamento da frente.
- A obra perdeu cadência por dependência externa não resolvida.
- PPC abaixo do aceitável para uma semana com baixo volume de compromisso.

Exemplos errados:
- Há oportunidade de alinhamento.
- Existe atenção moderada em alguns itens.
- Recomenda-se observação próxima do cenário.

## Referências

- `references/input-template.md`
- `references/kpis.md`
- `references/output-template.md`
- `references/rules.md`
- `references/exemplo-casa7.md` — relatório de exemplo preenchido com dados reais. Carregar quando precisar calibrar formato ou checar padrão de saída.
- `references/workflow.md` — etapas detalhadas de operação e tabela de fallback por bloco ausente. Carregar quando precisar orientar o fluxo de processamento.

Use `references/exemplo-casa7.md` como âncora de formato para as primeiras execuções reais.
Use `references/workflow.md` quando precisar seguir o fluxo operacional resumido da skill ponta a ponta.

Carregue apenas o arquivo necessário para o pedido em questão.