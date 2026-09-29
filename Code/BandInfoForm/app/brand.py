"""3CDC brand shell for band-facing email (brand rollout phase 2, 2026-09-29).

Every band email is still AUTHORED as plain text (the .md.j2 templates,
venue_email.py blocks, dayahead/finalize/booking_update bodies). This module
turns that text into branded HTML at send time, so no template has to change
and the plain text stays the single source of the words.

Colors, fonts, logos and addresses come from brand/brand.json. Nothing here
hardcodes a hex except the near-black text fallback used only when a venue's
own color can't hold contrast.

render_email(body, venue) -> html. Structure is read from the text itself:
  URL alone on a line      -> button
  ──── line                -> divider
  "Heading:" (short)       -> section heading; "Heading (note):" keeps the note
  "Label: value" run       -> two-column facts table (the block under the divider)
  "  4:00pm   Load-In"     -> schedule table
  "- item" / "  - item"    -> bullet; a short "Label:" lead is bolded
  indented other line      -> small note under the thing above it
  "Thanks," + last line    -> sign-off
"""
import base64
import html as _h
import json
import os
import re
from pathlib import Path

# brand/ sits beside this file both locally (app/brand) and on the VM, where
# deploy_app.command flattens app/ into /opt/band-advance (brand ships with it)
BRAND_DIR = Path(os.environ.get("ADVANCE_BRAND_DIR")
                 or Path(__file__).resolve().parent / "brand")
# Public base the email's <img> tags point at. Outlook strips data: URIs, so
# production mail must reference hosted files (served by app.py /brand/<file>).
LOGO_BASE = os.environ.get("ADVANCE_BRAND_URL", "https://advance.tinydoorstudios.com/brand/")
NEAR_BLACK = "#231F20"
WHITE = "#FFFFFF"

_brand = None


def brand():
    global _brand
    if _brand is None:
        _brand = json.loads((BRAND_DIR / "brand.json").read_text())
    return _brand


def venue_profile(venue):
    """The venue's brand entry, resolving aliases ("Zeigler Park"). None when
    the guide has no entry (Elm Street Plaza) -> corporate look."""
    b = brand()
    for name, v in b["venues"].items():
        if venue == name or venue in v.get("aliases", []):
            return dict(v, name=name)
    return None


# --- contrast (WCAG relative luminance) ------------------------------------

