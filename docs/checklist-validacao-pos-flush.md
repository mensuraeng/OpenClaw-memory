# Checklist mínimo de validação pós-flush

_Atualizado em 2026-04-21 17:38 BRT_

## Objetivo
Garantir que cada flush deixe a memória mais confiável, não mais volumosa ou contraditória.

## Checklist obrigatório
1. a frente alterada tem arquivo canônico definido?
2. o arquivo canônico foi atualizado antes do diário, quando necessário?
3. o diário registrou apenas delta desta janela?
4. houve duplicação desnecessária de bloco antigo?
5. alguma documentação lateral ficou contraditória com o arquivo canônico?
6. padrão, fallback e nível de productização ficaram explícitos quando aplicável?
7. o estado real ficou classificado corretamente: planejado, preparado, executado ou bloqueado?
8. existe evidência real recente para o que foi marcado como executado?
9. o próximo passo correto ficou claro?
10. se nada material mudou, o flush foi evitado?

## Regra curta
Se o flush aumentou volume sem aumentar verdade operacional, ele foi ruim.
