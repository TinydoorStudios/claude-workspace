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
GATE_PASS_2 = os.environ.get("ADVANCE_GATE_PASS_2", "1313")
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
# Signed artist id carried on the band form (audit #6) — a plain hidden
# artist_id could be edited to rename another artist / change their email.
_artist_signer = URLSafeSerializer(SECRET, salt="advance-artist-id")


def artist_token(artist_id):
    return _artist_signer.dumps(int(artist_id)) if artist_id else ""


def verify_artist_token(tok):
    try:
        return int(_artist_signer.loads(tok)) if tok else None
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
    if not f.get("band_name"):
        abort(400, "Band name is required.")

    # The band's own link carries a SIGNED artist id (audit #6). A raw
    # artist_id field is ignored — it could be edited to hijack another
    # artist's record.
    verified_artist_id = verify_artist_token(f.get("artist_token"))

    # Stage plot: upload OR description is required, not both (Brian,
    # 2026-09-08) — exempt only if this band already has one on file.
    upload = request.files.get("stage_plot_file")
    has_upload = bool(upload and upload.filename)
    has_desc = bool((f.get("stage_plot_desc") or "").strip())
    if not has_upload and not has_desc:
        has_existing = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    artist = advance_db.get_artist(cur, verified_artist_id) if verified_artist_id else None
                    if not artist:
                        artist = advance_db.find_artist_by_name(cur, f.get("band_name"))
                    if artist:
                        cur.execute("""SELECT 1 FROM submissions WHERE artist_id=%s
                                       AND COALESCE(data->>'stage_plot_file','') <> '' LIMIT 1""",
                                    (artist["id"],))
                        has_existing = cur.fetchone() is not None
            except Exception as e:
                _log_db_error("stage_plot_check", e)
        if not has_existing:
            abort(400, "Please provide a stage plot upload or a description — at least one is required.")

    # WP location monitor cap — hard limit (Brian, 2026-09-06)
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
    rec = {k: v for k, v in f.items() if k not in ("artist_id", "artist_token")}
    if verified_artist_id:
        rec["artist_id"] = str(verified_artist_id)
    if (rec.get("show_series") or "").strip().lower() == "default":
        rec["show_series"] = ""
    rec["_submitted_at"] = dt.datetime.now().isoformat(timespec="seconds")

    file_info = None
    if has_upload:
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
            result = advance_db.record_submission(rec, file_info=file_info, source="form")
            rec["_db"] = {"artist_id": result["artist_id"], "show_id": result["show_id"],
                          "submission_id": result["submission_id"]}
        except Exception as e:
            _log_db_error("record_submission", e)
            _alert_db_write_failure(rec, e)
    try:
        disk_path.write_text(json.dumps(rec, indent=2))
    except OSError as e:
        _log_db_error("disk_rewrite", e)

    # 4) Notify, best-effort
    _notify_submission(rec)
    _notify_email("submission", rec)
    if result and result.get("match"):
        _email_submission_match(result, rec)

    # 5) File ONLY this show's advance doc, in the background — blank cells
    #    only, never overwriting (audit #1). Uses the artist the submission
    #    actually landed on, which may be the booked name (audit #6).
    regen_rec = dict(rec)
    if result:
        regen_rec["band_name"] = result["artist_name"]
    _regen_submitted_show(regen_rec)

    submitted_lang = "es" if (f.get("form_lang") or "").strip().lower() == "es" else "en"
    return render_template("thanks.html", band=f.get("band_name"),
                            lang=submitted_lang, t=i18n.translator(submitted_lang))


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


def _send_outlook_email(to, subject, body=None, html=None, attachment=None, timeout=30, attachments=None):
    """(ok, error) — thin wrapper over mailer.send, the single send path
    (audit #3: a send only counts when n8n confirms Graph accepted it)."""
    return mailer.send(to, subject, body=body, html=html, attachment=attachment, timeout=timeout,
                       attachments=attachments)


def _send_internal_email(subject, html, to=None):
    return mailer.alert(subject, html, to=to)


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
            logf.write(f"\n--- {dt.datetime.now().isoformat(timespec='seconds')} ---\n")
            logf.flush()
            cmd = [sys.executable, "run_now.py"] + (["--scope", scope] if scope else [])
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
    try:
        subprocess.run([sys.executable, "run_now.py"] + (["--scope", scope] if scope else []),
                        cwd=TOOLS_DIR, capture_output=True, text=True, timeout=1200)
    except Exception as e:
        _log_db_error("late_booking_pipeline", e)
        return
    _trigger_immediate_advance()


