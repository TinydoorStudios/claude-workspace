#!/usr/bin/env python3
"""3CDC Band Advance — public intake form + prefill + gated search view.

Design rule (never break the live form): a submission is saved to DISK FIRST,
then written to Postgres best-effort. A DB outage logs a warning and the artist
still gets the thank-you page. The disk JSON remains the durable record and the
backfill tool can replay anything the DB missed.
"""
import hmac
import ipaddress
import json
import re
import secrets
import subprocess
import sys
import threading
import time
import datetime as dt
import mimetypes
from pathlib import Path

from flask import (
    Flask, render_template, request, abort, session,
    redirect, url_for, send_from_directory,
)
from urllib.parse import quote
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadData

import forms_config
import i18n
import es_translate
import mailer
import status_labels

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
UPLOADS = DATA / "uploads"
LOG = DATA / "db_errors.log"
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

import os
SECRET = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
GATE_PASS = os.environ.get("ADVANCE_GATE_PASS", "lockdown")
# Second standing passcode (Brian, 2026-09-12) — either one opens the gate.
# No source-default: a guessable default landed in git history once already
# (audit 2026-09-16 #2/#7) — the real value lives only in advance.env now.
GATE_PASS_2 = os.environ.get("ADVANCE_GATE_PASS_2", "")
VALID_GATE_PASSES = {p for p in (GATE_PASS, GATE_PASS_2) if p}
INTERNAL_TOKEN = os.environ.get("ADVANCE_INTERNAL_TOKEN", "")
PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
NOTIFY_URL = os.environ.get("ADVANCE_NOTIFY_URL", "")
LIFECYCLE_NOW_URL = os.environ.get("ADVANCE_LIFECYCLE_NOW_URL", "")
# n8n's real-send webhook, called directly (Brian, 2026-09-13) for the
# unresponded-at-3-days alert — an actual SEND, never a draft, so it skips
# the "Advance Notify" formatting workflow NOTIFY_URL points at (that one's
# shape is booking/submission-specific). Flask and n8n run on the same VM
# (see n8n/README.md), so localhost:5678 is a safe default with no env var
# required — override only if that ever changes.
INTERNAL_SEND_URL = os.environ.get("ADVANCE_INTERNAL_SEND_URL",
                                    "http://localhost:5678/webhook/internal-send-outlook")
# "Email band" button (Brian, 2026-09-14): creates a real Outlook draft in the
# Production@3cdc.org mailbox via the internal-create-outlook-draft workflow.
CREATE_DRAFT_URL = os.environ.get("ADVANCE_CREATE_DRAFT_URL",
                                  "http://localhost:5678/webhook/internal-create-outlook-draft")
UNRESPONDED_ALERT_TO = os.environ.get("ADVANCE_UNRESPONDED_ALERT_TO", "blloyd@3cdc.org")
# FSQ regular-vehicle parking notice (Brian, 2026-09-15): drafted, never
# sent, to whoever handles garage validations. A mirror workflow for large
# vehicles, to a different recipient, is a separate later build.
FSQ_PARKING_NOTICE_TO = os.environ.get("ADVANCE_FSQ_PARKING_NOTICE_TO", "Mtully@3cdc.org")
TOOLS_DIR = BASE / "tools"

app = Flask(__name__)
app.secret_key = SECRET
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB cap on the stage-plot upload
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    # Strict, not Lax (audit 2026-09-16 security #4): every *.tinydoorstudios.com
    # subdomain — including the guest uploads portal — counted as "same-site"
    # under Lax, so an HTML file dropped there (or an XSS on any sibling host)
    # could fire an authenticated cross-origin POST here using a staffer's
    # live session. The CSRF token below is the other half of this fix.
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_SECURE=True,  # served over HTTPS via the Cloudflare tunnel
    PERMANENT_SESSION_LIFETIME=dt.timedelta(hours=12),
)

# URLSafeTimedSerializer, not the plain (non-expiring) URLSafeSerializer
# (audit 2026-09-16 security #9): a forwarded reminder link used to be
# forever-valid — whoever held it, even months later, could still open and
# overwrite that artist's record. See PREFILL_TOKEN_MAX_AGE below.
_signer = URLSafeTimedSerializer(SECRET, salt="advance-prefill")
# Signed artist id carried on the band form (audit #6) — a plain hidden
# artist_id could be edited to rename another artist / change their email.
_artist_signer = URLSafeTimedSerializer(SECRET, salt="advance-artist-id")
PREFILL_TOKEN_MAX_AGE = 180 * 24 * 3600


def artist_token(artist_id):
    return _artist_signer.dumps(int(artist_id)) if artist_id else ""


def verify_artist_token(tok):
    try:
        return int(_artist_signer.loads(tok, max_age=PREFILL_TOKEN_MAX_AGE)) if tok else None
    except (BadData, TypeError, ValueError):
        return None


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


# Extension -> magic bytes the file must actually start with (audit
# 2026-09-16, security #1 / app #15). secure_filename() alone only strips
# path characters and a client-side accept= is trivially bypassed; either
# uploader copies whatever lands here straight into the real 3CDC Dropbox
# venue folder as "the band's stage plot" for staff to double-click.
UPLOAD_MAGIC = {
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG",),
    ".jpg": (b"\xff\xd8",),
    ".jpeg": (b"\xff\xd8",),
    ".docx": (b"PK",),
    ".xlsx": (b"PK",),
    ".doc": (b"\xd0\xcf",),
}
UPLOAD_MAX_BYTES = 15 * 1024 * 1024


def _save_upload(upload, stamp, slug):
    """Validate + save one uploaded stage plot. Returns (stored_name, dest)
    or aborts 400/413. Shared by both upload sites (/submit and the staff
    booking-answers path) so neither can drift from the other again."""
    orig_ext = Path(upload.filename or "").suffix.lower()
    safe = secure_filename(upload.filename or "") or ""
    safe_ext = Path(safe).suffix.lower()
    # A non-Latin filename ("план.pdf") loses its extension too —
    # secure_filename() strips everything but ASCII — so fall back to the
    # original name's extension rather than rejecting a real file outright.
    ext = safe_ext or orig_ext
    if ext not in UPLOAD_MAGIC:
        abort(400, "Stage plot must be a PDF, image, Word, or Excel file.")
    head = upload.stream.read(8)
    upload.stream.seek(0)
    if not any(head.startswith(sig) for sig in UPLOAD_MAGIC[ext]):
        abort(400, "That file doesn't look like a real "
                    f"{ext.lstrip('.').upper()} — please re-export and try again.")
    upload.stream.seek(0, 2)  # SEEK_END
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size > UPLOAD_MAX_BYTES:
        abort(413, "Stage plot is too large (15 MB max) — please compress it and try again.")
    if not safe or not safe_ext:
        safe = f"plot{ext}"
    stored = f"{stamp}__{slug}__{safe}"
    dest = UPLOADS / stored
    upload.save(dest)
    return stored, dest


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
        return _signer.loads(token, max_age=PREFILL_TOKEN_MAX_AGE)
    except BadData:
        return None


# ── language ─────────────────────────────────────────────────────────────────
# ?lang=es on any form route serves the Spanish copy (form.html pulls every
# label/help/option string from i18n.py's STRINGS table via `t()`). Field
# `name=`s and stored option `value=`s stay English regardless of `lang` —
# only display text changes, so the DB/docfill/daysheet pipeline never has
# to know which language a band used. `form_lang` is a hidden field carrying
# that choice through to /submit, so the thank-you page (and, later, the
# submission-notify translation step) know the language after the redirect
# away from any `?lang=` query string.

def _lang():
    l = (request.args.get("lang") or "").strip().lower()
    return "es" if l == "es" else "en"


def _lang_url(new_lang):
    """Current path, query string swapped to `lang=new_lang` — for the
    Español/English toggle link on the form itself."""
    from urllib.parse import urlencode
    args = request.args.to_dict(flat=True)
    args["lang"] = new_lang
    return f"{request.path}?{urlencode(args)}"


@app.context_processor
def _inject_i18n():
    lang = _lang()
    return {"lang": lang, "t": i18n.translator(lang), "lang_url": _lang_url}


# ── public form ─────────────────────────────────────────────────────────────

@app.get("/")
def form():
    cfg = forms_config.get_config(
        series_key=request.args.get("series"),
        venue=request.args.get("venue"),
        location=request.args.get("location"),
        lang=_lang(),
    )
    cfg["third_party"] = advance_db.is_third_party(request.args.get("series"))
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill={}, returning=False, artist_name=None,
        tech_packs=forms_config.tech_packs(),
        known_artist_id=None, artist_tok="", locked_venue=False, locked_date=False,
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
    # Carry ?lang= through the redirect (Flask's url_for doesn't inherit the
    # incoming query string) so a Spanish-language emailed link still opens
    # the Spanish form after the short-code hop.
    kw = {"lang": request.args["lang"]} if request.args.get("lang") else {}
    return redirect(url_for("prefilled_form", token=token, **kw))


@app.get("/f/<token>")
def prefilled_form(token):
    """Pre-addressed link from the advance list. The token seeds band name + venue
    + date + series from the sheet row (so a first-time band opens the form already
    addressed); a returning band also gets their prior answers pre-filled."""
    payload = read_prefill_token(token) or {}
    seed = payload.get("s") or {}
    series = seed.get("series") or request.args.get("series")
    # An act's position on the bill used to tailor its form here — FSQ hid the
    # drum-riser question from openers and direct support. Every artist is asked
    # now, worded "if available" (Brian, 2026-09-15), so the form no longer
    # depends on where an artist falls on the night.
    cfg = forms_config.get_config(
        series_key=series, venue=seed.get("venue") or request.args.get("venue"),
        location=seed.get("location") or request.args.get("location"),
        lang=_lang())
    # Brian, 2026-09-14: staff fill in a 3rd-party advance themselves, so no
    # field on it is required (form renders novalidate; /submit skips checks).
    cfg["third_party"] = advance_db.is_third_party(series)
    prefill, returning, artist_name = {}, False, None
    # Locked = this specific value came from us (the booking record / matched
    # artist), not from the band typing it — bands can't edit these two.
    # Band / Group Name used to be a third locked field, but it's editable now
    # (Brian, 2026-09-09) like every other carried-over answer — known_artist_id
    # is how a rename still lands on the SAME artist record instead of a fuzzy
    # name match risking a duplicate (see upsert_artist's known_id).
    locked_venue = bool(seed.get("venue"))
    locked_date = bool(seed.get("date"))
    known_artist_id = None
    # Seed venue/date/contact/band-name into prefill independent of the DB
    # lookup below — these come straight from the signed token, so a link
    # still renders real values even if the artist lookup skips or fails (DB
    # down, no match) or there's no artist id at all yet (a brand-new
    # manual-entry booking — see _manual_fill_link — issued before the
    # pipeline has ever created an artist row for this band). None of these
    # are locked except venue/date; the artist-found branch below overwrites
    # this dict wholesale with the same seed values plus prior-submission
    # data, so nothing here is lost when a match does exist.
    if locked_venue:
        prefill["venue"] = seed["venue"]
    if locked_date:
        prefill["show_date"] = seed["date"]
    if seed.get("band_name"):
        prefill["band_name"] = seed["band_name"]
    if seed.get("contact_name"):
        prefill["contact_name"] = seed["contact_name"]
    if seed.get("contact_email"):
        prefill["contact_email"] = seed["contact_email"]
    if payload.get("a") and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                artist = advance_db.get_artist(cur, payload["a"])
                sub = advance_db.newest_submission(cur, payload["a"]) if artist else None
            if artist:
                artist_name = artist["name"]
                known_artist_id = artist["id"]
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
                # Staff-typed contact for THIS booking (Brian, 2026-09-09) wins
                # over a stale contact from a prior show — but only if staff
                # actually entered one; otherwise the prior submission's own
                # contact_name/contact_email (already in base, if any) stands.
                # Never locked: editable like every other carried-over answer.
                if seed.get("contact_name"):
                    seed_fields["contact_name"] = seed["contact_name"]
                if seed.get("contact_email"):
                    seed_fields["contact_email"] = seed["contact_email"]
                prefill = {**base, **seed_fields}
                if not cfg.get("venue_preselect"):
                    cfg["venue_preselect"] = prefill.get("venue")
        except Exception as e:
            _log_db_error("prefill", e)
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill=prefill, returning=returning, artist_name=artist_name,
        tech_packs=forms_config.tech_packs(),
        known_artist_id=known_artist_id, artist_tok=artist_token(known_artist_id),
        locked_venue=locked_venue, locked_date=locked_date,
    )


