#!/usr/bin/env bash
# =============================================================================
# Band Advance — weekly full backup
# =============================================================================
# Runs ON the n8n VM (192.168.200.84), which is the one machine that holds
# every moving part of this pipeline: the Postgres database, the deployed app,
# the uploaded band files, the env/secrets, the n8n workflows, and a live
# Dropbox mirror of ~/Dropbox/Nyquist (the Advancing cockpit).
#
# It builds ONE self-contained, self-restoring archive and pushes it to both
# TrueNAS boxes. Every archive carries its own restore.sh and RESTORE.md — you
# never need this repo, this script, or a network to rebuild from one. It also
# keeps a second, completely different kind of backup on Cold Storage only: a
# plain uncompressed mirror of the live Dropbox folder, no tar/zip, browsable
# directly for instant access in an emergency (Brian, 2026-09-11).
#
# Scheduled by band-advance-backup.timer (Sundays 03:15). Manual run:
#   sudo /opt/band-advance/backup/advance_backup.sh
#   sudo /opt/band-advance/backup/advance_backup.sh --dry-run
#
# Design rules:
#   • Never abort the whole run on one failed section — collect the failure,
#     keep going, label the archive PARTIAL, exit non-zero at the end.
#     A partial backup beats no backup.
#   • Everything except secrets is plaintext, so a restore ALWAYS works.
#     Secrets ride in secrets.tar.gz.gpg; a lost passphrase costs convenience,
#     never data (restore.sh generates fresh secrets and carries on).
#   • Verify after writing: sha256 checked locally AND on each NAS.
# =============================================================================
set -uo pipefail

# ---------------------------------------------------------------- config ----
APP_DIR="${APP_DIR:-/opt/band-advance}"
DB_CONTAINER="${DB_CONTAINER:-advance-db}"
DB_USER="${DB_USER:-advance}"
DB_NAME="${DB_NAME:-advance}"
DB_COMPOSE="${DB_COMPOSE:-$APP_DIR/db/docker-compose.yml}"
N8N_DIR="${N8N_DIR:-/opt/n8n}"
DROPBOX_DIR="${DROPBOX_DIR:-/home/brian/Dropbox/Nyquist}"
WORKROOT="${WORKROOT:-/var/backups/band-advance}"
LOG_DIR="${LOG_DIR:-/var/log/band-advance}"
PASS_FILE="${PASS_FILE:-/etc/band-advance-backup.pass}"
SSH_KEY="${SSH_KEY:-/home/brian/.ssh/nas_backup}"
RUN_AS="${RUN_AS:-brian}"

# NAS targets:  name|ssh-destination|remote-directory|keep|monthly
#   keep    — how many archives this box holds, rotating (oldest deleted)
#   monthly — extra 1st-of-month archives held on top; 0 means flat rotation
#
# Audio NAS is the short-term primary — a flat rotating 8 (Brian, 2026-09-10,
# swapped from Cold Storage). Cold Storage is the long-term archive: 12 weekly
# plus a 1st-of-month copy held for 24 months, so there's a real two-year tail.
TARGETS=(
  "coldstorage|brian@192.168.200.35|/mnt/The-Pool/ClaudeBackup/band-advance|12|24"
  "audionas|brian@192.168.200.36|/mnt/AudioNas/brian/band-advance-backups|8|0"
)

# Cold-Storage-only, uncompressed mirror of the live Dropbox Nyquist folder
# (Brian, 2026-09-11): no tar, no zip, nothing to extract — the whole point is
# that in an emergency, someone can open this directory on the NAS directly
# and every advance/template/status sheet is just... there. A true mirror
# (rsync --delete), not a version history — that's what the tarball archive
# above is for. Deliberately Cold-Storage-only, not also on Audio NAS.
MIRROR_DIR="${MIRROR_DIR:-/mnt/The-Pool/ClaudeBackup/band-advance-dropbox-mirror}"

KEEP_LOCAL="${KEEP_LOCAL:-4}"            # archives kept on the VM
KEEP_WEEKLY="${KEEP_WEEKLY:-12}"         # fallback when a target omits its keep
KEEP_MONTHLY="${KEEP_MONTHLY:-24}"       # fallback when a target omits its monthly
N8N_PGDUMP_MAX_MB="${N8N_PGDUMP_MAX_MB:-1024}"

# Email report — the n8n "Band Advance — Backup Report" workflow owns the
# formatting and the send; this script just hands it the facts.
NOTIFY="${NOTIFY:-1}"
NOTIFY_TO="${NOTIFY_TO:-blloyd@3cdc.org}"
NOTIFY_ONLY_ON_FAIL="${NOTIFY_ONLY_ON_FAIL:-0}"
NOTIFY_URL="${NOTIFY_URL:-http://localhost:5678/webhook/band-advance-backup-report}"

