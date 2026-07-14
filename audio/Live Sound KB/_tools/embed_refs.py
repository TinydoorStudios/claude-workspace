#!/usr/bin/env python3
"""
embed_refs.py — Brian Lloyd / Live Sound KB
-------------------------------------------------
Reusable helper for getting REAL photos into PDFs without scraping the web.

Workflow:
  1. You drop image files (jpg/jpeg/png/webp/heic) into a drop folder, e.g.
       Live Sound KB/_refs/<topic>/
  2. (Optional) add captions/credits in a captions.tsv in that folder:
       filename<TAB>caption<TAB>credit
     ...or a per-image sidecar <basename>.txt holding "caption | credit".
     If neither exists, the filename (underscores -> spaces) is used as caption.
  3. Claude runs this helper (or imports it) to:
       - build a standalone captioned contact sheet PDF, or
       - inject a captioned photo grid into another PDF (the C3 deep-dive, etc.)

EXIF orientation is auto-corrected so phone shots/screenshots sit upright.

CLI:
  python3 embed_refs.py <drop_folder> <out.pdf> "Title" ["Subtitle"]

Import:
  from embed_refs import ref_flowables, has_images
  flowables = ref_flowables(folder, content_width, palette=...)   # list[Flowable]
"""

import os, sys, csv, glob, tempfile
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, Flowable, KeepTogether)

IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff")

# palette (matches Brian's show docs)
PAL = dict(header="#1A1A2E", sub="#0F3460", accent="#E94560", paper="#FBFAF6",
           ink="#22232b", grey="#6b7280", alt="#E8EEF7", warn="#FFE4B5")

_CACHE = os.path.join(tempfile.gettempdir(), "ref_img_cache")
os.makedirs(_CACHE, exist_ok=True)

# optional HEIC support
try:
    import pillow_heif  # noqa
    pillow_heif.register_heif_opener()
except Exception:
    pass


def _styles():
    ss = getSampleStyleSheet()
    return dict(
        cap=ParagraphStyle("cap", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=9, textColor=colors.HexColor(PAL["ink"]), leading=11.5),
        cred=ParagraphStyle("cred", parent=ss["Normal"], fontName="Helvetica-Oblique",
                            fontSize=7.8, textColor=colors.HexColor(PAL["grey"]), leading=9.5),
        ph=ParagraphStyle("ph", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=10, textColor=colors.HexColor(PAL["ink"]), leading=14),
    )


def _load_captions(folder):
    """Return {filename: (caption, credit)} from captions.tsv and/or sidecar .txt."""
    caps = {}
    tsv = os.path.join(folder, "captions.tsv")
    if os.path.exists(tsv):
        with open(tsv, newline="", encoding="utf-8") as f:
            for row in csv.reader(f, delimiter="\t"):
                if not row or row[0].strip().startswith("#"):
                    continue
                fn = row[0].strip()
                cap = row[1].strip() if len(row) > 1 else ""
                cred = row[2].strip() if len(row) > 2 else ""
                caps[fn] = (cap, cred)
    # per-image sidecars override / fill gaps
    for side in glob.glob(os.path.join(folder, "*.txt")):
        base = os.path.splitext(os.path.basename(side))[0]
        # find the image this sidecar belongs to
        for ext in IMG_EXTS:
            cand = base + ext
            if os.path.exists(os.path.join(folder, cand)):
                txt = open(side, encoding="utf-8").read().strip()
                if "|" in txt:
                    cap, cred = [p.strip() for p in txt.split("|", 1)]
                else:
                    cap, cred = txt, ""
                caps[cand] = (cap, cred)
                break
    return caps


def _prep_image(path):
    """Open, apply EXIF orientation, convert to an embeddable RGB file. Returns
    (cache_path, width_px, height_px) or None if unreadable."""
    from PIL import Image as PImage, ImageOps
    try:
        im = PImage.open(path)
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        out = os.path.join(_CACHE, "rdy_" + str(abs(hash(path))) + ".png")
        im.save(out, "PNG")
        return out, im.width, im.height
    except Exception as e:
        sys.stderr.write(f"[embed_refs] skip {os.path.basename(path)}: {e}\n")
        return None


def list_images(folder):
    """Ordered image paths in folder (case-insensitive ext, name-sorted)."""
    files = []
    for fn in sorted(os.listdir(folder)):
        if os.path.splitext(fn)[1].lower() in IMG_EXTS:
            files.append(os.path.join(folder, fn))
    return files


def has_images(folder):
    return bool(folder and os.path.isdir(folder) and list_images(folder))


def _nice(fn):
    base = os.path.splitext(fn)[0]
    return base.replace("_", " ").replace("-", " ").strip().capitalize()