@app.post("/submit")
def submit():
    f = request.form
    # Review 2026-09-14 (H5): a filled honeypot field is a bot. Show the
    # thank-you page and save nothing — no artist, no show, no notify.
    if (f.get("website") or "").strip():
        lang = "es" if (f.get("form_lang") or "").strip().lower() == "es" else "en"
        return render_template("thanks.html", band=f.get("band_name"),
                               lang=lang, t=i18n.translator(lang))
    # audit 2026-09-16 security #7: rate limit — 5/IP/hour, 60 site-wide/
    # hour. Fails open (never blocks a real submission over a DB hiccup) —
    # abort() lives outside the try so it isn't itself swallowed as an error.
    # Staging's test suite fires far more than 5 submissions/hour from one
    # IP on purpose; exempt it the same way ADVANCE_STAGING already gates
    # other production-only behavior.
    limited = False
    if DB_OK and os.environ.get("ADVANCE_STAGING") != "1":
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                limited = advance_db.submit_rate_limited(cur, _client_ip())
                advance_db.record_submit_attempt(cur, _client_ip())
                conn.commit()
        except Exception as e:
            _log_db_error("submit_rate_limit", e)
    if limited:
        abort(429)
    # Brian, 2026-09-14: a 3rd-party advance is filled in by staff — nothing
    # on it is required (band name, stage plot, any of it). Same for a staff
    # edit from the dashboard's Edit form button (signed-in staff only).
    staff_edit = bool(f.get("staff_edit")) and bool(session.get("auth"))
    third = advance_db.is_third_party(f.get("show_series")) or staff_edit
    if not f.get("band_name") and not third:
        abort(400, "Band name is required.")

    # The band's own link carries a SIGNED artist id (audit #6). A raw
    # artist_id field is ignored — it could be edited to hijack another
    # artist's record.
    verified_artist_id = verify_artist_token(f.get("artist_token"))
    band_name = (f.get("band_name") or "").strip() or _third_party_band_name(
        verified_artist_id, f.get("venue"), f.get("show_date"))

    # Stage plot: upload OR description is required, not both (Brian,
    # 2026-09-08) — exempt only if this band already has one on file.
    upload = request.files.get("stage_plot_file")
    has_upload = bool(upload and upload.filename)
    has_desc = bool((f.get("stage_plot_desc") or "").strip())
    if not has_upload and not has_desc and not third:
        has_existing = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    artist = advance_db.get_artist(cur, verified_artist_id) if verified_artist_id else None
                    if not artist:
                        artist = advance_db.find_artist_by_name(cur, band_name)
                    if artist:
                        cur.execute("""SELECT 1 FROM submissions WHERE artist_id=%s
                                       AND COALESCE(data->>'stage_plot_file','') <> '' LIMIT 1""",
                                    (artist["id"],))
                        has_existing = cur.fetchone() is not None
            except Exception as e:
                _log_db_error("stage_plot_check", e)
        if not has_existing:
            abort(400, "Please provide a stage plot upload or a description — at least one is required.")

    # WP location monitor cap — hard limit (Brian, 2026-09-06). Resolve the
    # stage the same way the form renderer does (explicit location, else the
    # series->stage binding), so a WP booking whose location field is blank
    # still gets capped by its series' stage instead of sailing past uncapped
    # (Brian, 2026-09-18 — Jazz At The Porch was entering 3 wedges on a 2-cap
    # stage because the series wasn't bound and this check only saw a blank
    # location).
    if f.get("venue") == "Washington Park":
        stage = forms_config.resolve_wp_location(
            "Washington Park", f.get("location"), f.get("show_series"))
        if stage:
            cap = forms_config.WP_LOCATIONS[stage]["monitor_cap"]
            try:
                requested = int(f.get("monitors") or 0)
            except ValueError:
                requested = 0
            if requested > cap:
                abort(400, f"{stage} is limited to {cap} monitors — please enter {cap} or fewer.")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = _slug(band_name)
    # audit 2026-09-16 security #7: no per-field length cap existed beyond
    # the whole-request MAX_CONTENT_LENGTH — a free-text field could carry
    # tens of MB into data/*.json and submissions.data. Free-text fields get
    # more room than everything else (venue/select/number fields).
    rec = {k: (v[:4000] if k in es_translate.FREE_TEXT_FIELDS else v[:300])
          for k, v in f.items() if k not in ("artist_id", "artist_token", "staff_edit")}
    rec["band_name"] = band_name
    if verified_artist_id:
        rec["artist_id"] = str(verified_artist_id)
    if (rec.get("show_series") or "").strip().lower() == "default":
        rec["show_series"] = ""
    rec["_submitted_at"] = dt.datetime.now().isoformat(timespec="seconds")
    if staff_edit:
        rec["_staff_edit"] = True

    file_info = None
    if has_upload:
        stored, dest = _save_upload(upload, stamp, slug)
        rec["stage_plot_file"] = stored
        file_info = {
            "filename": upload.filename, "stored_name": stored,
            "mime": upload.mimetype,
            "size": dest.stat().st_size if dest.exists() else None,
        }

    # 1) DISK FIRST — before translation or anything else that can be slow
    #    or fail (audit #23). Rewritten below once the record is enriched.
    disk_path = DATA / f"{stamp}__{slug}.json"
    disk_path.write_text(json.dumps(rec, indent=2))

    # 2) Spanish free-text answers -> English (fails soft, originals kept)
    if (rec.get("form_lang") or "").strip().lower() == "es":
        try:
            es_translate.translate_es_fields(rec, log=_log_db_error)
        except Exception as e:
            _log_db_error("es_translate", e)

    # 3) Postgres, best-effort: resolves the booking (audit #6) and carries a
    #    returning band's plot forward when they didn't re-upload (audit #8).
    result = None
    if DB_OK:
        try:
            result = advance_db.record_submission(rec, file_info=file_info,
                                                  source="staff" if staff_edit else "form")
            rec["_db"] = {"artist_id": result["artist_id"], "show_id": result["show_id"],
                          "submission_id": result["submission_id"]}
        except Exception as e:
            _log_db_error("record_submission", e)
            _alert_db_write_failure(rec, e)
    try:
        disk_path.write_text(json.dumps(rec, indent=2))
    except OSError as e:
        _log_db_error("disk_rewrite", e)

    # 4) Notify, best-effort — not for a staff edit (nobody needs a "form
    #    received" ping for their own correction)
    if not staff_edit:
        _notify_submission(rec)
        _notify_email("submission", rec)
        if rec.get("venue") == "Fountain Square":
            _queue_fsq_parking(rec)
    if result and result.get("match"):
        _email_submission_match(result, rec)

    # 5) File ONLY this show's advance doc, in the background — blank cells
    #    only, never overwriting (audit #1). Uses the artist the submission
    #    actually landed on, which may be the booked name (audit #6).
    regen_rec = dict(rec)
    if result:
        regen_rec["band_name"] = result["artist_name"]
    _regen_submitted_show(regen_rec, submission_id=(result or {}).get("submission_id"))

    # a staff edit lands on the doc review for this show, which waits for
    # the doc check above and then lists anything waiting on a decision
    if staff_edit and result:
        return redirect(url_for("doc_review", venue=rec.get("venue"),
                                date=(rec.get("show_date") or "")[:10], sub=result["submission_id"]))

    submitted_lang = "es" if (f.get("form_lang") or "").strip().lower() == "es" else "en"
    return render_template("thanks.html", band=band_name,
                            lang=submitted_lang, t=i18n.translator(submitted_lang))


def _third_party_band_name(artist_id, venue, show_date):
    """Name for a 3rd-party advance submitted with Band Name blank: the
    linked artist, else the one 3rd-party booking at that venue+date, else a
    placeholder. Only reached when the name is blank."""
    if not DB_OK:
        return "3rd Party Event"
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            artist = advance_db.get_artist(cur, artist_id) if artist_id else None
            if artist:
                return artist["name"]
            d = advance_db.to_date(show_date)
            if venue and d:
                cur.execute("""SELECT DISTINCT artist_name FROM bookings
                               WHERE venue=%s AND event_date=%s
                                 AND lower(btrim(COALESCE(series,''))) = '3rd party'""",
                            (venue, d))
                rows = cur.fetchall()
                if len(rows) == 1:
                    return rows[0]["artist_name"]
    except Exception as e:
        _log_db_error("third_party_band_name", e)
    return "3rd Party Event"


def _alert_db_write_failure(rec, err):
    """The submission is safe on disk but didn't reach the database — without
    this nobody would know until the band got a 'please fill this out'."""
    mailer.alert(
        f"Advance submission NOT saved to the database — {rec.get('band_name')}",
        f"<p>{mailer.esc(rec.get('band_name'))} @ {mailer.esc(rec.get('venue'))} "
        f"{mailer.esc(rec.get('show_date'))} submitted the form. It's saved on disk but the "
        f"database write failed: <code>{mailer.esc(repr(err))}</code>.</p>"
        "<p>Reminders for this show will keep going until it's replayed.</p>")


def _email_submission_match(result, rec):
    m = result["match"]
    link = f"{PUBLIC_URL}/submission-match/{m['id']}"
    typed = mailer.esc(rec.get("band_name"))
    where = f"{mailer.esc(rec.get('venue'))} {mailer.esc(rec.get('show_date'))}"
    if m["status"] == "attached_auto":
        subject = f"Check a submission match — “{rec.get('band_name')}” attached to {m['booked_name']}"
        body = (f"<p>A band submitted as <b>{typed}</b> for {where}, but no booking has that name. "
                f"The only unanswered booking that night is <b>{mailer.esc(m['booked_name'])}</b>, "
                "so the submission was attached to it (its reminders stop now).</p>"
                f"<p><a href='{link}'>Confirm, or “Wrong band, detach” →</a></p>")
    else:
        names = ", ".join(mailer.esc(c["artist_name"]) for c in m["candidates"]) or "none"
        subject = f"Pick the booking for a submission — “{rec.get('band_name')}”"
        body = (f"<p>A band submitted as <b>{typed}</b> for {where}. No booking has that name, and "
                f"there isn't exactly one unanswered booking that night (candidates: {names}). "
                "It was saved under the name they typed.</p>"
                f"<p><a href='{link}'>Pick the booking it belongs to →</a></p>")
    # Review 2026-09-14 (E1): rides the 7am digest and the dashboard's
    # "Needs you" panel instead of its own email.
    if DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                advance_db.queue_digest_item(cur, "match", subject, body, link)
                cur.execute("UPDATE submission_matches SET notified_at=now() WHERE id=%s", (m["id"],))
                conn.commit()
        except Exception as e:
            _log_db_error("match_notified", e)


def _regen_submitted_show(rec, submission_id=None):
    """Regenerate just the submitting show's advance doc — never the whole tree
    (Brian, 2026-09-11: one band's submission was restamping every file). Needs
    venue + show_date + band_name, all carried on the form. Detached, best-effort."""
    venue = (rec.get("venue") or "").strip()
    date = (rec.get("show_date") or "").strip()[:10]
    artist = (rec.get("band_name") or "").strip()
    if not (venue and date and artist):
        return
    try:
        log_path = BASE / "data" / "regen_show.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as logf:
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} "
                       f"{artist} @ {venue} {date} ---\n")
            logf.flush()
            subprocess.Popen(
                [sys.executable, "regen_show.py", "--venue", venue,
                 "--date", date, "--artist", artist]
                + (["--submission-id", str(submission_id)] if submission_id else []),
                cwd=TOOLS_DIR, stdout=logf, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except Exception as e:
        _log_db_error("regen_submitted_show", e)


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
    the request the event came from.

    event_type MUST win the dict merge (Brian, 2026-09-13 — "Second Wind"/
    "Wishy" bug): the booking form has its own "Event Type" field
    (Internal/Third Party), stored under the same key `event_type`. With
    `fields` unpacked SECOND, that field silently clobbered the discriminator
    n8n's Format Email node branches on, so every single booking (any booking
    has an Event Type) mis-rendered as "Advance form completed" instead of
    "New booking" — not intermittent, guaranteed on every one."""
    if not NOTIFY_URL:
        return
    try:
        import urllib.request
        body = json.dumps({**fields, "event_type": event_type}).encode()
        req = urllib.request.Request(
            NOTIFY_URL, data=body,
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN},
        )
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        _log_db_error("notify_email", e)


def _send_outlook_email(to, subject, body=None, html=None, attachment=None, timeout=90, attachments=None):
    """(ok, error) — thin wrapper over mailer.send, the single send path
    (audit #3: a send only counts when n8n confirms Graph accepted it)."""
    return mailer.send(to, subject, body=body, html=html, attachment=attachment, timeout=timeout,
                       attachments=attachments)


def _send_internal_email(subject, html, to=None):
    return mailer.alert(subject, html, to=to)


def _create_outlook_draft(to, subject, body=None, html=None, attachments=None, timeout=30):
    """(ok, error, web_link) — put a message in Production@3cdc.org's drafts
    instead of sending it. The single draft path, shared by the artist page's
    "Email band" button and by a booking flagged "draft, don't send"
    (bookings.draft_only — Brian, 2026-09-15).

    Mirrors mailer.send's payload shape, attachments included, so a drafted
    welcome carries the same venue load-in doc and tech pack a sent one would.
    Honours the same two kill switches as a real send: a draft nobody asked for
    is as unwelcome in a staging run as an email."""
    if os.environ.get("ADVANCE_MAIL_DISABLED") == "1":
        return False, "mail disabled", None
    if (os.environ.get("ADVANCE_STAGING") == "1"
            and not CREATE_DRAFT_URL.startswith("http://127.0.0.1:8199")):
        return False, "staging refuses non-stub url", None
    content = html if html else (body or "")
    if not str(content).strip():
        return False, "empty body", None
    payload = {"to": to, "subject": subject}
    payload["html" if html else "body"] = content
    att = list(attachments or [])
    if att:
        payload["attachment_name"], payload["attachment_type"], payload["attachment_content"] = att[0]
        if len(att) > 1:
            payload["attachments"] = [{"name": n, "type": t, "content": c} for n, t, c in att[1:]]
    try:
        import urllib.request
        req = urllib.request.Request(
            CREATE_DRAFT_URL, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except Exception as e:  # noqa: BLE001
        return False, repr(e)[:200], None
    if isinstance(raw, list):
        raw = raw[0] if raw else {}
    gbody = raw.get("body") if isinstance(raw, dict) else None
    status = raw.get("statusCode") if isinstance(raw, dict) else None
    if status in (200, 201) and isinstance(gbody, dict) and gbody.get("id"):
        return True, None, gbody.get("webLink")
    return False, f"draft not created (HTTP {status}): {str(gbody)[:200]}", None


def _run_pipeline_background(scope=None):
    """Kick off run_now.py in the background — never blocks or risks the request
    it's called from. Detached (start_new_session) so it outlives this worker.
    run_now.py's own lock file makes overlapping triggers (this + the booking
    button) safe. Output goes to a log, not /dev/null (2026-09-10) — a real
    failure here used to vanish with zero trace anywhere, which is exactly
    what let one bad event silently block every band's advance for hours."""
    try:
        log_path = BASE / "data" / "run_now_background.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as logf:
            label = scope if isinstance(scope, str) else ", ".join(scope or [])
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')}"
                       f"{' (' + label + ')' if label else ''} ---\n")
            logf.flush()
            scopes = [scope] if isinstance(scope, str) else list(scope or [])
            cmd = [sys.executable, "run_now.py"]
            for sc in scopes:
                cmd += ["--scope", sc]
            subprocess.Popen(
                cmd, cwd=TOOLS_DIR,
                stdout=logf, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except Exception as e:
        _log_db_error("run_pipeline_background", e)


def _trigger_immediate_advance():
    """Fire n8n's on-demand Advance Lifecycle webhook — same drafting/reminder
    logic as the daily 9am check, run right now instead of waiting for it.
    Best-effort, same pattern as _notify_email."""
    if not LIFECYCLE_NOW_URL:
        return
    try:
        import urllib.request
        req = urllib.request.Request(
            LIFECYCLE_NOW_URL, data=b"{}",
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN},
        )
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        _log_db_error("trigger_immediate_advance", e)


def _run_pipeline_then_trigger_now(scope=None):
    """Late-booking path: a show inside the 21-day window at the moment it's
    booked can't wait for the next daily check the way a normal-lead-time
    booking can (Brian, 2026-09-03). Runs the pipeline SYNCHRONOUSLY so the
    show is actually seeded in the database before triggering the immediate
    draft + notify — then fires it. Runs in a background thread (not the
    request thread) so /booking's response is never held up by it."""
    # Output goes to the same log as the background run (2026-09-14): it used
    # to be captured and dropped, so a failed late-booking run left no trace.
    try:
        log_path = BASE / "data" / "run_now_background.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as logf:
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} "
                       f"(late booking{', ' + scope if scope else ''}) ---\n")
            logf.flush()
            proc = subprocess.run([sys.executable, "run_now.py"] + (["--scope", scope] if scope else []),
                                  cwd=TOOLS_DIR, stdout=logf, stderr=subprocess.STDOUT, timeout=1200)
            if proc.returncode != 0:
                logf.write(f"exit {proc.returncode}\n")
    except Exception as e:
        _log_db_error("late_booking_pipeline", e)
        return
    if proc.returncode != 0:
        _log_db_error("late_booking_pipeline", RuntimeError(
            f"run_now.py exit {proc.returncode} ({scope}) — see run_now_background.log"))
        return
    _trigger_immediate_advance()


# ── gated views (passcode) ──────────────────────────────────────────────────

GATED_PREFIXES = ("/staff", "/search", "/artist", "/file", "/submission", "/booking",
                  "/dashboard", "/show", "/doc-review")

GATE_MAX_FAILS = 5
GATE_WINDOW_MIN = 15
# Global throttle (audit 2026-09-16 #2): a distributed attempt spread across
# many /64s or /24s never trips any single lockout, so cap total failures
# across every IP too.
GATE_GLOBAL_MAX_FAILS = 30
GATE_NOTIFY_COOLDOWN_MIN = 60


def _csrf_token():
    """Per-session token (audit 2026-09-16 security #4) — get-or-create so
    every gated page renders the same one for its whole session lifetime."""
    tok = session.get("csrf")
    if not tok:
        tok = secrets.token_urlsafe(32)
        session["csrf"] = tok
    return tok


@app.context_processor
def _inject_csrf():
    return {"csrf_token": _csrf_token}


@app.before_request
def _gate():
    p = request.path
    if request.method == "POST" and p.startswith(GATED_PREFIXES) and session.get("auth"):
        sent = request.form.get("csrf") or request.headers.get("X-CSRF") or ""
        if not hmac.compare_digest(sent, session.get("csrf") or ""):
            abort(403)
    if p.startswith(GATED_PREFIXES) and not session.get("auth"):
        return redirect(url_for("gate", next=p))


@app.after_request
def _security_headers(resp):
    """Baseline headers (audit 2026-09-16 security #12) — live had none of
    these at all. Cloudflare terminates TLS in front of this app, but HSTS
    still belongs on the origin response so a client that somehow reaches
    us over plain HTTP is told to stop."""
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return resp


