# NotebookLM sync failed

- error: Not logged in.

Checked locations:
  • Storage file: /root/.notebooklm/storage_state.json
  • NOTEBOOKLM_AUTH_JSON: not set

Options to authenticate:
  1. Run: notebooklm login
  2. Set NOTEBOOKLM_AUTH_JSON env var (for CI/CD)
  3. Use --storage /path/to/file.json flag
