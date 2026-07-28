#!/usr/bin/env python3
"""
make_show_page.py — build a Live Sound KB wiki show page + asset folder from a
built show folder. Used by the show-wiki-push skill.

Reads the show's spec.json (the same one build_packet.py rendered the packet
from), writes Wiki/show-<venue>-<date>-<slug>.md, and copies the full packet
into Wiki/assets/shows/<date>-<slug>/ under slugified filenames so the asset
URLs need no escaping.

Every file linked on the page is copied — a link with no file behind it is the
bug the old FSQ skill shipped, so the copy list is derived from the link list,
not maintained beside it.

Usage:
    python3 make_show_page.py "<show folder>" [--wiki "<Wiki dir>"] [--dry-run]
"""

import argparse, json, os, re, shutil, sys

VENUE_FULL = {"fsq": "Fountain Square", "memo": "Memorial Hall"}
VENUE_ABBR = {"fsq": "FSQ", "memo": "Memo"}
VENUE_ARTICLE = {"fsq": "venue-fountain-square", "memo": "venue-memorial-hall"}
DEFAULT_WIKI = os.path.expanduser("~/Documents/Claude/audio/Live Sound KB/Wiki")


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def fmt_hz(f):
    f = float(f)
    return f"{f / 1000:g}kHz" if f >= 1000 else f"{f:g}Hz"


def band_cell(b):
    if not b or b.get("gain") is None or str(b.get("type", "")).upper() == "FLAT":
        return "FLAT"
    kind = "Shelf" if str(b["type"]).upper() == "SHELF" else "Bell"
    cell = f"{b['gain']:+g}@{fmt_hz(b['freq'])} Q{b['q']:g} {kind}"
    if b.get("deq"):
        cell += " +DEQ"
    return cell


def bands_by_num(ch):
    out = {1: None, 2: None, 3: None, 4: None}
    for b in ch.get("bands", []):
        out[int(b["b"])] = b
    return out


MD_CH = re.compile(r"^##\s*Ch\s*(\S+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$")
MD_FILT = re.compile(r"^HPF:\s*([\w.]+)\s*\|\s*LPF:\s*([\w.]+)", re.I)
MD_BAND = re.compile(r"^B([1-4]):\s*(.+?)\s*$")


def channels_from_md(path):
    """Parse the FOH Channel Processing .md — the artifact the .ses was patched from.

    The .md is authoritative, not spec.json: a show can be revised after its spec
    was written (Nasty Nati shipped Rev 2.0 with the spec still at Rev 1.0), and a
    page built from a stale spec would document a show that never happened.
    """
    chans, cur, rev = [], None, ""
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## ") and " · " in line and "Ch " not in line[:6]:
            m = re.search(r"·\s*(Rev [^·]+?)\s*$", line)
            if m:
                rev = m.group(1).strip()
            continue
        m = MD_CH.match(line)
        if m:
            cur = dict(ch=m.group(1), name=m.group(2), mic=m.group(3),
                       hpf=20, lpf=None, bands={}, comp=None, gate=None)
            chans.append(cur)
            continue
        if cur is None:
            continue
        m = MD_FILT.match(line)
        if m:
            hp, lp = m.group(1), m.group(2)
            cur["hpf"] = float(hp) if hp.replace(".", "").isdigit() else 20
            cur["lpf"] = float(lp) if lp.replace(".", "").isdigit() else None
            continue
        m = MD_BAND.match(line)
        if m:
            n, body = int(m.group(1)), m.group(2)
            if body.strip().upper() == "FLAT":
                cur["bands"][n] = None
                continue
            p = [x.strip() for x in body.split("|")]
            if len(p) >= 4:
                cur["bands"][n] = dict(b=n, gain=float(p[0]), freq=float(p[1]),
                                       q=float(p[2]), type=p[3],
                                       deq=("DEQ" in body.upper()))
            continue
        # the .md separates dynamics fields with "|", which would break the wiki
        # table this lands in — swap to a middot on the way in
        if line.startswith("COMP:"):
            cur["comp"] = " · ".join(x.strip() for x in line[5:].split("|"))
        elif line.startswith("GATE:"):
            cur["gate"] = " · ".join(x.strip() for x in line[5:].split("|"))
    return chans, rev


def first_sentences(text, n=2):
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", " ".join(str(text).split()))
    return " ".join(parts[:n]).strip()


# (label, source filename suffix, asset basename, viewable)
ASSETS = [
    ("MASTER", " - MASTER.pdf", "master.pdf", True, "PDF (full packet)"),
    ("Show Packet", " - Show Packet.pdf", "show-packet.pdf", True, "PDF"),
    ("FOH EQ Reasoning", " - FOH EQ Reasoning.pdf", "foh-eq-reasoning.pdf", True, "PDF"),
    ("Stage Plot", " - Stage Plot.pdf", "stage-plot.pdf", True, "PDF (band-provided)"),
    ("Rider", " - Rider.pdf", "rider.pdf", True, "PDF (band-provided)"),
    ("Input List", " - Input List.xlsx", "input-list.xlsx", False, "Excel"),
    ("FOH Channel Processing", " - FOH Channel Processing.md",
     "foh-channel-processing.md", False, "Markdown (patcher source)"),
]


