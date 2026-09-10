#!/usr/bin/env bash
# =============================================================================
# Band Advance — restore
# =============================================================================
# Ships INSIDE every archive. Run it from the extracted archive directory on the
# machine you want the pipeline to live on (bare Debian 12 is fine):
#
#     tar xzf band-advance-YYYYMMDD-HHMMSS.tar.gz
#     sudo ./band-advance-YYYYMMDD-HHMMSS/restore.sh
#
# That single command rebuilds: OS packages, the app tree, the python venv, the
# Postgres container, the database, every uploaded band file, the disk-first
# submission records, the systemd service, and the Dropbox Advancing tree.
#
# It is deliberately NON-DESTRUCTIVE:
#   • an existing populated 'advance' database is RENAMED aside, never dropped
#   • an existing populated ~/Dropbox/Nyquist is left alone; the tree lands in
#     ./restored-Nyquist-<stamp> instead (use --force-dropbox to overlay)
#   • n8n is not touched unless you pass --with-n8n
#
# Options:
#   --db-only          just the database
#   --data-only        database + uploads + submission JSON (no app/venv/systemd)
#   --with-n8n         also import n8n workflows + credentials  (disruptive)
#   --force-dropbox    overlay the Dropbox tree onto a live ~/Dropbox/Nyquist
#   --dropbox-dest D   put the Dropbox tree at D instead
#   --app-dir D        install to D instead of /opt/band-advance
#   --no-verify        skip the checksum check (don't)
#   --yes              never prompt
# =============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
APP_DIR="/opt/band-advance"
DROPBOX_DEST=""
SVC_USER="${SUDO_USER:-brian}"
MODE="full"; WITH_N8N=0; FORCE_DROPBOX=0; VERIFY=1; ASSUME_YES=0
FAILURES=(); NOTES=()

while [ $# -gt 0 ]; do
  case "$1" in
    --db-only)       MODE="db" ;;
    --data-only)     MODE="data" ;;
    --with-n8n)      WITH_N8N=1 ;;
    --force-dropbox) FORCE_DROPBOX=1 ;;
    --dropbox-dest)  DROPBOX_DEST="$2"; shift ;;
    --app-dir)       APP_DIR="$2"; shift ;;
    --no-verify)     VERIFY=0 ;;
    --yes|-y)        ASSUME_YES=1 ;;
    -h|--help)       sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
  shift
done

