#!/usr/bin/env python3
"""Write queued follow-up drafts (from the n8n daily check) to .md files so they
surface in your workspace like the other drafts."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "followups")
OUT.mkdir(exist_ok=True)


def main():
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, band, contact_email, subject, body, sent_at "
            "FROM followup_queue ORDER BY id"
        )
        rows = cur.fetchall()
    for r in rows:
        if r.get("sent_at"):
            continue  # already sent
        slug = re.sub(r"[^a-z0-9]+", "-", (r["band"] or "band").lower()).strip("-")
        (OUT / f"{slug}__followup.md").write_text(
            f"To: {r['contact_email'] or ''}\n{r['subject']}\n\n{r['body']}\n"
        )
    pending = sum(1 for r in rows if not r.get("sent_at"))
    print(f"{pending} pending follow-up draft(s) -> {OUT}")


if __name__ == "__main__":
    main()
