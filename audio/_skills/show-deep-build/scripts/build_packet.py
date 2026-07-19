#!/usr/bin/env python3
"""
build_packet.py — deep-research show packet engine (show-deep-build skill).

ONE source of truth (a deep-research spec.json) -> every paperwork output:
  <Show> - FOH Channel Processing.md   (patcher input; feed to the venue .ses patcher)
  <Show> - Input List.xlsx             (+ Monitors / Reverbs sheets when the spec carries them)
  <Show> - Show Packet.pdf             (via show-packet-builder-template.py)
  <Show> - FOH EQ Reasoning.pdf        (the EQ Rationale — required deep-research deliverable)
  <Show> - MASTER.pdf                  (everything in one PDF: packet + rationale + any
                                        band-provided "<Show> - Stage Plot.pdf"/"- Rider.pdf"
                                        found in the show folder; individual files still ship)

House rules enforced at validation (2026-07-08 additions):
  - RESERVED template channels error out (fsq ch 10 = SNARE PL8 return; OH pair is
    STEREO on fader 9 — never split across 9/10)
  - "reverbs" is REQUIRED every show, FSQ included (3 complementary vocal + 1-2
    instrument + general when warranted; Seventh Heaven presets verbatim, each with
    settings + in-plugin EQ + why, plus spec-level "reverb_pairing"). Explicit
    opt-out: "no_reverb": true.
  - Stage plots are BAND-PROVIDED — never generated; drop theirs in the show folder
    as "<Show> - Stage Plot.pdf" and the MASTER picks it up.

The .ses itself is built per-venue by the existing patcher (Q225 SES Patcher SOP) using the .md
this script writes. This script does NOT touch the .ses.

The spec is VALIDATED before anything is written (house rules: ribbon = no 48V, vocals cuts-only,
whole dB, band/freq ranges) and the .md is auto-linted with audio/_shared/md_lint.py after writing.
Validation errors abort; warnings print.

Usage:
  python3 build_packet.py --spec "<spec.json>" --out "<show folder>" \
      [--packet-builder "~/Documents/Claude/audio/show-packet-builder-template.py"]

Deps: openpyxl + reportlab (pip3 install --user; both present on the Mac as of 2026-07-06).
Spec schema: see references/spec-schema.md. Channels list only ACTIVE bands; any band 1-4 not
present is treated as FLAT. Band numbering is Brian's console convention: b1=low .. b4=high.
"""
import argparse, json, os, sys, importlib.util

VENUE_LABELS = {"fsq": "Fountain Square", "memo": "Memorial Hall", "wp": "Washington Park",
                "esp": "Elm Street Plaza", "csp": "Court Street Plaza", "zp": "Zeigler Park",
                "ia": "Imagination Alley", "greaves": "Greaves Concert Hall"}
KNOWN_SECTIONS = {"DRUMS", "BASS", "RHYTHM", "GUITAR", "KEYS", "PIANO", "STRINGS", "HORNS",
                  "VOCALS", "AMBIENT", "SPARE"}
RIBBON_FLAG = "⚠ RIBBON — NO 48V"
TOUR_FLAG = "⚑ TOUR — confirm at load-in"

# Template faders that are NOT inputs — assigning a source here clobbers an
# FX return (learned the hard way: Hot Magnolias put OH R on FSQ ch 10 and
# overwrote the snare plate return, 2026-07-08). The venue patcher also hard
# refuses these; catching it at spec time is cheaper.
RESERVED_CH = {
    "fsq": {10: "SNARE PL8 — snare plate reverb return. Overheads are STEREO "
                "on fader 9 (both OH mics on that one fader); an OH pair "
                "never spills onto 10."},
}

# ---------------------------------------------------------------- spec helpers
def load_spec(p):
    with open(p) as f:
        return json.load(f)

def venue_label(spec):
    return spec.get("venue_label") or VENUE_LABELS.get(str(spec.get("venue", "")).lower(), "")

def fmt_freq(f):
    f = float(f)
    return f"{f/1000:g} kHz" if f >= 1000 else f"{f:g} Hz"

def bands_by_num(ch):
    """Return {1..4: band-dict or None}. Missing / gain==None / type FLAT -> None."""
    out = {1: None, 2: None, 3: None, 4: None}
    for b in ch.get("bands", []):
        n = int(b["b"])
        if b.get("gain") is None or str(b.get("type", "")).upper() == "FLAT":
            continue
        out[n] = b
    return out

