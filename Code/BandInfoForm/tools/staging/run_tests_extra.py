#!/opt/band-advance/venv/bin/python3
"""Extra staging tests for the 2026-09-16 work (merged edit page, band answers
on the booking form, docmerge column drift, fill_engineer anchor, played_within
exclusion, purge + rerun, ambiguous clock times, late-booking path).

Promoted from Handoffs/band-advance-audit-2026-09-16/run_tests_extra.py into
tools/staging/ (audit ops #4) — this is now the real, run-from-here copy.

x-d and x-g were xfail until root causes B (docmerge column-position
provenance) and A (purge/merge/rename never touch the sheet) landed — both
fixed 2026-09-16 (Opus session); x-j (rename) and x-k (merge) were added with
A, x-l onward with B. x-h was rewritten instead of left
xfail: root cause C (bare clock times) WAS fixed in this same batch (item
20), so the old test — which asserted the buggy behavior — no longer
describes what should happen; it now checks the fix directly.

x-t onward check the 2026-09-21 audit sweep's fixes, one test per fix (or
per tight group), each named for its finding id in a comment. The series ran
past x-y, so it continues x-aa, x-ab, ...; x-z stays the last test. Use a
trailing colon to -k one exactly ("-k x-a:" vs "-k x-aa"). Tests that need
a code path gunicorn doesn't expose (booking_update, dayahead,
finalize_thankyou timeouts) call the tool in-process and patch mailer.send
in THIS process only; the staging app and its stub are never touched.

Runs ON THE VM against the clone, after `set -a; . ~/advtest/advtest.env; set +a`.
Imports the helpers from tools/staging/run_tests.py (same dir on sys.path).
Every test records how many stub sends it produced, printed at the end.

    /opt/band-advance/venv/bin/python ~/advtest/run_tests_extra.py [-k name]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "advtest" / "code" / "tools" / "staging"))
sys.argv, _saved = [sys.argv[0]], sys.argv          # keep run_tests' -k parser quiet
from run_tests import *  # noqa: E402,F401,F403
import run_tests as rt  # noqa: E402
sys.argv = _saved
ONLY_X = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "-k" else None

MAIL_PER_TEST = {}


def no_redirect_get(path):
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    op = urllib.request.build_opener(NoRedir, urllib.request.HTTPCookieProcessor(rt.jar))
    try:
        with op.open(APP + path, timeout=60) as r:
            return r.status, r.headers.get("Location"), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), e.read().decode()


def booking_data(band, venue, d, set_start, set_end="22:30", series="Jazz on the Square", **kw):
    data = {"artist_name": band, "venue": venue, "event_date": d.isoformat(), "series": series,
            "contact_name": "Test Contact", "contact_email": f"{re.sub('[^a-z]', '', band.lower())}@example.test",
            "entered_by": "tests", "set_start": set_start, "set_end": set_end}
    data.update(kw)
    return data


def show_for(band, venue, d):
    return q("""SELECT s.* FROM shows s JOIN artists a ON a.id=s.artist_id
                WHERE a.match_key=%s AND s.venue=%s AND s.show_date=%s ORDER BY s.id DESC LIMIT 1""",
             (db.normalize(band), venue, d), one=True)


def booking_for(band, venue, d):
    return q(r"""SELECT * FROM bookings WHERE venue=%s AND event_date=%s
                 AND lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g')))=%s ORDER BY id DESC LIMIT 1""",
             (venue, d, db.normalize(band)), one=True)


def clear_date(venue, d):
    """Staging clones live bookings; keep a test date's bill to this test's acts."""
    x("UPDATE shows SET responded_at=COALESCE(responded_at, now()) WHERE venue=%s AND show_date=%s", (venue, d))


def sends_to(n0, email):
    return [m for m in sends_since(n0) if (m["payload"].get("to") or "").lower() == email.lower()]


# ── (a) merged edit page ─────────────────────────────────────────────────────
@test("x-a: merged edit page GET/POST /show/<id>/edit")
def tx_edit_page():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=30), "Merge Edit Band"
    email = "mergeeditband@example.test"
    base = booking_data(band, venue, d, "19:11", "20:11", event_start="7:11p", event_end="8:11p",
                        monitors="3", stage_type="Flat stage", performers="4",
                        own_engineer="No — use house engineers", backline="two combo amps",
                        contact_phone="555-0199", stage_plot_desc="drums center")
    st, _ = post("/booking", base)
    check(st == 200, f"booking with band answers created ({st})")
    check(wait_run_now(), "booking run finished")
    b = booking_for(band, venue, d)
    s = show_for(band, venue, d)
    check(b and s, f"booking + show rows exist (b={bool(b)} s={bool(s)})")
    if not (b and s):
        return
    sid, bid = s["id"], b["id"]
    st, html = get(f"/show/{sid}/edit")
    check(st == 200 and "Edit Show" in html and f'action="/show/{sid}/edit"' in html,
          f"edit page renders as Edit Show and posts to itself ({st})")
    for name in ("event_name", "event_date", "venue", "location", "series", "lead_name", "lead_phone",
                 "load_in", "soundcheck", "event_start", "event_end", "curfew", "set_time", "set_start",
                 "set_end", "artist_name", "contact_name", "contact_email", "email_note", "entered_by",
                 "skip_welcome_email", "draft_only", "band_emails",
                 "contact_phone", "performers", "stage_type", "monitors", "uses_iems", "iem_count",
                 "own_iems", "split_snake", "own_engineer", "merch", "band_tent", "vehicle_count",
                 "large_vehicle_count", "backline", "scenic", "lighting", "stage_plot_desc",
                 "additional", "stage_escort_name", "stage_escort_cell", "ack_loadin", "ack_95db",
                 "ack_reqs", "stage_plot_file"):
        if f'name="{name}"' not in html:
            check(False, f"field {name} missing from the merged edit page")
    check('name="set_start" id="set_start_input" value="19:11"' in html, "set_start prefilled 19:11")
    # editable on /show/<id>/edit again (Brian, 2026-09-19) — one named
    # input, no disabled twin, no hidden shadow copy
    check(f'name="artist_name" id="artist_name_input" value="{band}"' in html
          and 'type="hidden" name="artist_name"' not in html, "artist prefilled and editable")
    check(f'name="event_date" value="{d.isoformat()}" required>' in html, "event date editable")
    check('<select name="venue" id="venue_select"' in html, "venue editable")
    check(f'value="{d.isoformat()}"' in html, "date prefilled")
    check('name="monitors" min="0" step="1" value="3"' in html, "monitors prefilled from the band-answers submission")
    check('value="Flat stage" selected' in html, "stage_type prefilled")
    check('value="No — use house engineers" selected' in html, "own_engineer prefilled")
    check('<textarea name="backline">two combo amps</textarea>' in html, "backline prefilled")
    check('name="contact_phone" value="555-0199"' in html, "contact_phone prefilled")
    check('id="draft_only" style="width:auto;margin-top:2px" checked' not in html, "draft_only unchecked")
    check('<option value="Jazz on the Square" selected' in html, "series prefilled")
    # /booking/<id>/edit redirects into the merged page
    st, loc, _ = no_redirect_get(f"/booking/{bid}/edit")
    check(st == 302 and loc and loc.endswith(f"/show/{sid}/edit"), f"/booking/{bid}/edit -> {st} {loc}")

    # POST a change: set_start, monitors, draft_only
    x("UPDATE shows SET advance_held_draft_at=now() WHERE id=%s", (sid,))  # pretend a draft is held
    n0 = mail_count()
    changed = dict(base, set_start="19:41", set_end="20:41", event_start="", event_end="",
                   load_in="", soundcheck="", set_time="", monitors="5", draft_only="on")
    st, html = post(f"/show/{sid}/edit", changed)
    # 2026-09-21 sweep (TEST-5): was `... or st == 200`; show_edit's success page says "Booking updated"
    check(st == 200 and "Booking updated" in html, f"save answered ({st})")
    b2 = booking_for(band, venue, d)
    check(b2["id"] == bid, "same booking row updated, no twin")
    check(b2["event_start"] == "7:41p" and b2["load_in"] == "6:41p", f"schedule re-derived ({b2['event_start']}, {b2['load_in']})")
    check(b2["draft_only"] is True, "draft_only persisted")
    check(b2["sheet_dirty"] is True, f"sheet_dirty set ({b2['sheet_dirty']})")
    sub = q("SELECT * FROM submissions WHERE artist_id=%s ORDER BY id DESC LIMIT 1", (s["artist_id"],), one=True)
    check(sub and sub["show_id"] == sid and sub["source"] == "staff" and (sub["data"] or {}).get("monitors") == "5",
          f"new staff submission on this show with monitors 5 ({sub and sub['data'].get('monitors')})")
    n_subs = q("SELECT count(*) AS n FROM submissions WHERE artist_id=%s", (s["artist_id"],), one=True)["n"]
    check(n_subs == 2, f"two submissions on file (booking + edit) ({n_subs})")
    mm = q("SELECT * FROM submission_matches WHERE submission_id=%s", (sub["id"],))
    check(not mm, "resolve_booking=False: no submission_matches row")
    held = q("SELECT advance_held_draft_at FROM shows WHERE id=%s", (sid,), one=True)["advance_held_draft_at"]
    check(held is not None, "ticking draft_only leaves a held draft stamp alone")
    be = q("SELECT changes, notify FROM booking_edits WHERE booking_id=%s ORDER BY id DESC LIMIT 1", (bid,), one=True)
    check(be and be["changes"].get("event_start") == {"old": "7:11p", "new": "7:41p"} and be["notify"] is False,
          f"band-facing diff recorded, no notify outside the 21-day window ({be})")
    # un-tick draft_only -> held stamp cleared
    check(wait_run_now(), "edit run finished")
    untick = dict(changed); untick.pop("draft_only")
    st, _ = post(f"/show/{sid}/edit", untick)
    held = q("SELECT advance_held_draft_at FROM shows WHERE id=%s", (sid,), one=True)["advance_held_draft_at"]
    check(st == 200 and held is None, f"un-ticking draft_only clears advance_held_draft_at ({held})")
    n_subs2 = q("SELECT count(*) AS n FROM submissions WHERE artist_id=%s", (s["artist_id"],), one=True)["n"]
    check(n_subs2 == n_subs, f"re-save with unchanged answers files no duplicate submission ({n_subs2})")
    check(wait_run_now(), "second edit run finished")
    MAIL_PER_TEST["x-a"] = sends_since(n0)


# ── (b) show with no booking row ─────────────────────────────────────────────
@test("x-b: edit page for a pure band submission (no booking row)")
def tx_no_booking():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=31), "Pure Sub Band"
    clear_date(venue, d)
    n0 = mail_count()
    st, _ = submit_form(band, venue, d, monitors="2", extra={"show_series": "Jazz on the Square"})
    check(st == 200 and wait_regen(), f"band submission accepted ({st})")
    s = show_for(band, venue, d)
    check(s is not None, "show row exists from the submission")
    if not s:
        return
    check(booking_for(band, venue, d) is None, "no booking row yet")
    st, html = get(f"/show/{s['id']}/edit")
    check(st == 200 and f'name="artist_name" id="artist_name_input" value="{band}"' in html,
          f"edit page loads without a booking ({st})")
    check('name="monitors" min="0" step="1" value="2"' in html, "band's own monitors answer prefilled")
    check('<option value="Jazz on the Square" selected' in html, "series taken from the show")
    data = booking_data(band, venue, d, "20:15", "21:15", contact_email="puresubband@example.test",
                        monitors="2", stage_type="Flat stage", own_engineer="No — use house engineers",
                        performers="4", stage_plot_desc="3-piece, drums center", contact_phone="555-0100",
                        # echo back exactly what the band's own form posted (the merged page
                        # prefills all of these, so a real Save round-trips them unchanged)
                        own_iems="No", merch="No", band_tent="No, not needed", vehicle_count="2",
                        large_vehicle_count="0", ack_loadin="yes", ack_95db="yes", ack_reqs="yes")
    st, html = post(f"/show/{s['id']}/edit", data)
    b = booking_for(band, venue, d)
    check(st == 200 and b is not None, f"first save created the booking ({st}, {bool(b)})")
    check(b and b["event_start"] == "8:15p" and b["series"] == "Jazz on the Square", f"booking carries the schedule ({b and b['event_start']})")
    n_subs = q("SELECT count(*) AS n FROM submissions WHERE show_id=%s", (s["id"],), one=True)["n"]
    check(n_subs == 1, f"unchanged answers -> no duplicate submission ({n_subs})")
    check(wait_run_now(), "run finished")
    st, loc, _ = no_redirect_get(f"/booking/{b['id']}/edit")
    check(st == 302 and loc.endswith(f"/show/{s['id']}/edit"), "new booking's edit link redirects to the merged page")
    MAIL_PER_TEST["x-b"] = sends_since(n0)


# ── (c) band answers before artist/show rows exist ───────────────────────────
@test("x-c: band answers on a brand-new booking attach to the right show, no false notice")
def tx_answers_first():
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=33)
    # a decoy: another unresponded booked show on the same bill (the case that
    # produced the false "needs a booking" notice)
    st, _ = post("/booking", booking_data("Decoy Bill Mate", venue, d, "21:00", "22:00"))
    check(st == 200 and wait_run_now(), "decoy bill-mate booked")
    band = "Fresh Answers Band"
    n_match = q("SELECT count(*) AS n FROM submission_matches", one=True)["n"]
    n_digest = q("SELECT count(*) AS n FROM digest_items WHERE kind='match'", one=True)["n"]
    n0 = mail_count()
    st, _ = post("/booking", booking_data(band, venue, d, "19:30", "20:30", monitors="4",
                                          stage_type="Drum riser", performers="5"))
    check(st == 200, f"booking with answers ({st})")
    # synchronous part: record_submission already ran inside the request
    s = show_for(band, venue, d)
    sub = q("SELECT * FROM submissions WHERE show_id=%s", (s["id"],)) if s else []
    check(s and len(sub) == 1 and sub[0]["source"] == "staff", f"submission attached to the band's own new show ({s and s['id']}, {len(sub)})")
    check(q("SELECT count(*) AS n FROM submission_matches", one=True)["n"] == n_match, "no submission_matches row")
    check(q("SELECT count(*) AS n FROM digest_items WHERE kind='match'", one=True)["n"] == n_digest, "no 'match' digest item")
    decoy = show_for("Decoy Bill Mate", venue, d)
    check(decoy and decoy["responded_at"] is None, "decoy show NOT stamped responded")
    with db.get_conn() as conn, conn.cursor() as cur:
        needs = [n for n in db.needs_attention(cur) if n["kind"] == "match" and (band in n["detail"] or "Decoy" in n["detail"])]
    check(not needs, f"no 'Submission needs a booking' for either band ({needs})")
    check(wait_run_now(), "run finished")
    s2 = show_for(band, venue, d)
    check(s2 and s2["id"] == s["id"], "run_now kept the same show row")
    n_shows = q("SELECT count(*) AS n FROM shows s JOIN artists a ON a.id=s.artist_id WHERE a.match_key=%s", (db.normalize(band),), one=True)["n"]
    check(n_shows == 1, f"exactly one show for the artist ({n_shows})")
    acts = q("""SELECT ea.artist_id FROM event_acts ea JOIN events e ON e.id=ea.event_id
                WHERE e.venue=%s AND e.event_date=%s""", (venue, d))
    check(any(a["artist_id"] == s["artist_id"] for a in acts), "artist is on the bill")
    rows, _ = doc_rows(venue, d, band)
    check(rows and rows.get("Monitors") == "4 wedges", f"doc column carries the booking-form answer ('{rows and rows.get('Monitors')}')")
    MAIL_PER_TEST["x-c"] = sends_since(n0)


# ── (d) docmerge column drift ────────────────────────────────────────────────
def _grid_cells(venue, d):
    """{(row label, col idx): text} straight from the filed doc + header names."""
    from docx import Document
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    doc = Document(str(DROP / reg["path"]))
    grid = daysheet.find_grid(doc)
    names = {}
    for r in grid.rows:
        if not r.cells[0].text.strip():
            for i, c in enumerate(r.cells[1:], start=1):
                names[i] = c.text.strip()
            break
    out = {}
    for r in grid.rows:
        lab = daysheet.norm(r.cells[0].text)
        for i, c in enumerate(r.cells[1:], start=1):
            out[(lab, i)] = daysheet.full_cell_text(c).strip()
    return names, out, Path(reg["path"]).name


def _notice_count(venue, d):
    return q("SELECT count(*) AS n FROM doc_notices WHERE venue=%s AND event_date=%s AND kind='diff'",
             (venue, d), one=True)["n"]


def _col_of(names, band):
    return next((i for i, n in names.items() if band in n), None)


