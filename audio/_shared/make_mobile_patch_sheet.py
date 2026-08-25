#!/usr/bin/env python3
"""
make_mobile_patch_sheet.py — phone-first patch sheet for the stage crew.

Reads a show's deep-build spec.json and writes TWO deliverables next to it:

  <Show> - Patch Sheet (Phone).html   self-contained, offline, tap-to-check-off
  <Show> - Patch Sheet (Phone).pdf    phone-shaped page, texts/AirDrops cleanly

This is a PATCH sheet, not an EQ document: channel, instrument, mic/DI, patch,
48V, stand, and the stage-critical flags. No EQ values — the crew patching the
stage doesn't need them and they make the page unreadable on a 6" screen.

Everything is derived from the spec, so it cannot drift from the packet. Run it
again after any spec change.

    python3 make_mobile_patch_sheet.py --spec "<show folder>/<Show>.spec.json"

Why HTML as the primary: it reflows to any phone, supports dark mode for a night
show, works with no signal once loaded, and can be saved to the home screen.
The PDF exists because texting a PDF is the lowest-friction way to hand it to a
crew that hasn't got the HTML.

PDF engine note (2026-08-08): reportlab, not weasyprint. WeasyPrint needs pango,
which isn't installed on Brian's Mac — `brew install pango` would fix it. Per
CLAUDE.md, reportlab is the sanctioned engine for standalone tool PDFs like this
one; the show packet itself is unaffected.
"""

import argparse
import html
import json
import os
import re
import sys

# Section accents. Row tints are the locked Input List palette from CLAUDE.md;
# the stripe/heading colours are darker relatives of the same hues so they hold
# up as text on both light and dark backgrounds.
SECTIONS = {
    "DRUMS":   {"label": "DRUMS / PERC",   "tint": "#FEF3C7", "head": "#FDE68A", "ink": "#92400E", "dark": "#FBBF24"},
    "BASS":    {"label": "BASS",           "tint": "#DCFCE7", "head": "#BBF7D0", "ink": "#065F46", "dark": "#34D399"},
    "RHYTHM":  {"label": "RHYTHM",         "tint": "#DCFCE7", "head": "#BBF7D0", "ink": "#065F46", "dark": "#34D399"},
    "GUITAR":  {"label": "GUITAR",         "tint": "#D1FAE5", "head": "#A7F3D0", "ink": "#047857", "dark": "#6EE7B7"},
    "PIANO":   {"label": "PIANO",          "tint": "#FCE7F3", "head": "#FBCFE8", "ink": "#9D174D", "dark": "#F472B6"},
    "KEYS":    {"label": "KEYS",           "tint": "#EDE9FE", "head": "#DDD6FE", "ink": "#5B21B6", "dark": "#A78BFA"},
    "STRINGS": {"label": "STRINGS",        "tint": "#DBEAFE", "head": "#BFDBFE", "ink": "#1E40AF", "dark": "#60A5FA"},
    "HORNS":   {"label": "HORNS / WINDS",  "tint": "#FFEDD5", "head": "#FCD9B4", "ink": "#9A3412", "dark": "#FB923C"},
    "VOCALS":  {"label": "VOCALS",         "tint": "#EDE9FE", "head": "#DDD6FE", "ink": "#4338CA", "dark": "#818CF8"},
    "AMBIENT": {"label": "AMBIENT / FOH",  "tint": "#E0E7FF", "head": "#C7D2FE", "ink": "#3730A3", "dark": "#818CF8"},
    "SPARE":   {"label": "SPARE",          "tint": "#F3F4F6", "head": "#E5E7EB", "ink": "#374151", "dark": "#9CA3AF"},
}
FALLBACK = SECTIONS["SPARE"]


def sec(name):
    return SECTIONS.get(str(name or "").upper(), FALLBACK)


