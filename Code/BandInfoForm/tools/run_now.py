#!/usr/bin/env python3
"""VM-native run: seed staff bookings into the live advance-list.xlsx, build the
package, file advance docs in place (never overwriting — docmerge.py), and fold
status back into the sheet.

    python3 run_now.py [--sheet PATH] [--scope "Venue|YYYY-MM-DD"]

--scope limits doc FILING to that show (a booking's own run, 2026-09-13 audit
#1); the sheet import, drafts and status still cover everything. No scope =
file every current show ("Run again").

Queues instead of quitting (audit #18): a second run waits for the one in
progress (kernel file lock, released automatically if a run dies), and a run
re-checks for bookings logged while it was working before it finishes, so a
booking entered back-to-back is never left unseeded.

Prints one JSON line to stdout on success: seeded/events/emails/followups/plots
counts. Non-zero exit + {"error": "..."} on failure.
"""
import argparse
import fcntl
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
sys.path.insert(0, str(HERE))
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import fieldspec as fs
import advance_db as db
NYQUIST_DEFAULT = fs.nyquist_root()
LOCK = HERE / ".run_now.lock"
# audit 2026-09-16 #21: below the caller's 1200s subprocess timeout (app.py)
# with real headroom left for the actual work after the lock is acquired —
# at 900 a long wait plus a normal run could still eat past 1200 and get
# SIGKILLed mid-save.
LOCK_WAIT_SECS = 600
MAX_PASSES = 3


def run(*args, input_text=None):
    return subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, check=True,
                           capture_output=True, text=True, input=input_text)


def acquire_lock():
    fh = open(LOCK, "a+")
    deadline = time.time() + LOCK_WAIT_SECS
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fh.seek(0)
            fh.truncate()
            fh.write(str(time.time()))
            fh.flush()
            return fh
        except BlockingIOError:
            if time.time() > deadline:
                raise SystemExit(f"waited {LOCK_WAIT_SECS}s for the run in progress — giving up")
            time.sleep(2)


def unseeded_count():
    out = run("seed_bookings.py", "--json")
    return len(json.loads(out.stdout or "[]"))


def one_pass(sheet, nyquist, scope, summary):
    # 0. delete the sheet rows of shows purged / merged away in the app (root
    #    cause A, audit 2026-09-16). First, before anything reads the sheet:
    #    a row left behind is imported again and the deleted show comes back
    #    with blank stamps — and gets welcomed again.
    rm = run("seed_bookings.py", "--removals-json")
    removals = json.loads(rm.stdout or "[]")
    if removals:
        rm_file = HERE / ".removals_tmp.json"
        rm_file.write_text(rm.stdout)
        try:
            removed = run("append_bookings.py", "--list", sheet, "--remove", rm_file)
            for line in (removed.stderr or "").splitlines():
                print(line, file=sys.stderr)
            ids = removed.stdout.strip()
            if ids:
                done = run("seed_bookings.py", "--removed", ids)
                for line in (done.stderr or "").splitlines():
                    print(line, file=sys.stderr)
                summary["removed"] += len(ids.split(","))
        finally:
            rm_file.unlink(missing_ok=True)

    # 1. pull any new staff bookings into the sheet
    bk = run("seed_bookings.py", "--json")
    bookings = json.loads(bk.stdout or "[]")
    if bookings:
        bk_file = HERE / ".bookings_tmp.json"
        bk_file.write_text(bk.stdout)
        try:
            appended = run("append_bookings.py", "--list", sheet, "--data", bk_file)
            ids = appended.stdout.strip()
            if ids:
                run("seed_bookings.py", "--seed", ids)
                summary["seeded"] += len(ids.split(","))
        finally:
            bk_file.unlink(missing_ok=True)

    # 1b. push bookings edited since they were seeded back over their sheet rows
    #     (2026-09-15). Has to run BEFORE the rebuild below, which reads the
    #     sheet: without it an edit made in the app loses to its own stale row
    #     and the bill silently reverts — including, now, its running order.
    ed = run("seed_bookings.py", "--edited")
    edited = json.loads(ed.stdout or "[]")
    if edited:
        ed_file = HERE / ".edited_tmp.json"
        ed_file.write_text(ed.stdout)
        try:
            synced = run("append_bookings.py", "--list", sheet, "--edited", ed_file)
            ids = synced.stdout.strip()
            if ids:
                run("seed_bookings.py", "--synced", ids)
                summary["edits_synced"] += len(ids.split(","))
        finally:
            ed_file.unlink(missing_ok=True)

    # 1c. reconcile: a booking whose sheet row vanished out from under it (a
    # hand edit, a bad merge) is invisible to seed_bookings.py --json —
    # seeded_at is already set — so it never re-seeds on its own and holds.py
    # orphans it permanently, Restore included (audit 2026-09-16 #19).
    # append_bookings.py --data already skips any booking whose ident IS
    # still in the sheet, so passing every future booking here is safe —
    # only ones actually missing get re-appended.
    with db.get_conn() as conn, conn.cursor() as cur:
        future = db.future_bookings(cur)
    if future:
        mi_file = HERE / ".reconcile_tmp.json"
        mi_file.write_text(json.dumps(future, default=str))
        try:
            reconciled = run("append_bookings.py", "--list", sheet, "--data", mi_file)
            ids = reconciled.stdout.strip()
            if ids:
                run("seed_bookings.py", "--seed", ids)
        finally:
            mi_file.unlink(missing_ok=True)

    # 2. rebuild events/drafts/status and file docs in place (scoped if asked)
    out = HERE / "_package"
    cmd = ["package_run.py", sheet, "--out", "_package"]
    for sc in scope or []:
        cmd += ["--scope", sc]
    built = run(*cmd)
    # per-doc actions and warnings into the run log (stderr, so the summary
    # JSON stays the last stdout line run_again.py parses)
    for line in (built.stdout or "").splitlines() + (built.stderr or "").splitlines():
        if line.lstrip().startswith(("doc ", "!")):
            print(line, file=sys.stderr)
    m = re.search(r"(\d+) event\(s\) filed .+? (\d+) email\(s\) .+? (\d+) follow-up\(s\) .+? "
                  r"(\d+) stage plot\(s\) .+? (\d+) day-sheet failure", built.stdout)
    if m:
        summary["events"], summary["emails"], summary["followups"], summary["plots"], summary["failed"] = \
            (int(x) for x in m.groups())

    # 3. overlay the internal email drafts onto the Nyquist cockpit (no
    #    --delete — an archive, not a mirror). Filed docs are NOT overlaid any
    #    more; package_run writes them in place and never overwrites.
    if (out / "drafts").exists():
        subprocess.run(["rsync", "-a", f"{out}/drafts/", f"{nyquist}/"], check=True)

    # 4. fold status + band answers back into the same sheet, in place
    status_path = out / "status.json"
    if status_path.exists():
        run("merge_status.py", "--list", sheet, "--data", status_path)

    # 4b. F2 (audit 2026-09-16): Dropbox never syncs Word/Excel's "~$" lock file,
    #     so a sheet open on a Mac is invisible here — the "(conflicted copy)"
    #     it leaves behind isn't. Tell Brian once per copy.
    report_conflicted_copies([sheet, nyquist / "Show Status Log.xlsx"])

    # 5. Show Status Log (best-effort — never blocks the pipeline)
    try:
        run("status_log.py")
    except subprocess.CalledProcessError as e:
        print(f"  ! status_log.py failed (non-fatal): {(e.stderr or '')[-500:]}", file=sys.stderr)