@test("x-d: docmerge column drift — an earlier act joins a filed bill, then a 4th act")
def tx_column_drift():
    # root cause B (audit 2026-09-16), fixed 2026-09-16 (Opus): cells are keyed
    # by artist and physically follow their artist when the bill reorders; a
    # 4th act is left off the doc with a Bill size notice (F9).
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=35)
    A, B, C, D = "Drift Act Alpha", "Drift Act Bravo", "Drift Act Charlie", "Drift Act Delta"
    post("/booking", booking_data(A, venue, d, "20:00", "20:45", monitors="4", backline="alpha amps", contact_phone="555-0001"))
    post("/booking", booking_data(B, venue, d, "21:00", "21:45", monitors="6", backline="bravo amps", contact_phone="555-0002"))
    check(wait_run_now(), "2-act bill filed")
    names, cells, fname = _grid_cells(venue, d)
    check(A in names.get(1, "") and B in names.get(2, ""), f"headers A,B ({names})")
    check(cells.get(("monitors", 1)) == "4 wedges" and cells.get(("monitors", 2)) == "6 wedges", "monitors under the right headers")
    reg = q("SELECT columns FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    sa, sb = show_for(A, venue, d), show_for(B, venue, d)
    check(reg and reg["columns"] == {"1": sa["artist_id"], "2": sb["artist_id"]}, f"filed_docs.columns records the map ({reg and reg['columns']})")
    n_not = _notice_count(venue, d)
    n0 = mail_count()

    # d1: a 3rd act with an EARLIER start, NO band answers (review=False path)
    post("/booking", booking_data(C, venue, d, "19:00", "19:45"))
    check(wait_run_now(), "3-act run finished")
    names, cells, fname = _grid_cells(venue, d)
    check(C in names.get(1, "") and A in names.get(2, "") and B in names.get(3, ""), f"headers now C,A,B ({names})")
    ok_cells = (cells.get(("monitors", 2)) == "4 wedges" and cells.get(("monitors", 3)) == "6 wedges"
                and not cells.get(("monitors", 1)))
    check(ok_cells, f"d1 monitors follow their artist: col1={cells.get(('monitors',1))!r} col2={cells.get(('monitors',2))!r} col3={cells.get(('monitors',3))!r}")
    bl = (cells.get(("backline", 2)), cells.get(("backline", 3)))
    check("alpha" in (bl[0] or "").lower() and "bravo" in (bl[1] or "").lower(), f"d1 backline follows its artist {bl}")
    check(not cells.get(("band contact — cell", 1)), f"d1 C's contact cell is not A's number ({cells.get(('band contact — cell', 1))!r})")
    n_not1 = _notice_count(venue, d)
    check(n_not1 == n_not, f"d1: zero new doc_notices for unchanged data ({n_not1 - n_not} new)")
    for r in q("SELECT field, doc_value, new_value FROM doc_notices WHERE venue=%s AND event_date=%s AND resolved_at IS NULL", (venue, d)):
        print(f"      notice: {r['field']!r}: doc={r['doc_value']!r} new={r['new_value']!r}")
    rows_a, _ = doc_rows(venue, d, A)
    rows_b, _ = doc_rows(venue, d, B)
    check(rows_a and rows_a.get("Monitors") == "4 wedges" and rows_b and rows_b.get("Monitors") == "6 wedges",
          f"read_filed_advance by artist: A={rows_a and rows_a.get('Monitors')} B={rows_b and rows_b.get('Monitors')}")

    # d2: a 4th act, EARLIER still, WITH band answers — D,C,A on the doc, B
    # (latest start) doesn't fit the 3-column template: a Bill size notice,
    # never folded onto column 3
    n_not = n_not1
    post("/booking", booking_data(D, venue, d, "18:00", "18:45", monitors="2", backline="delta keys"))
    check(wait_run_now(), "4-act run finished")
    names, cells, fname = _grid_cells(venue, d)
    print(f"      headers after D: {names}")
    ca, cb, cc, cd = (_col_of(names, X) for X in (A, B, C, D))
    check((cd, cc, ca, cb) == (1, 2, 3, None), f"d2: D,C,A on the doc, B off it (D={cd} C={cc} A={ca} B={cb})")
    check(cells.get(("monitors", 3)) == "4 wedges", f"d2: column 3 is A's, not overwritten by B ({cells.get(('monitors', 3))!r})")
    check(cells.get(("monitors", 1)) == "2 wedges", f"d2: D's monitors under D's header ({cells.get(('monitors', 1))!r})")
    check("bravo" not in " ".join(v for (lab, i), v in cells.items() if v).lower(), "d2: none of B's answers on the doc")
    n_not2 = _notice_count(venue, d)
    check(n_not2 == n_not, f"d2: zero new diff notices for unchanged data ({n_not2 - n_not} new)")
    size = q("SELECT * FROM doc_notices WHERE venue=%s AND event_date=%s AND kind='bill_size'", (venue, d))
    check(size and B in size[0]["new_value"], f"d2: Bill size notice names the act left off ({[x['new_value'] for x in size]})")
    MAIL_PER_TEST["x-d"] = sends_since(n0)


# ── (l) hand edit travels with its artist ───────────────────────────────────
def _edit_doc_cell(venue, d, label, col, text):
    from docx import Document
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    path = DROP / reg["path"]
    doc = Document(str(path))
    for r in daysheet.find_grid(doc).rows:
        if daysheet.norm(r.cells[0].text) == label:
            daysheet.set_cell(r.cells[col], text)
            break
    doc.save(str(path))


@test("x-l: 1-act doc, hand edit, earlier act added — the edit travels, column 1 is clean, no notices")
def tx_hand_edit_travels():
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=37)
    A, B = "Travel Act Alpha", "Travel Act Bravo"
    post("/booking", booking_data(A, venue, d, "20:00", "20:45", monitors="4", contact_phone="555-0101", backline="two amps"))
    check(wait_run_now(), "1-act doc filed")
    _edit_doc_cell(venue, d, "backline", 1, "two amps + Brian's spare DI")
    n_not = _notice_count(venue, d)
    post("/booking", booking_data(B, venue, d, "19:00", "19:45"))
    check(wait_run_now(), "2-act run finished")
    names, cells, _ = _grid_cells(venue, d)
    check(B in names.get(1, "") and A in names.get(2, ""), f"headers B,A ({names})")
    check(not cells.get(("monitors", 1)) and not cells.get(("band contact — cell", 1)) and not cells.get(("backline", 1)),
          f"column 1 carries none of A's values ({cells.get(('monitors', 1))!r}, {cells.get(('band contact — cell', 1))!r}, {cells.get(('backline', 1))!r})")
    check(cells.get(("backline", 2)) == "two amps + Brian's spare DI", f"hand edit moved with A ({cells.get(('backline', 2))!r})")
    check(cells.get(("monitors", 2)) == "4 wedges" and cells.get(("band contact — cell", 2)) == "555-0101", "A's answers under A")
    check(_notice_count(venue, d) == n_not, f"zero new notices ({_notice_count(venue, d) - n_not})")
    r = run_tool("run_now.py")
    names2, cells2, _ = _grid_cells(venue, d)
    check(r.returncode == 0 and cells2 == cells and _notice_count(venue, d) == n_not, "a second pass changes nothing")


# ── (m) cancelled act returns its column to the template ────────────────────
@test("x-m: cancelling an act gives its column back to the template")
def tx_cancel_retracts():
    # daysheet.py never fills a cancelled act's cells (Brian, 2026-09-17: the
    # act itself keeps its own column, header marked CANCELLED — see x-o for
    # the case where a new booking takes its exact slot instead), so the
    # column's VALUES must still read as template, not the cancelled band's
    # old answers under a blank header.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=39)
    A, B = "Retract Act Alpha", "Retract Act Bravo"
    post("/booking", booking_data(A, venue, d, "19:00", "19:45", monitors="3", backline="alpha kit", contact_phone="555-0201"))
    post("/booking", booking_data(B, venue, d, "20:00", "20:45", monitors="5", backline="bravo kit", contact_phone="555-0202"))
    check(wait_run_now(), "2-act doc filed")
    _names, cells, _ = _grid_cells(venue, d)
    check(cells.get(("monitors", 2)) == "5 wedges", "B filled")
    n_not = _notice_count(venue, d)
    sb = show_for(B, venue, d)
    post(f"/show/{sb['id']}/cancel")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "run after cancel")
    names, cells, _ = _grid_cells(venue, d)
    print(f"      headers after cancel: {names}")
    check("CANCELLED" in names.get(2, ""), f"col 2 header marks B cancelled, not blank/playing ({names.get(2)!r})")
    check(not cells.get(("monitors", 2)) and not cells.get(("backline", 2)) and not cells.get(("band contact — cell", 2)),
          f"B's column back to the template ({cells.get(('monitors', 2))!r}, {cells.get(('backline', 2))!r}, {cells.get(('band contact — cell', 2))!r})")
    check(cells.get(("monitors", 1)) == "3 wedges" and "alpha" in (cells.get(("backline", 1)) or ""), "A untouched")
    check(_notice_count(venue, d) == n_not, f"no notices from the retraction ({_notice_count(venue, d) - n_not})")


@test("x-o: a new booking into a cancelled act's exact slot takes over its column outright")
def tx_cancel_slot_takeover():
    # Brian, 2026-09-17: cancelling an artist keeps them on the bill (their
    # own column, header CANCELLED — x-m) right up until someone else is
    # booked into their exact venue+date+set-start, at which point the new
    # band replaces them outright — no leftover CANCELLED column sitting
    # next to the new act, nothing of the cancelled band's answers in reach.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=44)
    A, B, C = "Takeover Act Alpha", "Takeover Act Bravo", "Takeover Act Charlie"
    sta, _ = post("/booking", booking_data(A, venue, d, "19:00", "19:45", monitors="3", backline="alpha kit", contact_phone="555-0301"))
    stb, _ = post("/booking", booking_data(B, venue, d, "20:00", "20:45", monitors="5", backline="bravo kit", contact_phone="555-0302"))
    check(wait_run_now(), f"2-act doc filed (booking posts: {sta}, {stb})")
    sa = show_for(A, venue, d)
    check(sa is not None, f"Alpha's show exists before cancelling ({sa})")
    if not sa:
        return
    post(f"/show/{sa['id']}/cancel")
    check(run_tool("run_now.py").returncode == 0, "run after cancel")
    names, _cells, _ = _grid_cells(venue, d)
    check(any("CANCELLED" in n and "Alpha" in n for n in names.values())
          and any("Bravo" in n and "CANCELLED" not in n for n in names.values()),
          f"A still on the bill, cancelled; B untouched ({names})")
    # Charlie books the exact slot Alpha's show was cancelled from
    post("/booking", booking_data(C, venue, d, "19:00", "19:45", monitors="7", backline="charlie kit", contact_phone="555-0303"))
    check(wait_run_now(), "run after the takeover booking")
    n_acts = q("""SELECT count(*) AS n FROM event_acts ea JOIN events e ON e.id=ea.event_id
                  WHERE e.venue=%s AND e.event_date=%s""", (venue, d), one=True)["n"]
    check(n_acts == 2, f"still exactly 2 acts on the bill, not 3 ({n_acts})")
    names, cells, _ = _grid_cells(venue, d)
    print(f"      headers after takeover: {names}")
    check(not any("Alpha" in n for n in names.values()), f"Alpha is nowhere in the headers ({names})")
    check(any(C in n for n in names.values()), f"Charlie is on the bill ({names})")
    col_c = _col_of(names, C)
    check(cells.get(("monitors", col_c)) == "7 wedges", f"Charlie's own answers filled his column ({cells.get(('monitors', col_c))!r})")
    col_b = _col_of(names, B)
    check(cells.get(("monitors", col_b)) == "5 wedges", f"Bravo untouched ({cells.get(('monitors', col_b))!r})")


@test("x-p: an orphaned stage-plot hyperlink is cleared when a column's occupant changes")
def tx_orphan_hyperlink():
    # docmerge merges the fresh build (F) into the filed doc (E). A hyperlink
    # in a grid cell is only ever pipeline-written (set_cell_link, stage
    # plots) — when the fresh build has no plot for that column (its occupant
    # changed to a band with none), the stale link must be cleared, not kept
    # as if it were a hand edit. Brian, FSQ 9/18: LimeLght replaced Wishy in
    # column 2 but the doc kept a stale Jet Jurgensmeyer plot link there.
    import docmerge
    from docx import Document
    from docx.oxml.ns import qn

    def sp_cell(doc, col):
        grid = daysheet.find_grid(doc)
        for r in grid.rows:
            if daysheet.norm(r.cells[0].text) == "stage plot":
                return r.cells[col]
        return None

    def has_link(cell):
        return next(cell._tc.iter(qn("w:hyperlink")), None) is not None

    T = Document(str(daysheet.UNIVERSAL_TEMPLATE))
    E = Document(str(daysheet.UNIVERSAL_TEMPLATE))
    F = Document(str(daysheet.UNIVERSAL_TEMPLATE))

    # E: a stale stage-plot link left in column 2 by a dropped band
    daysheet.set_cell_link(sp_cell(E, 2), "See DB — dropped-band-stageplot.pdf",
                           "https://www.dropbox.com/scl/fi/x/dropped-band-stageplot.pdf?dl=1")
    check(has_link(sp_cell(E, 2)), "setup: E column 2 starts with a stage-plot hyperlink")

    # F (fresh build) has nothing in column 2 — the new occupant has no plot
    changed, _notices, _prov = docmerge.merge(T, F, E, cols={1: 11, 2: 22, 3: 33},
                                              old_cols={1: 11, 2: 22, 3: 33})
    check(not has_link(sp_cell(E, 2)), f"orphaned hyperlink cleared from column 2 (changed={changed})")
    check(not daysheet.full_cell_text(sp_cell(E, 2)).strip(),
          f"column 2 stage-plot cell reads blank ({daysheet.full_cell_text(sp_cell(E, 2))!r})")
    check(not has_link(sp_cell(E, 1)) and not has_link(sp_cell(E, 3)),
          "columns 1 and 3 (never linked) untouched")


# ── (n) conflicted copy ──────────────────────────────────────────────────────
@test("x-n: a Dropbox conflicted copy beside a filed doc or the sheet raises a notice")
def tx_conflicted_copy():
    login()
    venue, d, A = "Fountain Square", TODAY + dt.timedelta(days=41), "Conflict Copy Band"
    post("/booking", booking_data(A, venue, d, "19:00", "19:45", monitors="3"))
    check(wait_run_now(), "doc filed")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    doc = DROP / reg["path"]
    cc = doc.with_name(f"{doc.stem} (Andi Schultes's conflicted copy {TODAY.isoformat()}){doc.suffix}")
    sheet = DROP / "Nyquist" / "advance-list.xlsx"
    scc = sheet.with_name(f"advance-list (Brian Lloyd's conflicted copy {TODAY.isoformat()}).xlsx")
    shutil.copy(doc, cc)
    shutil.copy(sheet, scc)
    try:
        r = run_tool("run_now.py")
        check(r.returncode == 0, "run with conflicted copies present")
        n = q("SELECT * FROM doc_notices WHERE kind='conflict' AND cell_key=%s", (f"conflict:{cc.name}",))
        check(len(n) == 1, f"doc conflicted copy -> one notice ({len(n)})")
        ns = q("SELECT * FROM doc_notices WHERE kind='conflict' AND cell_key=%s", (f"conflict:{scc.name}",))
        check(len(ns) == 1, f"sheet conflicted copy -> one notice ({len(ns)})")
        run_tool("run_now.py")
        n2 = q("SELECT count(*) AS n FROM doc_notices WHERE kind='conflict' AND cell_key IN (%s, %s)",
               (f"conflict:{cc.name}", f"conflict:{scc.name}"), one=True)["n"]
        check(n2 == 2, f"a second run doesn't repeat them ({n2})")
    finally:
        cc.unlink(missing_ok=True)
        scc.unlink(missing_ok=True)


# ── (e) fill_engineer anchor ─────────────────────────────────────────────────
@test("x-e: fill_engineer anchors on the earliest real act's own set_start")
def tx_fill_engineer():
    from docx import Document
    captured = {}

    def fake(venue, date, series=None, event_name=None, artist_name=None, event_start=None):
        captured.update(venue=venue, date=date, artist_name=artist_name, event_start=event_start)
        return {"foh": "Fake FOH", "mon": None}

    real = daysheet.staffing.engineers_for
    daysheet.staffing.engineers_for = fake
    try:
        doc = Document(str(daysheet.UNIVERSAL_TEMPLATE))
        grid = daysheet.find_grid(doc)
        event = {"venue": "Fountain Square", "event_date": TODAY + dt.timedelta(days=40), "series": "Jazz on the Square",
                 "name": "Anchor Night", "details": {"event_start": "5:00p"}}
        acts = [{"artist": {"name": "Late Act"}, "artist_order": 2, "set_start": "9:00p"},
                {"artist": {"name": "Early Act"}, "artist_order": 1, "set_start": "8:00p"}]
        daysheet.fill_engineer(grid, event, 2, acts=acts)
        check(captured.get("event_start") == "8:00p" and captured.get("artist_name") == "Early Act",
              f"anchor = earliest act's own set_start, not event.details ({captured})")
        txt = "\n".join(c.text for r in grid.rows for c in r.cells if daysheet.norm(r.cells[0].text) == "engineer")
        check("FOH – Fake FOH" in txt, "engineer row written")
        captured.clear()
        acts[1]["_cancelled"] = True
        daysheet.fill_engineer(grid, event, 2, acts=acts)
        check(captured.get("event_start") == "9:00p", f"cancelled earliest act skipped ({captured})")
    finally:
        daysheet.staffing.engineers_for = real


# ── (f) played_within excludes the show being welcomed ───────────────────────
@test("x-f: a band whose only submission is for THIS show is NEW, not RETURNING")
def tx_played_within():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=12), "Only Show Band"
    email = "onlyshowband@example.test"
    for hhmm, house in (("19:23", "7:23p"), ("20:23", "8:23p"), ("21:23", "9:23p")):
        st, _ = post("/booking", booking_data(band, venue, d, hhmm, "22:00", event_start=house, monitors="3",
                                              stage_type="Flat stage", contact_email=email))
        if st == 200:
            break
    check(st == 200 and wait_run_now(), f"booked with answers ({st})")
    s = show_for(band, venue, d)
    with db.get_conn() as conn, conn.cursor() as cur:
        with_ex = db.played_within(cur, s["artist_id"], d, exclude_show_id=s["id"])
        without = db.played_within(cur, s["artist_id"], d)
    check(with_ex is None and without is not None, f"played_within: excluded -> None, not excluded -> hit ({bool(with_ex)}, {bool(without)})")
    n0 = mail_count()
    x("UPDATE shows SET advance_draft_created_at=NULL, responded_at=NULL WHERE id=%s", (s["id"],))
    st, body = post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    mine = sends_to(n0, email)
    check(len(mine) == 1, f"one welcome ({len(mine)})")
    text = mine[0]["payload"].get("body", "") if mine else ""
    check("Good to have you back" not in text and "what we have on file" not in text, "welcome is the NEW version, no recap")
    check("Welcome to" in text, "welcome text present")
    MAIL_PER_TEST["x-f"] = sends_since(n0)


# ── (g) purge then run_now ───────────────────────────────────────────────────
def sheet_rows_for(band, venue, d):
    from sheet import read_advance_sheet
    rows = read_advance_sheet(DROP / "Nyquist" / "advance-list.xlsx")
    return [r for r in rows if db.normalize(r.get("artist_name")) == db.normalize(band)
            and (r.get("venue") or "").strip().lower() == venue.lower()
            and (r.get("event_date") or "")[:10] == d.isoformat()]


