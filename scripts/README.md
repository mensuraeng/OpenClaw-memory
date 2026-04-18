# OpenClaw Memory — Scripts

> Diretorio: /root/.openclaw/workspace/projects/openclaw-memory/scripts
> Atualizado: 2026-04-18

## Scripts Ativos

| Script | Frequencia | Funcao |
|--------|-----------|--------|
| nightly_consolidate.py | Cron 22:00 | Consolida notas do dia, move para memoria institucional |
| update_memory_panel.py | Chamado pelo nightly | Atualiza secao Estado Atual do MEMORY.md com dados derivados |
| daily_diff.sh | Sob demanda | Responde: o que mudou hoje/semana? quais decisoes/riscos ativos? |
| executive_memory_brief.py | Sob demanda | Gera briefing executivo da memoria |
| executive_memory_query.py | Sob demanda | Consulta semantica na memoria (com failsafe memory_search_safe) |
| capture_event.py | Sob demanda | Captura evento para memoria |
| capture_openclaw_event.py | Sob demanda | Variante OpenClaw de captura de evento |
| loop_closure.py | Sob demanda | Fecha loops abertos na memoria |
| promote_institutional_memory.py | Sob demanda | Promove notas diarias para memoria institucional |
| import_mission_control_events.py | Sob demanda | Importa eventos do Mission Control |
| bootstrap_openclaw_memory.sh | Setup unico | Bootstrap inicial do sistema de memoria |

## Archive
Arquivos obsoletos em archive/.

## Crons configurados
```
0 22   * * * root python3 /root/.openclaw/workspace/projects/openclaw-memory/scripts/nightly_consolidate.py
30 22  * * * root cd /root/.openclaw/workspace/projects/openclaw-memory && git add -A && git commit -m "chore: nightly sync $(date +%Y-%m-%d)" && git push origin main
```