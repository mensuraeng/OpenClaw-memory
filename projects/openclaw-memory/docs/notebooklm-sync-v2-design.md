# NotebookLM → OpenClaw daily note-delta sync

**Date:** 2026-04-21
**Owner:** Alê (aa.mensura@gmail.com)
**Status:** approved

## Goal

Every night, compare the current state of notes across all NotebookLM
notebooks against an inventory from the previous run, and record what
changed into OpenClaw's memory. Overwrite note contents in place; emit a
per-day changelog of deltas. The first run seeds silently.

## Scope

- **In scope:** user-created notes (`notebooklm note list`/`get`) across
  every notebook in the account.
- **Out of scope:** sources, summaries, artifacts, conversation history,
  notebook-level metadata changes. The detector looks only at notes.

## Decisions (from brainstorm)

| Question | Choice |
|---|---|
| Notebook scope | All notebooks in the account |
| Signals tracked | Notes only (created / edited / deleted / renamed) |
| Destination for note content | One file per note, overwritten on change |
| Changelog format | One file per day, only if there's a delta |
| Delta detection | SHA-256 of note `content` (NotebookLM exposes no `updated_at`) |
| Error handling | Log + Telegram notification on auth failure / fatal error |
| First-run behavior | Silent seed (populate inventory + note files, no changelog) |
| Schedule | 02:00 America/Sao_Paulo daily (before backup at 02:15) |
| Driver | Linux systemd timer + pure Python script (deterministic, no LLM) |

## Architecture

Three components, coupled by the filesystem:

1. **`nblm_sync.py`** — single Python script at
   `/root/.openclaw/bin/nblm_sync.py`, runs in the existing
   `/root/.openclaw/venvs/notebooklm/` venv. Uses
   `notebooklm.NotebookLMClient` directly (no subprocess). Idempotent.

2. **`notebooklm-sync.service` + `notebooklm-sync.timer`** —
   `/etc/systemd/system/`, fires 02:00 America/Sao_Paulo daily,
   `Persistent=true`, logs via journald.

3. **Memory layout** under
   `/root/.openclaw/workspace/memory/integrations/notebooklm/`:
   - `_state/inventory.json` —
     `{notebook_id → {note_id → {title, content_hash, last_seen}}}`
   - `_state/errors.log` — append-only failure log
   - `notes/<notebook_id>/<note_id>.md` — current content of each note,
     overwritten on change, deleted when the note is removed upstream
   - `changes/YYYY-MM-DD.md` — daily delta, created only when there's a
     delta, **not** created on the first-run seed

The script is the sole writer of these paths. systemd serializes
invocations, so there is no concurrency.

## Components (inside the script)

| Function | Responsibility |
|---|---|
| `load_inventory()` / `save_inventory()` | Read/write `_state/inventory.json`. Atomic via temp file + rename. |
| `fetch_current_state(client)` | `client.notebooks.list()` → iterate → `client.notes.list()` (+ `note.get()` if content not included). Returns `{nb_id → {note_id → Note}}`. |
| `compute_diff(prev, curr)` | Returns a `Diff` with `added`, `edited`, `removed`, `renamed`, grouped by `notebook_id`. |
| `write_notes(curr, touched)` | Writes `notes/<nb>/<note>.md` for every note in `touched` (added ∪ edited ∪ renamed). Frontmatter: `title`, `notebook_id`, `note_id`, `created_at`, `content_hash`, `updated_at_sync`. |
| `write_changes(diff, day)` | Creates `changes/<day>.md` with `## Novas`, `## Editadas`, `## Removidas`, `## Renomeadas` sections. Each bullet links to the note file. Skipped on empty diff. |
| `notify_telegram(msg)` | `curl` to Bot API; swallows its own errors. |
| `main()` | Orchestrates, classifies exceptions, returns exit code. |

Configuration in `/root/.openclaw/bin/nblm_sync.config.json`:

