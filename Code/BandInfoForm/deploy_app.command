#!/bin/bash
# Redeploy the Band Advance system (Flask app + offline tools) to the n8n VM.
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to deploy_log.txt.
#
# This ships CODE only. It does NOT touch the database container, the env files,
# or the systemd unit contents — those are one-time setup (see db/DEPLOY notes
# in README). Rollback = git: redeploy an earlier commit (no app.py.bak copies
# any more).
#
# Sequence (audit 2026-09-16 ops #4): stage everything into a scratch dir
# on the VM first, run migrations against it, THEN stop the service and
# rsync the staged tree into place — so a bad extraction or a failed
# migration is caught before the live tree (or the running service) is
# ever touched, instead of tar writing straight over live files.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY $VM"
APP_DIR=/opt/band-advance
# Review 2026-09-14 (H6): this tree is shared by several Claude sessions and
# a `git checkout` by any of them changes what this script would ship.
# Refuse unless the deployed branch is checked out here.
WANT="${ADVANCE_DEPLOY_BRANCH:-main}"
CUR="$(git -C "$HERE" branch --show-current 2>/dev/null)"
if [ "$CUR" != "$WANT" ]; then
  echo "REFUSING to deploy: $HERE is on branch '$CUR', expected '$WANT' (set ADVANCE_DEPLOY_BRANCH to override)."
  exit 1
fi
NEW_SHA="$(git -C "$HERE" rev-parse HEAD)"

# Every relative path (under $APP_DIR on the VM) this deploy ships, shared
# between the drift check below and the tar staging step — one list, so
# they can never quietly drift apart from each other.
APP_FILES=(app.py advance_db.py forms_config.py i18n.py es_translate.py mailer.py status_labels.py)
TOOLS_FILES=(
  draft_emails.py backfill.py event.py daysheet.py sheet.py import_sheet.py fieldspec.py
  build_template.py status_sheet.py package_run.py venue_email.py staffing.py
  extract_advance_recap.py seed_bookings.py append_bookings.py merge_status.py run_now.py
  run_again.py status_log.py daily_digest.py crew_report.py regen_show.py finalize_thankyou.py
  docmerge.py holds.py migrate_filed_docs.py import_riffpay.py dayahead.py booking_update.py
  doc_review.py missing_reports.py
)
TOOLS_DIRS=(email_templates lists doc_templates staging)
SHIPPED_FILES=("${APP_FILES[@]}" requirements.txt db/schema.sql)
for f in "${TOOLS_FILES[@]}"; do SHIPPED_FILES+=("tools/$f"); done
# tools/ ships a curated subset (above), not the whole directory, so the
# drift check walks it explicitly too — a blanket `git ls-tree tools`
# would flag files that were never part of any deploy in the first place.
SHIPPED_DIRS=(templates ops db/migrations backup)
for d in "${TOOLS_DIRS[@]}"; do SHIPPED_DIRS+=("tools/$d"); done

