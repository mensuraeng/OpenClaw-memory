# Captura Automática — OpenClaw Memory

## Objetivo

Criar um caminho mínimo, confiável e padronizado para os agentes registrarem contexto útil no inbox diário.

## MVP

O MVP grava em dois destinos por agente:
- `notes.md` para leitura humana rápida
- `events.jsonl` para estrutura e processamento futuro

## Script base

```bash
python3 scripts/capture_event.py \
  --agent mensura \
  --type decision \
  --title "Mudança de rotina" \
  --body "Obras devem rodar apenas em dias úteis." \
  --source cron \
  --meta '{"job":"cobranca-rdo"}'
```

## Captura automática de alto sinal

```bash
python3 scripts/capture_openclaw_event.py \
  --agent main \
  --event-type decision_made \
  --title "Regra operacional formalizada" \
  --body "A operação passa a seguir patamar 10/10 como princípio." \
  --source telegram \
  --meta '{"priority":"high"}'
```

Eventos de baixo sinal são ignorados por padrão.

## Importação de eventos do Mission Control

```bash
python3 scripts/import_mission_control_events.py
```

Esse importador transforma eventos relevantes do runtime do Mission Control em memória institucional futura.

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