log()  { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*"; }
step() { echo; echo "── $* ──────────────────────────────────────"; }
ok()   { echo "   ok: $*"; }
note() { echo "   note: $*"; NOTES+=("$*"); }
bad()  { echo "   FAIL: $*"; FAILURES+=("$*"); }
need_root() { [ "$(id -u)" -eq 0 ] || { echo "run with sudo"; exit 1; }; }

echo "═══ Band Advance restore ═══"
echo "archive:  $HERE"
echo "mode:     $MODE   app-dir: $APP_DIR   service user: $SVC_USER"
[ -f "$HERE/MANIFEST.txt" ] && grep -E '^(archive|created|status):' "$HERE/MANIFEST.txt" | sed 's/^/          /'
if grep -q '^status:      PARTIAL' "$HERE/MANIFEST.txt" 2>/dev/null; then
  echo
  echo "  !! This archive is marked PARTIAL — something failed when it was made."
  echo "     Read MANIFEST.txt before relying on it. Restoring anyway is still"
  echo "     usually right; just know what is missing."
fi
if [ "$ASSUME_YES" = 0 ] && [ -t 0 ]; then
  read -r -p "proceed? [y/N] " a; [ "${a,,}" = "y" ] || exit 0
fi
need_root

# ---------------------------------------------------------------- verify ----
if [ "$VERIFY" = 1 ] && [ -f "$HERE/CHECKSUMS.sha256" ]; then
  step "verifying archive integrity"
  if ( cd "$HERE" && sha256sum -c CHECKSUMS.sha256 --quiet ); then ok "all files match their checksums"
  else bad "CHECKSUM MISMATCH — this archive is damaged. Try an older one, or the copy on the other NAS."
       [ "$ASSUME_YES" = 0 ] && { read -r -p "continue anyway? [y/N] " a; [ "${a,,}" = "y" ] || exit 1; }
  fi
fi

# ------------------------------------------------------------ packages ------
if [ "$MODE" = "full" ]; then
  step "1/8  OS packages"
  MISSING=()
  for p in docker.io docker-compose-plugin python3-venv python3-pip rsync gnupg; do
    dpkg -s "$p" >/dev/null 2>&1 || MISSING+=("$p")
  done
  if [ ${#MISSING[@]} -gt 0 ]; then
    log "installing: ${MISSING[*]}"
    apt-get update -qq >/dev/null 2>&1
    apt-get install -y -qq "${MISSING[@]}" >/dev/null 2>&1 \
      && ok "installed ${MISSING[*]}" || bad "apt install failed: ${MISSING[*]}"
  else ok "all required packages already present"; fi
  systemctl enable --now docker >/dev/null 2>&1
fi

# ------------------------------------------------------------- secrets ------
step "2/8  secrets"
SECRETS_DIR="$(mktemp -d)"; chmod 700 "$SECRETS_DIR"
trap 'rm -rf "$SECRETS_DIR"' EXIT
GOT_SECRETS=0
if [ -f "$HERE/secrets.tar.gz.gpg" ]; then
  for PASS in "${BACKUP_PASS:-}" "lockdown"; do
    [ -z "$PASS" ] && continue
    if printf '%s' "$PASS" | gpg --batch --quiet --pinentry-mode loopback --passphrase-fd 0 \
         -d "$HERE/secrets.tar.gz.gpg" 2>/dev/null | tar -C "$SECRETS_DIR" -xzf - 2>/dev/null; then
      GOT_SECRETS=1; ok "secrets decrypted"; break
    fi
  done
  if [ "$GOT_SECRETS" = 0 ] && [ -t 0 ]; then
    read -r -s -p "   passphrase for secrets.tar.gz.gpg (blank = generate fresh): " PASS; echo
    if [ -n "$PASS" ] && printf '%s' "$PASS" | gpg --batch --quiet --pinentry-mode loopback \
         --passphrase-fd 0 -d "$HERE/secrets.tar.gz.gpg" 2>/dev/null | tar -C "$SECRETS_DIR" -xzf - 2>/dev/null; then
      GOT_SECRETS=1; ok "secrets decrypted"
    fi
  fi
fi
if [ "$GOT_SECRETS" = 0 ]; then
  note "no secrets recovered — generating FRESH credentials. Data restores fine."
  note "consequence: previously-issued /f/<token> prefill links stop working, and"
  note "the n8n Graph credential must be re-entered. Nothing is lost."
  mkdir -p "$SECRETS_DIR/secrets-plain"
  NEWPW="$(head -c 24 /dev/urandom | base64 | tr -d '/+=' | head -c 32)"
  NEWSEC="$(head -c 32 /dev/urandom | xxd -p -c 64)"
  cat > "$SECRETS_DIR/secrets-plain/advance.env" <<EOF
ADVANCE_DB_URL=postgresql://advance:$NEWPW@127.0.0.1:5433/advance
ADVANCE_SECRET=$NEWSEC
ADVANCE_GATE_PASS=lockdown
ADVANCE_PUBLIC_URL=https://advance.tinydoorstudios.com
EOF
  echo "ADVANCE_DB_PASSWORD=$NEWPW" > "$SECRETS_DIR/secrets-plain/advance-db.env"
fi
SP="$SECRETS_DIR/secrets-plain"

# ------------------------------------------------------------ app tree ------
if [ "$MODE" = "full" ]; then
  step "3/8  application tree"
  if [ -d "$APP_DIR" ] && [ -n "$(ls -A "$APP_DIR" 2>/dev/null)" ]; then
    mv "$APP_DIR" "$APP_DIR.pre-restore.$STAMP"
    note "existing $APP_DIR moved aside to $APP_DIR.pre-restore.$STAMP"
  fi
  mkdir -p "$APP_DIR"
  rsync -a "$HERE/app/" "$APP_DIR/" && ok "app tree installed" || bad "app tree copy failed"
  install -m 600 "$SP/advance.env" "$APP_DIR/advance.env" 2>/dev/null && ok "advance.env" || bad "advance.env missing"
  mkdir -p "$APP_DIR/db"
  install -m 600 "$SP/advance-db.env" "$APP_DIR/db/.env" 2>/dev/null && ok "db/.env" || bad "db/.env missing"
  cp "$HERE/docker/advance-db.compose.yml" "$APP_DIR/db/docker-compose.yml" 2>/dev/null

  step "4/8  python venv"
  python3 -m venv "$APP_DIR/venv" >/dev/null 2>&1
  if [ -f "$HERE/app/requirements.lock.txt" ]; then
    "$APP_DIR/venv/bin/pip" install -q --upgrade pip >/dev/null 2>&1
    "$APP_DIR/venv/bin/pip" install -q -r "$HERE/app/requirements.lock.txt" >/dev/null 2>&1 \
      && ok "deps installed from the pinned lock file" \
      || { "$APP_DIR/venv/bin/pip" install -q -r "$HERE/app/requirements.txt" >/dev/null 2>&1 \
             && note "pinned install failed; installed from requirements.txt instead" \
             || bad "pip install failed"; }
  else
    "$APP_DIR/venv/bin/pip" install -q -r "$HERE/app/requirements.txt" >/dev/null 2>&1 \
      && ok "deps installed" || bad "pip install failed"
  fi
  id "$SVC_USER" >/dev/null 2>&1 && chown -R "$SVC_USER:$SVC_USER" "$APP_DIR"
else
  step "3-4/8  app tree + venv — skipped ($MODE)"
fi

# ------------------------------------------------------------- database -----
step "5/8  database"
DBPW="$(grep '^ADVANCE_DB_PASSWORD=' "$SP/advance-db.env" 2>/dev/null | cut -d= -f2-)"
COMPOSE="$APP_DIR/db/docker-compose.yml"
[ -f "$COMPOSE" ] || COMPOSE="$HERE/docker/advance-db.compose.yml"
if ! docker ps --format '{{.Names}}' | grep -qx advance-db; then
  ( cd "$(dirname "$COMPOSE")" && ADVANCE_DB_PASSWORD="$DBPW" docker compose -f "$COMPOSE" up -d ) >/dev/null 2>&1 \
    && ok "advance-db container started" || bad "could not start advance-db"
fi
for i in $(seq 1 60); do
  docker exec advance-db pg_isready -U advance -d advance >/dev/null 2>&1 && break
  sleep 2
done
if docker exec advance-db pg_isready -U advance -d advance >/dev/null 2>&1; then
  ok "postgres is accepting connections"
  ROWS="$(docker exec advance-db psql -U advance -d advance -tAc \
          "select coalesce(sum(n_live_tup),0) from pg_stat_user_tables;" 2>/dev/null | tr -d ' ')"
  if [ "${ROWS:-0}" -gt 0 ]; then
    docker exec advance-db psql -U advance -d postgres -c \
      "alter database advance rename to advance_pre_restore_$STAMP;" >/dev/null 2>&1 \
      && note "existing database held $ROWS rows — renamed to advance_pre_restore_$STAMP (nothing dropped)" \
      || bad "could not set the existing database aside; refusing to overwrite it"
    docker exec advance-db psql -U advance -d postgres -c "create database advance owner advance;" >/dev/null 2>&1
  fi
  if [ -f "$HERE/db/advance.dump" ]; then
    docker exec -i advance-db pg_restore -U advance -d advance --clean --if-exists --no-owner \
      < "$HERE/db/advance.dump" >/dev/null 2>&1
    ok "restored from advance.dump"
  elif [ -f "$HERE/db/advance.sql.gz" ]; then
    gunzip -c "$HERE/db/advance.sql.gz" | docker exec -i advance-db psql -U advance -d advance >/dev/null 2>&1
    ok "restored from advance.sql.gz"
  else
    bad "no database dump in this archive"
  fi
else
  bad "postgres never came up — database NOT restored"
fi

# --------------------------------------------------------------- data -------
step "6/8  uploads + submission records"
mkdir -p "$APP_DIR/data/uploads"
if [ -d "$HERE/appdata/uploads" ]; then
  rsync -a "$HERE/appdata/uploads/" "$APP_DIR/data/uploads/" \
    && ok "$(find "$APP_DIR/data/uploads" -type f | wc -l) uploaded files restored" || bad "uploads restore failed"
fi
if [ -d "$HERE/appdata/json" ] && compgen -G "$HERE/appdata/json/*.json" >/dev/null; then
  cp -pn "$HERE/appdata/json"/*.json "$APP_DIR/data/" 2>/dev/null
  ok "$(ls -1 "$HERE/appdata/json" | wc -l) submission JSON records restored"
fi
id "$SVC_USER" >/dev/null 2>&1 && chown -R "$SVC_USER:$SVC_USER" "$APP_DIR/data"

# ------------------------------------------------------------- dropbox ------
step "7/8  Dropbox Advancing tree"
if [ -d "$HERE/dropbox/Nyquist" ]; then
  HOME_DIR="$(getent passwd "$SVC_USER" | cut -d: -f6)"; HOME_DIR="${HOME_DIR:-/home/$SVC_USER}"
  DEST="${DROPBOX_DEST:-$HOME_DIR/Dropbox/Nyquist}"
  LIVE=0
  [ -d "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ] && LIVE=1
  if [ "$LIVE" = 1 ] && [ "$FORCE_DROPBOX" = 0 ]; then
    DEST="$PWD/restored-Nyquist-$STAMP"
    note "$HOME_DIR/Dropbox/Nyquist already has content — NOT overwritten."
    note "the archived tree was restored to $DEST instead (--force-dropbox to overlay)"
  fi
  mkdir -p "$DEST"
  rsync -a "$HERE/dropbox/Nyquist/" "$DEST/" && ok "Advancing tree restored to $DEST" || bad "Dropbox tree restore failed"
  id "$SVC_USER" >/dev/null 2>&1 && chown -R "$SVC_USER:$SVC_USER" "$DEST" 2>/dev/null
  for f in "advance-list.xlsx" "Show Status Log.xlsx" "Blank Advances" "Series Email Templates"; do
    [ -e "$DEST/$f" ] && ok "present: $f" || bad "MISSING after restore: $f"
  done
else
  bad "no Dropbox tree in this archive"
fi

# --------------------------------------------------------------- service ----
if [ "$MODE" = "full" ]; then
  step "8/8  service + timer"
  for unit in band-advance.service band-advance-backup.service band-advance-backup.timer; do
    [ -f "$HERE/systemd/$unit" ] && install -m 644 "$HERE/systemd/$unit" "/etc/systemd/system/$unit" && ok "installed $unit"
  done
  [ -f /etc/systemd/system/band-advance.service ] || cat > /etc/systemd/system/band-advance.service <<EOF
[Unit]
Description=3CDC Band Advance Form
After=network.target docker.service

[Service]
User=$SVC_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/advance.env
ExecStart=$APP_DIR/venv/bin/gunicorn -w 2 -b 0.0.0.0:8097 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now band-advance >/dev/null 2>&1
  [ -f /etc/systemd/system/band-advance-backup.timer ] && systemctl enable --now band-advance-backup.timer >/dev/null 2>&1
  sleep 3
  [ "$(systemctl is-active band-advance)" = "active" ] && ok "band-advance service is active" || bad "band-advance service did not start (journalctl -u band-advance)"
else
  step "8/8  service — skipped ($MODE)"
fi

# ------------------------------------------------------------------ n8n -----
if [ "$WITH_N8N" = 1 ]; then
  step "extra  n8n import"
  N8N_DIR=/opt/n8n
  if [ -f "$SP/n8n.env" ] && [ ! -f "$N8N_DIR/.env" ]; then
    mkdir -p "$N8N_DIR"; install -m 600 "$SP/n8n.env" "$N8N_DIR/.env"; ok "n8n .env restored (carries N8N_ENCRYPTION_KEY)"
  fi
  [ -f "$HERE/docker/n8n.compose.yml" ] && [ ! -f "$N8N_DIR/docker-compose.yml" ] \
    && cp "$HERE/docker/n8n.compose.yml" "$N8N_DIR/docker-compose.yml"
  if docker ps --format '{{.Names}}' | grep -qx n8n-n8n-1; then
    NC="docker compose -f $N8N_DIR/docker-compose.yml exec -T n8n n8n"
    docker compose -f "$N8N_DIR/docker-compose.yml" cp "$HERE/n8n/workflows/." n8n:/tmp/wf_in >/dev/null 2>&1
    $NC import:workflow --separate --input=/tmp/wf_in >/dev/null 2>&1 && ok "workflows imported" || bad "workflow import failed"
    if [ -f "$SP/n8n_credentials.decrypted.json" ]; then
      docker compose -f "$N8N_DIR/docker-compose.yml" cp "$SP/n8n_credentials.decrypted.json" n8n:/tmp/creds.json >/dev/null 2>&1
      $NC import:credentials --input=/tmp/creds.json >/dev/null 2>&1 && ok "credentials imported" || bad "credential import failed"
    fi
    # import:workflow does NOT carry active state — replay it.
    if [ -f "$HERE/n8n/workflow_active_state.txt" ]; then
      while IFS='|' read -r wid active wname; do
        [ "$active" = "t" ] && $NC publish:workflow --id="$wid" >/dev/null 2>&1 && ok "re-activated: $wname"
      done < "$HERE/n8n/workflow_active_state.txt"
    fi
    note "n8n webhook routes register several seconds AFTER /healthz answers 200 — don't trust a first-attempt 404"
  else
    bad "n8n container not running — start /opt/n8n first, then rerun with --with-n8n"
  fi
fi

# ---------------------------------------------------------------- verify ----
step "verification"
if [ -f "$HERE/db/counts.txt" ] && docker exec advance-db pg_isready -U advance -d advance >/dev/null 2>&1; then
  printf '   %-18s %10s %10s\n' "table" "expected" "restored"
  MISMATCH=0
  while IFS='|' read -r tbl expected; do
    [ -z "$tbl" ] && continue
    actual="$(docker exec advance-db psql -U advance -d advance -tAc "select count(*) from \"$tbl\";" 2>/dev/null | tr -d ' ')"
    printf '   %-18s %10s %10s' "$tbl" "$expected" "${actual:-ERR}"
    if [ "${actual:-x}" = "$expected" ]; then echo "  ✓"; else echo "  ← differs"; MISMATCH=1; fi
  done < "$HERE/db/counts.txt"
  [ "$MISMATCH" = 0 ] && ok "every table matches the backup's row counts" \
    || note "row counts differ from backup time — expected if the source kept running after the dump; investigate if the gap is large"
fi
if curl -fs --max-time 5 http://localhost:8097/healthz >/dev/null 2>&1; then
  ok "app answering on http://localhost:8097/healthz"
else
  [ "$MODE" = "full" ] && bad "app is not answering on :8097"
fi

echo
echo "═══════════════════════════════════════════════════════════"
if [ ${#FAILURES[@]} -eq 0 ]; then echo "  RESTORE COMPLETE"; else echo "  RESTORE FINISHED WITH ${#FAILURES[@]} FAILURE(S)"; printf '   ! %s\n' "${FAILURES[@]}"; fi
[ ${#NOTES[@]} -gt 0 ] && { echo; echo "  notes:"; printf '   - %s\n' "${NOTES[@]}"; }
cat <<'EOF'

  Still to do by hand (they live outside this machine):
   1. Cloudflare ingress: advance.tinydoorstudios.com -> http://localhost:8097
      The n8n-tunnel is REMOTE-managed — edit ingress via the Cloudflare API,
      never via a local config.yml. Token + IDs: TDS_Credentials_CheatSheet.md
   2. Dropbox: if this is a fresh host, link the headless client and set
      selective sync to Nyquist/ ONLY before letting it write.
   3. If secrets were regenerated, re-send any outstanding /f/<token> prefill
      links and re-enter the Graph credential in n8n.

  Verify by hand:  https://advance.tinydoorstudios.com/search   (passcode: lockdown)
EOF
[ ${#FAILURES[@]} -gt 0 ] && exit 1
exit 0
