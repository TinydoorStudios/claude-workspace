#!/usr/bin/env python3
"""Band-changeover sheet for the FSQ 2026-08-07 double bill.

Reads BOTH show specs and derives the input differences mechanically, so the sheet
can never drift from the packets it is bound with. Renders with reportlab to match
the rest of the packet (weasyprint's system libs aren't available on this Mac).

    python3 build_changeover.py
"""
import json, os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
BAND_A = "Bright Light Social Hour"
BAND_B = "J Roddy Walston"
OUT = os.path.join(HERE, "FSQ 2026-08-07 - Band Changeover.pdf")

# palette (project CLAUDE.md)
NAVY   = colors.HexColor("#1A3A5C")
ACCENT = colors.HexColor("#2E6DA4")
TITLEBAR = colors.HexColor("#1F2937")
SUBBAR = colors.HexColor("#374151")
COLHDR = colors.HexColor("#111827")
STRIKE_H, STRIKE_R = colors.HexColor("#FCD9B4"), colors.HexColor("#FFEDD5")
ADD_H,    ADD_R    = colors.HexColor("#BBF7D0"), colors.HexColor("#DCFCE7")
MOVE_H,   MOVE_R   = colors.HexColor("#DDD6FE"), colors.HexColor("#EDE9FE")
STAY_H,   STAY_R   = colors.HexColor("#E5E7EB"), colors.HexColor("#F3F4F6")
WARN               = colors.HexColor("#FFE4B5")
CREAM              = colors.HexColor("#F4F0E8")

S_TITLE = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white,
                         leading=24)
S_SUB   = ParagraphStyle("s", fontName="Helvetica", fontSize=9.5, textColor=colors.white, leading=13)
S_H     = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=11, textColor=colors.black,
                         leading=14, spaceBefore=2, spaceAfter=2)
S_CELL  = ParagraphStyle("c", fontName="Helvetica", fontSize=8.5, leading=10.5)
S_CELLB = ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5)
S_MONO  = ParagraphStyle("m", fontName="Courier-Bold", fontSize=9, leading=11)
S_BODY  = ParagraphStyle("b", fontName="Helvetica", fontSize=9, leading=12.5)
S_NOTE  = ParagraphStyle("n", fontName="Helvetica", fontSize=8.5, leading=11.5)


def load(name):
    with open(os.path.join(HERE, f"{name}.spec.json")) as f:
        return json.load(f)


def chmap(spec):
    return {c["ch"]: c for c in spec["channels"]}


def P(t, st=S_CELL):
    return Paragraph(t, st)


def block(title, header_bg, row_bg, rows, widths, head):
    """One coloured section: bar + table."""
    bar = Table([[Paragraph(title, S_H)]], colWidths=[sum(widths)])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), header_bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    data = [[Paragraph(f"<font color='white'><b>{h}</b></font>", S_CELL) for h in head]] + rows
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), COLHDR),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA6B2")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), row_bg))
    t.setStyle(TableStyle(st))
    return KeepTogether([bar, t, Spacer(1, 10)])