# ── gated views (passcode) ──────────────────────────────────────────────────

GATED_PREFIXES = ("/staff", "/search", "/artist", "/file", "/submission", "/booking",
                  "/dashboard", "/show")

GATE_MAX_FAILS = 5
GATE_WINDOW_MIN = 15


@app.before_request
def _gate():
    p = request.path
    if p.startswith(GATED_PREFIXES) and not session.get("auth"):
        return redirect(url_for("gate", next=p))


def _client_ip():
    return (request.headers.get("CF-Connecting-IP")
            or (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
            or request.remote_addr or "unknown")


def _safe_next(nxt):
    """Only ever redirect to a page on this site (audit #13)."""
    if nxt and nxt.startswith("/") and not nxt.startswith("//") and "\\" not in nxt:
        return nxt
    return url_for("staff")


def _gate_locked(cur, ip):
    cur.execute("""SELECT locked_at FROM gate_lockouts
                   WHERE ip=%s AND locked_at > now() - (%s || ' minutes')::interval""",
                (ip, GATE_WINDOW_MIN))
    return cur.fetchone() is not None


@app.route("/gate", methods=["GET", "POST"])
def gate():
    """Staff passcode gate. Both standing passcodes stay valid; 5 wrong tries
    from one IP within 15 minutes locks that IP out for 15 minutes and emails
    Brian once (audit #13). Counts live in the database so every worker
    shares them. If the database is down the gate still works, unthrottled —
    never lock staff out over a DB outage."""
    ip = _client_ip()
    if request.method == "POST":
        locked = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    locked = _gate_locked(cur, ip)
            except Exception as e:
                _log_db_error("gate_check", e)
        if locked:
            return render_template("gate.html",
                                   error=f"Too many attempts — try again in {GATE_WINDOW_MIN} minutes."), 429
        ok = request.form.get("passcode") in VALID_GATE_PASSES
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    cur.execute("INSERT INTO gate_attempts (ip, ok) VALUES (%s,%s)", (ip, ok))
                    if not ok:
                        cur.execute("""SELECT count(*) AS n FROM gate_attempts
                                       WHERE ip=%s AND NOT ok
                                         AND attempted_at > now() - (%s || ' minutes')::interval
                                         AND attempted_at > COALESCE((SELECT locked_at FROM gate_lockouts
                                                                      WHERE ip=%s), '-infinity')""",
                                    (ip, GATE_WINDOW_MIN, ip))
                        if cur.fetchone()["n"] >= GATE_MAX_FAILS:
                            cur.execute("""INSERT INTO gate_lockouts (ip, locked_at, notified_at)
                                           VALUES (%s, now(), NULL)
                                           ON CONFLICT (ip) DO UPDATE SET locked_at=now(), notified_at=NULL""",
                                        (ip,))
                            locked = True
                    conn.commit()
                if locked:
                    sent, _ = mailer.alert(
                        "Advance staff login locked out — repeated wrong passcodes",
                        f"<p>{GATE_MAX_FAILS} wrong passcodes from IP <b>{mailer.esc(ip)}</b> within "
                        f"{GATE_WINDOW_MIN} minutes. That IP is locked out for {GATE_WINDOW_MIN} minutes.</p>")
                    if sent:
                        with advance_db.get_conn() as conn, conn.cursor() as cur:
                            cur.execute("UPDATE gate_lockouts SET notified_at=now() WHERE ip=%s", (ip,))
                            conn.commit()
            except Exception as e:
                _log_db_error("gate_record", e)
        if ok:
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
            # carried so the dashboard can offer Mark Finalized inline
            # (Brian, 2026-09-13: "I don't want to go searching for bands")
            # without a second round-trip to look them up.
            "artist_id": r["artist_id"], "show_id": r["show_id"],
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


BOOKING_SLOTS = ["headliner", "direct_support", "opener"]
# No-series choices (audit #16). The top Series pick decides internal vs 3rd
# party; the old Event Type field is gone from the form.
STANDALONE_SERIES = ["Stand-Alone Internal", "3rd Party"]


def _event_type_for_series(series):
    return "Third Party" if (series or "").strip().lower() == "3rd party" else "Internal"


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


def _booking_form(error=None, form=None, status=200):
    return render_template("booking.html", venues=forms_config.VENUES,
                           wp_locations=list(forms_config.WP_LOCATIONS),
                           slots=BOOKING_SLOTS, series_by_venue=_series_by_venue(),
                           standalone_series=STANDALONE_SERIES,
                           locked_schedule_series=_locked_schedule_series(),
                           error=error, form=form or {}), status


def _slot_taken(cur, venue, event_date, slot, artist_name, series=None):
    """Another band already holds this slot on this venue+date (audit #20).
    A 3rd-party event is its own bill (Brian, 2026-09-14): its slots never
    collide with the internal show's, and vice versa."""
    third = advance_db.is_third_party(series)
    cur.execute(
        r"""SELECT b.artist_name FROM bookings b
            LEFT JOIN artists a ON a.match_key = lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g')))
            LEFT JOIN shows s ON s.artist_id = a.id AND s.venue = b.venue AND s.show_date = b.event_date
            WHERE b.venue=%s AND b.event_date=%s AND b.slot=%s
              AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) <> %s
              AND s.cancelled_at IS NULL
              AND (lower(btrim(COALESCE(b.series,''))) = '3rd party') = %s
            LIMIT 1""",
        (venue, event_date, slot, advance_db.normalize(artist_name), third))
    row = cur.fetchone()
    return row["artist_name"] if row else None


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
      #20 a slot already held by another band that night is refused; a
          multi-band night has no default slot"""
    if request.method == "POST":
        f = request.form
        data = {k: (f.get(k) or "").strip() for k in advance_db.BOOKING_FIELDS}
        data["skip_welcome_email"] = f.get("skip_welcome_email") == "on"
        if not data["entered_by"]:
            return _booking_form("Who's entering this is required.", f, 400)
        if not data["venue"] or not advance_db.to_date(data["event_date"]):
            return _booking_form("Venue and a valid event date are required.", f, 400)
        if not data["series"] or data["series"].lower() == "default":
            return _booking_form("Pick a series — or Stand-Alone Internal / 3rd Party.", f, 400)
        # Brian, 2026-09-14: on a 3rd-party event the artist/band is optional
        # too. The booking row still needs a name (it's the upsert key and the
        # sheet/artist match), so a blank one takes the event name.
        if not data["artist_name"]:
            if not advance_db.is_third_party(data["series"]):
                return _booking_form("Artist name is required.", f, 400)
            data["artist_name"] = data["event_name"] or "3rd Party Event"
        # Brian, 2026-09-14: a 3rd-party event usually comes with no band
        # contact at all — name, email and phone are optional for it. No
        # email simply means no welcome / reminders / day-before for that show.
        if (not data["skip_welcome_email"] and "@" not in data["contact_email"]
                and not advance_db.is_third_party(data["series"])):
            return _booking_form("Contact email is required (or check Manual band advance).", f, 400)
        if data["band_count"] not in ("", "1") and not data["slot"]:
            return _booking_form("Pick a slot — this night has more than one band.", f, 400)
        if not data["slot"]:
            data["slot"] = "headliner"
        data["event_type"] = _event_type_for_series(data["series"])
        saved = False
        if DB_OK:
            try:
                with advance_db.get_conn() as conn, conn.cursor() as cur:
                    taken = _slot_taken(cur, data["venue"], advance_db.to_date(data["event_date"]),
                                        data["slot"], data["artist_name"], series=data["series"])
                    if taken:
                        slot_h = data["slot"].replace("_", " ")
                        return _booking_form(
                            f"{taken} is already the {slot_h} on {data['event_date']} — pick another slot.",
                            f, 409)
                    advance_db.insert_booking(cur, data)
                    conn.commit()
                saved = True
            except Exception as e:
                _log_db_error("insert_booking", e)
        if not saved:
            return _booking_form("Couldn't save — the database is unreachable. Try again shortly.", f, 503)
        _notify_email("booking", data)
        show_date = advance_db.to_date(data.get("event_date"))
        days_out = (show_date - dt.date.today()).days if show_date else None
        urgent = days_out is not None and 0 <= days_out <= 21
        scope = f"{data['venue']}|{show_date.isoformat()}" if show_date else None
        if urgent:
            threading.Thread(target=_run_pipeline_then_trigger_now, args=(scope,), daemon=True).start()
        else:
            _run_pipeline_background(scope)
        fill_link = _manual_fill_link(data) if data["skip_welcome_email"] else None
        return render_template("booking.html", venues=forms_config.VENUES,
                               slots=BOOKING_SLOTS, saved=data, urgent=urgent,
                               fill_link=fill_link)
    return _booking_form(form={})[0]


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
        shows = advance_db.artist_shows(cur, artist_id)
        subs = advance_db.artist_submissions(cur, artist_id)
        files_by_sub = {s["id"]: advance_db.submission_files(cur, s["id"]) for s in subs}
    return render_template("artist.html", artist=artist, shows=shows,
                           subs=subs, files_by_sub=files_by_sub,
                           state_labels=DASHBOARD_STATE_LABELS)


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
        try:
            import urllib.request
            req = urllib.request.Request(
                CREATE_DRAFT_URL, data=json.dumps({"to": to, "subject": subject, "body": body}).encode(),
                headers={"Content-Type": "application/json", "X-Advance-Token": INTERNAL_TOKEN})
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = json.loads(resp.read().decode("utf-8", "replace") or "{}")
            if isinstance(raw, list):
                raw = raw[0] if raw else {}
            gbody = raw.get("body") if isinstance(raw, dict) else None
            status = raw.get("statusCode") if isinstance(raw, dict) else None
            if status in (200, 201) and isinstance(gbody, dict) and gbody.get("id"):
                result.update(ok=True, link=gbody.get("webLink"), to=to)
            else:
                result["error"] = f"draft not created (HTTP {status}): {str(gbody)[:200]}"
        except Exception as e:  # noqa: BLE001
            result["error"] = repr(e)[:200]
            _log_db_error("draft_reply", e)
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
    return _back(url_for("artist_detail", artist_id=s["artist_id"]))


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
        advance_db.merge_shows(cur, show_id, target_id)
        advance_db.release_candidate_holds(cur, show_id)
        conn.commit()
    return redirect(url_for("artist_detail", artist_id=tgt["artist_id"]))


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


LIFECYCLE_LOCK_KEY = 874201913


def _internal_auth():
    if not INTERNAL_TOKEN or request.headers.get("X-Advance-Token") != INTERNAL_TOKEN:
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

    lock_conn = advance_db.get_conn()
    lock_conn.autocommit = True
    initial, followup, failures, dayahead = [], [], 0, []
    drafts_dir = None
    try:
        lock_conn.execute("SELECT pg_advisory_lock(%s)", (LIFECYCLE_LOCK_KEY,))
        with advance_db.get_conn() as conn, conn.cursor() as cur:
            advance_db.record_job_run(cur, "advance-lifecycle", source)
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
                "slot": r["slot"] or "", "set_time": r["set_time"] or "",
                "email_note": r["email_note"] or "",
                "band_count": str(r["band_count"]) if r["band_count"] else "",
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
            try:
                subprocess.run([sys.executable, "draft_emails.py", str(batch_file),
                                "--out", str(drafts_dir)],
                               cwd=TOOLS_DIR, capture_output=True, text=True,
                               timeout=180, check=True)
            except Exception as e:
                rendered = False
                _log_db_error("lifecycle_draft_render", e)
            finally:
                batch_file.unlink(missing_ok=True)

            from draft_emails import slug as _dslug
            seen_shows = set()
            for r in due_initial:
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
                    fail(r["show_id"], "welcome", "welcome email didn't render")
                    continue
                text = hits[0].read_text()
                subj_line, _, body = text.partition("\n")
                subject = subj_line.removeprefix("Subject:").strip()
                ok, err = _send_outlook_email(r["email"], subject, body=body.lstrip("\n"),
                                              attachments=ve.venue_attachments(r["venue"]))
                if not ok:
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
            # Review 2026-09-14 (M2): a bilingual series (Salsa) gets the
            # Spanish half under the English one, same shape as its welcome.
            if r["series"] and ve.is_bilingual_series(r["series"]):
                greeting_es = (f"Hola {r['contact_name']} y {r['artist_name']}"
                               if r["contact_name"] else f"Hola {r['artist_name']}")
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
            ok, err = _send_outlook_email(r["email"], subject, body=body,
                                          attachments=ve.venue_attachments(r["venue"]))
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
        try:
            from dayahead import send_due as _dayahead_send_due
            dayahead = _dayahead_send_due(fail)
        except Exception as e:  # noqa: BLE001 — never blocks the rest of the run
            _log_db_error("dayahead", e)
            dayahead = []

        _email_send_failures()
    except Exception as e:
        _log_db_error("advance_lifecycle", e)
        return {"error": e.__class__.__name__, "initial": initial, "followup": followup}, 500
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
    _internal_auth()
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
