#!/usr/bin/env python3
"""3CDC Band Advance — public intake form + prefill + gated search view.

Design rule (never break the live form): a submission is saved to DISK FIRST,
then written to Postgres best-effort. A DB outage logs a warning and the artist
still gets the thank-you page. The disk JSON remains the durable record and the
backfill tool can replay anything the DB missed.
"""
import json
import re
import subprocess
import sys
import datetime as dt
import mimetypes
from pathlib import Path

from flask import (
    Flask, render_template, request, abort, session,
    redirect, url_for, send_from_directory,
)
from urllib.parse import quote
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeSerializer, BadData

import forms_config

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
UPLOADS = DATA / "uploads"
LOG = DATA / "db_errors.log"
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

import os
SECRET = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
GATE_PASS = os.environ.get("ADVANCE_GATE_PASS", "lockdown")
INTERNAL_TOKEN = os.environ.get("ADVANCE_INTERNAL_TOKEN", "")
PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
NOTIFY_URL = os.environ.get("ADVANCE_NOTIFY_URL", "")
TOOLS_DIR = BASE / "tools"

app = Flask(__name__)
app.secret_key = SECRET
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB cap on the stage-plot upload
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,  # served over HTTPS via the Cloudflare tunnel
)

_signer = URLSafeSerializer(SECRET, salt="advance-prefill")

# advance_db is optional at import time so the form still runs if psycopg is missing
try:
    import advance_db
    DB_OK = True
except Exception as e:  # pragma: no cover
    advance_db = None
    DB_OK = False
    (DATA / "db_import_error.log").write_text(f"{dt.datetime.now()}: {e}\n")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "band").lower()).strip("-")[:40] or "band"


def us_date(d):
    """M/D/Y for anything shown in a drafted email — matches draft_emails.py's
    own convention."""
    return d.strftime("%m/%d/%Y") if d else ""


def _log_db_error(context, err):
    with LOG.open("a") as fh:
        fh.write(f"{dt.datetime.now().isoformat()}  {context}: {err!r}\n")


def make_prefill_token(artist_id, show=None):
    """Signed, stateless token for a returning-artist link. show is optional
    context (venue/date) so the prefilled form can target the right booking."""
    return _signer.dumps({"a": artist_id, "s": show})


def read_prefill_token(token):
    try:
        return _signer.loads(token)
    except BadData:
        return None


# ── public form ─────────────────────────────────────────────────────────────

@app.get("/")
def form():
    cfg = forms_config.get_config(
        series_key=request.args.get("series"),
        venue=request.args.get("venue"),
    )
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill={}, returning=False, artist_name=None,
        tech_packs=forms_config.tech_packs(),
    )


@app.get("/s/<code>")
def short_link(code):
    """Short redirect for an emailed /f/<token> link — the signed token is long
    (venue + date + series + signature); emails carry this instead."""
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        token = advance_db.resolve_short_link(cur, code)
    if not token:
        abort(404)
    return redirect(url_for("prefilled_form", token=token))


@app.get("/f/<token>")
def prefilled_form(token):
    """Pre-addressed link from the advance list. The token seeds band name + venue
    + date + series from the sheet row (so a first-time band opens the form already
    addressed); a returning band also gets their prior answers pre-filled."""
    payload = read_prefill_token(token) or {}
    seed = payload.get("s") or {}
    series = seed.get("series") or request.args.get("series")
    cfg = forms_config.get_config(
        series_key=series, venue=seed.get("venue") or request.args.get("venue"))
    prefill, returning, artist_name = {}, False, None
    if payload.get("a") and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                artist = advance_db.get_artist(cur, payload["a"])
                sub = advance_db.newest_submission(cur, payload["a"]) if artist else None
            if artist:
                artist_name = artist["name"]
                base = {}
                if sub:
                    base = dict(sub.get("data") or {})  # prior answers
                    base.pop("show_date", None)
                    returning = True
                # identity from the sheet row wins over any prior submission
                seed_fields = {"band_name": artist["name"]}
                if seed.get("venue"):
                    seed_fields["venue"] = seed["venue"]
                if seed.get("date"):
                    seed_fields["show_date"] = seed["date"]
                prefill = {**base, **seed_fields}
                if not cfg.get("venue_preselect"):
                    cfg["venue_preselect"] = prefill.get("venue")
        except Exception as e:
            _log_db_error("prefill", e)
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill=prefill, returning=returning, artist_name=artist_name,
        tech_packs=forms_config.tech_packs(),
    )


