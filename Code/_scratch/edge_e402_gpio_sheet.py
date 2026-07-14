#!/usr/bin/env python3
"""Edge -> Lab Gruppen E 40:2 GPIO power-control wiring sheet (Rev C — direct dry, no power)."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable)
from reportlab.lib.enums import TA_LEFT

OUT = "/Users/brianlloyd/Documents/Claude/Edge_E40-2_GPIO_Power_Control.pdf"
PIN = "8"  # Local Logic Output # placed in Composer

TITLE_BAR = colors.HexColor("#1F2937")
SUB_BAR   = colors.HexColor("#374151")
HEADER    = colors.HexColor("#111827")
ACCENT    = colors.HexColor("#2E6DA4")
WARN_BG   = colors.HexColor("#FFE4B5")
NOTE_BG   = colors.HexColor("#F4F0E8")
ALT       = colors.HexColor("#E8EEF7")
GOOD_BG   = colors.HexColor("#DCFCE7")

styles = getSampleStyleSheet()
body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=9.5, leading=13, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                    fontSize=12, textColor=ACCENT, spaceBefore=10, spaceAfter=4)
cellb = ParagraphStyle("cellb", parent=body, fontName="Helvetica-Bold", fontSize=9)
cell  = ParagraphStyle("cell", parent=body, fontSize=9, leading=11)


class TitleBar(Flowable):
    def __init__(self, w, title, sub):
        self.w = self.width = w
        self.title, self.sub, self.height = title, sub, 58
    def draw(self):
        c = self.canv
        c.setFillColor(TITLE_BAR); c.rect(0, 24, self.w, 34, fill=1, stroke=0)
        c.setFillColor(SUB_BAR);   c.rect(0, 0, self.w, 24, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16); c.drawString(12, 35, self.title)
        c.setFont("Helvetica", 9);       c.drawString(12, 8, self.sub)


class Schematic(Flowable):
    def __init__(self, w):
        self.w = self.width = w
        self.height = 210
    def box(self, x, y, w, h, label, lines, fill=colors.white):
        c = self.canv
        c.setLineWidth(1.2); c.setStrokeColor(HEADER); c.setFillColor(fill)
        c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
        c.setFillColor(HEADER); c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(x + w/2, y + h - 13, label)
        c.setFont("Helvetica", 7.4); c.setFillColor(colors.HexColor("#333333"))
        ty = y + h - 27
        for ln in lines:
            c.drawString(x + 8, ty, ln); ty -= 11
    def wire(self, pts, label=None, lx=None, ly=None):
        c = self.canv
        c.setLineWidth(1.5); c.setStrokeColor(ACCENT)
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
        if label:
            c.setFont("Helvetica", 7); c.setFillColor(ACCENT)
            c.drawString(lx, ly, label)
    def dot(self, x, y):
        c = self.canv; c.setFillColor(ACCENT); c.circle(x, y, 2.2, fill=1, stroke=0)
    def draw(self):
        c = self.canv
        # Edge box (left)
        self.box(0, 70, 150, 80, "SYMETRIX EDGE — control connector",
                 ["Local Logic Output #%s" % PIN, "  (open-collector, sinks to GND)",
                  "Logic GND  (common terminal)"], fill=ALT)
        # Amp 1 (top right)
        self.box(360, 140, 150, 62, "E 40:2  —  AMP 1  (front)",
                 ["GPI  sense", "GPI  common / GND"])
        # Amp 2 (bottom right)
        self.box(360, 30, 150, 62, "E 40:2  —  AMP 2  (front)",
                 ["GPI  sense", "GPI  common / GND"])
        # Logic Out #8 -> both amp GPI sense (parallel)
        # node out at (150,132), branch up to amp1 sense (360,185) and down to amp2 sense (360,75)
        self.wire([(150,132),(255,132)])
        self.dot(255,132)
        self.wire([(255,132),(255,185),(360,185)], "Logic Out #%s -> GPI sense (both)" % PIN, 158, 190)
        self.wire([(255,132),(255,75),(360,75)])
        # Logic GND -> both amp GPI common (parallel)
        self.wire([(150,118),(235,118)])
        self.dot(235,118)
        self.wire([(235,118),(235,171),(360,171)], "Logic GND -> GPI common (both)", 158, 106)
        self.wire([(235,118),(235,61),(360,61)])


def P(t, s=body): return Paragraph(t, s)

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.6*inch, rightMargin=0.6*inch,
                        topMargin=0.5*inch, bottomMargin=0.5*inch)
W = doc.width
flow = [TitleBar(W, "Edge → Lab Gruppen E 40:2 — GPIO Power Control",
                 "Direct dry contact, NO power supply, NO relay  ·  Edge Logic Out #%s → 2 × E 40:2  ·  Rev C · 2026-06-30" % PIN),
        Spacer(1, 10)]

flow.append(P("How it works", h2))
flow.append(P(
    "The E 40:2 GPI is a dry-contact input that supplies its own sense — <b>short its two GPI terminals = amp ON</b>, "
    "open = STANDBY. The Edge <b>Local Logic Output #%s</b> is an open-collector output that, when the toggle is ON, "
    "shorts to the Edge control ground. Wire it straight across both amps' GPI pairs and it closes them — <b>no power "
    "supply, no relay, nothing to power.</b> One toggle, both amps." % PIN))

flow.append(P("Wiring — Edge Logic Out #%s to both amps" % PIN, h2))
flow.append(Schematic(W))

flow.append(P("Connection list", h2))
wt = Table([
    [P("<b>Edge control connector</b>",cellb), P("<b>→</b>",cellb),
     P("<b>Amp 1 GPI (front)</b>",cellb), P("<b>Amp 2 GPI (front)</b>",cellb), P("<b>Purpose</b>",cellb)],
    [P("Local Logic Output #%s" % PIN,cell),P("→",cell),P("GPI sense",cell),P("GPI sense",cell),P("Sinks both GPIs to GND when ON",cell)],
    [P("Logic GND (common)",cell),P("→",cell),P("GPI common / GND",cell),P("GPI common / GND",cell),P("Shared return",cell)],
], colWidths=[1.9*inch, 0.3*inch, 1.5*inch, 1.5*inch, W-5.2*inch])
wt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),HEADER), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, ALT]),
    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#B0B8C4")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),5),
    ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("FONTSIZE",(0,0),(-1,-1),8.7)]))
flow.append(wt)
flow.append(Spacer(1,3))
flow.append(P("Both amps land in parallel on the one logic output: Logic Out #%s to both GPI-sense terminals, "
              "Logic GND to both GPI-common terminals. Toggle ON = both amps on; OFF = both standby." % PIN, small))

flow.append(P("Composer side (done)", h2))
flow.append(P("Local Logic Output #%s placed, driven by a latching on/off toggle labeled Amp Power. Save the design; "
              "push to the unit when the venue is safe to interrupt." % PIN, body))

flow.append(Spacer(1,6))
poln = Table([[P("<b>Polarity — the one adjustment:</b> the amp's <b>GPI sense</b> terminal goes to Logic Out #%s; "
    "the amp's <b>common/GND</b> terminal goes to Logic GND. The Edge output only conducts one way. If an amp doesn't "
    "switch, swap its two leads — that's the only thing to fix." % PIN, body)]],
    colWidths=[W])
poln.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),WARN_BG),
    ("BOX",(0,0),(-1,-1),0.7,colors.HexColor("#C9A227")),
    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
flow.append(poln)

flow.append(Spacer(1,6))
notes = Table([[P("<b>Notes:</b>  (1) This is not galvanically isolated — both amps share the Edge control ground. "
    "For low-voltage on/off control that is standard and fine. A truly floating/isolated contact would require a relay + "
    "coil power, which is deliberately avoided here.  (2) Auto-standby (APD/APO) is automatic and not user-adjustable on "
    "the amp: ~20 min of silent inputs sends it to standby (&lt;1W); it self-wakes in ~2 s on the next signal. GPI OFF = "
    "forced standby (your off); GPI ON = forced on. No amp setup needed; front-panel POWER still works locally.  (3) Confirm the two GPI "
    "terminal roles (sense vs common) against the amp's silkscreen before landing wires.", body)]],
    colWidths=[W])
notes.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GOOD_BG),
    ("BOX",(0,0),(-1,-1),0.8,colors.HexColor("#065F46")),
    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
flow.append(notes)

doc.build(flow)
print("WROTE", OUT)
