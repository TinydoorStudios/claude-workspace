#!/usr/bin/env python3
"""File a Memorial Hall show's advance doc + uploads into Dropbox (2026-09-29).

Memo doesn't use the universal day-sheet. Its paperwork lives in a folder per
show, the way the Memo team has always filed it:

    3CDC Memorial Hall/<MM.YYYY> MEMO/<MM.DD.YY> <Event>/
        MEMO Adv - <Event>.docx
        <every file the artist or staff uploaded, original names>

The doc is drawn fresh from the database each time by build_memo_template
(one layout for the blank template and the filled doc):

  - each act's answers = its Memo submissions layered oldest -> newest
    (memo_fields.merge: a later non-blank answer wins, blanks never erase)
  - event-level answers = the same layering across every act on the bill
  - booking row seeds what nobody has typed yet (times, lead, contact)
  - crew = the staffing sheet's Memorial Hall block (Mix -> FOH/Monitors,
    Tech -> LX, Stagehand -> Stage Hand x2, Stage Support x3, Other ->
    Additional Info; Brian 2026-09-29), then the staff "Crew override" box
  - Curfew = End of Show + 90 min when blank
  - one artist -> the one-artist layout; a second act booked into the same
    show (same date + event name) -> the two-artist layout

A person may hand-edit the filed doc in Dropbox. The doc's hash is recorded
at every write (data/memo_docs.json); if the file on disk no longer matches,
it is left alone and the new version is saved beside it as
"MEMO Adv - <Event> (updated MMDDYY-HHMM).docx". Past shows are never touched.

    memo_doc.py --show-id 123
    memo_doc.py --venue "Memorial Hall" --date 2026-10-04 --artist "Holly Bowling"
    memo_doc.py --show-id 123 --out /tmp/test.docx     (write there, file nothing)
"""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db  # noqa: E402
import build_memo_template as T  # noqa: E402
import fieldspec as fs  # noqa: E402
import memo_fields as M  # noqa: E402
import staffing  # noqa: E402

DATA = HERE.parent / "data"
if not (DATA / "uploads").exists() and (HERE.parent / "app" / "data" / "uploads").exists():
    DATA = HERE.parent / "app" / "data"
UPLOADS = DATA / "uploads"
LEDGER = DATA / "memo_docs.json"


# ── small helpers ────────────────────────────────────────────────────────────
def _norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip()).lower()


def _clock(v):
    """'19:30' (a time input) -> '7:30p'; anything else passes through."""
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", str(v or "").strip())
    if not m:
        return str(v or "").strip()
    h, mi = int(m.group(1)), int(m.group(2))
    return f"{h % 12 or 12}:{mi:02d}{'a' if h < 12 else 'p'}"


def _minutes(v):
    """'19:30' / '7:30p' / '7:30 PM' / '10p' -> minutes past midnight, or None."""
    s = str(v or "").strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?([ap])?m?", s)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if ap == "p" and h < 12:
        h += 12
    if ap == "a" and h == 12:
        h = 0
    if not ap and ":" not in s:
        return None
    return h * 60 + mi


def _plus(v, mins):
    base = _minutes(v)
    if base is None:
        return ""
    t = (base + mins) % 1440
    h, mi = divmod(t, 60)
    return f"{h % 12 or 12}:{mi:02d}{'a' if h < 12 else 'p'}"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _ledger():
    try:
        return json.loads(LEDGER.read_text())
    except (OSError, ValueError):
        return {}


def _save_ledger(led):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text(json.dumps(led, indent=1, sort_keys=True))
    tmp.replace(LEDGER)


def _safe_name(s):
    return re.sub(r'[\\/:*?"<>|]+', "-", str(s or "")).strip(" .") or "Show"


# ── who is on the bill ──────────────────────────────────────────────────────
def _booking(cur, venue, date, artist_name):
    cur.execute(r"""SELECT * FROM bookings WHERE venue=%s AND event_date=%s
                    AND lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g'))) = %s
                    ORDER BY id DESC LIMIT 1""", (venue, date, _norm(artist_name)))
    return cur.fetchone()