def _client_ip():
    # CF-Connecting-IP is only trustworthy from Cloudflare's own hop — which,
    # once gunicorn binds 127.0.0.1 (audit #6/#23), is the only thing that can
    # reach us as 127.0.0.1. A LAN client on the public port used to be able
    # to spoof this header outright (audit 2026-09-16 #7).
    if request.remote_addr == "127.0.0.1":
        cf = request.headers.get("CF-Connecting-IP")
        if cf:
            return cf
    return request.remote_addr or "unknown"


def _lockout_net(ip):
    """Collapse an address to the block it locks out with — one attacker has
    far more than one address across a /64 (IPv6) or /24 (IPv4), so keying
    lockouts on the bare IP let them route around it for free (audit #2)."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    prefix = 64 if addr.version == 6 else 24
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))


def _safe_next(nxt):
    """Only ever redirect to a page on this site (audit #13).

    audit 2026-09-16 security #5: the old check let a control character
    through — "/%09/evil.example" decodes to a leading tab, which both
    gunicorn's header validator and browsers themselves tolerate/strip,
    turning "/\\t/evil.example" into a scheme-relative "//evil.example" by
    the time it reaches the browser. Reject any C0 control character (incl.
    tab) up front, and parse with urlsplit rather than trusting startswith
    alone — a scheme or netloc anywhere in the string is refused outright."""
    from urllib.parse import urlsplit
    if nxt and not re.search(r"[\x00-\x1f\\]", nxt):
        u = urlsplit(nxt)
        if not u.scheme and not u.netloc and u.path.startswith("/") and not u.path.startswith("//"):
            return nxt
    return url_for("staff")


def _gate_locked(cur, net):
    cur.execute("""SELECT locked_at FROM gate_lockouts
                   WHERE ip=%s AND locked_at > now() - (%s || ' minutes')::interval""",
                (net, GATE_WINDOW_MIN))
    return cur.fetchone() is not None


@app.route("/gate", methods=["GET", "POST"])
def gate():
    """Staff passcode gate. Both standing passcodes stay valid; 5 wrong tries
    from one IP within 15 minutes locks that IP out for 15 minutes and emails
    Brian once (audit #13). Counts live in the database so every worker
    shares them. If the database is down the gate still works, unthrottled —
    never lock staff out over a DB outage."""
    ip = _client_ip()
    net = _lockout_net(ip)
    if request.method == "POST":
        locked = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    locked = _gate_locked(cur, net)
            except Exception as e:
                _log_db_error("gate_check", e)
        if locked:
            return render_template("gate.html",
                                   error=f"Too many attempts — try again in {GATE_WINDOW_MIN} minutes."), 429
        posted = request.form.get("passcode") or ""
        ok = any(hmac.compare_digest(posted, p) for p in VALID_GATE_PASSES)
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    cur.execute("INSERT INTO gate_attempts (ip, ok) VALUES (%s,%s)", (ip, ok))
                    if not ok:
                        cur.execute("""SELECT count(*) AS n FROM gate_attempts
                                       WHERE ip::inet <<= %s::cidr AND NOT ok
                                         AND attempted_at > now() - (%s || ' minutes')::interval
                                         AND attempted_at > COALESCE((SELECT locked_at FROM gate_lockouts
                                                                      WHERE ip=%s), '-infinity')""",
                                    (net, GATE_WINDOW_MIN, net))
                        net_fails = cur.fetchone()["n"]
                        cur.execute("""SELECT count(*) AS n FROM gate_attempts
                                       WHERE NOT ok
                                         AND attempted_at > now() - (%s || ' minutes')::interval""",
                                    (GATE_WINDOW_MIN,))
                        global_fails = cur.fetchone()["n"]
                        if net_fails >= GATE_MAX_FAILS or global_fails >= GATE_GLOBAL_MAX_FAILS:
                            cur.execute("""INSERT INTO gate_lockouts (ip, locked_at, notified_at)
                                           VALUES (%s, now(), NULL)
                                           ON CONFLICT (ip) DO UPDATE SET locked_at=now()""",
                                        (net,))
                            locked = True
                    conn.commit()
                if locked:
                    with advance_db.get_conn() as conn, conn.cursor() as cur:
                        cur.execute("SELECT notified_at FROM gate_lockouts WHERE ip=%s", (net,))
                        row = cur.fetchone()
                    cooled_down = (not row or not row["notified_at"]
                                   or row["notified_at"] <
                                   dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=GATE_NOTIFY_COOLDOWN_MIN))
                    if cooled_down:
                        sent, _ = mailer.alert(
                            "Advance staff login locked out — repeated wrong passcodes",
                            f"<p>{GATE_MAX_FAILS} wrong passcodes from <b>{mailer.esc(net)}</b> within "
                            f"{GATE_WINDOW_MIN} minutes. That block is locked out for {GATE_WINDOW_MIN} minutes.</p>")
                        if sent:
                            with advance_db.get_conn() as conn, conn.cursor() as cur:
                                cur.execute("UPDATE gate_lockouts SET notified_at=now() WHERE ip=%s", (net,))
                                conn.commit()
            except Exception as e:
                _log_db_error("gate_record", e)
        if ok:
            session.permanent = True  # audit #4/#12: cookie now expires server-side after 12h
            session["auth"] = True
            return redirect(_safe_next(request.args.get("next")))
        if locked:
            return render_template("gate.html",
                                   error=f"Too many attempts — try again in {GATE_WINDOW_MIN} minutes."), 429
        return render_template("gate.html", error="Incorrect passcode."), 403
    return render_template("gate.html", error=None)


@app.get("/staff")
def staff():
    """Staff landing page — the one door into everything past the gate: log a
    new booking, or browse bands already advanced. Linked from the dashboard;
    the gate lands here by default too."""
    return render_template("staff.html")


# ── live dashboard (Brian, 2026-09-12) ──────────────────────────────────────
# Every advance from today forward — sites, bands, where each stands in the
# pipeline. Meant to be left open (a kiosk tab, a second monitor): the page is
# static HTML/JS that polls /dashboard/data on an interval, so nothing here
# ever needs a hard reload to stay current.

# "awaiting" and "ready_to_send" both used to mean "a Gmail/Outlook draft is
# sitting there, waiting on either the 21-day mark or you to press send" —
# accurate before the live-send migration. Since that migration (2026-09-13),
# advance_draft_created_at means the welcome was already SENT for real the
# moment shows_due_for_initial_advance picked the show up (now gated at 21
# days out — see that function's docstring for the incident this closes), so
# both states now mean the exact same real-world thing: sent, no response
# yet. Caught 2026-09-13 when Brian saw Dixie Karas labeled "Awaiting
# Window" on the live dashboard after her welcome had already gone out —
# same underlying drift status_log.py's Excel legend already called out for
# the Show Status Log, just never carried over to this page. Same label for
# both states on purpose (days-out is already shown on the bill card itself
# via days-badge, so nothing is lost by not distinguishing them here).
#
# "responded" relabeled "Advancing In Progress" and "finalized" added
# (Brian, 2026-09-13) — the point after a band responds where a human still
# has to review everything and sign off (POST /artist/<id>/finalize/<show_id>)
# before it's really done. Same rename applied everywhere else this state is
# shown — status_log.py/daily_digest.py (which used "Completed", a different
# word for the same state — already-existing drift, fixed here too) and
# merge_status.py/status_sheet.py's color maps — so nothing says something
# different from this page ever again.
DASHBOARD_STATE_LABELS = status_labels.dashboard_map()


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.get("/dashboard/data")
def dashboard_data():
    """JSON feed the dashboard polls. Rows sharing a venue+date are grouped
    into one bill (same assumption `shows`' own unique constraint makes —
    artist+venue+date is the booking key) so a multi-band night reads as one
    card, not three separate ones — UNLESS they're actually different events
    on the same venue+date (Brian, 2026-09-17: a 3rd-party event and the
    normal internal bill can share a date — Sept 30 FSQ — and always need
    their own cards). event_acts is the source of truth for which event a
    show landed on; before the pipeline has run once for a brand-new
    booking there's no event_acts row yet, so a 3rd-party/internal split by
    series is the fallback bucket."""
    if not DB_OK:
        return {"error": "db-unavailable", "bills": [], "generated_at": dt.datetime.now().isoformat()}, 503
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            rows = advance_db.dashboard_status(cur)
            cur.execute("""SELECT venue, event_date, count(*) AS n FROM doc_notices
                           WHERE kind='diff' AND resolved_at IS NULL AND event_date >= CURRENT_DATE
                           GROUP BY venue, event_date""")
            open_reviews = {(r["event_date"], r["venue"]): r["n"] for r in cur.fetchall()}
            cur.execute("""SELECT s.id AS show_id, ev.id AS event_id, ev.name AS event_name
                           FROM shows s
                           JOIN event_acts ea ON ea.artist_id = s.artist_id
                           JOIN events ev ON ev.id = ea.event_id
                             AND ev.venue = s.venue AND ev.event_date = s.show_date
                           WHERE s.show_date >= CURRENT_DATE""")
            show_events = {r["show_id"]: (r["event_id"], r["event_name"]) for r in cur.fetchall()}
    except Exception as e:
        _log_db_error("dashboard_data", e)
        return {"error": "query-failed", "bills": [], "generated_at": dt.datetime.now().isoformat()}, 500

    bills, order = {}, []
    for r in rows:
        event_id, event_name = show_events.get(r["show_id"], (None, None))
        third = advance_db.is_third_party(r["show_series"])
        bucket = event_id if event_id is not None else ("3rd-party" if third else "internal")
        key = (r["show_date"], r["venue"], bucket)
        review_key = (r["show_date"], r["venue"])
        if key not in bills:
            bills[key] = {
                "date": r["show_date"].isoformat() if r["show_date"] else None,
                "venue": r["venue"] or "Venue TBD",
                "series": event_name or r["show_series"] or "",
                "days_until": r["days_until_show"],
                "reviews": open_reviews.get(review_key, 0),
                "acts": [],
            }
            order.append(key)
        label, css = DASHBOARD_STATE_LABELS.get(r["state"], (r["state"] or "Unknown", "queued"))
        bills[key]["acts"].append({
            "band": r["band"], "state": r["state"],
            "state_label": label, "state_css": css,
            # carried so the dashboard can offer Mark Finalized inline
            # (Brian, 2026-09-13: "I don't want to go searching for bands")
            # without a second round-trip to look them up.
            "artist_id": r["artist_id"], "show_id": r["show_id"],
            # booking_id (2026-09-14): the bookings row for this act, if
            # staff logged one — powers the "Edit booking" button. A show
            # that only exists because the band submitted the advance form
            # directly (no staff booking row) has no booking to edit.
            "booking_id": r.get("booking_id"),
        })
    return {"bills": [bills[k] for k in order], "generated_at": dt.datetime.now().isoformat()}


@app.get("/dashboard/needs")
def dashboard_needs():
    """Open decisions and problems for the dashboard's "Needs you" panel
    (review 2026-09-14, E1) — the same feed the 7am digest prints."""
    if not DB_OK:
        return {"items": [], "error": "db-unavailable"}, 503
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            items = advance_db.needs_attention(cur)
    except Exception as e:
        _log_db_error("dashboard_needs", e)
        return {"items": [], "error": "query-failed"}, 500
    for it in items:
        it["since"] = it["since"].isoformat() if it.get("since") else None
    return {"items": items, "generated_at": dt.datetime.now().isoformat()}


# BOOKING_SLOTS retired 2026-09-15 — staff no longer picks a slot or a band
# count. Set Start decides the order (earliest is Artist 1) and the bill counts
# itself. See advance_db.order_acts.
# No-series choices (audit #16). The top Series pick decides internal vs 3rd
# party; the old Event Type field is gone from the form.
STANDALONE_SERIES = ["Stand-Alone Internal", "3rd Party"]


def _event_type_for_series(series):
    return "Third Party" if (series or "").strip().lower() == "3rd party" else "Internal"


# Set Start / Set End (Brian, 2026-09-15): two new required fields on the
# booking form that aren't stored themselves — their only job is filling
# Load-In / Sound Check / Start / End / Set Length. booking.html's JS does
# this live as staff type; these are the server-side mirror, so a field the
# JS didn't reach (a non-JS client, a direct API call) still gets filled —
# and only ever fills a BLANK field, never overwrites what staff (or the JS)
# already put there.
_CLOCK_RE = re.compile(r'^\s*(\d{1,2}):(\d{2})\s*([ap])m?\s*$', re.IGNORECASE)


def _time_to_minutes(hhmm):
    """'19:00' (a native <input type=time>'s value) -> 1140, or None."""
    try:
        h, m = (hhmm or "").strip().split(":")
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None


def _minutes_to_clock(mins):
    """1140 -> '7:00p' — matches the form's own placeholder convention
    ('e.g. 4:30p', 'e.g. 11:00p') and the JS calc that drives the live
    preview in booking.html."""
    mins = ((mins % 1440) + 1440) % 1440
    h, m = divmod(mins, 60)
    ap = "a" if h < 12 else "p"
    h = h % 12 or 12
    return f"{h}:{m:02d}{ap}"


def _clock_to_hhmm(text):
    """The reverse — '7:00p' / '11:30am' -> '19:00' / '11:30' for a native
    <input type=time>'s value, or None if it doesn't look like a plain
    clock time (a locked-schedule series renders other text here, e.g.).
    Backfills Set Start/Set End when opening the edit page for a booking
    that predates this feature, from its existing Start/End."""
    m = _CLOCK_RE.match(text or "")
    if not m:
        return None
    h, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    if not (1 <= h <= 12 and 0 <= mm < 60):
        return None
    h = h % 12
    if ap == "p":
        h += 12
    return f"{h:02d}:{mm:02d}"


def _derive_schedule(data, f):
    """Fill event_start/event_end/load_in/soundcheck/set_time from
    Set Start/Set End wherever the caller (staff, or the JS) left them
    blank. Mutates `data` in place."""
    s = _time_to_minutes(f.get("set_start"))
    e = _time_to_minutes(f.get("set_end"))
    if s is not None and not data.get("load_in"):
        data["load_in"] = _minutes_to_clock(s - 60)
    if s is not None and not data.get("soundcheck"):
        data["soundcheck"] = _minutes_to_clock(s - 30)
    if s is not None and not data.get("event_start"):
        data["event_start"] = _minutes_to_clock(s)
    if e is not None and not data.get("event_end"):
        data["event_end"] = _minutes_to_clock(e)
    if s is not None and e is not None and not data.get("set_time"):
        d = e - s
        if d <= 0:
            d += 1440
        data["set_time"] = f"{d} min"


def _locked_schedule_series():
    """Best-effort — an empty list just means the booking form shows the
    schedule-time fields for every series, never blocks the form from
    loading."""
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        import venue_email as ve
        return ve.locked_schedule_series()
    except Exception as e:
        _log_db_error("locked_schedule_series", e)
        return []


def _series_schedule_defaults():
    """Best-effort — an empty dict just means no series pre-fills the
    schedule-time fields (they fall back to being hidden, as before)."""
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        import venue_email as ve
        return ve.all_schedule_defaults()
    except Exception as e:
        _log_db_error("series_schedule_defaults", e)
        return {}


def _series_by_venue():
    """Best-effort — an empty dict just means the form falls back to the
    stand-alone choices + '+ Add new series…'. The stand-alone choices are
    never listed as a venue's series (they'd drag the venue picker along)."""
    if not DB_OK:
        return {}
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            raw = advance_db.series_by_venue(cur)
    except Exception as e:
        _log_db_error("series_by_venue", e)
        return {}
    skip = {x.lower() for x in STANDALONE_SERIES}
    raw = {v: [x for x in opts if x.lower() not in skip] for v, opts in raw.items()}
    ordered = {}
    for v in forms_config.VENUES:
        if raw.get(v):
            ordered[v] = raw[v]
    for v, opts in raw.items():
        if v not in ordered and opts:
            ordered[v] = opts
    return ordered


def _record_booking_band_answers(f, files, data, existing_artist_id=None):
    """A staffer filled in the band's own questions right on the booking form
    (Brian, 2026-09-16). Builds the same `rec` shape /submit would from a real
    submission and calls record_submission — one system, not two: the answer
    reaches search, the day-sheet and the doc exactly the way a band's own
    submission does.

    No-ops (returns None) when none of those fields were touched, and when the
    touched values exactly match the artist's newest submission already on
    file — so re-saving a booking's schedule doesn't quietly file a duplicate
    "the band submitted again" row every time. Never raises: a failure here
    must not undo the booking save that already happened."""
    posted = {k: (f.get(k) or "").strip() for k in advance_db.BOOKING_BAND_ANSWER_FIELDS}
    upload = files.get("stage_plot_file")
    has_upload = bool(upload and upload.filename)
    if not any(posted.values()) and not has_upload:
        return None
    if not DB_OK:
        return None
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            artist = (advance_db.get_artist(cur, existing_artist_id) if existing_artist_id
                     else advance_db.find_artist_by_name(cur, data.get("artist_name")))
            if artist:
                prior = advance_db.newest_submission(cur, artist["id"])
                prior_data = (prior or {}).get("data") or {}

                def _prior_value(k):
                    v = prior_data.get(k)
                    if v not in (None, ""):
                        return str(v).strip()
                    v = (prior or {}).get(k)
                    if isinstance(v, bool):  # own_iems / merch are BOOLEAN in that column
                        v = "Yes" if v else "No"
                    return str(v or "").strip()

                if not has_upload and all(
                        posted.get(k, "") == _prior_value(k)
                        for k in advance_db.BOOKING_BAND_ANSWER_FIELDS):
                    return None  # nothing actually changed since the last answer on file
    except Exception as e:  # noqa: BLE001
        _log_db_error("booking_band_answers_precheck", e)

    rec = dict(posted)
    rec["band_name"] = data.get("artist_name") or ""
    rec["venue"] = data.get("venue") or ""
    rec["show_date"] = data.get("event_date") or ""
    rec["show_series"] = data.get("series") or ""
    rec["contact_name"] = data.get("contact_name") or ""
    rec["contact_email"] = data.get("contact_email") or ""
    rec["_submitted_at"] = dt.datetime.now().isoformat(timespec="seconds")
    rec["_staff_edit"] = True
    if existing_artist_id:
        # audit 2026-09-16 #10: without this, record_submission falls back to
        # its own name-matching — fine most of the time, but a name typed
        # slightly differently than the artist record (or matching another
        # band entirely) used to create a second artist for a show we
        # already know the artist_id of.
        rec["artist_id"] = str(existing_artist_id)
    rec = {k: v for k, v in rec.items() if v not in (None, "")}

    file_info = None
    if has_upload:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        stored, dest = _save_upload(upload, stamp, _slug(rec["band_name"]))
        rec["stage_plot_file"] = stored
        file_info = {"filename": upload.filename, "stored_name": stored,
                    "mime": upload.mimetype, "size": dest.stat().st_size if dest.exists() else None}
    try:
        # resolve_booking=False (Brian caught this 2026-09-16): the booking
        # form ALREADY says exactly which artist/venue/date this belongs to —
        # there's nothing to resolve. With it left on, record_submission's own
        # fuzzy matching ran anyway and, finding no show yet for a brand-new
        # artist (the booking row exists but upsert_show hasn't run for it),
        # fell back to "is there exactly one other unresponded show at this
        # venue+date" — found one (an unrelated band on the same bill) and
        # flagged a false "needs a booking" notice against it, even though the
        # submission had already correctly created its own artist and show.
        # stamp_responded=False (audit 2026-09-16 #9): typing the band's
        # answers straight into the booking form isn't the same as the band
        # having responded to a welcome that hasn't gone out yet — without
        # this the show never gets welcomed or reminded at all, even though
        # the thank-you page tells staff it will.
        return advance_db.record_submission(rec, file_info=file_info, source="staff",
                                            resolve_booking=False, stamp_responded=False)
    except Exception as e:  # noqa: BLE001
        _log_db_error("booking_band_answers", e)
        return None


def _manual_fill_link(data):
    """Link to the band's own full advance form for a manual-entry booking
    (skip_welcome_email). Same signed-token/short-link shape as the
    reminder link, without an artist id."""
    token = _signer.dumps({"a": None, "s": {
        "venue": data.get("venue") or None,
        "date": data.get("event_date") or None,
        "series": data.get("series") or None,
        "location": data.get("location") or None,
        "band_name": data.get("artist_name") or None,
        "contact_name": data.get("contact_name") or None,
        "contact_email": data.get("contact_email") or None,
    }})
    if DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                code = advance_db.get_or_create_short_link(cur, token)
                conn.commit()
            return f"{PUBLIC_URL}/s/{code}"
        except Exception as e:
            _log_db_error("manual_fill_link", e)
    return f"{PUBLIC_URL}/f/{token}"


def _booking_form(error=None, form=None, status=200, edit_booking_id=None, show_id=None):
    return render_template("booking.html", venues=forms_config.VENUES,
                           wp_locations=list(forms_config.WP_LOCATIONS),
                           series_by_venue=_series_by_venue(),
                           standalone_series=STANDALONE_SERIES,
                           locked_schedule_series=_locked_schedule_series(),
                           series_schedule_defaults=_series_schedule_defaults(),
                           error=error, form=form or {}, edit_booking_id=edit_booking_id,
                           show_id=show_id), status


def _booking_row_to_form(b):
    """A bookings row (DB types) -> the string-keyed dict booking.html's
    prefill logic expects (same shape request.form gives the /booking POST
    handler)."""
    form = {k: ("" if b.get(k) is None else str(b[k])) for k in advance_db.BOOKING_FIELDS}
    if b.get("event_date"):
        form["event_date"] = b["event_date"].isoformat()
    form["skip_welcome_email"] = bool(b.get("skip_welcome_email"))
    form["band_emails"] = bool(b.get("band_emails"))
    form["draft_only"] = bool(b.get("draft_only"))
    # Set Start/Set End (2026-09-15) predate this booking if it's older than
    # the feature — back-fill them from the existing Start/End so editing an
    # old booking doesn't get stopped by two newly-required fields it never
    # had a chance to fill in the first place.
    hhmm = _clock_to_hhmm(form.get("event_start"))
    if hhmm:
        form["set_start"] = hhmm
    hhmm = _clock_to_hhmm(form.get("event_end"))
    if hhmm:
        form["set_end"] = hhmm
    # Band's own answers (2026-09-16): prefill from whatever's already on
    # file, the same way the band's own form prefills a returning artist —
    # reopening this booking shows what was last recorded, not a blank slate.
    if DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                artist = advance_db.find_artist_by_name(cur, b.get("artist_name"))
                sub = advance_db.newest_submission(cur, artist["id"]) if artist else None
            if sub:
                sub_data = sub.get("data") or {}
                for k in advance_db.BOOKING_BAND_ANSWER_FIELDS:
                    v = sub_data.get(k)
                    if v in (None, "") and sub.get(k) is not None:
                        v = sub.get(k)          # promoted column fallback
                        if isinstance(v, bool):  # own_iems / merch are BOOLEAN there
                            v = "Yes" if v else "No"
                    if v not in (None, ""):
                        form[k] = str(v)
        except Exception as e:  # noqa: BLE001
            _log_db_error("booking_band_answers_prefill", e)
    return form


def _set_start_taken(cur, venue, event_date, set_start, artist_name, series=None,
                     location=None, exclude_booking_id=None):
    """Another artist already starts at this exact time on this venue+date.

    This replaced _slot_taken on 2026-09-15 (audit #20's rule, re-pointed at the
    thing that now matters): set start decides who is Artist 1, so two artists
    sharing one start time makes the running order a coin flip. Refused here,
    where a human is sitting in front of the form and can fix it.
    A 3rd-party event is its own bill (Brian, 2026-09-14): its times never
    collide with the internal show's, and vice versa.

    exclude_booking_id (booking edit, 2026-09-14): the row being edited
    still carries its pre-edit values until the UPDATE commits, so a rename
    that keeps the same time would otherwise collide with itself — exclude
    it by id rather than by (now stale) name."""
    if not set_start:
        return None
    # audit 2026-09-16 #20 (root cause C): compare parsed minutes, not raw
    # text — "7:00" and "7:00pm" on one bill used to raise no clash at all
    # (a plain SQL string equality on event_start), and order wrong.
    target = advance_db.parse_clock(set_start)
    if target is None:
        return None
    third = advance_db.is_third_party(series)
    # Washington Park runs up to three stages on one date (Main Stage / Porch /
    # Bandstand), and two of them at 7:00pm is a normal night, not a mistake —
    # so a clash needs the same location too, not just the same venue.
    params = [venue, event_date, (location or "").strip(),
              advance_db.normalize(artist_name), third]
    exclude_sql = ""
    if exclude_booking_id:
        exclude_sql = " AND b.id <> %s"
        params.append(exclude_booking_id)
    cur.execute(
        r"""SELECT b.artist_name, b.event_start FROM bookings b
            LEFT JOIN artists a ON a.match_key = lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g')))
            LEFT JOIN shows s ON s.artist_id = a.id AND s.venue = b.venue AND s.show_date = b.event_date
            WHERE b.venue=%s AND b.event_date=%s
              AND COALESCE(btrim(b.location),'') = %s
              AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) <> %s
              AND s.cancelled_at IS NULL
              AND (lower(btrim(COALESCE(b.series,''))) = '3rd party') = %s"""
        + exclude_sql, params)
    for row in cur.fetchall():
        if advance_db.parse_clock(row["event_start"]) == target:
            return row["artist_name"]
    return None


def _validate_booking_data(f):
    """POST form -> (data dict, None) or (None, error message). Shared by
    every route that saves a bookings row (create, booking-only edit, and the
    merged show edit) so the rules can't drift between them (Brian, 2026-09-16
    — 'one page that lets me change anything with the booking or the artist').

    Rules (audit 2026-09-13):
      #3  contact email is required unless "Manual band advance" is checked
      #16 Series is required: a named series, "Stand-Alone Internal" or
          "3rd Party"; that pick sets Event Type (named series = Internal)
      Set Start / Set End (Brian, 2026-09-15) are required on every booking;
      they aren't stored fields themselves — see _derive_schedule."""
    data = {k: (f.get(k) or "").strip() for k in advance_db.BOOKING_FIELDS}
    data["skip_welcome_email"] = f.get("skip_welcome_email") == "on"
    data["draft_only"] = f.get("draft_only") == "on"
    # 3rd Party: the band gets no automated email unless this is ticked
    # (Brian, 2026-09-14). Meaningless for other series — always stored off.
    data["band_emails"] = f.get("band_emails") == "on" and advance_db.is_third_party(data["series"])
    if not data["entered_by"]:
        return None, "Who's entering this is required."
    if not data["venue"] or not advance_db.to_date(data["event_date"]):
        return None, "Venue and a valid event date are required."
    if not f.get("set_start") or not f.get("set_end"):
        return None, "Set Start and Set End are required."
    if not data["series"] or data["series"].lower() == "default":
        return None, "Pick a series — or Stand-Alone Internal / 3rd Party."
    # Brian, 2026-09-14: a 3rd-party event must have an Event Name, and its
    # artist/band is optional. The booking row still needs a name (it's the
    # upsert key and the sheet/artist match), so a blank one takes the event
    # name.
    if advance_db.is_third_party(data["series"]) and not data["event_name"]:
        return None, "Event Name is required for a 3rd-party event."
    if not data["artist_name"]:
        if not advance_db.is_third_party(data["series"]):
            return None, "Artist name is required."
        data["artist_name"] = data["event_name"]
    # Brian, 2026-09-14: a 3rd-party event usually comes with no band contact
    # at all — name, email and phone are optional for it. No email simply
    # means no welcome / reminders / day-before for that show.
    if (not data["skip_welcome_email"] and "@" not in data["contact_email"]
            and not advance_db.is_third_party(data["series"])):
        return None, "Contact email is required (or check Manual band advance)."
    data["event_type"] = _event_type_for_series(data["series"])
    # A series with a fixed schedule (Salsa On The Square, Brian, 2026-09-17)
    # pre-fills curfew with its baked-in value — load_in/soundcheck/
    # event_start/event_end aren't defaulted here because _derive_schedule
    # (right below) already derives all four from Set Start/Set End, which
    # by this point are required and present in `f` (checked above) — the
    # booking form's JS fills those two natively for a locked series, same
    # source (venue_email.SERIES_SCHEDULE_DEFAULTS) as this curfew default.
    # Blanks only — a staffer who typed an explicit curfew still wins.
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        import venue_email as ve
        curfew_default = ve.schedule_defaults_for(data["series"]).get("curfew")
        if curfew_default and not data.get("curfew"):
            data["curfew"] = curfew_default
    except Exception as e:  # noqa: BLE001 — a missing default just leaves the field blank
        _log_db_error("schedule_defaults_for", e)
    _derive_schedule(data, f)
    # audit 2026-09-16 #20 (root cause C): reject a bare "H:MM" with no
    # am/pm outright — Set Start/Set End are native <input type=time>
    # (always unambiguous 24h from the browser), but these five are free
    # text, and a typed "5:00" with no meridian is exactly how Rob Keenan's
    # FSQ 9/23 booking got emailed to the band as "5:00" instead of "5:00pm".
    for field in ("load_in", "soundcheck", "event_start", "event_end", "curfew"):
        v = data.get(field)
        if v and re.match(r"^\s*\d{1,2}:\d{2}\s*$", v):
            label = field.replace("_", " ").title()
            return None, f'{label} "{v}" needs am or pm — e.g. "{v}pm" or "{v}am".'
    return data, None


@app.route("/booking", methods=["GET", "POST"])
def booking():
    """Short staff intake form for a new artist booking. Writes to the bookings
    table, then runs the pipeline scoped to THIS show only (audit #1): seeds
    the sheet, files this show's doc (blank cells only), and — for a show
    already inside the 21-day window — triggers the welcome send right away.

    Rules (audit 2026-09-13):
      #3  contact email is required unless "Manual band advance" is checked
      #16 Series is required: a named series, "Stand-Alone Internal" or
          "3rd Party"; that pick sets Event Type (named series = Internal)
      #20 a set start already taken by another artist that night is refused —
          it decides the running order, so it has to be unique on the bill
      Set Start / Set End (Brian, 2026-09-15) are required on every booking;
      they aren't stored fields themselves — see _derive_schedule."""
    if request.method == "POST":
        f = request.form
        data, err = _validate_booking_data(f)
        if err:
            return _booking_form(err, f, 400)
        saved = False
        conflict_show_id = None
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    taken = _set_start_taken(cur, data["venue"], advance_db.to_date(data["event_date"]),
                                             data.get("event_start"), data["artist_name"],
                                             series=data["series"], location=data.get("location"))
                    if taken:
                        return _booking_form(
                            f"{taken} already starts at {data['event_start']} on "
                            f"{data['event_date']} — set start decides the running order, "
                            f"so two artists can't share one.", f, 409)
                    # audit 2026-09-16 #11: a re-POST for a band already
                    # booked this venue+date used to silently upsert via
                    # insert_booking's ON CONFLICT — no diff, no sheet_dirty,
                    # no "info changed" notice, and every checkbox this blank
                    # form defaults to unchecked (draft_only, skip_welcome_
                    # email, band_emails) would reset even if deliberately
                    # set before. Route through update_booking instead, same
                    # as an explicit edit would.
                    existing = advance_db.find_booking(cur, data["venue"],
                                                        advance_db.to_date(data["event_date"]),
                                                        data["artist_name"])
                    if existing:
                        advance_db.update_booking(cur, existing["id"], data)
                        conflict_show_id = advance_db.show_for_booking(
                            cur, data["artist_name"], data["venue"],
                            advance_db.to_date(data["event_date"]))
                        conflict_show_id = conflict_show_id["id"] if conflict_show_id else None
                    else:
                        advance_db.insert_booking(cur, data)
                    conn.commit()
                saved = True
            except Exception as e:
                _log_db_error("insert_booking", e)
        if not saved:
            return _booking_form("Couldn't save — the database is unreachable. Try again shortly.", f, 503)
        if conflict_show_id:
            return redirect(url_for("show_edit", show_id=conflict_show_id, updated=1))
        band_answers_saved = _record_booking_band_answers(f, request.files, data) is not None
        _notify_email("booking", data)
        show_date = advance_db.to_date(data.get("event_date"))
        days_out = (show_date - dt.date.today()).days if show_date else None
        urgent = days_out is not None and 0 <= days_out <= 21
        scope = f"{data['venue']}|{show_date.isoformat()}" if show_date else None
        if urgent:
            threading.Thread(target=_run_pipeline_then_trigger_now, args=(scope,), daemon=True).start()
        else:
            _run_pipeline_background(scope)
        # staff fill the form themselves for a manual advance, and for a
        # 3rd-party booking the band isn't emailed about
        silent_third = advance_db.is_third_party(data["series"]) and not data["band_emails"]
        # The fill-later link is only worth showing if the answers weren't
        # already entered right here (Brian, 2026-09-16 — the band's own
        # questions are now on this page, so the two-step "save, then click a
        # link to a second form" path is the fallback, not the default).
        fill_link = (_manual_fill_link(data)
                    if (data["skip_welcome_email"] or silent_third) and not band_answers_saved
                    else None)
        return render_template("booking.html", venues=forms_config.VENUES,
                               saved=data, urgent=urgent, band_answers_saved=band_answers_saved,
                               fill_link=fill_link, silent_third=silent_third)
    return _booking_form(form={})[0]


@app.route("/booking/<int:booking_id>/edit", methods=["GET", "POST"])
def booking_edit(booking_id):
    """Edit a logged booking's own core fields (venue/date/schedule/contact —
    the bookings row itself), distinct from /show/<id>/edit which
    edits the BAND'S advance-form answers. Same validation as /booking;
    writes via advance_db.update_booking, which queues an "info changed"
    email to the band (see BAND_FACING_FIELDS) when a band-facing field
    changed and the show is still inside the 21-day window — sent at the
    next daily lifecycle run, never immediately (Brian, 2026-09-14)."""
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        existing = advance_db.get_booking(cur, booking_id)
        if existing:
            show = advance_db.show_for_booking(cur, existing.get("artist_name"), existing.get("venue"),
                                               existing.get("event_date"))
        else:
            show = None
    if not existing:
        abort(404)
    # The merged edit page (Brian, 2026-09-16) is keyed by show_id — once a
    # show exists for this booking there's something to merge WITH (the
    # band's own answers), so a GET here goes straight there. Before a show
    # exists (the pipeline hasn't run yet, or this is a same-second re-open
    # right after creating the booking) there's genuinely nothing to merge —
    # this page keeps working exactly as it always has until that catches up.
    if request.method == "GET" and show:
        return redirect(url_for("show_edit", show_id=show["id"]))
    if request.method == "POST":
        f = request.form
        data, err = _validate_booking_data(f)
        if err:
            return _booking_form(err, f, 400, booking_id)
        changes, will_notify = {}, False
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                taken = _set_start_taken(cur, data["venue"], advance_db.to_date(data["event_date"]),
                                         data.get("event_start"), data["artist_name"],
                                         series=data["series"], location=data.get("location"),
                                         exclude_booking_id=booking_id)
                if taken:
                    return _booking_form(
                        f"{taken} already starts at {data['event_start']} on "
                        f"{data['event_date']} — set start decides the running order, "
                        f"so two artists can't share one.", f, 409, booking_id)
                was_draft_only = bool((advance_db.get_booking(cur, booking_id) or {}).get("draft_only"))
                changes, will_notify = advance_db.update_booking(cur, booking_id, data)
                # Clearing "draft, don't send" releases the hold: the welcome
                # sitting in drafts stops being the reason this show is quiet,
                # and the next lifecycle run sends it for real (Brian,
                # 2026-09-15). Ticking it on an already-sent show does nothing
                # — advance_draft_created_at is what that query gates on.
                if was_draft_only and not data["draft_only"]:
                    show = advance_db.show_for_booking(cur, data["artist_name"], data["venue"],
                                                       advance_db.to_date(data["event_date"]))
                    if show:
                        advance_db.clear_advance_held_draft(cur, show["id"])
                conn.commit()
        except Exception as e:
            _log_db_error("update_booking", e)
            return _booking_form("Couldn't save — the database is unreachable. Try again shortly.",
                                 f, 503, booking_id)
        band_answers_saved = _record_booking_band_answers(f, request.files, data) is not None
        show_date = advance_db.to_date(data.get("event_date"))
        scope = f"{data['venue']}|{show_date.isoformat()}" if show_date else None
        _run_pipeline_background(scope)
        return render_template("booking.html", venues=forms_config.VENUES,
                               saved=data, urgent=False, band_answers_saved=band_answers_saved,
                               edited=True, edit_changes=changes, will_notify=will_notify,
                               edit_booking_id=booking_id)
    return _booking_form(form=_booking_row_to_form(existing), edit_booking_id=booking_id)[0]


RUN_STATUS = BASE / "data" / "run_status.json"


@app.post("/booking/run")
def booking_run():
    """'Run again': starts a FULL run (every current show's doc, blank cells
    only) in the background and returns immediately (audit #23); the page
    polls /booking/run/status."""
    try:
        RUN_STATUS.write_text(json.dumps({"state": "running",
                                          "started": dt.datetime.now().isoformat(timespec="seconds")}))
        log_path = BASE / "data" / "run_now_background.log"
        with open(log_path, "a") as logf:
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} (Run again) ---\n")
            logf.flush()
            subprocess.Popen([sys.executable, "run_again.py", str(RUN_STATUS)], cwd=TOOLS_DIR,
                             stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)
    except Exception as e:
        _log_db_error("booking_run", e)
        return {"state": "error", "error": e.__class__.__name__}, 500
    return {"state": "running"}


@app.get("/booking/run/status")
def booking_run_status():
    try:
        return json.loads(RUN_STATUS.read_text())
    except (OSError, ValueError):
        return {"state": "idle"}


@app.get("/search")
def search():
    """Text search by band name, or browse venue -> series -> band when no
    query is typed. A query always wins over browse position (typing search
    clears the browse breadcrumb)."""
    q = request.args.get("q", "").strip()
    venue = request.args.get("venue", "").strip()
    series_param = request.args.get("series")  # unset=not chosen, "__none__"=no-series bucket
    results, venues, series_list, bands = [], [], [], []
    if q and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                results = advance_db.search_artists(cur, q)
        except Exception as e:
            _log_db_error("search", e)
    elif not q and DB_OK:
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                if venue and series_param is not None:
                    series = None if series_param == "__none__" else series_param
                    bands = advance_db.browse_bands(cur, venue, series)
                elif venue:
                    series_list = advance_db.browse_series(cur, venue)
                else:
                    venues = advance_db.browse_venues(cur)
        except Exception as e:
            _log_db_error("browse", e)
    return render_template(
        "search.html", q=q, results=results, db_ok=DB_OK,
        venue=venue, series=series_param,
        venues=venues, series_list=series_list, bands=bands,
    )


@app.get("/artist/<int:artist_id>")
def artist_detail(artist_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        artist = advance_db.get_artist(cur, artist_id)
        if not artist:
            abort(404)
        shows = [dict(s) for s in advance_db.artist_shows(cur, artist_id)]
        for s in shows:
            if advance_db.is_third_party(s.get("show_series")):
                s["band_emails"] = advance_db.band_emails_on(cur, s["show_id"])
        subs = advance_db.artist_submissions(cur, artist_id)
        files_by_sub = {s["id"]: advance_db.submission_files(cur, s["id"]) for s in subs}
    return render_template("artist.html", artist=artist, shows=shows,
                           subs=subs, files_by_sub=files_by_sub,
                           state_labels=DASHBOARD_STATE_LABELS, today=dt.date.today())


def _back(default):
    return redirect(_safe_next(request.form.get("next") or request.args.get("next") or default))


@app.post("/artist/<int:artist_id>/finalize/<int:show_id>")
def finalize_show(artist_id, show_id):
    """Human sign-off that a show's advance is fully complete (Brian,
    2026-09-13). Re-checks server-side that the show belongs to this artist
    and has a response on file; `WHERE finalized_at IS NULL` makes the stamp
    atomically idempotent, so the thank-you can never double-fire.

    Thank-you (audit #14): runs as a detached worker (tools/finalize_thankyou.py
    --send) that skips past/cancelled shows, records sent/failed on the show,
    and emails Brian if it couldn't send."""
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        show = advance_db.get_show(cur, show_id)
        if not show or show["artist_id"] != artist_id:
            abort(404)
        st = advance_db.show_state(cur, show_id)
        if st not in ("responded", "finalized"):
            abort(400, "This show has no response on file yet — nothing to finalize.")
        result = advance_db.finalize_show(cur, show_id)
        conn.commit()
    if result:
        _spawn_tool("finalize_thankyou.py", "--send", "--show-id", str(show_id),
                    log_name="thankyou.log")
    return redirect(url_for("artist_detail", artist_id=artist_id))


def _recap_for_draft(sub):
    """Compact 'what you sent us' block for the reply draft."""
    if not sub:
        return ""
    d = sub.get("data") or {}
    yn = lambda v: "Yes" if v is True else ("No" if v is False else None)  # noqa: E731
    rows = [
        ("Performers + crew", sub.get("performers")),
        ("Monitors", f"{sub['monitors']} wedges" if sub.get("monitors") is not None else None),
        ("IEMs", (d.get("uses_iems") or yn(sub.get("own_iems")))
                 + (f" — own system: {yn(sub.get('own_iems'))}" if str(d.get("uses_iems", "")).lower() == "yes" else "")
                 if (d.get("uses_iems") or sub.get("own_iems") is not None) else None),
        ("Split snake", sub.get("split_snake")),
        ("Stage", sub.get("stage_type")),
        ("Own engineer", sub.get("own_engineer")),
        ("Backline", d.get("backline")),
        ("Merch", yn(sub.get("merch"))),
        ("Band tent", sub.get("band_tent")),
        ("Vehicles", (f"{sub['vehicle_count']} total"
                      + (f", {sub['large_vehicle_count']} large" if sub.get("large_vehicle_count") is not None else ""))
                     if sub.get("vehicle_count") is not None else None),
        ("Stage plot", "on file" if d.get("stage_plot_file") else (d.get("stage_plot_desc") or None)),
        ("Scenic", d.get("scenic")), ("Lighting", d.get("lighting")),
        ("Stage escort", d.get("stage_escort_name")),
        ("Anything else", d.get("additional")),
        ("Changed since last time", d.get("changed_notes")),
    ]
    return "\n".join(f"  {k}: {v}" for k, v in rows if v not in (None, "", "None"))


def _queue_fsq_parking(rec):
    """Hold this Fountain Square submission's parking numbers for tomorrow's
    digest instead of drafting/sending anything now (Brian, 2026-09-15 —
    step 2, supersedes the per-submission draft built and live-tested
    earlier the same day: 'from this point forward... hold that information
    until the next day'). Best-effort, same pattern as _notify_email: never
    blocks or breaks the submission it came from. No-ops if the submission
    was never recorded to the DB (rec["_db"] unset) — there'd be nowhere to
    hold it."""
    db_ids = rec.get("_db")
    if not DB_OK or not db_ids:
        return
    try:
        vehicles = int(rec.get("vehicle_count") or 0)
    except (TypeError, ValueError):
        vehicles = 0
    try:
        large = int(rec.get("large_vehicle_count") or 0)
    except (TypeError, ValueError):
        large = 0
    show_date = None
    sd = (rec.get("show_date") or "").strip()
    if sd:
        try:
            show_date = dt.date.fromisoformat(sd)
        except ValueError:
            show_date = None
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.queue_fsq_parking(
                cur,
                artist_id=db_ids.get("artist_id"), show_id=db_ids.get("show_id"),
                band=rec.get("band_name") or "(no band name given)",
                venue="Fountain Square", show_date=show_date,
                contact_name=rec.get("contact_name"), contact_email=rec.get("contact_email"),
                contact_phone=rec.get("contact_phone"),
                vehicle_count=vehicles, large_vehicle_count=large)
            conn.commit()
    except Exception as e:  # noqa: BLE001
        _log_db_error("fsq_parking_queue", e)


@app.post("/internal/fsq-parking-digest")
def fsq_parking_digest():
    """Called once a day by n8n's 'FSQ Parking Digest' workflow. One email,
    only when there's something to report (Brian, 2026-09-15, step 2: 'if
    no new submissions have come in the night before, do not send the
    digest') — every FSQ band queued since the last run, broken out
    individually with its own contact info and regular-vehicle count, never
    just a grand total. Auto-sent for real to Mtully@3cdc.org, same
    real-send path as the ops Daily Digest — not a draft.

    Returns {"send": false} when the queue is empty so the workflow's own
    IF node skips the send step; this endpoint never sends anything
    itself, only says what to send. Marks every included item delivered
    before returning, same convention as the general digest_items queue
    (tools/daily_digest.py) — a downstream send failure would need a manual
    resend, not a silent duplicate tomorrow. Token-protected, same as
    /internal/daily-digest."""
    _internal_auth()
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        items = advance_db.undelivered_fsq_parking(cur)
        if not items:
            return {"send": False}
        rows_html = []
        for it in items:
            regular = max((it.get("vehicle_count") or 0) - (it.get("large_vehicle_count") or 0), 0)
            when = us_date(it["show_date"]) if it.get("show_date") else "(not given)"
            rows_html.append(
                "<tr>"
                "<td style='padding:8px 14px 8px 0;border-top:1px solid #ddd'>"
                f"<b>{mailer.esc(it['band'])}</b><br>"
                f"<span style='color:#666;font-size:12px'>{mailer.esc(when)}</span></td>"
                "<td style='padding:8px 14px;border-top:1px solid #ddd;font-size:13px'>"
                f"{mailer.esc(it.get('contact_name') or '(none given)')}<br>"
                f"{mailer.esc(it.get('contact_email') or '')}<br>"
                f"{mailer.esc(it.get('contact_phone') or '')}</td>"
                "<td style='padding:8px 0 8px 14px;border-top:1px solid #ddd;"
                "text-align:right;font-size:14px;font-weight:700'>"
                f"{regular}"
                "<div style='font-weight:400;color:#666;font-size:11px'>"
                f"of {it.get('vehicle_count') or 0} total, "
                f"{it.get('large_vehicle_count') or 0} large</div></td>"
                "</tr>")
        count = len(items)
        subject = f"FSQ Parking Validations — {count} band{'s' if count != 1 else ''}"
        html = (
            "<div style='font-family:-apple-system,sans-serif'>"
            f"<p>{count} Fountain Square band{'s' if count != 1 else ''} "
            "submitted since the last check:</p>"
            "<table style='border-collapse:collapse;width:100%'>"
            "<tr style='text-align:left;font-size:11px;color:#888;text-transform:uppercase'>"
            "<th style='padding:0 14px 6px 0'>Band / Date</th>"
            "<th style='padding:0 14px 6px'>Contact</th>"
            "<th style='padding:0 0 6px 14px;text-align:right'>Regular validations</th>"
            "</tr>" + "".join(rows_html) + "</table></div>")
        # Send here, from Flask, via the real-send path (audit 2026-09-16
        # #16) — this used to hand {send:true, subject, html} back to n8n's
        # own Send node and mark every item delivered regardless, so a
        # downstream send failure lost that night's parking validations for
        # good. Now delivered is stamped only once mailer.send confirms it.
        ok, err = mailer.send(FSQ_PARKING_NOTICE_TO, subject, html=html)
        if ok:
            advance_db.mark_fsq_parking_delivered(cur, [it["id"] for it in items])
            conn.commit()
        else:
            _log_db_error("fsq_parking_digest_send", RuntimeError(err))
    return {"send": ok, "subject": subject, "html": html, "to": FSQ_PARKING_NOTICE_TO,
           "error": None if ok else err}


def _build_reply_draft(show, artist, sub):
    first = (sub.get("contact_name") or (sub.get("data") or {}).get("contact_name") or "").strip().split(" ")[0]
    band = artist["name"]
    greeting = f"Hello {band}" if (not first or first.lower() in band.lower().split()) else f"Hello {first} and {band}"
    when = us_date(show["show_date"]) if show.get("show_date") else ""
    subject = f"Your {show['venue']} advance — {band}" + (f", {when}" if when else "")
    body = (f"{greeting},\n\n\n\n"
            "Thanks,\nBrian Lloyd\n3CDC Events / Production\n(315) 404-5648\n\n"
            "──────────────────────────────\n"
            f"For reference, what you sent us for {show['venue']}{(' on ' + when) if when else ''}:\n"
            f"{_recap_for_draft(sub)}\n")
    return subject, body


@app.post("/artist/<int:artist_id>/draft/<int:show_id>")
def draft_reply(artist_id, show_id):
    """Create an Outlook draft to the band's contact, addressed and with their
    answers pasted below, so a question thread starts from a real draft in
    Production@3cdc.org (Brian, 2026-09-14). Never sends. Answers JSON when
    asked for it (the dashboard), otherwise bounces back to the artist page."""
    if not DB_OK:
        abort(503)
    wants_json = "application/json" in (request.headers.get("Accept") or "")
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        show = advance_db.get_show(cur, show_id)
        artist = advance_db.get_artist(cur, artist_id)
        if not show or not artist or show["artist_id"] != artist_id:
            abort(404)
        cur.execute("SELECT * FROM submissions WHERE show_id=%s ORDER BY submitted_at DESC LIMIT 1", (show_id,))
        sub = cur.fetchone() or advance_db.newest_submission(cur, artist_id)
    to = ((sub or {}).get("contact_email") or artist.get("last_email") or "").strip()
    result = {"ok": False, "error": None, "link": None}
    if not to:
        result["error"] = "no contact email on file"
    else:
        subject, body = _build_reply_draft(show, artist, sub or {})
        ok, err, link = _create_outlook_draft(to, subject, body=body)
        if ok:
            result.update(ok=True, link=link, to=to)
        else:
            result["error"] = err
            _log_db_error("draft_reply", RuntimeError(err or "draft failed"))
    if wants_json:
        return result, (200 if result["ok"] else 502)
    q = ("drafted=1" if result["ok"] else "draft_error=" + quote(result["error"] or "failed"))
    return redirect(url_for("artist_detail", artist_id=artist_id) + "?" + q
                    + (f"&draft_link={quote(result['link'])}" if result.get("link") else ""))


def _spawn_tool(script, *args, log_name="tools_background.log"):
    try:
        log_path = BASE / "data" / log_name
        with open(log_path, "a") as logf:
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} {script} {' '.join(args)} ---\n")
            logf.flush()
            subprocess.Popen([sys.executable, script, *args], cwd=TOOLS_DIR,
                             stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)
    except Exception as e:
        _log_db_error(f"spawn_{script}", e)


# ── cancel / hold / merge (audit #4) ────────────────────────────────────────

@app.post("/show/<int:show_id>/cancel")
def show_cancel(show_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            abort(404)
        advance_db.cancel_show(cur, show_id)
        if s.get("hold_reason") == "missing from the advance sheet":
            advance_db.release_candidate_holds(cur, show_id)
        conn.commit()
    # Brian, 2026-09-17: used to wait for the 06:30 nightly run to rename the
    # filed doc and mark the act header — same-day fix, matching purge's own
    # immediate trigger just below.
    if s.get("show_date"):
        _run_pipeline_background(f"{s['venue']}|{s['show_date'].isoformat()}")
    return _back(url_for("artist_detail", artist_id=s["artist_id"]))


@app.post("/show/<int:show_id>/band-emails")
def show_band_emails(show_id):
    """3rd-party opt-in toggle on the artist page (Brian, 2026-09-14): turns
    the normal automated band emails on or off for this show's booking."""
    if not DB_OK:
        abort(503)
    on = request.form.get("on") == "1"
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            abort(404)
        advance_db.set_band_emails(cur, show_id, on)
        conn.commit()
    return _back(url_for("artist_detail", artist_id=s["artist_id"]))


@app.post("/show/<int:show_id>/advance-sent")
def show_advance_sent(show_id):
    """"I sent it myself" for a welcome that was held as a draft (Brian,
    2026-09-15). Stamps the show as advanced WITHOUT sending anything, which
    clearing the draft-only checkbox can't do — that one means "go ahead and
    send it", and would put a second copy in front of the band."""
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            abort(404)
        days_out = ((s["show_date"] - dt.date.today()).days
                    if s.get("show_date") else None)
        advance_db.mark_advance_sent_by_hand(cur, show_id, days_out)
        conn.commit()
    return _back(url_for("artist_detail", artist_id=s["artist_id"]))


@app.post("/show/<int:show_id>/purge")
def show_purge(show_id):
    """Irreversible: deletes this one show's submission, uploaded files,
    booking row, event act, and history entirely (Brian, 2026-09-15 —
    the 'complete removal' option on the dashboard's cancel dialog; the
    artist row and any other booking they have elsewhere is untouched — see
    advance_db.purge_show). `confirm_name` must match the artist's name
    exactly (case-insensitive) — the modal supplies it after the user types
    it; this is the server-side backstop so a bare POST can't fire it."""
    if not DB_OK:
        abort(503)
    body = request.get_json(silent=True) or {}
    confirm_name = (body.get("confirm_name") or "").strip().lower()
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            return {"ok": False, "error": "not-found"}, 404
        cur.execute("SELECT name FROM artists WHERE id=%s", (s["artist_id"],))
        row = cur.fetchone()
        real_name = (row["name"] if row else "") or ""
        if not confirm_name or confirm_name != real_name.strip().lower():
            return {"ok": False, "error": "name-mismatch"}, 400
        summary = advance_db.purge_show(cur, show_id)
        conn.commit()
    # root cause A (audit 2026-09-16): the sheet row goes now, not whenever the
    # next pipeline run happens to come along — the tombstone already stops a
    # resurrection, this just keeps the sheet honest and re-files what's left
    # of the bill without this act.
    if summary and summary.get("show_date"):
        _run_pipeline_background(f"{summary['venue']}|{summary['show_date']}")
    return {"ok": True, "summary": summary}


@app.post("/show/<int:show_id>/uncancel")
def show_uncancel(show_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            abort(404)
        advance_db.uncancel_show(cur, show_id)
        conn.commit()
    return _back(url_for("artist_detail", artist_id=s["artist_id"]))


@app.get("/show/<int:show_id>/hold")
def show_hold(show_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.show_with_artist(cur, show_id)
        if not s:
            abort(404)
        cands = advance_db.merge_candidates(cur, show_id)
        cur.execute("SELECT state FROM advance_status WHERE show_id=%s", (show_id,))
        st = (cur.fetchone() or {}).get("state")
    return render_template("show_hold.html", s=s, cands=cands, state=st,
                           state_labels=DASHBOARD_STATE_LABELS)


@app.post("/show/<int:show_id>/restore")
def show_restore(show_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.get_show(cur, show_id)
        if not s:
            abort(404)
        advance_db.restore_show(cur, show_id)
        advance_db.release_candidate_holds(cur, show_id)
        conn.commit()
    return redirect(url_for("show_hold", show_id=show_id))


@app.post("/show/<int:show_id>/merge/<int:target_id>")
def show_merge(show_id, target_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        tgt = advance_db.get_show(cur, target_id)
        if not tgt or not advance_db.get_show(cur, show_id):
            abort(404)
        old = advance_db.get_show(cur, show_id)
        advance_db.merge_shows(cur, show_id, target_id)
        advance_db.release_candidate_holds(cur, show_id)
        conn.commit()
    _run_pipeline_background([f"{x['venue']}|{x['show_date'].isoformat()}"
                              for x in {(old["venue"], old["show_date"]): old,
                                        (tgt["venue"], tgt["show_date"]): tgt}.values()
                              if x.get("show_date")])
    return redirect(url_for("artist_detail", artist_id=tgt["artist_id"]))


# ── doc change review (Brian, 2026-09-14) ────────────────────────────────────
# Anything a resubmission would change in a filled cell of the advance doc
# waits on /doc-review for Keep doc / Use new (docmerge's resubmission review).

@app.route("/show/<int:show_id>/edit", methods=["GET", "POST"])
def show_edit(show_id):
    """The one place to edit a show (Brian, 2026-09-16 — 'doesn't make sense
    to' keep Edit Booking and Edit Form as two separate pages once one of them
    could already touch the band's own answers; merged into one screen, one
    Save): booking logistics (venue/date/schedule/contact/series/toggles) and
    the band's own questions together.

    Keyed by show_id, not booking_id, because show_id is the more universal
    handle — a show can exist (from a real band submission) with no staff
    booking ever logged for it. When a booking row IS on file, this edits it
    in place exactly as /booking/<id>/edit always has (same validation, same
    'info changed' notice on a band-facing change); when one ISN'T, saving
    here creates it — nothing distinguishes the two from the person typing,
    same as Brian asked for."""
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        s = advance_db.show_with_artist(cur, show_id)
        if not s:
            abort(404)
        booking = advance_db.get_booking_for_show(cur, s)

    if request.method == "POST":
        f = request.form
        data, err = _validate_booking_data(f)
        if err:
            return _booking_form(err, f, 400, show_id=show_id)
        # Venue / date / artist are editable here again (Brian, 2026-09-19:
        # "even when finalized I need to be able to edit all fields"). They
        # were pinned to the show's own values (audit 2026-09-16 #10) because
        # changing one forked a brand-new show onto the new identity — fresh
        # welcome, blank stamps — while the original sat behind until holds.py
        # parked it as an orphan. carry_show_with_booking (root cause A,
        # 2026-09-17) is the real fix and now covers this page: the show
        # moves/renames WITH the booking, keeping its stamps, submissions and
        # filed doc, and merges into any show already sitting on the new
        # venue+date. update_booking calls it; when this show has no bookings
        # row yet, the else branch below calls it directly.
        if not data.get("event_date") and s["show_date"]:
            data["event_date"] = s["show_date"].isoformat()
        new_date = advance_db.to_date(data.get("event_date"))
        moved = (data["venue"], new_date) != (s["venue"], s["show_date"])
        renamed = advance_db.normalize(data["artist_name"]) != advance_db.normalize(s["artist_name"])
        old_ident = {"artist_name": s["artist_name"], "venue": s["venue"],
                     "event_date": s["show_date"]}
        changes, will_notify = {}, False
        booking_id = booking["id"] if booking else None
        artist_id = s["artist_id"]
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                taken = _set_start_taken(cur, data["venue"], new_date,
                                         data.get("event_start"), data["artist_name"],
                                         series=data["series"], location=data.get("location"),
                                         exclude_booking_id=booking_id)
                if taken:
                    return _booking_form(
                        f"{taken} already starts at {data['event_start']} on "
                        f"{data['event_date']} — set start decides the running order, "
                        f"so two artists can't share one.", f, 409, show_id=show_id)
                if renamed or moved:
                    # A move/rename can land on an identity staff already
                    # logged a booking for. Shows merge (carry_show_with_
                    # booking does it); two bookings rows can't — uq_bookings_
                    # ident owns that key — so say which one to edit instead
                    # of failing on the constraint. With no bookings row of
                    # our own, that existing row IS the one to edit.
                    there = advance_db.find_booking(cur, data["venue"], new_date,
                                                    data["artist_name"])
                    if there and there["id"] != booking_id:
                        if booking_id:
                            return _booking_form(
                                f"{data['artist_name']} is already booked at {data['venue']} on "
                                f"{data['event_date']}. Edit that booking instead of moving this "
                                f"one onto it.", f, 409, show_id=show_id)
                        booking_id = there["id"]
                released_draft = False
                if booking_id:
                    was_draft_only = bool((advance_db.get_booking(cur, booking_id) or {}).get("draft_only"))
                    changes, will_notify = advance_db.update_booking(cur, booking_id, data)
                    released_draft = was_draft_only and not data["draft_only"]
                else:
                    booking_id = advance_db.insert_booking(cur, data)
                    if renamed or moved:
                        advance_db.carry_show_with_booking(cur, old_ident, data)
                # The show can come out of that under a different id — a merge
                # into a show already on the new venue+date keeps the one
                # that was there — so everything below works on the survivor,
                # not the id this request came in on. The held-draft release
                # waits for it too: clearing the stamp on a row the merge just
                # deleted would silently do nothing.
                survivor = advance_db.show_for_booking(cur, data["artist_name"], data["venue"], new_date)
                if survivor:
                    show_id, artist_id = survivor["id"], survivor["artist_id"]
                if released_draft:
                    advance_db.clear_advance_held_draft(cur, show_id)
                conn.commit()
        except Exception as e:
            _log_db_error("show_edit_save", e)
            return _booking_form("Couldn't save — the database is unreachable. Try again shortly.",
                                 f, 503, show_id=show_id)
        answer_result = _record_booking_band_answers(
            f, request.files, data, existing_artist_id=artist_id)
        band_answers_saved = answer_result is not None
        scope = [f"{data['venue']}|{new_date.isoformat()}"] if new_date else []
        # A move leaves the old bill an act short — rebuild that doc too, or
        # it keeps showing a band that isn't playing there any more.
        if moved and s["show_date"]:
            scope.append(f"{s['venue']}|{s['show_date'].isoformat()}")
        _run_pipeline_background(scope)
        # staff-typed band answers file into the doc exactly like a real
        # submission would (audit #10 test gap, found running the staging
        # suite 2026-09-16): without this, a staff edit's submission row
        # never got its doc regenerated or doc_checked_at stamped, leaving
        # doc-review's "waiting" state stuck forever for it.
        if answer_result:
            _regen_submitted_show(
                {"venue": data["venue"], "show_date": data["event_date"],
                 "band_name": answer_result.get("artist_name") or data["artist_name"]},
                submission_id=answer_result.get("submission_id"))
        return render_template("booking.html", venues=forms_config.VENUES,
                               saved=data, urgent=False, band_answers_saved=band_answers_saved,
                               edited=True, edit_changes=changes, will_notify=will_notify,
                               show_id=show_id)

    form = _booking_row_to_form(booking or {
        "artist_name": s["artist_name"], "venue": s["venue"], "event_date": s["show_date"],
        "contact_email": s.get("last_email") or "",
    })
    # Series/artist name/venue/date come from the SHOW when there's no booking
    # to read them from yet. All four are editable (2026-09-19) — a change to
    # artist/venue/date carries the show itself, see the POST branch.
    if not form.get("series"):
        form["series"] = s.get("show_series") or ""
    return _booking_form(form=form, show_id=show_id)[0]


def _review_date(v):
    try:
        return dt.date.fromisoformat((v or "")[:10])
    except ValueError:
        abort(400, "bad date")


@app.get("/doc-review")
def doc_review():
    if not DB_OK:
        abort(503)
    venue = request.args.get("venue") or ""
    d = _review_date(request.args.get("date"))
    sub_id = request.args.get("sub", type=int)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        notices = advance_db.open_doc_notices(cur, venue, d)
        sub = advance_db.get_submission(cur, sub_id) if sub_id else None
        cur.execute("""SELECT field, doc_value, new_value, resolution, resolved_at FROM doc_notices
                       WHERE venue=%s AND event_date=%s AND kind='diff' AND resolved_at IS NOT NULL
                         AND resolved_at > now() - interval '2 hours'
                         AND resolution IN ('kept', 'applied')
                       ORDER BY resolved_at DESC LIMIT 20""", (venue, d))
        recent = cur.fetchall()
        cur.execute("""SELECT a.name FROM shows s JOIN artists a ON a.id=s.artist_id
                       WHERE s.venue=%s AND s.show_date=%s AND s.cancelled_at IS NULL ORDER BY a.name""",
                    (venue, d))
        bands = [r["name"] for r in cur.fetchall()]
    waiting_check = bool(sub and not sub.get("doc_checked_at"))
    applying = any(n.get("apply_requested_at") and not n.get("apply_error") for n in notices)
    return render_template("doc_review.html", venue=venue, d=d, notices=notices, sub=sub,
                           waiting=waiting_check or applying, waiting_check=waiting_check,
                           recent=recent, bands=bands)


@app.post("/doc-review/decide")
def doc_review_decide():
    if not DB_OK:
        abort(503)
    venue = request.form.get("venue") or ""
    d = _review_date(request.form.get("date"))
    apply_ids = []
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        for n in advance_db.open_doc_notices(cur, venue, d):
            choice = request.form.get(f"n{n['id']}")
            if choice == "keep":
                advance_db.keep_doc_value(cur, n)
            elif choice == "apply" and n.get("cell_key"):
                cur.execute("""UPDATE doc_notices SET apply_requested_at=now(), apply_error=NULL
                               WHERE id=%s""", (n["id"],))
                apply_ids.append(n["id"])
        conn.commit()
    if apply_ids:
        try:
            log_path = BASE / "data" / "doc_review.log"
            with open(log_path, "a") as logf:
                logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} "
                           f"apply {apply_ids} ---\n")
                logf.flush()
                subprocess.Popen([sys.executable, "doc_review.py", "--apply", *map(str, apply_ids)],
                                 cwd=TOOLS_DIR, stdout=logf, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        except Exception as e:
            _log_db_error("doc_review_apply", e)
    return redirect(url_for("doc_review", venue=venue, date=d.isoformat()))


# ── submission ↔ booking matches (audit #6) ─────────────────────────────────

@app.get("/submission-match/<int:match_id>")
def submission_match(match_id):
    if not DB_OK:
        abort(503)
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        m = advance_db.get_match(cur, match_id)
        if not m:
            abort(404)
        sub = advance_db.get_submission(cur, m["submission_id"])
        current = advance_db.show_with_artist(cur, sub["show_id"]) if sub and sub.get("show_id") else None
        cur.execute(
            """SELECT s.id AS show_id, a.name AS artist_name, s.venue, s.show_date, s.responded_at
               FROM shows s JOIN artists a ON a.id=s.artist_id
               WHERE s.venue=%s AND s.cancelled_at IS NULL
                 AND s.show_date BETWEEN %s::date - 30 AND %s::date + 30
                 AND NOT EXISTS (SELECT 1 FROM submissions x WHERE x.show_id=s.id)
               ORDER BY abs(s.show_date - %s::date), a.name""",
            (m["venue"], m["show_date"], m["show_date"], m["show_date"]))
        options = cur.fetchall()
    return render_template("submission_match.html", m=m, sub=sub, current=current, options=options)


@app.post("/submission-match/<int:match_id>/confirm")
def submission_match_confirm(match_id):
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE submission_matches SET status='confirmed', resolved_at=now() WHERE id=%s",
                    (match_id,))
        conn.commit()
    return redirect(url_for("submission_match", match_id=match_id))


@app.post("/submission-match/<int:match_id>/detach")
def submission_match_detach(match_id):
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        m = advance_db.get_match(cur, match_id)
        if not m:
            abort(404)
        sub = advance_db.get_submission(cur, m["submission_id"])
        advance_db.detach_submission(cur, m["submission_id"], m["typed_name"], m["venue"],
                                     m["show_date"], series=(sub.get("data") or {}).get("show_series") or None)
        cur.execute("UPDATE submission_matches SET status='detached', resolved_at=now() WHERE id=%s",
                    (match_id,))
        conn.commit()
    return redirect(url_for("submission_match", match_id=match_id))


@app.post("/submission-match/<int:match_id>/attach/<int:show_id>")
def submission_match_attach(match_id, show_id):
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        m = advance_db.get_match(cur, match_id)
        if not m or not advance_db.get_show(cur, show_id):
            abort(404)
        advance_db.reattach_submission(cur, m["submission_id"], show_id)
        cur.execute("""UPDATE submission_matches SET status='attached_manual', booked_show_id=%s,
                       resolved_at=now() WHERE id=%s""", (show_id, match_id))
        conn.commit()
        s = advance_db.show_with_artist(cur, show_id)
    _regen_submitted_show({"venue": s["venue"], "show_date": s["show_date"].isoformat(),
                           "band_name": s["artist_name"]})
    return redirect(url_for("submission_match", match_id=match_id))


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


@app.get("/venue-doc/<venue>/<path:filename>")
def venue_doc(venue, filename):
    """Serves a venue's standing email attachment (load-in doc, tech pack)
    by direct link (audit 2026-09-16 #17) — a reminder/day-before email
    links here instead of re-attaching the same file the welcome already
    sent. No auth, same sensitivity as the public form itself: the filename
    must start with the fixed `_attachment` prefix venue_email.py writes it
    under, and must resolve inside that one venue's own folder."""
    sys.path.insert(0, str(TOOLS_DIR))
    import venue_email as ve
    if not filename.startswith("_attachment"):
        abort(404)
    vdir = (ve.SERIES_EMAIL_ROOT / venue.strip()).resolve()
    target = (vdir / filename).resolve()
    if vdir not in target.parents or not target.is_file():
        abort(404)
    return send_from_directory(vdir, filename, as_attachment=False)


@app.get("/stage-plot/<venue>/<date>/<path:filename>")
def stage_plot_file(venue, date, filename):
    """Serves a filed stage plot by a stable URL (Brian, 2026-09-17). The
    advance doc's stage-plot hyperlink used to be a bare relative filename
    (Word resolving it against "wherever the folder lives") — that only
    works when the viewer has real local filesystem access next to the doc.
    Opening the doc on a phone (Word mobile, Dropbox's own preview) has no
    such access at all ("no handler for the stage plot file"), and even on
    desktop it depended on Dropbox having already materialized the sibling
    file. No auth, same sensitivity as the public form itself and venue_doc
    above — the filename must resolve inside that one venue+month's own
    folder, which is all the path-safety this needs."""
    sys.path.insert(0, str(TOOLS_DIR))
    import fieldspec as fs
    try:
        d = dt.date.fromisoformat(date)
    except ValueError:
        abort(404)
    folder = (fs.real_dropbox_root() / fs.real_venue_folder(venue) / fs.real_month_folder(venue, d)).resolve()
    target = (folder / filename).resolve()
    if folder not in target.parents or not target.is_file():
        abort(404)
    return send_from_directory(folder, filename, as_attachment=False)


LIFECYCLE_LOCK_KEY = 874201913


def _internal_auth():
    token = request.headers.get("X-Advance-Token") or ""
    if not INTERNAL_TOKEN or not hmac.compare_digest(token, INTERNAL_TOKEN):
        abort(403)


@app.post("/internal/advance-lifecycle")
def advance_lifecycle():
    """Called by n8n's daily 9am 'Advance Lifecycle Check' (?source=cron) and
    on demand for a late booking. Sends for real via Outlook.

      - WELCOME (initial advance): a show within 21 days, not yet welcomed,
        not responded, not cancelled / on hold, not a manual-entry booking.
      - FOLLOW-UPS at 7 / 3 / 1 days out while there's no response.
      - UNRESPONDED ALERT to Brian at 3 days out (manual-entry shows too).

    Audit 2026-09-13:
      #3  a send is stamped ONLY when mailer confirms it (Graph 202). A
          failure, a missing email address, or a draft that didn't render
          leaves the show unsent — it retries on the next run — and Brian
          gets one email per show/kind per day naming the band and the error.
      #5  each show is stamped the moment its send is confirmed (its own
          commit), and a Postgres advisory lock lets only one lifecycle run
          send at a time — a second run waits, then sees the stamps.
      #21 only the closest open reminder sends per show per run (older open
          ones are marked skipped), so a missed day never sends two at once.
          Each scheduled run is recorded for the 10:15 watchdog."""
    _internal_auth()
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    source = (request.args.get("source") or "on-demand").strip()[:20]
    sys.path.insert(0, str(TOOLS_DIR))
    import venue_email as ve

    # audit 2026-09-16 ops #4 (Brian's call: the cheap fix): gunicorn kills
    # this worker at 120s regardless of what it's mid-write on — a large
    # welcome batch could get SIGKILLed between a confirmed send and its
    # own commit. The per-show loops below check this and stop themselves
    # cleanly well before that, so whatever's left over just runs on the
    # next scheduled pass instead of being killed uncleanly.
    deadline = time.monotonic() + 100
    ran_out_of_time = False

    lock_conn = advance_db.get_conn()
    lock_conn.autocommit = True
    initial, followup, failures, dayahead, booking_updates = [], [], 0, [], []
    held_drafts = []
    drafts_dir = None
    try:
        lock_conn.execute("SELECT pg_advisory_lock(%s)", (LIFECYCLE_LOCK_KEY,))
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.record_job_run(cur, "advance-lifecycle", source)
            # audit 2026-09-16 security #9: both tables grow forever with
            # nothing else that ever prunes them. Rides the daily 9am run —
            # no new systemd unit needed.
            advance_db.prune_short_links_and_gate_attempts(cur)
            conn.commit()

        def fail(show_id, kind, error):
            nonlocal failures
            failures += 1
            with advance_db.get_conn() as c2, c2.cursor() as k:
                advance_db.record_send_failure(k, show_id, kind, error)
                c2.commit()

        # ── welcomes ──
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            due_initial = advance_db.shows_due_for_initial_advance(cur)
        if due_initial:
            batch = [{
                "name": r["artist_name"], "show_date": r["show_date"].isoformat(),
                "venue": r["venue"] or "", "series": r["series"] or "",
                "email": r["email"] or "", "location": r["location"] or "",
                "event_name": r["event_name"] or "", "lead_name": r["lead_name"] or "",
                "lead_phone": r["lead_phone"] or "", "load_in": r["load_in"] or "",
                "soundcheck": r["soundcheck"] or "", "event_start": r["event_start"] or "",
                "event_end": r["event_end"] or "", "curfew": r["curfew"] or "",
                "set_time": r["set_time"] or "",
                "email_note": r["email_note"] or "",
                "contact_name": r["contact_name"] or "",
                "contact_email": r["booking_contact_email"] or "",
            } for r in due_initial]
            batch_file = TOOLS_DIR / f".lifecycle_initial_batch_{os.getpid()}.json"
            batch_file.write_text(json.dumps(batch))
            # Review 2026-09-14 (M5): render into this run's own folder, not
            # the shared tools/drafts/ that every package run wipes — a
            # booking landing mid-run used to delete a draft between render
            # and read, and the mtime glob could pick up a stale file.
            import tempfile
            drafts_dir = Path(tempfile.mkdtemp(prefix="lifecycle-drafts-", dir=str(TOOLS_DIR)))
            rendered = True
            render_error = ""
            try:
                # check=True dropped (audit 2026-09-16 #15): draft_emails.py
                # now catches per-row failures itself and keeps rendering the
                # rest of the batch, so a nonzero exit here means something
                # genuinely fatal (not one bad row) — either way, per-show
                # fallback below (checking `hits`) already handles a show
                # that has no rendered file, so raising on a bad exit code
                # only added a less informative failure path on top of it.
                proc = subprocess.run([sys.executable, "draft_emails.py", str(batch_file),
                                       "--out", str(drafts_dir)],
                                      cwd=TOOLS_DIR, capture_output=True, text=True,
                                      timeout=180)
                if proc.returncode != 0:
                    rendered = False
                    render_error = (proc.stderr or proc.stdout or "").strip()[-500:]
                    _log_db_error("lifecycle_draft_render",
                                  RuntimeError(f"exit {proc.returncode}: {render_error}"))
            except Exception as e:
                rendered = False
                render_error = repr(e)
                _log_db_error("lifecycle_draft_render", e)
            finally:
                batch_file.unlink(missing_ok=True)

            from draft_emails import slug as _dslug
            seen_shows = set()
            for r in due_initial:
                if time.monotonic() > deadline:
                    ran_out_of_time = True
                    break
                if r["show_id"] in seen_shows:      # H1 belt-and-braces
                    continue
                seen_shows.add(r["show_id"])
                if not r["email"]:
                    if not advance_db.is_third_party(r["series"]):
                        fail(r["show_id"], "welcome", "no contact email on file")
                    continue
                hits = sorted(drafts_dir.glob(f"{_dslug(r['artist_name'])}__{r['show_date'].isoformat()}__*.md"),
                              key=lambda p: p.stat().st_mtime, reverse=True)
                if not rendered or not hits:
                    reason = "welcome email didn't render"
                    if render_error:
                        reason += f" — {render_error}"
                    fail(r["show_id"], "welcome", reason)
                    continue
                text = hits[0].read_text()
                subj_line, _, body = text.partition("\n")
                subject = subj_line.removeprefix("Subject:").strip()
                # "Draft the advance email, don't send it" (Brian, 2026-09-15):
                # the welcome lands in Production@3cdc.org's drafts and a human
                # sends it. The show is NOT stamped as advanced — the band
                # hasn't been contacted — so the reminder cadence stays shut
                # until the box is cleared. See advance_db.mark_advance_held_as_draft.
                welcome_to = ve.with_extra_recipients(r["email"], r["series"])
                if r.get("draft_only"):
                    ok, err, link = _create_outlook_draft(
                        welcome_to, subject, body=body.lstrip("\n"),
                        attachments=ve.venue_attachments(r["venue"]))
                    if not ok:
                        fail(r["show_id"], "welcome_draft", err)
                        continue
                    with advance_db.get_conn() as conn, conn.cursor() as cur:
                        advance_db.mark_advance_held_as_draft(cur, r["show_id"])
                        conn.commit()
                    held_drafts.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                                        "show_date": us_date(r["show_date"]), "link": link})
                    continue
                ok, err = _send_outlook_email(welcome_to, subject, body=body.lstrip("\n"),
                                              attachments=ve.venue_attachments(r["venue"]))
                if not ok:
                    if err and err.startswith("TIMEOUT:"):
                        # audit 2026-09-16 #17: unknown outcome — Graph may
                        # have actually sent it despite the timeout here.
                        # Stop the automatic retry (a real retry risks a
                        # genuine double-send) by stamping this show sent,
                        # same as a confirmed send would; record it as
                        # welcome_unknown, not welcome, so the daily failure
                        # digest tells Brian to verify by hand rather than
                        # reporting a plain failure that isn't necessarily one.
                        with advance_db.get_conn() as conn, conn.cursor() as cur:
                            advance_db.mark_advance_drafted(cur, r["show_id"])
                            conn.commit()
                        fail(r["show_id"], "welcome_unknown", err)
                    else:
                        fail(r["show_id"], "welcome", err)
                    continue
                days_out = (r["show_date"] - dt.date.today()).days
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    advance_db.mark_advance_drafted(cur, r["show_id"])
                    advance_db.mark_stale_followup_tiers_skipped(cur, r["show_id"], days_out)
                    conn.commit()
                initial.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                                "show_date": us_date(r["show_date"])})
            import shutil as _shutil
            _shutil.rmtree(drafts_dir, ignore_errors=True)

        # ── follow-ups: closest open tier only, per show (#21) ──
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            by_show = {}
            for tier in advance_db.FOLLOWUP_TIERS:
                for r in advance_db.shows_due_for_followup(cur, tier):
                    by_show.setdefault(r["show_id"], []).append((tier, r))
        for show_id, tiers in by_show.items():
            if time.monotonic() > deadline:
                ran_out_of_time = True
                break
            tiers.sort(key=lambda t: t[0])
            tier, r = tiers[0]
            older = [t for t, _ in tiers[1:]]
            if not r["email"]:
                if not advance_db.is_third_party(r["series"]):
                    fail(show_id, f"followup_{tier}", "no contact email on file")
                continue
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                token = _signer.dumps({"a": r["artist_id"],
                                       "s": {"venue": r["venue"],
                                             "date": r["show_date"].isoformat(),
                                             "series": r["series"] or None,
                                             "location": r["location"] or None,
                                             "contact_name": r["contact_name"] or None,
                                             "contact_email": r["booking_contact_email"] or None}})
                code = advance_db.get_or_create_short_link(cur, token)
                conn.commit()
            link = f"{PUBLIC_URL}/s/{code}"
            when = f" on {us_date(r['show_date'])}" if r["show_date"] else ""
            subject = f"Reminder — performance details for your 3CDC show ({r['venue']}{when})"
            # audit 2026-09-16 #23: reuse the welcome's own greeting rule
            # instead of a separate inline one that lacked its "don't
            # repeat the name" guard — a solo act booked under their own
            # name used to read "Hello Patsy Meyer and Patsy Meyer and
            # Groove Latin".
            from draft_emails import _greeting_contact_name
            greeting_name = _greeting_contact_name(r["contact_name"], r["artist_name"])
            greeting = (f"Hello {greeting_name} and {r['artist_name']}"
                        if greeting_name else f"Hello {r['artist_name']}")
            body = (
                f"{greeting},\n\n"
                f"Circling back on the performance details for your show at "
                f"{r['venue']}{when} — we still need them to run it well: stage "
                "plot, monitors, hospitality, and a couple of site logistics. "
                "It takes about five minutes:\n\n"
                f"{link}\n\n"
                "If you've already sent this over, disregard. Thanks,\n"
                "3CDC Events / Production"
            )
            # Review 2026-09-14 (M2): a bilingual series (Salsa) gets the
            # Spanish half under the English one, same shape as its welcome.
            if r["series"] and ve.is_bilingual_series(r["series"]):
                greeting_es = (f"Hola {greeting_name} y {r['artist_name']}"
                               if greeting_name else f"Hola {r['artist_name']}")
                when_es = f" el {us_date(r['show_date'])}" if r["show_date"] else ""
                body_es = (
                    f"{greeting_es},\n\n"
                    f"Les escribimos de nuevo sobre los detalles de su presentación en "
                    f"{r['venue']}{when_es} — todavía los necesitamos para que el show salga bien: "
                    "plano de escenario, monitores, hospitalidad y un par de detalles logísticos. "
                    "Toma unos cinco minutos:\n\n"
                    f"{link}?lang=es\n\n"
                    "Si ya nos enviaron esta información, ignoren este mensaje. Gracias,\n"
                    "3CDC Eventos / Producción"
                )
                sep = "─" * 42
                body = f"{body}\n\n{sep}\nESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}"
            # audit 2026-09-16 #17: link the venue's standing docs instead of
            # re-attaching them — the welcome already carried the real
            # attachment (every FSQ email was carrying its own 1.4 MB copy).
            doc_links = ve.venue_doc_links_text(r["venue"])
            if doc_links:
                body = f"{body}\n\n{doc_links}"
            ok, err = _send_outlook_email(ve.with_extra_recipients(r["email"], r["series"]), subject, body=body)
            if not ok:
                fail(show_id, f"followup_{tier}", err)
                continue
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                advance_db.mark_followup_sent(cur, show_id, tier, sent=True)
                for t in older:
                    advance_db.mark_followup_sent(cur, show_id, t, sent=False)
                conn.commit()
            followup.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                             "show_date": us_date(r["show_date"]), "days_out": tier})

        # ── unresponded-at-3-days alert to Brian ──
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            due_unresponded = advance_db.shows_due_for_unresponded_alert(cur, 3)
        unresponded_sent = 0
        if due_unresponded:
            band_word = "band" if len(due_unresponded) == 1 else "bands"
            subject = (f"Advance follow-up needed — {len(due_unresponded)} {band_word} "
                       "unresponded at 3 days out")
            tr = "".join(
                f"<tr><td style=\"padding:4px 10px 4px 0;color:#6b7280;font:13px -apple-system,sans-serif\">"
                f"{mailer.esc(r['artist_name'])}"
                + (" <b style='color:#b45309'>MANUAL — staff never filled the form</b>" if r["manual"] else "")
                + f"</td><td style=\"padding:4px 0;font:13px -apple-system,sans-serif\">"
                f"<b>{mailer.esc(r['venue'] or '')}</b> — {us_date(r['show_date'])}</td></tr>"
                for r in due_unresponded)
            html = (f"<div style=\"font-family:-apple-system,sans-serif\">"
                    f"<p>These bands are now inside the 3-day mark with no advance form on file — "
                    f"worth a manual follow-up:</p><table>{tr}</table>"
                    f"<p style=\"margin-top:14px\"><a href=\"{PUBLIC_URL}/dashboard\">Open the dashboard →</a></p></div>")
            # Review 2026-09-14 (E1): queued for the digest + the dashboard
            # panel (which lists these live anyway) instead of its own email.
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                advance_db.queue_digest_item(cur, "unresponded", subject, html, f"{PUBLIC_URL}/dashboard")
                for r in due_unresponded:
                    advance_db.mark_unresponded_alert_sent(cur, r["show_id"])
                conn.commit()
            unresponded_sent = len(due_unresponded)

        # ── day-before confirmations (review 2026-09-14, E5) ──
        # Skipped entirely once the deadline's passed — small phases, but
        # every bit of headroom left matters once welcome/followup already
        # ate the budget (audit 2026-09-16 ops #4).
        if not ran_out_of_time:
            try:
                from dayahead import send_due as _dayahead_send_due
                dayahead = _dayahead_send_due(fail)
            except Exception as e:  # noqa: BLE001 — never blocks the rest of the run
                _log_db_error("dayahead", e)
                dayahead = []

        # ── booking-edit "info changed" notices (Brian, 2026-09-14) ──
        if not ran_out_of_time:
            try:
                from booking_update import send_due as _booking_update_send_due
                booking_updates = _booking_update_send_due(fail)
            except Exception as e:  # noqa: BLE001 — never blocks the rest of the run
                _log_db_error("booking_update", e)
                booking_updates = []

        # ── thank-you, automatic (audit 2026-09-16 #23, Brian's call) ──
        # finalize_thankyou.send_for_show already records its own outcome
        # (thankyou_sent_at/thankyou_error) and queues its own digest item
        # on failure — nothing here needs fail() too.
        thankyou = []
        if not ran_out_of_time:
            try:
                from finalize_thankyou import send_for_show as _send_thankyou
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    due_thankyou = advance_db.shows_due_for_thankyou(cur)
                for show_id in due_thankyou:
                    if time.monotonic() > deadline:
                        ran_out_of_time = True
                        break
                    try:
                        _send_thankyou(show_id)
                        thankyou.append(show_id)
                    except Exception as e:  # noqa: BLE001 — one show's failure never blocks the rest
                        _log_db_error("thankyou_auto", e)
            except Exception as e:  # noqa: BLE001 — never blocks the rest of the run
                _log_db_error("thankyou_auto", e)

        _email_send_failures()
    except Exception as e:
        _log_db_error("advance_lifecycle", e)
        return {"error": e.__class__.__name__, "initial": initial, "followup": followup,
                "held_drafts": held_drafts}, 500
    finally:
        try:
            lock_conn.execute("SELECT pg_advisory_unlock(%s)", (LIFECYCLE_LOCK_KEY,))
        except Exception:
            pass
        lock_conn.close()
        if drafts_dir:
            import shutil as _shutil
            _shutil.rmtree(drafts_dir, ignore_errors=True)

    return {"initial": initial, "followup": followup, "dayahead": dayahead,
            "held_drafts": held_drafts, "booking_updates": booking_updates,
            "thankyou": thankyou, "ran_out_of_time": ran_out_of_time,
            "unresponded_alert_sent": unresponded_sent, "failures": failures}


