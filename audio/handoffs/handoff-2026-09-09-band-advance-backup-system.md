# Context Handoff — 2026-09-09
**Session topic:** Band Advance — weekly backup + one-command restore to both NAS boxes, Cold Storage rotating at 8, n8n completion-report workflow
**Repo / Branch:** `Code/BandInfoForm/`, branch `advance-system` (pushed to origin)

---

## What We Did

The advance pipeline had no backup of its own — the nightly Mac rsync covered the repo, but nothing covered the Postgres database, the band uploads, the env/secrets, the n8n workflows, or the Dropbox `Nyquist/` cockpit. Built a weekly system that packages all of it into one self-contained, self-restoring archive and pushes it to both TrueNAS boxes, restorable with a single command on bare hardware. Then two follow-ups: Cold Storage retention cut to a flat rotating 8, and the completion email moved into its own n8n workflow. Everything drilled end to end the same day rather than assumed.

---

## Current State

- **Done:**
  - `backup/` in the repo, deployed to `/opt/band-advance/backup/` on the n8n VM. `band-advance-backup.timer` — Sundays 03:15, `Persistent=true`, enabled. Next fire Sun 2026-09-13 03:15.
  - Runs on the VM, not the Mac, because the VM is the one machine holding every moving part at once (Postgres, the app, the uploads, the env, n8n, and a live Dropbox mirror of `Nyquist/`).
  - Pushes to **both** boxes: Cold Storage `/mnt/The-Pool/ClaudeBackup/band-advance/` and Audio NAS `/mnt/AudioNas/brian/band-advance-backups/`. VM→NAS over a dedicated ed25519 key `~/.ssh/nas_backup`, authorised on both.
  - Archive (~28 MB) holds: the DB twice (`advance.dump` custom-format + `advance.sql.gz` plain) with exact per-table row counts, all band uploads, the disk-first submission JSON, the deployed app with deps pinned, the `.docx`/`.j2` templates, the whole Dropbox `Nyquist/` tree, all n8n workflows + their active-state map + the n8n DB, systemd units, compose files — plus its own `restore.sh` and `RESTORE.md`.
  - Secrets split into `secrets.tar.gz.gpg` (AES256, passphrase `lockdown`). Everything else plaintext.
  - Retention is **per-target**: `TARGETS` lines are `name|host|dir|keep|monthly`. Cold Storage = flat rotating **8**. Audio NAS = 12 weekly + 24 first-of-month. 4 on the VM.
  - n8n workflow **Band Advance — Backup Report (Cold Storage)** (`band-advance-backup-report`) live and active — owns the completion email, sends as Production@3cdc.org via Graph to blloyd@3cdc.org.
  - `install_backup.command` (idempotent installer/redeploy, includes the workflow deploy) and `restore_advance.command` (Mac-side restore driver) both working.
  - Committed and pushed: `a644c59`, `6371d98`, `18d4d44`, `a372e4d`. KB pipeline article, active-projects and CHANGELOG updated; auto-memories written.
- **In progress:** Nothing mid-stream. Clean stopping point.
- **Up next:** Whatever Brian brings. Nothing in this system is waiting on anything.

---

## Key Decisions (Locked)

- **Backup runs on the n8n VM**, not the Mac — the VM holds all of it at once and is always on. The Mac's nightly `com.tinydoor.claude-backup` rsync stays as-is for the repo/git history.
- **Secrets are split out and optional.** Everything except `secrets.tar.gz.gpg` is plaintext so a restore ALWAYS works. If the passphrase is ever lost, `restore.sh` mints fresh credentials and carries on — the entire cost is that outstanding `/f/<token>` prefill links die and the Graph credential needs re-entering. Brian chose this over encrypting the whole archive, which would turn a forgotten passphrase into total data loss.
- **Cold Storage holds a flat rotating 8** — Brian's call, it's the box he actually opens. The Audio NAS deliberately keeps the deeper tail (12 weekly + 24 monthly) so nothing older is genuinely gone.
- **"Complete" requires the sha256 to have been re-verified ON the NAS**, not merely that a copy arrived. A copy that landed unverified reports as FAILED in the email subject, on purpose.
- **Restores never destroy.** A populated `advance` DB is renamed to `advance_pre_restore_<stamp>`, an existing `/opt/band-advance` is moved aside, a live `~/Dropbox/Nyquist` is left alone (tree lands in `./restored-Nyquist-<stamp>` unless `--force-dropbox`). n8n untouched without `--with-n8n`.
- **Partial beats nothing.** A failed section is recorded, not fatal — the archive still gets built, is labelled `PARTIAL` in its manifest, and the job exits non-zero.
- **The email lives in n8n, not the script.** The script POSTs facts; the workflow owns formatting and the send, so the email can be reworked without touching the backup job.
- **No missed-run watchdog** — offered, Brian declined ("no not needed"). If the VM or n8n is down at 03:15 the result is silence, not an alarm. Don't build it unless he asks.

---

## Open Items

