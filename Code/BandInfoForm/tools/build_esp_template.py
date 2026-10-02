#!/usr/bin/env python3
"""Build the Elm Street Plaza Prod Adv template from the universal one (Brian, 2026-10-01).

ESP's winter advance is basic: the summer Blues & Brews docs (one column, schedule, lead,
deliverables, audio, misc) minus everything a plaza date never uses. Rather than fork the
fill engine, ESP keeps the universal grid and header (so docmerge, provenance, recap
reading and the three artist columns all work unchanged) and drops the rows nobody fills
there: PA, Subs, the LIGHTING row + Stage Type + Lighting Notes, VIDEO, Dressing Room Tent.
Every fill routine looks rows up by label and skips a missing one, so nothing else changes.

    python3 build_esp_template.py          # writes doc_templates/ESP Show Advance.docx
"""
import sys
from pathlib import Path

from docx import Document

HERE = Path(__file__).resolve().parent
SRC = HERE / "doc_templates" / "3CDC Universal Show Advance.docx"
OUT = HERE / "doc_templates" / "ESP Show Advance.docx"
DROP_ROWS = {"pa", "subs", "lighting", "stage type", "lighting notes", "video", "dressing room tent"}


def norm(s):
    return " ".join((s or "").split()).lower().rstrip("?")


def build(out=OUT):
    doc = Document(str(SRC))
    sys.path.insert(0, str(HERE))
    import daysheet
    grid = daysheet.find_grid(doc)
    if grid is None:
        sys.exit("universal template has no EVENT INFORMATION grid")
    dropped = []
    for row in list(grid.rows):
        label = norm(row.cells[0].text)
        if label in DROP_ROWS:
            dropped.append(label)
            grid._tbl.remove(row._tr)
    missing = DROP_ROWS - set(dropped)
    if missing:
        sys.exit(f"rows not found in the universal template: {sorted(missing)}")
    doc.save(str(out))
    return dropped


if __name__ == "__main__":
    print("dropped:", ", ".join(build()))
    print("wrote", OUT)
