#!/usr/bin/env python3
"""
mic_page_gen.py  — Live Sound KB mic-page generator (framework).

One record in -> a full mic wiki page + a reference PDF + an asset folder, all
matching the Audio-Technica PRO 6L / DPA 4099 house style. This is the single
source of truth for how a "mic in the locker/KB" is documented. Every time Brian
says "add a mic," fill a record (see mic_data.json / mic-record.schema) and run
this; then publish with kb-publish.sh.

Usage:
    python3 mic_page_gen.py --data mic_data.json            # build all records
    python3 mic_page_gen.py --data mic_data.json --slug shure-sm57   # one mic
    python3 mic_page_gen.py --data mic_data.json --wire     # also rewrite the
             mic-library thumbnails table, index.md links, and kb-nav.json

Outputs (per mic, relative to the Wiki/ root):
    Wiki/mic-<slug>.md
    Wiki/assets/mics/<slug>/mic-<slug>.pdf
    Wiki/assets/mics/<slug>/               # photo drop folder (full + thumb)

Photo convention (files Brian/te browser step drop in later):
    Wiki/assets/mics/<slug>/<slug>.jpg        full-size, shown on the detail page
    Wiki/assets/mics/<slug>/<slug>-thumb.jpg  thumbnail, shown on the library page
The page and library row reference these paths; they render the moment the file
exists, and show a neutral placeholder line until then.
"""
import argparse, json, os, sys, datetime, html, re