def flags_for(ch):
    """Stage-critical flags, derived from the channel rather than hand-listed.

    Only things that change what the crew physically DOES go here. An EQ value
    never does; a polarity invert, phantom power or a dead-to-the-PA channel
    always does."""
    out = []
    # Scan the ACTIONABLE `notes` field only — never `mic_notes`. mic_notes is
    # desk-side reasoning and routinely describes what a DIFFERENT channel does
    # ("ch 4 is polarity inverted against this channel"), which produced a
    # false POLARITY INVERT flag on the snare top. On a patch sheet that is not
    # a cosmetic bug: the crew would have flipped a channel that must not be
    # flipped. Fixed 2026-08-08 during the first run of this tool.
    notes = str(ch.get("notes") or "")
    low = notes.lower()

    if ch.get("ribbon"):
        out.append(("NO 48V — RIBBON", "danger"))
    elif ch.get("phantom"):
        out.append(("48V", "power"))

    if ch.get("tour"):
        out.append(("TOUR — ARTIST GEAR", "tour"))
    if "polarity invert" in low:
        out.append(("POLARITY INVERT", "danger"))
    if "muted from the mains" in low or "muted from mains" in low:
        out.append(("MUTED FROM MAINS", "danger"))
    if "stereo channel" in low or "stereo pair with" in low or "(pair)" in str(ch.get("mic") or "").lower():
        out.append(("STEREO", "info"))
    if "windscreen" in low:
        out.append(("WINDSCREEN", "info"))
    m = re.search(r"wireless\s*([1-4])", str(ch.get("mic") or ""), re.I)
    if m:
        out.append(("WIRELESS " + m.group(1), "info"))
    if "load-in flag" in low or "⚑" in notes:
        out.append(("CONFIRM AT LOAD-IN", "tour"))
    return out


def titles(ch):
    """(headline, subtitle) for a channel card.

    The headline is the FADER LABEL (`name`), because that is what is printed on
    the console surface and on the band's own sheet — and on a vocal channel it
    is the singer's NAME, which is the single most useful thing on a patch sheet:
    the crew is handing a mic to Aretha, not to "Vocal (female)". The instrument
    becomes the subtitle where it adds something the label doesn't already say.
    """
    name = str(ch.get("name") or "").strip()
    inst = str(ch.get("instrument") or "").strip()
    if not name:
        return inst, ""
    if not inst:
        return name, ""
    n, i = name.lower(), inst.lower()
    # "Kick In" / "Kick Drum (inside)" both earn their place; "Click" / "Click
    # Reference" does not — drop the subtitle when it just restates the label.
    if i == n or i.startswith(n) or n.startswith(i):
        return name, ""
    return name, inst


def crew_note(ch):
    """The one line of the notes field a patcher actually needs.

    The packet's notes are written for Brian at the desk and run long. Here we
    keep only sentences that describe a physical action or a hazard, so the card
    stays readable at arm's length on a dark stage."""
    notes = str(ch.get("notes") or "").replace("⚠", "").replace("⚑", "").strip()
    if not notes:
        return ""
    keep = []
    for s in re.split(r"(?<=[.!])\s+", notes):
        t = s.strip()
        if not t:
            continue
        l = t.lower()
        # drop paperwork housekeeping — renumbering history, rev provenance,
        # and anything that's purely a desk-side EQ remark
        if any(k in l for k in ("renumbered", "rev 1's", "not re-asked",
                                "not re-litigated", "carried, not",
                                "mic changed from", "channel repurposed",
                                "source changed from", "new channel —")):
            continue
        if any(k in l for k in ("halve b3", "so halve", "b3 to", "alternates,",
                                "if baritone", "if tenor")):
            continue
        keep.append(t)
    # Never truncate mid-sentence — a note that stops at "Move the " reads as a
    # broken document, and a crew member can't tell whether they lost something
    # that mattered. Add whole sentences until the budget is spent, then stop.
    out, budget = [], 300
    for t in keep:
        if out and len(" ".join(out)) + 1 + len(t) > budget:
            break
        out.append(t)
    return " ".join(out)


