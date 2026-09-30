#!/opt/band-advance/venv/bin/python
"""Memorial Hall advance, end to end, against the staging clone (2026-09-29).

    ~/advtest/code/tools/staging/test_memo.py

Books a Memo show as staff, fills the staff side, fills the band side from a
cookie-less session with several uploads, then checks the filed doc + files
in ~/advtest/Dropbox, blank-never-erases, the two-artist switch, hand-edit
protection, and that the universal form still renders.
"""
import datetime as dt
import http.cookiejar
import io
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

T = Path.home() / "advtest"
for line in (T / "advtest.env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()
CODE = T / "code"
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(CODE / "tools"))
import advance_db as db  # noqa: E402
import docx  # noqa: E402

with db.get_conn() as _c:
    assert _c.execute("SELECT current_database()").fetchone()["current_database"] == "advance_test"

APP = "http://127.0.0.1:8198"
PY = "/opt/band-advance/venv/bin/python"
DROP = Path(os.environ["ADVANCE_DROPBOX_ROOT"])
DATE = dt.date.today() + dt.timedelta(days=40 + int(uuid.uuid4().int % 300))  # fresh date per run
TAG = uuid.uuid4().hex[:5]
EVENT = f"Memo Test Night {TAG}"
BAND1, BAND2 = f"Test Quartet {TAG}", f"Opener Duo {TAG}"
RESULTS = []


def check(cond, msg):
    RESULTS.append(bool(cond))
    print(("  ok   " if cond else "  FAIL ") + msg, flush=True)


class Client:
    def __init__(self):
        # the session cookie is Secure; staging is plain http on localhost
        self.jar = http.cookiejar.CookieJar(policy=http.cookiejar.DefaultCookiePolicy(
            secure_protocols=("http", "https")))
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def req(self, path, data=None, files=None, method=None):
        url = path if path.startswith("http") else APP + path
        body, hdr = None, {}
        if files is not None:
            b = uuid.uuid4().hex
            buf = io.BytesIO()
            for k, v in (data or []):
                buf.write(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
            for k, name, content in files:
                buf.write(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{name}\"\r\n"
                          "Content-Type: application/octet-stream\r\n\r\n".encode() + content + b"\r\n")
            buf.write(f"--{b}--\r\n".encode())
            body, hdr = buf.getvalue(), {"Content-Type": f"multipart/form-data; boundary={b}"}
        elif data is not None:
            body = urllib.parse.urlencode(data).encode()
            hdr = {"Content-Type": "application/x-www-form-urlencoded"}
        r = urllib.request.Request(url, data=body, headers=hdr, method=method)
        try:
            with self.op.open(r, timeout=120) as resp:
                return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace"), url


def pdf(tag):
    return b"%PDF-1.4\n% " + tag.encode() + b"\n%%EOF\n"


def csrf_of(html):
    m = re.search(r'name="csrf" value="([^"]+)"', html)
    return m.group(1) if m else ""


def token_of(url):
    return urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]


def book(staff, artist, email, start="20:00", end="21:30"):
    st, html, _ = staff.req("/booking")
    c = csrf_of(html)
    st, html, _ = staff.req("/booking", {
        "csrf": c, "entered_by": "Nyquist test", "series": "Stand-Alone Internal",
        "event_name": EVENT, "event_date": DATE.isoformat(), "venue": "Memorial Hall",
        "set_start": start, "set_end": end, "artist_name": artist,
        "contact_name": "Pat Tester", "contact_email": email, "event_start": "", "event_end": ""})
    m = re.search(r'href="(https?://[^"]+/(?:s|f)/[^"]+)"', html)
    return st, (m.group(1) if m else None), html


def memo_doc(show_id):
    out = subprocess.run([PY, "memo_doc.py", "--show-id", str(show_id)], cwd=CODE / "tools",
                         capture_output=True, text=True, env=os.environ)
    return (out.stdout + out.stderr).strip()


