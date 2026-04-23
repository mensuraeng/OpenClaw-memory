# Agent Daily Planner — Flávia Edition

Skill para planejamento diário e acompanhamento de execução, adaptado ao padrão de memória da Flávia.

## Objetivo

Organizar o dia operacional do Alê com base em:
- pendências ativas em `/root/2nd-brain/02-context/pending.md`
- decisões relevantes em `/root/2nd-brain/02-context/decisions.md`
- lições e padrões em `/root/2nd-brain/02-context/lessons.md`
- projetos ativos em `/root/2nd-brain/04-projects/`
- memória diária da Flávia em `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md`
- capturas de sessão e legado local apenas quando forem necessárias

## Regras do skill

### `/plan today`
Gerar ou atualizar `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` com estrutura diária operacional:

```markdown
# YYYY-MM-DD

## Prioridades do Dia
- [ ] tarefa 1
- [ ] tarefa 2

## Pendências Críticas
- item aguardando decisão/input

## Alertas
- risco, prazo, desvio, follow-up

## Entregas do Dia
- item entregue

## Notas Operacionais
- contexto, decisão, aprendizado curto
```

Fontes obrigatórias:
- `/root/2nd-brain/02-context/pending.md`
- `/root/2nd-brain/02-context/decisions.md`
- `/root/2nd-brain/04-projects/` relevantes
- último `/root/2nd-brain/06-agents/flavia/memory/YYYY-MM-DD.md` existente, quando útil

### `/plan review`
Revisar o dia atual e resumir:
- concluído
- pendente
- o que carregar para amanhã
- bloqueios

### `/plan ship <descrição>`
Adicionar item em `## Entregas do Dia` no arquivo diário atual.

### `/plan block <descrição>`
Adicionar item em `## Alertas` ou `## Pendências Críticas`, conforme contexto.

### `/plan standup`
Gerar formato executivo curto:
- Ontem
- Hoje
- Bloqueios

### `/plan carry`
Carregar itens pendentes relevantes do dia anterior para o dia atual, sem duplicação burra.

## Estrutura de memória compatível

```text
/root/2nd-brain/
  01-identity/
  02-context/
    decisions.md
    lessons.md
    pending.md
  03-knowledge/
  04-projects/
  05-journal/2026/
  06-agents/flavia/memory/YYYY-MM-DD.md

/root/.openclaw/workspace/
  memory/feedback/
  memory/context/credentials.md
  scripts/
  agents/
```

## Restrições

- Nunca criar `projects.json`
- Nunca tratar `memory/context/` ou `memory/projects/` do workspace como memória canônica
- Não duplicar conteúdo que já foi consolidado no `2nd-brain`
- Priorizar clareza operacional, não template bonito

## Fit operacional

Este skill existe para reduzir reorientação, aumentar continuidade e transformar memória em cadência executiva real.
