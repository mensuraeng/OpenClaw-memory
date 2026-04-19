# Runtime seguro do Capability Evolver para o workspace do Alê

## Objetivo
Usar o Evolver como camada de melhoria contínua controlada para skills internas, sem autonomia irrestrita e sem acoplamento à rede externa.

## Modo de operação aprovado
- Execução manual e pontual
- Preferência por `node index.js run` seguido de revisão humana
- Estratégia fixa: `harden`
- Bridge desabilitada
- Worker pool desabilitado
- Auto issue desabilitado
- Self modify desabilitado
- Rollback em `stash`

## Casos de uso prioritários
1. Refinar skills de análise de cronograma e relatórios preditivos
2. Detectar padrões de erro recorrente em execuções reais
3. Gerar base auditável de melhorias reutilizáveis
4. Consolidar aprendizado por tipo de projeto, cliente e saída esperada

## Casos de uso proibidos
- Rodar em loop permanente sem supervisão
- Habilitar worker pool
- Habilitar auto publicação externa
- Permitir autoedição do próprio Evolver
- Tratar saída do Evolver como mudança já aprovada

## Rotina recomendada
1. Executar após lote relevante de sessões ou erros recorrentes
2. Revisar sinais identificados
3. Selecionar apenas melhorias pequenas e reversíveis
4. Validar manualmente antes de incorporar na skill alvo
5. Registrar o aprendizado útil nas skills reais do workspace

## Interpretação correta
O Evolver não substitui tua direção técnica. Ele organiza hipóteses de melhoria com trilha auditável. O ganho está em reduzir retrabalho de refinamento, não em delegar decisão.
