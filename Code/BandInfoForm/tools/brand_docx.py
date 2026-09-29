#!/usr/bin/env python3
"""3CDC brand pass for the Prod Adv .docx (brand rollout phase 4, 2026-09-29).

Two jobs:

  restyle(src, dst)        one-off, reproducible: turns the universal template
                           into the branded one. Avenir Next body, Avenir Next
                           Condensed labels, charcoal text, charcoal section
                           bars, gray rules, 3CDC logo in the page header.
                           Style only — no cell text changes, so docmerge's
                           blank-template comparisons (text-based) are
                           unaffected.
  add_venue_logo(doc, v)   at doc creation (daysheet.build): puts the venue's
                           wordmark at the right end of the header. The
                           template is shared by every venue, so the venue
                           mark can't live in it.

Colors and logo files come from app/brand/brand.json via app/brand.py.

    python3 brand_docx.py restyle "doc_templates/3CDC Universal Show Advance.docx" out.docx
"""
import copy
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent / "app", HERE.parent):
    if (_c / "brand.py").exists():
        sys.path.insert(0, str(_c))
        break
import brand  # noqa: E402

BODY = "Avenir Next"
LABEL = "Avenir Next Condensed"
RULE = "9D9FA2"        # corporate gray, table rules
BAR = "595A5C"         # corporate charcoal, section bars + text
PANEL = "EEEEEF"       # neutral panel behind the EVENT INFORMATION values
SECTION_LABELS = {"EVENT INFORMATION", "AUDIO", "MISC"}
LOGO_H = Inches(0.30)
LINE = 204            # 240 = single spacing


def _hex(c):
    return c.lstrip("#").upper()


def _set_fonts(rpr, name):
    f = rpr.find(qn("w:rFonts"))
    if f is None:
        f = OxmlElement("w:rFonts")
        rpr.insert(0, f)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        f.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if f.get(qn(a)) is not None:
            del f.attrib[qn(a)]


def _rpr(r):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        r.insert(0, rpr)
    return rpr


def _set_color(rpr, hexc):
    c = rpr.find(qn("w:color"))
    if c is None:
        c = OxmlElement("w:color")
        rpr.append(c)
    c.set(qn("w:val"), hexc)


def _cell_text(tc):
    return "".join(t.text or "" for t in tc.iter(qn("w:t"))).strip()


def _shade(tc, fill):
    tcpr = tc.find(qn("w:tcPr"))
    if tcpr is None:
        tcpr = OxmlElement("w:tcPr")
        tc.insert(0, tcpr)
    shd = tcpr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcpr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def _is_label_cell(tc):
    """First cell of a row in the EVENT INFORMATION grid (the row labels)."""
    tr = tc.getparent()
    return tr is not None and tr.tag == qn("w:tr") and tr.find(qn("w:tc")) is tc


