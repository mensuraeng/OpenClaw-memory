# Security hardening — 2026-04-22

Triggered by discovery that the VPS root password and a GitHub Personal
Access Token had been committed to this (public) repository in
`memory/2026-04-07-api-keys.md` on 2026-04-07. The commit was deleted
the same day, but the password remained in git history.

## Actions taken

1. **Removed hardcoded password** from
   `/root/.openclaw/mia-finance/xp_export_automation.js` (file not in git);
   replaced with environment-variable-based config.

2. **Purged PAT from local caches**:
   - `/root/.git-credentials` emptied
   - `/root/.gitconfig` credential helper removed
   - `.git/config` of both workspace clones switched to SSH remote
     (`git@github.com:mensuraeng/OpenClaw-memory.git`) — SSH key
     `/root/.ssh/id_ed25519_openclaw_github` already registered against
     the `mensuraeng` GitHub account.

3. **Rotated VPS root password** via `chpasswd`. New password stored
   in `/root/.vault/root-password.txt` (0600, root only) and delivered
   to Alê via Telegram.

4. **Rewrote git history** with `git filter-repo` removing
   `memory/2026-04-07-api-keys.md` from all commits (233 → 231).
   Force-pushed cleaned history to `origin/master`. Pre-rewrite bundle
   preserved in `/root/.vault/openclaw-memory-pre-filter.bundle`.

5. **Verified cleanup**:
   - raw path `master/memory/2026-04-07-api-keys.md` → 404 ✅
   - `git log -S 'Fla06071982'` → empty ✅
   - dangling-commit SHA still serves file (known GitHub behavior —
     requires GitHub Support ticket to purge; mitigated by password
     rotation).

## Actions still required from Alê (human)

- [ ] **Revoke the old PAT** `ghp_VQwb…p17xxFi` in GitHub UI
      (Settings → Developer settings → Personal access tokens →
      Revoke). Local caches already purged but the token itself
      remains valid on GitHub until revoked manually.
- [ ] **Optional**: open a GitHub Support ticket requesting purge of
      dangling commits `aa7225c94` and `4b70a3bd6`. Residual risk
      only — the credentials exposed there have been rotated.
- [ ] **Optional**: disable `PasswordAuthentication` in
      `/etc/ssh/sshd_config.d/50-cloud-init.conf` after confirming
      SSH-key login works from Windows (`alesurface`). If you can
      currently SSH with the key `openclaw-vps-key`, you can safely
      flip it. Until you do, the server still accepts password logins.

## Backup artifacts (local only)

- `/root/.vault/root-password.txt` — new root password
- `/root/.vault/openclaw-memory-pre-filter.bundle` — pre-rewrite repo
- `/root/.git-credentials.bak.*` — old credential cache

Keep them only until the manual actions above are complete, then wipe.