def build_html(spec):
    show = spec.get("show_name", "Show")
    rows = []
    last = None
    for ch in spec.get("channels", []):
        s = sec(ch.get("section"))
        if ch.get("section") != last:
            rows.append({"kind": "head", "s": s})
            last = ch.get("section")
        rows.append({"kind": "row", "ch": ch, "s": s})

    chans = [c for c in spec.get("channels", [])]
    n_total = len(chans)
    phantom = [c["ch"] for c in chans if c.get("phantom")]
    inverts = [c["ch"] for c in chans
               if "polarity invert" in str(c.get("notes", "")).lower()]
    ribbons = [c["ch"] for c in chans if c.get("ribbon")]
    tours = [c["ch"] for c in chans if c.get("tour")]

    def alert_block():
        items = []
        if ribbons:
            items.append(('danger', 'RIBBON — NO 48V',
                          "Ch " + ", ".join(str(x) for x in ribbons) +
                          ". Phantom power destroys the ribbon. Check before you patch, not after."))
        if inverts:
            items.append(('danger', 'POLARITY INVERT',
                          "Ch " + ", ".join(str(x) for x in inverts) +
                          ". Set on the desk, not at the mic. If it's missed, these channels "
                          "cancel against the ones they're paired with."))
        if phantom:
            items.append(('power', '48V ON THESE ONLY',
                          "Ch " + ", ".join(str(x) for x in phantom) +
                          ". Everything else is a dynamic or a line feed — leave phantom off."))
        if tours:
            items.append(('tour', 'ARTIST-PROVIDED GEAR',
                          "Ch " + ", ".join(str(x) for x in tours) + ". Confirm at load-in."))
        if not items:
            return ""
        out = ['<section class="alerts">']
        for kind, title, body in items:
            out.append(f'<div class="alert {kind}"><b>{html.escape(title)}</b>'
                       f'<span>{html.escape(body)}</span></div>')
        out.append('</section>')
        return "\n".join(out)

    css_sections = "\n".join(
        f'.s-{k} {{ --tint:{v["tint"]}; --head:{v["head"]}; --ink:{v["ink"]}; --dk:{v["dark"]}; }}'
        for k, v in SECTIONS.items())

    body = []
    for r in rows:
        s = r["s"]
        key = next((k for k, v in SECTIONS.items() if v is s), "SPARE")
        if r["kind"] == "head":
            body.append(f'<h2 class="sechead s-{key}">{html.escape(s["label"])}</h2>')
            continue
        ch = r["ch"]
        fl = flags_for(ch)
        chips = "".join(
            f'<i class="chip c-{k}">{html.escape(t)}</i>' for t, k in fl)
        note = crew_note(ch)
        head, sub = titles(ch)
        patch = html.escape(str(ch.get("patch") or f"Local {ch['ch']}"))
        stand = html.escape(str(ch.get("stand") or "—"))
        body.append(f'''<article class="card s-{key}" data-ch="{ch['ch']}" data-phantom="{'1' if ch.get('phantom') else '0'}">
  <div class="num">{ch['ch']}</div>
  <div class="main">
    <div class="inst">{html.escape(head)}</div>
    {f'<div class="sub">{html.escape(sub)}</div>' if sub else ''}
    <div class="mic">{html.escape(str(ch.get('mic') or ''))}</div>
    <div class="meta"><span class="patch">{patch}</span><span class="stand">Stand: {stand}</span></div>
    {f'<div class="chips">{chips}</div>' if chips else ''}
    {f'<div class="note">{html.escape(note)}</div>' if note else ''}
  </div>
  <div class="tick" aria-hidden="true"></div>
</article>''')

    zones = ("Split patch zones: <b>R-1…R-16</b> red · <b>G-1…G-12</b> green · "
             "<b>B-1…B-12</b> blue · <b>O-1…O-12</b> orange · <b>WIRELESS</b> for the handhelds.")

    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1A3A5C" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b1220" media="(prefers-color-scheme: dark)">
