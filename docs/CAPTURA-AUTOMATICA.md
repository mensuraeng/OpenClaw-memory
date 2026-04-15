# Captura Automática — OpenClaw Memory

## Objetivo

Criar um caminho mínimo, confiável e padronizado para os agentes registrarem contexto útil no inbox diário.

## MVP

O MVP grava em dois destinos por agente:
- `notes.md` para leitura humana rápida
- `events.jsonl` para estrutura e processamento futuro

## Script

```bash
python3 scripts/capture_event.py \
  --agent mensura \
  --type decision \
  --title "Mudança de rotina" \
  --body "Obras devem rodar apenas em dias úteis." \
  --source cron \
  --meta '{"job":"cobranca-rdo"}'
```

## Tipos sugeridos

- `decision`
- `lesson`
- `pending`
- `risk`
- `project_update`
- `integration_update`
- `meeting`
- `email`
- `system`

## Regra prática

Se vale rastreabilidade, grave no `events.jsonl`.
Se vale leitura humana posterior, grave também no `notes.md`.

## Princípio

Captura primeiro. Sofisticação depois.
