# Agent Daily Planner — Flávia Edition

Skill para planejamento diário e acompanhamento de execução, adaptado ao padrão de memória da Flávia.

## Objetivo

Organizar o dia operacional do Alê com base em:
- pendências ativas em `memory/context/pending.md`
- decisões relevantes em `memory/context/decisions.md`
- lições e padrões em `memory/context/lessons.md`
- projetos ativos em `memory/projects/`
- memória diária em `memory/YYYY-MM-DD.md`
- capturas de sessão em `memory/sessions/`

## Regras do skill

### `/plan today`
Gerar ou atualizar `memory/YYYY-MM-DD.md` com estrutura diária operacional:

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
- `memory/context/pending.md`
- `memory/context/decisions.md`
- `memory/projects/*.md` relevantes
- último `memory/YYYY-MM-DD.md` existente, quando útil

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
memory/
  YYYY-MM-DD.md
  context/
    decisions.md
    lessons.md
    pending.md
    business-context.md
    people.md
  projects/
    *.md
  sessions/
    *.md
  feedback/
    *.json
  integrations/
    *.md
  content/
    ...
```

## Restrições

- Nunca criar `projects.json`
- Nunca escrever fora do padrão acima
- Não duplicar conteúdo que já foi consolidado em `context/` ou `projects/`
- Priorizar clareza operacional, não template bonito

## Fit operacional

Este skill existe para reduzir reorientação, aumentar continuidade e transformar memória em cadência executiva real.
