# Band Advance — backup & restore

Every week the whole pipeline is packaged into one self-contained, self-restoring
archive and pushed to both TrueNAS boxes. Each archive carries its own
`restore.sh` and `RESTORE.md`, so rebuilding never depends on this repo, on
GitHub, or on the machine that made it.

**Schedule:** Sundays 03:15 (`Persistent=true` — a missed run catches up on boot).
**Runs on:** the n8n VM, `192.168.200.84`.
**Lands on:** Cold Storage `/mnt/The-Pool/ClaudeBackup/band-advance/` **and**
Audio NAS `/mnt/AudioNas/brian/band-advance-backups/`.
**Retention:** Cold Storage holds a flat rotating **8** — newest kept, oldest deleted every run.
The Audio NAS keeps the deeper history (12 weekly + every 1st-of-month for 24 months) so there
is still a long tail somewhere. 4 kept locally on the VM.
**Report:** every run emails blloyd@3cdc.org from the n8n workflow
**Band Advance — Backup Report (Cold Storage)**.

---

## Install (once)

```bash
~/Documents/Claude/Code/BandInfoForm/backup/install_backup.command
```

Ships the kit to the VM, mints the VM an ed25519 key and authorises it on both
NAS boxes, creates the target directories, writes the GPG passphrase file,
enables the timer, then runs one backup and shows you what landed. Idempotent —
re-run it any time, and after editing any script here.

---

## Restore

```bash
~/Documents/Claude/Code/BandInfoForm/backup/restore_advance.command
```

Pulls the newest archive off Cold Storage (falls back to the Audio NAS),
verifies the sha256 on the Mac, ships it to the VM, and runs the archive's own
restore. `--list` shows what exists, `--archive NAME` picks one, `--host` aims
at different hardware, `--fetch-only` just downloads it.

If the Mac is gone too, the archive restores itself on any Debian box:

```bash
tar xzf band-advance-YYYYMMDD-HHMMSS.tar.gz
sudo ./band-advance-YYYYMMDD-HHMMSS/restore.sh
```

Full detail — options, what's in the archive, the from-absolute-zero runbook,
and the three things a restore can't do for you — is in `RESTORE.md`, which
also ships inside every archive.

---

## What gets captured

Everything the pipeline is made of, from the one machine that holds all of it:

- **The database** — `pg_dump` in custom format *and* as plain gzipped SQL, plus
  exact per-table row counts so a restore can be verified rather than assumed.
- **The uploads** — every stage plot and input list any band has ever sent.
- **The disk-first submission JSON** — the reliability-rule copies that survive
  even when Postgres is down.
- **The deployed app and every tool** — including the `.docx` advance and
  day-sheet templates, the `.j2` email templates, and the list templates, with
  python deps pinned to exactly what was running.
- **The Dropbox Advancing cockpit** — `advance-list.xlsx`, `Show Status Log.xlsx`,
  `Blank Advances/`, `Series Email Templates/`, the FSQ and WP venue archives,
  `_template/`, `_bin/`, `generate.command`.
