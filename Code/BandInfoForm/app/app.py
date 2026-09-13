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
import threading
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
import i18n
import es_translate

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
GATE_PASS_2 = os.environ.get("ADVANCE_GATE_PASS_2", "1313")
VALID_GATE_PASSES = {p for p in (GATE_PASS, GATE_PASS_2) if p}
INTERNAL_TOKEN = os.environ.get("ADVANCE_INTERNAL_TOKEN", "")
PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
NOTIFY_URL = os.environ.get("ADVANCE_NOTIFY_URL", "")
LIFECYCLE_NOW_URL = os.environ.get("ADVANCE_LIFECYCLE_NOW_URL", "")
CLEANUP_DRAFTS_URL = os.environ.get("ADVANCE_CLEANUP_DRAFTS_URL", "")
# n8n's real-send webhook, called directly (Brian, 2026-09-13) for the
# unresponded-at-3-days alert — an actual SEND, never a draft, so it skips
# the "Advance Notify" formatting workflow NOTIFY_URL points at (that one's
# shape is booking/submission-specific). Flask and n8n run on the same VM
# (see n8n/README.md), so localhost:5678 is a safe default with no env var
# required — override only if that ever changes.
INTERNAL_SEND_URL = os.environ.get("ADVANCE_INTERNAL_SEND_URL",
                                    "http://localhost:5678/webhook/internal-send-outlook")
UNRESPONDED_ALERT_TO = os.environ.get("ADVANCE_UNRESPONDED_ALERT_TO", "blloyd@3cdc.org")
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
    return render_template(
        "form.html", venues=forms_config.VENUES, cfg=cfg,
        prefill={}, returning=False, artist_name=None,
        tech_packs=forms_config.tech_packs(),
        known_artist_id=None, locked_venue=False, locked_date=False,
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
    # This act's slot drives a couple of form tweaks (FSQ hides the drum-riser
    # question for openers/direct support — Brian, 2026-09-11). Looked up live
    # so it works for links issued before slot was carried anywhere.
    slot = None
    if payload.get("a") and DB_OK and seed.get("venue") and seed.get("date"):
        try:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                slot = advance_db.slot_for(cur, payload["a"], seed["venue"], seed["date"])
        except Exception as e:
            _log_db_error("slot_lookup", e)
    cfg = forms_config.get_config(
        series_key=series, venue=seed.get("venue") or request.args.get("venue"),
        location=seed.get("location") or request.args.get("location"), slot=slot,
        lang=_lang())
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
    # Seed venue/date into prefill independent of the DB lookup below — these
    # come straight from the signed token, so a locked field still renders its
    # real value even if the artist lookup skips or fails (DB down, no match).
    if locked_venue:
        prefill["venue"] = seed["venue"]
    if locked_date:
        prefill["show_date"] = seed["date"]
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
        known_artist_id=known_artist_id, locked_venue=locked_venue,
        locked_date=locked_date,
    )