@test("x-g: purge_show then run_now — sheet row deleted, doc retired, nothing comes back")
def tx_purge():
    # root cause A (audit 2026-09-16), fixed 2026-09-16 (Opus): purge writes a
    # sheet_removals tombstone, run_now deletes the sheet row before the
    # rebuild and renames the orphaned doc "PURGED - …".
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=36), "Purge Me Band"
    post("/booking", booking_data(band, venue, d, "19:00", "20:00", monitors="3", vehicle_count="2"))
    check(wait_run_now(), "booked + filed")
    check(len(sheet_rows_for(band, venue, d)) == 1, "booking reached the sheet")
    s = show_for(band, venue, d)
    sid, aid = s["id"], s["artist_id"]
    x("INSERT INTO fsq_parking_queue (artist_id, show_id, band, venue, show_date, vehicle_count) VALUES (%s,%s,%s,%s,%s,2)", (aid, sid, band, venue, d))
    reg_before = q("SELECT id, path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    check(reg_before, f"a doc was filed before the purge ({len(reg_before)})")  # 2026-09-21 sweep (TEST-5)
    n0 = mail_count()
    st, body = post(f"/show/{sid}/purge", json_body={"confirm_name": band.lower()})
    check(st == 200 and json.loads(body).get("ok"), f"purge answered ok ({st} {body[:120]})")
    check(q("SELECT 1 FROM shows WHERE id=%s", (sid,), one=True) is None, "shows row gone")
    check(not q("SELECT 1 FROM submissions WHERE show_id=%s", (sid,)), "submissions gone")
    check(booking_for(band, venue, d) is None, "booking row gone")
    check(not q("SELECT 1 FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d)), "filed_docs registry cleared (only act)")
    check(not q("SELECT 1 FROM event_acts WHERE artist_id=%s", (aid,)), "event_acts gone")
    check(not q("SELECT 1 FROM fsq_parking_queue WHERE show_id=%s", (sid,)), "fsq_parking_queue no longer points at the show")
    check(not q("SELECT 1 FROM digest_items WHERE link LIKE %s", (f"%/show/{sid}%",)), "no digest item links the show")
    tomb = q("SELECT * FROM sheet_removals WHERE venue=%s AND event_date=%s AND match_key=%s",
             (venue, d, db.normalize(band)), one=True)
    check(tomb is not None, "sheet_removals tombstone written")
    r = run_tool("run_now.py")
    check(r.returncode == 0, f"run_now after purge exits 0 ({r.stdout[-200:]}{r.stderr[-300:]})")
    check(wait_run_now(), "background run from the purge finished too")
    back = show_for(band, venue, d)
    check(back is None, f"purged show does NOT come back on the next run (found show {back and back['id']})")
    check(booking_for(band, venue, d) is None, "booking does not come back")
    check(not q("SELECT 1 FROM event_acts WHERE artist_id=%s", (aid,)), "event_acts stays clear")
    check(not sheet_rows_for(band, venue, d), "sheet row deleted")
    tomb = q("SELECT * FROM sheet_removals WHERE id=%s", (tomb["id"],), one=True)
    check(tomb["applied_at"] is not None, "tombstone stamped applied")
    for reg in reg_before:
        p = DROP / reg["path"]
        retired = p.with_name(f"PURGED - {p.name}")
        check(not p.exists() and retired.exists(), f"doc renamed PURGED in place ({retired.name})")
    reg_after = q("SELECT id, path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    check(not reg_after, f"no doc re-filed for the date ({[Path(x['path']).name for x in reg_after]})")
    r = run_tool("run_now.py")
    check(r.returncode == 0 and show_for(band, venue, d) is None, "second run: still gone")
    st, _ = post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    MAIL_PER_TEST["x-g"] = sends_since(n0)
    check(not [m for m in MAIL_PER_TEST["x-g"] if "purgemeband" in (m["payload"].get("to") or "")],
          "nothing sent to the purged band")


# ── (j) rename in place ──────────────────────────────────────────────────────
def _book_first_free(band, venue, d, email, times=(("19:17", "7:17p"), ("20:17", "8:17p"), ("21:17", "9:17p"))):
    st = None
    for hhmm, house in times:
        st, _ = post("/booking", booking_data(band, venue, d, hhmm, "22:00", event_start=house, contact_email=email))
        if st == 200:
            return hhmm, house
    check(False, f"couldn't book {band} on any free start ({st})")
    return None, None


@test("x-j: renaming a booked band moves its artist, show, sheet row and doc — no second welcome")
def tx_rename():
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=14)
    A, B, email = "Renamee Typpo Band", "Renamee Typo Band", "renamee@example.test"
    hhmm, house = _book_first_free(A, venue, d, email)
    if not hhmm:
        return
    check(wait_run_now(), "booked + filed")
    n0 = mail_count()
    post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    s = show_for(A, venue, d)
    check(s and s["advance_draft_created_at"], "welcomed under the typo name")
    check(any((m["payload"].get("subject") or "").startswith("Welcome") for m in sends_to(n0, email)),
          "the one welcome went out")
    b = booking_for(A, venue, d)
    check(daysheet.read_filed_advance(venue, d, A) is not None, "doc carries A")
    n1 = mail_count()
    st, _ = post(f"/booking/{b['id']}/edit",
                 booking_data(B, venue, d, hhmm, "22:00", event_start=house, contact_email=email))
    check(st == 200, f"rename saved ({st})")
    check(wait_run_now(), "run after the rename finished")
    arts = q("SELECT id, name FROM artists WHERE match_key IN (%s, %s)", (db.normalize(A), db.normalize(B)))
    check(len(arts) == 1 and arts[0]["name"] == B and arts[0]["id"] == s["artist_id"],
          f"one artist, renamed in place ({arts})")
    shows = q("SELECT * FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s", (s["artist_id"], venue, d))
    check(len(shows) == 1 and shows[0]["id"] == s["id"], f"one show, same id ({[x['id'] for x in shows]})")
    check(shows and shows[0]["advance_draft_created_at"] == s["advance_draft_created_at"], "welcome stamp intact")
    check(not sheet_rows_for(A, venue, d) and len(sheet_rows_for(B, venue, d)) == 1, "sheet row moved to the new name")
    check(daysheet.read_filed_advance(venue, d, B) is not None and daysheet.read_filed_advance(venue, d, A) is None,
          "filed doc names B, not A")
    check(not q("SELECT 1 FROM shows WHERE held_at IS NOT NULL AND id=%s", (s["id"],)), "show not held as an orphan")
    post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    welcomes = [m for m in sends_to(n1, email) if (m["payload"].get("subject") or "").startswith(("Welcome", "Bienvenidos"))]
    check(not welcomes, f"no second welcome ({len(welcomes)})")
    MAIL_PER_TEST["x-j"] = sends_since(n0)


# ── (k) merge a typo'd show into the real one ────────────────────────────────
@test("x-k: merge_shows — typo side's sheet row deleted, stamps carried, nothing resurrects")
def tx_merge():
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=15)
    A, B = "Mergee Typpo Act", "Zebra Crossing Quartet"
    email = "mergeetyppo@example.test"
    if not _book_first_free(A, venue, d, email, times=(("19:19", "7:19p"), ("20:19", "8:19p"), ("21:19", "9:19p")))[0]:
        return
    check(wait_run_now(), "typo booking filed")
    n0 = mail_count()
    post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    old = show_for(A, venue, d)
    check(old and old["advance_draft_created_at"], "typo show welcomed")
    st, _ = submit_form(B, venue, d, monitors="5")
    check(st in (200, 302), f"real band submits under the right name ({st})")
    wait_regen()
    new = show_for(B, venue, d)
    check(new is not None, "real show exists")
    if not (old and new):
        return
    st, _ = post(f"/show/{old['id']}/merge/{new['id']}")
    check(st in (200, 302), f"merge answered ({st})")
    check(show_for(A, venue, d) is None and booking_for(A, venue, d) is None, "typo show + booking gone")
    check(q("SELECT 1 FROM sheet_removals WHERE match_key=%s AND reason='merge'", (db.normalize(A),), one=True),
          "merge tombstone written")
    check(wait_run_now(), "run after merge finished")
    r = run_tool("run_now.py")
    check(r.returncode == 0, f"explicit run_now ok ({r.stderr[-300:]})")
    check(show_for(A, venue, d) is None, "typo show does not resurrect")
    check(not sheet_rows_for(A, venue, d), "typo sheet row deleted")
    new = show_for(B, venue, d)
    check(new and new["advance_draft_created_at"] == old["advance_draft_created_at"], "welcome stamp carried to the real show")
    n1 = mail_count()
    post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    welcomes = [m for m in sends_since(n1) if (m["payload"].get("subject") or "").startswith(("Welcome", "Bienvenidos"))
                and any(k in (m["payload"].get("to") or "") for k in ("mergee", "zebracrossing"))]
    check(not welcomes, f"no welcome to either side after the merge ({len(welcomes)})")
    MAIL_PER_TEST["x-k"] = sends_since(n0)


# ── (h) ambiguous clock times ────────────────────────────────────────────────
@test("x-h: bare clock times rejected at entry; same time spelled differently still clashes")
def tx_ampm():
    # audit 2026-09-16 root cause C: FIXED in this same batch (item 20),
    # unlike x-d/x-g. The original version of this test asserted the buggy
    # behavior itself (bare "7:00" silently reads as 7am) as a way to prove
    # the bug existed; now that _validate_booking_data rejects a bare
    # "H:MM" with no am/pm outright, that path can't be exercised through
    # /booking any more — rewritten to check the actual fix instead of
    # leaving this permanently xfail for a bug that's already gone.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=38)
    check(db.parse_clock("5:00") == 17 * 60,
          f"parse_clock: bare '5:00' (hour 1-6) now reads as PM -> {db.parse_clock('5:00')}")
    check(db.parse_clock("11:00") == 11 * 60,
          f"parse_clock: bare '11:00' (outside 1-6) stays literal 24h -> {db.parse_clock('11:00')}")
    n0 = mail_count()
    st1, _ = post("/booking", booking_data("Ampm Band One", venue, d, "19:00", "20:00", event_start="7:00"))
    check(st1 == 400, f"a bare event_start with no am/pm is refused at entry, not silently misread ({st1})")
    st2, _ = post("/booking", booking_data("Ampm Band Two", venue, d, "19:00", "20:00", event_start="7:00pm"))
    check(st2 == 200, f"an explicit am/pm event_start is accepted ({st2})")
    st3, _ = post("/booking", booking_data("Ampm Band Three", venue, d, "19:30", "20:30", event_start="7pm"))
    check(st3 == 409, f"same clock time under a different (but unambiguous) spelling still clashes ({st3})")
    MAIL_PER_TEST["x-h"] = sends_since(n0)


# ── (i) late booking ─────────────────────────────────────────────────────────
@test("x-i: late booking (5 days out) — pipeline runs, one welcome, no reminder")
def tx_late():
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=5), "Late Booking Band"
    email = "latebookingband@example.test"
    n0 = mail_count()
    st = None
    for hhmm, house in (("19:13", "7:13p"), ("20:13", "8:13p"), ("21:13", "9:13p")):
        st, html = post("/booking", booking_data(band, venue, d, hhmm, "22:00", event_start=house, contact_email=email))
        if st == 200:
            break
    # 2026-09-21 sweep (TEST-5): was `... or st == 200`; the page never said "within 21 days"
    check(st == 200 and "inside the 21-day window" in html, f"late booking accepted on the urgent path ({st})")
    check(wait_run_now(), "synchronous late-booking run finished")
    s = show_for(band, venue, d)
    check(s is not None, "show seeded by the run")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    # 2026-09-21 sweep (TEST-5): the old `or True` passed on any doc for the date, a clone's included
    check(daysheet.read_filed_advance(venue, d, band) is not None, f"filed doc for the date carries {band} ({len(reg)} registered)")
    after_run = sends_to(n0, email)
    print(f"      welcomes after run_now alone (LIFECYCLE_NOW_URL blank in staging): {len(after_run)}")
    n1 = mail_count()
    st, body = post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    mine = sends_to(n1, email)
    subs = [m["payload"]["subject"] for m in mine]
    check(len(mine) == 1 and not subs[0].startswith("Reminder"), f"exactly one send to the band and it's the welcome ({subs})")
    s = show_for(band, venue, d)
    check(s["advance_draft_created_at"] is not None, "show stamped advance_draft_created_at")
    tiers = {r["days_before"]: r["sent"] for r in q("SELECT days_before, sent FROM advance_reminders WHERE show_id=%s", (s["id"],))}
    check(tiers.get(7) is False and 3 not in tiers and 1 not in tiers, f"tier 7 pre-skipped, 3/1 open, none sent ({tiers})")
    n2 = mail_count()
    post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})
    check(not sends_to(n2, email), "second lifecycle run sends nothing more to the band")
    MAIL_PER_TEST["x-i"] = sends_since(n0)


