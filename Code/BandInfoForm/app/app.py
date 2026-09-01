#!/usr/bin/env python3
"""3CDC Band Advance — public intake form + prefill + gated search view.

Design rule (never break the live form): a submission is saved to DISK FIRST,
then written to Postgres best-effort. A DB outage logs a warning and the artist
still gets the thank-you page. The disk JSON remains the durable record and the
backfill tool can replay anything the DB missed.
"""
import json
import re
import datetime as dt
import mimetypes
from pathlib import Path

from flask import (
    Flask, render_template, request, abort, session,
    redirect, url_for, send_from_directory,
)
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
    )


@app.get("/f/<token>")
def prefilled_form(token):
    """Returning-artist link: prefill the form from the band's newest submission."""
    payload = read_prefill_token(token)
    cfg = forms_config.get_config(series_key=request.args.get("series"),
                                  venue=request.args.get("venue"))
    prefill, returning, artist_name = {}, False, None
    if payload and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                artist = advance_db.get_artist(cur, payload.get("a"))
                sub = advance_db.newest_submission(cur, payload.get("a")) if artist else None
            if artist:
                artist_name = artist["name"]
                if sub:
                    prefill = dict(sub.get("data") or {})
                    # band name is locked to the exact stored name; date is fresh
                    prefill["band_name"] = artist["name"]
                    prefill.pop("show_date", None)
                    returning = True
                    if not cfg.get("venue_preselect"):
                        cfg["venue_preselect"] = prefill.get("venue")
        except Exception as e:
            _log_db_error("prefill", e)
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill=prefill, returning=returning, artist_name=artist_name,
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

    # 3) Notify, best-effort (Slack webhook if configured).
    _notify_submission(rec)

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


# ── gated views (passcode) ──────────────────────────────────────────────────

GATED_PREFIXES = ("/search", "/artist", "/file", "/submission")


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
