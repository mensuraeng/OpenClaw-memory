# Agent Task Tracker — Flávia Edition

Skill para manter estado operacional de tarefas sem competir com a estrutura principal de memória.

## Objetivo

Dar continuidade entre sessões, resets e compactions, registrando:
- o que está em andamento
- o que está bloqueado
- o que foi concluído recentemente
- processos em background relevantes

## Fonte oficial

Arquivo principal:
- `/root/2nd-brain/02-context/pending.md`

Arquivo complementar de sessão/dia:
- `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md`

## Regra central

**Não criar `memory/tasks.md`.**

Acompanhar tarefas usando:
- `/root/2nd-brain/02-context/pending.md` para estado durável
- `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` para progresso do dia

## Quando atualizar

### 1. Nova tarefa recebida
- Se for tarefa que sobrevive à conversa atual, registrar em `/root/2nd-brain/02-context/pending.md`
- Se for tarefa curta do dia, registrar em `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` em `## Prioridades do Dia` ou `## Notas Operacionais`

### 2. Processo em background iniciado
Registrar em `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md`:
- session id
- comando
- servidor/contexto
- objetivo do processo

### 3. Progresso relevante
Atualizar:
- `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` com andamento do dia
- `/root/2nd-brain/02-context/pending.md` se mudou status estrutural

### 4. Conclusão
- remover ou marcar como resolvido em `/root/2nd-brain/02-context/pending.md`
- registrar entrega em `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` em `## Entregas do Dia`

### 5. Falha ou bloqueio
- registrar em `/root/2nd-brain/02-context/pending.md`
- descrever bloqueio e dependência

## Estrutura recomendada

### Em `/root/2nd-brain/02-context/pending.md`
```markdown
## Em andamento interno
- [ ] tarefa durável

## Aguardando Alê
- [ ] decisão/input necessário

## Aguardando terceiros
- [ ] dependência externa
```

### Em `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md`
```markdown
## Prioridades do Dia
- [ ] tarefa

## Entregas do Dia
- item entregue

## Notas Operacionais
- progresso, session id, comando, bloqueio, observação
```

## Regras

- Nunca duplicar lista inteira de tarefas em múltiplos arquivos
- `pending.md` do `2nd-brain` guarda estado durável
- `YYYY-MM-DD.md` da Flávia no `2nd-brain` guarda contexto diário
- Se a tarefa deixou de ser relevante estruturalmente, não manter em `pending.md`
- Clareza operacional > log detalhado

## Fit operacional

Este skill existe para reduzir perda de contexto, sem criar mais uma camada concorrente de memória.
