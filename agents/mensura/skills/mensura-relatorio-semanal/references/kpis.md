# KPIs do MVP — mensura-relatorio-semanal

## 1. PPC

### Fórmula
PPC = atividades concluídas na semana / atividades planejadas na semana

### Regras
- Contar apenas o que foi explicitamente prometido para a semana.
- Não contar execução espontânea fora do compromisso.
- Se não houver atividades planejadas, não forçar PPC = 100%.
- Nessa situação, declarar: "PPC não calculável, semana sem base de compromisso válida."

### Leitura sugerida
- >= 0,85: aceitável
- 0,70 a 0,84: atenção
- < 0,70: ruim

Não tratar faixas como verdade absoluta. O contexto importa.

## 2. IRR

### Fórmula
IRR = restrições removidas no período / total de restrições do horizonte analisado

### Base mínima
Só calcular se houver, no mínimo:
- lista identificável de restrições
- status removida sim/não
- janela temporal coerente

### Regras
- Não estimar remoção por inferência indireta.
- Restrição sem status claro não entra como removida.
- Se a base vier confusa, declarar IRR como não confiável.

### IRR = indefinido
Situação: não há base suficiente de restrições para cálculo confiável.

Reportar como:
- IRR não calculado neste relatório.
- IRR indefinido por ausência ou inconsistência da base de restrições.

### Leitura sugerida
- >= 0,80: bom nível de remoção
- 0,60 a 0,79: atenção
- < 0,60: sistema de destravamento fraco

## 3. IAO

IAO não é KPI padrão do MVP.

### Regra
- Não calcular no MVP, salvo pedido explícito com base suficiente.
- Só usar se o usuário trouxer explicitamente uma base consistente de decisões resolvidas na obra versus decisões escaladas.
- Se usar, declarar como leitura experimental do MVP.
- Reportar como: IAO não calculado neste relatório.
- Nunca reportar IAO = 0 quando a causa for ausência de dados.

## 4. Nível de confiança dos dados

### Alto
- base semanal clara
- atividades identificáveis
- restrições e pendências coerentes
- sem contradições relevantes

### Médio
- há lacunas parciais
- KPIs saem com ressalva
- leitura executiva ainda é defensável

### Baixo
- base parcial ou contraditória
- leitura válida apenas para diagnóstico preliminar
- relatório sai parcial e sem firmeza KPI

## 5. Exceções que devem sempre ser destacadas
- atividade prometida e não concluída
- restrição vencida e não removida
- decisão pendente sem resposta após múltiplas cobranças
- risco ativo sem ação de contenção
- ação combinada na semana anterior e não executada

## Casos especiais e regras de nulidade

### PPC = 0
Situação: todas as atividades prometidas não foram concluídas.

Reportar como:
- PPC = 0/N = 0%.
- Não omitir. É dado real e relevante.

### PPC não calculável
Situação: não há atividades registradas como prometidas para a semana.

Reportar como:
- PPC não calculável, nenhuma atividade foi comprometida para esta semana.

Atenção:
- isso pode indicar ausência de reunião Lean ou de registro de compromisso.

### IRR não calculável
Situação: não há restrições registradas no horizonte.

Reportar como:
- IRR não calculável, nenhuma restrição registrada no período.

### IAO = -1
Situação: Decisões Totais = 0, nenhuma decisão registrada no período.

Significado:
- dado inválido, não indica autonomia real, indica ausência de registro.

Reportar como:
- IAO = -1, dado inválido, Decisões Totais = 0.
- Não interpretar como autonomia nula.

Ação recomendada:
- verificar se houve decisões não registradas ou se o período foi inativo.

### IAO não calculável no MVP
- manter a regra padrão do MVP.
- só calcular sob pedido explícito e com base suficiente.