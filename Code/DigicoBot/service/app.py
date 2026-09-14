"""DigiBot API — the brain behind the n8n Slack workflows.

n8n owns the Slack token and does every Slack call; this service never talks to Slack. It gets
plain JSON in and returns plain JSON out, so every endpoint is testable with curl.

  GET  /health
  POST /answer          {question, user, channel, ts, history:[{role,text}]} → {text, figures, ...}
  POST /teach           {text, user, question, slack_link}                    → {ok, id}
  POST /reaction        {reaction, user, channel, ts, message_text, message_user, is_bot_message}
  POST /index           re-pull both wikis, re-embed changed pages
  POST /inbox/rebuild   rewrite the teachings-inbox wiki page
  GET  /gaps/digest     the weekly text for Brian's DM (marks gaps reported)
  GET  /search?q=       retrieval only (debug / eval)
  GET  /stats
"""
import re
import threading
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import agent
from db import apply_schema, get_conn
from indexer import index_teaching, run_index
from search import search
from settings import S
from wiki import Wiki

app = FastAPI(title='DigiBot')
_index_lock = threading.Lock()


@app.on_event('startup')
def _startup():
    apply_schema()


class Turn(BaseModel):
    role: str
    text: str
    user: str | None = None


class AnswerReq(BaseModel):
    question: str
    user: str | None = None
    channel: str | None = None
    ts: str | None = None
    channel_type: str | None = None     # 'im' for DMs
    event_type: str | None = None       # 'message' | 'app_mention'
    history: list[Turn] = []


class TeachReq(BaseModel):
    text: str
    user: str
    question: str | None = None
    slack_link: str | None = None


class ReactionReq(BaseModel):
    reaction: str
    user: str
    channel: str
    ts: str
    message_text: str | None = None
    message_user: str | None = None
    is_bot_message: bool = False
    thread_root_text: str | None = None
    slack_link: str | None = None


def _seen(key: str) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('INSERT INTO seen_events(key) VALUES(%s) ON CONFLICT DO NOTHING RETURNING key', (key,))
        hit = cur.fetchone() is None
        conn.commit()
    return hit


TEACH_RE = re.compile(r'^\s*(?:<@[A-Z0-9]+>\s*)?teach\s*:\s*(.+)$', re.I | re.S)


def _teach(text: str, user: str, question: str | None, link: str | None) -> dict:
    if user not in S.teachers:
        return {'ok': False, 'text': "Only Brian can teach me for now. I've logged it as a suggestion for him."}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('INSERT INTO teachings(text,question,taught_by,slack_link) VALUES(%s,%s,%s,%s) RETURNING id',
                    (text.strip(), question, user, link))
        tid = cur.fetchone()[0]
        conn.commit()
        index_teaching(conn, tid, text.strip(), question)
    return {'ok': True, 'id': tid, 'text': f"Got it — teaching #{tid} saved and searchable now. It'll show on the teachings inbox page tonight."}


@app.get('/health')
def health():
    return {'ok': True, 'models': S.models, 'home_channel': S.home_channel}


def _should_answer(req: AnswerReq) -> str | None:
    """Return a skip reason, or None to answer."""
    if S.bot_user_id and req.user == S.bot_user_id:
        return 'own message'
    text = req.question
    mentioned = (f'<@{S.bot_user_id}>' in text) if S.bot_user_id else bool(re.search(r'<@[A-Z0-9]+>', text))
    is_dm = req.channel_type == 'im'
    is_home = bool(S.home_channel) and req.channel == S.home_channel
    if req.event_type == 'message' and mentioned and not is_dm:
        return 'mention handled by app_mention event'
    if not (req.event_type == 'app_mention' or is_dm or is_home):
        return 'not a DM, mention, or home-channel message'
    return None


@app.post('/answer')
def post_answer(req: AnswerReq):
    why = _should_answer(req)
    if why:
        return {'skip': True, 'reason': why}
    if req.channel and req.ts and _seen(f'{req.channel}:{req.ts}'):
        return {'skip': True, 'reason': 'duplicate event'}
    q = req.question.strip()
    m = TEACH_RE.match(q)
    if m:
        root = req.history[0].text if req.history else None
        link = f'{req.channel}/{req.ts}' if req.channel else None
        r = _teach(m.group(1), req.user or '', root, link)
        if not r['ok']:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute('INSERT INTO gaps(question,reason,asked_by,channel,ts) VALUES(%s,%s,%s,%s,%s)',
                            (m.group(1)[:1000], 'teach attempt by non-teacher', req.user, req.channel, req.ts))
                conn.commit()
        return {'text': r['text'], 'figures': [], 'mode': 'teach'}
    q = re.sub(r'<@[A-Z0-9]+>', '', q).strip()
    if not q:
        return {'text': "Ask me anything about the Q225 — patching, snapshots, Mustard, the racks, what a light means.", 'figures': [], 'mode': 'empty'}
    try:
        hist = []
        for t in req.history:
            role = 'assistant' if (t.role == 'assistant' or (S.bot_user_id and t.user == S.bot_user_id)) else 'user'
            hist.append({'role': role, 'text': t.text})
        out = agent.answer(q, hist, req.user, req.channel, req.ts)
    except agent.RateLimited as e:
        return {'text': "I'm rate-limited right now (free tier). Give it a minute and ask again.", 'figures': [], 'mode': 'ratelimited', 'error': str(e)[:200]}
    out['mode'] = 'answer'
    return out


@app.post('/teach')
def post_teach(req: TeachReq):
    return _teach(req.text, req.user, req.question, req.slack_link)


