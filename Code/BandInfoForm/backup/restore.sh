#!/usr/bin/env bash
# =============================================================================
# Band Advance — restore
# =============================================================================
# Ships INSIDE every archive. Run it from the extracted archive directory on the
# machine you want the pipeline to live on (Debian 12 with Docker Compose v2 —
# Debian's own repo doesn't carry it, add Docker's apt repo first; this script
# installs the rest):
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
#   --with-n8n         also start n8n if needed, import workflows + credentials,
#                      then restart it  (disruptive)
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
  # 2026-09-21 sweep (OPS-17): one apt call per package (Debian 12 has no docker-compose-plugin,
  # which used to sink the whole transaction), --no-remove so apt can never uninstall a live
  # docker-ce (it Conflicts: docker.io), and docker.io only when there's no Docker at all.
  MISSING=()
  for p in python3-venv python3-pip rsync gnupg curl; do
    dpkg -s "$p" >/dev/null 2>&1 || MISSING+=("$p")
  done
  command -v docker >/dev/null 2>&1 || MISSING+=("docker.io")
  if [ ${#MISSING[@]} -gt 0 ]; then
    log "installing: ${MISSING[*]}"
    apt-get update -qq >/dev/null 2>&1
    for p in "${MISSING[@]}"; do
      apt-get install -y -qq --no-remove "$p" >/dev/null 2>&1 && ok "installed $p" || bad "apt install failed: $p"
    done
  else ok "all required packages already present"; fi
  systemctl enable --now docker >/dev/null 2>&1
  if ! docker compose version >/dev/null 2>&1; then
    for p in docker-compose-plugin docker-compose-v2 docker-compose; do
      apt-get install -y -qq --no-remove "$p" >/dev/null 2>&1 || continue
      docker compose version >/dev/null 2>&1 && { ok "compose v2 via $p"; break; }
    done
    docker compose version >/dev/null 2>&1 \
      || bad "Docker Compose v2 ('docker compose') is not available — Debian 12's own repo doesn't carry it; add Docker's apt repo (docs.docker.com/engine/install/debian), apt-get install docker-compose-plugin, then re-run"
  fi
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
  note "every n8n credential (Graph first) must be re-entered. Nothing is lost."
  mkdir -p "$SECRETS_DIR/secrets-plain"
  NEWPW="$(head -c 24 /dev/urandom | base64 | tr -d '/+=' | head -c 32)"
  # 2026-09-21 sweep (OPS-17): od, not xxd — xxd isn't on a minimal Debian 12, and an
  # empty ADVANCE_SECRET gave Flask secret_key=''. od is coreutils (Essential).
  NEWSEC="$(head -c 32 /dev/urandom | od -An -vtx1 | tr -d ' \n')"
  # audit 2026-09-16 ops #4: without a token here, EVERY /internal/*
  # endpoint (the whole n8n-driven lifecycle, both digests, the watchdog,
  # missing-reports) 403s until someone notices and sets one by hand — a
  # fresh-secrets restore used to come back up looking healthy while all
  # of that silently didn't work.
  NEWTOKEN="$(head -c 32 /dev/urandom | od -An -vtx1 | tr -d ' \n')"
  if [ ${#NEWSEC} -eq 64 ] && [ ${#NEWTOKEN} -eq 64 ] && [ ${#NEWPW} -ge 20 ]; then
    cat > "$SECRETS_DIR/secrets-plain/advance.env" <<EOF
ADVANCE_DB_URL=postgresql://advance:$NEWPW@127.0.0.1:5433/advance
ADVANCE_SECRET=$NEWSEC
ADVANCE_GATE_PASS=lockdown
ADVANCE_PUBLIC_URL=https://advance.tinydoorstudios.com
ADVANCE_INTERNAL_TOKEN=$NEWTOKEN
ADVANCE_NOTIFY_URL=http://localhost:5678/webhook/advance-notify
ADVANCE_LIFECYCLE_NOW_URL=http://localhost:5678/webhook/advance-lifecycle-now
EOF
    note "fresh ADVANCE_INTERNAL_TOKEN generated — every n8n workflow's X-Advance-Token"
    note "header needs updating to match before internal endpoints (lifecycle, digests,"
    note "the watchdog) will work again"
    note "not regenerable: DROPBOX_APP_KEY/SECRET/REFRESH_TOKEN (stage-plot links fall back to the app URL until re-added), ADVANCE_GATE_PASS_2, GROQ_API_KEY, ADVANCE_SLACK_WEBHOOK — re-add from TDS_Credentials"
    echo "ADVANCE_DB_PASSWORD=$NEWPW" > "$SECRETS_DIR/secrets-plain/advance-db.env"
  else
    bad "could not generate fresh secrets — advance.env and the DB password NOT written"
  fi
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
# audit 2026-09-16 ops #4/#5: stop the app FIRST — restoring onto a box
# where band-advance is already live (a rollback, not just a fresh
# bootstrap) used to swap the database out from under a running service,
# racing its in-flight requests against the rename/restore below.
systemctl stop band-advance >/dev/null 2>&1 && note "band-advance stopped for the restore" || true
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
SKIP_DB=0
if docker exec advance-db pg_isready -U advance -d advance >/dev/null 2>&1; then
  ok "postgres is accepting connections"
  ROWS="$(docker exec advance-db psql -U advance -d advance -tAc \
          "select coalesce(sum(n_live_tup),0) from pg_stat_user_tables;" 2>/dev/null | tr -d ' ')"
  if [ "${ROWS:-0}" -gt 0 ]; then
    if docker exec advance-db psql -U advance -d postgres -c \
      "alter database advance rename to advance_pre_restore_$STAMP;" >/dev/null 2>&1; then
      note "existing database held $ROWS rows — renamed to advance_pre_restore_$STAMP (nothing dropped)"
      docker exec advance-db psql -U advance -d postgres -c "create database advance owner advance;" >/dev/null 2>&1
    else
      # audit ops #4: this used to say "refusing to overwrite it" and then
      # restore into the SAME still-populated "advance" database anyway —
      # pg_restore --clean drops existing objects first, so the live data
      # this was supposed to protect would have been destroyed regardless.
      SKIP_DB=1
      bad "could not set the existing database aside — SKIPPING the restore to protect it (still has $ROWS rows, untouched)"
    fi
  fi
  if [ "$SKIP_DB" = 1 ]; then
    :
  elif [ -f "$HERE/db/advance.dump" ]; then
    if docker exec -i advance-db pg_restore -U advance -d advance --clean --if-exists --no-owner \
      < "$HERE/db/advance.dump" >/dev/null 2>&1; then
      ok "restored from advance.dump"
    else
      bad "pg_restore reported errors — check journalctl / the container logs before trusting this database"
    fi
  elif [ -f "$HERE/db/advance.sql.gz" ]; then
    if gunzip -c "$HERE/db/advance.sql.gz" | docker exec -i advance-db psql -U advance -d advance \
      -v ON_ERROR_STOP=1 >/dev/null 2>&1; then
      ok "restored from advance.sql.gz"
    else
      bad "psql reported errors restoring advance.sql.gz — check the database before trusting it"
    fi
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
  # audit 2026-09-16 ops #4: install every unit the archive actually
  # carries, not a hardcoded 3 — advance_backup.sh now captures whatever's
  # really on the host, so this has to match rather than silently drop the
  # nightly-run/db-nightly/lifecycle-watchdog/dropbox units on the floor.
  INSTALLED_ANY_UNIT=0
  if [ -d "$HERE/systemd" ]; then
    for unit_path in "$HERE/systemd"/*.service "$HERE/systemd"/*.timer; do
      [ -f "$unit_path" ] || continue
      unit="$(basename "$unit_path")"
      install -m 644 "$unit_path" "/etc/systemd/system/$unit" && ok "installed $unit" && INSTALLED_ANY_UNIT=1
    done
  fi
  # the scripts those units ExecStart — a unit with no script behind it
  # fails at runtime even though it installed clean.
  if [ -d "$HERE/systemd/ops" ]; then
    mkdir -p "$APP_DIR/ops"
    cp "$HERE/systemd/ops"/*.sh "$HERE/systemd/ops"/*.py "$APP_DIR/ops/" 2>/dev/null
    chmod +x "$APP_DIR/ops"/*.sh 2>/dev/null
    id "$SVC_USER" >/dev/null 2>&1 && chown -R "$SVC_USER:$SVC_USER" "$APP_DIR/ops"
    ok "ops/*.sh scripts restored"
  fi
  [ -f /etc/systemd/system/band-advance.service ] || cat > /etc/systemd/system/band-advance.service <<EOF
[Unit]
Description=3CDC Band Advance Form
After=network.target docker.service

[Service]
User=$SVC_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/advance.env
ExecStart=$APP_DIR/venv/bin/gunicorn --worker-class gthread -w 4 --threads 4 --timeout 120 --graceful-timeout 120 -b 127.0.0.1:8097 -b 172.17.0.1:8097 app:app
Restart=always
TimeoutStopSec=150

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now band-advance >/dev/null 2>&1
  # enable every timer the archive installed (not just the backup one) —
  # a fresh box otherwise silently runs with none of the nightly jobs.
  for timer_path in /etc/systemd/system/*.timer; do
    [ -f "$timer_path" ] || continue
    t="$(basename "$timer_path")"
    case "$t" in band-advance*|advance-*|dropbox*) systemctl enable --now "$t" >/dev/null 2>&1 ;; esac
  done
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
  N8N_COMPOSE="$N8N_DIR/docker-compose.yml"
  n8n_healthy() {  # up to 180s — a fresh n8n database runs its migrations first
    for _i in $(seq 1 36); do
      curl -sf -o /dev/null --max-time 5 http://localhost:5678/healthz && return 0
      sleep 5
    done
    return 1
  }
  # 2026-09-21 sweep (OPS-4): on a fresh host nothing has started n8n yet — --with-n8n
  # is already the opt-in to touching it, so bring it up here instead of failing below.
  if ! docker ps --format '{{.Names}}' | grep -qx n8n-n8n-1 \
     && [ -f "$N8N_COMPOSE" ] && [ -f "$N8N_DIR/.env" ]; then
    ( cd "$N8N_DIR" && docker compose up -d ) >/dev/null 2>&1 \
      && ok "n8n started from $N8N_DIR" || bad "could not start n8n (cd $N8N_DIR && sudo docker compose up -d)"
    n8n_healthy || note "n8n not answering /healthz yet after starting it"
  fi
  if docker ps --format '{{.Names}}' | grep -qx n8n-n8n-1; then
    NC="docker compose -f $N8N_COMPOSE exec -T n8n n8n"
    # credentials BEFORE workflows, so they exist when the workflows are re-activated
    if [ -f "$SP/n8n_credentials.decrypted.json" ]; then
      docker compose -f "$N8N_DIR/docker-compose.yml" cp "$SP/n8n_credentials.decrypted.json" n8n:/tmp/creds.json >/dev/null 2>&1
      $NC import:credentials --input=/tmp/creds.json >/dev/null 2>&1 && ok "credentials imported" || bad "credential import failed"
    elif [ -f "$HERE/n8n/credentials.enc.json" ]; then
      # 2026-09-21 sweep (OPS-4): nothing here restores n8n's own database, so the old
      # "credentials come from it" note was false — import the still-encrypted export,
      # but only into an n8n holding none, running the archive's own key.
      PGU="$(grep '^POSTGRES_USER=' "$N8N_DIR/.env" 2>/dev/null | cut -d= -f2)"
      PGD="$(grep '^POSTGRES_DB=' "$N8N_DIR/.env" 2>/dev/null | cut -d= -f2)"
      NCRED="$(docker exec n8n-postgres-1 psql -U "$PGU" -d "$PGD" -tAc 'select count(*) from credentials_entity;' 2>/dev/null | tr -d ' ')"
      ARCH_KEY="$(grep '^N8N_ENCRYPTION_KEY=' "$SP/n8n.env" 2>/dev/null | cut -d= -f2- | tr -d '"\047')"
      RUN_KEY="$(docker compose -f "$N8N_COMPOSE" exec -T n8n printenv N8N_ENCRYPTION_KEY 2>/dev/null </dev/null | tr -d '\r')"
      # a key n8n generated for itself (not passed in the env) lives in its config file
      [ -z "$RUN_KEY" ] && RUN_KEY="$(docker compose -f "$N8N_COMPOSE" exec -T n8n cat /home/node/.n8n/config 2>/dev/null </dev/null \
        | sed -n 's/.*"encryptionKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
      if ! [[ "$NCRED" =~ ^[0-9]+$ ]]; then
        bad "could not count n8n credentials — credentials.enc.json not imported"
      elif [ "$NCRED" -gt 0 ]; then
        note "n8n already holds $NCRED credential(s) — left alone; to overwrite from the archive, import n8n/credentials.enc.json by hand"
      elif [ -z "$ARCH_KEY" ]; then
        bad "credentials.enc.json NOT imported — the archive's N8N_ENCRYPTION_KEY wasn't recovered, so re-enter every n8n credential (Graph first) by hand"
      elif [ "$RUN_KEY" != "$ARCH_KEY" ]; then
        bad "running n8n's N8N_ENCRYPTION_KEY differs from the archive's — credentials NOT imported (they'd land undecryptable). Put the archived key in $N8N_DIR/.env, docker compose up -d --force-recreate n8n, re-run"
      else
        docker compose -f "$N8N_COMPOSE" cp "$HERE/n8n/credentials.enc.json" n8n:/tmp/creds.json >/dev/null 2>&1
        $NC import:credentials --input=/tmp/creds.json >/dev/null 2>&1 </dev/null \
          && ok "credentials imported (encrypted, same key)" || bad "credential import failed"
        docker compose -f "$N8N_COMPOSE" exec -T n8n rm -f /tmp/creds.json >/dev/null 2>&1 </dev/null
      fi
    else
      bad "no n8n credentials in this archive — re-enter them by hand (Graph first)"
    fi
    docker compose -f "$N8N_DIR/docker-compose.yml" cp "$HERE/n8n/workflows/." n8n:/tmp/wf_in >/dev/null 2>&1
    $NC import:workflow --separate --input=/tmp/wf_in >/dev/null 2>&1 && ok "workflows imported" || bad "workflow import failed"
    # import:workflow does NOT carry active state — replay it. </dev/null: compose exec
    # forwards stdin, which would swallow the rest of this file after the first workflow.
    if [ -f "$HERE/n8n/workflow_active_state.txt" ]; then
      while IFS='|' read -r wid active wname; do
        if [ "$active" = "t" ]; then
          $NC publish:workflow --id="$wid" >/dev/null 2>&1 </dev/null \
            && ok "re-activated: $wname" || bad "could not re-activate: $wname"
        fi
      done < "$HERE/n8n/workflow_active_state.txt"
    fi
    # 2026-09-21 sweep (OPS-4): publish:workflow only takes effect on restart — schedules
    # and webhook routes (the 9am lifecycle, internal-send-outlook) stayed dead without it.
    ( cd "$N8N_DIR" && docker compose restart n8n ) >/dev/null 2>&1 \
      && ok "n8n restarted (schedules + webhook routes only mount on restart)" \
      || bad "n8n restart failed — cd $N8N_DIR && sudo docker compose restart n8n"
    if n8n_healthy; then
      sleep 15   # webhook routes register several seconds AFTER /healthz answers 200
      ok "n8n answering /healthz after the restart"
    else
      bad "n8n not answering /healthz 3 min after restart"
    fi
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
   2. Dropbox: on a fresh host, link the headless client, then as brian (not
      root) run `bash /opt/band-advance/ops/dropbox_exclude.sh` and copy it to
      ~/dropbox_exclude.sh (the live copy). It keeps Nyquist/ plus the seven
      '3CDC <Venue>' folders the advance docs file into and excludes everything
      else, including the bulky legacy archive subfolders. Re-run it until
      `~/dropbox.py exclude list` covers every other top-level item, before the
      06:30 nightly run files anything.
   3. If secrets were regenerated, re-send any outstanding /f/<token> prefill
      links and re-enter every n8n credential (Graph first).

  Verify by hand:  https://advance.tinydoorstudios.com/search   (passcode: lockdown)
EOF
[ ${#FAILURES[@]} -gt 0 ] && exit 1
exit 0