def build(folder, wiki, dry=False):
    folder = os.path.abspath(os.path.expanduser(folder))
    specs = [f for f in os.listdir(folder) if f.endswith(".spec.json")]
    if not specs:
        raise SystemExit(f"no .spec.json in {folder}")
    spec = json.load(open(os.path.join(folder, specs[0]), encoding="utf-8"))

    venue = spec.get("venue", "fsq")
    name = spec["show_name"]
    date = spec.get("show_date", "")
    sl = slug(name)
    asset_dir = f"{date}-{sl}"
    page = f"show-{venue}-{date}-{sl}"
    vfull, vabbr = VENUE_FULL.get(venue, venue), VENUE_ABBR.get(venue, venue.upper())

    # ---- assets: copy first, link only what landed ----------------------------
    dest = os.path.join(wiki, "assets", "shows", asset_dir)
    rows, copied = [], []
    if not dry:
        os.makedirs(dest, exist_ok=True)

    for label, suffix, base, viewable, kind in ASSETS:
        src = os.path.join(folder, f"{name}{suffix}")
        if not os.path.exists(src):
            continue
        if not dry:
            shutil.copy2(src, os.path.join(dest, base))
        copied.append(base)
        url = f"/assets/shows/{asset_dir}/{base}"
        if viewable:
            link = (f'<a href="{url}" target="_blank" rel="noopener">View</a> · '
                    f'<a href="{url}?dl=1" download>Download</a>')
        else:
            link = f'<a href="{url}?dl=1" download>Download</a>'
        rows.append(f"| {label} — {link} | {kind} |")

    ses_src = os.path.join(folder, f"{name}.ses")
    if os.path.exists(ses_src):
        base = f"{sl}.ses"
        if not dry:
            shutil.copy2(ses_src, os.path.join(dest, base))
        copied.append(base)
        rows.append(f'| {name}.ses — <a href="/assets/shows/{asset_dir}/{base}?dl=1" '
                    f'download>Download</a> | Q225 showfile |')

    spec_src = os.path.join(folder, specs[0])
    if not dry:
        shutil.copy2(spec_src, os.path.join(dest, "spec.json"))
    copied.append("spec.json")
    rows.append(f'| Build spec — <a href="/assets/shows/{asset_dir}/spec.json?dl=1" '
                f'download>Download</a> | JSON (reproducibility) |')

    # ---- page ----------------------------------------------------------------
    md_path = os.path.join(folder, f"{name} - FOH Channel Processing.md")
    chans, md_rev = channels_from_md(md_path)
    rev = md_rev or spec.get("rev", "")
    spec_stale = len(chans) != len(spec.get("channels", []))

    blurb = first_sentences(spec.get("artist_profile"), 2)
    room = first_sentences(spec.get("room_context"), 1)
    intro = " ".join(x for x in (blurb, room) if x)

    L = [f"# Show: {name} — {vfull}, {date}", "",
         f"**Venue:** {vfull} ({vabbr}) · **Console:** {spec.get('console_label', 'DiGiCo Q225')} "
         f"· **Date:** {date} · **Rev:** {rev}", ""]
    if intro:
        L += [intro, ""]
    L += ["## Files", "", "| File | Type |", "|---|---|"] + rows + ["", "## Input List", "",
          "| Ch | Instrument | Mic/DI |", "|---|---|---|"]
    for c in chans:
        L.append(f"| {c['ch']} | {c['name']} | {c.get('mic', '')} |")

    L += ["", "## EQ — Channel Processing", "",
          "Band order: B4 (high) → B3 → B2 → B1 (low). HPF/LPF dialed by hand at soundcheck "
          "— not written to the .ses. Read from the FOH .md the showfile was patched from.", "",
          "| Ch | Instrument | HPF | LPF | B4 | B3 | B2 | B1 |",
          "|---|---|---|---|---|---|---|---|"]
    for c in chans:
        bb = c["bands"]
        lpf = c.get("lpf")
        L.append(f"| {c['ch']} | {c['name']} | {fmt_hz(c.get('hpf', 20))} | "
                 f"{'off' if not lpf else fmt_hz(lpf)} | "
                 + " | ".join(band_cell(bb.get(n)) for n in (4, 3, 2, 1)) + " |")

    dyn = [c for c in chans if c.get("comp") or c.get("gate")]
    if dyn:
        L += ["", "## Dynamics — documented, not patched", "",
              "Mustard is paperwork only (rule 2026-07-16): reasoned on the build, dialed by "
              "hand at the desk, never written into the .ses.", "",
              "| Ch | Instrument | Compressor | Gate / Duck |", "|---|---|---|---|"]
        for c in dyn:
            L.append(f"| {c['ch']} | {c['name']} | {c.get('comp') or '—'} | "
                     f"{c.get('gate') or '—'} |")

    L += ["", "## .ses File", "",
          "Patched with the venue patcher on the shared Q225 engine (byte-verify + full "
          "readback PASS). Written: fader names and EQ bands. Not written: HPF/LPF and "
          "dynamics — those are documented in the packet and dialed by hand.", "",
          "## Show Folder", "",
          f"`~/Documents/Claude/audio/{vfull}/{os.path.basename(folder)}/`", "",
          "## Related", "",
          f"[[{VENUE_ARTICLE.get(venue, 'venues')}]], [[console-digico-q225]], "
          f"[[pipeline-spec-{venue}]], [[shows]]", ""]

    out = os.path.join(wiki, f"{page}.md")
    if not dry:
        open(out, "w", encoding="utf-8").write("\n".join(L))
    return dict(page=page, path=out, asset_dir=asset_dir, files=copied,
                channels=len(chans), name=name, date=date, venue=venue,
                vabbr=vabbr, spec=spec, rev=rev, spec_stale=spec_stale,
                dynamics=len(dyn))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--wiki", default=DEFAULT_WIKI)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = build(a.folder, a.wiki, a.dry_run)
    flag = "  ⚠ spec.json channel count != .md — page built from the .md" if r["spec_stale"] else ""
    print(f"{r['page']}  ·  {r['channels']} ch  ·  {r['rev']}  ·  {r['dynamics']} dyn  ·  "
          f"{len(r['files'])} assets{flag}")


if __name__ == "__main__":
    main()
