"""Hybrid retrieval: pgvector cosine + Postgres full-text, fused with reciprocal rank fusion,
then boosted by source tier (teachings 4 › venue/KB 3 › how-to 2 › manual 1)."""
from db import get_conn
from embed import embed_query
from settings import S

_SELECT = '''
SELECT c.id, c.section, c.text, c.tier, c.figures, c.teaching_id,
       p.title, p.url, p.path, p.source
FROM chunks c LEFT JOIN pages p ON p.id = c.page_id
'''


def search(q: str, k: int | None = None) -> list[dict]:
    k = k or S.top_k
    vec = embed_query(q)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(_SELECT + 'WHERE c.embedding IS NOT NULL ORDER BY c.embedding <=> %s::vector LIMIT 30', (vec,))
        v_rows = cur.fetchall()
        cur.execute(_SELECT + '''WHERE c.tsv @@ websearch_to_tsquery('english', %s)
                    ORDER BY ts_rank_cd(c.tsv, websearch_to_tsquery('english', %s)) DESC LIMIT 30''', (q, q))
        t_rows = cur.fetchall()
    scores, rows = {}, {}
    for rank, r in enumerate(v_rows):
        scores[r[0]] = scores.get(r[0], 0) + 1.0 / (60 + rank); rows[r[0]] = r
    for rank, r in enumerate(t_rows):
        scores[r[0]] = scores.get(r[0], 0) + 1.0 / (60 + rank); rows[r[0]] = r
    for cid in scores:
        scores[cid] *= 1 + 0.15 * (rows[cid][3] - 1)
    ordered = sorted(scores, key=scores.get, reverse=True)[:k]
    out = []
    for cid in ordered:
        r = rows[cid]
        out.append({'id': r[0], 'section': r[1], 'text': r[2], 'tier': r[3], 'figures': list(r[4] or []),
                    'teaching_id': r[5], 'title': r[6] or 'Staff teaching', 'url': r[7] or '', 'path': r[8] or '',
                    'source': r[9] or 'teaching', 'score': round(scores[cid], 4)})
    return out


def read_page(path: str) -> dict | None:
    """Full page text by wiki path (either wiki). Accepts a full URL or a bare path."""
    path = path.strip().rstrip('/')
    for prefix in (S.digico_public_url, S.kb_public_url):
        if path.startswith(prefix):
            path = path[len(prefix):]
    path = path.lstrip('/')
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT title, url, content, source FROM pages WHERE path=%s OR path LIKE %s ORDER BY length(path) LIMIT 1',
                    (path, '%/' + path.split('/')[-1]))
        r = cur.fetchone()
    if not r:
        return None
    return {'title': r[0], 'url': r[1], 'content': r[2], 'source': r[3]}


def page_index() -> list[dict]:
    """Titles + paths of the curated layers, for the system prompt."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT title, path, url, tier FROM pages
                       WHERE tier >= 2 OR source='kb' ORDER BY tier DESC, path""")
        return [{'title': t, 'path': p, 'url': u, 'tier': tier} for t, p, u, tier in cur.fetchall()]
