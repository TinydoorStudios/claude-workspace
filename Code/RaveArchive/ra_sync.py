#!/usr/bin/env python3
"""
ra_sync.py - incremental, resumable, window-aware mirror of an Internet Archive item.

Standard library only. Nothing to pip install, nothing for a TrueNAS upgrade to wipe.

Typical use:
    # 2 GB stratified test pull
    ./ra_sync.py --dest /mnt/POOL/RaveArchive --test-bytes 2G

    # nightly window: start from cron at 22:00, stop cleanly at 07:00
    ./ra_sync.py --dest /mnt/POOL/RaveArchive --until 07:00

    # several items in one window, worked in the order given
    ./ra_sync.py --dest /mnt/POOL/RaveArchive --items a,b,c --until 07:00

Every run is idempotent: files already present and verified are skipped, partial
files resume via HTTP Range, and anything that fails is retried on the next run.
"""

import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

METADATA_URL = "https://archive.org/metadata/{item}"
DOWNLOAD_URL = "https://archive.org/download/{item}/{path}"
USER_AGENT = "ra_sync/1.0 (personal archival mirror; contact tinydoorstudios@gmail.com)"

CHUNK = 1 << 20          # 1 MiB read size
MAX_ATTEMPTS = 3
SKIP_NAMES = {".DS_Store"}


class DeadlineReached(Exception):
    """Raised when the nightly window closes mid-transfer."""


# ---------------------------------------------------------------- utilities

def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0


def parse_size(s):
    s = str(s).strip().upper()
    mult = 1
    for suffix, m in (("TB", 1 << 40), ("GB", 1 << 30), ("MB", 1 << 20),
                      ("KB", 1 << 10), ("T", 1 << 40), ("G", 1 << 30),
                      ("M", 1 << 20), ("K", 1 << 10), ("B", 1)):
        if s.endswith(suffix):
            mult = m
            s = s[: -len(suffix)]
            break
    return int(float(s) * mult)


def next_occurrence(hhmm):
    """Return the next datetime matching HH:MM local time."""
    hour, minute = (int(x) for x in hhmm.split(":"))
    now = dt.datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += dt.timedelta(days=1)
    return target


class Log:
    def __init__(self, path):
        self.lock = threading.Lock()
        self.fh = open(path, "a", encoding="utf-8", buffering=1) if path else None

    def __call__(self, msg):
        line = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
        with self.lock:
            print(line, flush=True)
            if self.fh:
                self.fh.write(line + "\n")


class RateLimiter:
    """Global token bucket, bytes/sec. Disabled when limit is None."""

    def __init__(self, bps):
        self.bps = bps
        self.lock = threading.Lock()
        self.allowance = float(bps) if bps else 0.0
        self.last = time.monotonic()

    def consume(self, n):
        if not self.bps:
            return
        while True:
            with self.lock:
                now = time.monotonic()
                self.allowance = min(self.bps,
                                     self.allowance + (now - self.last) * self.bps)
                self.last = now
                if self.allowance >= n:
                    self.allowance -= n
                    return
                deficit = (n - self.allowance) / self.bps
            time.sleep(min(deficit, 0.5))


# ---------------------------------------------------------------- metadata