def show_id_for(artist):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT s.id FROM shows s JOIN artists a ON a.id=s.artist_id
                       WHERE a.name=%s AND s.venue='Memorial Hall' AND s.show_date=%s""", (artist, DATE))
        r = cur.fetchone()
        return r["id"] if r else None


def doc_text(p):
    d = docx.Document(str(p))
    from docx.oxml.ns import qn
    return "\n".join("".join(t.text or "" for t in para.iter(qn("w:t")))
                     for para in d.element.body.iter(qn("w:p")))


def main():
    global DATE
    staff = Client()
    st, _, _ = staff.req("/gate", {"passcode": os.environ.get("ADVANCE_GATE_PASS", "lockdown")})
    check(st in (200, 302), "staff signs in")

    # ── booking -> staff fill link
    st, link, html = book(staff, BAND1, f"pat+{TAG}@example.com")
    check(st == 200 and link, f"Memo booking saved and shows a fill link ({link})")
    if not link:
        print(st, re.findall(r'class="banner[^"]*"[^>]*>\s*([^<]+)', html)[:3])
        return
    st, html, url = staff.req(link)
    tok = token_of(url)
    check(st == 200 and "Memorial Hall Production Advance" in html, "fill link opens the Memo form")
    check(">Schedule<" in html and ">Crew<" in html, "staff view shows Schedule + Crew")
    c = csrf_of(html)

    # ── staff fills the staff side + two stage plots + a tech rider
    st, html, url = staff.req("/memo/submit", [
        ("token", tok), ("csrf", c), ("band_name", BAND1), ("show_date", DATE.isoformat()),
        ("presenter", "JBM Productions"), ("event_type", "Third Party Event"),
        ("doors", "19:00"), ("set_1", "20:00"), ("set_1_end", "20:55"), ("set_2", "21:15"),
        ("set_2_end", "22:15"), ("end_of_show", "22:15"),
        ("intermission", "Yes"), ("video", "Sam Video"),
        ("crew_override", "Stage Support: Ann, Bo, Cy, Di"),
        ("hospitality", "Yes"), ("hospitality_amount", "250"),
        ("buyout", "No"), ("parking", "SP+ Lot"), ("dashboard_passes", "3"),
        ("dressing_rooms__seen", "1"), ("dressing_rooms", "A"), ("dressing_rooms", "B"),
        ("settlement", "Yes"), ("settlement_contact", "Tour manager"),
        ("internal_notes", "Backline budget $1,100 internal"),
    ], files=[("up_stage_plot", "Plot page 1.pdf", pdf("p1")),
              ("up_stage_plot", "Plot page 2.pdf", pdf("p2")),
              ("up_tech_rider", "Tech Rider 2026.pdf", pdf("tr"))])
    check(st == 200 and "Saved." in html, "staff save returns to the form with a Saved banner")
    check('value="19:00"' in html and "Plot page 2.pdf" in html,
          "saved form shows staff answers + files on file")

    # ── the band's own view: no staff sections, staff answers invisible, uploads
    band = Client()
    st, html, _ = band.req(link)
    check(st == 200 and ">Schedule<" not in html and "hospitality_amount" not in html
          and "internal_notes" not in html and "budget $1,100" not in html,
          "band view hides every staff section/field, internal notes included")
    check("Plot page 1.pdf" not in html and "Already on file" not in html,
          "band doesn't see the files staff uploaded")
    st, html, _ = band.req("/memo/submit", [
        ("token", tok), ("band_name", BAND1), ("show_date", DATE.isoformat()),
        ("wedges", "4"), ("iems", "Yes"), ("iem_count", "2"), ("own_iems", "Yes"),
        ("split_snake", "Yes"), ("own_foh", "Yes"), ("engineer_foh", "Mike FOH"), ("own_mon", "House"),
        ("engineer_mon", "Ghost Name"),                             # own_mon=House: must be dropped
        ("risers", "Yes"), ("riser_count", "2"), ("veh_sprinter", "1"), ("veh_bus", "1"),
        ("photography", "No"),
        ("photo_restrictions", "No flash, first three songs"), ("backline", "Yes"),
        ("backline_notes", "Fender Twin"), ("contact_phone", "513-555-0100"),
        ("console_foh", "Tour"), ("console_foh_name", "Avid S6L"), ("foh_footprint", "10' x 6'"),
        ("buyout_amount", "99999"), ("doors", "03:00"),            # staff-only: must be ignored
    ], files=[("up_input_list", "Input List.xlsx", b"PK\x03\x04fake"),
              ("up_hospitality", "Hosp Rider.pdf", pdf("h"))])
    check(st == 200 and "Thank" in html, "band submit lands on the thank-you page")

    st, html, _ = band.req(link)
    check("Input List.xlsx" in html and "Plot page 1.pdf" not in html,
          "band still sees their own uploads, not ours")
    check("Total FOH footprint needed" in html and "do our best to accommodate" in html
          and "Avid S6L" in html, "tour FOH follow-ups + note on the band form")
    sid = show_id_for(BAND1)
    check(sid, "submissions landed on one Memo show")
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM submissions WHERE show_id=%s AND data->>'_form'='memo'", (sid,))
        n_sub = cur.fetchone()["n"]
        cur.execute("""SELECT count(*) AS n FROM files f JOIN submissions s ON s.id=f.submission_id
                       WHERE s.show_id=%s""", (sid,))
        n_files = cur.fetchone()["n"]
    check(n_sub == 2 and n_files == 5, f"2 memo submissions, 5 file rows ({n_sub}, {n_files})")

    # ── doc + files in the show folder
    time.sleep(3)
    print("   ", memo_doc(sid))
    month = DROP / "3CDC Memorial Hall" / f"{DATE.month:02d}.{DATE.year} MEMO"
    folder = month / f"{DATE.strftime('%m.%d.%y')} {EVENT}"
    doc = folder / f"MEMO Adv - {EVENT}.docx"
    check(doc.exists(), f"doc filed at {doc.relative_to(DROP)}")
    names = sorted(p.name for p in folder.iterdir()) if folder.exists() else []
    pre = f"{DATE.strftime('%m.%d.%y')} {BAND1}"
    want = [f"{pre} Stage Plot.pdf", f"{pre} Stage Plot 2.pdf", f"{pre} Tech Rider.pdf",
            f"{pre} Input List.xlsx", f"{pre} Hospitality Rider.pdf"]
    check(all(x in names for x in want), f"all 5 uploads filed under date + act + type: {names}")
    if doc.exists():
        t = doc_text(doc)
        check("ARTIST: " + BAND1 in t, "artist name on the doc")
        check("7:00p" in t and "10:15p" in t, "schedule times printed 7:00p style")
        check("11:45p" in t, "curfew = end of show + 90 min")
        check("Tour FOH" in t and "Avid S6L" in t and "10' x 6'" in t, "tour FOH console name + footprint on the doc")
        check("Set 1 End" in t and "8:55p" in t and "Set 2 Start" in t and "9:15p" in t,
              "both sets carry a start and an end time")
        check("3:00a" not in t, "band could not set a staff field (doors)")
        check("99999" not in t and "$ 250" in t, "band could not set buyout; staff hospitality $ printed")
        check("☒ Third Party Event" in t and "JBM Productions" in t, "event type + presenter")
        check("Wedges: 4" in t and "No flash, first three songs" in t, "band answers on the doc")
        check("Sam Video" in t and "Di" in t, "video + crew override (4th stage support kept)")
        check("☒ SP+ Lot — Dashboard passes: 3" in t, "parking choice + passes")
        check("A ☒" in t and "B ☒" in t, "dressing rooms ticked")
        check(f"{pre} Stage Plot.pdf" in t, "stage plot row names the filed files")
        check("Own rig: Yes" in t and "Split: Yes" in t, "IEM chain (own rig -> split) on the doc")
        check("FOH – Mike FOH" in t and "Mon – House" in t and "Ghost Name" not in t,
              "engineer questions: name only when bringing their own")
        check("#: 2" in t and "4' x 8' x 1'" in t, "risers + count + size note")
        check("1 sprinter" in t and "1 bus" in t, "vehicle types + counts")
        check("VIDEO" not in t and "Pre-Roll" not in t, "video section gone")
        check("Backline budget $1,100 internal" in t, "internal notes print on the doc")
        check("ARTIST 2" not in t, "one artist -> one-artist layout")

    # ── blank never erases: staff saves again with the hospitality box blank
    st, html, _ = staff.req(link)
    staff.req("/memo/submit", [("token", tok), ("csrf", csrf_of(html)), ("band_name", BAND1),
                               ("show_date", DATE.isoformat()), ("hospitality_amount", ""),
                               ("house", "19:30")], files=[])
    print("   ", memo_doc(sid))
    t = doc_text(doc) if doc.exists() else ""
    check("$ 250" in t and "7:30p" in t, "a blank save kept earlier answers and added the new one")

    # ── a band change to a settled answer is asked, not applied
    maillog = Path(os.environ["MAILLOG"])
    m0 = len(maillog.read_text().splitlines()) if maillog.exists() else 0
    st, html, _ = band.req("/memo/submit", [
        ("token", tok), ("band_name", BAND1), ("show_date", DATE.isoformat()),
        ("wedges", "5"), ("photography", "Yes"), ("meet_greet", "No")], files=[])
    check(st == 200, "band resubmits with two changed answers and one new one")
    with db.get_conn() as conn, conn.cursor() as cur:
        opn = db.open_memo_decisions(cur, show_id=sid)
    check(sorted(d["field"] for d in opn) == ["photography", "wedges"],
          f"two held decisions, the new answer applied ({[d['field'] for d in opn]})")
    print("   ", memo_doc(sid))
    t = doc_text(doc) if doc.exists() else ""
    check("Wedges: 4" in t and "Wedges: 5" not in t, "doc keeps the current answer while undecided")
    lines = maillog.read_text().splitlines()[m0:] if maillog.exists() else []
    check(any("changes to decide" in ln for ln in lines), "internal 'changes to decide' ping sent (stub)")
    st, html, _ = staff.req(link)
    check("band change(s) waiting on you" in html, "staff form shows the waiting banner")
    st, html, _ = staff.req(f"/doc-review?venue=Memorial%20Hall&date={DATE.isoformat()}")
    check(st == 200 and "Band changed an answer (2)" in html, "Doc Review lists both as questions")
    ids = {d["field"]: d["id"] for d in opn}
    st, html, _ = staff.req("/doc-review/memo", {"csrf": csrf_of(html), "venue": "Memorial Hall",
                                                 "date": DATE.isoformat(),
                                                 f"m{ids['wedges']}": "apply",
                                                 f"m{ids['photography']}": "keep"})
    with db.get_conn() as conn, conn.cursor() as cur:
        left = db.open_memo_decisions(cur, show_id=sid)
    check(st == 200 and not left, "both decided")
    time.sleep(3)
    print("   ", memo_doc(sid))
    t = doc_text(doc) if doc.exists() else ""
    check("Wedges: 5" in t, "Use new -> the band's answer is on the doc")
    ph = t.split("Photography")[1][:30] if "Photography" in t else ""
    check("☒ No" in ph, f"Keep current -> photography stays No ({ph!r})")

    # ── second act on the same event -> two-artist doc
    st, link2, h2 = book(staff, BAND2, f"duo+{TAG}@example.com", "19:00", "19:40")
    if not link2:
        print(re.findall(r'class="banner[^"]*"[^>]*>([^<]+)', h2)[:3])
    sid2 = show_id_for(BAND2)
    if not sid2 and link2:
        st, html, url = band.req(link2)
        band.req("/memo/submit", [("token", token_of(url)), ("band_name", BAND2),
                                  ("show_date", DATE.isoformat()), ("wedges", "2")], files=[])
        sid2 = show_id_for(BAND2)
    check(sid2, "second act booked into the same event")
    print("   ", memo_doc(sid))
    t = doc_text(doc) if doc.exists() else ""
    check("ARTIST 2" in t and BAND2 in t, "second act switches the doc to the two-artist layout")

    # ── hand edit is never overwritten
    time.sleep(6)   # let the app's own background filings from the saves above finish
    if doc.exists():
        d = docx.Document(str(doc))
        d.add_paragraph("hand edit")
        d.save(str(doc))
        band.req("/memo/submit", [("token", tok), ("band_name", BAND1), ("show_date", DATE.isoformat()),
                                  ("set_length", "2 x 45")], files=[])
        out = memo_doc(sid)
        print("   ", out)
        check("hand edit" in doc_text(doc), "hand-edited doc left alone")
        check(any("(updated" in p.name for p in folder.iterdir()), "new version saved beside it")

    # ── Memo's own ladder: welcome at 30 days out, chases 15/10/7/5/3/2/1
    import json as _json
    maillog = Path(os.environ["MAILLOG"])
    n0 = len(maillog.read_text().splitlines()) if maillog.exists() else 0
    keep, DATE = DATE, dt.date.today() + dt.timedelta(days=26)
    email26 = f"memo26+{TAG}@example.com"
    st, _, _ = book(staff, f"Thirty Window {TAG}", email26, "17:00", "17:30")
    got = False
    for _ in range(20 if db.welcome_paused("Memorial Hall") else 40):
        time.sleep(3)
        lines = maillog.read_text().splitlines()[n0:] if maillog.exists() else []
        # band-facing sends only; the internal "booking logged" notify also names the contact
        if any(email26 in ln and "/internal-send-outlook" in ln for ln in lines):
            got = True
            break
    if db.welcome_paused("Memorial Hall"):
        check(not got, "Memo welcome paused: a show booked 26 days out gets no email")
    else:
        check(got, "Memo show booked 26 days out gets its welcome now (inside Memo's 30-day window)")
    DATE = keep
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM shows WHERE venue='Memorial Hall' AND show_date=%s",
                    (dt.date.today() + dt.timedelta(days=26),))
        sid26 = [r["id"] for r in cur.fetchall()]
        cur.execute("SELECT days_before FROM advance_reminders WHERE show_id = ANY(%s)", (sid26,))
        skipped = sorted(r["days_before"] for r in cur.fetchall())
        ok = True
        for tier in db.ALL_CHASE_TIERS:
            try:
                db.shows_due_for_followup(cur, tier)
            except Exception as e:  # noqa: BLE001
                ok = False
                print("   tier", tier, e)
    check(ok and db.ALL_CHASE_TIERS == (15, 10, 5, 3, 2, 1), "every chase tier's due query runs")
    check(skipped == [], f"no Memo tier pre-skipped at 26 days out ({skipped})")
    check(db.welcome_days("Fountain Square") == 21 and db.tiers_for("Fountain Square") == (10, 7, 3, 1),
          "other venues keep 21 / 10-7-3-1")

    # ── the universal form is untouched
    st, html, _ = Client().req("/")
    check(st == 200 and "bandform" in html, "universal form still renders")
    st, html, _ = Client().req("/?venue=Memorial%20Hall")
    check(st == 200 and "memoform" in html, "?venue=Memorial Hall opens the Memo form")

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