def rl(s):
    """Convert markdown **bold** to ReportLab <b> tags for PDF paragraphs."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", str(s))

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Live Sound KB/
WIKI = os.path.join(KB, "Wiki")
ASSETS = os.path.join(WIKI, "assets", "mics")
TODAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------- helpers
def q(v):
    """YAML-safe scalar: quote anything with a colon/special char."""
    s = str(v)
    if any(c in s for c in ':#"\n') or s.strip() != s:
        return '"' + s.replace('"', '\\"') + '"'
    return s

def thumb_path(slug):  return f"/assets/mics/{slug}/{slug}-thumb.jpg"
def full_path(slug):   return f"/assets/mics/{slug}/{slug}.jpg"
def pdf_path(slug):    return f"/assets/mics/{slug}/mic-{slug}.pdf"

# ---------------------------------------------------------------- markdown page
def build_md(m):
    slug = m["slug"]
    tags = ", ".join(m.get("tags", []))
    fm = [
        "---",
        f'title: {q(m["name"])}',
        f'description: {q(m["description"])}',
        "published: true",
        f"date: {m.get('date', TODAY)}",
        "editor: markdown",
        f"tags: [{tags}]",
        f'Status: {q(m["status"])}',
        f'Last updated: {q(m.get("date", TODAY))}',
        f'Sources: {q(m.get("sources",""))}',
        f'Summary: {q(m.get("summary",""))}',
        "---",
        "",
        f"# {m['name']}",
        "",
        # photo block: renders when the file is dropped in; placeholder otherwise
        f'<div style="width:100%;max-width:340px;height:300px;border-radius:10px;'
        f"background:#f4f4f4 url('{full_path(slug)}') center/contain no-repeat;"
        f'border:1px solid #e2e6ea;margin:4px 0 12px;"></div>',
        "",
        f"**Reference sheet:** [Download PDF]({pdf_path(slug)})",
        "",
        m["intro"],
        "",
        "## Specifications",
        "",
        "| Spec | Value |",
        "|---|---|",
    ]
    for k, v in m["specs"].items():
        fm.append(f"| {k} | {v} |")
    fm += ["", "## Sound and placement", "", m["sound"], ""]
    if m.get("bestfit"):
        fm.append("Best-fit sources:")
        fm.append("")
        for b in m["bestfit"]:
            fm.append(f"- {b}")
        fm.append("")
    if m.get("notes"):
        fm.append("## Notes")
        fm.append("")
        for n in m["notes"]:
            fm.append(f"- {n}")
        fm.append("")
    if m.get("comparable"):
        fm += ["## Comparable mics", "", "| Mic | Relationship |", "|---|---|"]
        for c in m["comparable"]:
            fm.append(f"| {c[0]} | {c[1]} |")
        fm.append("")
    fm += ["## Related Pages", ""]
    for label, path in m.get("related", []):
        fm.append(f"- [{label}]({path})")
    fm.append("")
    return "\n".join(fm)

# ---------------------------------------------------------------- reference PDF
def build_pdf(m, out_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, Image, HRFlowable)

    NAVY = colors.HexColor("#1A3A5C")
    ACC  = colors.HexColor("#2E6DA4")
    slug = m["slug"]
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=NAVY, fontSize=20,
                        spaceAfter=2, alignment=0)
    sub = ParagraphStyle("sub", parent=ss["Normal"], textColor=ACC, fontSize=10,
                         spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=NAVY, fontSize=12,
                        spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=ss["Normal"], fontSize=7.5,
                           textColor=colors.grey)

    doc = SimpleDocTemplate(out_path, pagesize=letter,
                            leftMargin=0.7*inch, rightMargin=0.7*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch,
                            title=f"{m['name']} — Mic Reference")
    F = []
    F.append(Paragraph(m["name"], h1))
    F.append(Paragraph(f"{m['category']} &nbsp;·&nbsp; {m['status']}", sub))
    F.append(HRFlowable(width="100%", thickness=1, color=ACC, spaceAfter=8))

    # optional photo
    img = os.path.join(ASSETS, slug, f"{slug}.jpg")
    if os.path.exists(img):
        try:
            F.append(Image(img, width=2.4*inch, height=2.4*inch, kind="proportional"))
            F.append(Spacer(1, 6))
        except Exception:
            pass

    F.append(Paragraph(rl(m["intro"]), body))
    F.append(Paragraph("Specifications", h2))
    rows = [["Spec", "Value"]] + [[k, str(v)] for k, v in m["specs"].items()]
    t = Table(rows, colWidths=[1.9*inch, 4.6*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F8")]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C0CCD8")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    F.append(t)

    F.append(Paragraph("Sound and placement", h2))
    F.append(Paragraph(rl(m["sound"]), body))
    for b in m.get("bestfit", []):
        F.append(Paragraph(f"• {rl(b)}", body))
    if m.get("notes"):
        F.append(Paragraph("Notes", h2))
        for n in m["notes"]:
            F.append(Paragraph(f"• {rl(n)}", body))
    if m.get("comparable"):
        F.append(Paragraph("Comparable mics", h2))
        crows = [["Mic", "Relationship"]] + [[c[0], c[1]] for c in m["comparable"]]
        ct = Table(crows, colWidths=[1.9*inch, 4.6*inch])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), ACC),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F8")]),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C0CCD8")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        F.append(ct)
    F.append(Spacer(1, 10))
    F.append(Paragraph(f"Live Sound KB · {m['name']} · generated {TODAY} · "
                       f"sources: {html.escape(m.get('sources',''))}", small))
    doc.build(F)

# ---------------------------------------------------------------- one mic
def build_one(m):
    slug = m["slug"]
    os.makedirs(os.path.join(ASSETS, slug), exist_ok=True)
    with open(os.path.join(WIKI, f"mic-{slug}.md"), "w") as f:
        f.write(build_md(m))
    build_pdf(m, os.path.join(ASSETS, slug, f"mic-{slug}.pdf"))
    return slug

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--slug", help="build just one mic by slug")
    ap.add_argument("--wire", action="store_true",
                    help="(re)write library thumbnails, index links, nav")
    args = ap.parse_args()
    data = json.load(open(args.data))
    all_mics = data["mics"] if isinstance(data, dict) else data
    mics = all_mics
    if args.slug:
        mics = [m for m in all_mics if m["slug"] == args.slug]
        if not mics:
            sys.exit(f"no mic with slug {args.slug}")
    built = [build_one(m) for m in mics]
    print(f"built {len(built)} page(s): {', '.join(built)}")
    if args.wire:
        # Always wire from the FULL record set. wire_all() regenerates the whole
        # gallery block between its markers, so handing it a --slug-filtered list
        # wiped every other tile — which is how the gallery ended up holding a
        # single mic. (Fixed 2026-07-30, caught adding the Shure PG52.)
        from mic_wire import wire_all
        wire_all(all_mics)
        print(f"wired library / index / nav — gallery rebuilt from {len(all_mics)} records")

if __name__ == "__main__":
    main()
