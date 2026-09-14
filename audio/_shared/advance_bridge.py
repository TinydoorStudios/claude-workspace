#!/usr/bin/env python3
"""
advance_bridge.py — the band advance pipeline → the show pipeline (Phase D, 2026-09-14).

The advance system (Code/BandInfoForm, live on the n8n VM) already knows every
booked show, the band's stage plot / input list uploads, and their monitor,
backline and input answers. The show pipeline lives on this Mac in
audio/<Venue>/<date> <Show>/. This script is the bridge, and it runs HERE
(the VM cannot create Mac folders):

  --sync   (default)  pull upcoming shows from the advance DB over SSH, scaffold
                      any show folder that doesn't exist yet, stamp the canonical
                      show key, fetch the band's stage plot / input list into the
                      folder, and write a facts-only <Show>.brief.json skeleton
                      (show_notes carries the band's monitor/backline/input
                      answers, so the deep build can mine them). Never overwrites
                      a file that already exists.
  --push-status       write ~/Dropbox/Nyquist/show-packet-status.json — every
                      show folder's status (rev, packet_built, ses_built,
                      published, harvested) keyed by show key. Dropbox syncs it to
                      the VM, where tools/status_log.py folds it into the Show
                      Status Log's Packet / .ses / Wiki columns. Runs after --sync
                      automatically.
  --from-json FILE    use a saved query result instead of SSH (tests, offline).
  --days N            window: today .. today+N (default 60). Past shows are never scaffolded.
  --dry-run           show what would be created, touch nothing.

Canonical show key (R43): <venue-abbr>-<YYYY-MM-DD>-<slug(artist)>, e.g.
fsq-2026-08-28-buffalo-wabs-and-the-price-hill-hustle. The same slug() lives in
Code/BandInfoForm/tools/fieldspec.py (show_key()) — keep them identical.

Needs: ssh alias `tds` (Tailscale) + ~/.ssh/proxmox_tds; the VM runs the DB in the
`advance-db` docker container and stores uploads at /opt/band-advance/data/uploads.
"""
import argparse, datetime, json, os, re, subprocess, sys

AUDIO = os.environ.get("ADVANCE_BRIDGE_AUDIO") or os.path.expanduser("~/Documents/Claude/audio")
NYQUIST = os.environ.get("ADVANCE_BRIDGE_NYQUIST") or os.path.expanduser("~/Dropbox/Nyquist")
VM = "brian@192.168.200.84"
SSH = ["ssh", "-J", "tds", "-i", os.path.expanduser("~/.ssh/proxmox_tds"), "-o", "ConnectTimeout=20", VM]
SCP_PREFIX = ["scp", "-o", "ProxyJump=tds", "-i", os.path.expanduser("~/.ssh/proxmox_tds")]
UPLOADS = "/opt/band-advance/data/uploads"

# advance DB venue name -> (scaffold code, venue folder)
VENUES = {
    "Fountain Square":    ("fsq",     "Fountain Square"),
    "Memorial Hall":      ("memo",    "Memorial Hall"),
    "Washington Park":    ("wp",      "Washington Park"),
    "Elm Street Plaza":   ("esp",     "Elm Street Plaza"),
    "Court Street Plaza": ("csp",     "Court Street Plaza"),
    "Zeigler Park":       ("zp",      "Zeigler Park"),
    "Imagination Alley":  ("ia",      "Imagination Alley"),
}
CONSOLE = {"fsq": "DiGiCo Quantum 225", "memo": "DiGiCo Quantum 225", "wp": "Midas M32"}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AUDIO, "_system"))
import show_status  # noqa: E402


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def show_key(venue, date, artist):
    return f"{VENUES.get(venue, ('x', ''))[0]}-{date}-{slug(artist)}"


