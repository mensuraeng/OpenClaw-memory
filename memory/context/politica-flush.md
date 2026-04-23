# Política de flush da memória

_Atualizado em 2026-04-21 14:25 BRT_

## Regra operacional
O diário deve funcionar como delta temporal, não como painel principal nem como cópia repetida de blocos antigos.

## Fluxo correto
1. atualizar primeiro o arquivo canônico da frente, quando existir
2. registrar no diário apenas o que mudou nesta janela
3. evitar duplicação de conteúdo histórico já consolidado
4. validar se alguma documentação lateral ficou contraditória com o arquivo canônico
5. rodar o checklist mínimo pós-flush em `docs/checklist-validacao-pos-flush.md`

## Regra curta
Se nada mudou, não regravar.
Se mudou pouco, registrar pouco.
Se mudou estruturalmente, atualizar o arquivo canônico e depois registrar só o delta.
Se criou conflito documental, o flush ainda não terminou.
