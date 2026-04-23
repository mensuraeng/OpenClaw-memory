---
name: mensura-morning-briefing
emoji: 📋
description: Gera um rascunho executivo matinal do portfólio monitorado da MENSURA usando a estrutura do Mensura Autopilot, com foco em risco, silêncio operacional e prioridades do dia.
author: Flávia | MENSURA Engenharia
trigger: manual
---

# Mensura Morning Briefing

## Objetivo
Gerar um resumo executivo curto e acionável das obras monitoradas, usando a skill `mensura-autopilot` como fonte principal de critério.

## Fontes obrigatórias
- `skills/mensura-autopilot/monitored-projects.yaml`
- `skills/mensura-autopilot/daily-runbook.md`
- `skills/mensura-autopilot/references/report-template.md`
- `skills/mensura-autopilot/projects/ccsp-casa7.md`
- `skills/mensura-autopilot/projects/pg-louveira.md`
- `skills/mensura-autopilot/projects/paranapiacaba.md`
- `skills/mensura-autopilot/projects/paranapiacaba-paralelepipedo.md`
- `skills/mensura-autopilot/projects/teatro-suzano.md`

## Instruções
1. Ler a carteira monitorada e os arquivos das obras.
2. Identificar:
   - alertas vermelhos
   - alertas amarelos
   - obras silenciosas
   - lacunas de visibilidade
3. Priorizar no máximo 3 a 5 itens para a direção.
4. Para cada prioridade, sempre escrever:
   - obra
   - fato
   - risco
   - ação recomendada
5. Se faltar dado real, explicitar a lacuna. Não inventar status.
6. Manter leitura total curta, em formato executivo.

## Regras
- Não enviar email nem mensagem automaticamente.
- Não usar integrações externas.
- Não criar narrativa para preencher ausência de dado.
- Sem texto bonito e vazio.
- Se não houver sinal suficiente, o briefing deve dizer isso claramente.

## Saída esperada
### Panorama geral
- quantidade de obras monitoradas
- vermelhos
- amarelos
- silenciosas

### Top prioridades do dia
Até 5 bullets.

### Obras com baixa visibilidade
Listar separadamente.

### Cobranças ou decisões sugeridas para hoje
Bullets diretos.