def group_for_show(cur, show_id):
    """(date, event_name, [show rows]) — every live Memo show on the same date
    whose booking carries the same event name. No event name -> the show alone."""
    s = db.show_with_artist(cur, show_id)
    if not s or s["venue"] != M.VENUE:
        return None
    b = _booking(cur, s["venue"], s["show_date"], s["artist_name"]) or {}
    ev_name = (b.get("event_name") or "").strip()
    cur.execute("""SELECT s.id, s.artist_id, s.show_date, s.venue, a.name AS artist_name
                   FROM shows s JOIN artists a ON a.id = s.artist_id
                   WHERE s.venue=%s AND s.show_date=%s AND s.cancelled_at IS NULL
                   ORDER BY s.id""", (s["venue"], s["show_date"]))
    same_day = cur.fetchall()
    group = []
    for r in same_day:
        rb = _booking(cur, r["venue"], r["show_date"], r["artist_name"]) or {}
        if r["id"] == show_id or (ev_name and _norm(rb.get("event_name")) == _norm(ev_name)):
            group.append({**r, "booking": rb})
    # a second act booked into the same event but with no show row yet (the
    # pipeline makes those on its own schedule) still counts: the doc goes
    # two-artist the moment the booking exists
    if ev_name:
        # every act that has a show row at all (a cancelled one included) is
        # already decided above; only booking-only acts are added here
        have = {_norm(r["artist_name"]) for r in group}
        cur.execute("""SELECT a.name FROM shows s JOIN artists a ON a.id = s.artist_id
                       WHERE s.venue=%s AND s.show_date=%s""", (s["venue"], s["show_date"]))
        have |= {_norm(r["name"]) for r in cur.fetchall()}
        cur.execute("SELECT * FROM bookings WHERE venue=%s AND event_date=%s ORDER BY id",
                    (s["venue"], s["show_date"]))
        for rb in cur.fetchall():
            if _norm(rb.get("event_name")) == _norm(ev_name) and _norm(rb["artist_name"]) not in have:
                have.add(_norm(rb["artist_name"]))
                group.append({"id": None, "artist_id": None, "show_date": s["show_date"],
                              "venue": s["venue"], "artist_name": rb["artist_name"], "booking": rb})
    # bill order: the booking's set time when both have one, else booking order
    group.sort(key=lambda r: (_minutes((r["booking"] or {}).get("event_start")) or 9999,
                              (r["booking"] or {}).get("id") or 0, r["id"]))
    return s["show_date"], ev_name or s["artist_name"], group


def memo_submissions(cur, show_id):
    cur.execute("""SELECT data, submitted_at FROM submissions
                   WHERE show_id=%s AND data->>'_form' = %s
                   ORDER BY submitted_at, id""", (show_id, M.FORM_KEY))
    return cur.fetchall()


def show_state(cur, show_id):
    """Merged answers for one show (what the form prefills from, too)."""
    return M.merge([r["data"] for r in memo_submissions(cur, show_id)])


# ── staffing ─────────────────────────────────────────────────────────────────
def _staff_row(date, hints):
    """The staffing-sheet row for this Memo show, or None. Memo books several
    events a day, so the row is picked by event/artist name when the date has
    more than one; never guessed."""
    cols = staffing.SCHEDULE_COLUMNS.get(M.VENUE)
    try:
        rows = staffing._fetch_csv(staffing.SCHEDULE_GID)
        codes = staffing._fetch_csv(staffing.CODES_GID)
    except Exception as e:  # noqa: BLE001 — sheet down isn't fatal
        print(f"[memo_doc] staffing sheet unreachable: {e!r}")
        return None, None
    need = max(cols.values())
    todays = [r for r in rows if len(r) > need and staffing._parse_date(r[cols["date"]]) == date
              and any((r[c] or "").strip() for k, c in cols.items() if k != "date")]
    if len(todays) == 1:
        return todays[0], codes
    hints = [_norm(h) for h in hints if _norm(h)]
    hit = [r for r in todays if any(h in _norm(r[cols["event"]]) for h in hints)]
    return (hit[0], codes) if len(hit) == 1 else (None, codes)