{
  echo "=== Band Advance deploy — $(date) — branch $CUR @ $(git -C "$HERE" rev-parse --short HEAD) ==="
  STAMP=$(date +%Y%m%d-%H%M%S)

  # audit 2026-09-16 ops #4: refuse when the VM has drifted from what git
  # thinks is deployed — exactly how the 09-14/09-15 incident happened
  # (missing_reports.py's route was added straight on the VM, never
  # committed, then silently overwritten by the next deploy). Skipped on
  # the very first deploy after this check ships (no marker yet to compare
  # against) or if the marked commit isn't in this tree's history.
  echo "--- pre-flight: check the VM matches the last deployed commit ---"
  PREV_SHA="$($SSH "cat $APP_DIR/.deployed_commit 2>/dev/null")"
  if [ -n "$PREV_SHA" ] && git -C "$HERE" cat-file -e "$PREV_SHA" 2>/dev/null; then
    ALL_PATHS=("${SHIPPED_FILES[@]}")
    for d in "${SHIPPED_DIRS[@]}"; do
      while IFS= read -r p; do ALL_PATHS+=("$p"); done < <(git -C "$HERE" ls-tree -r --name-only "$PREV_SHA" -- "$d" 2>/dev/null)
    done
    LOCAL_MANIFEST="$(mktemp)"; REMOTE_MANIFEST="$(mktemp)"
    for p in "${ALL_PATHS[@]}"; do
      sha="$(git -C "$HERE" show "$PREV_SHA:$p" 2>/dev/null | shasum -a 256 | awk '{print $1}')"
      [ -n "$sha" ] && echo "$sha  $p" >> "$LOCAL_MANIFEST"
    done
    printf '%s\n' "${ALL_PATHS[@]}" | $SSH "cd $APP_DIR && xargs -I{} sh -c 'sha256sum \"{}\" 2>/dev/null'" > "$REMOTE_MANIFEST"
    DRIFT="$(comm -23 <(sort "$LOCAL_MANIFEST") <(sort "$REMOTE_MANIFEST") | awk '{print $2}')"
    rm -f "$LOCAL_MANIFEST" "$REMOTE_MANIFEST"
    if [ -n "$DRIFT" ]; then
      echo "REFUSING to deploy: the VM has changed since commit ${PREV_SHA:0:8} in files this deploy would overwrite:"
      echo "$DRIFT" | sed 's/^/  /'
      echo "Someone (or something) edited these directly on the VM. Commit the VM's"
      echo "version into git first (pull it down, review, commit), or if the VM copy"
      echo "is genuinely disposable, redeploy with ADVANCE_DEPLOY_FORCE=1 to override."
      [ "${ADVANCE_DEPLOY_FORCE:-0}" = "1" ] || exit 1
      echo "ADVANCE_DEPLOY_FORCE=1 set — overwriting the drifted files anyway."
    else
      echo "ok: VM matches ${PREV_SHA:0:8} for every file this deploy touches"
    fi
  else
    echo "no usable .deployed_commit marker yet — skipping the drift check this run"
  fi

  echo "--- stage payloads ---"
  tar -C "$HERE/app"   -czf /tmp/adv_app.tgz   "${APP_FILES[@]}" templates || exit 1
  tar -C "$HERE/tools" -czf /tmp/adv_tools.tgz "${TOOLS_FILES[@]}" "${TOOLS_DIRS[@]}" || exit 1
  # db/schema.sql, backup/ and requirements.txt now ship too (audit ops #4)
  # — they used to just sit in git, never actually reaching the VM through
  # this script, so a fix to any of them (like this batch's own schema.sql
  # and backup/ changes) silently never took effect.
  tar -C "$HERE" -czf /tmp/adv_ops.tgz ops db/migrations db/schema.sql backup requirements.txt || exit 1

  echo "--- copy to VM ---"
  scp -J tds -i "$KEY" /tmp/adv_app.tgz   "$VM:/tmp/adv_app.tgz"   || { echo "SCP app FAILED"; exit 1; }
  scp -J tds -i "$KEY" /tmp/adv_tools.tgz "$VM:/tmp/adv_tools.tgz" || { echo "SCP tools FAILED"; exit 1; }
  scp -J tds -i "$KEY" /tmp/adv_ops.tgz   "$VM:/tmp/adv_ops.tgz"   || { echo "SCP ops FAILED"; exit 1; }
  rm -f /tmp/adv_app.tgz /tmp/adv_tools.tgz /tmp/adv_ops.tgz

  echo "--- stage into $APP_DIR.new, migrate, then swap ---"
  $SSH "
    set -e
    # /opt itself isn't writable by the deploy user, only inside
    # \$APP_DIR — sudo the create, then hand it back so the rest of this
    # (plain tar/rsync) doesn't need sudo sprinkled everywhere.
    sudo rm -rf $APP_DIR.new
    sudo mkdir -p $APP_DIR.new/tools
    sudo chown -R \"\$(id -un)\":\"\$(id -gn)\" $APP_DIR.new
    tar -C $APP_DIR.new       -xzf /tmp/adv_app.tgz
    tar -C $APP_DIR.new/tools -xzf /tmp/adv_tools.tgz
    tar -C $APP_DIR.new       -xzf /tmp/adv_ops.tgz
    rm -f /tmp/adv_app.tgz /tmp/adv_tools.tgz /tmp/adv_ops.tgz

    # schema migrations are idempotent (IF NOT EXISTS / ON CONFLICT) and
    # apply to the live DB regardless of which tree reads the .sql from —
    # run them here, BEFORE anything live is touched, so a failed
    # migration stops the whole deploy with nothing swapped in yet.
    for m in $APP_DIR.new/db/migrations/*.sql; do
      echo \"migration: \$(basename \$m)\"
      sudo docker exec -i advance-db psql -U advance -d advance -v ON_ERROR_STOP=1 -q < \"\$m\" || { echo 'MIGRATION FAILED — nothing live was touched'; exit 1; }
    done

    # never restart mid-run: a restart kills an in-flight pipeline run,
    # doc filing or thank-you send (audit cleanup). Wait up to 10 minutes.
    for i in \$(seq 1 120); do
      if pgrep -f '[r]un_now.py|[r]un_again.py|[p]ackage_run.py|[r]egen_show.py|[f]inalize_thankyou.py|[d]raft_emails.py' >/dev/null; then
        [ \$i = 1 ] && echo 'waiting for an in-flight pipeline run to finish...'
        sleep 5
      else
        break
      fi
    done

    sudo systemctl stop band-advance
    # overlays the staged tree onto the live one — additive, same as the
    # old tar extraction (nothing outside what's shipped, e.g. venv/,
    # data/, advance.env, db/.env, is ever touched or removed).
    rsync -a $APP_DIR.new/ $APP_DIR/
    rm -rf $APP_DIR.new
    echo '$NEW_SHA' | sudo tee $APP_DIR/.deployed_commit >/dev/null

    # systemd units + timers (reference copies live in ops/)
    sudo cp $APP_DIR/ops/*.service $APP_DIR/ops/*.timer /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo cp $APP_DIR/ops/band-advance-logrotate /etc/logrotate.d/band-advance
    sudo systemctl enable --now advance-nightly-run.timer advance-db-nightly.timer advance-lifecycle-watchdog.timer dropbox-cache-guard.timer dropbox.service >/dev/null 2>&1
    sudo systemctl start band-advance
    sleep 3
    if [ \"\$(systemctl is-active band-advance)\" != active ]; then
      echo 'band-advance did not come back up after the deploy (journalctl -u band-advance)'
      exit 1
    fi
    echo \"service: \$(systemctl is-active band-advance)\"
    curl -sf http://localhost:8097/healthz || { echo 'healthz did not respond OK'; exit 1; }
    echo
  " || { echo "DEPLOY FAILED — see above"; exit 1; }
  echo "=== done $(date) — https://advance.tinydoorstudios.com ==="
} 2>&1 | tee "$LOG"
# audit 2026-09-16 ops #4: propagate a failure as a real exit code — the
# whole run above is piped through tee, so $? here would otherwise always
# be tee's, never reflecting a migration/drift/restart failure.
! grep -qE 'REFUSING to deploy|DEPLOY FAILED' "$LOG"
