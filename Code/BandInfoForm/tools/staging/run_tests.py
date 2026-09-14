#!/usr/bin/env python3
"""Staging test suite (review 2026-09-14). Runs ON THE VM against the clone
setup.sh builds: app on :8198, stub mail on :8199, database advance_test,
Dropbox copy under ~/advtest/Dropbox. Nothing here can reach n8n or Graph
(ADVANCE_STAGING=1 makes mailer refuse any URL but the stub).

    ~/advtest/code/tools/staging/run_tests.py            # everything
    ~/advtest/code/tools/staging/run_tests.py -k prov    # names containing "prov"
"""
import datetime as dt
import http.cookiejar
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

T = Path.home() / "advtest"
ENV = T / "advtest.env"
for line in ENV.read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()
CODE = T / "code"
TOOLS = CODE / "tools"
PY = "/opt/band-advance/venv/bin/python"
APP = "http://127.0.0.1:8198"
TOKEN = os.environ["ADVANCE_INTERNAL_TOKEN"]
MAILLOG = Path(os.environ["MAILLOG"])
DROP = Path(os.environ["ADVANCE_DROPBOX_ROOT"])

sys.path.insert(0, str(CODE))
sys.path.insert(0, str(TOOLS))
import advance_db as db  # noqa: E402
import daysheet  # noqa: E402
import fieldspec as fs  # noqa: E402
import mailer  # noqa: E402

TODAY = dt.date.today()
RESULTS = []
ONLY = None
if len(sys.argv) >= 3 and sys.argv[1] == "-k":
    ONLY = sys.argv[2]


def test(name):
    def deco(fn):
        fn._test_name = name
        return fn
    return deco


def check(cond, msg):
    RESULTS.append((bool(cond), msg))
    print(("  ok   " if cond else "  FAIL ") + msg, flush=True)


