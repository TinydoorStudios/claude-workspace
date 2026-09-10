# Band Advance — how to bring it all back

This file ships inside every backup archive. If you are reading it out of an
archive, everything you need is in the folder next to it. You do not need the
GitHub repo, the old VM, or a working network to anything but the NAS.

---

## The one command

On the machine that should run the pipeline (a bare Debian 12 box is fine):

```bash
tar xzf band-advance-YYYYMMDD-HHMMSS.tar.gz
sudo ./band-advance-YYYYMMDD-HHMMSS/restore.sh
```

That rebuilds, in order: OS packages → app tree → python venv → Postgres
container → the database → every band-uploaded file → the disk-first submission
records → the systemd service → the Dropbox Advancing tree. Then it verifies
itself: it re-checks every file against the archive's checksums, diffs the
restored table row counts against the counts captured at backup time, and curls
`/healthz`. It prints what matched and what didn't.

If the Mac is alive, the even shorter version — pulls the newest archive off the
NAS, ships it to the target host, runs the restore, and prints the verification:

```bash
~/Documents/Claude/Code/BandInfoForm/backup/restore_advance.command
```

---

## What is in the archive

| Path | What it is |
|---|---|
| `db/advance.dump` | Postgres custom-format dump — what `restore.sh` loads |
| `db/advance.sql.gz` | plain SQL of the same data — readable in a text editor, loadable by any psql, needs no tooling and no version match. The long-term insurance copy. |
| `db/schema.sql` | the DDL on its own |
| `db/counts.txt` | exact row counts at backup time — the restore verifies against these |
| `app/` | the deployed Flask app, `advance_db.py`, `forms_config.py`, every tool in `tools/`, the `.docx` advance/day-sheet templates, the `.j2` email templates, the list templates |
| `app/requirements.lock.txt` | exact pinned python versions that were actually running |
| `appdata/json/` | the disk-first submission records (the reliability-rule copies) |
| `appdata/uploads/` | every stage plot and input list a band has ever uploaded |
| `dropbox/Nyquist/` | the Advancing cockpit — `advance-list.xlsx`, `Show Status Log.xlsx`, `Blank Advances/`, `Series Email Templates/`, the FSQ/WP venue archives, `_template/`, `_bin/`, `generate.command` |
| `n8n/workflows/` | every n8n workflow definition |
| `n8n/workflow_active_state.txt` | which ones were switched on — `import:workflow` does not carry this, so the restore replays it |
| `n8n/n8n_pg.dump` | the whole n8n database, as a backstop |
| `systemd/` | the service + timer units, plus `HOST-NOTES.txt` (IPs, tunnel facts, versions) |
| `docker/` | compose files for `advance-db` and for n8n |
| `secrets.tar.gz.gpg` | AES256. `advance.env`, the DB password, n8n's `.env` (which carries `N8N_ENCRYPTION_KEY`), and a decrypted copy of the n8n credentials. Passphrase is in `TDS_Credentials_CheatSheet.md`. |
| `MANIFEST.txt` | sizes, counts, row counts, and any failure or warning from the run that produced this archive |
| `CHECKSUMS.sha256` | sha256 of every file in the archive |

### The secrets are optional on purpose

Everything except `secrets.tar.gz.gpg` is plaintext, so a restore always works.
If the passphrase is ever lost, `restore.sh` generates fresh credentials and
keeps going. The only cost: previously-issued `/f/<token>` prefill links stop
working, and the Graph credential has to be re-entered in n8n. **No data is
lost either way.** That was the deliberate trade — a forgotten passphrase must
never be able to hold the data hostage.

---

## Restore options

```bash
sudo ./restore.sh                     # everything (default)
sudo ./restore.sh --db-only           # just the database
sudo ./restore.sh --data-only         # database + uploads + submission JSON
sudo ./restore.sh --with-n8n          # also import the n8n workflows + credentials
sudo ./restore.sh --force-dropbox     # overlay onto a live ~/Dropbox/Nyquist
sudo ./restore.sh --dropbox-dest DIR  # put the Advancing tree somewhere else
sudo ./restore.sh --app-dir DIR       # install somewhere other than /opt/band-advance
sudo ./restore.sh --yes               # no prompts
```