def _email_send_failures():
    """One email listing every send failure not yet reported (at most one per
    show / kind / day, via send_failures)."""
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        rows = advance_db.unnotified_send_failures(cur)
    if not rows:
        return
    tr = "".join(
        f"<tr><td style='padding:4px 10px'>{mailer.esc(r['artist_name'])}</td>"
        f"<td style='padding:4px 10px'>{mailer.esc(r['venue'])} {us_date(r['show_date'])}</td>"
        f"<td style='padding:4px 10px'>{mailer.esc(r['kind'])}</td>"
        f"<td style='padding:4px 10px'>{mailer.esc(r['error'])}</td></tr>" for r in rows)
    html = ("<div style='font-family:-apple-system,sans-serif;font-size:13px'>"
            "<p>These emails did <b>not</b> go out. Nothing was marked sent — each one retries on the "
            "next run. Fix whatever's named (a missing address, an Outlook/n8n problem) and it will send.</p>"
            "<table border='1' cellspacing='0' style='border-collapse:collapse'>"
            "<tr><th>Band</th><th>Show</th><th>Email</th><th>Why</th></tr>" + tr + "</table></div>")
    ok, _ = mailer.alert(f"Advance emails NOT sent — {len(rows)} need attention", html)
    if ok:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.mark_send_failures_notified(cur, [r["id"] for r in rows])
            conn.commit()