def fetch_metadata(item, cache_path, max_age=3600, log=print):
    if cache_path and os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < max_age:
            log(f"metadata: using cache ({age/60:.0f} min old)")
            with open(cache_path, encoding="utf-8") as fh:
                return json.load(fh)

    url = METADATA_URL.format(item=item)
    log(f"metadata: fetching {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    if cache_path:
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        os.replace(tmp, cache_path)
    return data


def select_originals(meta):
    """Keep source==original, drop IA-generated derivatives and OS cruft."""
    out = []
    for f in meta.get("files", []):
        if f.get("source") != "original":
            continue
        name = f.get("name", "")
        if os.path.basename(name) in SKIP_NAMES:
            continue
        if not f.get("size"):
            continue
        out.append({
            "name": name,
            "size": int(f["size"]),
            "md5": f.get("md5"),
        })
    out.sort(key=lambda x: x["name"])
    return out


def stratified_sample(files, budget):
    """
    Deterministic test selection under a byte budget, chosen to exercise the
    awkward parts: every file extension present, at least one file living in a
    subdirectory, at least one name with a leading space or an ampersand, a mix
    of small and large, then sequential fill.
    """
    picked, seen, total = [], set(), 0

    def take(f):
        nonlocal total
        if f["name"] in seen or total + f["size"] > budget:
            return False
        seen.add(f["name"])
        picked.append(f)
        total += f["size"]
        return True

    def ext(f):
        return f["name"].rsplit(".", 1)[-1].lower()

    # one of each extension, smallest first so the budget stretches
    by_ext = {}
    for f in files:
        by_ext.setdefault(ext(f), []).append(f)
    for e in sorted(by_ext):
        for f in sorted(by_ext[e], key=lambda x: x["size"]):
            if take(f):
                break

    # something inside a subdirectory
    for f in sorted((f for f in files if "/" in f["name"]), key=lambda x: x["size"]):
        if take(f):
            break

    # awkward filenames
    for f in sorted((f for f in files
                     if f["name"][:1] in (" ", "&", "_") or "&" in f["name"]),
                    key=lambda x: x["size"]):
        if take(f):
            break

    # one genuinely large file, to prove sustained transfer + resume
    for f in sorted(files, key=lambda x: -x["size"]):
        if f["size"] <= budget - total and take(f):
            break

    # fill the rest sequentially for a realistic run
    for f in files:
        if total >= budget:
            break
        take(f)

    picked.sort(key=lambda x: x["name"])
    return picked, total


# ---------------------------------------------------------------- transfer

def md5_of_partial(path, log):
    h = hashlib.md5()
    size = 0
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            h.update(b)
            size += len(b)
    return h, size


def download_one(item, f, dest, deadline, limiter, log, stats):
    name = f["name"]
    final = os.path.join(dest, name)
    part = final + ".part"
    os.makedirs(os.path.dirname(final) or dest, exist_ok=True)

    url = DOWNLOAD_URL.format(
        item=item, path=urllib.parse.quote(name, safe="/"))

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if deadline and time.time() >= deadline:
            raise DeadlineReached()

        offset = 0
        digest = hashlib.md5()
        if os.path.exists(part):
            existing = os.path.getsize(part)
            if 0 < existing < f["size"]:
                digest, offset = md5_of_partial(part, log)
                log(f"resume  {name}  from {human(offset)}")
            elif existing >= f["size"]:
                os.remove(part)

        headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
        if offset:
            headers["Range"] = f"bytes={offset}-"

        started = time.monotonic()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                if offset and resp.status != 206:
                    # server ignored the range; start clean
                    offset = 0
                    digest = hashlib.md5()
                mode = "ab" if offset else "wb"
                with open(part, mode) as out:
                    while True:
                        if deadline and time.time() >= deadline:
                            out.flush()
                            os.fsync(out.fileno())
                            raise DeadlineReached()
                        buf = resp.read(CHUNK)
                        if not buf:
                            break
                        limiter.consume(len(buf))
                        out.write(buf)
                        digest.update(buf)
                        offset += len(buf)
                        with stats["lock"]:
                            stats["bytes"] += len(buf)

            got = os.path.getsize(part)
            if got != f["size"]:
                raise IOError(f"size mismatch: got {got}, expected {f['size']}")
            if f["md5"] and digest.hexdigest() != f["md5"]:
                os.remove(part)
                raise IOError("md5 mismatch")

            os.replace(part, final)
            secs = max(time.monotonic() - started, 0.001)
            log(f"ok      {name}  {human(f['size'])}  "
                f"{human(f['size'] / secs)}/s")
            return True

        except DeadlineReached:
            raise
        except Exception as exc:  # noqa: BLE001 - retry anything transient
            if attempt == MAX_ATTEMPTS:
                log(f"FAIL    {name}  {exc}")
                return False
            backoff = min(60, 2 ** attempt) + random.uniform(0, 2)
            log(f"retry   {name}  attempt {attempt}/{MAX_ATTEMPTS}: {exc} "
                f"(sleep {backoff:.0f}s)")
            time.sleep(backoff)
    return False


# ---------------------------------------------------------------- reporting

def write_manifest(path, files, dest):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "size", "md5", "present", "on_disk_size"])
        for f in files:
            p = os.path.join(dest, f["name"])
            present = os.path.exists(p)
            w.writerow([f["name"], f["size"], f["md5"] or "",
                        int(present), os.path.getsize(p) if present else 0])


