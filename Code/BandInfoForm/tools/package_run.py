#!/usr/bin/env python3
"""Build the advance filing tree from the advance list spreadsheet.

Rebuilds events+acts from the sheet (form submissions are never touched),
then:

  - files each event's advance doc + stage plots IN PLACE in the real venue
    folder, ~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/ — created once,
    after that only blank cells are ever filled (tools/docmerge.py; 2026-09-13
    audit #1). A value that differs from what the doc already says is left
    alone and emailed to Brian as a notice. Past shows are never touched.
    --scope "Venue|YYYY-MM-DD" limits filing to one show (a booking's run).
  - writes internal email drafts under --out/drafts/<VenueAbbr>/<Year>/
    <MM Month>/Email Drafts/ (run_now.py overlays those onto Nyquist/)
  - writes --out/status.json for the sheet's STATUS block

Nothing here sends band email.

  python3 package_run.py ~/Dropbox/Nyquist/advance-list.xlsx --out _package [--scope "Fountain Square|2026-09-18"]
"""
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import daysheet
import docmerge
import fieldspec as fs
import holds
from draft_emails import slug  # same slug the drafts are named with

PY = sys.executable
DRAFTS = HERE / "drafts"
FOLLOWUPS = HERE / "followups"
UPLOADS = HERE.parent / "data" / "uploads"      # where the form stores stage plots


def run(*args):
    subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, check=True)


def safe(s):
    """Filesystem-safe, human-readable — keep spaces, drop path-hostile chars."""
    s = re.sub(r"[/\\:*?\"<>|]+", "-", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)


def event_dir(ev):
    """~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/ — where this event's
    advance doc + stage plot live, written in place (never via an overlay)."""
    venue = ev.get("venue")
    real_folder = fs.real_venue_folder(venue)
    d = ev.get("event_date")
    root = fs.real_dropbox_root()
    if d:
        return root / real_folder / fs.real_month_folder(venue, d)
    return root / real_folder / "No Date"


def event_drafts_dir(out, ev):
    """<out>/drafts/<VenueAbbr>/<Year>/<MM Month>/Email Drafts/ — internal
    working drafts, stays on the Nyquist-cockpit scheme, never the real folder."""
    venue = fs.venue_abbr(ev.get("venue"))
    d = ev.get("event_date")
    base = (out / "drafts" / safe(venue) / str(d.year) / fs.month_folder(d)
            if d else out / "drafts" / safe(venue) / "No Date")
    return base / fs.EMAIL_DRAFTS_DIR


def event_stem(ev, acts):
    d = ev.get("event_date")
    # Name + headliner — single source of truth in fieldspec.py, shared with
    # regen_show.py's single-show path so both never drift apart on what an
    # event's filename looks like. See fieldspec.event_display_name /
    # top_of_bill_name for the actual rule. Cancelled (review 2026-09-14,
    # M4): every act on the bill is cancelled -> the same file is renamed in
    # place with a CANCELLED marker after the date stamp; undo-cancel renames
    # it back on the next run. 2026-09-21 sweep (DAY-6): a cancelled headliner
    # on a live bill no longer names the file — docmerge.filing_display_name.
    name = docmerge.filing_display_name(ev, acts)
    if d:
        return fs.advance_stem(name, d)
    return f"{safe(name)} Prod Adv"


def find_one(folder, pattern):
    hits = sorted(folder.glob(pattern))
    return hits[0] if hits else None


def report_filing_error(ev, stem, what, err):
    """2026-09-21 sweep (PIPE-7): a per-event filing failure reaches Brian's
    digest instead of only this run's stderr. Keyed per show/field/exception
    type/day, so a standing failure is reported once a day. Never raises."""
    try:
        import mailer
        d = ev.get("event_date")
        venue = ev.get("venue") or ""
        msg = f"{type(err).__name__}: {err}"[:500]
        with db.get_conn() as conn, conn.cursor() as cur:
            nid = db.insert_doc_notice(cur, venue, d, docmerge.event_key(ev), "filing_error", what,
                                       f"{dt.date.today().isoformat()} {type(err).__name__}", msg,
                                       detail=f"{stem}.docx")
            if nid:
                # informational, like run_now's conflicted-copy notice: closed at
                # once and marked notified so it rides only this digest item
                db.resolve_doc_notice(cur, nid, "auto")
                db.mark_doc_notices_notified(cur, [nid])
                db.queue_digest_item(
                    cur, "doc", f"{what} could not be filed — {stem}",
                    f"<p><b>{mailer.esc(what)}</b> for <b>{mailer.esc(stem)}</b> "
                    f"({mailer.esc(venue)}, {mailer.esc(d.isoformat() if d else '')}) "
                    "could not be filed, so that show's doc isn't being updated. "
                    "Every run retries it.</p>"
                    f"<pre style='white-space:pre-wrap'>{mailer.esc(msg)}</pre>")
            conn.commit()
    except Exception as e2:  # noqa: BLE001 — a report, never a reason to fail the run
        print(f"  ! could not record filing error for '{stem}': {e2!r}", file=sys.stderr)