### It refuses to destroy things

- An `advance` database that already has rows is **renamed** to
  `advance_pre_restore_<stamp>`, never dropped. Both are then sitting there and
  you can compare them.
- An existing `/opt/band-advance` is moved to `/opt/band-advance.pre-restore.<stamp>`.
- A `~/Dropbox/Nyquist` that already has content is **left alone** — the archived
  tree lands in `./restored-Nyquist-<stamp>` instead, and the restore says so.
  Pass `--force-dropbox` only when you actually mean to overlay a live folder.
- n8n is not touched at all unless you pass `--with-n8n`.

---

## The three things a restore cannot do for you

1. **Cloudflare ingress.** `advance.tinydoorstudios.com` → `http://localhost:8097`.
   The `n8n-tunnel` is **remote-managed** (`config_src: cloudflare`) — editing a
   local `config.yml` fixes nothing. Add the ingress rule via the Cloudflare API.
   Token and account/zone IDs are in `TDS_Credentials_CheatSheet.md`; there are
   ready-made scripts at `audio/Live Sound KB/_tools/KB-Fix-Tunnel-API.command`.
2. **Dropbox linking.** On a fresh host, link the headless client
   (`~/.dropbox-dist/dropboxd` + `~/dropbox.py`) and set selective sync to
   `Nyquist/` **only** before letting it write anything. Nothing outside
   `Nyquist/` is ever written or deleted from the VM side.
3. **The Graph client secret**, if secrets were regenerated. Re-enter it in the
   n8n credential — and note it goes in the Client **Secret Value** field, not
   the Secret **ID**. That exact mix-up cost a whole debugging session once.

---

## Rebuilding from absolute zero — full runbook

If the VM is gone and you are starting on new hardware:

```bash
# 1. New Debian 12 VM, static IP, your SSH key in ~/.ssh/authorized_keys
# 2. Pull the newest archive off either NAS
scp brian@192.168.200.35:/mnt/The-Pool/ClaudeBackup/band-advance/latest.tar.gz .
#    (or the second copy, if Cold Storage is the thing that died)
scp brian@192.168.200.36:/mnt/AudioNas/brian/band-advance-backups/latest.tar.gz .

# 3. Restore
tar xzf latest.tar.gz && sudo ./band-advance-*/restore.sh

# 4. Bring n8n back too, if this host is also replacing the n8n VM
cd /opt/n8n && sudo docker compose up -d
sudo ./band-advance-*/restore.sh --with-n8n

# 5. Point the tunnel at the new host (Cloudflare API — see above)
# 6. Link Dropbox, selective-sync to Nyquist/ only
# 7. Check it: https://advance.tinydoorstudios.com/search   (passcode: lockdown)
```

Where things live once restored:

| Piece | Path |
|---|---|
| App | `/opt/band-advance/` (`app.py`, `advance_db.py`, `forms_config.py`, `templates/`) |
| Tools | `/opt/band-advance/tools/` |
| Runtime data | `/opt/band-advance/data/` (submission JSON + `uploads/`) |
| Secrets | `/opt/band-advance/advance.env`, `/opt/band-advance/db/.env` |
| Database | `advance-db` container, `127.0.0.1:5433`, volume `advance_pgdata` |
| Service | `band-advance.service` → gunicorn on `:8097` |
| Backups | `/opt/band-advance/backup/`, timer `band-advance-backup.timer` |
| Advancing cockpit | `~/Dropbox/Nyquist/` |

---

## Checking a backup without restoring it

```bash
tar tzf band-advance-YYYYMMDD-HHMMSS.tar.gz | head          # does it open
tar xzf band-advance-YYYYMMDD-HHMMSS.tar.gz
cd band-advance-YYYYMMDD-HHMMSS
cat MANIFEST.txt                                            # what's inside, and did anything fail
sha256sum -c CHECKSUMS.sha256                               # is it intact
zcat db/advance.sql.gz | grep -c "^INSERT\|^COPY"           # is there really data in there
```

A restore drill onto a throwaway VM, once in a while, is the only thing that
actually proves any of this. An untested backup is a rumour.
