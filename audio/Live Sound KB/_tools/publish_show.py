#!/usr/bin/env python3
"""
publish_show.py — one command publishes a built show to the Live Sound KB.

    python3 publish_show.py "<show folder>" [--no-push] [--skip-verify]

What it does, in order:
  1. reads show.status.json — warns if the .ses was never built
  2. make_show_page.build(): writes Wiki/show-<venue>-<date>-<slug>.md and copies
     the packet into Wiki/assets/shows/<date>-<slug>/ (page built from the .md)
  3. inserts the show into shows.md under its venue heading (if absent)
  4. appends a Completed Shows row to active-projects.md (if absent)
  5. runs kb-publish.sh (git commit+push, rsync assets, publish pages via the
     Wiki.js API, nav rebuild, sample download check)          [--no-push skips]
  6. verifies HTTP 200 on the page and on the MASTER asset     [--skip-verify skips]
  7. stamps `published` in show.status.json with the URL
  8. appends the spec's kb_writeback + reconciliation lines to
     _learning/PENDING.md so the next deep build harvests them (R44)

Only escalate to Wiki.js database surgery (the old show-wiki-push Step 7) if
step 6 fails after kb-publish.sh reported the page published.
"""
import argparse, datetime, json, os, re, subprocess, sys, urllib.request, base64

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(HERE)
WIKI = os.path.join(KB, "Wiki")
AUDIO = os.path.dirname(KB)
PUBLIC = "https://kb.tinydoorstudios.com"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(AUDIO, "_shared"))
import make_show_page, show_status  # noqa: E402


def secrets():
    """KB_BASIC_AUTH etc. from ~/.claude/kb-secrets.sh (bash `export X=...` lines)."""
    out = {}
    for p in (os.path.expanduser("~/.claude/kb-secrets.sh"), os.path.join(HERE, "kb-secrets.sh")):
        if os.path.exists(p):
            for line in open(p):
                m = re.match(r'\s*(?:export\s+)?(KB_[A-Z_]+)=["\']?([^"\'\n]*)', line)
                if m:
                    out.setdefault(m.group(1), m.group(2))
    return out


def http_ok(url, auth=None):
    # Cloudflare answers python-urllib's default UA with 403; curl's UA gets the real status.
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "curl/8.4.0 publish_show"})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return f"ERR {e}"


def upsert_shows_index(r):
    p = os.path.join(WIKI, "shows.md")
    s = open(p, encoding="utf-8").read()
    link = f"(/{r['page']})"
    if link in s:
        return "shows.md: already listed"
    heading = {"fsq": "## Fountain Square (FSQ)", "memo": "## Memorial Hall (Memo)"}[r["venue"]]
    if heading not in s:
        s = s.rstrip("\n") + f"\n\n{heading}\n"
    blurb = make_show_page.first_sentences(r["spec"].get("artist_profile"), 1)
    entry = (f"### [{r['name']} — {r['date']}]{link}\n"
             f"DiGiCo Q225 · {r['channels']} channels · {r['rev']}" + (f" · {blurb}" if blurb else "") + "\n\n"
             "| File | Type |\n|---|---|\n"
             f"| [Show Page]{link} | Wiki page |\n"
             f"| [MASTER packet — View](/assets/shows/{r['asset_dir']}/master.pdf) · [Download](/assets/shows/{r['asset_dir']}/master.pdf?dl=1) | PDF |\n"
             f"| [{r['name']}.ses — Download](/assets/shows/{r['asset_dir']}/{make_show_page.slug(r['name'])}.ses?dl=1) | Q225 showfile |\n\n")
    i = s.index(heading) + len(heading)
    j = s.index("\n", i) + 1
    # drop a "No show pages yet" placeholder if present
    s = s[:j] + "\n" + entry + re.sub(r"^\*?No show pages yet\.?\*?\n+", "", s[j:].lstrip("\n"), count=1)
    open(p, "w", encoding="utf-8").write(s)
    return "shows.md: entry added"