QUERY = r"""
SELECT json_agg(row_to_json(t)) FROM (
  SELECT s.id AS show_id, a.name AS artist, s.venue, s.show_date::text AS show_date,
         s.show_series,
         (SELECT sub.data FROM submissions sub
            WHERE sub.show_id = s.id
               OR (sub.artist_id = s.artist_id AND sub.venue = s.venue AND sub.show_date = s.show_date)
            ORDER BY sub.submitted_at DESC LIMIT 1) AS data,
         (SELECT json_agg(json_build_object('id', f.id, 'kind', f.kind, 'filename', f.filename,
                                            'stored_name', f.stored_name, 'mime', f.mime))
            FROM files f JOIN submissions sub ON sub.id = f.submission_id
            WHERE sub.show_id = s.id
               OR (sub.artist_id = s.artist_id AND sub.venue = s.venue AND sub.show_date = s.show_date)) AS files,
         (SELECT to_jsonb(b)->>'event_name' FROM bookings b
            WHERE b.venue = s.venue AND b.event_date = s.show_date
              AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) =
                  lower(btrim(regexp_replace(a.name, '\s+', ' ', 'g'))) LIMIT 1) AS event_name,
         (SELECT to_jsonb(b)->>'event_start' FROM bookings b
            WHERE b.venue = s.venue AND b.event_date = s.show_date LIMIT 1) AS event_start
  FROM shows s JOIN artists a ON a.id = s.artist_id
  WHERE s.show_date BETWEEN current_date AND current_date + %d
  ORDER BY s.show_date
) t
"""


def pull(days):
    q = (QUERY % days).replace("\n", " ")
    cmd = SSH + ["sudo -n docker exec advance-db psql -U advance -d advance -Atc " + json.dumps(q)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"advance DB query failed:\n{p.stderr[-800:]}")
    return json.loads(p.stdout.strip() or "null") or []


def notes_from(data):
    """The band's answers, as one show_notes block the deep build mines."""
    d = data or {}
    parts = []
    for label, key in (("Monitors", "monitors"), ("Own IEMs", "own_iems"), ("Split snake", "split_snake"),
                       ("Stage type", "stage_type"), ("Performers", "performers"), ("Backline", "backline"),
                       ("Input notes", "input_notes"), ("Stage plot (described)", "stage_plot_desc"),
                       ("Scenic", "scenic"), ("Own engineer", "own_engineer"), ("Questions", "questions")):
        v = str(d.get(key) or "").strip()
        if v:
            parts.append(f"{label}: {v}")
    return " | ".join(parts) if parts else "no advance answers on file yet"


def fetch(stored_name, dest, dry):
    if os.path.exists(dest):
        return "kept"
    if dry:
        return "would fetch"
    p = subprocess.run(SCP_PREFIX + [f"{VM}:{UPLOADS}/{stored_name}", dest], capture_output=True, text=True)
    return "fetched" if p.returncode == 0 else f"FAILED ({p.stderr.strip()[-120:]})"