@app.post("/internal/lifecycle-watchdog")
def lifecycle_watchdog():
    """Called by a VM systemd timer at 10:15 (audit #21): if today's scheduled
    9am lifecycle check never reached this app, email Brian once."""
    _internal_auth()
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    today9 = dt.datetime.combine(dt.date.today(), dt.time(8, 55))
    with advance_db.get_conn() as conn, conn.cursor() as cur:
        ran = advance_db.job_ran_since(cur, "advance-lifecycle", "cron", today9)
        alerted = advance_db.job_ran_since(cur, "lifecycle-watchdog-alert", "auto",
                                           dt.datetime.combine(dt.date.today(), dt.time()))
    if ran or alerted:
        return {"ran": ran, "alerted": alerted}
    ok, err = mailer.alert(
        "Advance 9am check did NOT run today",
        "<p>The daily Advance Lifecycle Check (welcomes, reminders, the 3-day alert) didn't run "
        "this morning — n8n or the VM may be down. Nothing was sent today. Check n8n; the next "
        "run catches up (one reminder per band, never a pile).</p>")
    if ok:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.record_job_run(cur, "lifecycle-watchdog-alert", "auto")
            conn.commit()
    return {"ran": False, "alert_sent": ok, "error": err}


@app.post("/internal/run-recap-extraction")
def run_recap_extraction():
    """Called by n8n's daily 2am 'Advance Recap Extraction' check. For every
    show that finished at least 3 days ago and doesn't have one yet, converts
    its filed advance .docx to PDF + MD (next to the .docx in the Dropbox
    venue tree) and stores the parsed recap — see tools/extract_advance_recap.py
    for why this can't just live in events/event_acts. Token-protected, same
    as /internal/run-followups. Never touches anything band-facing directly;
    the stored recap is read later by draft_emails.py for a returning artist."""
    _internal_auth()
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    sys.path.insert(0, str(TOOLS_DIR))
    from extract_advance_recap import run as _run_extraction
    try:
        result = _run_extraction()
    except Exception as e:
        _log_db_error("run_recap_extraction", e)
        return {"error": e.__class__.__name__}, 500
    return result


