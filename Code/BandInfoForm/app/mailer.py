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


def send(to, subject, body=None, html=None, attachment=None, timeout=30):
    """(ok, error). ok=True only on a confirmed send. Never raises."""
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
    if attachment:
        payload["attachment_name"], payload["attachment_type"], payload["attachment_content"] = attachment
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