@app.post("/submit")
def submit():
    f = request.form
    if not f.get("band_name"):
        abort(400, "Band name is required.")

    # Stage plot: upload OR description is required, not both (Brian,
    # 2026-09-08) — exempt only if this band already has one on file (same
    # "only upload if it has changed" rule the form itself follows). Real
    # server-side check, not just the form's client-side one.
    upload = request.files.get("stage_plot_file")
    has_upload = bool(upload and upload.filename)
    has_desc = bool((f.get("stage_plot_desc") or "").strip())
    if not has_upload and not has_desc:
        has_existing = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    # Prefer the known artist id (same reasoning as
                    # record_submission's known_id) — a band that just edited
                    # its own name shouldn't lose its "already have a stage
                    # plot on file" exemption because the edited text no
                    # longer matches its old match_key.
                    artist = None
                    known_id = f.get("artist_id")
                    if known_id:
                        try:
                            artist = advance_db.get_artist(cur, int(known_id))
                        except (TypeError, ValueError):
                            artist = None
                    if not artist:
                        artist = advance_db.find_artist_by_name(cur, f.get("band_name"))
                    if artist:
                        sub = advance_db.newest_submission(cur, artist["id"])
                        if sub and (sub.get("data") or {}).get("stage_plot_file"):
                            has_existing = True
            except Exception as e:
                _log_db_error("stage_plot_check", e)
        if not has_existing:
            abort(400, "Please provide a stage plot upload or a description — at least one is required.")

    # WP location monitor cap — hard limit (Brian, 2026-09-06): Porch/Bandstand/
    # Main Stage each have a physical wedge count that can't be exceeded.
    if f.get("venue") == "Washington Park" and f.get("location") in forms_config.WP_LOCATIONS:
        cap = forms_config.WP_LOCATIONS[f["location"]]["monitor_cap"]
        try:
            requested = int(f.get("monitors") or 0)
        except ValueError:
            requested = 0
        if requested > cap:
            abort(400, f"{f['location']} is limited to {cap} monitors — please enter {cap} or fewer.")

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

    # 0) A Spanish-language submission (form_lang, carried on the hidden
    # form_lang field set by the language the band's form was rendered in —
    # see i18n.py) gets its free-text answers translated to English HERE,
    # before anything downstream — disk JSON, Postgres, the notify email,
    # the filed advance/daysheet doc — ever sees them (Brian, 2026-09-12).
    # Every select/radio/number field is already English regardless of
    # language (i18n.py only swaps the on-screen label, never the stored
    # value), so only the open textareas need this. Fails soft: on any
    # error (no API key configured, the API down/slow, a bad response) the
    # original Spanish text is left in place rather than blocking or
    # corrupting the submission.
    if (rec.get("form_lang") or "").strip().lower() == "es":
        try:
            es_translate.translate_es_fields(rec, log=_log_db_error)
        except Exception as e:
            _log_db_error("es_translate", e)

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

    # 4) Regenerate ONLY this band's advance doc in the background (Brian,
    # 2026-09-11) — a submit must not re-file every other show. Fire-and-forget:
    # the band's thank-you page never waits on it.
    _regen_submitted_show(rec)

    # 5) A band that just submitted no longer needs a "please fill this out"
    # nag sitting in Outlook — clean up any stale draft for them (Brian,
    # 2026-09-12). Best-effort, same as the notify/regen steps above.
    _cleanup_outlook_drafts(rec)

    # The language the BAND used (carried on the form's hidden form_lang
    # field), not whatever ?lang= happens to be on this POST's query string
    # (there usually isn't one) — explicit kwargs here win over the
    # context processor's query-string-based default (Flask re-applies the
    # caller's own context keys last).
    submitted_lang = "es" if (f.get("form_lang") or "").strip().lower() == "es" else "en"
    return render_template("thanks.html", band=f.get("band_name"),
                            lang=submitted_lang, t=i18n.translator(submitted_lang))


def _regen_submitted_show(rec):
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
                 "--date", date, "--artist", artist],
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


def _send_outlook_email(to, subject, body=None, html=None, attachment=None, timeout=15):
    """Fire an ACTUAL send (never a draft) via n8n's 'Internal Send —
    Outlook' webhook — used for BOTH Brian's own internal alerts and, as
    of the 2026-09-13 live-send migration, band-facing advance/follow-up
    email too (previously routed through 'Internal Create Draft' for
    Brian to review; that path is no longer used by this app). Pass
    `body` for plain text (the normal case — every advance/follow-up
    email is plain text) or `html` for a formatted internal alert; not
    both. `attachment` is (name, content_type, base64_content), same
    shape venue_email.venue_attachment() returns. Best-effort: never
    raises, returns True/False so the caller can decide whether to stamp
    a 'sent' flag. Never blocks the request it's called from beyond the
    timeout (band-facing sends get a longer one than internal alerts —
    Graph attachment uploads can be slow)."""
    if not INTERNAL_SEND_URL:
        return False
    try:
        import urllib.request
        payload = {"to": to, "subject": subject}
        if html:
            payload["html"] = html
        else:
            payload["body"] = body or ""
        if attachment:
            payload["attachment_name"], payload["attachment_type"], payload["attachment_content"] = attachment
        req = urllib.request.Request(
            INTERNAL_SEND_URL, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN},
        )
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception as e:
        _log_db_error("send_outlook_email", e)
        return False


