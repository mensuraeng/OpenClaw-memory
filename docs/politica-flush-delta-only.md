# Política de flush delta-only

_Atualizado em 2026-04-21 14:25 BRT_

## Objetivo
Evitar inflação do diário, duplicação de blocos antigos e perda de legibilidade na memória temporal.

## Regra principal
O diário deve registrar apenas:
- novo fato validado
- nova decisão
- novo bloqueio real
- nova pendência relevante
- nova lição aprendida

## Não fazer
- regravar blocos antigos completos
- duplicar grandes seções já registradas
- usar o diário como substituto do arquivo canônico da frente
- usar o diário para repetir estado atual que já mora em arquivo temático

## Ordem correta
1. atualizar arquivo canônico da frente, quando aplicável
2. registrar no diário apenas o delta novo
3. manter o diário como trilha temporal curta e cumulativa

## Heurística prática
Se o conteúdo já existe e continua verdadeiro, não reescrever no diário.
Só registrar o que mudou.
