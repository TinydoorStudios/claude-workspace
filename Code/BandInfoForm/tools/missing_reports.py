#!/usr/bin/env python3
"""Missing show reports — who was staffed in a report-owing role but never
submitted a show report (Brian, 2026-09-14: "alert me to anyone who doesn't
submit a report for their shift").

Split of labor, deliberately:
  - The ROSTER side (who owed a report) is read here from the same public
    3CDC staffing sheet the rest of the advance pipeline reads, via
    staffing.collect_days() — so every initial/nickname is already resolved
    to a real person through the codes tab. No new name-matching invented.
  - The SUBMISSIONS side (who actually reported) is PRIVATE (the Form
    responses sheet isn't public), so band-advance never reaches it. n8n,
    which already holds the Google Sheets OAuth credential, reads that sheet
    and hands the rows to build_missing() via /internal/missing-reports.

Report-owing roles per Brian: Mix (FOH + Mon), Tech Lead, Stagehand / Stage
Support. Cam-switch and "Other" don't owe a report. Brian himself is exempt.

Deadline rule (Brian): a report for a show on date D is due by NOON the next
day (D+1). Run at noon daily; a show is "due" once its D+1 noon has passed,
i.e. D <= yesterday. We look back over a trailing window and re-list anyone
still missing every day until they submit (chase-daily), so nothing slips.
"""
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import staffing as st
import crew_report as cr

# Roles that owe a report. mix is handled separately (foh/mon are single
# values, not a list); these are the list-valued roles pulled from an entry.
_REQUIRED_LIST_ROLES = ("tech", "stagehand", "stage_support")

# Person exempt from the rule (Brian). Compared against the canonical
# "First Last" the codes tab resolves — BL / Brian / BRIAN all land here.
_EXEMPT = {"brian lloyd"}

# Go-live floor (Brian, 2026-09-14: "start it from today"). Shows dated
# before this are never flagged — the backlog of pre-launch shifts is
# grandfathered, the check only chases shows from launch day forward. The
# system holds no per-person state, so this floor IS the "clear old flags":
# every run recomputes live, and anything before the floor simply drops out.
START_DATE = dt.date(2026, 9, 14)


def _venue_key(name):
    """Collapse a venue label from either side (staffing sheet or a report's
    Event Site) to one comparable key. Memo == Memorial Hall; the three
    venues that share one staffing block (Zeigler Park / Court Street Plaza /
    Imagination Alley) collapse together, because the sheet genuinely can't
    tell them apart and staffing.collect_days() reports them under one
    combined label."""
    n = (name or "").strip().lower()
    if not n:
        return ""
    if "memo" in n:
        return "memorial hall"
    if "fountain" in n:
        return "fountain square"
    if "washington" in n:
        return "washington park"
    if "elm" in n:
        return "elm street plaza"
    if any(k in n for k in ("zeigler", "ziegler", "court street", "imagination")):
        return "zp/cs/ia"
    return n


def _norm_name(name):
    return " ".join((name or "").strip().lower().split())


def _codes_by_email(codes_rows):
    """email(lower) -> canonical 'First Last', from the codes tab's Email
    column (col 5 in the Production Tech Staff block)."""
    out = {}
    for row in codes_rows[2:]:
        if len(row) < 6:
            continue
        email = (row[5] or "").strip().lower()
        name = f"{(row[1] or '').strip()} {(row[2] or '').strip()}".strip()
        if email and name:
            out[email] = name
    return out


def _canon_person(submitted_by, email, codes_rows, email_map):
    """A report's self-identified submitter -> canonical 'First Last'.
    Email is the strongest key (exact, unambiguous); fall back to resolving
    the typed name as a code / first name via the same codes tab the roster
    uses, then to a raw normalized 'first last'. Returns a lowercased key."""
    e = (email or "").strip().lower()
    if e and e in email_map:
        return _norm_name(email_map[e])
    tok = (submitted_by or "").strip()
    if tok:
        resolved = st._format_row(st._resolve_row(tok, codes_rows))
        if resolved:
            return _norm_name(resolved)
        # A full "First Last" the person typed that isn't a code — try to
        # match it against the codes tab's own first+last before giving up.
        low = _norm_name(tok)
        for row in codes_rows[2:]:
            if len(row) < 3:
                continue
            full = _norm_name(f"{row[1]} {row[2]}")
            if full and full == low:
                return full
        return low
    return ""