@app.post("/internal/daily-digest")
def daily_digest():
    """Called by n8n's daily 'Daily Digest' workflow. Builds the morning
    ops summary (today's shows, today's crew across every staffed venue,
    advancing activity in the last 24h, every show within 14 days ranked
    with its live status — Brian, 2026-09-09) and hands back
    {subject, html, to} for n8n's Send Summary node to send via Outlook for
    real, same as every band-facing advance/follow-up email since the
    2026-09-13 live-send migration. Absorbed the standalone Crew
    Report's daily send the same day ("combine the two emails into one");
    that workflow's cron trigger was removed, only its on-demand webhook
    remains, still served by /internal/crew-report below.
    Token-protected, same as /internal/run-followups."""
    _internal_auth()
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    sys.path.insert(0, str(TOOLS_DIR))
    from daily_digest import build_digest
    try:
        subject, html, queued_ids = build_digest(mark_delivered=False)
    except Exception as e:
        _log_db_error("daily_digest", e)
        return {"error": e.__class__.__name__}, 500
    # comma-separated — internal_send_outlook.json's Send via Graph node
    # splits b.to on "," into one Graph recipient per address (Brian,
    # 2026-09-15: add aschultes@3cdc.org).
    to = "blloyd@3cdc.org,aschultes@3cdc.org"
    # Send here, from Flask (audit 2026-09-16 #16) — queued digest_items
    # (doc notices, pipeline failures, etc.) are stamped delivered only once
    # this confirms sent; a failed send used to lose them for good, since
    # build_digest() marked them delivered unconditionally before handing
    # off to n8n's own Send node.
    ok, err = mailer.send(to, subject, html=html)
    if ok:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.mark_digest_items_delivered(cur, queued_ids)
            conn.commit()
    else:
        _log_db_error("daily_digest_send", RuntimeError(err))
    return {"subject": subject, "html": html, "to": to, "sent": ok,
           "error": None if ok else err}


