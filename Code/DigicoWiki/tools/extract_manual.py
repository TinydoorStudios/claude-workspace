#!/usr/bin/env python3
"""
extract_manual.py — turn a DiGiCo PDF manual into wiki-ready markdown + figures.

Walks every page as an ordered stream of text and image blocks (PyMuPDF), detects
numbered section headings by font (bold, >= heading size), and writes one markdown
file per top-level section (e.g. 2.4 Snapshots Menu) with H2/H3 subsections and the
figures inline exactly where they sit in the manual.

    python3 extract_manual.py <pdf> <out_md_dir> <out_fig_dir> --prefix ref --start-page 12

Figures land as <out_fig_dir>/<prefix>-p<page>-<n>.png and are referenced in the
markdown as /figures/<prefix>-p<page>-<n>.png (the Wiki.js asset path we publish to).
"""
import fitz, re, os, sys, argparse, hashlib, json

HEAD_RE = re.compile(r'^(\d+(?:\.\d+){1,3})\s*$')          # "2.4.3" span on its own
CHAP_RE = re.compile(r'^Chapter\s+(\d+):\s*(.+?)\s*$')
FIG_RE  = re.compile(r'^Figure\s+\d+\s*-\s*(.+)$')

def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:70]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('md_dir'); ap.add_argument('fig_dir')
    ap.add_argument('--prefix', default='ref'); ap.add_argument('--start-page', type=int, default=1)
    ap.add_argument('--end-page', type=int, default=0)
    ap.add_argument('--min-img', type=int, default=90, help='skip images smaller than this (px, either side)')
    ap.add_argument('--body-size', type=float, default=11.0)
    ap.add_argument('--single', default='', help='unnumbered doc: put everything in one page with this title')
    ap.add_argument('--single-h', type=float, default=14.0, help='font size that counts as a heading in --single mode')
    a = ap.parse_args()
    os.makedirs(a.md_dir, exist_ok=True); os.makedirs(a.fig_dir, exist_ok=True)
    doc = fitz.open(a.pdf)
    end = a.end_page or doc.page_count
    sections = []      # list of dict(num, title, level, chapter, items=[('p',text)|('img',path,alt)])
    cur = None; chapter = None; chapter_title = ''
    seen_hash = {}
    figcount = 0
    def new_section(num, title, level):
        nonlocal cur
        cur = dict(num=num, title=title, level=level, chapter=chapter, chapter_title=chapter_title, items=[], pages=set())
        sections.append(cur)
    pending_num = None
    if a.single:
        chapter, chapter_title = 1, a.single
        new_section('1.1', a.single, 1)
    for pno in range(a.start_page-1, end):
        page = doc[pno]; pg = pno+1
        blocks = page.get_text('dict')['blocks']
        blocks.sort(key=lambda b: (round(b['bbox'][1]/6), b['bbox'][0]))
        imgn = 0
        # --- classify image blocks: big screenshots vs small masked callout labels/arrows ---
        xref_of = {}; smask_of = {}
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                xref_of[(round(r.x0), round(r.y0))] = img[0]; smask_of[img[0]] = img[1]
        ib = [b for b in blocks if b['type'] == 1]
        def key(b): return (round(b['bbox'][0]), round(b['bbox'][1]))
        big = [b for b in ib if (b['bbox'][2]-b['bbox'][0]) >= 110 and (b['bbox'][3]-b['bbox'][1]) >= 70]
        small = [b for b in ib if b not in big]
        merged_clip = {id(b): fitz.Rect(b['bbox']) for b in big}
        skip = set()
        for sb in small:
            r = fitz.Rect(sb['bbox']); near = None
            for bb in big:
                if fitz.Rect(bb['bbox']).intersects(r + (-140, -140, 140, 140)): near = bb; break
            if near is not None:
                merged_clip[id(near)] |= r; skip.add(id(sb))          # callout joins its screenshot
            elif smask_of.get(xref_of.get(key(sb))):                   # stray masked label with no screenshot: drop
                skip.add(id(sb))
        for b in blocks:
            if b['type'] == 1:
                w, h = b['width'], b['height']
                if id(b) in skip or w < a.min_img or h < a.min_img or cur is None: continue
                xref = xref_of.get(key(b))
                if xref is None: continue
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha >= 4: pix = fitz.Pixmap(fitz.csRGB, pix)
                    data = pix.tobytes('png')          # only used as the dedupe key (keeps filenames stable)
                except Exception as e:
                    continue
                hsh = hashlib.md5(data).hexdigest()
                if hsh in seen_hash:
                    path = seen_hash[hsh]
                else:
                    imgn += 1; figcount += 1
                    fn = f"{a.prefix}-p{pg:03d}-{imgn}.png"
                    path = os.path.join(a.fig_dir, fn)
                    clip = (merged_clip.get(id(b)) or fitz.Rect(b['bbox'])) + (-4, -4, 4, 4)
                    rendered = page.get_pixmap(clip=clip, dpi=220, alpha=False)
                    from PIL import Image as _I, ImageStat as _S
                    _im = _I.frombytes('RGB', (rendered.width, rendered.height), rendered.samples)
                    if sum(_S.Stat(_im).stddev)/3 < 6:          # flat colour = callout box / stencil, not a figure
                        seen_hash[hsh] = None; imgn -= 1; figcount -= 1; continue
                    rendered.save(path); seen_hash[hsh] = path
                if path is None: continue
                cur['items'].append(('img', os.path.basename(path), '', pg)); cur['pages'].add(pg)
                continue
            # text block
            if cur is not None and cur['items'] and cur['items'][-1][0]=='t':
                cur['items'].append(('br','','',pg))
            for line in b['lines']:
                spans = line['spans']
                text = ''.join(s['text'] for s in spans).strip()
                if not text: continue
                s0 = spans[0]; bold = 'Bold' in s0['font']; size = s0['size']
                # running header
                if 'Software Reference Manual' in text and size >= 13: continue
                if 'Getting Started' in text and size >= 13 and b['bbox'][1] < 60: continue
                m = CHAP_RE.match(text)
                if m and size >= 18:
                    chapter, chapter_title = int(m.group(1)), m.group(2); continue
                if size >= 20 and bold and not a.single:
                    chapter_title = text.strip(); continue
                m = HEAD_RE.match(text)
                if a.single: m = None
                if m and bold and size >= a.body_size:
                    pending_num = m.group(1); continue
                if pending_num and bold:
                    num = pending_num; pending_num = None
                    new_section(num, text, num.count('.')); cur['pages'].add(pg); continue
                if pending_num: pending_num = None
                # heading on same line: "2.4.3 Title"
                m = re.match(r'^(\d+(?:\.\d+){1,3})\s+(\S.*)$', text)
                if a.single: m = None
                if m and bold and size >= a.body_size and len(text) < 90:
                    new_section(m.group(1), m.group(2), m.group(1).count('.')); cur['pages'].add(pg); continue
                if cur is None: continue
                fm = FIG_RE.match(text)
                if fm and size < 10:
                    # attach caption to last image
                    for i in range(len(cur['items'])-1, -1, -1):
                        if cur['items'][i][0]=='img' and not cur['items'][i][2]:
                            it = cur['items'][i]; cur['items'][i] = ('img', it[1], fm.group(1).strip(), it[3]); break
                    continue
                if size < 8: continue
                if re.fullmatch(r'\d{1,3}', text): continue                       # bare page number
                if cur is not None and not bold and re.fullmatch(r'\d+(?:\.\d+)*\s+.{3,60}', text) and text.split(' ',1)[1].strip() == (cur['title'] if cur['num']==('.'.join(cur['num'].split('.')[:2])) else cur['title']) : continue
                style = 'b' if bold else ('i' if 'Italic' in s0['font'] else '')
                if not bold and ('F3' in s0['font'] and 'CIDFont' in s0['font']): style = 'b'
                if a.single and size >= a.single_h and len(text) < 90:
                    cur['items'].append(('h', text, '', pg)); continue
                text = text.replace('\uf0b7', '•')
                if re.match(r'^(•|o\s|\d{1,2}\.\s|-\s)', text):
                    cur['items'].append(('br','','',pg)); style = 'li'
                cur['items'].append(('t', text, style, pg)); cur['pages'].add(pg)
    # ---- emit markdown: one file per level-1 section (x.y), H3 for deeper ----
    files = {}
    order = []
    for s in sections:
        top = '.'.join(s['num'].split('.')[:2])
        if top not in files:
            files[top] = []; order.append(top)
        files[top].append(s)
    index = []
    for top in order:
        secs = files[top]; head = secs[0]
        title = (a.single if a.single else (f"{top} {head['title']}" if head['num']==top else f"{top}"))
        fn = (f"{a.prefix}.md" if a.single else f"{a.prefix}-{top.replace('.','-')}-{slug(head['title'])}.md")
        out = [f"# {title}", '', f"*{('Chapter '+str(head['chapter'])+': ') if head['chapter'] else ''}{head['chapter_title']} — manual pages {min(head['pages'])}–{max(max(x['pages']) for x in secs if x['pages'])}*", '']
        for s in secs:
            if s['num'] != top:
                out.append(f"{'#'*(min(s['level'],3)+1)} {s['num']} {s['title']}"); out.append('')
            para = []
            def flush():
                if para: out.append(' '.join(para)); out.append(''); para.clear()
            items = s['items']; merged = []; i = 0
            while i < len(items):
                it = items[i]
                if it[0]=='t' and it[2] in ('', 'b') and len(it[1]) < 26:
                    run = [it[1]]; j = i+1
                    while j+1 < len(items) and items[j][0]=='br' and items[j+1][0]=='t' and items[j+1][2] in ('', 'b') and len(items[j+1][1]) < 26:
                        run.append(items[j+1][1]); j += 2
                    if len(run) >= 3:
                        merged.append(('t', 'Labels: ' + ' · '.join(run), 'i', it[3])); merged.append(('br','','',it[3])); i = j; continue
                merged.append(it); i += 1
            for it in merged:
                if it[0]=='img':
                    flush(); alt = it[2] or f"{head['title']} (manual p.{it[3]})"
                    out.append(f"![{alt}](/figures/{it[1]})"); 
                    if it[2]: out.append(f"*{it[2]}*")
                    out.append('')
                elif it[0]=='br':
                    flush()
                elif it[0]=='h':
                    flush(); out.append(f"## {it[1]}"); out.append('')
                else:
                    t = it[1]
                    if it[2]=='li':
                        flush(); t = re.sub(r'^(•|o\s)\s*', '- ', t); out.append(t); out.append('')
                    elif it[2]=='b' and len(t) < 60 and not t.endswith(('.', ':', ',')):
                        flush(); out.append(f"**{t}**"); out.append('')
                    else:
                        para.append(t)
            flush()
        open(os.path.join(a.md_dir, fn), 'w').write('\n'.join(out))
        index.append(dict(file=fn, num=top, title=head['title'], chapter=head['chapter'], chapter_title=head['chapter_title'], subs=[(x['num'], x['title']) for x in secs if x['num']!=top]))
    json.dump(index, open(os.path.join(a.md_dir, f"_{a.prefix}-index.json"), 'w'), indent=1)
    print(f"{len(sections)} sections -> {len(order)} pages, {figcount} figures")

if __name__ == '__main__':
    main()