def build_missing(submissions, days=7, today=None):
    """submissions: list of {submitted_by, email, site, date} (date as
    YYYY-MM-DD or m/d/yy). Returns {count, items, text}.

    items: [{name, venue, event, date (ISO), roles:[...]}] for every
    report-owing person with no matching submission for their show's
    venue+date, over the trailing `days` window ending yesterday."""
    today = today or dt.date.today()
    end = today - dt.timedelta(days=1)          # yesterday: latest show now due
    start = end - dt.timedelta(days=max(0, days - 1))
    if start < START_DATE:                       # never look before go-live
        start = START_DATE
    if end < start:                              # whole window predates launch
        return {"count": 0, "items": [], "text": ""}

    codes_rows = st._fetch_csv(st.CODES_GID)
    schedule_rows = st._fetch_csv(st.SCHEDULE_GID)
    email_map = _codes_by_email(codes_rows)

    # ---- submitted set: (person_key, venue_key, iso_date) ----
    submitted = set()
    for s in submissions or []:
        d = st._parse_date(s.get("date")) or _iso(s.get("date"))
        if not d:
            continue
        person = _canon_person(s.get("submitted_by"), s.get("email"),
                               codes_rows, email_map)
        if not person:
            continue
        submitted.add((person, _venue_key(s.get("site")), d.isoformat()))

    # ---- expected set from the roster ----
    by_date = cr.collect_days(start, end, schedule_rows=schedule_rows,
                              codes_rows=codes_rows)
    # (person_key, venue_key, iso) -> {name, venue, event, date, roles}
    expected = {}
    for d, entries in by_date.items():
        iso = d.isoformat()
        for e in entries:
            vkey = _venue_key(e["venue"])
            people = []
            mix = e.get("mix") or {}
            if mix.get("foh"):
                people.append((mix["foh"], "Mix (FOH)"))
            if mix.get("mon"):
                people.append((mix["mon"], "Mix (Mon)"))
            seen_list = set()
            for role in _REQUIRED_LIST_ROLES:
                for nm in e.get(role) or []:
                    tag = (_norm_name(nm), role)
                    if tag in seen_list:      # merged stagehand/stage_support
                        continue
                    seen_list.add(tag)
                    label = "Stagehand" if role in ("stagehand", "stage_support") else "Tech Lead"
                    people.append((nm, label))
            for nm, role_label in people:
                pkey = _norm_name(nm)
                if not pkey or pkey in _EXEMPT:
                    continue
                k = (pkey, vkey, iso)
                if k not in expected:
                    expected[k] = {"name": nm, "venue": e["venue"],
                                   "event": e["event"], "date": iso,
                                   "roles": []}
                if role_label not in expected[k]["roles"]:
                    expected[k]["roles"].append(role_label)

    # ---- diff ----
    missing = [v for k, v in expected.items() if k not in submitted]
    missing.sort(key=lambda x: (x["date"], x["name"], x["venue"]), reverse=False)
    missing.sort(key=lambda x: x["date"], reverse=True)

    return {"count": len(missing), "items": missing,
            "text": _render(missing, today)}


def _iso(s):
    try:
        return dt.date.fromisoformat((s or "").strip())
    except Exception:
        return None


def _render(missing, today):
    if not missing:
        return ""
    stamp = today.strftime("%a %b %-d")
    lines = [f":rotating_light: *Missing show reports* — as of {stamp} noon",
             ""]
    for m in missing:
        d = dt.date.fromisoformat(m["date"]).strftime("%a %-m/%-d")
        roles = ", ".join(m["roles"])
        ev = f" — {m['event']}" if m["event"] and m["event"] != "(unnamed)" else ""
        lines.append(f"• *{m['name']}* — {m['venue']}{ev} ({d}) · {roles}")
    return "\n".join(lines)
