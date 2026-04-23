# Fase 3 — endurecimento operacional da memória e contexto

_Atualizado em 2026-04-21 14:17 BRT_

## Objetivo
Fazer a melhoria de memória sair de documentação estática e virar disciplina operacional real.

## Problema que a Fase 3 resolve
Mesmo com arquivos canônicos criados, ainda existe risco de:
- não consultar o arquivo certo sob pressão
- responder com base no diário longo em vez do estado atual
- deixar o diário crescer com duplicação excessiva
- não expandir o padrão para novas frentes conforme elas surgem

## Frentes da Fase 3

### 1. Protocolo curto e acionável
Consolidar um protocolo único de retomada dentro de `memory/context/`, não apenas em `docs/`, para que a memória operacional passe a apontar para ele como regra viva.

### 2. Mapa de frentes críticas
Criar um índice curto com:
- nome da frente
- arquivo canônico
- estado atual
- próximo foco

Isso reduz perda de tempo e erro de consulta.

### 3. Diário como delta, não repositório total
Meta operacional:
- parar de tratar o diário como lugar de regravar blocos inteiros antigos
- registrar no diário apenas o delta novo
- usar arquivos canônicos para estado corrente
- usar o diário para trilha temporal, não para substituir a memória temática

### 4. Regra de expansão
Toda frente crítica nova deve ganhar arquivo canônico quando tiver qualquer uma destas características:
- side effect externo
- recorrência operacional
- dependência de credencial ou acesso
- risco de confusão entre preparado e executado
- risco de ser retomada muitas vezes ao longo da semana

### 5. Regra de verdade operacional
Ao retomar qualquer frente, a resposta deve sair do arquivo canônico e não do histórico difuso.

## Critério de sucesso da Fase 3
- existe um protocolo único de retomada dentro da memória
- existe um mapa curto das frentes críticas
- o diário passa a registrar mais delta e menos repetição
- novas frentes passam a ser canonizadas mais cedo
- a retomada usa o estado operacional atual como fonte primária

## Próximos passos depois da Fase 3
1. aplicar essa disciplina nas próximas execuções reais
2. revisar quais frentes ainda faltam canonização
3. reduzir duplicação histórica do diário em novos flushes