def restyle(src, dst):
    d = Document(str(src))
    b = d.element.body

    # document defaults: Avenir Next, charcoal
    st = d.styles.element
    dd = st.find(qn("w:docDefaults"))
    rpr = dd.find(qn("w:rPrDefault")).find(qn("w:rPr"))
    _set_fonts(rpr, BODY)
    _set_color(rpr, BAR)
    for rf in st.iter(qn("w:rFonts")):
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            if rf.get(qn(a)):
                rf.set(qn(a), BODY)

    grid = None
    for t in b.iter(qn("w:tbl")):
        if "EVENT INFORMATION" in _cell_text(t):
            if grid is None or len(list(t.iter(qn("w:tbl")))) < len(list(grid.iter(qn("w:tbl")))):
                grid = t

    # every run: body font; bold label cells in the grid: condensed
    for r in b.iter(qn("w:r")):
        rp = _rpr(r)
        _set_fonts(rp, BODY)
        c = rp.find(qn("w:color"))
        if c is not None and c.get(qn("w:val")) in ("000000", "auto"):
            c.set(qn("w:val"), BAR)
    if grid is not None:
        for tr in grid.findall(qn("w:tr")):
            tcs = tr.findall(qn("w:tc"))
            if not tcs:
                continue
            label = tcs[0]
            text = _cell_text(label)
            for r in label.iter(qn("w:r")):
                _set_fonts(_rpr(r), LABEL)
            if text in SECTION_LABELS:
                fill = BAR
                for tc in tcs:
                    # the EVENT INFORMATION values sit on a light panel; the
                    # AUDIO / MISC bars run full width in charcoal
                    if tc is not label and text == "EVENT INFORMATION":
                        _shade(tc, PANEL)
                        continue
                    _shade(tc, fill)
                    for r in tc.iter(qn("w:r")):
                        rp = _rpr(r)
                        _set_color(rp, "FFFFFF")
                        if rp.find(qn("w:b")) is None:
                            rp.append(OxmlElement("w:b"))
            # the ARTIST 1/2/3 header row: condensed, like the labels
            if any(_cell_text(tc).startswith("ARTIST 1") for tc in tcs):
                for tc in tcs:
                    for r in tc.iter(qn("w:r")):
                        _set_fonts(_rpr(r), LABEL)

    # "SCHEDULE" / "Lead" / "Cell" labels in the left column: condensed too
    for p in b.iter(qn("w:p")):
        txt = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
        if txt in ("SCHEDULE", "Lead", "Cell", "Band Deliverables:"):
            for r in p.iter(qn("w:r")):
                _set_fonts(_rpr(r), LABEL)

    # rules: black -> corporate gray (softer grid, same weights)
    for tag in ("w:top", "w:bottom", "w:left", "w:right", "w:insideH", "w:insideV"):
        for e in b.iter(qn(tag)):
            if e.get(qn("w:val")) not in (None, "nil", "none"):
                e.set(qn("w:color"), RULE)

    # the old beige fill anywhere else -> neutral panel
    for shd in b.iter(qn("w:shd")):
        if (shd.get(qn("w:fill")) or "").upper() == "EAE7DD":
            shd.set(qn("w:fill"), PANEL)

    # header: 3CDC logo left, right tab stop for the venue mark
    sec = d.sections[0]
    sec.header_distance = Inches(0.3)
    sec.top_margin = Inches(0.75)
    hp = sec.header.paragraphs[0]
    for r in list(hp.runs):
        r._r.getparent().remove(r._r)
    width = sec.page_width - sec.left_margin - sec.right_margin
    hp.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
    corp = brand.brand()["corporate"]["logos"]["primary"]
    hp.add_run().add_picture(str(brand.BRAND_DIR / corp), height=LOGO_H)
    hp.add_run("\t")

    # Avenir Next carries a much taller line gap than Calibri; at Word's
    # "single" the grid ran four rows onto page 2. 0.85 of single brings the
    # line height back to roughly Calibri's.
    for p in b.iter(qn("w:p")):
        ppr = p.find(qn("w:pPr"))
        if ppr is None:
            ppr = OxmlElement("w:pPr")
            p.insert(0, ppr)
        sp = ppr.find(qn("w:spacing"))
        if sp is None:
            sp = OxmlElement("w:spacing")
            ppr.append(sp)
        if sp.get(qn("w:lineRule")) in (None, "auto"):
            sp.set(qn("w:line"), str(LINE))
            sp.set(qn("w:lineRule"), "auto")

    # the mission statement: smaller, so the header's height is paid back
    for p in d.paragraphs[:2]:
        for r in p.runs:
            r.font.size = Pt(8.5)
    d.save(str(dst))


def add_venue_logo(doc, venue):
    """Venue wordmark at the header's right tab. No-op for a venue the guide
    doesn't cover (Elm Street Plaza), or a header without the branded tab."""
    v = brand.venue_profile(venue or "")
    if not v:
        return False
    logo = brand.BRAND_DIR / "logos" / f"{v['slug']}-typelogo.png"
    if not logo.exists():
        return False
    hp = doc.sections[0].header.paragraphs[0]
    if not hp.paragraph_format.tab_stops or len(hp.paragraph_format.tab_stops) == 0:
        return False
    if len(hp._p.findall(".//" + qn("w:drawing"))) >= 2:
        return False  # already stamped
    hp.add_run().add_picture(str(logo), height=Inches(0.26))
    return True


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "restyle":
        restyle(sys.argv[2], sys.argv[3])
        print("wrote", sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
