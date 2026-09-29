"""Avenir Next for every reportlab document (Brian, 2026-09-29: "Avenir
everywhere", show packets included, after adopting the 3CDC brand guide).

install() re-registers reportlab's built-in Helvetica family names with the
Avenir Next faces from macOS's own font file. Every existing fontName=
'Helvetica…', setFont('Helvetica…'), stringWidth(..., 'Helvetica…') and the
stylesheet defaults then render and measure in Avenir, with no call site
changed. Courier stays Courier: channel numbers and EQ strings keep their
monospace columns.

Symbols: built-in Helvetica silently borrowed ✓ ■ → etc. from ZapfDingbats /
Symbol; a TrueType font gets no such fallback, and Avenir has none of those
glyphs, so the 48V ticks, section markers and arrows drew blank (caught on the
2026-09-29 before/after build). install() therefore builds, once, a local copy
of each Avenir face with the missing symbols grafted in from Apple Symbols /
Menlo, cached in ~/Library/Caches/nyquist-fonts (derived from system fonts;
never committed). Delete that folder to force a rebuild.

Bold maps to Avenir Next Demi Bold: closest to Helvetica Bold's weight, and it
keeps width growth down in tight table cells.

Off a Mac (no Avenir file) install() does nothing and the build falls back to
real Helvetica, so a build never fails over a font.
"""
import os
from pathlib import Path

AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
DONORS = ["/System/Library/Fonts/Apple Symbols.ttf", "/System/Library/Fonts/Menlo.ttc"]
CACHE = Path.home() / "Library" / "Caches" / "nyquist-fonts"
SYMBOLS = "■□▪▫●○◆◇▲△▼▽►◄★☆☐☑☒✓✔✗✕✘⚑⚐⚠←↑→↓↔↕⇒⇐━─│▌▐≥≤≠±∞"
# subfont indices in Avenir Next.ttc (macOS 14)
_FACES = {"Helvetica": 7, "Helvetica-Bold": 2, "Helvetica-Oblique": 4,
          "Helvetica-BoldOblique": 3}
_VERSION = "1"
_done = None


def _load(path):
    from fontTools.ttLib import TTCollection, TTFont
    return TTCollection(path).fonts[0] if path.endswith(".ttc") else TTFont(path)


def _build(idx, out):
    """Avenir face `idx` + every SYMBOLS glyph it lacks, scaled from a donor."""
    from fontTools.ttLib import TTCollection
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.transformPen import TransformPen
    base = TTCollection(AVENIR).fonts[idx]
    upm = base["head"].unitsPerEm
    cmap = base.getBestCmap()
    glyf, hmtx = base["glyf"], base["hmtx"]
    order = list(base.getGlyphOrder())
    added = {}
    for donor_path in DONORS:
        donor = _load(donor_path)
        dcmap, dgs = donor.getBestCmap(), donor.getGlyphSet()
        s = upm / donor["head"].unitsPerEm
        for ch in SYMBOLS:
            cp = ord(ch)
            if cp in cmap or cp in added or cp not in dcmap:
                continue
            src = dcmap[cp]
            pen = TTGlyphPen(None)
            dgs[src].draw(TransformPen(pen, (s, 0, 0, s, 0, 0)))
            name = f"nyq_{cp:04X}"
            glyf[name] = pen.glyph()
            adv = int(round(donor["hmtx"][src][0] * s))
            glyf[name].recalcBounds(glyf)
            hmtx[name] = (adv, getattr(glyf[name], "xMin", 0))
            order.append(name)
            added[cp] = name
    base.setGlyphOrder(order)
    for t in base["cmap"].tables:
        if t.isUnicode():
            t.cmap.update(added)
    base["maxp"].numGlyphs = len(order)
    for tag in ("post",):
        if tag in base and hasattr(base[tag], "extraNames"):
            base[tag].formatType = 3.0  # drop glyph names; avoids post table sync issues
    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(str(out))


def install():
    """True when Avenir is active. Safe to call more than once."""
    global _done
    if _done is not None:
        return _done
    _done = False
    if not os.path.exists(AVENIR):
        return False
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    for name, idx in _FACES.items():
        path = CACHE / f"avenir-next-{idx}-sym-v{_VERSION}.ttf"
        try:
            if not path.exists():
                _build(idx, path)
            pdfmetrics.registerFont(TTFont(name, str(path)))
        except Exception as e:  # noqa: BLE001 — no fontTools / bad donor: plain Avenir
            import sys
            print(f"brand_fonts: symbol graft failed for {name} ({e!r}); "
                  "✓ ■ → will draw blank in this build", file=sys.stderr)
            pdfmetrics.registerFont(TTFont(name, AVENIR, subfontIndex=idx))
    for bold, ital, name in [(0, 0, "Helvetica"), (1, 0, "Helvetica-Bold"),
                             (0, 1, "Helvetica-Oblique"), (1, 1, "Helvetica-BoldOblique")]:
        addMapping("Helvetica", bold, ital, name)
    _done = True
    return True