def _scope_set(values):
    """--scope "Venue|YYYY-MM-DD" (repeatable) -> {(venue, date)}; empty = every event."""
    out = set()
    for v in values or []:
        venue, _, date = v.partition("|")
        if venue and date:
            out.add((venue.strip(), date.strip()[:10]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--out", default="_package")
    ap.add_argument("--scope", action="append",
                    help='only file docs for this show: "Venue|YYYY-MM-DD" (repeatable)')
    ap.add_argument("--no-mail", action="store_true",
                    help="never email (doc-change notices are still recorded)")
    ap.add_argument("--dry-run-docs", action="store_true",
                    help="report what filing would do; write no doc/plot and record nothing")
    args = ap.parse_args()
    scope = _scope_set(args.scope)

    out = (HERE / args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # 1. rebuild the event/act model from the sheet (submissions untouched).
    # The truncate lives inside import_sheet.py's own transaction now (audit
    # 2026-09-16 #18) — it reads and validates the sheet FIRST and never
    # wipes events/event_acts on a sheet it couldn't read.
    run("import_sheet.py", args.sheet)

    # 2. regenerate the flat draft artifacts into their working dirs
    for d in (DRAFTS, daysheet.FILLED):
        if d.exists():
            for f in d.glob("*"):
                if f.is_file():
                    f.unlink()
    run("draft_emails.py", args.sheet)
    run("status_sheet.py", "--json", str(out / "status.json"))

    # 3. file each event's advance doc IN PLACE in the real venue folder —
    #    created once, then only blank cells ever filled (docmerge.py). No
    #    staging tree + rsync overlay any more: that overlay is what used to
    #    overwrite every filed doc on every run (2026-09-13 audit #1).
    n_events = n_emails = n_followups = n_plots = n_failed = 0
    plot_rels = {}   # (band, venue, date) -> relative path to the filed stage plot
    results = []
    today = dt.date.today()
    with db.get_conn() as conn, conn.cursor() as cur:
        events = db.list_events(cur)
        per_day = {}
        for e in events:
            k = (e.get("venue"), e.get("event_date"))
            per_day[k] = per_day.get(k, 0) + 1
        loaded = [(e["id"], db.get_event(cur, e["id"]), db.event_acts(cur, e["id"])) for e in events]

    for eid, ev, acts in loaded:
        n_events += 1
        d = ev.get("event_date")
        venue = ev.get("venue")
        in_scope = (not scope) or ((venue, d.isoformat() if d else "") in scope)
        folder = event_dir(ev)
        stem = event_stem(ev, acts)
        future = bool(d) and d >= today

        stageplot_names = {}
        plot_notices = []
        for a in acts:
            stored = ((a.get("submission") or {}).get("data") or {}).get("stage_plot_file")
            if not stored or not d:
                continue
            band = a["artist"]["name"] if a.get("artist") else "band"
            fname = f"{fs.stageplot_stem(band, d)}{Path(stored).suffix}"
            src = UPLOADS / stored
            plot_ok = False
            if in_scope and future:
                if not src.exists():
                    print(f"  ! stage plot file missing on server: {stored}")
                else:
                    # 2026-09-21 sweep (PIPE-7): one plot's OSError (Dropbox perms,
                    # disk full) used to abort the whole run — every later event too.
                    try:
                        fname, notice = docmerge.file_stage_plot(src, folder, fname,
                                                                  dry_run=args.dry_run_docs)
                        if notice:
                            plot_notices.append(notice)
                        n_plots += 1
                        plot_ok = True
                    except Exception as e:  # noqa: BLE001
                        n_failed += 1
                        print(f"  ! stage plot failed for {band} on '{stem}': {e!r}", file=sys.stderr)
                        if not args.dry_run_docs:
                            report_filing_error(ev, stem, f"Stage plot — {band}", e)
            try:
                on_disk = (folder / fname).exists()
            except OSError:
                on_disk = False
            if on_disk or plot_ok:
                stageplot_names[band] = fname
                rel = (Path("..") / fs.real_venue_folder(venue) /
                       fs.real_month_folder(venue, d) / fname).as_posix()
                plot_rels[(band.strip().lower(), (venue or "").strip().lower(),
                           d.isoformat())] = rel

        if in_scope and future:
            try:
                res = docmerge.file_event_doc(
                    eid, ev, acts, stem, stageplot_names=stageplot_names, today=today,
                    dry_run=args.dry_run_docs,
                    n_events_same_day=per_day.get((venue, d), 1))
                res["notices"] = (res.get("notices") or []) + plot_notices
                results.append((ev, res))
                print(f"  doc {res['action']:9} {Path(res.get('path') or '').name}"
                      + (f"  (renamed from {res['renamed_from']})" if res.get("renamed_from") else "")
                      + (f"  filled {res['filled']}" if res.get("filled") else "")
                      + (f"  {len(res['notices'])} notice(s)" if res.get("notices") else "")
                      + ("  [hand-edited]" if res.get("hand_edited") else ""))
                if res["action"] in ("locked", "conflict"):
                    n_failed += 1
            except (Exception, SystemExit) as e:
                # one event failing (missing template, unreadable doc) never
                # takes down every other event in the run (2026-09-10)
                n_failed += 1
                print(f"  ! day-sheet failed for '{stem}' ({venue}): {e!r}", file=sys.stderr)
                if not args.dry_run_docs:   # 2026-09-21 sweep (PIPE-7): tell Brian, not just the log
                    report_filing_error(ev, stem, "Advance doc", e)

        date = d.isoformat() if d else None
        drafts_dir = event_drafts_dir(out, ev)
        for a in acts:
            if not a.get("artist"):
                continue
            name = a["artist"]["name"]
            sg = slug(name)
            # 2026-09-21 sweep (MAIL-2): drafts carry the venue now — never copy the
            # band's other-venue draft (or, undated, any dated one) into this event.
            draft = find_one(DRAFTS, f"{sg}__{date or 'nodate'}__{slug(venue)}__*.md")
            if draft:
                drafts_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(draft, drafts_dir / f"{stem} email - {safe(name)}.md")
                n_emails += 1

    if results and not args.dry_run_docs:
        # audit 2026-09-16 #18: the actual doc filing above already
        # succeeded by this point — a failure just recording/emailing the
        # change notices must not lose that work or crash the run before it
        # prints its summary.
        try:
            new_notices = docmerge.record_and_email_notices(results, send_mail=not args.no_mail)
            if new_notices:
                print(f"  {new_notices} new doc-change notice(s) recorded")
        except Exception as e:  # noqa: BLE001
            print(f"  ! record_and_email_notices failed (non-fatal): {e!r}", file=sys.stderr)

    # 3b. any current show no longer in the sheet goes ON HOLD — no sends —
    #     until Brian cancels / restores / merges it (audit #4)
    try:
        holds.run(args.sheet, send_mail=not args.no_mail, dry_run=args.dry_run_docs)
    except Exception as e:  # noqa: BLE001 — never blocks filing
        print(f"  ! holds check failed: {e!r}", file=sys.stderr)

    # 4. tell the status merge where each filed stage plot landed (for the sheet link)
    status_path = out / "status.json"
    if plot_rels and status_path.exists():
        recs = json.loads(status_path.read_text())
        for r in recs:
            key = ((r.get("band") or "").strip().lower(),
                   (r.get("venue") or "").strip().lower(),
                   (r.get("date") or "")[:10])
            if key in plot_rels:
                r["stageplot_rel"] = plot_rels[key]
        status_path.write_text(json.dumps(recs, indent=2, default=str))

    print(f"\nPackage built at {out}")
    print(f"  {n_events} event(s) filed · {n_emails} email(s) · "
          f"{n_followups} follow-up(s) · {n_plots} stage plot(s) · "
          f"{n_failed} day-sheet failure(s)")


if __name__ == "__main__":
    main()
