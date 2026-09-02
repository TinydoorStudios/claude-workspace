#!/usr/bin/env python3
"""VM-native run: seed staff bookings into the live advance-list.xlsx, build the
package, file it into the venue tree, and fold status back into the sheet.

This is the server-side twin of the old Mac generate.command, now that the sheet
lives on this box too (Dropbox-synced ~/Dropbox/Nyquist/, no SSH/scp/rsync hop
needed). Meant to be called from the /booking thank-you page's "Run now" button,
or by hand:

    python3 run_now.py [--sheet PATH]

Prints one JSON line to stdout on success: seeded/events/emails/followups/plots
counts. Non-zero exit + {"error": "..."} on failure. Refuses to overlap a run
already in progress (lock file, stale after 10 min).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
NYQUIST_DEFAULT = Path.home() / "Dropbox" / "Nyquist"
LOCK = HERE / ".run_now.lock"
LOCK_STALE_SECS = 600


def run(*args, input_text=None):
    return subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, check=True,
                           capture_output=True, text=True, input=input_text)


def acquire_lock():
    if LOCK.exists():
        age = time.time() - LOCK.stat().st_mtime
        if age < LOCK_STALE_SECS:
            raise SystemExit(f"a run is already in progress (started {int(age)}s ago)")
    LOCK.write_text(str(time.time()))


def release_lock():
    LOCK.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", type=Path, default=NYQUIST_DEFAULT / "advance-list.xlsx")
    args = ap.parse_args()
    sheet = args.sheet
    nyquist = sheet.parent

    if not sheet.exists():
        print(json.dumps({"error": f"sheet not found at {sheet}"}))
        sys.exit(1)

    acquire_lock()
    try:
        summary = {"seeded": 0, "events": 0, "emails": 0, "followups": 0, "plots": 0}

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
                    summary["seeded"] = len(ids.split(","))
            finally:
                bk_file.unlink(missing_ok=True)

        # 2. rebuild the package (events, day-sheets, email drafts, status.json)
        out = HERE / "_package"
        built = run("package_run.py", sheet, "--out", "_package")
        m = re.search(r"(\d+) event\(s\) filed .+? (\d+) email\(s\) .+? (\d+) follow-up\(s\) .+? (\d+) stage plot",
                      built.stdout)
        if m:
            summary["events"], summary["emails"], summary["followups"], summary["plots"] = \
                (int(x) for x in m.groups())

        # 3. overlay the built tree into the live Dropbox-synced folder (no delete —
        #    it's an archive, not a mirror)
        subprocess.run(["rsync", "-a", "--exclude=status.json", f"{out}/", f"{nyquist}/"],
                        check=True)

        # 4. fold status + band answers back into the same sheet, in place
        status_path = out / "status.json"
        if status_path.exists():
            run("merge_status.py", "--list", sheet, "--data", status_path)

        print(json.dumps(summary))
    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": e.__class__.__name__,
                           "cmd": " ".join(str(a) for a in e.cmd),
                           "stderr": (e.stderr or "")[-2000:]}))
        sys.exit(1)
    finally:
        release_lock()


if __name__ == "__main__":
    main()