def _send_internal_email(subject, html, to=None):
    """Brian's own internal alerts (HTML) — thin wrapper over
    _send_outlook_email defaulting `to` to his address."""
    return _send_outlook_email(to or UNRESPONDED_ALERT_TO, subject, html=html)


def _cleanup_outlook_drafts(rec):
    """Best-effort: once a band submits, any drafted (or scheduled-but-unsent)
    Outlook email still sitting there for them is stale — delete it so nobody
    accidentally sends a "please fill this out" nag to a band that already
    responded (Brian, 2026-09-12).

    Matches by the artist's own KNOWN contact email (artists.last_email — the
    address any advance/follow-up draft was actually addressed to), not
    whatever the band just typed into the form — that could be a different
    band member's inbox than the one staff have on file and drafted to."""
    if not CLEANUP_DRAFTS_URL or not DB_OK:
        return
    try:
        email = None
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            artist = None
            known_id = rec.get("artist_id")
            if known_id:
                try:
                    artist = advance_db.get_artist(cur, int(known_id))
                except (TypeError, ValueError):
                    artist = None
            if not artist:
                artist = advance_db.find_artist_by_name(cur, rec.get("band_name"))
            if artist:
                email = (artist.get("last_email") or "").strip()
        if not email:
            return
        import urllib.request
        body = json.dumps({"band": rec.get("band_name"), "email": email}).encode()
        req = urllib.request.Request(
            CLEANUP_DRAFTS_URL, data=body,
            headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN},
        )
        urllib.request.urlopen(req, timeout=8)
    except Exception as e:
        _log_db_error("cleanup_outlook_drafts", e)