def _cell(path, caption, credit, cell_w, S):
    prepped = _prep_image(path)
    if not prepped:
        return None
    cpath, w, h = prepped
    img_w = cell_w
    img_h = img_w * h / w
    max_h = 2.7 * inch
    if img_h > max_h:
        img_h = max_h
        img_w = img_h * w / h
    parts = [Image(cpath, img_w, img_h)]
    if caption:
        parts += [Spacer(1, 3), Paragraph(caption, S["cap"])]
    if credit:
        parts += [Paragraph(f"Source: {credit}", S["cred"])]
    return parts  # a list of flowables sits cleanly inside a table cell


def ref_flowables(folder, content_width, cols=2, empty_note=None):
    """Return a list of Flowables: a captioned grid of the images in `folder`.
    If empty, returns a single placeholder Flowable with drop instructions."""
    S = _styles()
    imgs = list_images(folder) if folder and os.path.isdir(folder) else []
    if not imgs:
        note = empty_note or (
            "No reference photos dropped yet. Save images into:<br/>"
            f"<b>{folder}</b><br/>"
            "then re-run — they embed here automatically. Optional captions in "
            "captions.tsv (filename &lt;tab&gt; caption &lt;tab&gt; credit).")
        return [_Placeholder(note, S)]
    caps = _load_captions(folder)
    gap = 14
    cell_w = (content_width - gap * (cols - 1)) / cols
    cells = []
    for p in imgs:
        fn = os.path.basename(p)
        cap, cred = caps.get(fn, (_nice(fn), ""))
        c = _cell(p, cap, cred, cell_w, S)
        if c:
            cells.append(c)
    # pack into rows
    flow = []
    for i in range(0, len(cells), cols):
        row = cells[i:i + cols]
        while len(row) < cols:
            row.append("")
        t = Table([row], colWidths=[cell_w + (gap if j < cols - 1 else 0) for j in range(cols)])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), gap),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 12)]))
        flow.append(t)
    return flow


class _Placeholder(Flowable):
    def __init__(self, html, S):
        super().__init__()
        self.p = Paragraph(html, S["ph"])
    def wrap(self, aw, ah):
        self.w = aw
        _, h = self.p.wrap(aw - 24, 1000)
        self.h = h + 28
        return (self.w, self.h)
    def draw(self):
        self.canv.setFillColor(colors.HexColor(PAL["warn"]))
        self.canv.roundRect(0, 0, self.w, self.h, 6, fill=1, stroke=0)
        self.canv.setFillColor(colors.HexColor(PAL["accent"]))
        self.canv.rect(0, 0, 4, self.h, fill=1, stroke=0)
        _, h = self.p.wrap(self.w - 24, 1000)
        self.p.drawOn(self.canv, 14, self.h - 14 - h)


# ---------------- standalone contact-sheet PDF ----------------
def make_contact_sheet(folder, out_pdf, title, subtitle=""):
    PAGE = landscape(letter); LW, LH = PAGE; M = 0.55 * inch; CW = LW - 2 * M
    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=ss["Normal"], fontName="Helvetica-Bold",
                        fontSize=22, textColor=colors.HexColor(PAL["header"]), leading=26)
    SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica",
                         fontSize=11, textColor=colors.HexColor(PAL["sub"]), leading=15)

    def bg(canv, doc):
        canv.saveState(); canv.setFillColor(colors.HexColor(PAL["paper"]))
        canv.rect(0, 0, LW, LH, fill=1, stroke=0)
        canv.setStrokeColor(colors.HexColor(PAL["header"])); canv.setLineWidth(0.6)
        canv.line(M, 0.42 * inch, LW - M, 0.42 * inch)
        canv.setFont("Helvetica", 8); canv.setFillColor(colors.HexColor(PAL["grey"]))
        canv.drawString(M, 0.28 * inch, "Reference Photos  ·  Live Sound KB  ·  Brian Lloyd")
        canv.drawCentredString(LW / 2, 0.28 * inch, f"{doc.page}")
        canv.restoreState()

    story = [Paragraph(title, H1)]
    if subtitle:
        story.append(Paragraph(subtitle, SUB))
    story.append(Spacer(1, 10))
    story += ref_flowables(folder, CW, cols=2)
    doc = SimpleDocTemplate(out_pdf, pagesize=PAGE, leftMargin=M, rightMargin=M,
                            topMargin=0.55 * inch, bottomMargin=0.6 * inch, title=title)
    doc.build(story, onFirstPage=bg, onLaterPages=bg)
    return out_pdf


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    folder, out_pdf, title = sys.argv[1], sys.argv[2], sys.argv[3]
    subtitle = sys.argv[4] if len(sys.argv) > 4 else ""
    n = len(list_images(folder)) if os.path.isdir(folder) else 0
    make_contact_sheet(folder, out_pdf, title, subtitle)
    print(f"built {out_pdf} from {n} image(s) in {folder}")