[ -f /etc/band-advance-backup.conf ] && . /etc/band-advance-backup.conf

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# ------------------------------------------------------------- plumbing -----
STAMP="$(date +%Y%m%d-%H%M%S)"
DAY_OF_MONTH="$(date +%d)"
NAME="band-advance-$STAMP"
STAGE="$WORKROOT/$NAME"
ARCHIVE="$WORKROOT/$NAME.tar.gz"
mkdir -p "$WORKROOT" "$LOG_DIR"
LOG="$LOG_DIR/backup-$STAMP.log"
FAILURES=()
WARNINGS=()
DB_COUNTS=""
CS_OK=0; CS_VERIFIED=0; CS_DIR=""; CS_KEEP=8; CS_PRUNED=""; CS_REMAIN=""
AN_OK=0; AN_VERIFIED=0; AN_DIR=""; AN_KEEP=8; AN_PRUNED=""; AN_REMAIN=""
MIRROR_OK=0; MIRROR_FILES=0

log()  { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"; }
step() { log ""; log "── $* ────────────────────────────────────────"; }
ok()   { log "   ok: $*"; }
warn() { log "   WARN: $*"; WARNINGS+=("$*"); }
fail() { log "   FAIL: $*"; FAILURES+=("$*"); }

sha_of() { sha256sum "$1" | awk '{print $1}'; }
human()  { du -sh "$1" 2>/dev/null | awk '{print $1}'; }

log "═══ Band Advance backup — $STAMP ═══"
log "stage:   $STAGE"
[ "$DRY_RUN" = 1 ] && log "MODE:    DRY RUN (build + verify locally, no NAS push, no prune)"

mkdir -p "$STAGE"/{db,app,appdata,dropbox,n8n,systemd,docker,secrets-plain}

# ============================================================================
# 1. Postgres — the advance database (the irreplaceable part)
# ============================================================================
step "1/10  advance database"
if docker inspect "$DB_CONTAINER" >/dev/null 2>&1; then
  # Custom-format dump: compact, the one restore.sh uses.
  if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc \
       > "$STAGE/db/advance.dump" 2>>"$LOG" && [ -s "$STAGE/db/advance.dump" ]; then
    ok "advance.dump ($(human "$STAGE/db/advance.dump"))"
  else
    fail "pg_dump custom-format failed"
  fi

  # Plain SQL as well — readable by eye, loadable by any psql, forever.
  if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" \
       > "$STAGE/db/advance.sql" 2>>"$LOG" && [ -s "$STAGE/db/advance.sql" ]; then
    gzip -9 "$STAGE/db/advance.sql"
    ok "advance.sql.gz ($(human "$STAGE/db/advance.sql.gz"))"
  else
    fail "pg_dump plain-SQL failed"
  fi

  # EXACT row counts (not pg_stat estimates), so a restore can be verified
  # against reality rather than hope. restore.sh diffs against this file.
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -tAF'|' -c \
    "select relname,
            (xpath('/row/c/text()', query_to_xml(
               format('select count(*) as c from %I.%I', schemaname, relname),
               false, true, '')))[1]::text::bigint
     from pg_stat_user_tables order by relname;" \
    > "$STAGE/db/counts.txt" 2>>"$LOG" && ok "exact row counts captured" || warn "row counts unavailable"
  # Held for the emailed report — $STAGE is deleted once the tarball is built.
  DB_COUNTS="$(cat "$STAGE/db/counts.txt" 2>/dev/null)"

  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
    "select version();" > "$STAGE/db/pg_version.txt" 2>/dev/null
else
  fail "container '$DB_CONTAINER' not running — NO DATABASE IN THIS ARCHIVE"
fi

cp "$APP_DIR/db/schema.sql" "$STAGE/db/schema.sql" 2>/dev/null \
  || warn "schema.sql not found at $APP_DIR/db/schema.sql (restore falls back to the dump's own DDL)"

# ============================================================================
# 2. Application code — exactly what is running, not what a repo thinks is
# ============================================================================
step "2/10  deployed application"
if rsync -a \
     --exclude 'venv/' --exclude '__pycache__/' --exclude '*.pyc' \
     --exclude 'app.py.bak.*' --exclude 'data/' --exclude '.git/' \
     --exclude 'tools/_package/' --exclude 'tools/filled/' \
     "$APP_DIR/" "$STAGE/app/" >>"$LOG" 2>&1; then
  # advance.env is a secret; it goes in the encrypted bundle, not here.
  rm -f "$STAGE/app/advance.env" "$STAGE/app/db/.env"
  ok "app tree ($(human "$STAGE/app"))"
else
  fail "app tree copy failed"
fi
"$APP_DIR/venv/bin/pip" freeze > "$STAGE/app/requirements.lock.txt" 2>/dev/null \
  && ok "python deps pinned (requirements.lock.txt)" || warn "pip freeze failed"

# ============================================================================
# 3. Runtime data — disk-first submission JSON + every band-uploaded file
# ============================================================================
step "3/10  runtime data (submissions + uploads)"
mkdir -p "$STAGE/appdata/json" "$STAGE/appdata/uploads"
if compgen -G "$APP_DIR/data/*.json" >/dev/null; then
  cp -p "$APP_DIR"/data/*.json "$STAGE/appdata/json/" 2>>"$LOG" \
    && ok "$(ls -1 "$STAGE/appdata/json" | wc -l) submission JSON files" \
    || fail "submission JSON copy failed"
else
  warn "no submission JSON found in $APP_DIR/data"
fi
cp -p "$APP_DIR/data/db_errors.log" "$STAGE/appdata/" 2>/dev/null

if [ -d "$APP_DIR/data/uploads" ]; then
  rsync -a "$APP_DIR/data/uploads/" "$STAGE/appdata/uploads/" >>"$LOG" 2>&1 \
    && ok "$(find "$STAGE/appdata/uploads" -type f | wc -l) uploaded files ($(human "$STAGE/appdata/uploads"))" \
    || fail "uploads copy failed"
else
  fail "uploads directory missing — band stage plots / input lists NOT backed up"
fi

# ============================================================================
# 4. Dropbox — the Advancing cockpit: the xlsx sheets, the venue archives,
#    the blank advances, the series email templates, generate.command
# ============================================================================
step "4/10  Dropbox Nyquist tree"
if [ -d "$DROPBOX_DIR" ]; then
  mkdir -p "$STAGE/dropbox/Nyquist"
  if rsync -a --exclude '.DS_Store' --exclude '~\$*' --exclude '.dropbox*' \
       "$DROPBOX_DIR/" "$STAGE/dropbox/Nyquist/" >>"$LOG" 2>&1; then
    ok "$(find "$STAGE/dropbox/Nyquist" -type f | wc -l) files ($(human "$STAGE/dropbox/Nyquist"))"
    for must in "advance-list.xlsx" "Show Status Log.xlsx" "Blank Advances" "Series Email Templates"; do
      [ -e "$STAGE/dropbox/Nyquist/$must" ] && ok "present: $must" \
        || warn "expected but missing from Dropbox tree: $must"
    done
  else
    fail "Dropbox tree copy failed"
  fi
else
  fail "$DROPBOX_DIR not found — the Advancing cockpit is NOT in this archive"
fi

# ============================================================================
# 5. n8n — the automation half (workflows, credentials, full DB)
# ============================================================================
step "5/10  n8n workflows + credentials"
mkdir -p "$STAGE/n8n/workflows"
N8N_CTR="${N8N_CTR:-n8n-n8n-1}"
NC="docker exec $N8N_CTR n8n"
if $NC export:workflow --all --separate --output=/tmp/n8n_wf_export >/dev/null 2>>"$LOG"; then
  docker cp "$N8N_CTR:/tmp/n8n_wf_export/." "$STAGE/n8n/workflows/" >>"$LOG" 2>&1 \
    && ok "$(ls -1 "$STAGE/n8n/workflows" | wc -l) workflows exported" \
    || fail "n8n workflow export copy-out failed"
  docker exec "$N8N_CTR" rm -rf /tmp/n8n_wf_export >/dev/null 2>&1
else
  fail "n8n export:workflow failed"
fi

# Which workflows are ACTIVE is not carried by import:workflow — record it.
docker exec n8n-postgres-1 psql -U "$(grep '^POSTGRES_USER=' "$N8N_DIR/.env" | cut -d= -f2)" \
  -d "$(grep '^POSTGRES_DB=' "$N8N_DIR/.env" | cut -d= -f2)" -tAF'|' \
  -c "select id, active, name from workflow_entity order by name;" \
  > "$STAGE/n8n/workflow_active_state.txt" 2>>"$LOG" \
  && ok "active-state map captured" || warn "could not read n8n workflow active state"

# Credentials, still encrypted with n8n's own key (that key rides in secrets/).
if $NC export:credentials --all --output=/tmp/n8n_creds.json >/dev/null 2>>"$LOG"; then
  docker cp "$N8N_CTR:/tmp/n8n_creds.json" "$STAGE/n8n/credentials.enc.json" >>"$LOG" 2>&1 \
    && ok "credentials exported (encrypted at rest)" || warn "credentials copy-out failed"
  docker exec "$N8N_CTR" rm -f /tmp/n8n_creds.json >/dev/null 2>&1
else
  warn "n8n export:credentials failed"
fi

# Full n8n database — the belt to the export's braces.
N8N_PG_USER="$(grep '^POSTGRES_USER=' "$N8N_DIR/.env" | cut -d= -f2)"
N8N_PG_DB="$(grep '^POSTGRES_DB=' "$N8N_DIR/.env" | cut -d= -f2)"
if docker exec n8n-postgres-1 pg_dump -U "$N8N_PG_USER" -d "$N8N_PG_DB" -Fc \
     > "$STAGE/n8n/n8n_pg.dump" 2>>"$LOG"; then
  SZ=$(( $(stat -c%s "$STAGE/n8n/n8n_pg.dump") / 1048576 ))
  if [ "$SZ" -gt "$N8N_PGDUMP_MAX_MB" ]; then
    rm -f "$STAGE/n8n/n8n_pg.dump"
    warn "n8n pg dump ${SZ}MB exceeded cap ${N8N_PGDUMP_MAX_MB}MB — dropped (workflow JSON still present)"
  else
    ok "n8n_pg.dump (${SZ}MB)"
  fi
else
  warn "n8n pg_dump failed (workflow JSON export still covers the rebuild)"
fi
cp "$APP_DIR/n8n"/*.json "$STAGE/n8n/" 2>/dev/null   # repo copies, as shipped

# ============================================================================
# 6. Host wiring — systemd units, docker compose, cloudflare ingress note
# ============================================================================
step "6/10  host configuration"
for unit in band-advance.service band-advance-backup.service band-advance-backup.timer; do
  cp "/etc/systemd/system/$unit" "$STAGE/systemd/$unit" 2>/dev/null && ok "unit: $unit"
done
cp "$APP_DIR/db/docker-compose.yml" "$STAGE/docker/advance-db.compose.yml" 2>/dev/null && ok "advance-db compose"
cp "$N8N_DIR/docker-compose.yml"    "$STAGE/docker/n8n.compose.yml"        2>/dev/null && ok "n8n compose"
{
  echo "host:        $(hostname)  $(hostname -I 2>/dev/null | awk '{print $1}')"
  echo "os:          $(. /etc/os-release; echo "$PRETTY_NAME")"
  echo "docker:      $(docker --version 2>/dev/null)"
  echo "python:      $(python3 --version 2>&1)"
  echo "public url:  https://advance.tinydoorstudios.com  ->  cloudflared ingress -> localhost:8097"
  echo "tunnel:      n8n-tunnel is REMOTE-managed (config_src: cloudflare) — local config.yml is ignored."
  echo "             Re-add ingress via the Cloudflare API only. Token/IDs: TDS_Credentials_CheatSheet.md"
} > "$STAGE/systemd/HOST-NOTES.txt"

# ============================================================================
# 7. Secrets — separate, encrypted, and never required for a data restore
# ============================================================================
step "7/10  secrets bundle"
cp "$APP_DIR/advance.env" "$STAGE/secrets-plain/advance.env" 2>/dev/null && ok "advance.env"
cp "$APP_DIR/db/.env"     "$STAGE/secrets-plain/advance-db.env" 2>/dev/null && ok "advance-db .env"
cp "$N8N_DIR/.env"        "$STAGE/secrets-plain/n8n.env" 2>/dev/null && ok "n8n .env (carries N8N_ENCRYPTION_KEY)"
# Decrypted n8n credentials — the only form usable if the encryption key is ever lost.
$NC export:credentials --all --decrypted --output=/tmp/n8n_creds_dec.json >/dev/null 2>&1 \
  && docker cp "$N8N_CTR:/tmp/n8n_creds_dec.json" \
       "$STAGE/secrets-plain/n8n_credentials.decrypted.json" >/dev/null 2>&1 \
  && ok "n8n credentials (decrypted copy)" || warn "decrypted credential export unavailable"
docker exec "$N8N_CTR" rm -f /tmp/n8n_creds_dec.json >/dev/null 2>&1

PASSPHRASE="lockdown"
[ -r "$PASS_FILE" ] && PASSPHRASE="$(head -n1 "$PASS_FILE")"
if [ -n "$(ls -A "$STAGE/secrets-plain" 2>/dev/null)" ]; then
  tar -C "$STAGE" -czf "$STAGE/secrets.tar.gz" secrets-plain 2>>"$LOG"
  if printf '%s' "$PASSPHRASE" | gpg --batch --yes --quiet --pinentry-mode loopback \
       --passphrase-fd 0 --symmetric --cipher-algo AES256 \
       -o "$STAGE/secrets.tar.gz.gpg" "$STAGE/secrets.tar.gz" 2>>"$LOG"; then
    ok "secrets.tar.gz.gpg (AES256)"
  else
    fail "GPG encryption failed — secrets NOT included"
  fi
  shred -u "$STAGE/secrets.tar.gz" 2>/dev/null || rm -f "$STAGE/secrets.tar.gz"
else
  fail "no secret files found to bundle"
fi
find "$STAGE/secrets-plain" -type f -exec shred -u {} \; 2>/dev/null
rm -rf "$STAGE/secrets-plain"

# ============================================================================
# 8. Manifest, restore script, checksums, tarball
# ============================================================================
step "8/10  manifest + restore kit + package"
cp "$APP_DIR/backup/restore.sh" "$STAGE/restore.sh" 2>/dev/null \
  || cp "$(dirname "$0")/restore.sh" "$STAGE/restore.sh" 2>/dev/null
if [ -f "$STAGE/restore.sh" ]; then chmod +x "$STAGE/restore.sh"; ok "restore.sh embedded"
else fail "restore.sh NOT embedded — this archive cannot self-restore"; fi
cp "$APP_DIR/backup/RESTORE.md" "$STAGE/RESTORE.md" 2>/dev/null \
  || cp "$(dirname "$0")/RESTORE.md" "$STAGE/RESTORE.md" 2>/dev/null

STATUS="COMPLETE"
[ ${#FAILURES[@]} -gt 0 ] && STATUS="PARTIAL"
{
  echo "Band Advance — backup manifest"
  echo "=============================="
  echo "archive:     $NAME"
  echo "created:     $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "source host: $(hostname) ($(hostname -I 2>/dev/null | awk '{print $1}'))"
  echo "status:      $STATUS"
  echo
  echo "RESTORE IN ONE COMMAND"
  echo "----------------------"
  echo "  tar xzf $NAME.tar.gz && sudo ./$NAME/restore.sh"
  echo "(read RESTORE.md for options and for the full rebuild-from-scratch path)"
  echo
  echo "CONTENTS"
  echo "--------"
  printf '  %-34s %s\n' "db/advance.dump"        "Postgres custom-format dump (restore.sh uses this)"
  printf '  %-34s %s\n' "db/advance.sql.gz"      "plain SQL dump — readable, portable, no tooling needed"
  printf '  %-34s %s\n' "db/schema.sql"          "DDL"
  printf '  %-34s %s\n' "db/counts.txt"          "row counts at backup time — verify the restore against these"
  printf '  %-34s %s\n' "app/"                   "the deployed Flask app + all offline tools + doc/email templates"
  printf '  %-34s %s\n' "app/requirements.lock.txt" "exact pinned python deps"
  printf '  %-34s %s\n' "appdata/json/"          "disk-first submission records"
  printf '  %-34s %s\n' "appdata/uploads/"       "every band-uploaded stage plot / input list"
  printf '  %-34s %s\n' "dropbox/Nyquist/"       "the Advancing cockpit: xlsx sheets, venue archives, blank advances, series email templates"
  printf '  %-34s %s\n' "n8n/workflows/"         "all n8n workflow definitions"
  printf '  %-34s %s\n' "n8n/workflow_active_state.txt" "which workflows were active (import does NOT carry this)"
  printf '  %-34s %s\n' "n8n/n8n_pg.dump"        "full n8n database"
  printf '  %-34s %s\n' "systemd/"               "service + timer units, host notes"
  printf '  %-34s %s\n' "docker/"                "compose files for advance-db and n8n"
  printf '  %-34s %s\n' "secrets.tar.gz.gpg"     "AES256, passphrase in TDS_Credentials_CheatSheet.md. NOT required — restore.sh generates fresh secrets if it can't open this."
  echo
  echo "SIZES"
  echo "-----"
  du -sh "$STAGE"/* 2>/dev/null | sed 's|'"$STAGE"'/|  |'
  echo
  echo "DATABASE ROW COUNTS AT BACKUP TIME"
  echo "----------------------------------"
  sed 's/^/  /' "$STAGE/db/counts.txt" 2>/dev/null || echo "  (unavailable)"
  echo
  if [ ${#FAILURES[@]} -gt 0 ]; then
    echo "FAILURES IN THIS RUN (archive is PARTIAL)"
    echo "----------------------------------------"
    printf '  ! %s\n' "${FAILURES[@]}"
    echo
  fi
  if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "WARNINGS"
    echo "--------"
    printf '  - %s\n' "${WARNINGS[@]}"
  fi
} > "$STAGE/MANIFEST.txt"

( cd "$STAGE" && find . -type f ! -name CHECKSUMS.sha256 -print0 \
    | sort -z | xargs -0 sha256sum > CHECKSUMS.sha256 )
ok "checksums for $(wc -l < "$STAGE/CHECKSUMS.sha256") files"

if tar -C "$WORKROOT" -czf "$ARCHIVE" "$NAME" 2>>"$LOG"; then
  ARCHIVE_SHA="$(sha_of "$ARCHIVE")"
  echo "$ARCHIVE_SHA  $NAME.tar.gz" > "$ARCHIVE.sha256"
  ok "archive: $NAME.tar.gz ($(human "$ARCHIVE"))"
else
  fail "tar failed — no archive produced"
fi

# Prove the tarball actually opens and its inner checksums hold, before shipping.
if [ -f "$ARCHIVE" ]; then
  if tar -tzf "$ARCHIVE" >/dev/null 2>&1; then ok "tarball integrity verified"
  else fail "tarball is unreadable"; fi
  VERIFY_DIR="$(mktemp -d)"
  tar -C "$VERIFY_DIR" -xzf "$ARCHIVE" 2>/dev/null
  if ( cd "$VERIFY_DIR/$NAME" && sha256sum -c CHECKSUMS.sha256 --quiet 2>>"$LOG" ); then
    ok "inner checksums verified after round-trip"
  else
    fail "inner checksum mismatch after round-trip"
  fi
  rm -rf "$VERIFY_DIR"
fi
rm -rf "$STAGE"

# ============================================================================
# 9. Ship to both NAS boxes, verify remotely, prune
# ============================================================================
step "9/10  push to NAS + retention"
SSH_OPTS="-i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new"
PUSHED=0
if [ "$DRY_RUN" = 1 ]; then
  log "   (dry run — skipping NAS push and prune)"
elif [ ! -f "$ARCHIVE" ]; then
  fail "no archive to push"
else
  for t in "${TARGETS[@]}"; do
    IFS='|' read -r NM HOST DIR TKEEP TMONTH <<< "$t"
    TKEEP="${TKEEP:-$KEEP_WEEKLY}"; TMONTH="${TMONTH:-$KEEP_MONTHLY}"
    log "   → $NM ($HOST:$DIR) — holding $TKEEP$([ "$TMONTH" -gt 0 ] && echo " + $TMONTH monthly")"
    [ "$NM" = "coldstorage" ] && { CS_DIR="$DIR"; CS_KEEP="$TKEEP"; }
    [ "$NM" = "audionas" ]    && { AN_DIR="$DIR"; AN_KEEP="$TKEEP"; }

    if ! ssh $SSH_OPTS "$HOST" "mkdir -p '$DIR'" 2>>"$LOG"; then
      fail "$NM unreachable — archive NOT copied there"
      continue
    fi
    if ! rsync -a --partial -e "ssh $SSH_OPTS" \
           "$ARCHIVE" "$ARCHIVE.sha256" "$HOST:$DIR/" >>"$LOG" 2>&1; then
      fail "$NM: rsync failed"
      continue
    fi
    [ "$NM" = "coldstorage" ] && CS_OK=1
    [ "$NM" = "audionas" ]    && AN_OK=1

    REMOTE_SHA="$(ssh $SSH_OPTS "$HOST" "sha256sum '$DIR/$NAME.tar.gz' 2>/dev/null | awk '{print \$1}'")"
    if [ "$REMOTE_SHA" != "$ARCHIVE_SHA" ]; then
      fail "$NM: checksum MISMATCH after copy (local $ARCHIVE_SHA / remote ${REMOTE_SHA:-none})"
      continue
    fi
    ok "$NM: copied and checksum-verified on the NAS"
    PUSHED=$((PUSHED+1))
    [ "$NM" = "coldstorage" ] && CS_VERIFIED=1
    [ "$NM" = "audionas" ]    && AN_VERIFIED=1

    # Keep a restore bootstrap beside the archives.
    ssh $SSH_OPTS "$HOST" "cd '$DIR' && ln -sf '$NAME.tar.gz' latest.tar.gz && ln -sf '$NAME.tar.gz.sha256' latest.tar.gz.sha256" 2>>"$LOG"

    # ---- retention, on the NAS --------------------------------------------
    # Two zsh facts matter here, because the TrueNAS login shell IS zsh:
    #   1. an unmatched glob ABORTS the command instead of passing through, so
    #      everything is matched with find, never a glob;
    #   2. zsh does NOT word-split an unquoted variable, so the doomed list is
    #      passed through a file and read line by line, never expanded inline.
    if [ "$TMONTH" -gt 0 ]; then
      SELECT_DOOMED="{ find . -maxdepth 1 -name 'band-advance-*.tar.gz' -printf '%f\\n' 2>/dev/null \
            | grep -vE 'band-advance-[0-9]{6}01-' | sort -r | tail -n +$((TKEEP+1)) ;
          find . -maxdepth 1 -name 'band-advance-*01-*.tar.gz' -printf '%f\\n' 2>/dev/null \
            | sort -r | tail -n +$((TMONTH+1)) ; }"
    else
      SELECT_DOOMED="find . -maxdepth 1 -name 'band-advance-*.tar.gz' -printf '%f\\n' 2>/dev/null \
            | sort -r | tail -n +$((TKEEP+1))"
    fi
    RET_OUT="$(ssh $SSH_OPTS "$HOST" "
      cd '$DIR' || exit 0
      D=/tmp/.ba_prune_$STAMP
      $SELECT_DOOMED > \"\$D\" 2>/dev/null
      echo '---PRUNED---'
      cat \"\$D\"
      while read -r f; do [ -n \"\$f\" ] && rm -f \"./\$f\" \"./\$f.sha256\"; done < \"\$D\"
      rm -f \"\$D\"
      echo '---REMAINING---'
      find . -maxdepth 1 -name 'band-advance-*.tar.gz' -printf '%f\\n' 2>/dev/null | sort -r
    " 2>>"$LOG")"

    PRUNED_LIST="$(printf '%s\n' "$RET_OUT" | sed -n '/^---PRUNED---$/,/^---REMAINING---$/p' | grep -v '^---' )"
    REMAIN_LIST="$(printf '%s\n' "$RET_OUT" | sed -n '/^---REMAINING---$/,$p'                | grep -v '^---' )"
    NPRUNED=$(printf '%s\n' "$PRUNED_LIST" | grep -c . )
    NREMAIN=$(printf '%s\n' "$REMAIN_LIST" | grep -c . )
    ok "$NM: now holding $NREMAIN of $TKEEP$([ "$NPRUNED" -gt 0 ] && echo ", rotated off $NPRUNED")"
    if [ "$NM" = "coldstorage" ]; then CS_PRUNED="$PRUNED_LIST"; CS_REMAIN="$REMAIN_LIST"; fi
    if [ "$NM" = "audionas" ];    then AN_PRUNED="$PRUNED_LIST"; AN_REMAIN="$REMAIN_LIST"; fi
  done

  [ "$PUSHED" -eq 0 ] && fail "archive reached ZERO NAS targets — it exists only on this VM"

  # Local retention on the VM.
  ls -1 "$WORKROOT"/band-advance-*.tar.gz 2>/dev/null | sort -r | tail -n +$((KEEP_LOCAL+1)) \
    | while read -r f; do rm -f "$f" "$f.sha256"; done
  find "$LOG_DIR" -name 'backup-*.log' -mtime +120 -delete 2>/dev/null
fi

# ============================================================================
# 10. Cold Storage only — a plain, uncompressed mirror of the live Dropbox
#     folder, browsable directly with no extraction step (Brian, 2026-09-11)
# ============================================================================
step "10/10 Cold Storage — uncompressed Dropbox mirror"
if [ "$DRY_RUN" = 1 ]; then
  log "   (dry run — skipping the mirror sync)"
elif [ ! -d "$DROPBOX_DIR" ]; then
  fail "mirror: $DROPBOX_DIR not found on this VM — nothing to sync"
else
  CS_HOST=""
  for t in "${TARGETS[@]}"; do
    IFS='|' read -r NM HOST _ <<< "$t"
    [ "$NM" = "coldstorage" ] && CS_HOST="$HOST"
  done
  if [ -z "$CS_HOST" ]; then
    fail "mirror: no coldstorage entry in TARGETS — can't find a host"
  elif ! ssh $SSH_OPTS "$CS_HOST" "mkdir -p '$MIRROR_DIR'" 2>>"$LOG"; then
    fail "mirror: $CS_HOST unreachable — Dropbox mirror NOT updated"
  else
    # --delete makes this a TRUE mirror of what's in Dropbox right now, not
    # an accumulating pile — the point is "exactly what's really there
    # today," which is what someone needs in an emergency, not a history
    # (the tarball archive above is what covers history/point-in-time).
    if rsync -a --delete --partial -e "ssh $SSH_OPTS" \
           "$DROPBOX_DIR/" "$CS_HOST:$MIRROR_DIR/" >>"$LOG" 2>&1; then
      MIRROR_OK=1
      MIRROR_FILES=$(ssh $SSH_OPTS "$CS_HOST" "find '$MIRROR_DIR' -type f | wc -l" 2>/dev/null | tr -d ' ')
      ok "mirror: synced — $MIRROR_FILES files now on Cold Storage at $MIRROR_DIR, no extraction needed"
    else
      fail "mirror: rsync to Cold Storage failed"
    fi
  fi
fi

# ------------------------------------------------------------- summary ------
step "summary"
[ ${#FAILURES[@]} -gt 0 ] && STATUS="PARTIAL"
log "status:        $STATUS"
log "archive:       ${ARCHIVE:-none}  ($(human "$ARCHIVE" 2>/dev/null))"
log "nas copies:    $PUSHED of ${#TARGETS[@]}"
log "warnings:      ${#WARNINGS[@]}"
log "failures:      ${#FAILURES[@]}"
[ ${#FAILURES[@]} -gt 0 ] && printf '  ! %s\n' "${FAILURES[@]}" | tee -a "$LOG"
log "log:           $LOG"

# Hand the facts to the n8n workflow "Band Advance — Backup Report", which
# owns the formatting and the send. The token lives in advance.env; the
# n8n-Postgres scrape is the fallback for a host where that file isn't readable.
if [ "$NOTIFY" = "1" ] && [ "$DRY_RUN" = 0 ]; then
  if [ "$NOTIFY_ONLY_ON_FAIL" = "1" ] && [ "$STATUS" = "COMPLETE" ] \
     && [ "$CS_VERIFIED" = 1 ] && [ "$AN_VERIFIED" = 1 ]; then
    log "notify: skipped (both NAS boxes verified, notify-only-on-fail)"
  else
    TOKEN="$(grep -m1 '^ADVANCE_INTERNAL_TOKEN=' "$APP_DIR/advance.env" 2>/dev/null | cut -d= -f2-)"
    if [ -z "$TOKEN" ]; then
      TOKEN="$(docker exec n8n-postgres-1 psql -U "$N8N_PG_USER" -d "$N8N_PG_DB" -tAc \
        "select nodes::text from workflow_entity where name ilike '%backup report%' limit 1;" 2>/dev/null \
        | grep -oE "EXPECTED_TOKEN = '[^']+'" | head -1 | sed "s/.*'\(.*\)'/\1/")"
    fi
    if [ -n "$TOKEN" ]; then
      PAYLOAD="$(mktemp)"
      BA_STAMP="$STAMP" BA_STATUS="$STATUS" BA_ARCHIVE="$NAME.tar.gz" \
      BA_BYTES="$(stat -c%s "$ARCHIVE" 2>/dev/null || echo 0)" \
      BA_TO="$NOTIFY_TO" BA_CS_DIR="$CS_DIR" BA_CS_KEEP="$CS_KEEP" \
      BA_CS_OK="$CS_OK" BA_CS_VER="$CS_VERIFIED" BA_AN_OK="$AN_OK" BA_AN_VER="$AN_VERIFIED" \
      BA_CS_PRUNED="$CS_PRUNED" BA_CS_REMAIN="$CS_REMAIN" \
      BA_AN_DIR="$AN_DIR" BA_AN_KEEP="$AN_KEEP" \
      BA_AN_PRUNED="$AN_PRUNED" BA_AN_REMAIN="$AN_REMAIN" BA_COUNTS="$DB_COUNTS" \
      BA_MIRROR_OK="$MIRROR_OK" BA_MIRROR_FILES="$MIRROR_FILES" BA_MIRROR_DIR="$MIRROR_DIR" \
      BA_FAILURES="$(printf '%s\n' "${FAILURES[@]:-}")" \
      BA_WARNINGS="$(printf '%s\n' "${WARNINGS[@]:-}")" \
      python3 - > "$PAYLOAD" <<'PYPAY'
import json, os
def lines(v):
    return [x.strip() for x in os.environ.get(v, "").splitlines() if x.strip()]
counts = {}
for row in lines("BA_COUNTS"):
    if "|" in row:
        t, n = row.split("|", 1)
        counts[t.strip()] = n.strip()
print(json.dumps({
    "to":      os.environ.get("BA_TO", "blloyd@3cdc.org"),
    "stamp":   os.environ.get("BA_STAMP", ""),
    "status":  os.environ.get("BA_STATUS", ""),
    "archive": os.environ.get("BA_ARCHIVE", ""),
    "bytes":   int(os.environ.get("BA_BYTES", "0") or 0),
    "coldstorage": {
        "ok":       os.environ.get("BA_CS_OK")  == "1",
        "verified": os.environ.get("BA_CS_VER") == "1",
        "path":     os.environ.get("BA_CS_DIR", ""),
        "keep":     int(os.environ.get("BA_CS_KEEP", "8") or 8),
        "archives": lines("BA_CS_REMAIN"),
        "pruned":   lines("BA_CS_PRUNED"),
        "count":    len(lines("BA_CS_REMAIN")),
    },
    "audionas": {
        "ok":       os.environ.get("BA_AN_OK")  == "1",
        "verified": os.environ.get("BA_AN_VER") == "1",
        "path":     os.environ.get("BA_AN_DIR", ""),
        "keep":     int(os.environ.get("BA_AN_KEEP", "8") or 8),
        "archives": lines("BA_AN_REMAIN"),
        "pruned":   lines("BA_AN_PRUNED"),
        "count":    len(lines("BA_AN_REMAIN")),
    },
    "mirror": {
        "ok":    os.environ.get("BA_MIRROR_OK") == "1",
        "files": int(os.environ.get("BA_MIRROR_FILES", "0") or 0),
        "path":  os.environ.get("BA_MIRROR_DIR", ""),
    },
    "db_rows":  counts,
    "failures": lines("BA_FAILURES"),
    "warnings": lines("BA_WARNINGS"),
}))
PYPAY
      # n8n registers webhook routes noticeably AFTER /healthz answers 200, so a
      # first-attempt 404 means "not mounted yet", not "workflow is broken".
      SENT=0
      for i in 1 2 3 4 5 6; do
        CODE="$(curl -sS -o /tmp/.ba_notify_resp -w '%{http_code}' -X POST \
          -H "x-advance-token: $TOKEN" -H 'Content-Type: application/json' \
          --data @"$PAYLOAD" "$NOTIFY_URL" 2>>"$LOG")"
        case "$CODE" in
          2*) SENT=1; break ;;
          404|000) sleep 5 ;;
          *) break ;;
        esac
      done
      if [ "$SENT" = 1 ]; then
        log "notify: report sent to $NOTIFY_TO (HTTP $CODE)"
      else
        warn "notify: report webhook returned HTTP ${CODE:-none} — no email sent"
        head -c 300 /tmp/.ba_notify_resp 2>/dev/null >> "$LOG"
      fi
      rm -f "$PAYLOAD" /tmp/.ba_notify_resp
    else
      warn "notify: could not resolve ADVANCE_INTERNAL_TOKEN — no email sent"
    fi
  fi
fi

# Leave a machine-readable status file the morning digest can read.
{
  echo "{"
  echo "  \"stamp\": \"$STAMP\","
  echo "  \"status\": \"$STATUS\","
  echo "  \"archive\": \"$NAME.tar.gz\","
  echo "  \"bytes\": $(stat -c%s "$ARCHIVE" 2>/dev/null || echo 0),"
  echo "  \"nas_copies\": $PUSHED,"
  echo "  \"coldstorage_verified\": $([ "$CS_VERIFIED" = 1 ] && echo true || echo false),"
  echo "  \"coldstorage_held\": $(printf '%s\n' "$CS_REMAIN" | grep -c .),"
  echo "  \"coldstorage_keep\": $CS_KEEP,"
  echo "  \"audionas_verified\": $([ "$AN_VERIFIED" = 1 ] && echo true || echo false),"
  echo "  \"audionas_held\": $(printf '%s\n' "$AN_REMAIN" | grep -c .),"
  echo "  \"audionas_keep\": $AN_KEEP,"
  echo "  \"mirror_ok\": $([ "$MIRROR_OK" = 1 ] && echo true || echo false),"
  echo "  \"mirror_files\": $MIRROR_FILES,"
  echo "  \"failures\": ${#FAILURES[@]},"
  echo "  \"warnings\": ${#WARNINGS[@]}"
  echo "}"
} > "$WORKROOT/last_backup.json"

log "═══ done ═══"
[ ${#FAILURES[@]} -gt 0 ] && exit 1
exit 0
