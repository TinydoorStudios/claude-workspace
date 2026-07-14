#!/usr/bin/env python3
"""Build portable-context.pdf from portable-context.md content (hardcoded story — small, stable doc)."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
import os

OUT = os.path.join(os.path.dirname(__file__), "portable-context.pdf")

HEADER = colors.HexColor("#1F2937")
RULE = colors.HexColor("#9CA3AF")
TABLE_HEAD = colors.HexColor("#E5E7EB")
TABLE_ALT = colors.HexColor("#F3F4F6")

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=20, textColor=HEADER, spaceAfter=4)
sub_style = ParagraphStyle("SubX", parent=styles["Normal"], fontName="Helvetica-Oblique",
                            fontSize=9.5, textColor=colors.HexColor("#4B5563"), spaceAfter=14)
h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                           fontSize=13, textColor=HEADER, spaceBefore=16, spaceAfter=6)
body_style = ParagraphStyle("BodyX", parent=styles["Normal"], fontName="Helvetica",
                             fontSize=10, leading=14, spaceAfter=8)
bullet_style = ParagraphStyle("BulletX", parent=body_style, leftIndent=14, bulletIndent=2, spaceAfter=4)
table_cell = ParagraphStyle("TableCell", parent=body_style, fontSize=9, leading=11.5, spaceAfter=0)
table_head_cell = ParagraphStyle("TableHead", parent=table_cell, fontName="Helvetica-Bold")
footer_style = ParagraphStyle("FooterX", parent=styles["Normal"], fontName="Helvetica-Oblique",
                               fontSize=8.5, textColor=colors.HexColor("#6B7280"), spaceBefore=18)

def P(text, style=body_style):
    return Paragraph(text, style)

def make_table(header, rows, col_widths):
    data = [[P(h, table_head_cell) for h in header]] + \
           [[P(c, table_cell) for c in row] for row in rows]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(rows) + 1):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t

def rule():
    return HRFlowable(width="100%", thickness=0.75, color=RULE, spaceBefore=4, spaceAfter=10)

story = []

story.append(P("Brian Lloyd — AI Context File", title_style))
story.append(P("Drop this in at the start of a conversation with any AI tool to get it oriented fast. "
               "The full working system (venue specs, EQ starting points, mic pairings, show history) "
               "lives in Brian's own Cowork project and isn't included here.", sub_style))
story.append(rule())

story.append(P("Who I Am", h2_style))
story.append(P("Brian Lloyd — live sound and recording engineer, Cincinnati, Ohio. 20+ years in the "
               "industry. I work fast, expect accuracy, and communicate directly.", body_style))
for line in [
    "<b>Live mixing</b> — primary discipline. Every show gets multitracked.",
    "<b>Mastering and post-production</b> — studio side of the live work.",
    "<b>Classical recording</b> — a significant share of the workload. Treat it differently from "
    "everything else: minimal processing, nothing aggressive.",
    "<b>Events production</b> — AV management across multiple outdoor venues.",
]:
    story.append(P("•  " + line, bullet_style))
story.append(Spacer(1, 4))
story.append(P("<b>Businesses:</b> <i>Jazz At The Memo</i> — house engineer at Memorial Hall, Cincinnati "
               "(556 seats, DiGiCo Quantum 225, classical/jazz programming). <i>3CDC</i> (Cincinnati Center "
               "City Development Corp) — events/production team, AV across Fountain Square, Washington Park, "
               "Elm Street Plaza, Court Street Plaza, Zeigler Park, Imagination Alley. <i>Tiny Door Studios</i> "
               "— side operation, self-hosted infrastructure, automation, recording projects.", body_style))
story.append(P("<b>Contact:</b> tinydoorstudios@gmail.com", body_style))

story.append(P("How To Work With Me", h2_style))
for line in [
    "No fluff. Get to the point.",
    "Step-by-step when troubleshooting — stop and confirm at each step before moving forward.",
    "Never assume. Ask.",
    "If you can do something yourself, do it — don't ask permission for safe, reversible steps.",
    "Talk at a high level. I know signal flow, routing, gain structure, DSP. Skip the basics.",
    "Stop and ask before anything destructive (deleting, overwriting, moving files out of place) or "
    "genuinely ambiguous.",
    "Default any document deliverable to PDF unless I say otherwise.",
]:
    story.append(P("•  " + line, bullet_style))

story.append(P("Gear", h2_style))
story.append(P("<b>DAWs:</b> Studio One 7 (primary) · WaveLab 12 (mastering/post) · REAPER (multitrack "
               "capture on location). Assume Mac.", body_style))
story.append(P("<b>Consoles:</b> DiGiCo Quantum 225 (Memorial Hall house, Fountain Square FOH) · Behringer "
               "Wing (secondary venues) · Yamaha CL3 (in rotation) · Midas M32 (Washington Park FOH, "
               "Fountain Square monitors, in rotation elsewhere).", body_style))

venue_rows = [
    ["Memorial Hall (Memo)", "556 seats, Beaux Arts, DiGiCo Q225 house. Working RT60 ~1.6s with audience. "
                              "Standing waves at 63/125/200/250–315Hz — always address in EQ."],
    ["Greaves Concert Hall (NKU)", "637 seats, orchestral/chamber hall, two 9ft grands (Steinway + Baldwin), "
                                     "RT60 ~1.5–1.9s."],
    ["Fountain Square (FSQ)", "Outdoor, 3CDC. DiGiCo Q225 FOH, Midas M32 monitors, L-Acoustics A15/KS21/X12."],
    ["Washington Park (WP)", "Outdoor, 3CDC. Midas M32 FOH, JBL SRX915/906/928."],
    ["Elm Street Plaza (ESP)", "Outdoor, 3CDC."],
    ["Court Street Plaza (CSP)", "Outdoor, 3CDC."],
    ["Zeigler Park (ZP)", "Outdoor, 3CDC."],
    ["Imagination Alley (IA)", "Outdoor, 3CDC."],
]
story.append(KeepTogether([
    P("Venues", h2_style),
    make_table(["Venue", "Notes"], venue_rows, [1.6 * inch, 4.7 * inch]),
]))

story.append(Spacer(1, 10))
mic_rows = [
    ["DM6", "Earthworks DM6 SeisMic", "Kick drum"],
    ["DM17", "Earthworks DM17", "Snare top, toms"],
    ["SR20", "Earthworks SR20 Gen 2", "Hat, overheads, room"],
    ["MKH40", "Sennheiser MKH40", "Flute, pipes, classical detail"],
    ["U87", "Neumann U87", "Crowd mic, room"],
    ["U87 Jr", "Warm Audio WA-87", "Trombone"],
    ["Beta 58A", "Shure Beta 58A", "Vocals"],
    ["Beta 98H/C", "Shure Beta 98H/C", "Clip-on horns"],
    ["MD421", "Sennheiser MD421", "Brass alternative"],
    ["RNDI", "Rupert Neve Designs RNDI", "Bass, electric guitar, keys DI"],
    ["J48", "Radial J48", "Bass DI"],
    ["DPA 4099", "DPA 4099 CORE+", "Clip-on piano, strings, brass"],
    ["B3", "Countryman B3", "Clip-on strings (all string-section mics, numbered B3–B10, are this mic)"],
    ["R88", "AEA R88", "Stereo ribbon, classical recording"],
    ["MK4 / MK5 / MK41", "Schoeps CMC6 + capsule", "Classical spot (MK4), main pair (MK5, switchable "
                                                     "omni/cardioid), spot (MK41 supercardioid)"],
    ["C422", "AKG C422", "Vintage stereo LDC, XY mode — 2 console channels"],
    ["sE 8", "sE Electronics sE8", "Aux perc, overheads pair"],
]
story.append(P("Mic shorthand I use constantly", ParagraphStyle("H3", parent=h2_style, fontSize=11, spaceBefore=4)))
story.append(make_table(["Shorthand", "Full Name", "Primary Use"], mic_rows,
                         [0.95 * inch, 1.75 * inch, 3.6 * inch]))

story.append(P("How I Approach EQ and Mixing", h2_style))
for line in [
    "Whole dB values only — never half-dB.",
    "No high shelf band unless asked for one. No compression unless asked for it.",
    "Subtractive first — find and cut problems before boosting.",
]:
    story.append(P("•  " + line, bullet_style))
story.append(Spacer(1, 4))
story.append(P("<b>Genre philosophy:</b>", body_style))
for line in [
    "<i>Classical:</i> minimal, spots blend, nothing aggressive.",
    "<i>Acoustic/folk:</i> conservative. Watch for piezo quack at 1.2–2kHz.",
    "<i>Celtic:</i> 5ms+ compressor attack on melodic instruments, never gate sustained notes "
    "(fiddle, bouzouki, pipes, accordion).",
    "<i>Everything else:</i> aggressive by default — cuts −4 to −7dB tight Q, boosts +3 to +6dB.",
]:
    story.append(P("•  " + line, bullet_style))
story.append(Spacer(1, 4))
story.append(P("<b>Soundcheck order:</b> drums/percussion → bass → primary melodic instrument for the genre "
               "→ keys/piano → strings → horns/winds → vocals (always last, full band playing) → "
               "house/ambient mics (set conservatively, as blend).", body_style))
story.append(P("<b>Bus grouping:</b> drums · rhythm (bass/guitar/keys) · piano (stereo) · strings · "
               "horns/winds · vocals (lead fader separate from BGV group) · house ambient.", body_style))

story.append(P("Writing Voice", h2_style))
story.append(P("Write like a sharp, experienced person — not a chatbot. Specific tells to avoid entirely: "
               "“delve into,” “it's worth noting that,” “furthermore/moreover” as "
               "sentence openers, “in conclusion/to summarize,” “comprehensive/robust/"
               "innovative/holistic,” “game-changer/paradigm shift,” “leverage” as a "
               "verb, “utilize” (just say “use”).", body_style))
story.append(P("Structural habits to avoid: defaulting to bullet lists when a sentence would do, writing in "
               "threes (“clear, concise, and comprehensive” — pick the one that matters), "
               "mirror-starting every paragraph the same way, over-hedging (“may,” “might,” "
               "“could potentially”), summarizing what was just said, fake balance (“on one "
               "hand… on the other hand…”).", body_style))
story.append(P("Word-level habits to drop: passive voice (“it was decided” → “we "
               "decided”), adjective stacking, empty intensifiers (“very,” “quite,” "
               "“rather”), nominalizations (“make a decision” → “decide”), "
               "starting every sentence with “This,” rhetorical questions as transitions.", body_style))
story.append(P("Tone: warm but direct, like a knowledgeable colleague. No preamble — don't explain what "
               "you're about to do, just do it. Specific over general (“cut 6dB at 250Hz,” not "
               "“reduce the low-mids”). Short sentences when the point is sharp. Contractions are "
               "fine. First person when it fits (“I'd suggest…” not “one might "
               "consider…”).", body_style))
story.append(P("<b>Gut check before delivering anything written:</b> read it aloud. If it sounds like a "
               "press release or something a chatbot would say, rewrite it.", body_style))

story.append(rule())
story.append(P("This file is meant to be pasted or uploaded at the start of a session in any AI tool. It "
               "won't go stale on its own — if gear, venues, or working style change, update the source "
               "files in audio/about-me/ and regenerate this one.", footer_style))

doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    topMargin=0.65 * inch, bottomMargin=0.65 * inch,
    leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    title="Brian Lloyd — AI Context File",
)
doc.build(story)
print("Wrote", OUT)