def crew_for(date, hints, override_text=""):
    cols = staffing.SCHEDULE_COLUMNS[M.VENUE]
    row, codes = _staff_row(date, hints)
    roles = {"FOH": [], "Monitors": [], "LX": [], "Stage Hand": [], "Video": [],
             "Stage Support": [], "Memo Lead": []}
    other = []
    if row:
        mix = staffing._split_mix_cell((row[cols["mix"]] or "").strip())
        if len(mix) in (1, 2):
            roles["FOH"] = [staffing._format_row_or_raw(mix[0], codes)]
            if len(mix) == 2:
                roles["Monitors"] = [staffing._format_row_or_raw(mix[1], codes)]

        def names(key):
            return staffing._resolve_names(
                staffing._split_mix_cell((row[cols[key]] or "").strip()), codes)
        roles["LX"] = names("tech")
        roles["Stage Hand"] = names("stagehand")
        roles["Stage Support"] = names("stage_support")
        other = names("other")
    # staff override box: "Role: a, b" per line
    for line in (override_text or "").splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = next((r for r in roles if _norm(r) == _norm(k) or _norm(r) + "s" == _norm(k)), None)
        if k:
            roles[k] = [x.strip() for x in re.split(r"[,/+&]", v) if x.strip()]
    return roles, other


def crew_rows(roles, video, lead):
    slots = {"Stage Hand": 2, "Stage Support": 3}
    out = []
    for role in ("FOH", "Monitors", "LX", "Stage Hand", "Video", "Stage Support", "Memo Lead"):
        if role == "Video":
            out.append(("Video", video or ", ".join(roles["Video"])))
            continue
        if role == "Memo Lead":
            out.append(("Memo Lead", lead or ", ".join(roles["Memo Lead"]) or M.DEFAULTS["memo_lead"]))
            continue
        names = roles[role]
        n = slots.get(role, 1)
        vals = names[:n] + [""] * (n - len(names[:n]))
        if len(names) > n:   # never drop a name: the last slot carries the rest
            vals[-1] = ", ".join(names[n - 1:])
        out += [(role, v) for v in vals]
    return out


# ── build ────────────────────────────────────────────────────────────────────
def values_for(cur, show_id):
    """(Values, info) for the show's whole bill, or (None, None)."""
    g = group_for_show(cur, show_id)
    if not g:
        return None, None
    date, ev_name, group = g
    acts, subs_all = [], []
    for r in group:
        subs = memo_submissions(cur, r["id"]) if r["id"] else []
        subs_all += [(x["submitted_at"], x["data"]) for x in subs]
        st = M.merge([x["data"] for x in subs])
        b = r["booking"] or {}
        a = {k: v for k, v in st.items() if k in M.FIELDS and M.FIELDS[k]["per_act"]}
        a["_name"] = r["artist_name"]
        for k, bk in (("contact_name", "contact_name"), ("contact_email", "contact_email")):
            a.setdefault(k, b.get(bk) or "")
        for k, dv in M.DEFAULTS.items():
            if k in M.FIELDS and M.FIELDS[k]["per_act"]:
                a.setdefault(k, dv)
        a["_files"] = st.get("memo_files", [])
        plots = [nm for f, nm in planned(date, a) if f.get("kind") == "stage_plot"]
        a["_stage_plot"] = ("See folder — " + ", ".join(plots)) if plots else ""
        a["_show_id"] = r["id"]
        acts.append(a)

    subs_all.sort(key=lambda x: x[0])
    evs = M.merge([d for _t, d in subs_all])
    event = {k: v for k, v in evs.items() if k in M.FIELDS and not M.FIELDS[k]["per_act"]}
    b0 = group[0]["booking"] or {}
    seeds = {"artist_load_in": b0.get("load_in"), "sound_check": b0.get("soundcheck"),
             "set_1": b0.get("event_start"), "end_of_show": b0.get("event_end"),
             "curfew": b0.get("curfew")}
    for k, v in seeds.items():
        if v and not event.get(k):
            event[k] = v
    if b0.get("lead_name") and not event.get("memo_lead"):
        event["memo_lead"] = " · ".join(x for x in (b0.get("lead_name"), b0.get("lead_phone")) if x)
    if not event.get("event_type") and b0.get("event_type"):
        et = _norm(b0["event_type"])
        event["event_type"] = "Third Party Event" if "third" in et or "3rd" in et else \
            "Internal Event" if "internal" in et else ""
    staff_times = staffing.event_times_for(M.VENUE, date, event_name=ev_name,
                                           artist_name=acts[0]["_name"]) or {}
    if staff_times.get("crew_call") and not event.get("crew_call"):
        event["crew_call"] = staff_times["crew_call"]
    for k in [f["key"] for f in M.SECTIONS[1][2]]:       # schedule -> 7:30p style
        if event.get(k) and M.FIELDS[k]["kind"] == "time":
            event[k] = _clock(event[k])
    if not event.get("curfew") and event.get("end_of_show"):
        event["curfew"] = _plus(event["end_of_show"], M.CURFEW_AFTER_END_MIN)
    event["_date"] = date.strftime("%A, %B %-d, %Y")
    event["_event"] = ev_name

    roles, other = crew_for(date, [ev_name] + [a["_name"] for a in acts],
                            event.get("crew_override", ""))
    crew = crew_rows(roles, event.get("video"), event.get("memo_lead"))
    if other:
        a0 = acts[0]
        note = "Staffing sheet (Other): " + ", ".join(other)
        a0["additional_info"] = (a0.get("additional_info", "") + "\n" + note).strip()

    V = T.Values(event=event, acts=acts, crew=crew)
    info = {"date": date, "event": ev_name, "acts": acts, "n": len(acts)}
    return V, info


