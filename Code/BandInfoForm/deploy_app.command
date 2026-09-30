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
#
# app/*.py and app/templates/ are FLATTENED on deploy (tar -C "$HERE/app" ..
# extracts straight into $APP_DIR, no "app/" component survives) — every
# other shipped path is identical on both sides. The drift check needs
# both spellings: REMOTE_TO_LOCAL_PREFIX carries the one local prefix
# ("app/") that doesn't match its remote path, keyed by the first path
# component, so it stays a single source of truth instead of a second
# hardcoded file list that could drift from this one.
APP_FILES=(app.py advance_db.py forms_config.py i18n.py es_translate.py mailer.py status_labels.py brand.py memo_fields.py)
TOOLS_FILES=(
  draft_emails.py backfill.py event.py daysheet.py sheet.py import_sheet.py fieldspec.py
  build_template.py status_sheet.py package_run.py venue_email.py staffing.py
  extract_advance_recap.py seed_bookings.py append_bookings.py merge_status.py run_now.py
  run_again.py status_log.py daily_digest.py crew_report.py regen_show.py finalize_thankyou.py
  docmerge.py holds.py migrate_filed_docs.py import_riffpay.py dayahead.py booking_update.py
  doc_review.py missing_reports.py backfill_doc_columns.py backfill_stageplot_links.py
  brand_docx.py build_memo_template.py memo_doc.py
)
TOOLS_DIRS=(email_templates lists doc_templates staging)
SHIPPED_FILES=("${APP_FILES[@]}" requirements.txt db/schema.sql)
for f in "${TOOLS_FILES[@]}"; do SHIPPED_FILES+=("tools/$f"); done
# tools/ ships a curated subset (above), not the whole directory, so the
# drift check walks it explicitly too — a blanket `git ls-tree tools`
# would flag files that were never part of any deploy in the first place.
SHIPPED_DIRS=(templates ops db/migrations backup)
for d in "${TOOLS_DIRS[@]}"; do SHIPPED_DIRS+=("tools/$d"); done
# remote path -> local git-path prefix, for the two flattened cases above.
_local_git_path() {
  case "$1" in
    templates/*) echo "app/$1" ;;
    *)
      for f in "${APP_FILES[@]}"; do [ "$1" = "$f" ] && { echo "app/$1"; return; }; done
      echo "$1"
      ;;
  esac
}

# 2026-09-21 sweep: ship committed code only. The tar steps read the WORKING
# TREE but .deployed_commit records HEAD, so an uncommitted edit (ours or a
# peer session's; the tree is shared) would reach production unrecorded and
# the next deploy's drift check would refuse with a false "edited on the VM".
DIRTY_PATHS=(app/templates app/brand ops db/migrations db/schema.sql backup requirements.txt)
for f in "${APP_FILES[@]}"; do DIRTY_PATHS+=("app/$f"); done
for f in "${TOOLS_FILES[@]}"; do DIRTY_PATHS+=("tools/$f"); done
for d in "${TOOLS_DIRS[@]}"; do DIRTY_PATHS+=("tools/$d"); done
DIRTY="$(git --no-optional-locks -C "$HERE" status --porcelain --untracked-files=all -- "${DIRTY_PATHS[@]}")"
if [ -n "$DIRTY" ]; then
  if [ "${ADVANCE_DEPLOY_DIRTY:-0}" != "1" ]; then
    echo "REFUSING to deploy: uncommitted changes in files this deploy ships:"
    echo "$DIRTY" | sed 's/^/  /'
    echo "Commit them first (git commit -- <paths>; the tree is shared, commit only your own), or set ADVANCE_DEPLOY_DIRTY=1 to ship them anyway."
    exit 1
  fi
  echo "ADVANCE_DEPLOY_DIRTY=1: shipping uncommitted changes. .deployed_commit will still record HEAD, so the next deploy's drift check will flag these files (commit them, then redeploy with ADVANCE_DEPLOY_FORCE=1)."
fi

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
    # `git show rev:path` always wants a path relative to the REPO ROOT,
    # even with -C — unlike ls-tree's pathspec matching (below), which
    # does respect -C's cwd for both matching and --name-only output.
    # Without this prefix every git-show lookup below silently failed
    # (empty content, "path exists, but not '<name>'"), so the local
    # manifest came back empty and every single shipped file looked
    # "drifted" on the very first real run of this check.
    REPO_PREFIX="$(git -C "$HERE" rev-parse --show-prefix)"
    ALL_PATHS=("${SHIPPED_FILES[@]}")
    for d in "${SHIPPED_DIRS[@]}"; do
      # "templates" is the one flattened dir here too (local: app/templates)
      # — query ls-tree against the real local path, then strip it back to
      # the remote spelling so ALL_PATHS stays in remote-path convention
      # throughout (matching _local_git_path's own "app/" special case).
      ld="$d"; [ "$d" = "templates" ] && ld="app/templates"
      while IFS= read -r p; do
        [ "$d" = "templates" ] && p="${p#app/}"
        ALL_PATHS+=("$p")
      done < <(git -C "$HERE" ls-tree -r --name-only "$PREV_SHA" -- "$ld" 2>/dev/null)
    done
    LOCAL_MANIFEST="$(mktemp)"; REMOTE_MANIFEST="$(mktemp)"
    for p in "${ALL_PATHS[@]}"; do
      lp="$(_local_git_path "$p")"
      # a file this deploy ships for the first time didn't exist at the last
      # deployed commit, so there's nothing on the VM it could have drifted
      # from — without this skip, `git show` of a missing path hashes to the
      # empty-string sha and every new file reads as "drifted"
      git -C "$HERE" cat-file -e "$PREV_SHA:${REPO_PREFIX}$lp" 2>/dev/null || continue
      sha="$(git -C "$HERE" show "$PREV_SHA:${REPO_PREFIX}$lp" 2>/dev/null | shasum -a 256 | awk '{print $1}')"
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
  tar -C "$HERE/app"   -czf /tmp/adv_app.tgz   "${APP_FILES[@]}" templates brand || { echo "TAR app FAILED"; exit 1; }
  tar -C "$HERE/tools" -czf /tmp/adv_tools.tgz "${TOOLS_FILES[@]}" "${TOOLS_DIRS[@]}" || { echo "TAR tools FAILED"; exit 1; }
  # db/schema.sql, backup/ and requirements.txt now ship too (audit ops #4)
  # — they used to just sit in git, never actually reaching the VM through
  # this script, so a fix to any of them (like this batch's own schema.sql
  # and backup/ changes) silently never took effect.
  tar -C "$HERE" -czf /tmp/adv_ops.tgz ops db/migrations db/schema.sql backup requirements.txt || { echo "TAR ops FAILED"; exit 1; }

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
    # 2026-09-21 sweep (OPS-13): doc-review applies too — the app spawns them
    # in its own cgroup, so a stop could land between apply_plot's two renames.
    for i in \$(seq 1 120); do
      if pgrep -f '[r]un_now.py|[r]un_again.py|[p]ackage_run.py|[r]egen_show.py|[f]inalize_thankyou.py|[d]raft_emails.py|[d]oc_review.py' >/dev/null; then
        [ \$i = 1 ] && echo 'waiting for an in-flight pipeline run to finish...'
        sleep 5
      else
        break
      fi
    done

    # 2026-09-21 sweep: /internal/advance-lifecycle runs INSIDE gunicorn (pgrep
    # can't see it) and holds advisory lock LIFECYCLE_LOCK_KEY 874201913 (app.py)
    # for the whole run; a stop mid-send loses the stamp and re-emails the band.
    for i in \$(seq 1 72); do
      n=\$(sudo docker exec advance-db psql -U advance -d advance -tAc \"SELECT count(*) FROM pg_locks WHERE locktype='advisory' AND classid=0 AND objid=874201913 AND objsubid=1\" 2>/dev/null || echo 0)
      [ \"\$n\" = 0 ] && break
      [ \$i = 1 ] && echo 'waiting for an in-flight lifecycle run to finish...'
      [ \$i = 72 ] && { echo 'DEPLOY FAILED — a lifecycle run still holds its lock after 6 minutes; service not stopped, live tree untouched (migrations are idempotent) — rerun the deploy'; exit 1; }
      sleep 5
    done

    sudo systemctl stop band-advance
    # $APP_DIR/backup pre-dates this deploy script ever shipping it, and
    # got here owned by a Mac-side UID (501/staff) that doesn't map to any
    # real account on the VM — fix that once here rather than failing on
    # it every single deploy. Unconditional, no test-and-skip guard.
    sudo mkdir -p $APP_DIR/backup
    sudo chown -R \"\$(id -un)\":\"\$(id -gn)\" $APP_DIR/backup
    # overlays the staged tree onto the live one — additive, same as the
    # old tar extraction (nothing outside what's shipped, e.g. venv/,
    # data/, advance.env, db/.env, is ever touched or removed).
    rsync -a $APP_DIR.new/ $APP_DIR/
    # sudo: removing a directory ENTRY under /opt needs write on /opt
    # itself, which the deploy user doesn't have, same reason the mkdir
    # above needed it.
    sudo rm -rf $APP_DIR.new
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
rc=${PIPESTATUS[0]}
# 2026-09-21 sweep (OPS-11): exit with the deploy block's own status — every failure
# path inside it runs `exit 1`, success (incl. an ADVANCE_DEPLOY_FORCE drift override)
# falls through to 0. Grepping the log missed scp/tar failures and failed every forced deploy.
exit "$rc"