def patch_label(ch):
    return ch.get("patch") or f"Local {ch['ch']}"

def flag_notes(ch):
    """Channel notes with the ribbon/TOUR flags prepended (input list + packet rows)."""
    flags = []
    if ch.get("ribbon"):
        flags.append(RIBBON_FLAG)
    if ch.get("tour"):
        flags.append(TOUR_FLAG)
    base = ch.get("notes") or ""
    return " · ".join(flags + ([base] if base else [])) or None

def esc(s):
    """Escape user text for reportlab Paragraph markup."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------------------------------------------------------- 0. validation
def validate_spec(spec):
    """House rules enforced as code. Returns (errors, warnings)."""
    errors, warnings = [], []
    if not spec.get("channels"):
        errors.append("spec has no channels")
        return errors, warnings
    reserved = RESERVED_CH.get(str(spec.get("venue", "")).lower(), {})
    # Reverb suggestions are a required deliverable, every show, FSQ included
    # (Brian, 2026-07-08): 3 complementary vocal options, 1-2 instrument, and
    # a general verb when warranted — Seventh Heaven Pro, presets verbatim
    # from the reverb KB, each with settings + in-plugin EQ + why, plus a
    # spec-level "reverb_pairing" line on using them together.
    revs = spec.get("reverbs") or []
    if not revs and not spec.get("no_reverb"):
        errors.append('spec has no "reverbs" — reverb suggestions are required every '
                      'show (FSQ included). 3 vocal + 1-2 instrument (+ general), '
                      'Seventh Heaven presets verbatim, settings + plugin EQ + why. '
                      'If Brian explicitly wants none, set "no_reverb": true.')
    if revs:
        roles = [str(r.get("role", "")).lower() for r in revs if isinstance(r, dict)]
        if roles.count("vocal") < 3:
            warnings.append(f"reverbs: {roles.count('vocal')} vocal option(s) — Brian wants "
                            "3 complementary vocal choices")
        if roles.count("instrument") < 1:
            warnings.append("reverbs: no instrument option — Brian wants 1-2 (horn-specific when asked)")
        if not spec.get("reverb_pairing"):
            warnings.append('reverbs present but no "reverb_pairing" — add the how-they-work-'
                            'together line')
        for r in revs:
            if isinstance(r, dict) and not (r.get("plugin_eq") or r.get("settings")):
                warnings.append(f"reverb {r.get('preset','?')!r}: no settings/plugin_eq — include "
                                "the in-plugin moves, not just the preset name")
    seen_ch, seen_secs, last_sec = set(), set(), None
    for ch in spec["channels"]:
        cid = ch.get("ch")
        tag = f"Ch {cid} ({ch.get('name','?')})"
        if cid in seen_ch:
            errors.append(f"{tag}: duplicate channel number")
        seen_ch.add(cid)
        if cid in reserved:
            errors.append(f"{tag}: Ch {cid} is RESERVED on the "
                          f"{spec.get('venue','')} template — {reserved[cid]}")
        if not ch.get("mic"):
            errors.append(f"{tag}: no mic/DI — don't guess a mic from an instrument")
        if not ch.get("instrument"):
            warnings.append(f"{tag}: no instrument field (input list falls back to fader name)")
        if ch.get("ribbon") and ch.get("phantom"):
            errors.append(f"{tag}: ribbon with phantom=true — NO 48V on ribbons, ever")
        sec = str(ch.get("section", "")).upper()
        if sec not in KNOWN_SECTIONS:
            warnings.append(f"{tag}: unknown section {sec!r}")
        if sec != last_sec:
            if sec in seen_secs:
                warnings.append(f"{tag}: section {sec} reappears out of order — "
                                "packet/rationale section bars will repeat; group the channels")
            seen_secs.add(sec)
            last_sec = sec
        hpf = ch.get("hpf", 20)
        if not (20 <= float(hpf) <= 20000):
            errors.append(f"{tag}: HPF {hpf} outside 20..20000")
        lpf = ch.get("lpf")
        if lpf is not None and not (20 <= float(lpf) <= 20000):
            errors.append(f"{tag}: LPF {lpf} outside 20..20000")
        for b in ch.get("bands", []):
            n = b.get("b")
            if n not in (1, 2, 3, 4):
                errors.append(f"{tag}: band number {n!r} not 1..4")
                continue
            g = b.get("gain")
            if g is None or str(b.get("type", "")).upper() == "FLAT":
                continue
            if not (-18 <= g <= 18):
                errors.append(f"{tag} B{n}: gain {g} outside ±18")
            if g != int(g):
                warnings.append(f"{tag} B{n}: fractional gain {g} dB (house rule: whole dB)")
            f = b.get("freq")
            if f is None or not (20 <= float(f) <= 20000):
                errors.append(f"{tag} B{n}: freq {f!r} outside 20..20000")
            q = b.get("q")
            if q is None or not (0.3 <= float(q) <= 20):
                warnings.append(f"{tag} B{n}: Q {q!r} outside 0.3..20")
            if sec == "VOCALS" and g > 0 and not b.get("approved"):
                errors.append(f"{tag} B{n}: +{g} dB boost on a VOCAL — vocals are cuts-only, "
                              "every genre (feedback control). If Brian explicitly approved it, "
                              'add "approved": true to the band.')
            if n == 4 and str(b.get("type", "")).upper() == "SHELF" and g > 0 and not b.get("approved"):
                warnings.append(f"{tag} B4: high-shelf boost — house rule is no high shelf "
                                "unless Brian asked; confirm it was requested")
            d = b.get("deq")
            if d and not all(k in d for k in ("thr", "atk_ms", "rel_ms")):
                errors.append(f"{tag} B{n}: DEQ missing thr/atk_ms/rel_ms")
        name = str(ch.get("name", ""))
        if len(name) > 12:
            warnings.append(f"{tag}: fader name is {len(name)} chars (>12 — legibility)")
    return errors, warnings

# ---------------------------------------------------------------- 1. .md (patcher input)
def write_md(spec, folder):
    show = spec["show_name"]
    vl = venue_label(spec)
    sub = " · ".join(x for x in [vl, spec.get("console_label", "DiGiCo Quantum 225"),
                                 spec.get("show_date", ""), spec.get("rev", "Rev 1.0")] if x)
    L = [f"# {show} — FOH Channel Processing", f"## {sub}",
         "*Deep-research pass. Active channels only. Band order: B4 (high) -> B3 -> B2 -> B1 (low).*", ""]
    for ch in spec["channels"]:
        L.append(f"## Ch {ch['ch']} | {ch['name']} | {ch['mic']}")
        lpf = ch.get("lpf")
        L.append(f"HPF: {ch.get('hpf',20):g} | LPF: {'OFF' if not lpf else f'{lpf:g}'}")
        bb = bands_by_num(ch)
        for n in (4, 3, 2, 1):
            b = bb[n]
            if not b:
                L.append(f"B{n}: FLAT"); continue
            ty = "SHELF" if str(b["type"]).upper() == "SHELF" else "BELL"
            line = f"B{n}: {b['gain']:+g} | {b['freq']:g} | {b['q']:g} | {ty}"
            d = b.get("deq")
            if d:
                line += f" | DEQ: thr={d['thr']:g} atk={d['atk_ms']:g}ms rel={d['rel_ms']:g}ms"
            L.append(line)
        L.append("")
    p = os.path.join(folder, f"{show} - FOH Channel Processing.md")
    open(p, "w").write("\n".join(L)); return p

def lint_md(md_path):
    """Auto-lint the written .md with the shared linter. Errors abort the build."""
    shared = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "..", "..", "..", "_shared"))
    if not os.path.isdir(shared):
        print("note: _shared not found — md_lint skipped"); return
    sys.path.insert(0, shared)
    try:
        import md_lint
    except ImportError:
        print("note: md_lint not importable — skipped"); return
    errors, warnings = md_lint.lint(md_path)
    for w in warnings:
        print("  md-lint warn:", w)
    if errors:
        for e in errors:
            print("  md-lint ERROR:", e)
        raise SystemExit("md_lint failed — the written .md is not patcher-safe")
    print("md_lint PASS —", len(warnings), "warnings")

# ---------------------------------------------------------------- 2. Input List .xlsx
def write_xlsx(spec, folder):
    import openpyxl
    from openpyxl.styles import Font, Alignment
    show = spec["show_name"]
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Input List"
    ws.append([show] + [None]*6)
    ws.append([f"{venue_label(spec) or spec.get('console_label','')} · {spec.get('show_date','')} · {spec.get('rev','')}"] + [None]*6)
    ws.append(["Ch", "Instrument", "Mic / DI", "Patch", "48V", "Stand", "Notes"])
    for c in ws[3]:
        c.font = Font(bold=True)
    red = Font(color="9B2222", bold=True)
    for ch in spec["channels"]:
        ws.append([ch["ch"], ch.get("instrument") or ch["name"], ch["mic"], patch_label(ch),
                   "✓" if ch.get("phantom") else None, ch.get("stand", "—"), flag_notes(ch)])
        if ch.get("ribbon"):
            ws[ws.max_row][6].font = red
    ws[1][0].font = Font(bold=True, size=14); ws[2][0].font = Font(italic=True, size=10)
    for i, w in enumerate([5, 16, 18, 10, 5, 8, 70], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=4):
        row[6].alignment = Alignment(wrap_text=True, vertical="top")

    def aux_sheet(title, headers, rows):
        s = wb.create_sheet(title)
        s.append(headers)
        for c in s[1]:
            c.font = Font(bold=True)
        for r in rows:
            s.append(r)
        for i, w in enumerate([14, 26, 60][:len(headers)], 1):
            s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    mons = spec.get("monitors")
    if mons:
        rows = [([m.get("mix", ""), m.get("who", ""), " · ".join(x for x in [m.get("type", ""), m.get("note", "")] if x)]
                 if isinstance(m, dict) else ["", "", str(m)]) for m in mons]
        aux_sheet("Monitors", ["Mix", "Who", "Type / Notes"], rows)
    revs = spec.get("reverbs")
    if revs:
        rows = []
        for r in revs:
            if isinstance(r, dict):
                rows.append([r.get("role", r.get("bus", "")), r.get("preset", ""),
                             r.get("settings", ""), r.get("plugin_eq", ""),
                             " · ".join(x for x in [r.get("why", ""), r.get("note", "")] if x)])
            else:
                rows.append(["", str(r), "", "", ""])
        if spec.get("reverb_pairing"):
            rows.append(["TOGETHER", "", "", "", spec["reverb_pairing"]])
        s = wb.create_sheet("Reverbs")
        s.append(["Role / Bus", "Preset (verbatim from KB)", "Settings", "In-plugin EQ", "Why / How to use"])
        for c in s[1]:
            c.font = Font(bold=True)
        for r in rows:
            s.append(r)
        for i, w in enumerate([12, 30, 34, 30, 60], 1):
            s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
        for row in s.iter_rows(min_row=2):
            for c in row[2:]:
                c.alignment = Alignment(wrap_text=True, vertical="top")

    p = os.path.join(folder, f"{show} - Input List.xlsx"); wb.save(p); return p

# ---------------------------------------------------------------- 3. Show Packet PDF
def build_packet_pdf(spec, folder, packet_builder_path):
    s = importlib.util.spec_from_file_location("pb", packet_builder_path)
    pb = importlib.util.module_from_spec(s); s.loader.exec_module(pb)
    accent = {"DRUMS": pb.DRUMS_BAR, "RHYTHM": pb.GUITAR_BAR, "BASS": pb.BASS_BAR,
              "GUITAR": pb.GUITAR_BAR, "KEYS": pb.KEYS_BAR, "PIANO": pb.PIANO_BAR,
              "STRINGS": pb.STRINGS_BAR, "HORNS": pb.HORNS_BAR, "VOCALS": pb.VOCALS_BAR,
              "AMBIENT": pb.AMBIENT_BAR}
    il, eqc = [], []
    for ch in spec["channels"]:
        sec = ch.get("section", "SPARE")
        il.append(dict(ch=ch["ch"], name=ch["name"], mic=ch["mic"], section=sec,
                       patch=patch_label(ch), phantom_48v=bool(ch.get("phantom")),
                       stand=ch.get("stand", "—"), notes=flag_notes(ch) or ""))
        rows = [dict(band="LC", freq=fmt_freq(ch.get("hpf", 20)), type="LC", gain="—",
                     q="—", notes="High-pass")]
        bb = bands_by_num(ch)
        for n in (4, 3, 2, 1):
            b = bb[n]
            if not b:
                rows.append(dict(band=str(n), freq="—", type="OFF", gain="—", q="—", notes="Flat")); continue
            note = ""
            d = b.get("deq")
            if d:
                note = f"DYNAMIC: thr={d['thr']:g}dB atk={d['atk_ms']:g}ms rel={d['rel_ms']:g}ms — bites only on peaks"
            rows.append(dict(band=str(n), freq=fmt_freq(b["freq"]),
                             type=("Shelf" if str(b["type"]).upper() == "SHELF" else "Bell"),
                             gain=f"{b['gain']:+g} dB", q=f"{b['q']:g}", notes=note))
        lpf = ch.get("lpf")
        rows.append(dict(band="HC", freq=("—" if not lpf else fmt_freq(lpf)), type="HC",
                         gain="—", q="—", notes=("No LPF" if not lpf else "Low-pass")))
        eqc.append(dict(ch=ch["ch"], name=ch["name"], mic=ch["mic"], section=sec,
                        accent=accent.get(sec, pb.TBD_BAR), mic_notes=ch.get("mic_notes", ""),
                        bands=rows, summary=ch.get("eq_summary", "")))
    console = "digico" if "225" in spec.get("console_label", "") or "digico" in spec.get("console_label","").lower() else "wing"
    show_data = dict(show_name=spec["show_name"], venue=venue_label(spec) or spec.get("venue", ""),
                     date=spec.get("show_date", ""), console_label=spec.get("console_label", "DiGiCo Quantum 225"),
                     foh_engineer=spec.get("foh_engineer", "Brian Lloyd"),
                     mon_engineer=spec.get("mon_engineer", "TBD"), show_time=spec.get("show_time", "TBD"),
                     rev=spec.get("rev", "Rev 1.0"), channel_count=len(spec["channels"]),
                     style_note=spec.get("style_note", spec.get("room_context", "")))
    p = os.path.join(folder, f"{spec['show_name']} - Show Packet.pdf")
    pb.build_show_packet(p, show_data, il, eqc, console=console); return p

# ---------------------------------------------------------------- 4. EQ Rationale PDF
def build_rationale_pdf(spec, folder):
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                     KeepTogether, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    HEADER_BG = colors.HexColor("#1A1A2E"); SUBHEAD = colors.HexColor("#0F3460")
    ACCENT = colors.HexColor("#E94560"); CHANGE = colors.HexColor("#FFF3CD")
    DECIDE = colors.HexColor("#E8F0E8")
    SECCOL = {"DRUMS": colors.HexColor("#D4E8D4"), "BASS": colors.HexColor("#D4D4E8"),
              "RHYTHM": colors.HexColor("#E8E4D4"), "GUITAR": colors.HexColor("#E8E4D4"),
              "KEYS": colors.HexColor("#E8D4E8"), "PIANO": colors.HexColor("#E8D4E8"),
              "STRINGS": colors.HexColor("#E8EEF7"), "HORNS": colors.HexColor("#FFE4B5"),
              "VOCALS": colors.HexColor("#E8D4D4"), "AMBIENT": colors.HexColor("#C7D2FE")}
    st = getSampleStyleSheet()
    H1 = ParagraphStyle('H1', parent=st['Title'], textColor=colors.white, fontSize=20, leading=24, alignment=TA_LEFT)
    SUB = ParagraphStyle('SUB', parent=st['Normal'], textColor=colors.white, fontSize=10, leading=13)
    SEC = ParagraphStyle('SEC', parent=st['Heading2'], textColor=colors.white, fontSize=12, leading=14)
    CHH = ParagraphStyle('CHH', parent=st['Heading3'], textColor=HEADER_BG, fontSize=10.5, leading=12, spaceAfter=1)
    EQ = ParagraphStyle('EQ', parent=st['Normal'], fontName='Courier-Bold', fontSize=8.2, leading=10, textColor=SUBHEAD)
    WHY = ParagraphStyle('WHY', parent=st['Normal'], fontSize=8.6, leading=11, textColor=colors.HexColor("#222222"))
    BODY = ParagraphStyle('BODY', parent=st['Normal'], fontSize=9, leading=12.5)
    p = os.path.join(folder, f"{spec['show_name']} - FOH EQ Reasoning.pdf")
    doc = SimpleDocTemplate(p, pagesize=landscape(letter), leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.45*inch, bottomMargin=0.45*inch)
    W = doc.width; els = []
    banner = Table([[Paragraph(f"{esc(spec['show_name'])} — FOH EQ Rationale", H1)],
                    [Paragraph(f"{esc(venue_label(spec) or spec.get('venue',''))} &middot; {esc(spec.get('console_label',''))} &middot; {esc(spec.get('show_date',''))} &middot; {esc(spec.get('rev',''))}", SUB)]], colWidths=[W])
    banner.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HEADER_BG),('LEFTPADDING',(0,0),(-1,-1),12),
                                ('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(0,0),10),
                                ('BOTTOMPADDING',(0,-1),(-1,-1),9),('TOPPADDING',(0,1),(-1,1),0)]))
    els += [banner, Spacer(1,8)]
    ctx = []
    if spec.get("artist_profile"): ctx.append(f"<b>Artist.</b> {esc(spec['artist_profile'])}")
    if spec.get("room_context"): ctx.append(f"<b>Room.</b> {esc(spec['room_context'])}")
    if spec.get("research_summary"): ctx.append(f"<b>Research.</b> {esc(spec['research_summary'])}")
    if spec.get("reverb_note"): ctx.append(f"<b>Reverb.</b> {esc(spec['reverb_note'])}")
    if spec.get("monitors"):
        ml = " &nbsp;&middot;&nbsp; ".join(
            (f"{esc(m.get('mix',''))} {esc(m.get('who',''))} ({esc(m.get('type',''))})".strip()
             if isinstance(m, dict) else esc(str(m))) for m in spec["monitors"])
        ctx.append(f"<b>Monitors.</b> {ml}")
    if ctx:
        els += [Paragraph("<br/><br/>".join(ctx), BODY), Spacer(1,6)]
    def note_box(title, items, bg, border):
        rows = [[Paragraph(f"<b>{title}</b>", CHH)]]
        for c in items:
            rows.append([Paragraph(f"&bull; {esc(c)}", WHY)])
        box = Table(rows, colWidths=[W])
        box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),0.5,border),
                                 ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
                                 ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        return box
    if spec.get("changes"):
        els += [note_box("What changed from the KB default / prior rev — and why",
                         spec["changes"], CHANGE, ACCENT), Spacer(1,8)]
    if spec.get("decisions"):
        els += [note_box("Question round — what was asked, what Brian decided",
                         spec["decisions"], DECIDE, SUBHEAD), Spacer(1,8)]
    # Reverb block — Seventh Heaven Pro suggestions (required every show):
    # preset (verbatim), settings, in-plugin EQ, why, and the pairing note.
    revs = spec.get("reverbs")
    if revs:
        items = []
        for r in revs:
            if isinstance(r, dict):
                seg = (f"<b>{esc(str(r.get('role', r.get('bus',''))).upper())}</b> — "
                       f"<b>{esc(r.get('preset',''))}</b>")
                for k, lbl in (("settings", "Settings"), ("plugin_eq", "In-plugin EQ"),
                               ("why", "Why"), ("note", "Note")):
                    if r.get(k):
                        seg += f" &nbsp;|&nbsp; {lbl}: {esc(r[k])}"
                items.append(seg)
            else:
                items.append(esc(str(r)))
        if spec.get("reverb_pairing"):
            items.append(f"<b>USING THEM TOGETHER</b> — {esc(spec['reverb_pairing'])}")
        rows = [[Paragraph("<b>Reverb — Seventh Heaven Pro (100% wet returns)</b>", CHH)]]
        for it in items:
            rows.append([Paragraph(f"&bull; {it}", WHY)])
        box = Table(rows, colWidths=[W])
        box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#EAF2FA")),
                                 ('BOX',(0,0),(-1,-1),0.5,SUBHEAD),
                                 ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
                                 ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        els += [box, Spacer(1,8)]
    def section_bar(title):
        t = Table([[Paragraph(title, SEC)]], colWidths=[W])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),SUBHEAD),('LEFTPADDING',(0,0),(-1,-1),10),
                               ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        return t
    def chan_block(ch):
        rowcol = SECCOL.get(ch.get("section","").upper(), colors.HexColor("#EEEEEE"))
        bb = bands_by_num(ch); parts = []
        for n in (4,3,2,1):
            b = bb[n]
            if not b: parts.append(f"B{n} flat"); continue
            seg = f"B{n} {b['gain']:+g}@{fmt_freq(b['freq'])} Q{b['q']:g} {('SHELF' if str(b['type']).upper()=='SHELF' else 'BELL')}"
            if b.get("deq"): seg += " +DEQ"
            parts.append(seg)
        lpf = ch.get("lpf")
        eqline = f"HPF {ch.get('hpf',20):g} | LPF {'off' if not lpf else f'{lpf:g}'} || " + " &nbsp; ".join(parts)
        head = f"<b>Ch {ch['ch']} &nbsp;|&nbsp; {esc(ch['name'])}</b> &middot; {esc(ch['mic'])}"
        if ch.get("ribbon"): head += f" &nbsp;<font color='#9B2222'><b>{RIBBON_FLAG}</b></font>"
        if ch.get("tour"): head += f" &nbsp;<font color='#8a6d00'><b>{TOUR_FLAG}</b></font>"
        inner = [[Paragraph(head, CHH)], [Paragraph(eqline, EQ)]]
        if ch.get("mic_notes"): inner.append([Paragraph(f"<i>{esc(ch['mic_notes'])}</i>", WHY)])
        if ch.get("eq_summary"): inner.append([Paragraph(esc(ch["eq_summary"]), WHY)])
        t = Table(inner, colWidths=[W])
        t.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
                               ('TOPPADDING',(0,0),(0,0),4),('BOTTOMPADDING',(0,-1),(-1,-1),5),
                               ('TOPPADDING',(0,1),(-1,-1),1),('BACKGROUND',(0,0),(-1,-1),rowcol),
                               ('LINEBELOW',(0,-1),(-1,-1),0.4,colors.HexColor("#cccccc"))]))
        return KeepTogether([t, Spacer(1,3)])
    last_sec = None
    for ch in spec["channels"]:
        sec = ch.get("section","").upper()
        if sec != last_sec:
            els += [section_bar(sec), Spacer(1,3)]; last_sec = sec
        els.append(chan_block(ch))
    els += [Spacer(1,6), HRFlowable(width="100%", thickness=0.5, color=ACCENT), Spacer(1,3),
            Paragraph("<font size=7 color='#777777'>Deep-research pass — values reasoned from mic behavior, instrument, genre, the artist's references, and the room. Informed starting points, not gospel; trust your ears at soundcheck.</font>", BODY)]
    doc.build(els); return p

# ---------------------------------------------------------------- 5. MASTER PDF
def build_master_pdf(spec, folder, pdf_paths):
    """One giant PDF with everything (Brian, 2026-07-08): Show Packet, then the
    EQ Rationale, then any band-provided stage plot / rider PDF found in the
    show folder. The individual files still ship — this is additive."""
    from pypdf import PdfWriter
    show = spec["show_name"]
    parts = list(pdf_paths)
    for tail in (" - Stage Plot.pdf", " - Rider.pdf"):
        extra = os.path.join(folder, f"{show}{tail}")
        if os.path.exists(extra):
            parts.append(extra)
    w = PdfWriter()
    for p in parts:
        w.append(p)
    out = os.path.join(folder, f"{show} - MASTER.pdf")
    with open(out, "wb") as f:
        w.write(f)
    return out

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--packet-builder",
                    default=os.path.expanduser("~/Documents/Claude/audio/show-packet-builder-template.py"))
    a = ap.parse_args()
    spec = load_spec(a.spec)
    errors, warnings = validate_spec(spec)
    for w in warnings:
        print("  spec warn:", w)
    if errors:
        for e in errors:
            print("  spec ERROR:", e)
        raise SystemExit(f"spec validation failed — {len(errors)} error(s), nothing written")
    print(f"spec validation PASS — {len(spec['channels'])} channels, {len(warnings)} warnings")
    os.makedirs(a.out, exist_ok=True)
    md = write_md(spec, a.out)
    lint_md(md)
    packet_pdf = build_packet_pdf(spec, a.out, a.packet_builder)
    rationale_pdf = build_rationale_pdf(spec, a.out)
    made = [md, write_xlsx(spec, a.out), packet_pdf, rationale_pdf,
            build_master_pdf(spec, a.out, [packet_pdf, rationale_pdf])]
    for m in made:
        print("WROTE", m)
    try:
        sys.path.insert(0, os.path.expanduser("~/Documents/Claude/audio/_shared"))
        import show_status
        show_status.stamp(a.out, "packet_built",
                          note=f"{len(spec['channels'])} channels, full packet")
    except ImportError:
        pass  # status stamp is best-effort — never blocks a build
    print("\nNEXT: run the venue .ses patcher on the .md, then verify on the console.")

if __name__ == "__main__":
    main()