def _lum(hexc):
    r, g, b = (int(hexc.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def palette(venue):
    """accent = headings/links (>=3:1 on white, large text), button = bg+fg
    pair (>=4.5:1), rule = decorative bar (any venue color)."""
    b = brand()
    c = b["corporate"]["colors"]
    v = venue_profile(venue)
    prim = v["primary"]["hex"] if v else c["blue"]["hex"]
    sec = v["secondary"]["hex"] if v else c["red"]["hex"]
    charcoal = c["charcoal"]["hex"]
    accent = next((x for x in (prim, sec) if contrast(x, WHITE) >= 3), charcoal)
    # white text on a venue color first (a gray button with dark text reads
    # as disabled), then dark text, then charcoal as the last resort
    pairs = [(bg, WHITE) for bg in (prim, sec)] + [(bg, NEAR_BLACK) for bg in (prim, sec)]
    button = next(((bg, fg) for bg, fg in pairs if contrast(bg, fg) >= 4.5), (charcoal, WHITE))
    return {"primary": prim, "secondary": sec, "accent": accent,
            "button_bg": button[0], "button_fg": button[1],
            "text": b["corporate"]["text"],
            # brand gray #9D9FA2 is 2.6:1 on white, too faint for 12-13px copy
            "muted": charcoal}


_web = None


def web_theme():
    """{venue name or alias: theme} for the public form and thank-you page
    (brand rollout phase 3). "_default" is the corporate look, used before a
    venue is picked and for venues the guide doesn't cover."""
    global _web
    if _web is None:
        b = brand()
        out = {}
        corp = palette("")
        corp["logo"] = None
        out["_default"] = corp
        for name, v in b["venues"].items():
            th = palette(name)
            th["logo"] = f"/brand/{v['slug']}-typelogo.png"
            for key in [name] + v.get("aliases", []):
                out[key] = th
        _web = out
    return _web


def _logo_src(rel, embed):
    if embed:
        data = base64.b64encode((BRAND_DIR / rel).read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    return LOGO_BASE + rel.split("/", 1)[-1]


# --- text -> html -----------------------------------------------------------

URL_RE = re.compile(r"https?://\S+")
SCHED_RE = re.compile(r"^\s+(\d{1,2}(?::\d\d)?\s?[ap]m)\s{2,}(.+)$", re.I)
FACT_RE = re.compile(r"^([A-Z][\w /&'().-]{1,34}):\s+(\S.*)$")
BULLET_RE = re.compile(r"^\s*[-•]\s+(.*)$")


def _inline(text, pal):
    out, last = [], 0
    for m in URL_RE.finditer(text):
        out.append(_h.escape(text[last:m.start()]))
        u = m.group(0).rstrip(".,)")
        out.append(f'<a href="{_h.escape(u)}" style="color:{pal["accent"]};">{_h.escape(u)}</a>')
        out.append(_h.escape(m.group(0)[len(u):]))
        last = m.end()
    out.append(_h.escape(text[last:]))
    return "".join(out)


def _bullet_html(item, pal):
    m = re.match(r"^([^:]{2,40}):\s+(.*)$", item)
    if m and not URL_RE.search(m.group(1)):
        return f"<strong>{_h.escape(m.group(1))}:</strong> {_inline(m.group(2), pal)}"
    return _inline(item, pal)


def body_html(text, pal, fonts):
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[0].startswith("Subject:"):
        lines = lines[1:]
    P = f'margin:0 0 14px 0;font-size:15px;line-height:1.55;color:{pal["text"]};'
    H = (f'margin:26px 0 8px 0;font-family:{fonts["heading_stack"]};font-weight:600;'
         f'font-size:17px;letter-spacing:.3px;text-transform:uppercase;color:{pal["accent"]};')
    NOTE = f'margin:4px 0 12px 0;font-size:13px;line-height:1.5;color:{pal["muted"]};font-style:italic;'
    out, i = [], 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if set(s) <= set("─—-_=") and len(s) >= 8:
            out.append(f'<div style="height:3px;background:{pal["secondary"]};margin:22px 0;"></div>')
            i += 1
            continue
        if URL_RE.fullmatch(s):
            out.append(
                f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 18px 0;"><tr>'
                f'<td style="background:{pal["button_bg"]};border-radius:4px;">'
                f'<a href="{_h.escape(s)}" style="display:inline-block;padding:13px 26px;'
                f'font-family:{fonts["heading_stack"]};font-size:16px;font-weight:600;letter-spacing:.5px;'
                f'text-transform:uppercase;color:{pal["button_fg"]};text-decoration:none;">'
                f'Complete your advance</a></td></tr></table>'
                f'<p style="{NOTE}font-style:normal;">Or paste this link: {_inline(s, pal)}</p>')
            i += 1
            continue
        # sign-off: "Thanks," followed by the sender line(s) to the end
        if s.rstrip(",") in ("Thanks", "Thank you", "Best", "Gracias") and i >= n - 4:
            rest = [x.strip() for x in lines[i + 1:] if x.strip()]
            out.append(f'<p style="{P}margin-top:24px;">{_h.escape(s)}<br>'
                       f'<strong>{"<br>".join(_h.escape(x) for x in rest)}</strong></p>')
            break
        # heading: short line ending in ':' (optionally "Heading (note):")
        if s.endswith(":") and not ln.startswith(" "):
            m = re.match(r"^(.*?)\s*\((.*)\):$", s)
            head, note = (m.group(1), m.group(2)) if m else (s[:-1], None)
            if len(head) <= 40:
                out.append(f'<h2 style="{H}">{_h.escape(head)}</h2>')
                if note:
                    out.append(f'<p style="{NOTE}margin-top:0;">{_h.escape(note[0].upper() + note[1:])}</p>')
                i += 1
                # schedule rows directly under a heading
                rows = []
                while i < n and SCHED_RE.match(lines[i]):
                    t, what = SCHED_RE.match(lines[i]).groups()
                    rows.append((t, what))
                    i += 1
                if rows:
                    out.append('<table role="presentation" cellpadding="0" cellspacing="0" '
                               'style="border-collapse:collapse;margin:0 0 6px 0;">' + "".join(
                        f'<tr><td style="padding:3px 18px 3px 0;font-size:15px;font-weight:600;'
                        f'color:{pal["accent"]};white-space:nowrap;">{_h.escape(t)}</td>'
                        f'<td style="padding:3px 0;font-size:15px;color:{pal["text"]};">{_h.escape(w)}</td></tr>'
                        for t, w in rows) + "</table>")
                continue
        # facts run: consecutive "Label: value" lines (+ indented notes under a row)
        if FACT_RE.match(ln) and not BULLET_RE.match(ln):
            start, rows = i, []
            while i < n and lines[i].strip():
                m = FACT_RE.match(lines[i])
                if m:
                    rows.append([m.group(1), m.group(2), None])
                elif lines[i].startswith(" ") and rows and not SCHED_RE.match(lines[i]):
                    rows[-1][2] = lines[i].strip()
                else:
                    break
                i += 1
            if len(rows) >= 2:
                out.append('<table role="presentation" cellpadding="0" cellspacing="0" width="100%" '
                           'style="border-collapse:collapse;margin:0 0 8px 0;">' + "".join(
                    f'<tr><td valign="top" style="padding:7px 14px 7px 0;width:150px;font-size:13px;'
                    f'font-weight:600;text-transform:uppercase;letter-spacing:.3px;color:{pal["muted"]};'
                    f'border-bottom:1px solid #E6E6E7;">{_h.escape(k)}</td>'
                    f'<td style="padding:7px 0;font-size:15px;color:{pal["text"]};border-bottom:1px solid #E6E6E7;">'
                    f'{_inline(v, pal)}'
                    + (f'<div style="{NOTE}margin:3px 0 0 0;">{_inline(note, pal)}</div>' if note else "")
                    + "</td></tr>" for k, v, note in rows) + "</table>")
                continue
            i = start  # a lone "Label: value" is just a paragraph
            ln, s = lines[i], lines[i].strip()
        if BULLET_RE.match(ln):
            items = []
            while i < n and BULLET_RE.match(lines[i]):
                items.append(BULLET_RE.match(lines[i]).group(1))
                i += 1
            out.append(f'<ul style="margin:0 0 14px 0;padding-left:20px;">' + "".join(
                f'<li style="margin:0 0 7px 0;font-size:15px;line-height:1.5;color:{pal["text"]};">'
                f'{_bullet_html(it, pal)}</li>' for it in items) + "</ul>")
            continue
        if ln.startswith(" "):
            out.append(f'<p style="{NOTE}">{_inline(s.lstrip("*"), pal)}</p>')
            i += 1
            continue
        out.append(f'<p style="{P}">{_inline(s, pal)}</p>')
        i += 1
    return "\n".join(out)


def render_email(body, venue, embed_images=False):
    """Plain-text email body -> full branded HTML document for `venue`."""
    b = brand()
    fonts = b["fonts"]
    pal = palette(venue)
    v = venue_profile(venue)
    corp = b["corporate"]["logos"]
    if v:
        head_logo = _logo_src(f"logos/{v['slug']}-typelogo.png", embed_images)
        head_alt, address = v["name"], v["address"]
    else:
        head_logo = _logo_src(corp["primary"], embed_images)
        head_alt, address = "3CDC", "Cincinnati, OH"
    foot_logo = _logo_src(corp["horizontal"], embed_images)
    inner = body_html(body, pal, fonts)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{_h.escape(head_alt)}</title></head>
<body style="margin:0;padding:0;background:#F2F2F2;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F2F2F2;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
 style="width:100%;max-width:600px;background:#FFFFFF;font-family:{fonts['body_stack']};">
<tr><td style="height:6px;background:{pal['primary']};font-size:0;line-height:0;">&nbsp;</td></tr>
<tr><td style="padding:26px 32px 18px 32px;border-bottom:1px solid #E6E6E7;">
 <img src="{head_logo}" alt="{_h.escape(head_alt)}" height="34" style="display:block;height:34px;width:auto;border:0;">
</td></tr>
<tr><td style="padding:26px 32px 30px 32px;">
{inner}
</td></tr>
<tr><td style="padding:20px 32px 26px 32px;background:#F7F7F7;border-top:3px solid {pal['secondary']};">
 <img src="{foot_logo}" alt="3CDC — Cincinnati Center City Development Corporation" height="30"
  style="display:block;height:30px;width:auto;border:0;margin:0 0 10px 0;">
 <p style="margin:0;font-size:12px;line-height:1.5;color:{pal['muted']};">
  3CDC Events / Production &middot; {_h.escape(head_alt)} &middot; {_h.escape(address)}</p>
</td></tr>
</table></td></tr></table></body></html>"""