def show_folder(date, ev_name):
    month = fs.real_dropbox_root() / fs.real_venue_folder(M.VENUE) / fs.real_month_folder(M.VENUE, date)
    prefix = date.strftime("%m.%d.%y")
    want = f"{prefix} {_safe_name(ev_name)}"
    if month.exists():
        # reuse a folder the team already made for this show ("09.20.26 Asleep at the Wheel")
        toks = {t for t in re.split(r"[^a-z0-9]+", _norm(ev_name)) if len(t) > 2}
        for p in sorted(month.iterdir()):
            if not p.is_dir() or not p.name.startswith(prefix[:5]):
                continue
            if _norm(p.name) == _norm(want):
                return p
            ptoks = set(re.split(r"[^a-z0-9]+", _norm(p.name)))
            if prefix in p.name and toks and len(toks & ptoks) >= max(1, len(toks) // 2):
                return p
    return month / want


def filed_name(date, act, kind, orig, n):
    """'10.04.26 Holly Bowling Stage Plot.pdf' (Brian, 2026-09-29); a second
    file in the same bucket gets ' 2'. 'Anything else' keeps its own name."""
    ext = Path(orig or "").suffix.lower()
    if kind not in M.FILED_NAME:
        return _safe_name(orig)
    return _safe_name(f"{date.strftime('%m.%d.%y')} {act} {M.FILED_NAME[kind]}"
                      + (f" {n}" if n > 1 else "")) + ext


def planned(date, a):
    """[(file info, filed name)] for one act, numbered per bucket in upload order."""
    seen, out = {}, []
    for f in a.get("_files") or []:
        seen[f["kind"]] = seen.get(f["kind"], 0) + 1
        out.append((f, filed_name(date, a["_name"], f["kind"], f.get("filename"), seen[f["kind"]])))
    return out


def file_uploads(folder, acts, date, dry_run=False):
    """Copy every upload in under its filed name. Bytes already in the folder
    under any name are skipped; a name taken by different bytes gets '(2)'."""
    copied = []
    have = {}
    if folder.exists():
        for p in folder.iterdir():
            if p.is_file():
                have.setdefault(p.stat().st_size, []).append(p)
    for a in acts:
        for f, name in planned(date, a):
            src = UPLOADS / f["stored_name"]
            if not src.exists():
                print(f"  ! upload missing on server: {f['stored_name']}")
                continue
            size = src.stat().st_size
            if any(_sha(p) == _sha(src) for p in have.get(size, [])):
                continue
            dest, n = folder / name, 2
            while dest.exists():
                dest = folder / f"{Path(name).stem} ({n}){Path(name).suffix}"
                n += 1
            if not dry_run:
                folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                have.setdefault(size, []).append(dest)
            copied.append(dest.name)
    return copied


@contextlib.contextmanager
def _one_at_a_time():
    """Every Memo filing runs under one lock: a form save's background run and
    a pipeline run landing together must not both decide 'not hand-edited' and
    then write over each other (or over an edit made in between)."""
    DATA.mkdir(parents=True, exist_ok=True)
    with open(DATA / "memo_doc.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def file_show(show_id, dry_run=False, out=None, today=None):
    """Build + file the doc for this show's bill. Returns a result dict shaped
    like docmerge.file_event_doc's so the pipeline can report it the same way."""
    if out or dry_run:
        return _file_show(show_id, dry_run=dry_run, out=out, today=today)
    with _one_at_a_time():
        return _file_show(show_id, today=today)


def _file_show(show_id, dry_run=False, out=None, today=None):
    today = today or dt.date.today()
    res = {"action": None, "path": None, "notices": [], "hand_edited": False,
           "renamed_from": None, "filled": 0, "review": False, "applied": set(), "copied": []}
    with db.get_conn() as conn, conn.cursor() as cur:
        V, info = values_for(cur, show_id)
    if not V:
        res["action"] = "not-memo"
        return res
    if out:
        T.build_advance(Path(out), 2 if info["n"] >= 2 else 1, V)
        res.update(action="created", path=str(out))
        return res
    if info["date"] < today:
        res["action"] = "past"
        return res
    if info["n"] > 2:
        res["notices"].append({"field": "Bill size", "kind": "bill_size",
                               "doc_value": "Memo doc holds 2 artists",
                               "new_value": ", ".join(a["_name"] for a in info["acts"][2:]),
                               "cell_key": f"bill_size:{info['n']}"})
    folder = show_folder(info["date"], info["event"])
    target = folder / f"MEMO Adv - {_safe_name(info['event'])}.docx"
    res["path"] = str(target)
    res["copied"] = file_uploads(folder, info["acts"], info["date"], dry_run=dry_run)
    if dry_run:
        res["action"] = "dry-run"
        return res

    led = _ledger()
    key = str(target)
    rec = led.get(key) or {}
    vhash = hashlib.sha256(repr((V.event, V.acts, V.crew)).encode()).hexdigest()
    if target.exists():
        if rec.get("sha") != _sha(target):
            # a person edited it (or it pre-dates the pipeline): never overwrite
            res["hand_edited"] = True
            stamp = dt.datetime.now().strftime("%m%d%y-%H%M")
            target = folder / f"MEMO Adv - {_safe_name(info['event'])} (updated {stamp}).docx"
            res["path"] = str(target)
        elif rec.get("values") == vhash:
            res["action"] = "unchanged"
            return res
    folder.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name("." + target.name + ".tmp")
    T.build_advance(tmp, 2 if info["n"] >= 2 else 1, V)
    if not res["hand_edited"] and target.exists() and rec.get("sha") != _sha(target):
        # edited by a person while we were building: keep theirs, save ours beside it
        res["hand_edited"] = True
        stamp = dt.datetime.now().strftime("%m%d%y-%H%M")
        target = folder / f"MEMO Adv - {_safe_name(info['event'])} (updated {stamp}).docx"
        res["path"] = str(target)
    tmp.replace(target)
    if not res["hand_edited"]:
        led[key] = {"sha": _sha(target), "values": vhash,
                    "written_at": dt.datetime.now().isoformat(timespec="seconds")}
        _save_ledger(led)
    res["action"] = "merged" if rec else "created"
    return res


def file_for_event(ev, acts, dry_run=False, today=None):
    """docmerge.file_event_doc's Memo branch: the pipeline hands over an
    events row + its acts; file the bill through the first act's show."""
    with db.get_conn() as conn, conn.cursor() as cur:
        for a in acts:
            if not a.get("artist_id"):
                continue
            cur.execute("""SELECT id FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s
                           AND cancelled_at IS NULL""",
                        (a["artist_id"], ev.get("venue"), ev.get("event_date")))
            row = cur.fetchone()
            if row:
                return file_show(row["id"], dry_run=dry_run, today=today)
    return {"action": "no-show", "path": None, "notices": [], "hand_edited": False,
            "renamed_from": None, "filled": 0, "review": False, "applied": set()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-id", type=int)
    ap.add_argument("--venue", default=M.VENUE)
    ap.add_argument("--date")
    ap.add_argument("--artist")
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sid = a.show_id
    if not sid:
        with db.get_conn() as conn, conn.cursor() as cur:
            art = db.find_artist_by_name(cur, a.artist or "")
            if art:
                cur.execute("SELECT id FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s",
                            (art["id"], a.venue, a.date))
                row = cur.fetchone()
                sid = row["id"] if row else None
    if not sid:
        sys.exit("no such Memo show")
    res = file_show(sid, dry_run=a.dry_run, out=a.out)
    print(f"memo doc {res['action']}: {res.get('path')}"
          + (f" (+{len(res['copied'])} file(s): {', '.join(res['copied'])})" if res.get("copied") else "")
          + (" [hand-edited: saved beside it]" if res.get("hand_edited") else ""))


if __name__ == "__main__":
    main()
