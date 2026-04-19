# Daily runbook - Mensura Autopilot

## Objetivo
Executar a rotina diária assistida do autopilot e consolidar um resumo executivo às 7h BRT.

## Passo a passo
1. Ler `monitored-projects.yaml`
2. Ler os arquivos em `projects/` correspondentes às obras monitoradas
3. Verificar quais obras têm atualização recente
4. Identificar obras silenciosas
5. Classificar alertas por criticidade
6. Montar relatório conforme `references/report-template.md`
7. Separar top prioridades do dia

## Regras
- máximo de 3 a 5 prioridades no topo
- se não houver sinal suficiente, reportar falta de visibilidade, não inventar narrativa
- obras estáveis entram curtas
- alertas sem ação recomendada são inválidos

## Modo assistido
Nesta fase, a rotina deve ser revisada antes de qualquer envio externo.

## Critério de qualidade
O resumo diário precisa responder em menos de 1 minuto de leitura:
- onde está o risco
- o que está parado
- o que cobrar hoje
- o que pode esperar

## Fonte primária desta fase
Na fase 2, a leitura base deve sair destes arquivos:
- `projects/ccsp-casa7.md`
- `projects/pg-louveira.md`
- `projects/paranapiacaba.md`
- `projects/paranapiacaba-paralelepipedo.md`
- `projects/teatro-suzano.md`

Se algum arquivo estiver vazio ou desatualizado, isso deve aparecer explicitamente no rascunho diário como lacuna de visibilidade.
