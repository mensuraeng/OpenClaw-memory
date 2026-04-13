# Sub-agents — Regra Operacional

_Atualizado em 2026-04-13_

## Princípio

Sub-agent nunca é `fire and forget`.
Quem dispara continua responsável pelo ciclo até o resultado, falha explícita ou escalonamento.

## Regra obrigatória

1. Ao spawnar
   - registrar o que o sub-agent vai fazer
   - manter clareza de objetivo e critério de saída

2. Follow-up
   - se a conclusão não voltar antes disso, checar status em 15 a 30 minutos
   - não deixar execução sem acompanhamento

3. Sucesso
   - resumir objetivamente o resultado
   - consolidar aprendizados ou artefatos quando fizer sentido

4. Falha
   - fazer retry imediato uma vez
   - se falhar 2 vezes, avisar o Alê com clareza

5. Proibição
   - nunca deixar sub-agent cair em limbo silencioso

## Intenção

Sub-agent serve para paralelizar trabalho, não para perder controle da execução.

Se não houver disciplina de follow-up, o custo oculto é alto:
- tarefa some sem conclusão
- bloqueio passa despercebido
- falha fica invisível
- confiança operacional cai