<title>{html.escape(show)} — Patch Sheet</title>
<style>
*{{box-sizing:border-box}}
:root{{
  --bg:#f6f7f9; --fg:#111827; --dim:#6b7280; --card:#fff; --line:#e5e7eb;
  --nav:#1A3A5C; --accent:#2E6DA4; --ok:#065F46;
}}
@media (prefers-color-scheme:dark){{
  :root{{ --bg:#0b1220; --fg:#e9edf3; --dim:#94a3b8; --card:#151d2b; --line:#243247;
          --nav:#0e1729; --accent:#5b9bd5; --ok:#34D399; }}
}}
html,body{{margin:0;padding:0;background:var(--bg);color:var(--fg);
  font:400 17px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-text-size-adjust:100%}}
header{{position:sticky;top:0;z-index:20;background:var(--nav);color:#fff;
  padding:calc(env(safe-area-inset-top) + 10px) 14px 10px;box-shadow:0 2px 10px rgba(0,0,0,.25)}}
header h1{{margin:0;font-size:21px;font-weight:700;letter-spacing:.2px}}
header .sub{{margin-top:3px;font-size:13px;opacity:.85}}
.bar{{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}}
.bar button{{flex:1 1 auto;min-height:40px;min-width:76px;border:0;border-radius:9px;
  background:rgba(255,255,255,.14);color:#fff;font:600 14px/1 inherit;padding:0 10px}}
.bar button[aria-pressed="true"]{{background:#fff;color:var(--nav)}}
.prog{{margin-top:8px;font-size:13px;opacity:.9;display:flex;align-items:center;gap:8px}}
.prog .track{{flex:1;height:6px;border-radius:99px;background:rgba(255,255,255,.2);overflow:hidden}}
.prog .fill{{height:100%;width:0;background:#fff;transition:width .2s}}
.zones{{padding:10px 14px;font-size:13px;color:var(--dim);border-bottom:1px solid var(--line)}}
.alerts{{padding:12px 12px 2px;display:grid;gap:8px}}
.alert{{border-radius:11px;padding:10px 12px;font-size:14.5px;display:grid;gap:2px;
  border-left:5px solid currentColor}}
.alert b{{font-size:13px;letter-spacing:.5px}}
.alert span{{color:var(--fg);opacity:.9}}
.alert.danger{{color:#B91C1C;background:#FEE2E2}}
.alert.power{{color:#065F46;background:#D1FAE5}}
.alert.tour{{color:#92400E;background:#FFF3CD}}
@media (prefers-color-scheme:dark){{
  .alert.danger{{color:#FCA5A5;background:#2a1416}} .alert.power{{color:#6EE7B7;background:#0e2620}}
  .alert.tour{{color:#FCD34D;background:#2a2110}}
}}
main{{padding:8px 12px calc(env(safe-area-inset-bottom) + 28px)}}
{css_sections}
.sechead{{position:sticky;top:0;z-index:10;margin:16px 0 8px;padding:8px 12px;border-radius:9px;
  font-size:13.5px;font-weight:800;letter-spacing:1px;background:var(--head);color:var(--ink)}}
@media (prefers-color-scheme:dark){{ .sechead{{background:#1c2942;color:var(--dk)}} }}
.card{{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
  border-left:6px solid var(--head);border-radius:13px;padding:12px;margin:0 0 8px;min-height:76px;
  -webkit-tap-highlight-color:transparent;cursor:pointer}}
@media (prefers-color-scheme:dark){{ .card{{border-left-color:var(--dk)}} }}
.num{{flex:0 0 46px;text-align:center;font:800 27px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:var(--ink);padding-top:2px}}
@media (prefers-color-scheme:dark){{ .num{{color:var(--dk)}} }}
.main{{flex:1;min-width:0}}
.inst{{font-weight:700;font-size:18px;line-height:1.25}}
.sub{{margin-top:1px;font-size:14.5px;color:var(--dim)}}
.mic{{margin-top:3px;font-size:16px;color:var(--fg);opacity:.92}}
.meta{{margin-top:6px;display:flex;gap:10px;flex-wrap:wrap;font-size:14px;color:var(--dim)}}
.meta .patch{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-weight:600;color:var(--accent)}}
.chips{{margin-top:7px;display:flex;gap:5px;flex-wrap:wrap}}
.chip{{font-style:normal;font-size:11.5px;font-weight:800;letter-spacing:.5px;padding:4px 8px;border-radius:99px;white-space:nowrap}}
.c-power{{background:#D1FAE5;color:#065F46}} .c-danger{{background:#FEE2E2;color:#B91C1C}}
.c-tour{{background:#FFF3CD;color:#92400E}} .c-info{{background:#E0E7FF;color:#3730A3}}
@media (prefers-color-scheme:dark){{
  .c-power{{background:#0e2620;color:#6EE7B7}} .c-danger{{background:#2a1416;color:#FCA5A5}}
  .c-tour{{background:#2a2110;color:#FCD34D}} .c-info{{background:#18213a;color:#A5B4FC}}
}}
.note{{margin-top:7px;font-size:13.5px;color:var(--dim);line-height:1.35}}
.tick{{flex:0 0 30px;height:30px;border-radius:50%;border:2px solid var(--line);margin-top:2px;position:relative}}
.card.done{{opacity:.5}}
.card.done .tick{{background:var(--ok);border-color:var(--ok)}}
.card.done .tick:after{{content:"";position:absolute;left:9px;top:4px;width:8px;height:15px;
  border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg)}}
.card.hide{{display:none}}
footer{{padding:6px 14px 30px;font-size:12.5px;color:var(--dim);text-align:center}}
</style></head><body>
<header>
  <h1>{html.escape(show)} — Patch</h1>
  <div class="sub">{html.escape(str(spec.get('venue_label','')))} · {html.escape(str(spec.get('show_date','')))} · {html.escape(str(spec.get('show_time','')))} · {n_total} ch</div>
  <div class="bar">
    <button id="f-all" aria-pressed="true">All</button>
    <button id="f-todo" aria-pressed="false">To do</button>
    <button id="f-48v" aria-pressed="false">48V only</button>
    <button id="reset">Reset</button>
  </div>
  <div class="prog"><span id="count">0 / {n_total}</span><span class="track"><span class="fill" id="fill"></span></span></div>
</header>
<div class="zones">{zones}</div>
{alert_block()}
<main id="list">
{chr(10).join(body)}
</main>
<footer>Tap a channel to check it off — saved on this phone only.<br>
Generated from {html.escape(show)}.spec.json · {html.escape(str(spec.get('rev','')))}</footer>
<script>
(function(){{
  var KEY = 'patch:' + {json.dumps(show)};
  var done = {{}};
  try {{ done = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{ done = {{}}; }}
  var cards = [].slice.call(document.querySelectorAll('.card'));
  var total = cards.length, mode = 'all';
  function save(){{ try {{ localStorage.setItem(KEY, JSON.stringify(done)); }} catch(e) {{}} }}
  function paint(){{
    var n = 0;
    cards.forEach(function(c){{
      var id = c.dataset.ch, on = !!done[id];
      c.classList.toggle('done', on);
      if (on) n++;
      var hide = (mode === 'todo' && on) || (mode === '48v' && c.dataset.phantom !== '1');
      c.classList.toggle('hide', hide);
    }});
    document.getElementById('count').textContent = n + ' / ' + total;
    document.getElementById('fill').style.width = (total ? (n / total * 100) : 0) + '%';
  }}
  cards.forEach(function(c){{
    c.addEventListener('click', function(){{
      var id = c.dataset.ch;
      if (done[id]) {{ delete done[id]; }} else {{ done[id] = 1; }}
      save(); paint();
      if (navigator.vibrate) navigator.vibrate(8);
    }});
  }});
  function setMode(m, btn){{
    mode = m;
    ['f-all','f-todo','f-48v'].forEach(function(i){{
      document.getElementById(i).setAttribute('aria-pressed', i === btn ? 'true' : 'false');
    }});
    paint();
  }}
  document.getElementById('f-all').onclick  = function(){{ setMode('all','f-all'); }};
  document.getElementById('f-todo').onclick = function(){{ setMode('todo','f-todo'); }};
  document.getElementById('f-48v').onclick  = function(){{ setMode('48v','f-48v'); }};
  document.getElementById('reset').onclick  = function(){{
    if (confirm('Clear every check mark?')) {{ done = {{}}; save(); paint(); }}
  }};
  paint();
}})();
</script>
</body></html>
'''


def build_pdf(spec, path):
    """Phone-shaped PDF — a tall narrow page so it fills an iPhone screen with
    no pinch-zooming, rather than an A4 page shrunk to 30%."""
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas as rl_canvas

    PW, PH = 3.9 * inch, 8.3 * inch          # ~ iPhone aspect
    M = 0.22 * inch
    c = rl_canvas.Canvas(path, pagesize=(PW, PH))
    c.setTitle(f"{spec.get('show_name','Show')} — Patch Sheet (Phone)")

    y = [PH - M]

    def newpage():
        c.showPage()
        y[0] = PH - M

    def need(h):
        if y[0] - h < M + 0.18 * inch:
            newpage()

    def hdr():
        h = 0.62 * inch
        c.setFillColor(HexColor("#1A3A5C"))
        c.rect(0, PH - h, PW, h, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(M, PH - 0.26 * inch, f"{spec.get('show_name','')} — PATCH")
        c.setFont("Helvetica", 7.4)
        c.drawString(M, PH - 0.40 * inch, f"{spec.get('venue_label','')} · {spec.get('show_date','')}")
        c.drawString(M, PH - 0.51 * inch,
                     f"{spec.get('show_time','')} · {len(spec.get('channels', []))} channels")
        y[0] = PH - h - 0.14 * inch

    hdr()

    chans = spec.get("channels", [])
    phantom = [str(x["ch"]) for x in chans if x.get("phantom")]
    inverts = [str(x["ch"]) for x in chans
               if "polarity invert" in str(x.get("notes", "")).lower()]
    ribbons = [str(x["ch"]) for x in chans if x.get("ribbon")]

    for title, body, bg, ink in [
        ("RIBBON — NO 48V", ", ".join(ribbons), "#FEE2E2", "#B91C1C") if ribbons else (None, None, None, None),
        ("POLARITY INVERT", ", ".join(inverts), "#FEE2E2", "#B91C1C") if inverts else (None, None, None, None),
        ("48V ON THESE ONLY", ", ".join(phantom), "#D1FAE5", "#065F46") if phantom else (None, None, None, None),
    ]:
        if not title:
            continue
        need(0.36 * inch)
        c.setFillColor(HexColor(bg))
        c.rect(M, y[0] - 0.32 * inch, PW - 2 * M, 0.32 * inch, stroke=0, fill=1)
        c.setFillColor(HexColor(ink))
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(M + 5, y[0] - 0.125 * inch, title)
        c.setFont("Helvetica", 8.4)
        c.drawString(M + 5, y[0] - 0.255 * inch, "Ch " + body)
        y[0] -= 0.40 * inch

    last = None
    for ch in chans:
        s = sec(ch.get("section"))
        if ch.get("section") != last:
            need(0.34 * inch + 0.62 * inch)   # header + one row: never orphan a bar
            c.setFillColor(HexColor(s["head"]))
            c.rect(M, y[0] - 0.20 * inch, PW - 2 * M, 0.20 * inch, stroke=0, fill=1)
            c.setFillColor(HexColor(s["ink"]))
            c.setFont("Helvetica-Bold", 7.6)
            c.drawString(M + 5, y[0] - 0.145 * inch, s["label"])
            y[0] -= 0.29 * inch
            last = ch.get("section")

        fl = flags_for(ch)
        chip_txt = "  ".join(t for t, _ in fl)
        head_t, sub_t = titles(ch)
        rowh = (0.50 * inch + (0.11 * inch if chip_txt else 0)
                + (0.115 * inch if sub_t else 0))
        need(rowh)
        top = y[0]
        c.setFillColor(HexColor(s["tint"]))
        c.rect(M, top - rowh + 0.04 * inch, PW - 2 * M, rowh - 0.05 * inch, stroke=0, fill=1)
        c.setFillColor(HexColor(s["ink"]))
        c.rect(M, top - rowh + 0.04 * inch, 0.035 * inch, rowh - 0.05 * inch, stroke=0, fill=1)

        c.setFillColor(HexColor("#111827"))
        c.setFont("Courier-Bold", 13)
        c.drawString(M + 0.10 * inch, top - 0.20 * inch, str(ch["ch"]))
        yy = top - 0.17 * inch
        c.setFont("Helvetica-Bold", 9.8)
        c.drawString(M + 0.44 * inch, yy, head_t[:32])
        if sub_t:
            yy -= 0.115 * inch
            c.setFont("Helvetica", 7.8)
            c.setFillColor(HexColor("#4b5563"))
            c.drawString(M + 0.44 * inch, yy, sub_t[:40])
            c.setFillColor(HexColor("#111827"))
        yy -= 0.13 * inch
        c.setFont("Helvetica", 8.4)
        c.drawString(M + 0.44 * inch, yy, str(ch.get("mic") or "")[:40])
        yy -= 0.12 * inch
        c.setFont("Helvetica", 7.4)
        c.setFillColor(HexColor("#374151"))
        c.drawString(M + 0.44 * inch, yy,
                     f"{ch.get('patch') or 'Local ' + str(ch['ch'])}   ·   Stand: {ch.get('stand') or '—'}")
        if chip_txt:
            yy -= 0.11 * inch
            c.setFont("Helvetica-Bold", 6.6)
            c.setFillColor(HexColor("#B91C1C" if any(k == "danger" for _, k in fl) else "#065F46"))
            c.drawString(M + 0.44 * inch, yy, chip_txt[:56])
        # empty box for writing the split-patch code in at load-in
        c.setStrokeColor(HexColor("#9CA3AF"))
        c.setLineWidth(0.5)
        c.rect(PW - M - 0.52 * inch, top - 0.40 * inch, 0.46 * inch, 0.26 * inch, stroke=1, fill=0)
        c.setFont("Helvetica", 5.4)
        c.setFillColor(HexColor("#6b7280"))
        c.drawCentredString(PW - M - 0.29 * inch, top - 0.13 * inch, "SPLIT")
        y[0] -= rowh

    need(0.3 * inch)
    c.setFont("Helvetica-Oblique", 6.4)
    c.setFillColor(HexColor("#6b7280"))
    c.drawString(M, M + 0.05 * inch,
                 f"Generated from {spec.get('show_name','')}.spec.json · {spec.get('rev','')}")
    c.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", default=None, help="output folder (default: alongside the spec)")
    a = ap.parse_args()

    with open(a.spec) as f:
        spec = json.load(f)
    outdir = a.out or os.path.dirname(os.path.abspath(a.spec))
    show = spec.get("show_name", "Show")

    hpath = os.path.join(outdir, f"{show} - Patch Sheet (Phone).html")
    with open(hpath, "w") as f:
        f.write(build_html(spec))
    print("WROTE", hpath)

    ppath = os.path.join(outdir, f"{show} - Patch Sheet (Phone).pdf")
    try:
        build_pdf(spec, ppath)
        print("WROTE", ppath)
    except Exception as e:
        print("PDF SKIPPED:", type(e).__name__, e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
