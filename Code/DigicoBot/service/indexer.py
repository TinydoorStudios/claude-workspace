"""Pull every page from the wikis, chunk by heading, embed, upsert.

Chunk shape: "Page: <title> › <H2> › <H3>\n\n<section text>", 300–1800 chars, split on paragraph
boundaries when a section runs long. Each chunk keeps the figure paths it mentions so the answer can
attach the screenshot. Pages whose content hash hasn't changed are skipped, so the nightly run is cheap.
"""
import hashlib
import re
import time

from db import get_conn
from embed import embed_texts
from settings import S
from wiki import Wiki

FIG_RE = re.compile(r'!\[[^\]]*\]\((/figures/[^)\s]+)\)')
HEAD_RE = re.compile(r'^(#{1,4})\s+(.+?)\s*$', re.M)
MAX_CHARS = 1800
MIN_CHARS = 120

TIER_BY_PREFIX = [  # digico wiki path prefix → tier
    ('venue/', 3), ('how-to/', 2), ('io/', 2), ('hardware/', 2), ('home', 2), ('console/', 1), ('reference/', 1), ('docs/', 1),
]


def tier_for(source: str, path: str) -> int:
    if source == 'kb':
        return 3
    for prefix, t in TIER_BY_PREFIX:
        if path.startswith(prefix):
            return t
    return 1


def strip_md(text: str) -> str:
    text = FIG_RE.sub('', text)                       # figure images (kept separately)
    text = re.sub(r'^>\s*Mirrored from.*$', '', text, flags=re.M)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)   # links → their text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_sections(md: str) -> list[tuple[list[str], str]]:
    """Return [(heading_path, body)] walking the heading tree."""
    out, stack, pos = [], [], 0
    matches = list(HEAD_RE.finditer(md))
    if not matches:
        return [([], md)]
    if matches[0].start() > 0:
        out.append(([], md[:matches[0].start()]))
    for i, m in enumerate(matches):
        level, title = len(m.group(1)), m.group(2).strip()
        stack = [s for s in stack if s[0] < level] + [(level, title)]
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        out.append(([t for _, t in stack], md[m.end():end]))
    return out


def chunk_page(title: str, md: str) -> list[dict]:
    chunks = []
    for hpath, body in split_sections(md):
        figs = FIG_RE.findall(body)
        text = strip_md(body)
        if len(text) < MIN_CHARS and not figs:
            continue
        section = ' › '.join([title] + [h for h in hpath if h != title])
        paras = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
        buf = ''
        parts = []
        for p in paras:
            if buf and len(buf) + len(p) + 2 > MAX_CHARS:
                parts.append(buf); buf = p
            else:
                buf = (buf + '\n\n' + p) if buf else p
        if buf:
            parts.append(buf)
        for part in parts:
            if len(part) < MIN_CHARS and len(parts) > 1 and not figs:
                continue
            chunks.append({'section': section, 'text': f'Page: {section}\n\n{part}', 'figures': figs[:4]})
    return chunks


def sync_source(source: str, wiki: Wiki, allow: set[str] | None, conn) -> dict:
    stats = {'seen': 0, 'updated': 0, 'skipped': 0, 'removed': 0}
    pages = [p for p in wiki.list_pages() if p.get('isPublished', True)]
    keep = set()
    for p in pages:
        path = p['path']
        if source == 'digico' and path in S.exclude_paths:
            continue
        if allow is not None and path.split('/')[-1] not in allow and path not in allow:
            continue
        keep.add(path); stats['seen'] += 1
        full = wiki.get_page(p['id'])
        content = full['content'] or ''
        sha = hashlib.sha1(content.encode()).hexdigest()
        with conn.cursor() as cur:
            cur.execute('SELECT id, content_sha FROM pages WHERE source=%s AND path=%s', (source, path))
            row = cur.fetchone()
            if row and row[1] == sha:
                stats['skipped'] += 1
                continue
            tier = tier_for(source, path)
            url = wiki.page_url(path)
            if row:
                page_id = row[0]
                cur.execute('UPDATE pages SET title=%s,url=%s,tier=%s,content=%s,content_sha=%s,updated_at=now() WHERE id=%s',
                            (full['title'], url, tier, content, sha, page_id))
                cur.execute('DELETE FROM chunks WHERE page_id=%s', (page_id,))
            else:
                cur.execute('INSERT INTO pages(source,path,title,url,tier,content,content_sha) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id',
                            (source, path, full['title'], url, tier, content, sha))
                page_id = cur.fetchone()[0]
            chunks = chunk_page(full['title'], content)
            if chunks:
                vecs = embed_texts([c['text'] for c in chunks])
                for i, (c, v) in enumerate(zip(chunks, vecs)):
                    cur.execute('INSERT INTO chunks(page_id,ord,section,text,tier,figures,embedding) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                                (page_id, i, c['section'], c['text'], tier, c['figures'], v))
            stats['updated'] += 1
        conn.commit()
    with conn.cursor() as cur:
        cur.execute('SELECT id, path FROM pages WHERE source=%s', (source,))
        for pid, path in cur.fetchall():
            if path not in keep:
                cur.execute('DELETE FROM pages WHERE id=%s', (pid,)); stats['removed'] += 1
    conn.commit()
    return stats


def index_teaching(conn, teaching_id: int, text: str, question: str | None):
    body = f'Page: Staff teaching (from Brian)\n\n{text}'
    if question:
        body += f'\n\nAsked in the thread: {question}'
    vec = embed_texts([body])[0]
    with conn.cursor() as cur:
        cur.execute('DELETE FROM chunks WHERE teaching_id=%s', (teaching_id,))
        cur.execute('INSERT INTO chunks(teaching_id,ord,section,text,tier,embedding) VALUES(%s,0,%s,%s,4,%s)',
                    (teaching_id, 'Staff teaching', body, vec))
    conn.commit()


def run_index() -> dict:
    t0 = time.time()
    out = {}
    with get_conn() as conn:
        out['digico'] = sync_source('digico', Wiki(S.digico_wiki_url, S.digico_wiki_key, S.digico_public_url), None, conn)
        if S.kb_wiki_key and S.kb_paths:
            out['kb'] = sync_source('kb', Wiki(S.kb_wiki_url, S.kb_wiki_key, S.kb_public_url), set(S.kb_paths), conn)
        with conn.cursor() as cur:
            cur.execute('SELECT id, text, question FROM teachings')
            rows = cur.fetchall()
            cur.execute('SELECT teaching_id FROM chunks WHERE teaching_id IS NOT NULL')
            have = {r[0] for r in cur.fetchall()}
        for tid, text, q in rows:
            if tid not in have:
                index_teaching(conn, tid, text, q)
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM pages'); out['pages'] = cur.fetchone()[0]
            cur.execute('SELECT count(*) FROM chunks'); out['chunks'] = cur.fetchone()[0]
    out['seconds'] = round(time.time() - t0, 1)
    return out


if __name__ == '__main__':
    print(run_index())