@app.post("/submit")
def submit():
    f = request.form
    if not f.get("band_name"):
        abort(400, "Band name is required.")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = _slug(f.get("band_name"))
    rec = {k: v for k, v in f.items()}
    rec["_submitted_at"] = dt.datetime.now().isoformat(timespec="seconds")

    file_info = None
    upload = request.files.get("stage_plot_file")
    if upload and upload.filename:
        safe = secure_filename(upload.filename)
        stored = f"{stamp}__{slug}__{safe}"
        dest = UPLOADS / stored
        upload.save(dest)
        rec["stage_plot_file"] = stored
        file_info = {
            "filename": upload.filename, "stored_name": stored,
            "mime": upload.mimetype,
            "size": dest.stat().st_size if dest.exists() else None,
        }

    # 1) DISK FIRST — the durable record. Never fails the request over the DB.
    (DATA / f"{stamp}__{slug}.json").write_text(json.dumps(rec, indent=2))

    # 2) Postgres, best-effort.
    if DB_OK:
        try:
            advance_db.record_submission(rec, file_info=file_info, source="form")
        except Exception as e:
            _log_db_error("record_submission", e)

    # 3) Notify, best-effort (Slack webhook if configured; summary email always).
    _notify_submission(rec)
    _notify_email("submission", rec)

    # 4) Run the pipeline in the background — doc/day-sheet/email drafts/venue
    # tree/sheet status all catch up on this response without anyone clicking
    # anything. Fire-and-forget: the band's thank-you page never waits on it.
    _run_pipeline_background()

    return render_template("thanks.html", band=f.get("band_name"))


def _notify_submission(rec):
    hook = os.environ.get("ADVANCE_SLACK_WEBHOOK")
    if not hook:
        return
    try:
        import urllib.request
        text = (f":memo: Band advance received — *{rec.get('band_name')}* "
                f"@ {rec.get('venue')} on {rec.get('show_date')} "
                f"({rec.get('performers')} ppl)")
        req = urllib.request.Request(
            hook, data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        _log_db_error("slack_notify", e)


def _notify_email(event_type, fields):
    """Fire the n8n 'Advance Notify' webhook — a quick-glance summary email for a
    new booking or a completed advance form. Best-effort: never blocks or breaks
    the request the event came from."""
    if not NOTIFY_URL:
        return
    try:
        import urllib.request
        body = json.dumps({"event_type": event_type, **fields}).encode()
        req = urllib.request.Request(
            NOTIFY_URL, data=body,
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN},
        )
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        _log_db_error("notify_email", e)


