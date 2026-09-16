#!/usr/bin/env python3
"""One send path for every email this system produces — band-facing sends
and Brian's internal alerts alike — so the confirm/kill-switch rules below
live in exactly one place (2026-09-13 audit, items 3/5).

Posts to n8n's "Internal Send — Outlook" webhook. A send counts as sent ONLY
when that webhook answers 2xx AND its JSON body does not say `"sent": false`.
The workflow's own "Confirm Sent" node throws when Graph returns anything but
202, which makes n8n answer 500 — so a Graph rejection (expired secret,
throttling, bad address) comes back here as a failure instead of a silent
200. A 2xx body without a `sent` key (an older workflow version) is treated
as sent, never as failed, so a contract mismatch can never cause a retry
loop that re-emails a band.

Kill switch: ADVANCE_MAIL_DISABLED=1 makes every call a logged no-op that
returns False (nothing is stamped as sent). Used for any manual run on the
live box. ADVANCE_STAGING=1 refuses to post anywhere except 127.0.0.1:8199
(the staging capture stub), so a staging process can never reach n8n.
"""
import datetime as dt
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "data" / "mail.log"

ALERT_TO = os.environ.get("ADVANCE_UNRESPONDED_ALERT_TO", "blloyd@3cdc.org")


def _send_url():
    return os.environ.get("ADVANCE_INTERNAL_SEND_URL",
                          "http://localhost:5678/webhook/internal-send-outlook")


def _log(line):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as fh:
            fh.write(f"{dt.datetime.now().isoformat(timespec='seconds')}  {line}\n")
    except OSError:
        pass


def send(to, subject, body=None, html=None, attachment=None, timeout=90, attachments=None):
    """(ok, error). ok=True only on a confirmed send. Never raises.
    `attachment` is one (name, type, base64) tuple; `attachments` a list of
    them (review 2026-09-14, E4: a venue can attach a load-in doc AND a tech
    pack). Both are accepted and combined."""
    if os.environ.get("ADVANCE_MAIL_DISABLED") == "1":
        _log(f"SUPPRESSED (kill switch) to={to!r} subject={subject!r}")
        return False, "mail disabled"
    url = _send_url()
    if os.environ.get("ADVANCE_STAGING") == "1" and not url.startswith("http://127.0.0.1:8199"):
        _log(f"REFUSED (staging, non-stub url {url}) to={to!r} subject={subject!r}")
        return False, "staging refuses non-stub url"
    content = html if html else (body or "")
    if not str(content).strip():
        _log(f"BLOCKED empty body to={to!r} subject={subject!r}")
        return False, "empty body"
    payload = {"to": to, "subject": subject}
    if html:
        payload["html"] = html
    else:
        payload["body"] = body or ""
    all_att = ([attachment] if attachment else []) + list(attachments or [])
    if all_att:
        payload["attachment_name"], payload["attachment_type"], payload["attachment_content"] = all_att[0]
        if len(all_att) > 1:
            payload["attachments"] = [{"name": n, "type": t, "content": c} for n, t, c in all_att[1:]]
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "X-Advance-Token": os.environ.get("ADVANCE_INTERNAL_TOKEN", "")},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        err = f"HTTP {e.code}"
        try:
            err += ": " + e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        _log(f"FAILED to={to!r} subject={subject!r} {err}")
        return False, err
    except (TimeoutError, urllib.error.URLError) as e:
        # A timeout means we never learned whether Graph actually sent it
        # (audit 2026-09-16 #17) — distinct from a definite failure, so the
        # caller can avoid an automatic retry that would double-send if the
        # original really did go through. urllib wraps a socket timeout in
        # URLError; TimeoutError catches urlopen's own timeout directly.
        if isinstance(e, urllib.error.URLError) and not isinstance(e.reason, TimeoutError):
            _log(f"FAILED to={to!r} subject={subject!r} {e!r}")
            return False, repr(e)
        _log(f"TIMEOUT (unknown outcome) to={to!r} subject={subject!r} {e!r}")
        return False, f"TIMEOUT: {e!r}"
    except Exception as e:  # noqa: BLE001
        _log(f"FAILED to={to!r} subject={subject!r} {e!r}")
        return False, repr(e)
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        data = {}
    if isinstance(data, list):
        data = data[0] if data else {}
    if isinstance(data, dict) and data.get("sent") is False:
        err = f"workflow reported not sent: {str(data)[:300]}"
        _log(f"FAILED to={to!r} subject={subject!r} {err}")
        return False, err
    _log(f"SENT to={to!r} subject={subject!r}")
    return True, None


def alert(subject, html, to=None):
    """Brian's internal alert. (ok, error)."""
    return send(to or ALERT_TO, subject, html=html)


def esc(s):
    import html as _h
    return _h.escape("" if s is None else str(s))