@test("x-q: purging a ghost act does NOT delete an event another show still sits on")
def tx_purge_keeps_event():
    # 2026-09-17/18 (MANY on the FSQ 9/26 Moon Festival): a show only gets an
    # event_acts row when the sheet import puts it on a bill, so "this was the
    # last act on the event" did not mean "nothing is left on this date". The
    # ghost act was the ONLY act on a real event whose actual booking had no
    # act row — purging it took the real event and its filed doc with it.
    login()
    venue = "Fountain Square"
    # 2026-09-21 sweep (TEST-1): +41 is x-n's date, whose act shared this bill
    d = TODAY + dt.timedelta(days=42)
    ghost, real = "Ghost Act Band", "Real Booking Band"
    post("/booking", booking_data(real, venue, d, "19:41", "22:00", event_start="7:41p"))
    check(wait_run_now(), "real booking filed")
    post("/booking", booking_data(ghost, venue, d, "20:41", "22:00", event_start="8:41p"))
    check(wait_run_now(), "ghost booking filed")
    s_real, s_ghost = show_for(real, venue, d), show_for(ghost, venue, d)
    check(s_real and s_ghost, "both shows seeded")
    act = q("SELECT id, event_id FROM event_acts WHERE artist_id=%s", (s_ghost["artist_id"],), one=True)
    check(act is not None, "ghost has an event_acts row")
    event_id = act["event_id"]
    # every other act on the bill (the real booking, plus any clone or test
    # sharing it) loses its act row — exactly the state the live DB was in
    x("DELETE FROM event_acts WHERE event_id=%s AND artist_id<>%s", (event_id, s_ghost["artist_id"]))
    check(len(q("SELECT 1 FROM event_acts WHERE event_id=%s", (event_id,))) == 1,
          "ghost act is now the only act on the event")
    reg_before = q("SELECT id, path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    check(reg_before, f"a doc was filed before the purge ({len(reg_before)})")  # 2026-09-21 sweep (TEST-5)
    st, body = post(f"/show/{s_ghost['id']}/purge", json_body={"confirm_name": ghost.lower()})
    check(st == 200 and json.loads(body).get("ok"), f"purge answered ok ({st} {body[:120]})")
    check(q("SELECT 1 FROM shows WHERE id=%s", (s_ghost["id"],), one=True) is None, "ghost show gone")
    check(q("SELECT 1 FROM events WHERE id=%s", (event_id,), one=True) is not None,
          "the EVENT survives — another show still sits on that venue+date")
    check(json.loads(body)["summary"].get("event_kept") == event_id, "summary reports the event was kept")
    check(json.loads(body)["summary"].get("filed_doc_retired") is None, "no filed doc retired")
    reg_after = q("SELECT id, path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    check({r["id"] for r in reg_after} == {r["id"] for r in reg_before},
          f"the real booking's filed doc registry row is untouched ({len(reg_before)} -> {len(reg_after)})")
    check(show_for(real, venue, d) is not None, "real show untouched")
    for reg in reg_before:
        check((DROP / reg["path"]).exists(), f"doc still in place ({Path(reg['path']).name})")


# ── (r) the merged edit page can move and rename a finalized show ───────────
@test("x-r: a FINALIZED show renamed + moved from the merged edit page carries with it")
def tx_edit_unlocked():
    login()
    venue = "Fountain Square"
    d1, d2 = TODAY + dt.timedelta(days=40), TODAY + dt.timedelta(days=41)
    A, B, email = "Unlock Edit Band", "Unlock Edit Band Renamed", "unlockeditband@example.test"
    clear_date(venue, d1)
    clear_date(venue, d2)
    hhmm, house = _book_first_free(A, venue, d1, email,
                                   times=(("19:40", "7:40p"), ("20:40", "8:40p"), ("21:40", "9:40p")))
    if not hhmm:
        return
    check(wait_run_now(), "booked + filed")
    n0 = mail_count()
    st, _ = submit_form(A, venue, d1, monitors="3")
    check(st in (200, 302) and wait_regen(), f"band answered ({st})")
    s = show_for(A, venue, d1)
    if not s:
        check(False, "no show to finalize")
        return
    post(f"/artist/{s['artist_id']}/finalize/{s['id']}", {})
    fin = q("SELECT finalized_at FROM shows WHERE id=%s", (s["id"],), one=True)["finalized_at"]
    check(fin is not None, "show finalized")

    # the point of the test: every field is editable on a finalized show
    st, html = get(f"/show/{s['id']}/edit")
    check(st == 200 and f'name="artist_name" id="artist_name_input" value="{A}"' in html
          and 'type="hidden" name="artist_name"' not in html
          and '<select name="venue" id="venue_select"' in html
          and f'name="event_date" value="{d1.isoformat()}" required>' in html,
          "artist / venue / date all editable on a finalized show")

    st, _ = post(f"/show/{s['id']}/edit",
                 booking_data(B, venue, d2, "19:40", "22:00", event_start="7:40p", contact_email=email))
    check(st == 200, f"rename + move saved ({st})")
    check(wait_run_now(), "run after the move finished")

    moved = show_for(B, venue, d2)
    check(moved and moved["id"] == s["id"], f"same show id at the new date ({moved and moved['id']} vs {s['id']})")
    check(moved and moved["finalized_at"] is not None, "finalized stamp survived the move")
    check(moved and moved["advance_draft_created_at"] == s["advance_draft_created_at"], "welcome stamp intact")
    check(show_for(A, venue, d1) is None, "nothing left behind on the old date")
    check(not q("SELECT 1 FROM shows WHERE venue=%s AND show_date=%s AND artist_id=%s",
                (venue, d1, s["artist_id"])), "no forked twin on the old date")
    arts = q("SELECT id, name FROM artists WHERE match_key IN (%s, %s)", (db.normalize(A), db.normalize(B)))
    check(len(arts) == 1 and arts[0]["name"] == B and arts[0]["id"] == s["artist_id"],
          f"one artist, renamed in place ({arts})")
    subs = q("SELECT count(*) AS n FROM submissions WHERE show_id=%s", (s["id"],), one=True)["n"]
    check(subs >= 1, f"the band's answers came along ({subs})")
    check(not sheet_rows_for(A, venue, d1) and len(sheet_rows_for(B, venue, d2)) == 1,
          "sheet row moved to the new name and date")
    check(daysheet.read_filed_advance(venue, d2, B) is not None
          and daysheet.read_filed_advance(venue, d1, A) is None, f"doc filed under {B} on the new date")
    check(not q("SELECT 1 FROM shows WHERE held_at IS NOT NULL AND id=%s", (s["id"],)), "not held as an orphan")
    MAIL_PER_TEST["x-r"] = sends_since(n0)


@test("x-s: a doc/booking band-name clash raises an artist_name decision that renames everywhere")
def tx_artist_name_notice():
    # Brian, 2026-09-19 (FSQ 9/25 "Adopt a mini who dey"): the doc's act-name
    # cell said DJ DIAMOND, the booking, the filename and every other cell
    # said DJ TBD, and the only thing on offer was Keep doc / Use new — either
    # way the show stays half-renamed. This is now its own decision kind.
    login()
    venue = "Fountain Square"
    d = TODAY + dt.timedelta(days=43)
    booked, real = "DJ Placeholder", "DJ Realname"
    post("/booking", booking_data(booked, venue, d, "19:43", "22:00", event_start="7:43p"))
    check(wait_run_now(), "booking filed")
    rows, path = doc_rows(venue, d, booked)
    check(path is not None, "advance doc filed")
    # hand-edit the act-name cell to a different band name, the way Brian did
    from docx import Document
    doc = Document(str(path))
    grid = daysheet.find_grid(doc)
    hit = None
    for r in grid.rows:
        for c in r.cells[1:]:
            if booked.lower() in (c.text or "").lower() and "artist" in (c.text or "").lower():
                hit = c
    check(hit is not None, "found the act-name cell")
    if hit is None:
        return
    # edit ONLY the band-name paragraph — set_cell would flatten the cell to
    # one line, which is not what a hand edit in Word does (and not what the
    # detector should match: a collapsed cell is a different cell)
    edited = False
    for para in hit.paragraphs:
        if para.text.strip().lower() == booked.lower():
            for i, run in enumerate(para.runs):
                run.text = real if i == 0 else ""
            edited = bool(para.runs)
    check(edited, "hand-edited the band-name line only")
    doc.save(str(path))
    run_tool("regen_show.py", "--venue", venue, "--date", d.isoformat(), "--artist", booked, "--no-mail")
    n = q("""SELECT * FROM doc_notices WHERE venue=%s AND event_date=%s AND kind='artist_name'
             AND resolved_at IS NULL""", (venue, d))
    check(len(n) == 1, f"one open artist_name decision ({[(x['kind'], x['field']) for x in n]})")
    if not n:
        return
    st, body = get(f"/doc-review?venue={urllib.parse.quote(venue)}&date={d.isoformat()}")
    check(st == 200 and "Which name is right?" in body, f"review page shows the name decision ({st})")
    check(real in body and booked in body, "both spellings offered")
    st, _ = post("/doc-review/decide", {"venue": venue, "date": d.isoformat(), f"n{n[0]['id']}": "rename"})
    res = q("SELECT resolution, apply_error FROM doc_notices WHERE id=%s", (n[0]["id"],), one=True)
    check(res["resolution"] == "renamed" and not res["apply_error"], f"decision resolved as renamed ({res})")
    check(show_for(real, venue, d) is not None, "the show now belongs to the doc's name")
    check(show_for(booked, venue, d) is None, "nothing left under the old name")
    b = booking_for(real, venue, d)
    check(b is not None, "the bookings row was renamed too")
    check(wait_run_now(), "the rename's pipeline run finished")
    check(sheet_rows_for(real, venue, d) and not sheet_rows_for(booked, venue, d),
          "the sheet row carries the new name")
    rows2, path2 = doc_rows(venue, d, real)
    check(path2 is not None and real.lower() in Path(path2).name.lower(),
          f"the filed doc is named for the new band ({path2 and Path(path2).name})")


# ── 2026-09-21 sweep: one check per fix that can be exercised in staging ─────
# x-t .. x-y, then x-aa onward (x-z stays the last test). Fixtures get their
# own dates (+6..+19 inside the welcome window, +53..+81 outside it) so no
# bill here is shared with another test's.

def _post_free(path, band, venue, d, email, minute, **kw):
    """POST a booking form to `path` on the first set start at :<minute> past
    7, 8 or 9pm that nothing on the cloned (live) bill already has.
    -> (status, html, "HH:MM", house clock); the last two are None when all
    three starts were taken."""
    st = html = None
    for h in (19, 20, 21):
        hhmm, house = f"{h}:{minute:02d}", f"{h - 12}:{minute:02d}p"
        st, html = post(path, booking_data(band, venue, d, hhmm, "22:30", event_start=house,
                                           contact_email=email, **kw))
        if st != 409:
            return st, html, hhmm, house
    return st, html, None, None


def _book_free(band, venue, d, email, minute, **kw):
    st, _html, hhmm, house = _post_free("/booking", band, venue, d, email, minute, **kw)
    if st != 200:
        check(False, f"couldn't book {band} on {d} ({st})")
        return None, None
    return hhmm, house


def _run_lifecycle():
    return post("/internal/advance-lifecycle?source=test", json_body={}, headers={"X-Advance-Token": TOKEN})


def _to_addrs(m):
    return {a.strip().lower() for a in (m["payload"].get("to") or "").split(",") if a.strip()}


def _sheet_set(band, venue, key, value):
    """Type `value` into `key`'s column of this band's row(s) in the STAGING
    advance-list.xlsx (DROP), the way Brian edits the sheet in Excel. Only
    call it with no pipeline run in flight. Returns how many rows changed."""
    from openpyxl import load_workbook
    from sheet import FIELDS
    path = DROP / "Nyquist" / "advance-list.xlsx"
    wb = load_workbook(path)
    ws = wb["Advance List"] if "Advance List" in wb.sheetnames else wb.worksheets[0]
    hdr, hrow = {}, None
    for r in range(1, 8):
        m = {FIELDS.get(str(c.value or "").strip().lower()): c.column for c in ws[r]
             if FIELDS.get(str(c.value or "").strip().lower())}
        if len(m) > len(hdr):
            hdr, hrow = m, r
    if not hrow or not {"artist_name", "venue", key} <= set(hdr):
        return 0
    n = 0
    for r in range(hrow + 1, ws.max_row + 1):
        if (db.normalize(str(ws.cell(r, hdr["artist_name"]).value or "")) == db.normalize(band)
                and str(ws.cell(r, hdr["venue"]).value or "").strip().lower() == venue.lower()):
            ws.cell(r, hdr[key]).value = value
            n += 1
    if n:
        wb.save(path)
    return n


def _welcome_code(body):
    m = re.search(re.escape(os.environ.get("ADVANCE_PUBLIC_URL") or APP) + r"/s/([A-Za-z0-9_-]+)", body or "")
    return m.group(1) if m else None


def _locked_date(html):
    m = re.search(r'<input type="hidden" name="show_date" value="([^"]*)">', html or "")
    return m.group(1) if m else None


def _artist_tok(html):
    m = re.search(r'name="artist_token" value="([^"]+)"', html or "")
    return m.group(1) if m else None


# echo of what submit_form's band posted — Edit Show pre-fills these, so a
# real Save round-trips them unchanged (same list x-b uses)
_BAND_ECHO = dict(stage_type="Flat stage", own_engineer="No — use house engineers", performers="4",
                  stage_plot_desc="3-piece, drums center", contact_phone="555-0100", own_iems="No",
                  merch="No", band_tent="No, not needed", vehicle_count="2", large_vehicle_count="0",
                  ack_loadin="yes", ack_95db="yes", ack_reqs="yes")


@test("x-t: the staff gate carries a deep link's query string through the passcode")
def tx_gate_keeps_query():
    # 2026-09-21 sweep (APPA-2): an emailed /doc-review?venue=..&date=.. link
    # opened with no session (Outlook's SameSite=Strict click, a phone, a
    # lapsed session) came back from the passcode as bare /doc-review -> 400
    # 'bad date', and a bookmarked /booking?manual=1 lost its Manual box.
    fresh = http.cookiejar.CookieJar(
        policy=http.cookiejar.DefaultCookiePolicy(secure_protocols=("http", "https")))

    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    op = urllib.request.build_opener(NoRedir, urllib.request.HTTPCookieProcessor(fresh))

    def hit(path, form=None):
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        req = urllib.request.Request(APP + path, data=data, method="POST" if form is not None else "GET")
        try:
            with op.open(req, timeout=60) as r:
                return r.status, r.headers.get("Location"), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Location"), e.read().decode("utf-8", "replace")

    def local(loc):
        u = urllib.parse.urlsplit(loc or "")
        return u.path + (f"?{u.query}" if u.query else "")

    venue, d = "Fountain Square", TODAY + dt.timedelta(days=43)
    for target, marker in (
            (f"/doc-review?venue={urllib.parse.quote(venue)}&date={d.isoformat()}",
             f"Advance doc changes — {venue}"),
            ("/booking?manual=1",
             'id="skip_welcome_email" onchange="onManualChange()" style="width:auto;margin-top:2px" checked>')):
        fresh.clear()
        st, loc, _ = hit(target)
        nxt = urllib.parse.parse_qs(urllib.parse.urlsplit(loc or "").query).get("next", [""])[0]
        check(st == 302 and local(loc).startswith("/gate?") and nxt == target,
              f"no session: {target} -> the gate, next= intact ({st} {loc})")
        if not loc:
            continue
        st, loc2, _ = hit(local(loc), {"passcode": os.environ.get("ADVANCE_GATE_PASS", "lockdown")})
        check(st in (302, 303) and local(loc2) == target, f"the passcode lands back on {target} ({st} {loc2})")
        st, _, body = hit(target)
        check(st == 200 and marker in body, f"{target} opens as linked ({st})")


@test("x-u: /stage-plot serves a filed stage plot, never the advance doc filed beside it")
def tx_stage_plot_route():
    # 2026-09-21 sweep (APPB-2): the public route only checked that the file
    # sat inside a real venue-month folder, which also holds the filed
    # '<MMDDYY> <Event> Prod Adv.docx' with every contact's phone and email.
    reg = q("""SELECT event_date, path FROM filed_docs WHERE venue='Fountain Square'
               AND event_date >= CURRENT_DATE ORDER BY id DESC LIMIT 1""", one=True)
    if not reg or not (DROP / reg["path"]).exists():
        check(False, f"a filed Fountain Square doc on disk to probe with ({reg and reg['path']})")
        return
    doc, d = DROP / reg["path"], reg["event_date"]
    base = f"/stage-plot/{urllib.parse.quote('Fountain Square')}/{d.isoformat()}/"
    st, _loc, _ = no_redirect_get(base + urllib.parse.quote(doc.name))
    check(st == 404, f"the filed advance doc is refused ({st} for {doc.name})")
    stem = fs.stageplot_stem("Route Probe Band", d)
    plots = [doc.parent / f"{stem}.pdf", doc.parent / f"{stem} (updated 092126-1015).pdf"]
    hidden = doc.parent / f".{stem}.pdf"
    try:
        for p in plots + [hidden]:
            p.write_bytes(b"%PDF-1.4 staging stage-plot probe")
        for p in plots:
            st, _loc, body = no_redirect_get(base + urllib.parse.quote(p.name))
            check(st == 200 and body.startswith("%PDF"), f"a filed stage plot is served ({st} for {p.name})")
        st, _loc, _ = no_redirect_get(base + urllib.parse.quote(hidden.name))
        check(st == 404, f"a dotfile is refused even when it reads Stageplot ({st})")
        st, _loc, _ = no_redirect_get(base + "sub/" + urllib.parse.quote(plots[0].name))
        check(st == 404, f"a path instead of a bare filename is refused ({st})")
    finally:
        for p in plots + [hidden]:
            p.unlink(missing_ok=True)


@test("x-v: re-logging a booked band keeps its flags and typed details, and files its answers")
def tx_relog_booking():
    # 2026-09-21 sweep (APPA-4, APPB-4): a second /booking POST for a band
    # already booked that night reset Manual advance / Draft only, blanked
    # lead/note/location, and dropped the answers it carried.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=61), "Relog Keep Band"
    email = "relogkeepband@example.test"
    hhmm, house = _book_free(band, venue, d, email, 31, skip_welcome_email="on", lead_name="Lead Keep",
                             email_note="Bring your own DI", load_in="4:31p")
    if not hhmm:
        return
    check(wait_run_now(), "booking run finished")
    b0 = booking_for(band, venue, d)
    check(b0 and b0["skip_welcome_email"] and b0["load_in"] == "4:31p",
          f"booked as a manual advance with a hand-set load-in ({b0 and (b0['skip_welcome_email'], b0['load_in'])})")
    if not b0:
        return
    n0 = mail_count()
    st, html = post("/booking", booking_data(band, venue, d, hhmm, "22:30", event_start=house, contact_email=email,
                                             monitors="4", stage_type="Flat stage", performers="3"))
    check(st == 200 and "Booking updated" in html, f"the re-log answers as an update ({st})")
    b1 = booking_for(band, venue, d)
    check(b1 and b1["id"] == b0["id"], "same booking row, no twin")
    if not b1:
        return
    check(b1["skip_welcome_email"] is True and not b1["draft_only"],
          f"Manual band advance survived the blank form ({b1['skip_welcome_email']}, {b1['draft_only']})")
    check(b1["lead_name"] == "Lead Keep" and b1["email_note"] == "Bring your own DI",
          f"typed details kept ({b1['lead_name']!r}, {b1['email_note']!r})")
    check(b1["load_in"] == "4:31p", f"hand-set load-in kept, not re-derived from Set Start ({b1['load_in']})")
    s = show_for(band, venue, d)
    sub = (q("SELECT data FROM submissions WHERE show_id=%s AND source='staff' ORDER BY id DESC LIMIT 1",
             (s["id"],), one=True) if s else None)
    check(sub and (sub["data"] or {}).get("monitors") == "4", "the re-log's answers were filed on the show")
    again = [m for m in mails(n0) if m["path"].endswith("/advance-notify")
             and m["payload"].get("event_type") == "booking" and m["payload"].get("artist_name") == band]
    check(not again, f"no second 'New booking' notice for an update ({len(again)})")
    check(wait_regen() and wait_run_now(), "the re-log's doc check and pipeline run finished")
    rows, _ = doc_rows(venue, d, band)
    check(rows and rows.get("Monitors") == "4 wedges", f"the answers reached the doc ('{rows and rows.get('Monitors')}')")
    MAIL_PER_TEST["x-v"] = sends_since(n0)


@test("x-w: Edit Show moving a booking-less show onto an existing booking adopts it without clobbering it")
def tx_adopt_booking():
    # 2026-09-21 sweep (APPB-3): a band that submitted under the wrong date
    # got its own booking-less show; moving it onto the real booking from
    # Edit Show overwrote that booking with the stray show's form and never
    # merged the show, so the band kept getting reminders after answering.
    login()
    venue = "Fountain Square"
    d, wrong = TODAY + dt.timedelta(days=62), TODAY + dt.timedelta(days=63)
    band, email = "Adopt Target Band", "adopttargetband@example.test"
    hhmm, house = _book_free(band, venue, d, email, 32, skip_welcome_email="on", lead_name="Lead Adopt",
                             email_note="Adopt note", load_in="4:32p")
    if not hhmm:
        return
    check(wait_run_now(), "booking run finished")
    b0, real = booking_for(band, venue, d), show_for(band, venue, d)
    if not (b0 and real):
        check(False, f"booking + show exist ({bool(b0)}, {bool(real)})")
        return
    clear_date(venue, wrong)
    st, _ = submit_form(band, venue, wrong, monitors="5")
    check(st == 200 and wait_regen(), f"the band submitted under the wrong date ({st})")
    stray = show_for(band, venue, wrong)
    check(stray and booking_for(band, venue, wrong) is None, "that made its own booking-less show")
    if not stray:
        return
    # what Edit Show posts for the stray show: pre-filled from it (no lead, no
    # note, Manual unticked, the band's own answers), only the date corrected
    st, _ = post(f"/show/{stray['id']}/edit",
                 booking_data(band, venue, d, hhmm, "22:30", event_start=house, contact_email=email,
                              monitors="5", **_BAND_ECHO))
    check(st == 200, f"moved onto the booked date ({st})")
    b1 = booking_for(band, venue, d)
    check(b1 and b1["id"] == b0["id"] and b1["skip_welcome_email"] is True,
          f"the booking kept Manual band advance ({b1 and b1['skip_welcome_email']})")
    check(b1 and b1["lead_name"] == "Lead Adopt" and b1["email_note"] == "Adopt note" and b1["load_in"] == "4:32p",
          f"the booking kept its own details ({b1 and (b1['lead_name'], b1['email_note'], b1['load_in'])})")
    check(q("SELECT 1 FROM shows WHERE id=%s", (stray["id"],), one=True) is None
          and show_for(band, venue, wrong) is None, "the stray show merged away")
    got = q("SELECT responded_at FROM shows WHERE id=%s", (real["id"],), one=True)
    n_band = q("SELECT count(*) AS n FROM submissions WHERE show_id=%s AND source <> 'staff'",
               (real["id"],), one=True)["n"]
    check(got and got["responded_at"] and n_band >= 1, f"the booked show carries the band's submission ({n_band})")
    check(booking_for(band, venue, wrong) is None, "no booking minted at the wrong date")
    check(wait_run_now(), "run after the move finished")


@test("x-x: staff-typed FSQ vehicle counts reach the parking queue once; a change replaces the pending row")
def tx_staff_parking():
    # 2026-09-21 sweep (FLOW-10): answers typed by staff on /booking or Edit
    # Show never queued Mtully's parking digest (only a band's own /submit
    # did), and every resubmission queued the band a second time.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=71), "Staff Parking Band"
    email = "staffparkingband@example.test"
    answers = dict(monitors="3", stage_type="Flat stage", performers="4", vehicle_count="2", large_vehicle_count="0")
    hhmm, house = _book_free(band, venue, d, email, 33, **answers)
    if not hhmm:
        return
    s = show_for(band, venue, d)
    if not s:
        check(False, "the booking's answers created the show")
        return

    def queued():
        return q("SELECT id, vehicle_count, digested_at FROM fsq_parking_queue WHERE show_id=%s ORDER BY id",
                 (s["id"],))
    rows = queued()
    check(len(rows) == 1 and rows[0]["vehicle_count"] == 2 and rows[0]["digested_at"] is None,
          f"the booking's vehicle count is queued once ({[(r['vehicle_count'], r['digested_at']) for r in rows]})")
    check(wait_run_now(), "booking run finished")

    def save(**change):
        st, _ = post(f"/show/{s['id']}/edit",
                     booking_data(band, venue, d, hhmm, "22:30", event_start=house, contact_email=email,
                                  **dict(answers, **change)))
        check(st == 200, f"Edit Show saved {change} ({st})")
    save(monitors="5")
    check([r["id"] for r in queued()] == [r["id"] for r in rows],
          "another answer changed, the counts didn't: nothing new queued")
    save(monitors="5", vehicle_count="3")
    rows = queued()
    check(len(rows) == 1 and rows[0]["vehicle_count"] == 3,
          f"a changed count replaces the undelivered row ({[r['vehicle_count'] for r in rows]})")
    x("UPDATE fsq_parking_queue SET digested_at=now() WHERE show_id=%s", (s["id"],))
    save(monitors="5", vehicle_count="4")
    rows = queued()
    check(len(rows) == 2 and [r["vehicle_count"] for r in rows if r["digested_at"] is None] == [4],
          f"once the digest went out, a new count queues beside it "
          f"({[(r['vehicle_count'], bool(r['digested_at'])) for r in rows]})")
    check(wait_run_now(), "edit runs finished")


@test("x-y: a staff save on Edit Show keeps the band's own contact and notes on the new record")
def tx_staff_save_keeps_band_contact():
    # 2026-09-21 sweep (PRIOR-9): the staff submission carried only posted
    # fields plus the BOOKING's contact, so saving any answer retracted the
    # band's own contact name (and changed_notes) from the doc and sheet.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=73), "Own Contact Band"
    clear_date(venue, d)
    st, _ = submit_form(band, venue, d, monitors="2",
                        extra={"contact_name": "Band Own Contact", "changed_notes": "new drummer this time",
                               "show_series": "Jazz on the Square"})
    check(st == 200 and wait_regen(), f"the band submitted ({st})")
    s = show_for(band, venue, d)
    if not s:
        check(False, "the submission made a show")
        return
    st, _html, _hh, _house = _post_free(f"/show/{s['id']}/edit", band, venue, d, "staffcontact@example.test", 34,
                                        **dict(_BAND_ECHO, contact_name="", monitors="3"))
    check(st == 200, f"staff saved a monitors change with the contact name blank ({st})")
    sub = q("SELECT source, data FROM submissions WHERE show_id=%s ORDER BY id DESC LIMIT 1", (s["id"],), one=True)
    data = (sub["data"] if sub else None) or {}
    check(sub and sub["source"] == "staff" and data.get("monitors") == "3",
          f"the save filed a staff submission ({sub and sub['source']}, {data.get('monitors')!r})")
    check(data.get("contact_name") == "Band Own Contact", f"the band's own contact name carried ({data.get('contact_name')!r})")
    check(data.get("contact_email") == "owncontactband@example.test",
          f"the band's own contact email outranks the staff-typed one ({data.get('contact_email')!r})")
    check(data.get("changed_notes") == "new drummer this time", f"changed_notes carried ({data.get('changed_notes')!r})")
    check(wait_run_now(), "save run finished")


@test("x-aa: a welcome link opens prefilled, and after the show moves it locks the NEW date")
def tx_welcome_link_follows_show():
    # 2026-09-21 sweep (MAIL-1): draft_emails signed welcome links untimed and
    # /f/ only read timed tokens, so every welcome opened a blank form.
    # (IDENT-6): a link sent before staff moved the show locked the old date
    # and the band's submission minted a phantom show there.
    login()
    venue, band, email = "Fountain Square", "Link Moved Band", "linkmovedband@example.test"
    d1, d2 = TODAY + dt.timedelta(days=13), TODAY + dt.timedelta(days=18)
    if not _book_free(band, venue, d1, email, 24)[0]:
        return
    check(wait_run_now(), "booking run finished")
    s = show_for(band, venue, d1)
    if not s:
        check(False, "show seeded")
        return
    x("UPDATE shows SET advance_draft_created_at=NULL, responded_at=NULL WHERE id=%s", (s["id"],))
    n0 = mail_count()
    _run_lifecycle()
    welcome = next((m for m in sends_to(n0, email) if (m["payload"].get("subject") or "").startswith("Welcome")), None)
    code = _welcome_code(welcome["payload"].get("body") if welcome else "")
    check(code, f"the welcome carries its /s/ form link (welcome sent: {bool(welcome)})")
    if not code:
        return
    st, html = get(f"/s/{code}")
    check(st == 200 and _locked_date(html) == d1.isoformat()
          and '<input type="hidden" name="venue" value="Fountain Square">' in html,
          f"the link opens the form addressed and locked to the show ({st}, {_locked_date(html)})")
    check(_artist_tok(html), "...and knows the artist")
    st, _html, _hh, _house = _post_free(f"/show/{s['id']}/edit", band, venue, d2, email, 24)
    check(st == 200, f"staff moved the show to {d2} after the link went out ({st})")
    check(wait_run_now(), "move run finished")
    st, html = get(f"/s/{code}")
    locked, tok = _locked_date(html), _artist_tok(html)
    check(st == 200 and locked == d2.isoformat(), f"the same link now locks the show's new date ({locked})")
    if not (locked and tok):
        return
    st, _ = submit_form(band, venue, dt.date.fromisoformat(locked), monitors="4", artist_tok=tok)
    check(st == 200 and wait_regen(), f"the band submitted from the old link ({st})")
    check(not q("SELECT 1 FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s", (s["artist_id"], venue, d1)),
          "no phantom show at the old date")
    got = q("SELECT show_date, responded_at FROM shows WHERE id=%s", (s["id"],), one=True)
    check(got and got["show_date"] == d2 and got["responded_at"] is not None, "the answers landed on the moved show")
    # links already in inboxes were signed untimed: honoured up to their show date
    from itsdangerous import URLSafeSerializer
    legacy = URLSafeSerializer(os.environ["ADVANCE_SECRET"], salt="advance-prefill")
    st, html = get("/f/" + legacy.dumps({"a": s["artist_id"], "s": {"venue": venue, "date": d2.isoformat()}}))
    check(st == 200 and _locked_date(html) == d2.isoformat(),
          f"an untimed link minted before the fix still prefills ({_locked_date(html)})")
    past = (TODAY - dt.timedelta(days=1)).isoformat()
    st, html = get("/f/" + legacy.dumps({"a": s["artist_id"], "s": {"venue": venue, "date": past}}))
    check(st == 200 and _locked_date(html) is None, "an untimed link for a past show opens the blank form")
    MAIL_PER_TEST["x-aa"] = sends_since(n0)


@test("x-ab: one band at two venues on one date gets each venue's own welcome")
def tx_two_venue_welcomes():
    # 2026-09-21 sweep (MAIL-2): both drafts got the same filename, so one
    # venue's welcome went out twice and the other never did.
    login()
    d, band, email = TODAY + dt.timedelta(days=17), "Two Venue Band", "twovenueband@example.test"
    if not _book_free(band, "Fountain Square", d, email, 25)[0]:
        return
    if not _book_free(band, "Washington Park", d, email, 25, series="Jazz At The Porch", location="Porch")[0]:
        return
    check(wait_run_now(), "booking runs finished")
    shows = [show_for(band, v, d) for v in ("Fountain Square", "Washington Park")]
    check(all(shows), f"a show at each venue ({[bool(s_) for s_ in shows]})")
    if not all(shows):
        return
    ids = [s_["id"] for s_ in shows]
    x("UPDATE shows SET advance_draft_created_at=NULL, responded_at=NULL WHERE id = ANY(%s)", (ids,))
    n0 = mail_count()
    _run_lifecycle()
    subjects = sorted(m["payload"].get("subject") or "" for m in sends_to(n0, email)
                      if (m["payload"].get("subject") or "").startswith("Welcome"))
    check(len(subjects) == 2 and any(" at Fountain Square" in sj for sj in subjects)
          and any(" at Washington Park" in sj for sj in subjects), f"one welcome per venue ({subjects})")
    stamped = q("SELECT count(*) AS n FROM shows WHERE id = ANY(%s) AND advance_draft_created_at IS NOT NULL",
                (ids,), one=True)["n"]
    check(stamped == 2, f"both shows stamped welcomed ({stamped})")
    MAIL_PER_TEST["x-ab"] = sends_since(n0)


@test("x-ac: a band renaming itself on its own link doesn't rename the artist; Brian gets the decision")
def tx_band_self_rename():
    # 2026-09-21 sweep (DBA-2): the rename hit the artists row only; bookings
    # and the sheet kept the old name, so the next run minted a second show
    # under it and welcomed the band again while the real one sat held.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=53)
    band, typed, email = "Self Rename Band", "DJ Self Rename Band", "selfrenameband@example.test"
    if not _book_free(band, venue, d, email, 26)[0]:
        return
    check(wait_run_now(), "booking run finished")
    s = show_for(band, venue, d)
    if not s:
        check(False, "show seeded")
        return
    from itsdangerous import URLSafeTimedSerializer
    link = URLSafeTimedSerializer(os.environ["ADVANCE_SECRET"], salt="advance-prefill").dumps(
        {"a": s["artist_id"], "s": {"venue": venue, "date": d.isoformat(), "series": "Jazz on the Square",
                                    "show_id": s["id"]}})
    st, html = get(f"/f/{link}")
    tok = _artist_tok(html)
    check(st == 200 and tok, f"the band's own link knows the artist ({st})")
    if not tok:
        return
    n_items = q("SELECT count(*) AS n FROM digest_items WHERE kind='band_name'", one=True)["n"]
    st, _ = submit_form(typed, venue, d, monitors="3", artist_tok=tok)
    check(st == 200 and wait_regen(), f"submitted under a new name ({st})")
    a = q("SELECT name FROM artists WHERE id=%s", (s["artist_id"],), one=True)
    check(a and a["name"] == band, f"the artists row keeps the booked name ({a and a['name']})")
    check(not q("SELECT 1 FROM artists WHERE match_key=%s", (db.normalize(typed),)), "no artist under the typed name")
    got = q("SELECT responded_at FROM shows WHERE id=%s", (s["id"],), one=True)
    check(got and got["responded_at"], "the submission landed on the booked show")
    n_now = q("SELECT count(*) AS n FROM digest_items WHERE kind='band_name'", one=True)["n"]
    item = q("SELECT subject FROM digest_items WHERE kind='band_name' ORDER BY id DESC LIMIT 1", one=True)
    check(n_now == n_items + 1 and item and typed in item["subject"],
          f"the typed name is queued for Brian to decide ({item and item['subject']})")
    r = run_tool("run_now.py")
    check(r.returncode == 0, f"run_now ok ({r.stderr[-300:]})")
    check(show_for(typed, venue, d) is None, "the next run mints no show under the typed name")
    held = q("SELECT held_at FROM shows WHERE id=%s", (s["id"],), one=True)
    check(held and held["held_at"] is None, "the real show is not held as a sheet orphan")


@test("x-ad: a band name with a non-breaking or narrow space upserts twice without crashing")
def tx_nbsp_names():
    # 2026-09-21 sweep (DBA-3): Python normalize() folds U+00A0/U+202F/U+2007,
    # the SQL match_key doesn't, so the fallback lookup found nothing and crashed.
    out = []
    with db.get_conn() as conn, conn.cursor() as cur:
        for nm in ("Nbsp Upsert Band", "Narrow Upsert Band", "Figure Upsert Band"):
            a1 = db.upsert_artist(cur, nm, email="nbspupsert@example.test")
            a2 = db.upsert_artist(cur, nm, email="nbspupsert@example.test")   # unchanged: the fallback lookup
            hit = db.find_artist_by_name(cur, nm)
            a3 = db.upsert_artist(cur, nm, known_id=a1)
            out.append((ascii(nm), a1, a2, hit and hit["id"], a3))
        conn.rollback()
    for nm, a1, a2, hid, a3 in out:
        check(a1 == a2 == hid == a3, f"{nm}: one artist id throughout ({a1}, {a2}, {hid}, {a3})")


@test("x-ae: an 'info changed' notice waits for contact, rides the welcome, and follows the band's current address")
def tx_notice_contact():
    # 2026-09-21 sweep (MAIL-6): the notice keyed on the 21-day window, not on
    # whether the band had been contacted. (MAIL-7): it went to the booking
    # contact, not the artist's current address every other email uses.
    import booking_update
    login()
    venue = "Fountain Square"
    # (a) inside the window, never contacted: held back, then carried by the welcome
    d, band, email = TODAY + dt.timedelta(days=16), "Carried Notice Band", "carriednoticeband@example.test"
    if not _book_free(band, venue, d, email, 35)[0]:
        return
    check(wait_run_now(), "booking run finished")
    b, s = booking_for(band, venue, d), show_for(band, venue, d)
    if not (b and s):
        check(False, f"booking + show exist ({bool(b)}, {bool(s)})")
        return
    x("UPDATE shows SET advance_draft_created_at=NULL, responded_at=NULL, advance_held_draft_at=NULL WHERE id=%s",
      (s["id"],))
    with db.get_conn() as conn, conn.cursor() as cur:
        changes, notify = db.update_booking(cur, b["id"], dict(db.get_booking(cur, b["id"]), load_in="5:05p"))
        conn.commit()
    check("load_in" in changes and notify, f"a load-in change inside the window queues a notice ({changes}, {notify})")
    n0 = mail_count()
    booking_update.send_due(lambda *a: None)
    check(not sends_to(n0, email), "nothing goes to a band that hasn't been contacted")
    pend = q("SELECT id, sent_at FROM booking_edits WHERE booking_id=%s AND notify ORDER BY id DESC LIMIT 1",
             (b["id"],), one=True)
    check(pend and pend["sent_at"] is None, "the notice waits")
    st, _ = _run_lifecycle()
    subjects = [m["payload"].get("subject") or "" for m in sends_to(n0, email)]
    check(st == 200 and any(sj.startswith("Welcome") for sj in subjects), f"the welcome went out ({subjects})")
    check(not any(sj.startswith("Updated booking details") for sj in subjects),
          "no 'changed from' email for a time the band never saw")
    if pend:
        row = q("SELECT sent_at, error FROM booking_edits WHERE id=%s", (pend["id"],), one=True)
        check(row["sent_at"] is not None and (row["error"] or "").startswith("skipped: welcome carried it"),
              f"resolved as carried by the welcome ({row})")
    # (b) welcomed, moved out of the window; the band's form named a new contact.
    # In-process edits only: a background run would re-sync last_email from the sheet.
    d2, d3, d4 = (TODAY + dt.timedelta(days=n) for n in (11, 54, 55))
    band2, old_email, new_email = "Moved Out Band", "movedoutband@example.test", "movedoutband-new@example.test"
    if not _book_free(band2, venue, d2, old_email, 36)[0]:
        return
    check(wait_run_now(), "second booking run finished")
    b2, s2 = booking_for(band2, venue, d2), show_for(band2, venue, d2)
    if not (b2 and s2):
        check(False, f"booking + show exist ({bool(b2)}, {bool(s2)})")
        return
    x("UPDATE shows SET advance_draft_created_at = now() - interval '1 day' WHERE id=%s", (s2["id"],))
    x("UPDATE artists SET last_email=%s WHERE id=%s", (new_email, s2["artist_id"]))
    for to_d, label in ((d3, "11 -> 54 days out"), (d4, "54 -> 55 days out, both outside the window")):
        with db.get_conn() as conn, conn.cursor() as cur:
            ch, nt = db.update_booking(cur, b2["id"], dict(db.get_booking(cur, b2["id"]), event_date=to_d))
            conn.commit()
        check("event_date" in ch and nt, f"{label}: a contacted band's move queues a notice ({nt})")
        n1 = mail_count()
        booking_update.send_due(lambda *a: None)
        got = sends_to(n1, new_email)
        check(len(got) == 1 and (got[0]["payload"].get("subject") or "").startswith("Updated booking details"),
              f"{label}: the notice went to the band's current address ({len(got)})")
        check(not sends_to(n1, old_email), f"{label}: not to the booking contact the band replaced")
    MAIL_PER_TEST["x-ae"] = sends_since(n0)


@test("x-af: a Salsa band's 'info changed' notice copies Nick and carries the Spanish half")
def tx_salsa_notice():
    # 2026-09-21 sweep (MAIL-4): the one Salsa band email without the
    # NRadina@gmail.com CC, and English-only.
    import booking_update
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=76)
    band, email = "Salsa Notice Band", "salsanoticeband@example.test"
    sid = db_upsert_show(db_upsert_artist(band, email), venue, d, series="Salsa On The Square")
    x("UPDATE shows SET advance_draft_created_at=now(), cancelled_at=NULL, held_at=NULL WHERE id=%s", (sid,))
    bid = None
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by,
                                                  load_in, event_start, curfew)
                           VALUES (%s, %s, %s, 'Salsa On The Square', %s, 'tests', '6:00p', '7:00p', '10:00p')
                           RETURNING id""", (band, venue, d, email))
            bid = cur.fetchone()["id"]
            _ch, notify = db.update_booking(cur, bid, dict(db.get_booking(cur, bid), load_in="6:30p"))
            conn.commit()
        check(notify, "a welcomed Salsa band's load-in change queues a notice")
        n0 = mail_count()
        booking_update.send_due(lambda *a: None)
        mine = [m for m in sends_since(n0) if email in _to_addrs(m)]
        check(len(mine) == 1, f"one notice ({len(mine)})")
        check(mine and "nradina@gmail.com" in _to_addrs(mine[0]),
              f"the series CC rides along ({mine and mine[0]['payload'].get('to')})")
        body = mine[0]["payload"].get("body", "") if mine else ""
        check("ESPAÑOL / SPANISH VERSION BELOW" in body and "Carga: 6:00p  ->  6:30p" in body,
              "the Spanish half carries the change")
        MAIL_PER_TEST["x-af"] = sends_since(n0)
    finally:
        if bid:
            x("DELETE FROM bookings WHERE id=%s", (bid,))
        x("UPDATE shows SET cancelled_at=now() WHERE id=%s", (sid,))


@test("x-ag: staff-typed booking answers keep the reminder ladder running and let the band's submission attach")
def tx_staff_answers_ladder():
    # 2026-09-21 sweep (FLOW-5): a staff submission counted as the band
    # answering everywhere but the welcome gate — no reminders, no 3-day
    # alert, and the band's real submission couldn't attach to its booking.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=6), "Staff Typed Band"
    if not _book_free(band, venue, d, "stafftypedband@example.test", 38,
                      monitors="3", stage_type="Flat stage", performers="4")[0]:
        return
    s = show_for(band, venue, d)
    if not s:
        check(False, "the booking's answers created the show")
        return
    check(q("SELECT 1 FROM submissions WHERE show_id=%s AND source='staff'", (s["id"],), one=True),
          "the typed answers are on file as a staff submission")
    check(wait_run_now(), "booking run finished")
    x("UPDATE shows SET advance_draft_created_at = now() - interval '3 days', responded_at=NULL WHERE id=%s", (s["id"],))
    x("DELETE FROM advance_reminders WHERE show_id=%s", (s["id"],))

    def due():
        with db.get_conn() as conn, conn.cursor() as cur:
            return ({r["show_id"] for r in db.shows_due_for_followup(cur, 7)},
                    {r["show_id"] for r in db.unresponded_shows_at(cur, venue, d)})
    due7, open_ = due()
    check(s["id"] in due7, "the 7-day reminder is still due")
    check(s["id"] in open_, "the booking still counts as unanswered for attaching")
    b = booking_for(band, venue, d)
    if b:
        x("UPDATE bookings SET skip_welcome_email=true WHERE id=%s", (b["id"],))
        due7_manual, _ = due()
        x("UPDATE bookings SET skip_welcome_email=false WHERE id=%s", (b["id"],))
        check(s["id"] not in due7_manual, "on a Manual band advance the staff answers ARE the advance: no reminder")
    else:
        check(False, "the booking row exists")
    x("UPDATE shows SET responded_at=COALESCE(responded_at, now()) WHERE venue=%s AND show_date=%s AND id<>%s",
      (venue, d, s["id"]))
    typed = "Staff Typed Band Quartet"
    st, _ = submit_form(typed, venue, d, monitors="5")
    check(st == 200 and wait_regen(), f"the band submitted under a close variant ({st})")
    m = q("SELECT status, booked_show_id FROM submission_matches WHERE typed_name=%s ORDER BY id DESC LIMIT 1",
          (typed,), one=True)
    check(m and m["status"] == "attached_auto" and m["booked_show_id"] == s["id"],
          f"it attached to the booked show ({m})")
    got = q("SELECT responded_at FROM shows WHERE id=%s", (s["id"],), one=True)
    check(got and got["responded_at"] is not None, "the booked show is now answered")


@test("x-ah: a band booked twice keeps each show's own answers in each show's doc")
def tx_two_dates_own_answers():
    # 2026-09-21 sweep (FLOW-4): every act filled from the artist's newest
    # submission across all shows, so the later booking's answers were
    # written silently into the earlier show's doc.
    login()
    venue, band, email = "Fountain Square", "Two Dates Band", "twodatesband@example.test"
    d1, d2 = TODAY + dt.timedelta(days=56), TODAY + dt.timedelta(days=57)
    if not _book_free(band, venue, d1, email, 39, monitors="6")[0]:
        return
    check(wait_run_now(), "first booking filed")
    rows, _ = doc_rows(venue, d1, band)
    check(rows and rows.get("Monitors") == "6 wedges", f"first doc has its own answer ('{rows and rows.get('Monitors')}')")
    n_not = _notice_count(venue, d1)
    if not _book_free(band, venue, d2, email, 39, monitors="2")[0]:
        return
    check(wait_run_now(), "second booking filed")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "a full pass over both docs")
    rows1, _ = doc_rows(venue, d1, band)
    rows2, _ = doc_rows(venue, d2, band)
    check(rows1 and rows1.get("Monitors") == "6 wedges",
          f"the first show's doc keeps its own answer ('{rows1 and rows1.get('Monitors')}')")
    check(rows2 and rows2.get("Monitors") == "2 wedges",
          f"the second show's doc has its own ('{rows2 and rows2.get('Monitors')}')")
    check(_notice_count(venue, d1) == n_not, f"no doc notices on the first date ({_notice_count(venue, d1) - n_not} new)")


@test("x-ai: renaming a band onto an existing artist keeps every hand edit in its doc column")
def tx_rename_onto_artist():
    # 2026-09-21 sweep (DOC-1): the show moved to another artist_id, the
    # filed doc's column map didn't, and the whole column went back to the
    # template — every hand edit gone.
    login()
    venue = "Fountain Square"
    d0, d = TODAY + dt.timedelta(days=58), TODAY + dt.timedelta(days=59)
    target, source, email = "Remap Target Band", "Remap Source Band", "remapsourceband@example.test"
    if not _book_free(target, venue, d0, "remaptargetband@example.test", 40)[0]:
        return
    hhmm, house = _book_free(source, venue, d, email, 40, monitors="4", backline="source amps")
    if not hhmm:
        return
    check(wait_run_now(), "both bookings filed")
    names, _cells, _ = _grid_cells(venue, d)
    col = _col_of(names, source)
    check(col is not None, f"the source band has a column ({names})")
    if col is None:
        return
    hand = "source amps + Brian's spare DI"
    _edit_doc_cell(venue, d, "backline", col, hand)
    tgt = q("SELECT id FROM artists WHERE match_key=%s", (db.normalize(target),), one=True)
    b = booking_for(source, venue, d)
    st, _ = post(f"/booking/{b['id']}/edit",
                 booking_data(target, venue, d, hhmm, "22:30", event_start=house, contact_email=email))
    check(st == 200, f"renamed onto the existing artist ({st})")
    s = show_for(target, venue, d)
    check(s and tgt and s["artist_id"] == tgt["id"], "the show moved onto that artist")
    reg = q("SELECT columns FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    ids = {int(v) for v in ((reg or {}).get("columns") or {}).values()}
    check(tgt and tgt["id"] in ids, f"the filed doc's column map was re-keyed to it ({reg and reg['columns']})")
    check(wait_run_now(), "rename run finished")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "another full pass ok")
    names, cells, _ = _grid_cells(venue, d)
    col = _col_of(names, target)
    check(col is not None and cells.get(("backline", col)) == hand,
          f"the hand edit is still there ({col}, {cells.get(('backline', col))!r})")
    check(col is not None and cells.get(("monitors", col)) == "4 wedges", "the band's answers are still there")


@test("x-aj: a hand-typed or pasted hyperlink survives a pass that has nothing for its cell")
def tx_hand_hyperlink():
    # 2026-09-21 sweep (DOC-2): any hyperlink in a cell the fresh build left
    # empty was treated as a stale pipeline link and erased — including
    # Word's auto-linked URLs and emails typed or pasted by hand.
    import docmerge
    from docx import Document
    from docx.oxml.ns import qn

    def row_cell(doc, label, col):
        for r in daysheet.find_grid(doc).rows:
            if daysheet.norm(r.cells[0].text).startswith(label):
                return r.cells[col]
        return None

    def has_link(cell):
        return cell is not None and next(cell._tc.iter(qn("w:hyperlink")), None) is not None

    T, E, F = (Document(str(daysheet.UNIVERSAL_TEMPLATE)) for _ in range(3))
    daysheet.set_cell_link(row_cell(E, "additional info", 2), "https://drive.example/rider.pdf",
                           "https://drive.example/rider.pdf")
    daysheet.set_cell_link(row_cell(E, "stage plot", 1), "https://drive.example/plot.pdf",
                           "https://drive.example/plot.pdf")
    daysheet.set_cell_link(row_cell(E, "stage plot", 3), "See DB — gone-band-stageplot.pdf",
                           "https://www.dropbox.com/scl/fi/x/gone-band-stageplot.pdf?dl=1")
    check(has_link(row_cell(E, "additional info", 2)) and has_link(row_cell(E, "stage plot", 1))
          and has_link(row_cell(E, "stage plot", 3)), "setup: three linked cells")
    docmerge.merge(T, F, E, cols={1: 11, 2: 22, 3: 33}, old_cols={1: 11, 2: 22, 3: 33})
    cell = row_cell(E, "additional info", 2)
    check(has_link(cell) and "rider.pdf" in daysheet.full_cell_text(cell),
          "a link typed into Additional Info is kept")
    check(has_link(row_cell(E, "stage plot", 1)), "a Drive link pasted into Stage Plot is kept")
    check(not has_link(row_cell(E, "stage plot", 3)), "the pipeline's own orphaned 'See DB' link is still cleared")


@test("x-ak: a venue-only move carries the filed doc into the new venue's month folder")
def tx_venue_move_doc():
    # 2026-09-21 sweep (DOC-7): the in-place rename compared filenames only,
    # and a venue move keeps the name, so the doc stayed in the old folder.
    login()
    d = TODAY + dt.timedelta(days=60)
    band, email = "Venue Move Band", "venuemoveband@example.test"
    if (q("SELECT 1 FROM shows WHERE venue='Fountain Square' AND show_date=%s LIMIT 1", (d,), one=True)
            or q("SELECT 1 FROM filed_docs WHERE venue='Washington Park' AND event_date=%s LIMIT 1", (d,), one=True)):
        check(True, f"the clone already has a Fountain Square show or a Washington Park doc on {d} — skipped")
        return
    kw = dict(series="Stand-Alone Internal", event_name="Venue Move Night")   # same filename at both venues
    if not _book_free(band, "Fountain Square", d, email, 41, **kw)[0]:
        return
    check(wait_run_now(), "booking filed")
    reg = q("SELECT path FROM filed_docs WHERE venue='Fountain Square' AND event_date=%s", (d,))
    check(len(reg) == 1 and reg[0]["path"].startswith(fs.real_venue_folder("Fountain Square") + "/"),
          f"doc filed under Fountain Square ({[r_['path'] for r_ in reg]})")
    s = show_for(band, "Fountain Square", d)
    if len(reg) != 1 or not s:
        return
    old = DROP / reg[0]["path"]
    st, _html, _hh, _house = _post_free(f"/show/{s['id']}/edit", band, "Washington Park", d, email, 41,
                                        location="Main Stage", **kw)
    check(st == 200, f"moved to Washington Park, same date ({st})")
    check(wait_run_now(), "move run finished")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "another full pass ok")
    reg2 = q("SELECT path FROM filed_docs WHERE venue='Washington Park' AND event_date=%s", (d,))
    want = f"{fs.real_venue_folder('Washington Park')}/{fs.real_month_folder('Washington Park', d)}/"
    check(len(reg2) == 1 and reg2[0]["path"].startswith(want) and (DROP / reg2[0]["path"]).exists(),
          f"the doc now lives in the Washington Park month folder ({[r_['path'] for r_ in reg2]})")
    check(not old.exists(), f"and not in the old folder ({old.name})")
    check(not q("SELECT 1 FROM filed_docs WHERE venue='Fountain Square' AND event_date=%s", (d,)),
          "nothing left registered at Fountain Square")


@test("x-al: two renames before the notice sends still leave one sheet row, under the last name")
def tx_double_rename():
    # 2026-09-21 sweep (IDENT-3): the sheet row was found by rebuilding its
    # identity from the pending notice's edit history; a second rename (or a
    # revert) before that notice sent pointed at a name the row no longer had.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=19)
    for names, minute in ((("Twice Renamed Alpha", "Twice Renamed Bravo", "Twice Renamed Charlie"), 37),
                          (("Revert Rename Xray", "Revert Rename Yankee", "Revert Rename Xray"), 47)):
        first, last = names[0], names[-1]
        email = f"{re.sub('[^a-z]', '', first.lower())}@example.test"
        hhmm, house = _book_free(first, venue, d, email, minute)
        if not hhmm:
            continue
        check(wait_run_now(), f"{first} booked + filed")
        s0, b = show_for(first, venue, d), booking_for(first, venue, d)
        if not (s0 and b):
            check(False, f"{first}: booking + show exist")
            continue
        for new in names[1:]:
            st, _ = post(f"/booking/{b['id']}/edit",
                         booking_data(new, venue, d, hhmm, "22:30", event_start=house, contact_email=email))
            check(st == 200, f"renamed to {new} ({st})")
            check(wait_run_now(), f"run after the rename to {new} finished")
        r = run_tool("run_now.py")
        check(r.returncode == 0, "another full pass ok")
        for nm in dict.fromkeys(names):
            want = 1 if nm == last else 0
            got = len(sheet_rows_for(nm, venue, d))
            check(got == want, f"{nm}: {want} sheet row(s) ({got})")
            if nm != last:
                check(show_for(nm, venue, d) is None, f"no show re-minted under {nm}")
        s1 = show_for(last, venue, d)
        check(s1 and s1["id"] == s0["id"], f"{last} is still the original show ({s1 and s1['id']} vs {s0['id']})")
        bi = q("SELECT sheet_ident FROM bookings WHERE id=%s", (b["id"],), one=True)
        check(bi and (bi["sheet_ident"] or {}).get("artist_name") == last,
              f"sheet_ident records the name the row was written under ({bi and bi['sheet_ident']})")


@test("x-am: renaming a sheet-typed show with no bookings row renames its sheet row in place")
def tx_sheet_typed_rename():
    # 2026-09-21 sweep (IDENT-2): Edit Show created a booking at the new name
    # and never touched the hand-typed row, which re-minted the old show.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=64)
    old, new, email = "Sheet Typd Band", "Sheet Typed Band", "sheettypedband@example.test"
    hhmm, house = _book_free(old, venue, d, email, 46)
    if not hhmm:
        return
    check(wait_run_now(), "booked + filed")
    s0, b0 = show_for(old, venue, d), booking_for(old, venue, d)
    check(s0 and b0 and len(sheet_rows_for(old, venue, d)) == 1, "sheet row + show + booking")
    if not (s0 and b0):
        return
    # a row Brian typed into the sheet himself: sheet row and show, no bookings row
    x("DELETE FROM bookings WHERE id=%s", (b0["id"],))
    st, _ = post(f"/show/{s0['id']}/edit",
                 booking_data(new, venue, d, hhmm, "22:30", event_start=house, contact_email=email))
    check(st == 200, f"renamed on Edit Show ({st})")
    check(wait_run_now(), "rename run finished")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "another full pass ok")
    check(not sheet_rows_for(old, venue, d) and len(sheet_rows_for(new, venue, d)) == 1,
          "the one sheet row now carries the new name")
    check(show_for(old, venue, d) is None, "the old spelling is not re-minted")
    s1 = show_for(new, venue, d)
    check(s1 and s1["id"] == s0["id"], f"same show, renamed ({s1 and s1['id']} vs {s0['id']})")


@test("x-an: the reconcile leaves dirty and cancelled bookings to step 1b, and re-seeding never moves seeded_at")
def tx_reconcile_stamps():
    # 2026-09-21 sweep (PRIOR-7, IDENT-3): 1c re-appended renamed (dirty)
    # bookings under their new identity and re-stamped seeded_at every pass;
    # an edit landing mid-run is kept dirty by the snapshot stamp.
    d = TODAY + dt.timedelta(days=80)
    band = "Reconcile Stamp Band"
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by,
                                              load_in, event_start, seeded_at, sheet_dirty)
                       VALUES (%s, 'Fountain Square', %s, 'Jazz on the Square', 'reconcilestamp@example.test',
                               'tests', '6:00p', '7:00p', now() - interval '5 days', true)
                       RETURNING id, seeded_at""", (band, d))
        row = cur.fetchone()
        bid, seeded0 = row["id"], row["seeded_at"]

        def listed():
            return bid in {r["id"] for r in db.future_bookings(cur)}
        dirty_listed = listed()
        cur.execute("UPDATE bookings SET sheet_dirty=false WHERE id=%s", (bid,))
        clean_listed = listed()
        sid = db.upsert_show(cur, db.upsert_artist(cur, band, email="reconcilestamp@example.test"),
                             "Fountain Square", d, series="Jazz on the Square")
        cur.execute("UPDATE shows SET cancelled_at=now() WHERE id=%s", (sid,))
        cancelled_listed = listed()
        cur.execute("UPDATE shows SET cancelled_at=NULL WHERE id=%s", (sid,))
        db.mark_bookings_seeded(cur, [bid])
        cur.execute("SELECT seeded_at, sheet_ident FROM bookings WHERE id=%s", (bid,))
        seeded = cur.fetchone()
        # the run wrote the row with load-in 6:00p; an edit to 6:30p landed mid-run
        cur.execute("SELECT * FROM bookings WHERE id=%s", (bid,))
        snap = {k: (v.isoformat() if isinstance(v, dt.date) else v) for k, v in cur.fetchone().items()}
        cur.execute("UPDATE bookings SET load_in='6:30p', sheet_dirty=true WHERE id=%s", (bid,))
        db.mark_bookings_synced(cur, [bid], snapshot={bid: snap})
        cur.execute("SELECT sheet_dirty, sheet_dirty_fields, sheet_ident FROM bookings WHERE id=%s", (bid,))
        synced = cur.fetchone()
        conn.rollback()
    check(not dirty_listed and clean_listed, f"a dirty booking is left to 1b, a clean one reconciled ({dirty_listed}, {clean_listed})")
    check(not cancelled_listed, "a cancelled show's booking is never re-added")
    check(seeded["seeded_at"] == seeded0, f"re-seeding keeps the first seeded_at ({seeded['seeded_at']} vs {seeded0})")
    check((seeded["sheet_ident"] or {}).get("artist_name") == band, f"and records sheet_ident ({seeded['sheet_ident']})")
    check(synced["sheet_dirty"] is True and list(synced["sheet_dirty_fields"] or []) == ["load_in"],
          f"a mid-run edit stays dirty, just that field ({synced['sheet_dirty']}, {synced['sheet_dirty_fields']})")
    check((synced["sheet_ident"] or {}).get("artist_name") == band, "sheet_ident stamped from what was written")