@app.post("/internal/crew-report")
def crew_report_endpoint():
    """Standalone, on-demand only (n8n's 'Crew Report' webhook — its daily
    cron trigger was removed 2026-09-09 now that Daily Digest carries
    today's crew every morning). Who's staffing every venue over the next
    14 days — Mix/Tech/Stagehand/Stage Support/Other, straight from the
    public 3CDC staffing sheet. Doesn't touch advance-db at all (pure
    staffing-sheet read), so no DB_OK gate. Token-protected, same as the
    other /internal endpoints."""
    _internal_auth()
    sys.path.insert(0, str(TOOLS_DIR))
    from crew_report import build_report
    try:
        html = build_report(days=14)
    except Exception as e:
        _log_db_error("crew_report", e)
        return {"error": e.__class__.__name__}, 500
    return {"subject": "3CDC Crew Report — Next 14 Days", "html": html, "to": "blloyd@3cdc.org"}


@app.post("/internal/missing-reports")
def missing_reports_endpoint():
    """Diff endpoint for n8n's 'Report Reminder' workflow (daily noon). n8n
    holds the Google Sheets OAuth credential for the private Form Responses
    sheet and POSTs the submitted rows here; this endpoint reads the PUBLIC
    staffing roster itself (staffing.collect_days()) and returns who's still
    missing a report. Re-added 2026-09-16 — the 09-14 build added this route
    straight on the VM and never committed it, so the 09-15 deploy overwrote
    it and the workflow errored daily until this audit caught it. Token-
    protected, same as the other /internal endpoints. Doesn't touch
    advance-db at all (pure staffing-sheet + posted-rows diff), so no DB_OK
    gate."""
    _internal_auth()
    body = request.get_json(silent=True) or {}
    submissions = body.get("submissions") or []
    days = body.get("days") or 7
    sys.path.insert(0, str(TOOLS_DIR))
    from missing_reports import build_missing
    try:
        return build_missing(submissions, days=days)
    except Exception as e:
        _log_db_error("missing_reports", e)
        return {"error": e.__class__.__name__}, 500


@app.errorhandler(413)
def _too_large(e):
    lang = (request.form.get("form_lang") or request.args.get("lang") or "en")
    msg = ("El archivo es demasiado grande. Por favor comprímalo e intente de nuevo."
           if lang == "es" else
           "That file is too large. Please compress it and try again.")
    return msg, 413


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