def write_provenance(path, item, meta, files, total_bytes):
    md = meta.get("metadata", {})
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"""# Provenance - {item}

Personal preservation copy of a public Internet Archive item.

| | |
|---|---|
| Source | https://archive.org/details/{item} |
| Uploader | {md.get('uploader', 'unknown')} |
| Added to IA | {md.get('addeddate', 'unknown')} |
| Mediatype | {md.get('mediatype', 'unknown')} |
| Original files mirrored | {len(files):,} |
| Bytes | {total_bytes:,} ({human(total_bytes)}) |
| First captured | {dt.date.today().isoformat()} |
| Tool | Code/RaveArchive/ra_sync.py |

Archive.org-generated derivatives (.afpk peak data, spectrogram PNGs, thumbnail
JPGs) are deliberately excluded - they are regenerable and are not source material.

Re-running ra_sync.py against the same destination picks up any sets added to the
item since this capture. Nothing already on disk is re-downloaded.
""")


# ---------------------------------------------------------------- main

def sync_item(item, args, root_dest, workdir, log, deadline, limiter):
    """Mirror one item. Returns (ok, failed, bytes, stopped_early, remaining)."""
    root = os.path.join(root_dest, item)
    os.makedirs(root, exist_ok=True)

    meta = fetch_metadata(item, os.path.join(workdir, f"{item}.metadata.json"),
                          log=log)
    files = select_originals(meta)
    grand_total = sum(f["size"] for f in files)
    log(f"[{item}] {len(files):,} original files, {human(grand_total)}")

    if args.test_bytes:
        files, budget_total = stratified_sample(files, parse_size(args.test_bytes))
        log(f"[{item}] TEST MODE: {len(files)} files, {human(budget_total)}")

    todo, have_bytes = [], 0
    for f in files:
        p = os.path.join(root, f["name"])
        if os.path.exists(p) and os.path.getsize(p) == f["size"]:
            have_bytes += f["size"]
            continue
        todo.append(f)
    todo_bytes = sum(f["size"] for f in todo)
    log(f"[{item}] on disk: {human(have_bytes)} | to fetch: "
        f"{len(todo):,} files, {human(todo_bytes)}")

    if args.dry_run:
        for f in todo[:20]:
            log(f"[{item}] would fetch  {human(f['size']):>10}  {f['name']}")
        if len(todo) > 20:
            log(f"[{item}] ... and {len(todo) - 20:,} more")
        return 0, 0, 0, False, todo_bytes

    if not todo:
        log(f"[{item}] current - nothing to fetch")
        write_manifest(os.path.join(workdir, f"{item}.MANIFEST.csv"), files, root)
        write_provenance(os.path.join(root, "PROVENANCE.md"), item, meta,
                         files, grand_total)
        return 0, 0, 0, False, 0

    stats = {"bytes": 0, "lock": threading.Lock()}
    ok = failed = 0
    stopped_early = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_one, item, f, root, deadline,
                               limiter, log, stats): f for f in todo}
        try:
            for fut in concurrent.futures.as_completed(futures):
                try:
                    if fut.result():
                        ok += 1
                    else:
                        failed += 1
                except DeadlineReached:
                    stopped_early = True
                    break
        finally:
            if stopped_early:
                for fut in futures:
                    fut.cancel()

    write_manifest(os.path.join(workdir, f"{item}.MANIFEST.csv"),
                   select_originals(meta), root)
    write_provenance(os.path.join(root, "PROVENANCE.md"), item, meta,
                     select_originals(meta), grand_total)

    remaining = max(grand_total - have_bytes - stats["bytes"], 0)
    log(f"[{item}] {'stopped at window close' if stopped_early else 'done'}: "
        f"{ok:,} ok, {failed:,} failed, {human(stats['bytes'])} fetched, "
        f"{human(remaining)} remaining")
    return ok, failed, stats["bytes"], stopped_early, remaining


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--item", default=None,
                    help="single item identifier (alias for --items)")
    ap.add_argument("--items", default=None,
                    help="comma-separated item identifiers, worked in order")
    ap.add_argument("--dest", required=True,
                    help="root directory; item files land in <dest>/<item>/")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--until", metavar="HH:MM",
                    help="stop cleanly at this local time (next occurrence)")
    ap.add_argument("--max-hours", type=float,
                    help="stop cleanly after this many hours")
    ap.add_argument("--test-bytes", metavar="SIZE",
                    help="stratified test pull under this budget, e.g. 2G")
    ap.add_argument("--bwlimit", metavar="RATE",
                    help="global cap, e.g. 20M (bytes/sec)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root_dest = os.path.abspath(args.dest)
    workdir = os.path.join(root_dest, "_ra_sync")
    os.makedirs(workdir, exist_ok=True)

    items = []
    for src in (args.items, args.item):
        if src:
            items.extend(x.strip() for x in src.split(",") if x.strip())

    # No items on the command line: take the queue from items.txt so the
    # schedule never has to be edited to add or drop an item.
    queue_file = os.path.join(workdir, "items.txt")
    if not items and os.path.exists(queue_file):
        with open(queue_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    items.append(line)
    if not items:
        items = ["RaveDownloads"]
    seen = set()
    items = [i for i in items if not (i in seen or seen.add(i))]

    log = Log(os.path.join(workdir, "sync.log"))

    deadline = None
    if args.until:
        deadline = next_occurrence(args.until).timestamp()
    if args.max_hours:
        cap = time.time() + args.max_hours * 3600
        deadline = min(deadline, cap) if deadline else cap
    if deadline:
        log(f"window closes at "
            f"{dt.datetime.fromtimestamp(deadline).strftime('%Y-%m-%d %H:%M')}")
    log(f"queue: {len(items)} item(s) - {', '.join(items)}")

    limiter = RateLimiter(parse_size(args.bwlimit) if args.bwlimit else None)
    started = time.monotonic()
    t_ok = t_failed = t_bytes = t_remaining = 0
    stopped_early = False

    for item in items:
        if deadline and time.time() >= deadline:
            log(f"window closed before reaching {item} - deferred to next run")
            stopped_early = True
            break
        try:
            ok, failed, got, stopped, remaining = sync_item(
                item, args, root_dest, workdir, log, deadline, limiter)
        except Exception as exc:  # noqa: BLE001 - one bad item must not kill the queue
            log(f"[{item}] ERROR - skipping this item: {exc}")
            t_failed += 1
            continue
        t_ok += ok
        t_failed += failed
        t_bytes += got
        t_remaining += remaining
        if stopped:
            stopped_early = True
            break

    elapsed = max(time.monotonic() - started, 0.001)
    log(f"{'WINDOW CLOSED' if stopped_early else 'RUN COMPLETE'}: "
        f"{t_ok:,} ok, {t_failed:,} failed, {human(t_bytes)} in "
        f"{elapsed/60:.1f} min ({human(t_bytes/elapsed)}/s)")
    if t_remaining > 0:
        log(f"remaining across queued items: ~{human(t_remaining)}")
    return 1 if t_failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ninterrupted - partial files kept, re-run to resume")
        sys.exit(130)