def sync(rows, dry=False):
    import scaffold_show
    scaffold_show.AUDIO = AUDIO
    out = []
    for r in rows:
        venue = (r.get("venue") or "").strip()
        if venue not in VENUES:
            out.append(f"skip  {r.get('artist')} @ {venue!r} — venue not mapped"); continue
        code, vfolder = VENUES[venue]
        artist, date = (r.get("artist") or "").strip(), r.get("show_date")
        if not artist or not date:
            continue
        key = show_key(venue, date, artist)
        folder = os.path.join(AUDIO, vfolder, f"{date} {artist}")
        # an existing folder for the same key under a different spelling wins
        existing = None
        vdir = os.path.join(AUDIO, vfolder)
        if os.path.isdir(vdir):
            for name in os.listdir(vdir):
                st = show_status.load(os.path.join(vdir, name))
                if st and st.get("show_key") == key:
                    existing = os.path.join(vdir, name); break
        folder = existing or folder
        made = []
        if not os.path.isdir(folder):
            if dry:
                made.append("would scaffold")
            else:
                rc = scaffold_show.main(["--venue", code, "--date", date, "--name", artist])
                if rc != 0:
                    out.append(f"FAIL  {key}: scaffold returned {rc}"); continue
                made.append("scaffolded")
        if not dry:
            st = show_status.load(folder) or {}
            if (st.get("show_key"), st.get("advance_show_id")) != (key, r.get("show_id")):
                _stamp_extra(folder, {"show_key": key, "advance_show_id": r.get("show_id"),
                                      "advance_event": r.get("event_name")})
                made.append("show_key stamped")
        # band files
        for f in (r.get("files") or []):
            ext = os.path.splitext(f.get("filename") or f.get("stored_name") or "")[1] or ".pdf"
            if f.get("kind") == "stage_plot":
                dest = os.path.join(folder, f"{artist} - Stage Plot{ext}")
            elif f.get("kind") == "input_list":
                dest = os.path.join(folder, f"{artist} - Input List (band){ext}")
            else:
                continue
            made.append(f"{os.path.basename(dest)}: {fetch(f['stored_name'], dest, dry)}")
        # brief skeleton
        brief = os.path.join(folder, f"{artist}.brief.json")
        if not os.path.exists(brief):
            if dry:
                made.append("would write brief.json")
            else:
                json.dump({
                    "show_name": artist, "artist": artist, "venue": code,
                    "venue_label": venue + (" (outdoor)" if code != "memo" else ""),
                    "console_label": CONSOLE.get(code, "confirm console"),
                    "show_date": date, "show_time": r.get("event_start") or "",
                    "foh_engineer": "Brian Lloyd", "mon_engineer": "", "rev": "Rev 0 — advance skeleton",
                    "show_key": key, "advance_show_id": r.get("show_id"),
                    "event_name": r.get("event_name") or "", "series": r.get("show_series") or "",
                    "show_notes": notes_from(r.get("data")),
                    "channels": [],
                }, open(brief, "w"), indent=2, ensure_ascii=False)
                made.append("brief.json written (facts only, no channels)")
        out.append(f"{'ok   ' if made else 'up-to-date'} {key}" + (f" — {'; '.join(made)}" if made else ""))
    return out


def _stamp_extra(folder, extra):
    st = show_status.load(folder) or {}
    st.update(extra)
    with open(os.path.join(folder, show_status.FILENAME), "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2); f.write("\n")


def push_status(dry=False):
    rows = {}
    for vcode, vfolder in VENUES.values():
        vdir = os.path.join(AUDIO, vfolder)
        if not os.path.isdir(vdir):
            continue
        for name in sorted(os.listdir(vdir)):
            m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.+)$", name)
            if not m:
                continue
            st = show_status.load(os.path.join(vdir, name))
            if not st:
                continue
            key = st.get("show_key") or f"{vcode}-{m.group(1)}-{slug(m.group(2))}"
            stages = st.get("stages") or {}
            rows[key] = {"show": m.group(2), "venue": vfolder, "date": m.group(1), "rev": st.get("rev"),
                         **{s: (stages.get(s) or {}).get("at") for s in ("packet_built", "ses_built", "published", "harvested")}}
    payload = {"generated": datetime.datetime.now().isoformat(timespec="seconds"), "shows": rows}
    dest = os.path.join(NYQUIST, "show-packet-status.json")
    if dry:
        return f"would write {dest} ({len(rows)} shows)"
    os.makedirs(NYQUIST, exist_ok=True)
    json.dump(payload, open(dest, "w"), indent=2)
    return f"wrote {dest} ({len(rows)} shows)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--push-status", action="store_true")
    ap.add_argument("--from-json")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.sync or a.push_status):
        a.sync = True
    if a.sync:
        rows = json.load(open(a.from_json)) if a.from_json else pull(a.days)
        print(f"advance shows in window: {len(rows)}")
        for line in sync(rows, a.dry_run):
            print(" ", line)
    print(" ", push_status(a.dry_run))


if __name__ == "__main__":
    main()
