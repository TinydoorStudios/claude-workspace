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
import fieldspec as fs
NYQUIST_DEFAULT = fs.nyquist_root()
LOCK = HERE / ".run_now.lock"
LOCK_WAIT_SECS = 900
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

    # 2. rebuild events/drafts/status and file docs in place (scoped if asked)
    out = HERE / "_package"
    cmd = ["package_run.py", sheet, "--out", "_package"]
    for sc in scope or []:
        cmd += ["--scope", sc]
    built = run(*cmd)
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

    # 5. Show Status Log (best-effort — never blocks the pipeline)
    try:
        run("status_log.py")
    except subprocess.CalledProcessError as e:
        print(f"  ! status_log.py failed (non-fatal): {(e.stderr or '')[-500:]}", file=sys.stderr)


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
        summary = {"seeded": 0, "events": 0, "emails": 0, "followups": 0, "plots": 0, "failed": 0}
        for _ in range(MAX_PASSES):
            one_pass(sheet, nyquist, args.scope, summary)
            if unseeded_count() == 0:
                break
        print(json.dumps(summary))
    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": e.__class__.__name__,
                           "cmd": " ".join(str(a) for a in e.cmd),
                           "stderr": (e.stderr or "")[-2000:]}))
        sys.exit(1)
    finally:
        try:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