@test("x-ao: a cancelled act never pushes a real act off a full bill")
def tx_cancelled_act_off_doc():
    # 2026-09-21 sweep (DAY-1): a cancelled opener kept column 1 and the
    # replacement pushed the real headliner off the 3-column doc.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=65)
    A, B, C, D = "Bill Cancel Opener", "Bill Cancel Support", "Bill Cancel Headliner", "Bill Cancel Replacement"
    for band, hhmm, house in ((A, "19:05", "7:05p"), (B, "20:05", "8:05p"), (C, "21:05", "9:05p")):
        st, _ = post("/booking", booking_data(band, venue, d, hhmm, "22:30", event_start=house))
        check(st == 200, f"{band} booked ({st})")
    check(wait_run_now(), "3-act bill filed")
    sa = show_for(A, venue, d)
    if not sa:
        check(False, "the opener's show exists")
        return
    post(f"/show/{sa['id']}/cancel")
    st, _ = post("/booking", booking_data(D, venue, d, "19:20", "22:30", event_start="7:20p"))
    check(st == 200, f"a replacement booked at a different start ({st})")
    check(wait_run_now(), "run after the replacement finished")
    r = run_tool("run_now.py")
    check(r.returncode == 0, "another full pass ok")
    names, _cells, _ = _grid_cells(venue, d)
    print(f"      headers: {names}")
    check((_col_of(names, D), _col_of(names, B), _col_of(names, C)) == (1, 2, 3),
          f"the three real acts hold the three columns ({names})")
    check(not any("CANCELLED" in n for n in names.values()), "no CANCELLED column on a full bill")
    size = q("""SELECT new_value FROM doc_notices WHERE venue=%s AND event_date=%s
                AND kind='bill_size' AND resolved_at IS NULL""", (venue, d))
    check(not any(C in (r_["new_value"] or "") for r_ in size), f"no 'not on the doc' notice for the headliner ({size})")