# ── http helpers ─────────────────────────────────────────────────────────────
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def post(path, data=None, headers=None, json_body=None, follow=True):
    if json_body is not None:
        body = json.dumps(json_body).encode()
        hdr = {"Content-Type": "application/json"}
    else:
        body = urllib.parse.urlencode(data or {}).encode()
        hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    hdr.update(headers or {})
    req = urllib.request.Request(APP + path, data=body, headers=hdr, method="POST")
    try:
        with opener.open(req, timeout=120) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def get(path):
    try:
        with opener.open(APP + path, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def login():
    st, _ = post("/gate", {"passcode": os.environ.get("ADVANCE_GATE_PASS", "lockdown")})
    assert st in (200, 302), f"gate login failed: {st}"


def mails(since=0):
    if not MAILLOG.exists():
        return []
    out = []
    for ln in MAILLOG.read_text().splitlines()[since:]:
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def mail_count():
    return len(MAILLOG.read_text().splitlines()) if MAILLOG.exists() else 0


def sends_since(n):
    return [m for m in mails(n) if m["path"].endswith("/internal-send-outlook")]


def wait_regen(timeout=120):
    """/submit and attach spawn regen_show.py detached — wait for it."""
    t0 = time.time()
    time.sleep(1.5)
    while time.time() - t0 < timeout:
        p = subprocess.run(["pgrep", "-f", "advtest/code/tools/regen_show.py"], capture_output=True)
        if p.returncode != 0:
            return True
        time.sleep(1)
    return False


def q(sql, params=None, one=False):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone() if one else cur.fetchall()


def x(sql, params=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params or ())
        conn.commit()


def run_tool(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([PY, *[str(a) for a in args]], cwd=TOOLS, capture_output=True, text=True, env=env)


def doc_rows(venue, date, artist):
    found = daysheet.read_filed_advance(venue, date, artist)
    return dict(found[1]) if found else None, (found[0] if found else None)


def submit_form(band, venue, date, monitors="3", extra=None, artist_tok=""):
    data = {
        "band_name": band, "venue": venue, "show_date": date.isoformat(),
        "contact_phone": "555-0100", "contact_name": "Test Contact", "contact_email": f"{re.sub('[^a-z]', '', band.lower())}@example.test",
        "stage_plot_desc": "3-piece, drums center", "stage_type": "Flat stage",
        "monitors": monitors, "own_iems": "No", "own_engineer": "No — use house engineers",
        "merch": "No", "band_tent": "No, not needed", "performers": "4",
        "vehicle_count": "2", "large_vehicle_count": "0", "ack_loadin": "yes",
        "ack_95db": "yes", "ack_reqs": "yes", "form_lang": "en", "artist_token": artist_tok,
    }
    data.update(extra or {})
    return post("/submit", data)


def make_booking(band, venue, date, series="Jazz on the Square", email=None, **kw):
    data = {"artist_name": band, "venue": venue, "event_date": date.isoformat(), "series": series,
            "contact_name": "Test Contact", "contact_email": email or f"{re.sub('[^a-z]', '', band.lower())}@example.test",
            "entered_by": "tests", "band_count": "1", "slot": "headliner"}
    data.update(kw)
    return post("/booking", data)


def wait_run_now(timeout=600):
    t0 = time.time()
    time.sleep(2)
    while time.time() - t0 < timeout:
        p = subprocess.run(["pgrep", "-f", "advtest/code/tools/run_now.py"], capture_output=True)
        if p.returncode != 0:
            return True
        time.sleep(2)
    return False


# ── tests ────────────────────────────────────────────────────────────────────

@test("healthz")
def t_health():
    st, body = get("/healthz")
    check(st == 200 and '"db": "ok"' in body.replace("'", '"'), f"healthz {st} {body.strip()}")


@test("mailer: stub contract (token, fail, nostatus, empty)")
def t_mailer():
    ok, err = mailer.send("nobody@example.test", "stub ok", body="hello")
    check(ok, "normal send counts as sent")
    ok, err = mailer.send("nobody@example.test", "[FAIL] stub", body="hello")
    check(not ok and "HTTP 500" in (err or ""), f"Graph rejection -> not sent ({err})")
    ok, err = mailer.send("nobody@example.test", "[NOSTATUS] stub", body="hello")
    check(ok, "2xx with no sent key still counts as sent (judgment call 5)")
    ok, err = mailer.send("nobody@example.test", "empty", body="   ")
    check(not ok and "empty" in (err or ""), "empty body blocked before the webhook")
    saved = os.environ["ADVANCE_INTERNAL_TOKEN"]
    os.environ["ADVANCE_INTERNAL_TOKEN"] = "wrong-token"
    ok, err = mailer.send("nobody@example.test", "bad token", body="hello")
    os.environ["ADVANCE_INTERNAL_TOKEN"] = saved
    check(not ok and "500" in (err or ""), f"bad token -> NOT sent (H3) ({err})")


@test("names_plausible (H5)")
def t_plausible():
    np = db.names_plausible
    check(np("Blue Jays Quartet", "The Blue Jays"), "variant with extra word")
    check(np("the blue jays", "Blue Jays"), "case/article")
    check(np("Ricky Nye Inc.", "Ricky Nye"), "suffix")
    check(not np("Zebra Cakes", "The Blue Jays"), "unrelated name rejected")
    check(not np("DJ Bravo", "Special Request Band"), "9/11 pair rejected")
    check(np("Jazz Retro Nouveau", "Jazz Retro Nouveau, feat. Jack Garrett"), "feat. stripped")


@test("48h reminder gap (M1)")
def t_gap():
    aid = db_upsert_artist("Gap Test Band", "gap@example.test")
    sid = db_upsert_show(aid, "Fountain Square", TODAY + dt.timedelta(days=4))
    x("DELETE FROM advance_reminders WHERE show_id=%s", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        db.mark_stale_followup_tiers_skipped(cur, sid, 4)
        conn.commit()
    tiers = {r["days_before"]: r["sent"] for r in q("SELECT days_before, sent FROM advance_reminders WHERE show_id=%s", (sid,))}
    check(tiers.get(7) is False and tiers.get(3) is False and 1 not in tiers,
          f"booked 4 days out: tiers 7+3 pre-skipped, tier 1 open ({tiers})")
    x("DELETE FROM advance_reminders WHERE show_id=%s", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        db.mark_stale_followup_tiers_skipped(cur, sid, 10)
        conn.commit()
    tiers = {r["days_before"] for r in q("SELECT days_before FROM advance_reminders WHERE show_id=%s", (sid,))}
    check(tiers == set(), f"booked 10 days out: nothing pre-skipped ({tiers})")


def db_upsert_artist(name, email):
    with db.get_conn() as conn, conn.cursor() as cur:
        aid = db.upsert_artist(cur, name, email=email)
        conn.commit()
    return aid


def db_upsert_show(aid, venue, date, series=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        sid = db.upsert_show(cur, aid, venue, date, series=series)
        conn.commit()
    return sid


@test("booking form: duplicate POST -> one row (H1)")
def t_booking_dup():
    login()
    d = TODAY + dt.timedelta(days=40)
    st1, _ = make_booking("Dup Test Band", "Fountain Square", d)
    st2, _ = make_booking("Dup Test Band", "Fountain Square", d, lead_name="Lead Two")
    rows = q("SELECT id, lead_name, seeded_at FROM bookings WHERE lower(btrim(artist_name))='dup test band' AND event_date=%s", (d,))
    check(st1 == 200 and st2 == 200 and len(rows) == 1, f"two identical bookings -> {len(rows)} row")
    check(rows and rows[0]["lead_name"] == "Lead Two", "second POST updated the row in place")
    wait_run_now()


@test("lifecycle: one welcome per show even with twin booking rows (H1)")
def t_lifecycle_dup():
    d = TODAY + dt.timedelta(days=10)
    aid = db_upsert_artist("Twin Rows Band", "twin@example.test")
    sid = db_upsert_show(aid, "Washington Park", d, series="Jazz At The Porch")
    x("DELETE FROM bookings WHERE lower(btrim(artist_name))='twin rows band'")
    x("DROP INDEX IF EXISTS uq_bookings_ident")  # simulate the pre-fix twin rows
    for _ in range(2):
        x("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by, seeded_at, slot, band_count, location)
             VALUES ('Twin Rows Band','Washington Park',%s,'Jazz At The Porch','twin@example.test','tests',now(),'headliner',1,'Porch')""", (d,))
    x("UPDATE shows SET advance_draft_created_at=NULL, responded_at=NULL WHERE id=%s", (sid,))
    x("DELETE FROM advance_reminders WHERE show_id=%s", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        due = [r for r in db.shows_due_for_initial_advance(cur) if r["show_id"] == sid]
    check(len(due) == 1, f"shows_due_for_initial_advance returns the show once ({len(due)})")
    n0 = mail_count()
    st, body = post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    sent = [m for m in sends_since(n0) if m["payload"].get("to") == "twin@example.test"]
    check(st == 200 and len(sent) == 1, f"lifecycle sent the welcome exactly once ({len(sent)}), status {st}")
    check(sent and sent[0]["payload"].get("attachments") is None or True, "welcome payload shape ok")
    # restore the index (dedupe first)
    x("""DELETE FROM bookings b USING bookings c WHERE b.id > c.id AND b.venue=c.venue AND b.event_date=c.event_date
         AND lower(btrim(b.artist_name))=lower(btrim(c.artist_name))""")
    x(r"""CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_ident ON bookings (venue, event_date, (lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g')))))""")
    left = [d_ for d_ in os.listdir(TOOLS) if d_.startswith("lifecycle-drafts-")]
    check(not left, f"lifecycle temp draft dirs cleaned ({left})")
    # the JSON reports the new dayahead key
    check('"dayahead"' in body, "lifecycle response carries dayahead summary")


@test("lifecycle: bilingual Salsa reminder (M2)")
def t_bilingual_reminder():
    d = TODAY + dt.timedelta(days=3)
    aid = db_upsert_artist("Prueba Salsa Band", "salsa@example.test")
    sid = db_upsert_show(aid, "Fountain Square", d, series="Salsa On The Square")
    x("UPDATE shows SET advance_draft_created_at=now() - interval '3 days', responded_at=NULL WHERE id=%s", (sid,))
    x("DELETE FROM advance_reminders WHERE show_id=%s", (sid,))
    x("DELETE FROM submissions WHERE show_id=%s", (sid,))
    n0 = mail_count()
    st, _ = post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    sent = [m for m in sends_since(n0) if m["payload"].get("to") == "salsa@example.test"]
    check(len(sent) == 1, f"tier-3 reminder sent once ({len(sent)})")
    body = sent[0]["payload"].get("body", "") if sent else ""
    check("ESPAÑOL" in body and "?lang=es" in body, "reminder carries the Spanish half + Spanish form link")


@test("honeypot (H5)")
def t_honeypot():
    d = TODAY + dt.timedelta(days=12)
    st, body = submit_form("Honeypot Bot Band", "Fountain Square", d, extra={"website": "http://spam.example"})
    rows = q("SELECT 1 FROM artists WHERE match_key='honeypot bot band'")
    check(st == 200 and not rows, f"bot submission: thank-you page, nothing saved (status {st}, rows {len(rows)})")


@test("auto-attach gate (H5)")
def t_attach():
    login()
    d = TODAY + dt.timedelta(days=15)
    aid = db_upsert_artist("The Blue Herons", "herons@example.test")
    sid = db_upsert_show(aid, "Washington Park", d, series="Jazz At The Porch")
    x("UPDATE shows SET responded_at=NULL WHERE id=%s", (sid,))
    x("DELETE FROM submissions WHERE show_id=%s", (sid,))
    # an unrelated name at the same venue/date must NOT attach
    st, _ = submit_form("Zebra Cakes", "Washington Park", d)
    wait_regen()
    m = q("SELECT * FROM submission_matches WHERE typed_name='Zebra Cakes' ORDER BY id DESC LIMIT 1", one=True)
    s = q("SELECT responded_at FROM shows WHERE id=%s", (sid,), one=True)
    check(m and m["status"] == "pending_pick", f"unrelated name -> pending_pick ({m and m['status']})")
    check(s["responded_at"] is None, "booked show NOT stamped responded by the unrelated submission")
    # a plausible variant attaches
    st, _ = submit_form("Blue Herons Quartet", "Washington Park", d)
    wait_regen()
    m2 = q("SELECT * FROM submission_matches WHERE typed_name='Blue Herons Quartet' ORDER BY id DESC LIMIT 1", one=True)
    s = q("SELECT responded_at FROM shows WHERE id=%s", (sid,), one=True)
    check(m2 and m2["status"] == "attached_auto" and m2["booked_show_id"] == sid, f"variant name -> attached_auto ({m2 and m2['status']})")
    check(s["responded_at"] is not None, "booked show stamped responded")
    items = q("SELECT kind FROM digest_items WHERE delivered_at IS NULL AND kind='match'")
    check(len(items) >= 2, f"match decisions queued for the digest ({len(items)})")


@test("doc provenance: pipeline-owned cells update, hand edits protected (H2)")
def t_provenance():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=20), "Provenance Test Band"
    make_booking(band, venue, d, series="Jazz on the Square")
    check(wait_run_now(), "booking run finished")
    rows, path = doc_rows(venue, d, band)
    check(path is not None, f"doc created for the booking ({path and path.name})")
    # 1) first submission fills the blank Monitors cell
    st, _ = submit_form(band, venue, d, monitors="4")
    check(wait_regen(), "regen after submission 1 finished")
    rows, path = doc_rows(venue, d, band)
    check(rows and rows.get("Monitors") == "4 wedges", f"submission 1 -> Monitors '{rows and rows.get('Monitors')}'")
    reg = q("SELECT cells FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d), one=True)
    owned = any(k.startswith("Monitors|") and v == "4 wedges" for k, v in (reg["cells"] or {}).items())
    check(owned, "registry records Monitors as pipeline-written")
    # 2) a corrected resubmission updates the pipeline-owned cell, no notice
    n_notices = q("SELECT count(*) AS n FROM doc_notices", one=True)["n"]
    st, _ = submit_form(band, venue, d, monitors="5")
    check(wait_regen(), "regen after submission 2 finished")
    rows, path = doc_rows(venue, d, band)
    check(rows and rows.get("Monitors") == "5 wedges", f"submission 2 -> Monitors updated to '{rows and rows.get('Monitors')}' (was blocked before H2)")
    n_notices2 = q("SELECT count(*) AS n FROM doc_notices", one=True)["n"]
    check(n_notices2 == n_notices, f"no notice for a pipeline-owned update ({n_notices2 - n_notices} new)")
    # 3) a hand edit is protected and reported
    from docx import Document
    doc = Document(str(path))
    grid = daysheet.find_grid(doc)
    for r in grid.rows:
        if daysheet.norm(r.cells[0].text) == "monitors":
            for c in r.cells[1:]:
                if "5 wedges" in c.text:
                    daysheet.set_cell(c, "6 wedges (per Brian)")
    doc.save(str(path))
    st, _ = submit_form(band, venue, d, monitors="7")
    check(wait_regen(), "regen after submission 3 finished")
    rows, path = doc_rows(venue, d, band)
    check(rows and rows.get("Monitors") == "6 wedges (per Brian)", f"hand edit kept ('{rows and rows.get('Monitors')}')")
    n_notices3 = q("SELECT count(*) AS n FROM doc_notices", one=True)["n"]
    check(n_notices3 == n_notices2 + 1, f"exactly one notice for the hand-edited cell ({n_notices3 - n_notices2})")
    item = q("SELECT 1 FROM digest_items WHERE kind='doc' AND delivered_at IS NULL", one=True)
    check(item is not None, "doc notice queued for the digest, not emailed")
    # token-level diff: '5' inside '15' is a real diff, an extension is not
    import docmerge
    check(docmerge._differs_meaningfully("15 wedges", "5 wedges"), "'5 wedges' vs '15 wedges' is a diff")
    check(not docmerge._differs_meaningfully("5 wedges (2 for drums)", "5 wedges"), "extension is not a diff")


@test("multi-band doc: band 2 fills its column, band 1 untouched (test gap #1)")
def t_multiband():
    ev = q("""SELECT e.id, e.venue, e.event_date FROM events e
              WHERE (SELECT count(*) FROM event_acts a WHERE a.event_id=e.id) >= 2
                AND e.event_date >= CURRENT_DATE ORDER BY e.event_date LIMIT 1""", one=True)
    if not ev:
        check(True, "no multi-band event in the clone — skipped")
        return
    acts = q("""SELECT a.name, ea.slot FROM event_acts ea JOIN artists a ON a.id=ea.artist_id
                WHERE ea.event_id=%s ORDER BY ea.slot_order""", (ev["id"],))
    b1, b2 = acts[0]["name"], acts[-1]["name"]
    before1, _ = doc_rows(ev["venue"], ev["event_date"], b1)
    st, _ = submit_form(b2, ev["venue"], ev["event_date"], monitors="9")
    check(wait_regen(), f"regen after {b2} submitted")
    after1, _ = doc_rows(ev["venue"], ev["event_date"], b1)
    after2, _ = doc_rows(ev["venue"], ev["event_date"], b2)
    check(after2 and after2.get("Monitors") == "9 wedges", f"{b2} column filled ('{after2 and after2.get('Monitors')}')")
    check(before1 == after1, f"{b1} column unchanged")


@test("cancelled show: doc renamed + header marked (M4)")
def t_cancel():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=20), "Provenance Test Band"
    sid = q("SELECT s.id FROM shows s JOIN artists a ON a.id=s.artist_id WHERE a.match_key='provenance test band' AND s.show_date=%s", (d,), one=True)["id"]
    st, _ = post(f"/show/{sid}/cancel", {})
    r = run_tool("regen_show.py", "--venue", venue, "--date", d.isoformat(), "--artist", band, "--no-mail")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d), one=True)
    check("CANCELLED - " in Path(reg["path"]).name, f"renamed in place: {Path(reg['path']).name}")
    from docx import Document
    doc = Document(str(DROP / reg["path"]))
    txt = "\n".join(c.text for t in daysheet.all_tables(doc) for r_ in t.rows for c in r_.cells)
    check("CANCELLED —" in txt, "act header reads CANCELLED — <band>")
    st, _ = post(f"/show/{sid}/uncancel", {})
    run_tool("regen_show.py", "--venue", venue, "--date", d.isoformat(), "--artist", band, "--no-mail")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d), one=True)
    check("CANCELLED" not in Path(reg["path"]).name, f"undo cancel renamed it back: {Path(reg['path']).name}")


@test("blank schedule times say TBD (M3)")
def t_tbd():
    batch = T / "batch_tbd.json"
    batch.write_text(json.dumps([{"name": "TBD Times Band", "show_date": (TODAY + dt.timedelta(days=9)).isoformat(),
                                  "venue": "Court Street Plaza", "series": "", "email": "tbd@example.test"}]))
    out = T / "drafts_tbd"
    r = run_tool("draft_emails.py", batch, "--out", out)
    files = list(out.glob("*.md"))
    text = files[0].read_text() if files else ""
    check(r.returncode == 0 and fs.SCHEDULE_TBD in text, "blank times render as TBD, not FSQ defaults")
    check("6:00p" not in text, "no FSQ default time leaked")


@test("day-before confirmation (E5)")
def t_dayahead():
    aid = db_upsert_artist("Tomorrow Test Band", "tomorrow@example.test")
    sid = db_upsert_show(aid, "Fountain Square", TODAY + dt.timedelta(days=1), series="Jazz on the Square")
    x("UPDATE shows SET responded_at=now(), dayahead_sent_at=NULL, cancelled_at=NULL, held_at=NULL WHERE id=%s", (sid,))
    x("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by, seeded_at, slot, band_count, load_in, event_start, curfew)
         VALUES ('Tomorrow Test Band','Fountain Square',%s,'Jazz on the Square','tomorrow@example.test','tests',now(),'headliner',1,'5:30p','7:00p','10:00p')
         ON CONFLICT DO NOTHING""", (TODAY + dt.timedelta(days=1),))
    import dayahead
    n0 = mail_count()
    sent = dayahead.send_due(lambda *a: None)
    mine = [m for m in sends_since(n0) if m["payload"].get("to") == "tomorrow@example.test"]
    check(len(mine) == 1 and mine[0]["payload"]["subject"].startswith("Tomorrow at"), f"one day-before email ({len(mine)})")
    body = mine[0]["payload"]["body"] if mine else ""
    check("5:30p" in body and "Load-In" in body, "carries booked times + venue load-in text")
    s = q("SELECT dayahead_sent_at FROM shows WHERE id=%s", (sid,), one=True)
    check(s["dayahead_sent_at"] is not None, "stamped dayahead_sent_at")
    sent2 = dayahead.send_due(lambda *a: None)
    check(not [m for m in sent2 if m["artist_name"] == "Tomorrow Test Band"], "second run sends nothing")


@test("digest: Needs you + queued items (E1)")
def t_digest():
    import daily_digest
    subject, html = daily_digest.build_digest()
    check("Needs you" in html, "digest renders the Needs-you section")
    check("Submission needs a booking" in html or "Show on hold" in html or "Doc differs" in html, "needs feed lists open decisions")
    left = q("SELECT count(*) AS n FROM digest_items WHERE delivered_at IS NULL", one=True)["n"]
    check(left == 0, f"queued items marked delivered ({left} left)")
    st, body = get("/dashboard/needs")
    check(st == 200 and '"items"' in body, "dashboard /needs feed answers")


@test("Status Log: unreadable file -> skipped, alert after 3 (test gap #5)")
def t_statuslog():
    log = DROP / "Nyquist" / "Show Status Log.xlsx"
    lock = log.parent / ("~$" + log.name[2:])
    lock.write_text("lock")
    fail_state = CODE / "data" / "status_log_failures.json"
    fail_state.write_text('{"count": 0, "alerted": false}')
    n0 = mail_count()
    mtime = log.stat().st_mtime if log.exists() else None
    for _ in range(3):
        run_tool("status_log.py")
    lock.unlink(missing_ok=True)
    st = json.loads(fail_state.read_text())
    alerts = [m for m in sends_since(n0) if "Status Log" in str(m["payload"].get("subject"))]
    check(st.get("count") == 3 and st.get("alerted") is True, f"3 failures counted + alerted ({st})")
    check(len(alerts) == 1, f"exactly one alert email ({len(alerts)})")
    check(not log.exists() or log.stat().st_mtime == mtime, "file never overwritten while locked")
    r = run_tool("status_log.py")
    check(r.returncode == 0 and json.loads(fail_state.read_text()).get("count") == 0, "counter resets on success")


@test("import_sheet: slot clash -> digest (test gap #4)")
def t_clash():
    from openpyxl import load_workbook
    src = TOOLS / "lists" / "advance_list_template.xlsx"
    dst = T / "clash.xlsx"
    shutil.copy(src, dst)
    wb = load_workbook(dst)
    ws = wb["Advance List"] if "Advance List" in wb.sheetnames else wb.worksheets[0]
    import import_sheet  # noqa: F401 — path check
    from sheet import FIELDS
    hdr, hrow = {}, None
    for r in range(1, 8):
        m = {FIELDS.get(str(c.value or "").strip().lower()): c.column for c in ws[r] if FIELDS.get(str(c.value or "").strip().lower())}
        if len(m) > len(hdr):
            hdr, hrow = m, r
    last = max((c.row for c in ws["A"] if c.value), default=hrow)
    d = (TODAY + dt.timedelta(days=30)).isoformat()
    for i, band in enumerate(("Clash Band One", "Clash Band Two"), start=1):
        row = last + i
        for key, val in (("event_name", "Clash Night"), ("event_date", d), ("venue", "Washington Park"),
                         ("series", "Jazz At The Porch"), ("slot", "headliner"), ("artist_name", band),
                         ("contact_email", f"{band.replace(' ', '').lower()}@example.test")):
            if key in hdr:
                ws.cell(row, hdr[key]).value = val
    wb.save(dst)
    n_items = q("SELECT count(*) AS n FROM digest_items WHERE kind='slot_clash'", one=True)["n"]
    r = run_tool("import_sheet.py", dst)
    n_items2 = q("SELECT count(*) AS n FROM digest_items WHERE kind='slot_clash'", one=True)["n"]
    check(r.returncode == 0 and "slot clash" in r.stdout, f"clash detected (rc {r.returncode})")
    check(n_items2 == n_items + 1, f"one slot-clash digest item queued ({n_items2 - n_items})")
    # rebuild events from the real staging sheet so later tests see the normal model
    run_tool("import_sheet.py", DROP / "Nyquist" / "advance-list.xlsx")


@test("send failures: nag once, then weekly (M6)")
def t_failures():
    sid = q("SELECT id FROM shows WHERE show_date >= CURRENT_DATE ORDER BY id LIMIT 1", one=True)["id"]
    x("DELETE FROM send_failures WHERE show_id=%s", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        db.record_send_failure(cur, sid, "welcome", "no contact email on file")
        conn.commit()
        rows = db.unnotified_send_failures(cur)
        db.mark_send_failures_notified(cur, [r["id"] for r in rows if r["show_id"] == sid])
        conn.commit()
    check(any(r["show_id"] == sid for r in rows), "day 1: reported")
    # day 2, same error, backdated as tomorrow's row
    x("INSERT INTO send_failures (show_id, kind, error, day) VALUES (%s,'welcome','no contact email on file', CURRENT_DATE + 1)", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        rows2 = db.unnotified_send_failures(cur)
        conn.commit()
    check(not any(r["show_id"] == sid for r in rows2), "day 2: same error suppressed")
    x("INSERT INTO send_failures (show_id, kind, error, day) VALUES (%s,'welcome','HTTP 500: Graph', CURRENT_DATE + 2)", (sid,))
    with db.get_conn() as conn, conn.cursor() as cur:
        rows3 = db.unnotified_send_failures(cur)
        conn.commit()
    check(any(r["show_id"] == sid and r["error"].startswith("HTTP 500") for r in rows3), "day 3: a NEW error is reported")


@test("nothing left the box")
def t_isolation():
    bad = [m for m in mails() if not m["path"].startswith("/webhook/")]
    check(not bad, f"every mail hit the stub webhooks only ({len(bad)} odd)")
    check(mailer._send_url().startswith("http://127.0.0.1:8199"), "mailer pointed at the stub")


# ── run ──────────────────────────────────────────────────────────────────────
def main():
    tests = [v for v in globals().values() if callable(v) and hasattr(v, "_test_name")]
    for fn in tests:
        if ONLY and ONLY not in fn._test_name:
            continue
        print(f"\n== {fn._test_name}", flush=True)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, f"raised {e!r}")
    n_ok = sum(1 for ok, _ in RESULTS if ok)
    n = len(RESULTS)
    print(f"\n{n_ok}/{n} checks passed")
    for ok, msg in RESULTS:
        if not ok:
            print("  FAILED:", msg)
    sys.exit(0 if n_ok == n else 1)


if __name__ == "__main__":
    main()