def _run_pipeline_background():
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
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} ---\n")
            logf.flush()
            subprocess.Popen(
                [sys.executable, "run_now.py"], cwd=TOOLS_DIR,
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


def _run_pipeline_then_trigger_now():
    """Late-booking path: a show inside the 21-day window at the moment it's
    booked can't wait for the next daily check the way a normal-lead-time
    booking can (Brian, 2026-09-03). Runs the pipeline SYNCHRONOUSLY so the
    show is actually seeded in the database before triggering the immediate
    draft + notify — then fires it. Runs in a background thread (not the
    request thread) so /booking's response is never held up by it."""
    try:
        subprocess.run([sys.executable, "run_now.py"], cwd=TOOLS_DIR,
                        capture_output=True, text=True, timeout=240)
    except Exception as e:
        _log_db_error("late_booking_pipeline", e)
        return
    _trigger_immediate_advance()


# ── gated views (passcode) ──────────────────────────────────────────────────

GATED_PREFIXES = ("/staff", "/search", "/artist", "/file", "/submission", "/booking", "/dashboard")


@app.before_request
def _gate():
    p = request.path
    if p.startswith(GATED_PREFIXES) and not session.get("auth"):
        return redirect(url_for("gate", next=p))


@app.route("/gate", methods=["GET", "POST"])
def gate():
    if request.method == "POST":
        if request.form.get("passcode") in VALID_GATE_PASSES:
            session["auth"] = True
            return redirect(request.args.get("next") or url_for("staff"))
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

DASHBOARD_STATE_LABELS = {
    "queued":           ("Queued",          "queued"),
    "awaiting":         ("Awaiting Window", "awaiting"),
    "ready_to_send":    ("Ready to Send",   "ready"),
    "followup_due":     ("Follow-up Due",   "due"),
    "followup_drafted": ("Follow-up Sent",  "followup"),
    "responded":        ("Advanced",        "responded"),
}


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.get("/dashboard/data")
def dashboard_data():
    """JSON feed the dashboard polls. Rows sharing a venue+date are grouped
    into one bill (same assumption `shows`' own unique constraint makes —
    artist+venue+date is the booking key) so a multi-band night reads as one
    card, not three separate ones."""
    if not DB_OK:
        return {"error": "db-unavailable", "bills": [], "generated_at": dt.datetime.now().isoformat()}, 503
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            rows = advance_db.dashboard_status(cur)
    except Exception as e:
        _log_db_error("dashboard_data", e)
        return {"error": "query-failed", "bills": [], "generated_at": dt.datetime.now().isoformat()}, 500

    bills, order = {}, []
    for r in rows:
        key = (r["show_date"], r["venue"])
        if key not in bills:
            bills[key] = {
                "date": r["show_date"].isoformat() if r["show_date"] else None,
                "venue": r["venue"] or "Venue TBD",
                "series": r["show_series"] or "",
                "days_until": r["days_until_show"],
                "acts": [],
            }
            order.append(key)
        label, css = DASHBOARD_STATE_LABELS.get(r["state"], (r["state"] or "Unknown", "queued"))
        bills[key]["acts"].append({
            "band": r["band"], "state": r["state"],
            "state_label": label, "state_css": css,
        })
    return {"bills": [bills[k] for k in order], "generated_at": dt.datetime.now().isoformat()}


BOOKING_SLOTS = ["headliner", "direct_support", "opener"]


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
    table, then runs the pipeline — seeds the sheet, builds the package, and
    gets the initial advance sent via Outlook without anyone clicking anything
    (live-send migration, Brian 2026-09-13 — used to draft in Gmail, then
    Outlook; now a real send). A show already inside the 21-day window at
    booking time can't wait for the next daily check: that case runs the
    pipeline synchronously (background thread, response isn't held up) and
    triggers the send + notify right away. Everything else runs on the
    normal next-daily-check cadence."""
    if request.method == "POST":
        f = request.form
        if not f.get("artist_name") or not f.get("entered_by"):
            return render_template("booking.html", venues=forms_config.VENUES,
                                   wp_locations=list(forms_config.WP_LOCATIONS),
                                   slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                                   locked_schedule_series=_locked_schedule_series(),
                                   error="Artist name and who's entering this are required.",
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
                                   wp_locations=list(forms_config.WP_LOCATIONS),
                                   slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                                   locked_schedule_series=_locked_schedule_series(),
                                   error="Couldn't save — the database is unreachable. Try again shortly.",
                                   form=f), 503
        _notify_email("booking", data)
        show_date = advance_db.to_date(data.get("event_date"))
        days_out = (show_date - dt.date.today()).days if show_date else None
        urgent = days_out is not None and 0 <= days_out <= 21
        if urgent:
            # inside the 21-day window at booking time — can't wait for the
            # next daily check like a normal-lead-time booking can.
            threading.Thread(target=_run_pipeline_then_trigger_now, daemon=True).start()
        else:
            _run_pipeline_background()
        return render_template("booking.html", venues=forms_config.VENUES,
                               slots=BOOKING_SLOTS, saved=data, urgent=urgent)
    return render_template("booking.html", venues=forms_config.VENUES,
                           wp_locations=list(forms_config.WP_LOCATIONS),
                           slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                           locked_schedule_series=_locked_schedule_series(), form={})


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
    """Called by n8n's daily 'Advance Lifecycle Check', and on-demand for a
    late booking (see _trigger_immediate_advance). LIVE-SEND MIGRATION
    (Brian, 2026-09-13): both guardrails below now SEND for real (via
    _send_outlook_email, straight to n8n's internal-send-outlook webhook)
    instead of building an Outlook draft for Brian to review — no more
    human-in-the-loop step for either one. Three guardrails (drafting-vs-
    sending history: drafted immediately at booking 2026-09-03; live-send
    migration + tier cadence trimmed to 7/3/1 + unresponded alert all
    2026-09-13):
      - INITIAL advance sends itself as soon as a booking is seeded — no
        21-day wait. Reuses draft_emails.py's render as-is (writes to
        tools/drafts/*.md same as always, unchanged), so the NEW-vs-
        RETURNING 6-month cross-venue check applies automatically, then
        sends that rendered content directly instead of turning it into a
        draft. Right after sending, any FOLLOWUP_TIERS mark already on or
        before TODAY (same day counts as already-passed too — a reminder
        never fires the same day as the welcome) is pre-skipped for this
        show for good (mark_stale_followup_tiers_skipped) — only tiers
        still strictly ahead of today stay open to fire later as their
        date arrives. The old 21-day "your draft is ready to send" nudge
        (shows_due_for_send_reminder/send_reminder_sent_at) is RETIRED —
        nothing to nudge about once the welcome sends itself.
      - FOLLOW-UP sends itself if nothing's heard back, at each of 7/3/1
        days out from the show (advance_db.FOLLOWUP_TIERS, trimmed from
        7/3/2/1 — the 2-day tier is gone) — date-driven, not tied to when
        the initial went out. Each tier fires at most once, independently,
        whether it actually sent (an email existed) or was marked resolved
        with nothing to send (mark_followup_sent(..., sent=False) for a
        band with no email on file, or because it was pre-skipped as
        stale above) — either way it never asks again for that tier.
      - UNRESPONDED ALERT fires ONE real email to Brian (bypassing n8n's
        draft path entirely, same as the two above) the first time a show
        crosses 3 days out with no submission on file — a flag for him to
        follow up by hand, listing every band that qualifies this run.
        Independent of the tier-3 band-facing follow-up above (own
        shows.unresponded_alert_sent_at column, own gate) and NOT skipped
        for a band with no email — he especially wants to know about those.
    due_followup/due_unresponded are queried in a FRESH query, after
    due_initial's own sends are committed, not before — a late booking
    already inside one of those windows at the moment it's booked must
    show up in THIS SAME run, not wait for tomorrow (bug found 2026-09-13:
    querying them up front, before due_initial's advance_draft_created_at
    commit, meant a same-request late booking could never appear in its
    own run since every one of these gates requires
    advance_draft_created_at IS NOT NULL).
    initial/followup come back as lightweight {artist_name, venue,
    show_date} summaries (no subject/body/to — those already went out for
    real) purely for n8n's own digest email to Brian. Token-protected,
    same as /internal/run-followups."""
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
    if not DB_OK:
        return {"error": "db-unavailable"}, 503

    initial, followup = [], []
    sys.path.insert(0, str(TOOLS_DIR))
    import venue_email as ve
    try:
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            due_initial = advance_db.shows_due_for_initial_advance(cur)

        # due_followup/due_reminders are queried AFTER due_initial is fully
        # processed and committed below, not up here (bug found 2026-09-13:
        # a late booking inside its OWN follow-up tier at the moment it's
        # booked — e.g. a Salsa band booked only 4 days out — was drafting
        # its initial advance but silently missing an immediately-due
        # follow-up for a full day, until the next 9am cron. Both queries
        # gate on `advance_draft_created_at IS NOT NULL`
        # (shows_due_for_followup/shows_due_for_send_reminder), which is
        # still NULL for a show due_initial hasn't drafted yet — querying
        # them here, before that commit, meant a same-request late booking
        # could never appear in its own run's due_followup, even when it's
        # already inside that tier's window. send_reminder never showed
        # this symptom only because the ready_now branch below already
        # special-cases it inline; follow-up had no equivalent. Querying
        # both fresh after the commit fixes it for good instead of adding
        # another one-off special case.)

        # ── initial advances: reuse draft_emails.py wholesale (NEW/RETURNING,
        # venue blocks, short link, bill grouping — all of it, unchanged) ──
        if due_initial:
            # every field draft_emails.py's batch format understands, not just
            # the bare minimum — see shows_due_for_initial_advance's 2026-09-08
            # fix note for why this list matters.
            batch = [{
                "name": r["artist_name"], "show_date": r["show_date"].isoformat(),
                "venue": r["venue"] or "", "series": r["series"] or "",
                "email": r["email"] or "", "location": r["location"] or "",
                "event_name": r["event_name"] or "", "lead_name": r["lead_name"] or "",
                "lead_phone": r["lead_phone"] or "", "load_in": r["load_in"] or "",
                "soundcheck": r["soundcheck"] or "", "event_start": r["event_start"] or "",
                "event_end": r["event_end"] or "", "curfew": r["curfew"] or "",
                "slot": r["slot"] or "", "set_time": r["set_time"] or "",
                "email_note": r["email_note"] or "",
                "band_count": str(r["band_count"]) if r["band_count"] else "",
                "contact_name": r["contact_name"] or "",
                "contact_email": r["booking_contact_email"] or "",
            } for r in due_initial]
            batch_file = TOOLS_DIR / ".lifecycle_initial_batch.json"
            batch_file.write_text(json.dumps(batch))
            try:
                subprocess.run([sys.executable, "draft_emails.py", str(batch_file)],
                               cwd=TOOLS_DIR, capture_output=True, text=True,
                               timeout=120, check=True)
            finally:
                batch_file.unlink(missing_ok=True)

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
                    # advance_draft_created_at is stamped regardless of
                    # whether an email address exists — the show has now
                    # been through the pipeline once, same as before this
                    # change; a band with no email just never gets sent
                    # anything (same gap that existed under drafting too).
                    days_out = (r["show_date"] - dt.date.today()).days if r["show_date"] else None
                    if r["email"]:
                        att = ve.venue_attachment(r["venue"])
                        ok = _send_outlook_email(r["email"], subject, body=body.lstrip("\n"),
                                                  attachment=att)
                        if ok:
                            initial.append({"artist_name": r["artist_name"],
                                            "venue": r["venue"] or "",
                                            "show_date": us_date(r["show_date"])})
                    advance_db.mark_advance_drafted(cur, r["show_id"])
                    # Live-send migration (Brian, 2026-09-13): the welcome
                    # sends for real the moment the booking is seeded, so
                    # there's no draft left sitting around to nudge Brian
                    # about at the 21-day mark — mark_send_reminder_sent /
                    # shows_due_for_send_reminder are retired, not called
                    # anywhere anymore. Any FOLLOWUP_TIERS mark that's
                    # already on or before TODAY (same day as this welcome
                    # counts as "already passed" too) gets permanently
                    # skipped for this show instead of firing a backdated
                    # reminder later — only tiers still ahead of today stay
                    # open to fire normally as their date arrives.
                    advance_db.mark_stale_followup_tiers_skipped(cur, r["show_id"], days_out)
                conn.commit()

        # Fresh queries, now that any show due_initial just drafted has its
        # advance_draft_created_at actually committed — see the note above
        # due_initial for why this can't run any earlier in this request.
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            # (show_id, tier) tag carried alongside each row so mark_followup_sent
            # below stamps the RIGHT tier — a show can legitimately show up under
            # more than one tier across different runs, never more than once per tier.
            due_followup = [(tier, r) for tier in advance_db.FOLLOWUP_TIERS
                             for r in advance_db.shows_due_for_followup(cur, tier)]
            due_unresponded = advance_db.shows_due_for_unresponded_alert(cur, 3)

        # ── follow-ups: date-driven, short-link, "performance detail" wording,
        # fired for real at each of 7/3/1 days out (advance_db.FOLLOWUP_TIERS)
        # — live-send migration, Brian 2026-09-13. A tier already on or before
        # the day a show was booked never reaches this point at all: it was
        # pre-skipped in the due_initial loop above (mark_stale_followup_
        # tiers_skipped), so shows_due_for_followup never returns it.
        if due_followup:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                for tier, r in due_followup:
                    if not r["email"]:
                        advance_db.mark_followup_sent(cur, r["show_id"], tier, sent=False)
                        continue
                    token = _signer.dumps({"a": r["artist_id"],
                                           "s": {"venue": r["venue"],
                                                 "date": r["show_date"].isoformat(),
                                                 "series": r["series"] or None,
                                                 "location": r["location"] or None,
                                                 "contact_name": r["contact_name"] or None,
                                                 "contact_email": r["booking_contact_email"] or None}})
                    code = advance_db.get_or_create_short_link(cur, token)
                    link = f"{PUBLIC_URL}/s/{code}"
                    when = f" on {us_date(r['show_date'])}" if r["show_date"] else ""
                    subject = f"Reminder — performance details for your 3CDC show ({r['venue']}{when})"
                    greeting = (f"Hello {r['contact_name']} and {r['artist_name']}"
                                if r["contact_name"] else f"Hello {r['artist_name']}")
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
                    att = ve.venue_attachment(r["venue"])
                    ok = _send_outlook_email(r["email"], subject, body=body, attachment=att)
                    if ok:
                        followup.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                                          "show_date": us_date(r["show_date"]), "days_out": tier})
                    advance_db.mark_followup_sent(cur, r["show_id"], tier, sent=ok)
                conn.commit()

        # ── unresponded-at-3-days alert: a real SENT email to Brian, not a
        # draft (Brian, 2026-09-13) — a flag for him to follow up manually,
        # separate from and in addition to the band-facing tier-3 follow-up
        # above. Includes a band with no email on file (the tier-3 follow-up
        # above skips those); one email listing every band that just crossed
        # the mark this run, not one email per band.
        unresponded_sent = 0
        if due_unresponded:
            with advance_db.get_conn() as conn, conn.cursor() as cur:
                rows = [(r["artist_name"], r["venue"] or "", us_date(r["show_date"]))
                        for r in due_unresponded]
                for r in due_unresponded:
                    advance_db.mark_unresponded_alert_sent(cur, r["show_id"])
                conn.commit()
            band_word = "band" if len(rows) == 1 else "bands"
            subject = f"Advance follow-up needed — {len(rows)} {band_word} unresponded at 3 days out"
            tr = "".join(
                f"<tr><td style=\"padding:4px 10px 4px 0;color:#6b7280;"
                f"font:13px -apple-system,sans-serif\">{n}</td>"
                f"<td style=\"padding:4px 0;font:13px -apple-system,sans-serif\">"
                f"<b>{v}</b> — {d}</td></tr>"
                for n, v, d in rows
            )
            html = (f"<div style=\"font-family:-apple-system,sans-serif\">"
                    f"<p>These bands are now inside the 3-day mark with no advance "
                    f"form on file — worth a manual follow-up:</p>"
                    f"<table>{tr}</table>"
                    f"<p style=\"margin-top:14px\">"
                    f"<a href=\"{PUBLIC_URL}/search\">Open the advance search →</a></p></div>")
            _send_internal_email(subject, html)
            unresponded_sent = len(rows)
    except Exception as e:
        _log_db_error("advance_lifecycle", e)
        return {"error": e.__class__.__name__}, 500

    return {"initial": initial, "followup": followup, "unresponded_alert_sent": unresponded_sent}


@app.post("/internal/run-recap-extraction")
def run_recap_extraction():
    """Called by n8n's daily 2am 'Advance Recap Extraction' check. For every
    show that finished at least 3 days ago and doesn't have one yet, converts
    its filed advance .docx to PDF + MD (next to the .docx in the Dropbox
    venue tree) and stores the parsed recap — see tools/extract_advance_recap.py
    for why this can't just live in events/event_acts. Token-protected, same
    as /internal/run-followups. Never touches anything band-facing directly;
    the stored recap is read later by draft_emails.py for a returning artist."""
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
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
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
    if not DB_OK:
        return {"error": "db-unavailable"}, 503
    sys.path.insert(0, str(TOOLS_DIR))
    from daily_digest import build_digest
    try:
        subject, html = build_digest()
    except Exception as e:
        _log_db_error("daily_digest", e)
        return {"error": e.__class__.__name__}, 500
    return {"subject": subject, "html": html, "to": "blloyd@3cdc.org"}


@app.post("/internal/crew-report")
def crew_report_endpoint():
    """Standalone, on-demand only (n8n's 'Crew Report' webhook — its daily
    cron trigger was removed 2026-09-09 now that Daily Digest carries
    today's crew every morning). Who's staffing every venue over the next
    14 days — Mix/Tech/Stagehand/Stage Support/Other, straight from the
    public 3CDC staffing sheet. Doesn't touch advance-db at all (pure
    staffing-sheet read), so no DB_OK gate. Token-protected, same as the
    other /internal endpoints."""
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
        abort(403)
    sys.path.insert(0, str(TOOLS_DIR))
    from crew_report import build_report
    try:
        html = build_report(days=14)
    except Exception as e:
        _log_db_error("crew_report", e)
        return {"error": e.__class__.__name__}, 500
    return {"subject": "3CDC Crew Report — Next 14 Days", "html": html, "to": "blloyd@3cdc.org"}


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
