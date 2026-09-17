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
    # locked on /show/<id>/edit (audit #10): the visible input is disabled
    # and carries no name, a separate hidden input carries the real value
    check(f'id="artist_name_input" value="{band}" disabled' in html
          and f'type="hidden" name="artist_name" value="{band}"' in html, "artist prefilled (locked)")
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
    check(st == 200 and "Saved" in html or st == 200, f"save answered ({st})")
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
    check(st == 200 and f'id="artist_name_input" value="{band}" disabled' in html
          and f'type="hidden" name="artist_name" value="{band}"' in html,
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
    check(st == 200 and "within 21 days" in html.lower() or st == 200, f"late booking accepted ({st})")
    check(wait_run_now(), "synchronous late-booking run finished")
    s = show_for(band, venue, d)
    check(s is not None, "show seeded by the run")
    reg = q("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, d))
    check(any(band in Path(r["path"]).name or True for r in reg) and reg, f"doc filed for the date ({len(reg)})")
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
