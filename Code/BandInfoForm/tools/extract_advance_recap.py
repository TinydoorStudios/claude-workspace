#!/usr/bin/env python3
"""Nightly (2am via n8n's "Advance Recap Extraction" workflow) recap capture.

GRACE_DAYS after a show, its filed advance .docx has had time to be corrected —
this converts it to PDF + MD (saved into the SAME venue/month folder as the
.docx, in the Dropbox tree) and stores the parsed recap in the DB. Currently
1 day (next-day, temporary per Brian 2026-09-07, while there's only a
handful of real runs to watch) — the original design was 3 days.

Why the DB write matters, not just the files: package_run.py TRUNCATEs and
rebuilds `events`/`event_acts` from the live sheet on every run — that's a
working model, not a history. Once a show scrolls off the sheet, its event
name and any staff overrides typed into the spreadsheet have no other durable
home. Reading the filed .docx directly (daysheet.read_filed_advance) still
works without events/event_acts (it locates the artist's column by matching
text inside the document, not by DB lookup), but doing that on-demand, months
later, at the moment some future show happens to need it, means depending on
the old file still being exactly where it was filed. Extracting early and
storing the result in `advance_recaps` fixes both problems at once.

Idempotent — UNIQUE(show_id) means re-running only touches shows that don't
already have a recap. A show whose advance was never filed (no submission,
cancelled, etc.) is skipped and retried on subsequent runs, bounded by
due_for_recap_extraction's lookback window so it doesn't retry forever.

Usage (also what the /internal/run-recap-extraction endpoint calls):
  python3 extract_advance_recap.py
"""
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
import daysheet as ds

# Brian's call 2026-09-07, temporary "for the time being": next day, not 3
# days out — shorten back once there's been enough real runs to trust it.
GRACE_DAYS = 1


def docx_to_pdf(docx_path, out_dir, timeout=120):
    """soffice --headless --convert-to pdf — needs LibreOffice on this box
    (apt install libreoffice-writer is the light option on the n8n VM)."""
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path)],
        check=True, capture_output=True, timeout=timeout,
    )
    pdf_path = out_dir / (docx_path.stem + ".pdf")
    if not pdf_path.exists():
        raise RuntimeError(f"soffice reported success but {pdf_path.name} wasn't written")
    return pdf_path


def rows_to_md(artist_name, venue, show_date, rows, source_docx):
    lines = [
        f"# {artist_name} — {venue} ({show_date.strftime('%m/%d/%Y')})",
        "",
        f"_Extracted from `{source_docx.name}` {GRACE_DAYS} days after the show._",
        "",
    ]
    for label, text in rows:
        lines.append(f"- **{label}:** {text}")
    return "\n".join(lines) + "\n"


def relative_to_root(path):
    try:
        return str(path.relative_to(ds.NYQUIST_DEFAULT))
    except ValueError:
        return str(path)  # root override in use (e.g. tests) — store the absolute path


def _safe(s):
    import re
    return re.sub(r"[^A-Za-z0-9]+", " ", str(s or "")).strip()


def run():
    extracted, skipped, pdf_failed = 0, 0, 0
    with db.get_conn() as conn, conn.cursor() as cur:
        due = db.due_for_recap_extraction(cur, grace_days=GRACE_DAYS)
        for show in due:
            found = ds.read_filed_advance(show["venue"], show["show_date"], show["artist_name"])
            if not found:
                print(f"  ! no filed advance found for {show['artist_name']} @ "
                      f"{show['venue']} {show['show_date']} — will retry")
                skipped += 1
                continue

            docx_path, rows = found
            folder = docx_path.parent
            # per-artist MD, always — a multi-band bill shares one .docx across
            # several shows, and md_path.stem alone would let the second act's
            # write clobber the first's (caught testing a real 2-band bill).
            # The PDF is the whole document either way, so it stays shared —
            # skip re-converting once one act on this bill has already made it.
            md_path = folder / f"{docx_path.stem} - {_safe(show['artist_name'])}.md"
            md_path.write_text(rows_to_md(show["artist_name"], show["venue"],
                                           show["show_date"], rows, docx_path))

            pdf_path = folder / f"{docx_path.stem}.pdf"
            if pdf_path.exists():
                print(f"  (pdf already filed for this bill: {pdf_path.name})")
            else:
                try:
                    pdf_path = docx_to_pdf(docx_path, folder)
                except Exception as e:  # noqa: BLE001 — PDF is nice-to-have, MD+DB is the point
                    print(f"  ! PDF conversion failed for {docx_path.name}: {e!r}")
                    pdf_failed += 1
                    pdf_path = None

            db.record_advance_recap(
                cur, show["show_id"], show["artist_id"], show["venue"], show["show_date"],
                source_docx=docx_path.name,
                md_path=relative_to_root(md_path),
                pdf_path=relative_to_root(pdf_path) if pdf_path else None,
                recap=rows,
            )
            conn.commit()
            extracted += 1
            print(f"  extracted: {show['artist_name']} @ {show['venue']} {show['show_date']} "
                  f"-> {md_path.name}" + ("" if pdf_path else " (no PDF)"))

    print(f"\n{extracted} recap(s) extracted, {skipped} not found yet, "
          f"{pdf_failed} PDF conversion failure(s).")
    return {"extracted": extracted, "skipped": skipped, "pdf_failed": pdf_failed}


if __name__ == "__main__":
    run()