def _run_pipeline_background():
    """Kick off run_now.py in the background — never blocks or risks the request
    it's called from. Detached (start_new_session) so it outlives this worker.
    run_now.py's own lock file makes overlapping triggers (this + the booking
    button) safe."""
    try:
        subprocess.Popen(
            [sys.executable, "run_now.py"], cwd=TOOLS_DIR,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        _log_db_error("run_pipeline_background", e)


# ── gated views (passcode) ──────────────────────────────────────────────────

GATED_PREFIXES = ("/search", "/artist", "/file", "/submission", "/booking")


@app.before_request
def _gate():
    p = request.path
    if p.startswith(GATED_PREFIXES) and not session.get("auth"):
        return redirect(url_for("gate", next=p))


@app.route("/gate", methods=["GET", "POST"])
def gate():
    if request.method == "POST":
        if request.form.get("passcode") == GATE_PASS:
            session["auth"] = True
            return redirect(request.args.get("next") or url_for("search"))
        return render_template("gate.html", error="Incorrect passcode."), 403
    return render_template("gate.html", error=None)


BOOKING_SLOTS = ["headliner", "direct_support", "opener"]


def _series_by_venue():
    """Best-effort — an empty dict just means the form falls back to a plain
    '+ Add new series…' entry, never blocks the booking form from loading.
    Ordered to match forms_config.VENUES; any venue name in the data that
    isn't in that list (renamed/retired venue) sorts to the end."""
    if not DB_OK:
        return {}
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            raw = advance_db.series_by_venue(cur)
    except Exception as e:
        _log_db_error("series_by_venue", e)
        return {}
    ordered = {}
    for v in forms_config.VENUES:
        if v in raw:
            ordered[v] = raw[v]
    for v, opts in raw.items():
        if v not in ordered:
            ordered[v] = opts
    return ordered


@app.route("/booking", methods=["GET", "POST"])
def booking():
    """Short staff intake form for a new artist booking. Writes to the bookings
    table; the next generate seeds it into the master spreadsheet."""
    if request.method == "POST":
        f = request.form
        if not f.get("artist_name") or not f.get("event_name"):
            return render_template("booking.html", venues=forms_config.VENUES,
                                   slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                                   error="Event name and artist name are required.",
                                   form=f), 400
        data = {k: (f.get(k) or "").strip() for k in advance_db.BOOKING_FIELDS}
        saved = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    advance_db.insert_booking(cur, data)
                    conn.commit()
                saved = True
            except Exception as e:
                _log_db_error("insert_booking", e)
        if not saved:
            return render_template("booking.html", venues=forms_config.VENUES,
                                   slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                                   error="Couldn't save — the database is unreachable. Try again shortly.",
                                   form=f), 503
        _notify_email("booking", data)
        return render_template("booking.html", venues=forms_config.VENUES,
                               slots=BOOKING_SLOTS, saved=data)
    return render_template("booking.html", venues=forms_config.VENUES,
                           slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(), form={})


@app.post("/booking/run")
def booking_run():
    """Thank-you-page button: seed the sheet, build the package, file the venue
    tree, fold status back in — all local now that the sheet lives on this box
    too (Dropbox-synced). Gated same as /booking. Idempotent (run_now.py locks
    against overlap); safe to click more than once."""
    try:
        p = subprocess.run(
            [sys.executable, "run_now.py"], cwd=TOOLS_DIR,
            capture_output=True, text=True, timeout=240,
        )
    except subprocess.TimeoutExpired:
        return {"error": "timed out after 240s"}, 504
    line = (p.stdout or "").strip().splitlines()[-1] if p.stdout else ""
    try:
        result = json.loads(line)
    except (ValueError, IndexError):
        return {"error": "bad output", "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}, 500
    if "error" in result:
        return result, 500
    return result


@app.get("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                results = advance_db.search_artists(cur, q)
        except Exception as e:
            _log_db_error("search", e)
    return render_template("search.html", q=q, results=results, db_ok=DB_OK)


@app.get("/artist/<int:artist_id>")
def artist_detail(artist_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        artist = advance_db.get_artist(cur, artist_id)
        if not artist:
            abort(404)
        shows = advance_db.artist_shows(cur, artist_id)
        subs = advance_db.artist_submissions(cur, artist_id)
        files_by_sub = {s["id"]: advance_db.submission_files(cur, s["id"]) for s in subs}
    return render_template("artist.html", artist=artist, shows=shows,
                           subs=subs, files_by_sub=files_by_sub)


@app.get("/file/<int:file_id>")
def download_file(file_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE id=%s", (file_id,))
        row = cur.fetchone()
    if not row or not row.get("stored_name"):
        abort(404)
    return send_from_directory(UPLOADS, row["stored_name"], as_attachment=True,
                               download_name=row.get("filename") or row["stored_name"])


@app.post("/internal/run-followups")
def run_followups():
    """Called by the n8n daily check. Finds advances that are follow-up due
    (emailed, no response, past the window) and queues a reminder draft for each.
    Idempotent — a band already queued is skipped. Token-protected; nothing sends."""
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    queued = []
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT show_id, band, venue, show_date, show_series, contact_email
                   FROM advance_status WHERE state = 'followup_due'"""
            )
            for r in cur.fetchall():
                link = f"{PUBLIC_URL}/?venue={quote(r['venue'] or '')}"
                if r.get("show_series"):
                    link += f"&series={quote(r['show_series'])}"
                when = f" on {r['show_date']}" if r.get("show_date") else ""
                subject = f"Reminder — advance details for your 3CDC show ({r['venue']}{when})"
                body = (
                    f"Hi {r['band']},\n\n"
                    f"Circling back on the advance for your show at {r['venue']}{when}. "
                    "We still need your show details to run it well — stage plot, monitors, "
                    "hospitality, and a couple of site logistics. It takes about five minutes:\n\n"
                    f"{link}\n\n"
                    "If you've already sent this over, disregard. Thanks,\n"
                    "3CDC Events / Production"
                )
                cur.execute(
                    """INSERT INTO followup_queue (show_id, band, contact_email, subject, body)
                       VALUES (%s,%s,%s,%s,%s)
                       ON CONFLICT (show_id) DO NOTHING RETURNING id""",
                    (r["show_id"], r["band"], r["contact_email"], subject, body),
                )
                if cur.fetchone():
                    queued.append(r["band"])
            conn.commit()
    except Exception as e:
        _log_db_error("run_followups", e)
        return {"error": e.__class__.__name__}, 500
    return {"queued": len(queued), "bands": queued}


@app.post("/internal/advance-lifecycle")
def advance_lifecycle():
    """Called by n8n's daily 'Advance Lifecycle Check'. Two date-driven guardrails
    (Brian, 2026-09-03):
      - INITIAL advance drafts itself 21 days out from the show, for any show
        that hasn't been drafted yet. Reuses draft_emails.py as-is, so the
        NEW-vs-RETURNING 6-month cross-venue check applies automatically —
        nothing new needed there.
      - FOLLOW-UP drafts itself if nothing's heard back by 7 days out from the
        show (date-driven, not tied to when the initial went out).
    Both come back as {to, subject, body} for n8n to create as real Gmail
    drafts (never sent from here) — Brian reviews and sends. Token-protected,
    same as /internal/run-followups."""
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
    if not DB_OK:
        return {"error": "db-unavailable"}, 503

    initial, followup = [], []
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            due_initial = advance_db.shows_due_for_initial_advance(cur)
            due_followup = advance_db.shows_due_for_followup(cur)

        # ── initial advances: reuse draft_emails.py wholesale (NEW/RETURNING,
        # venue blocks, short link, bill grouping — all of it, unchanged) ──
        if due_initial:
            batch = [{
                "name": r["artist_name"], "show_date": r["show_date"].isoformat(),
                "venue": r["venue"] or "", "series": r["series"] or "",
                "email": r["email"] or "",
            } for r in due_initial]
            batch_file = TOOLS_DIR / ".lifecycle_initial_batch.json"
            batch_file.write_text(json.dumps(batch))
            try:
                subprocess.run([sys.executable, "draft_emails.py", str(batch_file)],
                               cwd=TOOLS_DIR, capture_output=True, text=True,
                               timeout=120, check=True)
            finally:
                batch_file.unlink(missing_ok=True)

            sys.path.insert(0, str(TOOLS_DIR))
            from draft_emails import slug as _dslug
            drafts_dir = TOOLS_DIR / "drafts"
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                for r in due_initial:
                    sg = _dslug(r["artist_name"])
                    hits = sorted(drafts_dir.glob(f"{sg}__{r['show_date'].isoformat()}__*.md"))
                    if not hits:
                        continue
                    text = hits[0].read_text()
                    subj_line, _, body = text.partition("\n")
                    subject = subj_line.removeprefix("Subject:").strip()
                    if not r["email"]:
                        continue
                    initial.append({"to": r["email"], "subject": subject,
                                    "body": body.lstrip("\n")})
                    advance_db.mark_advance_drafted(cur, r["show_id"])
                conn.commit()

        # ── follow-ups: date-driven, short-link, "performance detail" wording ──
        if due_followup:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                for r in due_followup:
                    if not r["email"]:
                        continue
                    token = _signer.dumps({"a": r["artist_id"],
                                           "s": {"venue": r["venue"],
                                                 "date": r["show_date"].isoformat(),
                                                 "series": r["series"] or None}})
                    code = advance_db.get_or_create_short_link(cur, token)
                    link = f"{PUBLIC_URL}/s/{code}"
                    when = f" on {us_date(r['show_date'])}" if r["show_date"] else ""
                    subject = f"Reminder — performance details for your 3CDC show ({r['venue']}{when})"
                    body = (
                        f"Hi {r['artist_name']},\n\n"
                        f"Circling back on the performance details for your show at "
                        f"{r['venue']}{when} — we still need them to run it well: stage "
                        "plot, monitors, hospitality, and a couple of site logistics. "
                        "It takes about five minutes:\n\n"
                        f"{link}\n\n"
                        "If you've already sent this over, disregard. Thanks,\n"
                        "3CDC Events / Production"
                    )
                    followup.append({"to": r["email"], "subject": subject, "body": body})
                    advance_db.mark_followup_drafted(cur, r["show_id"])
                conn.commit()
    except Exception as e:
        _log_db_error("advance_lifecycle", e)
        return {"error": e.__class__.__name__}, 500

    return {"initial": initial, "followup": followup}


@app.get("/healthz")
def healthz():
    status = {"form": "ok", "db": "unknown"}
    if DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1")
            status["db"] = "ok"
        except Exception as e:
            status["db"] = f"down: {e.__class__.__name__}"
    else:
        status["db"] = "module-missing"
    return status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8097)