def report_conflicted_copies(paths):
    """One digest line per Dropbox conflicted copy of a shared workbook — its
    edits exist only in the copy until someone merges them by hand."""
    try:
        import docmerge
        found = [(p, cc) for p in paths for cc in docmerge.conflicted_copies(p)]
        if not found:
            return
        with db.get_conn() as conn, conn.cursor() as cur:
            for p, cc in found:
                # event_date is NULL for a workbook, and the UNIQUE index treats
                # NULLs as distinct — dedupe by hand
                cur.execute("SELECT 1 FROM doc_notices WHERE kind='conflict' AND cell_key=%s",
                            (f"conflict:{cc.name}",))
                if cur.fetchone():
                    continue
                nid = db.insert_doc_notice(cur, "", None, p.name.lower(), "conflict",
                                           "Conflicted copy", cc.name, p.name,
                                           detail=p.name, cell_key=f"conflict:{cc.name}")
                if nid:
                    db.resolve_doc_notice(cur, nid, "auto")
                    db.mark_doc_notices_notified(cur, [nid])   # rides the digest item below
                    import mailer
                    db.queue_digest_item(
                        cur, "doc", f"Conflicted copy of {p.name}",
                        f"<p>Dropbox made <b>{mailer.esc(cc.name)}</b> next to "
                        f"<b>{mailer.esc(p.name)}</b> — somebody saved it while the pipeline "
                        "was writing it. Anything typed into the copy isn't in the real file; "
                        "merge it by hand, then delete the copy.</p>")
                    print(f"  ! conflicted copy: {cc.name}", file=sys.stderr)
            conn.commit()
    except Exception as e:  # noqa: BLE001 — a report, never a reason to fail the run
        print(f"  ! conflicted-copy check failed (non-fatal): {e!r}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", type=Path, default=NYQUIST_DEFAULT / "advance-list.xlsx")
    ap.add_argument("--scope", action="append")
    args = ap.parse_args()
    sheet = args.sheet
    nyquist = sheet.parent

    if not sheet.exists():
        print(json.dumps({"error": f"sheet not found at {sheet}"}))
        sys.exit(1)

    lock = acquire_lock()
    try:
        summary = {"seeded": 0, "edits_synced": 0, "removed": 0, "events": 0, "emails": 0,
                   "followups": 0, "plots": 0, "failed": 0}
        for _ in range(MAX_PASSES):
            one_pass(sheet, nyquist, args.scope, summary)
            if unseeded_count() == 0:
                break
        print(json.dumps(summary))
    except subprocess.CalledProcessError as e:
        err = {"error": e.__class__.__name__,
               "cmd": " ".join(str(a) for a in e.cmd),
               "stderr": (e.stderr or "")[-2000:]}
        print(json.dumps(err))
        # audit 2026-09-16 #18: most calls into this script are background
        # subprocesses (app.py's _run_pipeline_background) — a failure here
        # used to be silent unless someone was watching that one invocation's
        # output. Surface it both ways: queued onto the daily digest, and an
        # immediate alert, same as any other pipeline failure.
        try:
            import advance_db as db
            import mailer
            html = (f"<p><b>{mailer.esc(err['cmd'])}</b> failed:</p>"
                    f"<pre style='white-space:pre-wrap'>{mailer.esc(err['stderr'])}</pre>")
            with db.get_conn() as conn, conn.cursor() as cur:
                db.queue_digest_item(cur, "pipeline_failure", "Advance pipeline run failed", html)
                conn.commit()
            mailer.alert("Advance pipeline run failed", html)
        except Exception:  # noqa: BLE001 — the failure path must never itself crash
            pass
        sys.exit(1)
    finally:
        try:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
