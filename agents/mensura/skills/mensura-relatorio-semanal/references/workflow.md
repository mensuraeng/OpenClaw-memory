# Workflow — mensura-relatorio-semanal

Etapas detalhadas de operação da skill do início ao fim.

## Etapa 1 — Classificar o pedido
Escolher um dos modos:
- Relatório semanal
- Diagnóstico rápido
- Comparativo semanal

## Etapa 2 — Inventariar a base recebida
Responder internamente:
- o que veio completo
- o que veio solto ou incompleto
- o que está ausente e é crítico
- o que impede cálculo confiável
- restrições vencidas sem remoção
- decisões sem resposta há mais de uma semana
- risco crítico sem ação de contenção definida

## Etapa 3 — Tabela de fallback por bloco ausente
| Situação | Ação |
|---|---|
| Bloco A ausente (identificação) | Perguntar: qual obra? qual período? |
| Bloco B ausente (tarefas) | Perguntar: quais atividades foram prometidas? quais foram concluídas? |
| Bloco C ausente (restrições) | Prosseguir sem IRR. Declarar ausência. |
| Bloco D ausente (riscos) | Prosseguir. Omitir seção de riscos ou indicar "não informado". |
| Dados contraditórios | Apontar contradição. Não corrigir por conta própria. Seguir com ressalva. |

## Etapa 4 — Declarar nível de confiança
Classificar a base como:
- Alto
- Médio
- Baixo

## Etapa 5 — Calcular só o que é defensável
- PPC: calcular se houver base de compromisso semanal.
- IRR: calcular só com base clara de restrições.
- IAO: não calcular no MVP, salvo pedido explícito com base suficiente.

## Etapa 6 — Estruturar leitura executiva
Responder:
- o que avançou
- o que travou
- qual o principal risco
- quais decisões estão pendentes
- o que precisa acontecer antes da próxima semana

## Etapa 7 — Gerar a saída
Usar `references/output-template.md`.

Para as primeiras execuções reais, usar `references/exemplo-casa7.md` como referência de formato e tom.