@test("x-ap: numbers, times and dates typed into the sheet come back as text and never crash the doc")
def tx_sheet_cell_types():
    # 2026-09-21 sweep (DAY-4): a numeric Contact Phone crashed daysheet.build.
    # (PRIOR-10): an Excel time/date cell crashed import_sheet mid-rebuild.
    from openpyxl import load_workbook
    from sheet import FIELDS, read_advance_sheet
    f = daysheet.merged_fields({"submission": None,
                                "sheet_fields": {"contact_phone": 5135550100, "performers": 5.0}})
    check(f.get("contact_phone") == "5135550100" and f.get("performers") == "5",
          f"sheet numbers merge as text ({f.get('contact_phone')!r}, {f.get('performers')!r})")
    vals = daysheet.act_row_values({"contact_name": "Pat", "contact_phone": 5135550100})
    check(vals.get("band contact — cell") == "5135550100", f"a raw number still fills the contact cell ({vals})")
    dst = T / "cell_types.xlsx"
    shutil.copy(TOOLS / "lists" / "advance_list_template.xlsx", dst)
    wb = load_workbook(dst)
    ws = wb["Advance List"] if "Advance List" in wb.sheetnames else wb.worksheets[0]
    hdr, hrow = {}, None
    for r in range(1, 8):
        m = {FIELDS.get(str(c.value or "").strip().lower()): c.column for c in ws[r]
             if FIELDS.get(str(c.value or "").strip().lower())}
        if len(m) > len(hdr):
            hdr, hrow = m, r
    row = max((c.row for c in ws["A"] if c.value), default=hrow) + 1
    typed = {"event_name": "Cell Type Night", "event_date": (TODAY + dt.timedelta(days=81)).isoformat(),
             "venue": "Fountain Square", "series": "Jazz on the Square", "artist_name": "Cell Type Band",
             "event_start": dt.time(19, 30), "load_in": dt.time(18, 0), "set_time": dt.time(1, 0),
             "contact_phone": 5135550100, "monitors": dt.datetime(TODAY.year, 3, 4)}
    for key, val in typed.items():
        if key in hdr:
            ws.cell(row, hdr[key]).value = val
    wb.save(dst)
    want = {"event_start": "7:30p", "load_in": "6:00p", "set_time": "60", "contact_phone": "5135550100",
            "monitors": f"{TODAY.year}-03-04"}
    rows = [r_ for r_ in read_advance_sheet(dst) if r_.get("artist_name") == "Cell Type Band"]
    check(len(rows) == 1, f"the typed row reads back ({len(rows)})")
    if not rows:
        return
    got = {k: rows[0].get(k) for k in want if k in hdr}
    check(got == {k: v for k, v in want.items() if k in hdr}, f"Excel-typed cells read as house text ({got})")
    check(all(v is None or isinstance(v, str) for v in rows[0].values()), "every value is text")
    json.dumps(rows[0])  # import_sheet's add_act writes these as JSON