- **n8n** — every workflow definition, which ones were switched on (import
  doesn't carry that, so the restore replays it), the credentials, and the whole
  n8n database as a backstop.
- **Host wiring** — systemd units, both compose files, IPs, versions, and the
  Cloudflare tunnel facts you'd otherwise have to rediscover.
- **Secrets** — separately, in `secrets.tar.gz.gpg` (AES256, passphrase in
  `TDS_Credentials_CheatSheet.md`).

### Why secrets are separate

Everything except that one file is plaintext, so a restore **always** works.
If the passphrase is ever lost, `restore.sh` generates fresh credentials and
carries on: outstanding `/f/<token>` prefill links stop working and the Graph
credential must be re-entered, and that is the entire cost. A forgotten
passphrase can never hold the data hostage.

---

## How it protects itself

- **Partial beats nothing.** A failed section is recorded, not fatal. The run
  continues, the archive is labelled `PARTIAL` in `MANIFEST.txt`, and the job
  exits non-zero so systemd and the email report both flag it.
- **Verified twice.** After packing, the tarball is re-extracted to a temp dir
  and every inner checksum re-checked before anything ships. After copying, the
  sha256 is recomputed *on each NAS* and compared. A mismatch is a failure, not
  a shrug.
- **Two independent NAS copies.** One unreachable box is a warning; zero
  reachable boxes is a failure, loudly.
- **Restores don't destroy.** A populated database is renamed aside, never
  dropped. An existing app dir is moved aside. A live `~/Dropbox/Nyquist` is
  left alone unless you explicitly say `--force-dropbox`.
- **You hear about it.** Each run POSTs its facts to the n8n workflow
  `band-advance-backup-report`, which builds and sends the email as
  Production@3cdc.org via Graph. The subject says plainly whether Cold Storage
  is good — *"Band Advance backup complete on Cold Storage — 2026-09-13"* or
  *"…FAILED on Cold Storage…"*. The body carries the archive name and size, the
  Cold Storage path, whether the sha256 was re-verified **on the NAS**, all
  eight archives it now holds (newest and oldest labelled), what rotated off
  this run, the captured row counts, and any failures or warnings. Each run also
  writes `/var/backups/band-advance/last_backup.json`.

---

## Operating it

```bash
VM='ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84'

# run one now
$VM 'sudo /opt/band-advance/backup/advance_backup.sh'

# build and verify an archive without shipping or pruning anything
$VM 'sudo /opt/band-advance/backup/advance_backup.sh --dry-run'

# when's the next one
$VM 'systemctl list-timers band-advance-backup --no-pager'

# last run
$VM 'systemctl status band-advance-backup --no-pager; cat /var/backups/band-advance/last_backup.json'
$VM 'ls -t /var/log/band-advance/*.log | head -1 | xargs tail -40'

# what's on the NAS
~/Documents/Claude/Code/BandInfoForm/backup/restore_advance.command --list
```

Settings can be overridden without editing the script — put them in
`/etc/band-advance-backup.conf` on the VM (`KEEP_LOCAL`, `NOTIFY`, `NOTIFY_TO`,
`NOTIFY_ONLY_ON_FAIL`, `NOTIFY_URL`, `TARGETS`).

Per-box retention lives in the `TARGETS` array, one line per NAS:

```
name|ssh-destination|remote-directory|keep|monthly
```

`keep` is how many archives that box holds, rotating. `monthly` is extra
1st-of-month archives kept on top — `0` means a flat rotation, which is what
Cold Storage runs.

### The report workflow

`n8n/backup_report.json` in this repo, deployed as
**Band Advance — Backup Report (Cold Storage)** (id `band-advance-backup-report`,
webhook `POST /webhook/band-advance-backup-report`, gated by the same
`x-advance-token` header the other internal workflows use). The backup script
sends it facts; the workflow owns the formatting and the Graph send, so the
email can be changed without touching the backup script.

`install_backup.command` redeploys it — it resolves the Graph credential id and
the token on the VM, stamps them into the JSON, imports, publishes, and restarts
n8n. **That restart matters:** n8n only mounts a newly imported webhook route on
restart, so without it the first POST comes back 404 from a workflow that is
actually fine.

---

## What this does not cover

- **Cloudflare tunnel ingress.** Remote-managed (`config_src: cloudflare`) — it
  can only be restored through the Cloudflare API, and `RESTORE.md` says how.
- **The git history.** The deployed code is captured in full, which is what a
  rebuild needs. History lives on GitHub and in the nightly
  `com.tinydoor.claude-backup` rsync of `~/Documents/Claude` to the same NAS.
- **Dropbox account linking** on a fresh host — manual, and selective sync must
  be set to `Nyquist/` only before the client is allowed to write.

---

## Once in a while, actually test it

Restore onto a throwaway VM and confirm the row counts match and `/search`
answers. Nothing else proves any of this works. An untested backup is a rumour.
