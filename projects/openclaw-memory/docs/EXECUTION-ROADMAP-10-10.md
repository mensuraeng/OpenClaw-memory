# OpenClaw Memory, roadmap de execução para 10/10

_Data: 2026-04-18_

## Meta
Levar o OpenClaw Memory de ~7/10 para 10/10 como segundo cérebro operacional, executivo e auditável.

## Critério de 10/10
O sistema só merece 10/10 quando consegue, com baixa fricção:
- capturar automaticamente fatos de alto sinal
- separar ruído de memória útil
- responder o que mudou, o que abriu, o que fechou e o que piorou
- sustentar fechamento de loop
- manter rastreabilidade entre evento, promoção e memória institucional
- continuar legível por humano

---

## Fase 1, captura real
Objetivo: aumentar massa crítica de sinais confiáveis.

### Entregas
- conectar `capture_openclaw_event.py` a mais eventos reais do ecossistema
- importar runtime do Mission Control de forma estável
- criar pontos de captura para email relevante, publicação, erro, bloqueio e decisão
- diferenciar origem manual vs observada

### Critério de pronto
- consultas semanais não retornam vazio por falta de evento
- toda semana útil tem trilha mínima de mudanças

---

## Fase 2, promoção com menos ruído
Objetivo: parar de subir lixo e melhorar qualidade institucional.

### Entregas
- score de relevância por evento
- melhor deduplicação semântica
- regras por tipo de evento
- promoção priorizando decisão, pendência, risco e fechamento

### Critério de pronto
- memória institucional deixa de acumular duplicata banal
- cada bloco promovido tem valor de consulta posterior

---

## Fase 3, fechamento de loop
Objetivo: a memória saber o que continua vivo e o que encerrou.

### Entregas
- distinguir item aberto, em andamento, bloqueado e encerrado
- suportar atualização de um mesmo tema ao longo do tempo
- criar rastreio de owner, próximo passo, prazo e status quando existir

### Critério de pronto
- responder com confiança: o que continua aberto e o que foi resolvido

---

## Fase 4, consulta executiva de verdade
Objetivo: responder perguntas gerenciais sem arqueologia manual.

### Perguntas-alvo
- o que mudou hoje?
- o que mudou nesta semana?
- quais decisões continuam abertas?
- quais riscos cresceram?
- quais bloqueios externos estão parados?
- o que foi concluído desde a última revisão?

### Critério de pronto
- briefing executivo útil sem depender de leitura manual de múltiplos arquivos

---

## Fase 5, governança e obsolescência
Objetivo: impedir apodrecimento silencioso da memória.

### Entregas
- política de arquivamento
- marcação de itens obsoletos
- revisão periódica de pendências antigas
- higiene da memória institucional

### Critério de pronto
- memória permanece viva e confiável, não só crescente

---

## Fase 6, integração operacional completa
Objetivo: memória deixar de ser projeto paralelo e virar infraestrutura real da Flávia.

### Entregas
- integração com rotinas BOOT e cockpit executivo
- ingestão dos principais eventos de operação
- uso recorrente em síntese, cobrança, priorização e destravamento

### Critério de pronto
- a memória passa a reduzir trabalho operacional real, não só organizar histórico

---

## Leitura brutal
Hoje o sistema já tem arquitetura boa.
O que falta para 10/10 não é desenho. É:
- mais captura real
- mais fechamento
- menos silêncio estrutural
- mais resposta executiva confiável