@test("x-aq: deleting a sheet row leaves every stage-plot link on its own band's row")
def tx_reanchor_links():
    # 2026-09-21 sweep (PIPE-1): openpyxl's delete_rows moved the cells but
    # not Hyperlink.ref, so each link below the deleted row was written onto
    # the next band's row (and from there into advance docs).
    from openpyxl import Workbook, load_workbook
    p = T / "pipe1_links.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Advance List"
    ws.append(["Artist Name", "Stage Plot"])
    for i, band in enumerate(("Alpha", "Bravo", "Charlie"), start=2):
        ws.cell(i, 1).value = band
        ws.cell(i, 2).value = f"{band} plot"
        ws.cell(i, 2).hyperlink = f"../{band}%20Stageplot.pdf"
    wb.save(p)
    loaded = fs.sheet_hash(p)
    wb = load_workbook(p)
    ws = wb["Advance List"]
    ws.delete_rows(2, 1)     # Alpha's row goes; Bravo and Charlie shift up
    fs.safe_save_workbook(wb, p, loaded)
    ws = load_workbook(p)["Advance List"]
    links = {r: (ws.cell(r, 2).hyperlink.target if ws.cell(r, 2).hyperlink else None) for r in (2, 3, 4)}
    check(links == {2: "../Bravo%20Stageplot.pdf", 3: "../Charlie%20Stageplot.pdf", 4: None},
          f"each link stayed with its band ({links})")
    check(ws.cell(2, 1).value == "Bravo" and ws.cell(3, 1).value == "Charlie", "the rows themselves shifted")


@test("x-ar: purging an orphan releases the shows held as its 'possible correction'")
def tx_purge_releases_candidates():
    # 2026-09-21 sweep (PIPE-4): Cancel/Restore/Merge released them, purge
    # didn't, so a real band stayed held (no emails at all) against a dead id.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=66)
    made = []

    def show(name):
        sid = db_upsert_show(db_upsert_artist(name, f"{re.sub('[^a-z]', '', name.lower())}@example.test"),
                             venue, d, series="Jazz on the Square")
        made.append(sid)
        return sid

    def hold(sid, reason):
        x("UPDATE shows SET held_at=now(), hold_reason=%s, hold_dismissed_at=NULL, cancelled_at=NULL WHERE id=%s",
          (reason, sid))
    try:
        orphan, cand = show("Purged Orphan Band"), show("Purged Orphan Band Two")
        hold(orphan, "missing from the advance sheet")
        hold(cand, f"possible correction of show {orphan}")
        st, body = post(f"/show/{orphan}/purge", json_body={"confirm_name": "purged orphan band"})
        check(st == 200 and json.loads(body).get("ok"), f"orphan purged ({st} {body[:120]})")
        c = q("SELECT held_at, hold_reason, hold_dismissed_at FROM shows WHERE id=%s", (cand,), one=True)
        check(c and c["held_at"] is None and c["hold_reason"] is None and c["hold_dismissed_at"] is not None,
              f"its candidate is released ({c})")
        check(wait_run_now(), "purge run finished")
        # holds.py's nightly sweep: an orphan gone some other way frees its candidate too
        gone, cand2 = show("Vanished Orphan Band"), show("Vanished Orphan Band Two")
        hold(gone, "missing from the advance sheet")
        hold(cand2, f"possible correction of show {gone}")
        x("DELETE FROM shows WHERE id=%s", (gone,))
        with db.get_conn() as conn, conn.cursor() as cur:
            released = db.release_stale_candidate_holds(cur)
            conn.commit()
        c2 = q("SELECT held_at FROM shows WHERE id=%s", (cand2,), one=True)
        check(cand2 in released and c2 and c2["held_at"] is None, f"a stale candidate hold is swept up ({released})")
    finally:
        x("UPDATE shows SET cancelled_at=now(), held_at=NULL WHERE id = ANY(%s)", (made,))


@test("x-as: an advance doc that can't be filed reaches the digest, and the run carries on")
def tx_filing_error_reported():
    # 2026-09-21 sweep (PIPE-7): a per-event filing failure only reached the
    # run log, so that show's doc quietly stopped updating.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=67), "Filing Error Band"
    if not _book_free(band, venue, d, "filingerrorband@example.test", 44)[0]:
        return
    check(wait_run_now(), "booked + filed")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s ORDER BY id DESC LIMIT 1", (venue, d), one=True)
    if not reg or not (DROP / reg["path"]).exists():
        check(False, f"a filed doc to break ({reg})")
        return
    doc = DROP / reg["path"]
    good = doc.read_bytes()
    try:
        doc.write_bytes(b"this is not a docx")
        r = run_tool("run_now.py")
        check(r.returncode == 0, f"the run carried on past the broken doc ({r.stderr[-300:]})")
        n = q("SELECT field FROM doc_notices WHERE venue=%s AND event_date=%s AND kind='filing_error'", (venue, d))
        check(any(r_["field"] == "Advance doc" for r_ in n), f"a filing_error notice was recorded ({n})")
        item = q("SELECT subject FROM digest_items WHERE kind='doc' AND subject LIKE %s ORDER BY id DESC LIMIT 1",
                 (f"Advance doc could not be filed — {d.strftime('%m%d%y')}%",), one=True)
        check(item is not None, "and queued for Brian's digest")
    finally:
        doc.write_bytes(good)


@test("x-at: the day after a responded show, the lifecycle sends the post-show thank-you once")
def tx_auto_thankyou():
    # 2026-09-21 sweep (PRIOR-2): the lifecycle picked past shows and
    # send_for_show refused every past show, yet reported them sent.
    import finalize_thankyou
    venue, band, email = "Fountain Square", "Thanks After Band", "thanksafterband@example.test"
    sid = db_upsert_show(db_upsert_artist(band, email), venue, TODAY - dt.timedelta(days=1), series="Jazz on the Square")
    x("""UPDATE shows SET responded_at=now(), thankyou_sent_at=NULL, thankyou_error=NULL,
                           cancelled_at=NULL, held_at=NULL WHERE id=%s""", (sid,))
    n0 = mail_count()
    st, body = _run_lifecycle()
    mine = sends_to(n0, email)
    subj = (mine[0]["payload"].get("subject") or "") if mine else ""
    check(st == 200 and len(mine) == 1 and subj.startswith(f"Thanks for playing {venue}"),
          f"one post-show thank-you ({len(mine)}: {subj!r})")
    text = mine[0]["payload"].get("body", "") if mine else ""
    check("See you" not in text and "You're All Set" not in text, "post-show copy, not the pre-show 'All Set' email")
    row = q("SELECT thankyou_sent_at, thankyou_error FROM shows WHERE id=%s", (sid,), one=True)
    check(row["thankyou_sent_at"] is not None and not row["thankyou_error"], f"stamped sent ({row})")
    try:
        reported = json.loads(body).get("thankyou") or []
    except ValueError:
        reported = []
    check(any(t.get("artist_name") == band for t in reported), "the run reports it by name")
    n1 = mail_count()
    _run_lifecycle()
    check(not sends_to(n1, email), "the next run sends nothing more")
    sid2 = db_upsert_show(db_upsert_artist("Thanks Manual Band", "thanksmanualband@example.test"),
                          venue, TODAY - dt.timedelta(days=3), series="Jazz on the Square")
    x("UPDATE shows SET thankyou_sent_at=NULL, thankyou_error=NULL, cancelled_at=NULL WHERE id=%s", (sid2,))
    ok = finalize_thankyou.send_for_show(sid2)
    row2 = q("SELECT thankyou_sent_at, thankyou_error FROM shows WHERE id=%s", (sid2,), one=True)
    check(ok is False and row2["thankyou_sent_at"] is None and row2["thankyou_error"] == "skipped: show already past",
          f"manual Finalize still refuses a past show ({row2})")
    MAIL_PER_TEST["x-at"] = sends_since(n0)


@test("x-au: the Status Log table spans its hidden Show ID column")
def tx_status_log_table():
    # 2026-09-21 sweep (RPT-2): Show ID sat outside the Excel Table, so a sort
    # moved the rows but not the ids, and manual notes landed on other shows.
    from openpyxl import load_workbook
    from openpyxl.utils import range_boundaries
    r = run_tool("status_log.py")
    check(r.returncode == 0, f"status_log ran ({r.stderr[-300:]})")
    log = DROP / "Nyquist" / "Show Status Log.xlsx"
    if not log.exists():
        check(False, "Status Log written")
        return
    found = None
    for ws in load_workbook(log).worksheets:
        if "ShowStatus" in ws.tables:
            found = (ws, ws.tables["ShowStatus"])
    check(found is not None, "the ShowStatus table exists")
    if not found:
        return
    ws, tbl = found
    min_col, min_row, max_col, _max_row = range_boundaries(tbl.ref)
    id_col = next((c for c in range(min_col, ws.max_column + 1) if ws.cell(min_row, c).value == "Show ID"), None)
    check(id_col is not None and id_col == max_col, f"Show ID is the table's last column ({tbl.ref}, Show ID col {id_col})")