@app.post('/reaction')
def post_reaction(req: ReactionReq):
    key = f'reaction:{req.channel}:{req.ts}:{req.user}:{req.reaction}'
    if _seen(key):
        return {'skip': True}
    if req.reaction in ('pushpin', 'round_pushpin') and req.user in S.teachers and req.message_text:
        r = _teach(req.message_text, req.user, req.thread_root_text, req.slack_link)
        return {'mode': 'teach', **r}
    if req.reaction in ('+1', 'thumbsup', '-1', 'thumbsdown') and req.is_bot_message:
        fb = 'up' if req.reaction in ('+1', 'thumbsup') else 'down'
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute('UPDATE qa_log SET feedback=%s WHERE channel=%s AND reply_ts=%s', (fb, req.channel, req.ts))
            n = cur.rowcount
            conn.commit()
        return {'mode': 'feedback', 'feedback': fb, 'matched': n}
    return {'mode': 'ignored'}


class ReplyTs(BaseModel):
    qa_id: int
    reply_ts: str


@app.post('/answer/posted')
def answer_posted(req: ReplyTs):
    """n8n calls this after posting the reply so 👍/👎 on the reply can be matched back."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('UPDATE qa_log SET reply_ts=%s WHERE id=%s', (req.reply_ts, req.qa_id))
        conn.commit()
    return {'ok': True}


@app.post('/index')
def post_index():
    if not _index_lock.acquire(blocking=False):
        raise HTTPException(409, 'index already running')
    try:
        return run_index()
    finally:
        _index_lock.release()


@app.post('/inbox/rebuild')
def inbox_rebuild():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT id, text, question, created_at, slack_link FROM teachings WHERE NOT folded ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.execute('SELECT question, reason, created_at FROM gaps ORDER BY created_at DESC LIMIT 40')
        gaps = cur.fetchall()
    lines = ['# Teachings inbox', '',
             "Things Brian taught DigiBot in Slack that haven't been folded into a proper page yet. "
             'DigiBot already answers from these. Move one into the right venue or how-to page, then mark it folded '
             '(`UPDATE teachings SET folded=true WHERE id=N` on the digibot database) and it drops off this list.', '']
    if not rows:
        lines.append('_Nothing waiting._')
    for tid, text, q, created, link in rows:
        lines.append(f'## #{tid} — {created.strftime("%Y-%m-%d")}')
        lines.append(text.strip())
        if q:
            lines.append(f'\n_Asked in the thread:_ {q.strip()[:300]}')
        lines.append('')
    lines += ['', '## Recent gaps (questions the wiki could not answer)', '']
    if not gaps:
        lines.append('_None logged._')
    for q, reason, created in gaps:
        lines.append(f'- {created.strftime("%Y-%m-%d")} — {q.strip()[:200]}' + (f' _({reason.strip()[:120]})_' if reason else ''))
    w = Wiki(S.digico_wiki_url, S.digico_wiki_key, S.digico_public_url)
    url = w.upsert_page(S.inbox_path, 'Teachings inbox', 'What Brian has taught DigiBot that is not on a real page yet, plus recent unanswered questions',
                        '\n'.join(lines), ['digibot'])
    return {'ok': True, 'url': url, 'teachings': len(rows), 'gaps': len(gaps)}


@app.get('/gaps/digest')
def gaps_digest():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT id, question, reason, asked_by, created_at FROM gaps WHERE NOT reported ORDER BY created_at')
        rows = cur.fetchall()
        cur.execute("SELECT count(*), count(*) FILTER (WHERE feedback='up'), count(*) FILTER (WHERE feedback='down') FROM qa_log WHERE created_at > now() - interval '7 days'")
        n, up, down = cur.fetchone()
        cur.execute('SELECT count(*) FROM teachings WHERE NOT folded')
        unfolded = cur.fetchone()[0]
        if rows:
            cur.execute('UPDATE gaps SET reported=true WHERE id = ANY(%s)', ([r[0] for r in rows],))
        conn.commit()
    week = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    text = [f'*DigiBot week ending {week}* — {n} questions, {up} 👍 / {down} 👎, {unfolded} teachings waiting on the inbox page.']
    if rows:
        text.append(f'\n*{len(rows)} things the wiki couldn\'t answer:*')
        for _id, q, reason, who, created in rows[:25]:
            text.append(f'• {q.strip()[:180]}' + (f' — _{reason.strip()[:80]}_' if reason else ''))
        if len(rows) > 25:
            text.append(f'…and {len(rows) - 25} more on the inbox page.')
    else:
        text.append('No gaps logged this week.')
    text.append(f'\nInbox: {S.digico_public_url}/{S.inbox_path}')
    return {'text': '\n'.join(text), 'gaps': len(rows), 'questions': n}


@app.get('/search')
def get_search(q: str, k: int = 6):
    return {'results': [{k2: v for k2, v in r.items() if k2 != 'text'} | {'text': r['text'][:300]} for r in search(q, k)]}


@app.get('/stats')
def stats():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('SELECT source, count(*) FROM pages GROUP BY source'); pages = dict(cur.fetchall())
        cur.execute('SELECT tier, count(*) FROM chunks GROUP BY tier ORDER BY tier'); tiers = {str(t): c for t, c in cur.fetchall()}
        cur.execute('SELECT count(*) FROM qa_log'); qa = cur.fetchone()[0]
        cur.execute('SELECT count(*) FROM teachings'); te = cur.fetchone()[0]
        cur.execute('SELECT count(*) FROM gaps WHERE NOT reported'); g = cur.fetchone()[0]
    return {'pages': pages, 'chunks_by_tier': tiers, 'questions': qa, 'teachings': te, 'gaps_unreported': g}