def upsert_active_projects(r):
    p = os.path.join(WIKI, "active-projects.md")
    s = open(p, encoding="utf-8").read()
    if f"[[{r['page']}]]" in s or f"/{r['page']})" in s:
        return "active-projects.md: already listed"
    hdr = "| Date | Show | Venue | Built | Harvested → |\n|---|---|---|---|---|\n"
    if hdr not in s:
        return "active-projects.md: Completed Shows table not found — add the row by hand"
    row = (f"| {r['date']} | {r['name']} | {r['vabbr']} | Full packet + .ses ({r['rev']}, {r['channels']} ch). "
           f"Published {datetime.date.today()} → [[{r['page']}]] | see `_learning/PENDING.md` |\n")
    s = s.replace(hdr, hdr + row, 1)
    s = re.sub(r'^Last updated: ".*?"$', f'Last updated: "{datetime.date.today()}"', s, count=1, flags=re.M)
    open(p, "w", encoding="utf-8").write(s)
    return "active-projects.md: row added"


def append_pending(r):
    p = os.path.join(KB, "_learning", "PENDING.md")
    res = (r["spec"].get("research") or {})
    items = []
    for line in (res.get("kb_writeback") or []):
        items.append(f"- [ ] **KB write-back** — {line} — {r['name']} {r['date']}")
    for line in (res.get("reconciliation") or []):
        if "no web" in line.lower() and "disagree" in line.lower():
            continue
        items.append(f"- [ ] **Reconciliation** — {line} — {r['name']} {r['date']}")
    if not items:
        return "PENDING.md: nothing to queue"
    s = open(p, encoding="utf-8").read() if os.path.exists(p) else "# PENDING\n"
    block = f"\n## From {r['name']} ({r['vabbr']} {r['date']}) — queued {datetime.date.today()}\n\n" + "\n".join(items) + "\n"
    if block.strip() in s:
        return "PENDING.md: already queued"
    open(p, "a", encoding="utf-8").write(block)
    return f"PENDING.md: {len(items)} item(s) queued"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--no-push", action="store_true", help="write pages/assets locally, skip kb-publish.sh")
    ap.add_argument("--skip-verify", action="store_true")
    a = ap.parse_args()
    folder = os.path.abspath(os.path.expanduser(a.folder))

    st = show_status.load(folder) or {}
    stages = st.get("stages") or {}
    if "ses_built" not in stages:
        print("WARN: show.status.json has no ses_built — publishing paperwork without a verified .ses build")
    if "published" in stages:
        print(f"note: already stamped published at {stages['published']['at']} — republishing")

    r = make_show_page.build(folder, WIKI, dry=False)
    print(f"page: {r['page']}  ·  {r['channels']} ch  ·  {r['rev']}  ·  {len(r['files'])} assets"
          + ("  ⚠ spec channel count != .md" if r["spec_stale"] else ""))
    print(" ", upsert_shows_index(r))
    print(" ", upsert_active_projects(r))

    if not a.no_push:
        rc = subprocess.call([os.path.join(HERE, "kb-publish.sh"), f"Show: {r['name']} ({r['vabbr']} {r['date']})"])
        if rc != 0:
            raise SystemExit(f"kb-publish.sh exited {rc} — not stamping published")

    url = f"{PUBLIC}/{r['page']}"
    if not a.skip_verify and not a.no_push:
        auth = secrets().get("KB_BASIC_AUTH") or None
        page_code = http_ok(url, auth)
        asset_code = http_ok(f"{PUBLIC}/assets/shows/{r['asset_dir']}/master.pdf", auth)
        print(f"  verify: page {page_code} · master.pdf {asset_code}")
        if page_code != 200 or asset_code != 200:
            raise SystemExit("verification failed — page or asset not reachable; see show-wiki-push "
                             "for the Wiki.js escalation. Not stamping published.")

    if a.no_push:
        print(f"\nDRY RUN — page + assets written locally, nothing pushed, not stamped. Would publish {url}")
        return
    show_status.stamp(folder, "published", note=url.replace("https://", ""))
    print(" ", append_pending(r))
    print(f"\nPUBLISHED {url}")


if __name__ == "__main__":
    main()
