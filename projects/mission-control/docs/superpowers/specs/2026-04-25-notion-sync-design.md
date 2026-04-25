# Design: Notion → 2nd-Brain Sync

**Data:** 2026-04-25
**Status:** aprovado
**Autor:** Flávia (COO)

---

## Objetivo

Manter o 2nd-brain atualizado com o conteúdo dos três workspaces Notion (Mensura, MIA, PCS), com sincronização completa na primeira execução e delta incremental nas seguintes. O sync roda automaticamente de madrugada para não interferir nas operações diurnas.

---

## Arquitetura

### Script principal
```
scripts/notion_sync.py
```

### Estrutura no 2nd-brain
```
03-knowledge/notion/
  mensura/
    pages/       ← uma página = um arquivo .md
    databases/   ← um database = um arquivo .md com tabela
  mia/
    pages/
    databases/
  pcs/
    pages/
    databases/
  _state/
    last_sync.json   ← { "mensura": "ISO8601", "mia": "...", "pcs": "..." }
```

### Tokens
Lidos em runtime de `/root/.openclaw/workspace/memory/context/credentials.md`. Nunca hardcoded.

---

## Fluxo de execução

1. Lê `_state/last_sync.json`
   - Se ausente ou vazio → **full sync** (busca tudo)
   - Se presente → **delta sync** (filtra `last_edited_time > last_sync[workspace]`)
2. Para cada workspace (Mensura, MIA, PCS):
   - Busca páginas modificadas via `POST /v1/search`
   - Busca databases modificados
   - Converte conteúdo para Markdown e salva/atualiza arquivos
   - Detecta deleções: IDs presentes no state mas ausentes na API → remove arquivo local
3. Atualiza `last_sync.json` com timestamp atual por workspace
4. Gera relatório em `logs/notion-sync-report.md`
5. `git add -A && git commit -m "sync(notion): delta YYYY-MM-DD" && git push` no 2nd-brain

---

## Formato dos arquivos

### Páginas (`pages/{notion_id}-{slug}.md`)
```markdown
---
notion_id: abc123
title: Reunião PCS 2026-04-22
type: page
workspace: pcs
last_edited: 2026-04-22T14:30Z
url: https://notion.so/abc123
---

# Reunião PCS 2026-04-22

[conteúdo convertido para markdown]
```

### Databases (`databases/{notion_id}-{slug}.md`)
```markdown
---
notion_id: def456
title: Pipeline Comercial
type: database
workspace: mensura
last_edited: 2026-04-24T10:00Z
---

# Pipeline Comercial

| Coluna1 | Coluna2 | ... |
|---------|---------|-----|
| ...     | ...     | ... |
```

**Nome dos arquivos:** `{notion_id}-{slug-do-titulo}.md`

---

## Interface de linha de comando

```bash
python notion_sync.py                  # delta (padrão)
python notion_sync.py --full           # força full sync
python notion_sync.py --workspace pcs  # só um workspace
python notion_sync.py --dry-run        # simula sem executar
```

---

## Cron

Roda às **3h da manhã** para não concorrer com scripts operacionais diurnos:

```cron
0 3 * * * /root/.openclaw/workspace/venv/bin/python /root/.openclaw/workspace/scripts/notion_sync.py >> /root/.openclaw/workspace/logs/cron/notion-sync.log 2>&1
```

---

## Tratamento de erros

| Situação | Comportamento |
|----------|---------------|
| 401 / 403 | Loga e interrompe (token inválido) |
| 429 (rate limit) | Retry com backoff exponencial (3x) |
| Falha no `git push` | Loga aviso, não aborta — arquivos já salvos localmente |
| Exceção genérica | Traceback completo em `logs/cron/notion-sync.log` |

---

## Relatório pós-sync

Salvo em `logs/notion-sync-report.md`:
```
Sync: 2026-04-25 03:00 | Mensura: +3 ~5 -1 | MIA: +0 ~2 -0 | PCS: +1 ~1 -0
```
`+` adicionados · `~` atualizados · `-` deletados

---

## Dependências

- `requests` (já no venv do workspace)
- `python-slugify` (para nomes de arquivo limpos)
- Acesso ao git do 2nd-brain (`/root/2nd-brain`)