```json
{
  "storage_path": "/root/.openclaw/credentials/notebooklm/storage_state.json",
  "memory_root": "/root/.openclaw/workspace/memory/integrations/notebooklm",
  "timezone": "America/Sao_Paulo",
  "telegram_bot_token_env": "TELEGRAM_BOT_TOKEN",
  "telegram_chat_id": "1067279351"
}
```

Secrets (`TELEGRAM_BOT_TOKEN`) come from environment, injected by the
systemd unit via `EnvironmentFile=/root/.openclaw/bin/nblm_sync.env`
(0600). No secrets in the config JSON, no secrets in the script.

## Data flow (one daily run)

```
02:00 SP — timer fires
  ↓
  nblm_sync.service → nblm_sync.py
  ↓
  1. load_inventory()   ← _state/inventory.json (empty on first run)
  ↓
  2. NotebookLMClient.from_storage(storage_path)
     │  on auth failure → notify_telegram + errors.log → exit 1
  ↓
  3. fetch_current_state() → {nb_id → {note_id → Note}}
  ↓
  4. Compute content_hash = sha256(note.content) for every note
  ↓
  5. compute_diff(prev, curr)
       │
       ├─ prev empty (first run):
       │    • write_notes(curr, ALL)   (silent seed)
       │    • save_inventory(curr)
       │    • DO NOT create changes/<day>.md
       │    • exit 0
       │
       └─ otherwise:
            • write_notes(curr, added ∪ edited ∪ renamed)
            • remove note files for diff.removed
            • write_changes(diff, today_sp) if diff non-empty
            • save_inventory(curr)
            • exit 0
```

### Timezone

Day boundary is `datetime.now(ZoneInfo("America/Sao_Paulo")).date()`, so
an execution that slips to 23:55 UTC (20:55 SP) does not land in the
"next day" file.

### Atomicity

Order of writes inside a run: (1) write note files, (2) write changes
file, (3) save inventory. If the script crashes before step 3, the next
run re-detects the same deltas and safely re-writes identical files.
The inventory is the commit point.

## Rename detection

A note is considered renamed when the same `note_id` appears in both
`prev` and `curr` with **identical content hash** but **different title**.
In that case: `renamed` (not `edited`), write a fresh
`notes/<nb>/<note>.md` (overwrite is fine — same file path since we key
by note_id), and the bullet in the changelog reads
`[renomeado] "<old title>" → "<new title>"`.

## Error handling

| Scenario | Behaviour |
|---|---|
| `storage_state.json` absent or missing SID (auth fail) | `notify_telegram("NotebookLM sync: sessão expirada, rodar login")`; append to `errors.log`; exit 1 |
| HTTP transient (timeout, 5xx) | retry 3× with exponential backoff (2s, 4s, 8s) — wrapped around `NotebookLMClient` calls |
| Unexpected exception | stack trace in `errors.log`; `notify_telegram("NotebookLM sync falhou: <short>")`; exit 2 |
| File I/O failure | abort run (no inventory update); next run retries |
| Telegram notification itself fails | swallow inside `notify_telegram` — never mask the root cause |

## Testing

- **Unit (pytest):** `compute_diff()` with fixtures covering
  bootstrap / added / edited / removed / renamed / no-op.
- **`--dry-run` flag:** lists planned actions without writing; used for
  local smoke.
- **Smoke first run (manual):** run once, confirm inventory populated
  and no `changes/*.md` created.
- **Smoke second run (manual):** re-run immediately, confirm 0 diff and
  no file churn.
- **Smoke timer:** `systemctl start notebooklm-sync.service` → inspect
  `journalctl -u notebooklm-sync`.

## Open items during implementation

- Confirm whether `client.notes.list()` returns `content` or only
  metadata. If content requires a follow-up `client.notes.get()`,
  adjust `fetch_current_state` to batch those calls.
- Decide if renamed-detection should also catch title changes with
  content changes (currently classified as `edited`, which is
  acceptable).
