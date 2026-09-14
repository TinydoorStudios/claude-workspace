#!/usr/bin/env python3
"""
gen_changelog.py — the KB CHANGELOG from git, not from hand-written entries.

Since 2026-09-14 (pipeline-fix, Brian's call) nobody appends to CHANGELOG.md by
hand. This prints (or, with --write, prepends to CHANGELOG.md under a marker)
the meaningful commits since a date, from two repos:

  - the workspace repo (~/Documents/Claude): commits touching audio/ — these
    carry the real messages (builds, skill changes, KB article edits made from
    sessions)
  - the Wiki repo (Live Sound KB/Wiki): commits that are NOT the launchd
    "KB auto-sync" heartbeat

    python3 gen_changelog.py --since 2026-09-14
    python3 gen_changelog.py --since 2026-09-14 --write
"""
import argparse, datetime, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(HERE)
WIKI = os.path.join(KB, "Wiki")
WORK = os.path.expanduser("~/Documents/Claude")
MARK = "<!-- generated-from-git-below -->"


def log(repo, since, paths=None, exclude=None):
    cmd = ["git", "-C", repo, "log", f"--since={since}", "--format=%ad · %s", "--date=short"]
    if paths:
        cmd += ["--"] + paths
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    return [l for l in out if not (exclude and exclude in l)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=(datetime.date.today() - datetime.timedelta(days=30)).isoformat())
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    lines = ["## Workspace (audio/) — from `git log`"]
    lines += [f"- {l}" for l in log(WORK, a.since, ["audio"])] or ["- (none)"]
    lines += ["", "## Wiki repo — from `git log` (auto-sync heartbeats filtered)"]
    lines += [f"- {l}" for l in log(WIKI, a.since, exclude="KB auto-sync")] or ["- (none)"]
    body = "\n".join(lines)
    if not a.write:
        print(body); return
    p = os.path.join(KB, "CHANGELOG.md")
    s = open(p, encoding="utf-8").read()
    gen = f"{MARK}\n\n# Since {a.since} — generated {datetime.date.today()}\n\n{body}\n\n"
    if MARK in s:
        head, _, tail = s.partition(MARK)
        # keep everything before the marker, replace the generated block up to the next H1 written by hand
        s = head + gen + tail.split("\n# ", 1)[1].join(["# ", ""]) if "\n# " in tail else head + gen
    else:
        s = gen + s
    open(p, "w", encoding="utf-8").write(s)
    print(f"CHANGELOG.md updated (since {a.since})")


if __name__ == "__main__":
    main()