- Rotate the Graph client secret — Brian's, still pending from the prior session. Nothing needs doing on the backup side when he does; the next weekly run picks the new value up automatically.
- Move the Band Advance pipeline's **band-facing** sends off Gmail drafts onto the proven Outlook connector — long-open, still not started.
- Delete the throwaway n8n "My workflow 4" test workflow — flagged for several sessions, never done.
- Memorial Hall venue build (richer rider/hospitality question set) — scoped, not started.
- No 2- or 3-band day-sheet template for Washington Park yet.
- Per-person advance ownership ("who's running this advance") has no DB field.
- **Not from this project, but worth a look:** the Mac's nightly `com.tinydoor.claude-backup` rsync has been flaky — Cold Storage skipped as unreachable on 9/8, and the Synology leg failed with broken pipes two nights running. That's the job covering the git history.
- `Projects/WP-Video-Distribution/` (one PDF proposal) is untracked in the workspace repo — pre-existing, left alone, not part of this work.

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| `Code/BandInfoForm/backup/advance_backup.sh` | bash | The weekly job — runs on the VM |
| `Code/BandInfoForm/backup/restore.sh` | bash | Ships inside every archive; the one-command restore |
| `Code/BandInfoForm/backup/install_backup.command` | bash | Idempotent installer/redeploy, run from the Mac |
| `Code/BandInfoForm/backup/restore_advance.command` | bash | Mac-side restore driver (finds newest, verifies, ships, restores) |
| `Code/BandInfoForm/backup/README.md` | md | Runbook |
| `Code/BandInfoForm/backup/RESTORE.md` | md | Rebuild instructions; also ships inside every archive |
| `Code/BandInfoForm/backup/band-advance-backup.service/.timer` | systemd | Weekly schedule |
| `Code/BandInfoForm/n8n/backup_report.json` | JSON | The completion-report workflow |

---

## Corrections / Watch-Outs

- **The TrueNAS login shell is zsh, and it bites twice.** (1) An unmatched glob **aborts** the whole remote command instead of passing through like bash — that silently killed the first run's retention step. (2) zsh does **not** word-split an unquoted variable, so a list of files can't be expanded inline. Rule for any command run against `.35`/`.36`: match with `find`, never a glob, and read lists from a file line by line.
- **n8n only mounts a newly imported webhook route on restart.** A freshly imported, published, genuinely-active workflow returned 404 to six consecutive POSTs. `install_backup.command` now restarts n8n as part of deploying the workflow — and note the route also registers noticeably *after* `/healthz` starts answering 200, so polling healthz alone isn't enough (sleep another 10–20s).
- macOS `/bin/bash` is 3.2 — no `${var,,}`. The Mac-side `.command` scripts use `tr` instead. Don't reintroduce bash-4 syntax there.
- TrueNAS `find -size -1k` rounds up, so it matches a 6-byte file. Use `-size -100c` when hunting genuinely tiny files.
- The archive's manifest reports `PARTIAL` when a section failed — read `MANIFEST.txt` before trusting an archive, and `restore.sh` warns about it up front.

---

## Verification Done (not assumed)

- Archive pulled back off Cold Storage, all 212 inner checksums verified.
- `advance.dump` restored into a throwaway Postgres container — all 10 tables hit their exact backup-time row counts; artists/submissions spot-checked, JSONB intact.
- `secrets.tar.gz.gpg` opened with the `lockdown` passphrase; all 12 n8n credentials recovered including the Graph one.
- Rotation: 11 archives seeded onto Cold Storage, one run, 8 left, newest kept, 3 rotated off. Test dummies cleaned up afterward — Cold Storage sits on 3 real archives now and fills to 8 over the coming weeks.
- Report workflow: execution `497168` success, Graph returned **202**, email delivered to blloyd@3cdc.org.

---

## Resume Prompt

> Picking up from a previous session on the Band Advance pipeline (`Code/BandInfoForm/`, branch `advance-system`, pushed to origin). Last session built the backup/restore system from scratch and it is fully live: a systemd timer on the n8n VM (Sundays 03:15) packages the whole pipeline — Postgres DB, band uploads, disk-first JSON, the deployed app with pinned deps, the .docx/.j2 templates, the entire Dropbox `Nyquist/` cockpit, all n8n workflows plus their active-state map, systemd units and compose files — into one self-restoring archive and pushes it to both TrueNAS boxes. Cold Storage holds a flat rotating 8; the Audio NAS keeps the deeper tail. Secrets ride separately in an AES256 GPG file so a lost passphrase costs convenience, never data. Restore is one command (`sudo ./band-advance-*/restore.sh`) and never destroys anything. An n8n workflow (`band-advance-backup-report`) emails blloyd@3cdc.org after every run, with "complete" gated on the sha256 having been re-verified on the NAS itself. All of it was drilled end to end — checksums, a real DB restore into a throwaway container matching exact row counts, the GPG bundle opening, and rotation pruning 11 archives to 8.
>
> Don't build a missed-run watchdog — Brian explicitly declined it. Don't touch the Graph client secret rotation (his). Don't start moving band-facing sends onto Outlook without him asking.
>
> Watch-outs carried forward: the TrueNAS login shell is zsh, where an unmatched glob aborts the remote command AND unquoted variables are not word-split — match with `find`, read lists from a file. n8n only mounts a newly imported webhook route on restart, and the route lags `/healthz` by another 10–20s after that. macOS `/bin/bash` is 3.2, so no bash-4 syntax in the `.command` scripts. And this repo's checked-out branch has flipped from `advance-system` to `main` on its own twice — check `git branch --show-current` if a file ever looks inexplicably wrong.
