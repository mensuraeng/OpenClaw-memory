# Arquitetura operacional - Mensura Autopilot

## Tese
O Mensura Autopilot é um sistema de acompanhamento proativo de obras e projetos. Ele existe para transformar sinais dispersos em leitura executiva curta, com priorização e ação recomendada.

## Objetivo central
Todos os dias, antes do início da operação, entregar uma leitura clara de:
- o que precisa de atenção
- onde existe risco de prazo, custo ou governança
- o que está parado demais
- quais ações devem ser cobradas ou decididas

## Escopo inicial recomendado
Começar pequeno.

### Portfólio inicial
- CCSP Casa7
- P&G Louveira
- Paranapiacaba
- Paranapiacaba - Paralelepípedo
- Teatro Suzano

## Funções do autopilot
1. Ler status e sinais disponíveis por obra
2. Aplicar checklist executivo padronizado
3. Detectar silêncio operacional
4. Classificar alertas por criticidade
5. Montar resumo matinal consolidado
6. Registrar pendências e exceções relevantes

## Entradas esperadas
O autopilot pode evoluir, mas a primeira versão deve aceitar qualquer combinação de:
- notas operacionais da obra
- status manuais
- atualizações de cronograma
- indicadores ou marcos-chave
- pendências sem atualização
- registros em memória/projeto

## Saídas esperadas
### Saída 1 - relatório executivo diário
Formato curto, com:
- panorama geral
- top alertas
- obras silenciosas
- prioridades do dia
- recomendações objetivas

### Saída 2 - alertas extraordinários
Somente quando houver:
- risco alto
- bloqueio relevante
- obra sem atualização além do limite
- desvio crítico de prazo/governança

## Princípios de desenho
- menos dashboards, mais decisão
- menos texto, mais prioridade
- cada alerta precisa de uma ação recomendada
- separar observação de interpretação
- separar ruído operacional de risco executivo

## Lógica de evolução
### Fase 1
Checklist e relatório diário manualmente alimentado

### Fase 2
Consolidação automática de múltiplas fontes

### Fase 3
Memória de padrões por obra e alertas preditivos mais fortes

## Riscos de implementação
- automação antes de critério
- excesso de alerta sem hierarquia
- mistura de dados sem confiabilidade mínima
- monitorar coisa demais e decidir de menos

## Regra-mãe
Se não ajudar o Alê a decidir mais rápido e com mais clareza às 7h, não entra no autopilot.
