# Restore Drill — latest

- Checked at UTC: `2026-04-30T09:11:56.019344+00:00`
- Overall: **attention**
- Workspace: `/root/.openclaw/workspace`
- Safety: read-only, tempfile sandbox, no external calls, no production restore.

## Checks
- **key_normalization_and_idempotency**: `ok`
  - Stability checks: {"backup_id_trailing_slash": true, "different_paths_remain_different": true, "manifest_query_trailing_slash": true, "path_relative_absolute_trailing_slash": true}
- **critical_sqlite_copy_integrity**: `ok` — integrity_check=ok
  - SQLite row counts: campaign_recipients=0, campaigns=0, companies=477, contact_sources=1817, contacts=1242, interactions=0, lead_hygiene_results=767, lead_hygiene_runs=1, suppression_list=474
- **second_brain_git_readonly**: `attention` — git status/fsck somente leitura executados
- **local_backup_manifests**: `ok`
  - Manifest count: 3

## Guardrails
- Não restaura sobre caminhos reais.
- Não apaga backups.
- Não executa `rm`.
- Não chama B2/serviços externos.
- Não imprime segredos.