def main():
    a, b = load(BAND_A), load(BAND_B)
    ca, cb = chmap(a), chmap(b)
    W = 7.5 * inch

    doc = SimpleDocTemplate(OUT, pagesize=letter,
                            leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                            topMargin=0.45 * inch, bottomMargin=0.45 * inch,
                            title="FSQ 2026-08-07 — Band Changeover",
                            author="Brian Lloyd")
    el = []

    # ---- title bar
    tb = Table([[Paragraph("BAND CHANGEOVER", S_TITLE)],
                [Paragraph("Fountain Square &middot; Friday 2026-08-07 &middot; DiGiCo Quantum 225 &nbsp;|&nbsp; "
                           "SET 1 <b>Bright Light Social Hour</b> &rarr; SET 2 <b>J Roddy Walston</b> &nbsp;|&nbsp; "
                           "FOH Brian Lloyd", S_SUB)]],
               colWidths=[W])
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TITLEBAR),
        ("BACKGROUND", (0, 1), (-1, 1), SUBBAR),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    el += [tb, Spacer(1, 10)]

    # ---- the one real trap
    trap = Table([[Paragraph(
        "<b>THE ONE THING THAT WILL BITE YOU:</b> the keys-amp SM57 changes channel. "
        "It is on <b>Local 19</b> for Bright Light and <b>Local 18</b> for J Roddy — because "
        "Bright Light's keyboard is stereo (17+18) and J Roddy's is mono (17). Move that tail, or "
        "the keys amp lands on a dead fader. Everything else at the break is a straight strike or add.",
        S_BODY)]], colWidths=[W])
    trap.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WARN),
        ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#B45309")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    el += [trap, Spacer(1, 12)]

    # ---- derive the diff
    only_a = sorted(set(ca) - set(cb))
    only_b = sorted(set(cb) - set(ca))
    both = sorted(set(ca) & set(cb))
    # "Changed in place" = the mic or the fader label actually moves. Instrument
    # prose differs on several shared channels (player names) without anything on
    # stage changing, so it is deliberately NOT part of the test.
    changed = [c for c in both if (ca[c]["mic"] != cb[c]["mic"]
                                   or ca[c]["name"] != cb[c]["name"])]
    same = [c for c in both if c not in changed]

    # STRIKE
    rows = []
    for c in only_a:
        ch = ca[c]
        rows.append([P(f"<b>{c}</b>", S_MONO), P(ch["name"], S_CELLB),
                     P(ch["instrument"]), P(ch["mic"])])
    el.append(block("STRIKE AFTER BRIGHT LIGHT &mdash; pull these off the stage and out of the split",
                    STRIKE_H, STRIKE_R, rows,
                    [0.5 * inch, 1.0 * inch, 3.0 * inch, 3.0 * inch],
                    ["Ch", "Fader", "Was", "Mic / DI"]))

    # ADD
    rows = []
    for c in only_b:
        ch = cb[c]
        patch = ch.get("patch", f"Local {c}")
        rows.append([P(f"<b>{c}</b>", S_MONO), P(ch["name"], S_CELLB),
                     P(ch["instrument"]), P(ch["mic"]), P(patch, S_MONO)])
    el.append(block("ADD FOR J RODDY &mdash; new inputs that were not up for the first set",
                    ADD_H, ADD_R, rows,
                    [0.5 * inch, 1.0 * inch, 2.4 * inch, 2.5 * inch, 1.1 * inch],
                    ["Ch", "Fader", "Now", "Mic / DI", "Patch"]))

    # CHANGES IN PLACE
    rows = []
    for c in changed:
        rows.append([P(f"<b>{c}</b>", S_MONO),
                     P(f"{ca[c]['name']} &mdash; {ca[c]['instrument']}<br/>"
                       f"<font size=7.5 color='#555555'>{ca[c]['mic']}</font>"),
                     P(f"{cb[c]['name']} &mdash; {cb[c]['instrument']}<br/>"
                       f"<font size=7.5 color='#555555'>{cb[c]['mic']}</font>")])
    el.append(block("CHANGES IN PLACE &mdash; same channel number, different source",
                    MOVE_H, MOVE_R, rows,
                    [0.5 * inch, 3.5 * inch, 3.5 * inch],
                    ["Ch", "Bright Light Social Hour", "J Roddy Walston"]))

    # STAYS PUT
    rows = []
    for c in same:
        rows.append([P(f"<b>{c}</b>", S_MONO), P(ca[c]["name"], S_CELLB),
                     P(ca[c]["mic"])])
    half = (len(rows) + 1) // 2
    left, right = rows[:half], rows[half:]
    while len(right) < len(left):
        right.append([P(""), P(""), P("")])
    merged = [l + r for l, r in zip(left, right)]
    w = [0.4 * inch, 0.95 * inch, 2.4 * inch] * 2
    el.append(block("STAYS PATCHED &mdash; do not touch. Same mic, same socket, both sets. "
                    "(The EQ still changes &mdash; it comes with the .ses.)",
                    STAY_H, STAY_R, merged, w,
                    ["Ch", "Fader", "Mic / DI", "Ch", "Fader", "Mic / DI"]))

    # ---- console + stage notes
    el.append(Paragraph("AT THE DESK", ParagraphStyle(
        "d", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY, spaceAfter=4)))
    desk = [
        "<b>Load <i>J Roddy Walston.ses</i>.</b> Every shared channel is re-EQ'd for the second band — "
        "the kit is the same drums but the curves are not. Shallower mud and box cuts across the kit "
        "(toms &minus;4 instead of &minus;6, snare box &minus;7 instead of &minus;8, kick box &minus;6 instead of &minus;7) "
        "because this set is built on drums that bloom.",
        "<b>The FX rack changes too, not just the channel EQ.</b> Bright Light runs Sun Plate A, Sunset "
        "Chamber and Studio B Close; J Roddy runs Echo Plate, Gold Hall and Snare Chamber. Vocal Plate, "
        "Guitar Room and Studio A carry over. Gold Hall ships with VLF at 0 dB — cut it to &minus;12 before "
        "you send anything to it.",
        "<b>Ring out faders 33&ndash;36 before the second set.</b> All four wireless override the template's "
        "184 Hz HPF and each writes a B4, which removes the template's &minus;18 dB @ 5 kHz Q20 feedback notch. "
        "Same warning applied to 25/26/27 for the first set.",
        "<b>Faders 20&ndash;27 go quiet</b> for the second set (percussion rig + the three wired vocals). "
        "Faders 33&ndash;36 come alive. Fader 19 goes dark.",
    ]
    for d in desk:
        el.append(Paragraph("&bull; " + d, S_NOTE))
        el.append(Spacer(1, 3))
    el.append(Spacer(1, 8))

    el.append(Paragraph("ON THE STAGE", ParagraphStyle(
        "d2", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY, spaceAfter=4)))
    stage = [
        "<b>Cymbals swap</b> — the backline quote says the rider does not request cymbals, so both bands "
        "bring their own. No repatch, but ch 5 (hat) and ch 9 (overheads) are hearing different metal, and "
        "both curves already account for it.",
        "<b>Snare may swap</b> — the backline ships both a 6.5&quot;&times;14&quot; and a 5.5&quot;&times;14&quot; DW Collectors "
        "maple snare on two stands, so a change between sets is set up for. Check which is up.",
        "<b>Second guitar amp comes into play.</b> Bright Light uses one amp (ch 13). J Roddy uses both — "
        "ch 13 on the '65 Twin Reverb (bright, owns the top lane) and ch 14 on the Blues Deluxe (tweed, "
        "owns the midrange lane). If the amps end up the other way round, swap the two EQ cards with them.",
        "<b>Keyboards are artist-supplied on both bands</b> (the backline Keyboard line is a two-tier stand "
        "and nothing else). Bright Light's is stereo into two DIs; J Roddy's is mono into one.",
        "<b>Bass rig and drum kit do not move.</b> Ampeg SVT-CL / 410HLF / SVT 15e and the DW Collectors kit "
        "serve both sets.",
    ]
    for s in stage:
        el.append(Paragraph("&bull; " + s, S_NOTE))
        el.append(Spacer(1, 3))
    el.append(Spacer(1, 10))

    tally = Table([[Paragraph(
        f"<b>Tally:</b> {len(only_a)} inputs struck &nbsp;&middot;&nbsp; {len(only_b)} added "
        f"&nbsp;&middot;&nbsp; {len(changed)} changed in place &nbsp;&middot;&nbsp; "
        f"{len(same)} untouched. &nbsp; Derived directly from the two show specs, so this sheet cannot "
        f"drift from the packets it is bound with.", S_NOTE)]], colWidths=[W])
    tally.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9AA6B2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    el.append(tally)

    doc.build(el)
    print("WROTE", OUT)
    print(f"  struck {len(only_a)} {only_a}")
    print(f"  added  {len(only_b)} {only_b}")
    print(f"  changed in place {changed} (+ ch 19 going dark)")
    print(f"  untouched {len(same)} {same}")


if __name__ == "__main__":
    main()
