#!/usr/bin/env python3
"""
build_site.py — assemble everything under content/ into site/pages.json for the publisher.

content layout (path on the wiki = folder/slug):
  content/home.md                → /home            (wiki root)
  content/how-to/*.md            → /how-to/<slug>   curated task pages
  content/io/*.md                → /io/<slug>       curated I/O + card pages
  content/manual/ref-*.md        → /reference/<n>-<slug>   Software Reference mirror
  content/manual/gs-*.md         → /console/<n>-<slug>     Getting Started mirror
  content/docs/*.md              → /docs/<slug>     other DiGiCo docs mirrored (release notes, TN339 …)
  content/venue/*.md             → /venue/<slug>    Memo / FSQ specifics (later)

A page's title is its first H1. Its description is the first plain paragraph (trimmed).
Also writes site/nav.json (sidebar tree) from the same scan.
"""
import os, re, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content'); OUT = os.path.join(ROOT, 'site'); os.makedirs(OUT, exist_ok=True)
SRC_NOTE = {
 'ref': "> Mirrored from the DiGiCo *SD & Quantum Software Reference Manual*, Issue H (June 2025, software V20+). Figures are DiGiCo's. For the V22 changes see [V22 Release Notes](/docs/v22-release-notes).",
 'gs':  "> Mirrored from the DiGiCo *Quantum 2 (Q225 / Q338) Getting Started* guide, Issue A. Figures are DiGiCo's.",
}
def load(fp):
    s = open(fp).read().strip()
    m = re.search(r'^#\s+(.+)$', s, re.M); title = m.group(1).strip() if m else os.path.basename(fp)
    body = s
    # description = first non-empty, non-heading, non-image, non-italic line
    desc = ''
    for line in s.splitlines():
        t = line.strip()
        if not t or t.startswith(('#', '!', '*', '>', '|', '-', 'Labels:')): continue
        desc = t[:250]; break
    return title, desc, body
pages = []; nav = []
def add(path, fp, tags, note=''):
    title, desc, body = load(fp)
    if note: body = re.sub(r'^(#\s+.+\n)', r'\1\n' + note.replace('\\', '\\\\') + '\n', body, count=1)
    pages.append(dict(path=path, title=title, description=desc or title, tags=tags, content=body, src=os.path.relpath(fp, ROOT)))
    return title
def numkey(fn):
    m = re.search(r'-(\d+)-(\d+)-', fn); return (int(m.group(1)), int(m.group(2))) if m else (99, 0)
# home
if os.path.exists(os.path.join(C, 'home.md')): add('home', os.path.join(C, 'home.md'), ['home'])
# curated folders
for folder, label, icon in [('how-to', 'How do I…', 'mdi-lightbulb-on-outline'), ('hardware', 'I/O, racks & DMI cards', 'mdi-server-network'), ('venue', 'Our venues', 'mdi-map-marker')]:
    files = sorted(glob.glob(os.path.join(C, folder, '*.md')))
    if not files: continue
    items = []
    for fp in files:
        slug = os.path.splitext(os.path.basename(fp))[0]
        t = add(f'{folder}/{slug}', fp, [folder]); items.append((t, f'/{folder}/{slug}'))
    nav.append((label, icon, items))
# manual mirrors
for prefix, folder, label, icon in [('gs', 'console', 'Console: Getting Started', 'mdi-console'), ('ref', 'reference', 'Software Reference (manual)', 'mdi-book-open-page-variant')]:
    files = sorted(glob.glob(os.path.join(C, 'manual', f'{prefix}-*.md')), key=lambda f: numkey(os.path.basename(f)))
    items = []
    for fp in files:
        slug = os.path.splitext(os.path.basename(fp))[0][len(prefix)+1:]
        t = add(f'{folder}/{slug}', fp, [folder, 'manual'], SRC_NOTE[prefix]); items.append((t, f'/{folder}/{slug}'))
    nav.append((label, icon, items))
# docs
files = sorted(glob.glob(os.path.join(C, 'docs', '*.md')))
items = []
for fp in files:
    slug = os.path.splitext(os.path.basename(fp))[0]
    t = add(f'docs/{slug}', fp, ['docs']); items.append((t, f'/docs/{slug}'))
if items: nav.append(('DiGiCo documents', 'mdi-file-document-multiple', items))
# section index pages (so /how-to, /io, /console, /reference, /docs resolve)
INTRO = {'how-to': "Task pages. Each one is a few steps, the screenshots from the manual, and a link to the manual section if you want the long version.",
         'hardware': "The cards in the console and the racks on stage: what each one does, how it's wired, how it's set up, what the lights mean.",
         'console': "DiGiCo's Quantum 2 (Q225/Q338) Getting Started guide, one page per section.",
         'reference': "The SD & Quantum Software Reference Manual (Issue H, V20+), one page per menu. Search finds text inside these.",
         'docs': "Other DiGiCo documents mirrored here: release notes, tech notes, rack and card guides."}
for label, icon, items in nav:
    folder = items[0][1].split('/')[1] if items else None
    if not folder or any(p['path']==folder for p in pages): continue
    body = [f"# {label}", '', INTRO.get(folder, ''), '']
    for t, tgt in items:
        d = next((p['description'] for p in pages if '/'+p['path']==tgt), '')
        body.append(f"- [{t}]({tgt})" + (f" — {d[:140]}" if d and folder in ('how-to','hardware') else ''))
    pages.append(dict(path=folder, title=label, description=INTRO.get(folder, label), tags=[folder,'index'], content='\n'.join(body), src='(generated)'))
json.dump(pages, open(os.path.join(OUT, 'pages.json'), 'w'))
json.dump(nav, open(os.path.join(OUT, 'nav.json'), 'w'), indent=1)
print(f"{len(pages)} pages, {sum(len(i[2]) for i in nav)} nav links, {sum(len(p['content']) for p in pages)//1000} KB")