@test("x-av: a Salsa band's day-before email carries the band schedule, not the crew table")
def tx_salsa_dayahead():
    # 2026-09-21 sweep (RPT-5): the day-before printed the day-sheet crew table
    # ('TBD Crew Call', Load-out) and English labels inside the Spanish half.
    import dayahead
    import venue_email as ve
    venue, d, series = "Fountain Square", TODAY + dt.timedelta(days=1), "Salsa On The Square"
    band, email = "Salsa Tomorrow Band", "salsatomorrowband@example.test"
    sid = db_upsert_show(db_upsert_artist(band, email), venue, d, series=series)
    x("""UPDATE shows SET responded_at=now(), dayahead_sent_at=NULL, dayahead_error=NULL,
                           cancelled_at=NULL, held_at=NULL WHERE id=%s""", (sid,))
    x("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by, seeded_at,
                               load_in, event_start, curfew)
         VALUES (%s, %s, %s, %s, %s, 'tests', now(), '6:00p', '7:00p', '10:00p') ON CONFLICT DO NOTHING""",
      (band, venue, d, series, email))
    try:
        n0 = mail_count()
        dayahead.send_due(lambda *a: None)
        mine = [m for m in sends_since(n0) if email in _to_addrs(m)]
        check(len(mine) == 1, f"one day-before email ({len(mine)})")
        body = mine[0]["payload"].get("body", "") if mine else ""
        crew = ve.crew_schedule_for(venue, series)
        if crew:
            old = [f"  {t or 'TBD'}    {label}" for label, t in crew]
            check(not any(line in body for line in old), "none of the crew-table rows are in the band's email")
        else:
            check(True, "no crew table configured for the series — that half skipped")
        for lang in ("en", "es"):
            block = ve.schedule_block_for(venue, series, lang=lang)
            first = next((ln.strip() for ln in (block or "").splitlines() if ln.strip()), None)
            check(first is None or first in body, f"the series' own {lang} schedule block is there ({first!r})")
        check("ESPAÑOL / SPANISH VERSION BELOW" in body, "bilingual")
        MAIL_PER_TEST["x-av"] = sends_since(n0)
    finally:
        x("DELETE FROM bookings WHERE venue=%s AND event_date=%s AND artist_name=%s", (venue, d, band))
        x("UPDATE shows SET cancelled_at=now() WHERE id=%s", (sid,))


@test("x-aw: crew call/curfew are never borrowed from another event on a double-booked day")
def tx_event_times_never_guess():
    # 2026-09-21 sweep (RPT-6): the first parseable Event row won, so a
    # 3rd-party doc got Final Fridays' crew call and curfew.
    d = TODAY + dt.timedelta(days=82)

    def row(event):
        r = [""] * 16
        r[6], r[8] = d.strftime("%m/%d/%Y"), event
        return r
    rows = [row("Final Fridays (4-11)"), row("Acme Corp Party (6-10)")]
    real = staffing._fetch_csv
    staffing._fetch_csv = lambda gid, timeout=10: rows
    try:
        fsq = "Fountain Square"
        check(staffing.event_times_for(fsq, d, series="3rd Party") is None,
              "nothing names the show and no start to place it: no times, not the first row's")
        check(staffing.event_times_for(fsq, d, series="Final Fridays") == {"crew_call": "4:00p", "curfew": "11:00p"},
              "the row naming the series wins")
        check(staffing.event_times_for(fsq, d, series="3rd Party", event_name="Acme Corp Party")
              == {"crew_call": "6:00p", "curfew": "10:00p"}, "the row naming the event wins")
        check(staffing.event_times_for(fsq, d, series="3rd Party", event_start="10:30p")
              == {"crew_call": "4:00p", "curfew": "11:00p"}, "the one row whose range holds the set start")
        rows[:] = [row("Jazz (3:30-10)")]
        check(staffing.event_times_for(fsq, d) == {"crew_call": "3:30p", "curfew": "10:00p"},
              "a single event that day still fills")
    finally:
        staffing._fetch_csv = real


@test("x-ax: a finished lifecycle run stamps its own done row, and the watchdog alerts at most once")
def tx_lifecycle_done_stamp():
    # 2026-09-21 sweep (OPS-7): the watchdog read the START stamp, so a run
    # that crashed after it was never reported.
    t0 = q("SELECT now() AS t", one=True)["t"]
    st, _ = _run_lifecycle()
    check(st == 200, f"lifecycle ran ({st})")
    done = q("SELECT 1 FROM job_runs WHERE job='advance-lifecycle-done' AND source='test' AND ran_at >= %s",
             (t0,), one=True)
    check(done is not None, "a completed run records advance-lifecycle-done")
    n0 = mail_count()
    bodies = []
    early = dt.datetime.now().time() < dt.time(9, 59)   # both calls land before the 10:00 cutoff
    for _ in range(2):
        st, body = post("/internal/lifecycle-watchdog", json_body={}, headers={"X-Advance-Token": TOKEN})
        check(st == 200, f"watchdog answered ({st} {body[:120]})")
        bodies.append(body)
    alerts = [m for m in sends_since(n0) if "9am check did NOT finish" in (m["payload"].get("subject") or "")]
    check(len(alerts) <= 1, f"two watchdog calls, at most one alert ({len(alerts)})")
    if early:
        check(all("before-10am" in b_ for b_ in bodies), "before 10:00 the watchdog stands down")


@test("x-ay: a sheet row with no usable date mints no show, run after run")
def tx_dateless_row():
    # 2026-09-21 sweep (DBB-6): NULL never hits uq_shows_booking, so every
    # pipeline run inserted another dateless shows row.
    batch = T / "batch_nodate.json"
    batch.write_text(json.dumps([{"name": "Dateless Row Band", "show_date": "TBD", "venue": "Fountain Square",
                                  "series": "Jazz on the Square", "email": "datelessrowband@example.test"}]))
    out = T / "drafts_nodate"
    for i in (1, 2):
        r = run_tool("draft_emails.py", batch, "--out", out)
        check(r.returncode == 0 and "no parseable show date" in r.stderr, f"run {i}: the row is skipped, said so")
    n = q("""SELECT count(*) AS n FROM shows s JOIN artists a ON a.id=s.artist_id WHERE a.match_key=%s""",
          (db.normalize("Dateless Row Band"),), one=True)["n"]
    check(n == 0, f"no shows row minted ({n})")


@test("x-az: a Start fixed in the sheet survives an unrelated app edit of the same booking")
def tx_sheet_edit_survives():
    # 2026-09-21 sweep (FLOW-12): the write-back rewrote every booking-owned
    # column that differed from the sheet, reverting Brian's own sheet fix.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=68), "Sheet Start Band"
    email = "sheetstartband@example.test"
    hhmm, house = _book_free(band, venue, d, email, 42)
    if not hhmm:
        return
    check(wait_run_now(), "booked + seeded")
    rows = sheet_rows_for(band, venue, d)
    check(len(rows) == 1 and rows[0].get("event_start") == house, f"the sheet row says {house}")
    fixed = house.replace(":42", ":52")
    check(_sheet_set(band, venue, "event_start", fixed) == 1, f"Brian retyped Start as {fixed} in the sheet")
    b = booking_for(band, venue, d)
    st, _ = post(f"/booking/{b['id']}/edit", booking_data(band, venue, d, hhmm, "22:30", event_start=house,
                                                         contact_email=email, lead_phone="555-0842"))
    check(st == 200, f"an unrelated edit (lead phone) saved ({st})")
    check(wait_run_now(), "edit run finished")
    rows = sheet_rows_for(band, venue, d)
    check(len(rows) == 1 and rows[0].get("event_start") == fixed,
          f"the sheet's Start survived ({rows and rows[0].get('event_start')})")
    check(rows and rows[0].get("lead_phone") == "555-0842", f"the edited field was written ({rows and rows[0].get('lead_phone')})")


@test("x-ba: a band name corrected in the sheet is not re-appended under the old spelling")
def tx_sheet_correction():
    # 2026-09-21 sweep (PIPE-3): run_now's reconcile re-appended the booked
    # spelling, so holds.py never asked and the band was welcomed twice.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=69)
    typo, fixed = "Laurelys Sheet Band", "Laurelies Sheet Band"
    if not _book_free(typo, venue, d, "laurelyssheetband@example.test", 43)[0]:
        return
    check(wait_run_now(), "booked + seeded")
    check(len(sheet_rows_for(typo, venue, d)) == 1, "the booked spelling is on the sheet")
    check(_sheet_set(typo, venue, "artist_name", fixed) == 1, "Brian corrected the name in the sheet")
    r = run_tool("run_now.py")
    check(r.returncode == 0, f"run_now ok ({r.stderr[-300:]})")
    check(not sheet_rows_for(typo, venue, d) and len(sheet_rows_for(fixed, venue, d)) == 1,
          "the old spelling was not re-appended")
    old, new = show_for(typo, venue, d), show_for(fixed, venue, d)
    check(old and old["held_at"] and old["hold_reason"] == "missing from the advance sheet",
          f"the booked show is held for Brian ({old and old['hold_reason']})")
    check(old and new and new["hold_reason"] == f"possible correction of show {old['id']}",
          f"the corrected row's show is offered as its correction ({new and new['hold_reason']})")


@test("x-bb: a send that timed out (outcome unknown) is stamped done and flagged, never re-sent")
def tx_timeouts_not_resent():
    # 2026-09-21 sweep (MAIL-5, PRIOR-13): only the welcome honoured the
    # TIMEOUT marker; notices, day-befores and thank-yous re-sent next run.
    # mailer.send is patched in THIS process only (booking_update, dayahead
    # and finalize_thankyou run here); every other address still hits the stub.
    import booking_update
    import dayahead
    import finalize_thankyou
    venue = "Fountain Square"
    notice_to, tomorrow_to, thanks_to = ("timeoutnoticeband@example.test", "timeouttomorrowband@example.test",
                                         "timeoutthanksband@example.test")
    ours = {notice_to, tomorrow_to, thanks_to}
    real_send = mailer.send

    def fake_send(to, subject, *a, **k):
        if ours & {p.strip().lower() for p in str(to or "").split(",")}:
            return False, "TIMEOUT: staging stub — Graph didn't answer in 90s"
        return real_send(to, subject, *a, **k)
    fails = []
    d = TODAY + dt.timedelta(days=77)
    sid = db_upsert_show(db_upsert_artist("Timeout Notice Band", notice_to), venue, d, series="Jazz on the Square")
    x("UPDATE shows SET advance_draft_created_at=now(), cancelled_at=NULL, held_at=NULL WHERE id=%s", (sid,))
    sid2 = db_upsert_show(db_upsert_artist("Timeout Tomorrow Band", tomorrow_to), venue,
                          TODAY + dt.timedelta(days=1), series="Jazz on the Square")
    x("""UPDATE shows SET responded_at=now(), dayahead_sent_at=NULL, dayahead_error=NULL,
                           cancelled_at=NULL, held_at=NULL WHERE id=%s""", (sid2,))
    sid3 = db_upsert_show(db_upsert_artist("Timeout Thanks Band", thanks_to), venue,
                          TODAY - dt.timedelta(days=2), series="Jazz on the Square")
    x("""UPDATE shows SET responded_at=now(), thankyou_sent_at=NULL, thankyou_error=NULL,
                           cancelled_at=NULL, held_at=NULL WHERE id=%s""", (sid3,))
    bid = None
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("""INSERT INTO bookings (artist_name, venue, event_date, series, contact_email, entered_by,
                                                  load_in, event_start, curfew)
                           VALUES ('Timeout Notice Band', %s, %s, 'Jazz on the Square', %s, 'tests',
                                   '6:00p', '7:00p', '10:00p') RETURNING id""", (venue, d, notice_to))
            bid = cur.fetchone()["id"]
            _ch, notify = db.update_booking(cur, bid, dict(db.get_booking(cur, bid), load_in="6:15p"))
            conn.commit()
        check(notify, "a welcomed band's load-in change queues a notice")
        mailer.send = fake_send
        try:
            booking_update.send_due(lambda s_, k, e: fails.append((s_, k)))
            dayahead.send_due(lambda s_, k, e: fails.append((s_, k)))
            thanked = finalize_thankyou.send_for_show(sid3, after_show=True)
        finally:
            mailer.send = real_send
        e = q("SELECT sent_at, error FROM booking_edits WHERE booking_id=%s AND notify ORDER BY id DESC LIMIT 1",
              (bid,), one=True)
        check(e and e["sent_at"] is not None and (e["error"] or "").startswith("TIMEOUT:")
              and (sid, "booking_update_unknown") in fails, f"notice: stamped done, flagged unknown ({e})")
        t2 = q("SELECT dayahead_sent_at, dayahead_error FROM shows WHERE id=%s", (sid2,), one=True)
        check(t2["dayahead_sent_at"] is not None and (t2["dayahead_error"] or "").startswith("TIMEOUT:")
              and (sid2, "dayahead_unknown") in fails, f"day-before: stamped done, flagged unknown ({t2})")
        t3 = q("SELECT thankyou_sent_at, thankyou_error FROM shows WHERE id=%s", (sid3,), one=True)
        check(thanked is False and t3["thankyou_sent_at"] is not None
              and "outcome unknown" in (t3["thankyou_error"] or ""), f"thank-you: stamped done, flagged ({t3})")
        n0 = mail_count()
        booking_update.send_due(lambda *a: None)
        dayahead.send_due(lambda *a: None)
        finalize_thankyou.send_for_show(sid3, after_show=True)
        again = [m for m in sends_since(n0) if ours & _to_addrs(m)]
        check(not again, f"nothing re-sent on the next run ({len(again)})")
    finally:
        if bid:
            x("DELETE FROM bookings WHERE id=%s", (bid,))
        x("UPDATE shows SET cancelled_at=now() WHERE id = ANY(%s)", ([sid, sid2],))


@test("x-bc: a 'Keep doc' clicked while a merge ran is re-applied to the merge's final write")
def tx_keep_doc_reapplied():
    # 2026-09-21 sweep (DOC-3): the running pass re-owned the kept cell, so a
    # later pass wrote the value Brian had rejected.
    d = TODAY + dt.timedelta(days=79)
    with db.get_conn() as conn, conn.cursor() as cur:
        def notice(key, doc_value, kept):
            cur.execute("""INSERT INTO doc_notices (venue, event_date, event_key, kind, field, new_value,
                                                    doc_value, cell_key, resolved_at, resolution)
                           VALUES ('Fountain Square', %s, 'keep race test', 'diff', %s, 'new', %s, %s,
                                   CASE WHEN %s THEN now() END, CASE WHEN %s THEN 'kept' END)
                           RETURNING id""", (d, key, doc_value, key, kept, kept))
            return cur.fetchone()["id"]
        ids = [notice("Monitors|a901", "6 wedges (per Brian)", True),
               notice("Backline|col2", "(cleared by hand)", True),
               notice("Stage Type|a901", "Riser", False)]
        cells = {"Monitors|a901": "4 wedges", "Backline|a902": "two amps", "Stage Type|a901": "Flat stage"}
        out = db.reapply_kept_decisions(cur, ids, dict(cells), {"2": 902})
        conn.rollback()
    check("Monitors|a901" not in out, f"a kept cell is given up by the pass ({out})")
    check("Backline|a902" not in out and out.get("Backline|col2") == "∅ kept blank",
          "a legacy column key maps to the artist key; a hand-cleared cell stays marked kept-blank")
    check(out.get("Stage Type|a901") == "Flat stage", "an undecided notice changes nothing")


@test("x-bd: an apply that never finished re-enables the choice instead of spinning forever")
def tx_stale_apply():
    # 2026-09-21 sweep (DOC-5): a crashed or locked-out apply left both radios
    # disabled on 'Writing it into the doc…' with the page reloading forever.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=75)
    ids = []
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            for field, mins in (("Monitors (stale apply)", 35), ("Backline (fresh apply)", 0)):
                cur.execute("""INSERT INTO doc_notices (venue, event_date, event_key, kind, field, new_value,
                                                        doc_value, cell_key, apply_requested_at)
                               VALUES (%s, %s, 'stale apply test', 'diff', %s, 'new', 'old', %s, %s)
                               RETURNING id""",
                            (venue, d, field, f"{field.split()[0]}|a903",
                             dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=mins)))
                ids.append(cur.fetchone()["id"])
            conn.commit()
        st, body = get(f"/doc-review?venue={urllib.parse.quote(venue)}&date={d.isoformat()}")
        check(st == 200 and "the apply never finished — pick again" in body,
              f"a 35-minute-old apply is shown as failed ({st})")
        check("Writing it into the doc…" in body, "a fresh one still shows as in progress")
    finally:
        if ids:
            x("DELETE FROM doc_notices WHERE id = ANY(%s)", (ids,))


@test("x-be: Merge's confirm dialog survives a band name with an apostrophe")
def tx_confirm_apostrophe():
    # 2026-09-21 sweep (APPB-9): the name broke the onsubmit JS, the browser
    # dropped the handler, and Merge fired with no confirmation.
    login()
    venue, d = "Fountain Square", TODAY + dt.timedelta(days=74)
    sid = db_upsert_show(db_upsert_artist("Rosie's Test Rhythm", "rosiestestrhythm@example.test"), venue, d,
                         series="Jazz on the Square")
    sid2 = db_upsert_show(db_upsert_artist("Rosies Test Rhythm Band", "rosiestestrhythmband@example.test"), venue, d,
                          series="Jazz on the Square")
    x("""UPDATE shows SET held_at=now(), hold_reason='missing from the advance sheet', cancelled_at=NULL
         WHERE id=%s""", (sid,))
    try:
        st, html = get(f"/show/{sid}/hold")
        check(st == 200 and "Rosies Test Rhythm Band" in html, f"the hold page lists the candidate ({st})")
        check("confirm('Merge Rosie" not in html, "no single-quoted JS string for the name to break")
        check('confirm("Merge Rosie\\u0027s Test Rhythm' in html, "the name is JSON-escaped inside confirm()")
    finally:
        x("UPDATE shows SET cancelled_at=now(), held_at=NULL WHERE id = ANY(%s)", ([sid, sid2],))


@test("x-bf: a RiffPay re-import never touches an act that's already booked")
def tx_riffpay_rerun():
    # 2026-09-21 sweep (RPT-1): seed_bookings deleted and re-inserted every
    # act, wiping staff flags and cascading away queued 'info changed' notices.
    import import_riffpay as rp
    check(rp.same_act("DJ Bravo", "Bravo") and rp.same_act("  The  Band ", "the band"), "same act: whole-word containment")
    check(not rp.same_act("Soul Revival", "Soul Collective") and not rp.same_act("Bravo", "Bravoz"),
          "not the same act: a shared word, or a longer word")
    venue, d, band = "Washington Park", TODAY + dt.timedelta(days=78), "Riffpay Keep Band"
    bid = None
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("""INSERT INTO bookings (artist_name, venue, event_date, series, location, contact_email,
                                                  entered_by, lead_name, skip_welcome_email, event_start)
                           VALUES (%s, %s, %s, 'Jazz At The Porch', 'Porch', 'riffpaykeepband@example.test',
                                   'tests', 'Staff Lead', true, '7:00p') RETURNING id""", (band, venue, d))
            bid = cur.fetchone()["id"]
            cur.execute("""INSERT INTO booking_edits (booking_id, changes, edited_by, notify)
                           VALUES (%s, %s::jsonb, 'tests', true) RETURNING id""",
                        (bid, json.dumps({"load_in": {"old": "6:00p", "new": "6:15p"}})))
            eid = cur.fetchone()["id"]
            conn.commit()
        ev = {"venue": venue, "event_date": d, "event_name": "", "location": "Porch", "series": "Jazz At The Porch",
              "curfew": "", "acts": [{"artist_name": band, "contact_email": "riffpay-new@example.test",
                                      "event_start": "7:30p"},
                                     {"artist_name": f"DJ {band}", "contact_email": "", "event_start": "7:00p"}]}
        check(rp.match_existing_bookings([ev])
              and all((a.get("existing_booking") or {}).get("id") == bid for a in ev["acts"]),
              f"both RiffPay spellings match the existing booking ({[a.get('existing_booking') for a in ev['acts']]})")
        check(rp.seed_bookings([ev]) == (0, 2), "nothing inserted, both left as already booked")
        b = q("SELECT * FROM bookings WHERE id=%s", (bid,), one=True)
        check(b and b["skip_welcome_email"] and b["lead_name"] == "Staff Lead" and b["event_start"] == "7:00p",
              f"the booking is exactly as staff left it ({b and (b['skip_welcome_email'], b['lead_name'], b['event_start'])})")
        check(q("SELECT 1 FROM booking_edits WHERE id=%s AND sent_at IS NULL", (eid,), one=True),
              "its queued 'info changed' notice survived")
        rows = q("""SELECT id FROM bookings WHERE venue=%s AND event_date=%s
                    AND lower(artist_name) LIKE %s""", (venue, d, "%riffpay keep band%"))
        check([r_["id"] for r_ in rows] == [bid], f"no second booking row ({[r_['id'] for r_ in rows]})")
    finally:
        if bid:
            x("DELETE FROM bookings WHERE id=%s", (bid,))


@test("x-bg: renaming a bill's event keeps its open doc decisions with its doc")
def tx_event_rename_rekeys():
    # 2026-09-21 sweep (IDENT-11): the event_key changed with the name, the
    # registry row followed but its notices didn't, so they stopped freezing
    # cells and Keep doc / Use new lost the doc.
    login()
    venue, d, band = "Fountain Square", TODAY + dt.timedelta(days=83), "Rekey Event Band"
    email = "rekeyeventband@example.test"
    hhmm, house = _book_free(band, venue, d, email, 48, event_name="Rekey Night Alpha")
    if not hhmm:
        return
    check(wait_run_now(), "booked + filed")
    reg = q("SELECT id, event_key FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    s = show_for(band, venue, d)
    check(len(reg) == 1 and reg[0]["event_key"] == "rekey night alpha" and s,
          f"one doc filed under the event's key ({[r_['event_key'] for r_ in reg]})")
    if len(reg) != 1 or not s:
        return
    nid = None
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("""INSERT INTO doc_notices (venue, event_date, event_key, kind, field, new_value,
                                                    doc_value, cell_key)
                           VALUES (%s, %s, 'rekey night alpha', 'diff', 'Backline (rekey probe)', 'probe amps',
                                   '(blank)', %s) RETURNING id""", (venue, d, f"Backline|a{s['artist_id']}"))
            nid = cur.fetchone()["id"]
            conn.commit()
        b = booking_for(band, venue, d)
        st, _ = post(f"/booking/{b['id']}/edit",
                     booking_data(band, venue, d, hhmm, "22:30", event_start=house, contact_email=email,
                                  event_name="Rekey Night Bravo"))
        check(st == 200, f"event renamed ({st})")
        check(wait_run_now(), "rename run finished")
        r = run_tool("run_now.py")
        check(r.returncode == 0, "another full pass ok")
        reg2 = q("SELECT id, event_key FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
        check(len(reg2) == 1 and reg2[0]["id"] == reg[0]["id"] and reg2[0]["event_key"] == "rekey night bravo",
              f"the same registry row, re-keyed; no second doc ({[(r_['id'], r_['event_key']) for r_ in reg2]})")
        n = q("SELECT event_key, resolved_at FROM doc_notices WHERE id=%s", (nid,), one=True)
        check(n and n["event_key"] == "rekey night bravo" and n["resolved_at"] is None,
              f"the open decision moved with it ({n})")
    finally:
        if nid:
            x("DELETE FROM doc_notices WHERE id=%s", (nid,))


@test("x-z: nothing left the box")
def tx_iso():
    bad = [m for m in mails() if not m["path"].startswith("/webhook/")]
    check(not bad, f"every mail hit the stub webhooks only ({len(bad)} odd)")


def main():
    tests = [v for v in globals().values() if callable(v) and getattr(v, "_test_name", "").startswith("x-")]
    for fn in tests:
        if ONLY_X and ONLY_X not in fn._test_name:
            continue
        print(f"\n== {fn._test_name}", flush=True)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, f"raised {e!r}")
    n_ok = sum(1 for ok, _ in rt.RESULTS if ok)
    n = len(rt.RESULTS)
    print(f"\n{n_ok}/{n} checks passed")
    for ok, msg in rt.RESULTS:
        if not ok:
            print("  FAILED:", msg)
    print("\nstub sends per test:")
    for k, v in MAIL_PER_TEST.items():
        print(f"  {k}: {len(v)} send(s) " + "; ".join(f"{m['payload'].get('to')} <{(m['payload'].get('subject') or '')[:50]}>" for m in v))
    sys.exit(0 if n_ok == n else 1)


if __name__ == "__main__":
    main()
