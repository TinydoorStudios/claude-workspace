"""The answering loop: pre-retrieve for the question, then one Groq call with tools available
(search_wiki / read_page / log_gap) for the cases where the first retrieval wasn't enough.

Built to live inside Groq's free-tier limits: the system prompt is short, chunks are trimmed to
~1500 chars, six chunks max, and most questions finish in a single call. On a 429 the next model
in DIGIBOT_MODELS is tried, then the caller gets a RateLimited so the bot can say so.
"""
import json
import re
import time

import httpx

from db import get_conn
from search import page_index, read_page, search
from settings import S

SYSTEM = """You are DigiBot, the help desk for the DiGiCo Quantum 225 console used by the 3CDC / Tiny Door Studios crew at Memorial Hall and Fountain Square. You answer from the wiki excerpts you are given and from the tools. You never invent button names, menu paths, or settings.

Rules:
- Answer only from the excerpts and tool results. If they don't cover the question, say "The wiki doesn't cover this yet" and call log_gap. Don't guess.
- Sources have tiers. Staff teachings from Brian (tier 4) and venue / KB pages (tier 3) describe how WE do it and outrank the manual (tier 1). When they disagree, follow the venue page and say so.
- Write like a colleague at the desk: short, direct, numbered steps for procedures, the panel and button names exactly as the wiki writes them (e.g. Layout > Channel List, the "main input" button). No preamble, no filler, no bullet lists of caveats.
- Slack mrkdwn only: *bold*, _italic_, `code`, numbered lines. No markdown headers, no tables, no ** double asterisks.
- End with a "Source:" line listing the page title(s) you used as Slack links: <url|Title>. One line, up to three links.
- If the question is about something that would change a live show mid-performance (recalling snapshots, loading sessions, resetting, re-patching, changing clocking), add one line: if it's show time, call Brian before doing it.
- If the user is just chatting or thanking you, reply in one short line with no Source line.

Curated pages that exist (search or read_page them by path when relevant):
{page_index}
"""

TOOLS = [
    {'type': 'function', 'function': {
        'name': 'search_wiki',
        'description': 'Search the Q225 wiki (manual, how-to pages, venue pages, staff teachings) for a different phrasing or a sub-topic. Returns the best-matching excerpts with page URLs.',
        'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}},
    {'type': 'function', 'function': {
        'name': 'read_page',
        'description': 'Read one full wiki page by its path (e.g. how-to/20-snapshots) when an excerpt is cut off or a multi-step procedure needs the whole page.',
        'parameters': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}}},
    {'type': 'function', 'function': {
        'name': 'log_gap',
        'description': 'Record that the wiki could not answer this question, so Brian knows what to write next. Call it whenever you have to say the wiki does not cover something.',
        'parameters': {'type': 'object', 'properties': {'question': {'type': 'string'}, 'reason': {'type': 'string'}}, 'required': ['question']}}},
]


class RateLimited(Exception):
    pass


def _fmt_chunks(chunks: list[dict], max_chars: int | None = None) -> str:
    parts = []
    for c in chunks:
        tier_name = {4: 'STAFF TEACHING', 3: 'VENUE / OUR WORKFLOW', 2: 'HOW-TO', 1: 'MANUAL'}.get(c['tier'], 'MANUAL')
        text = c['text'][:(max_chars or S.chunk_chars_in_prompt)]
        figs = (' | figures: ' + ', '.join(S.digico_public_url + f for f in c['figures'])) if c['figures'] else ''
        parts.append(f"[{tier_name}] {c['title']} — {c['url']}{figs}\n{text}")
    return '\n\n---\n\n'.join(parts)


def _groq(model: str, messages: list[dict], tools: list[dict] | None) -> dict:
    body = {'model': model, 'messages': messages, 'temperature': 0.2, 'max_tokens': 900}
    if tools:
        body['tools'] = tools; body['tool_choice'] = 'auto'
    r = httpx.post(S.groq_url, headers={'Authorization': 'Bearer ' + S.groq_key, 'Content-Type': 'application/json'},
                   json=body, timeout=90)
    if r.status_code in (400, 404, 413, 429, 498, 500, 502, 503):
        # 404/400 = model gone or rejected the request (Groq retires models without notice);
        # 413/429/498/503 = over the free-tier limit. Either way: try the next model.
        raise RateLimited(f'{model}: HTTP {r.status_code} {r.text[:200]}')
    r.raise_for_status()
    return r.json()


def _call(messages, tools):
    """Walk the model list; if every model is over its per-minute limit, wait once and walk it again."""
    last = None
    for attempt in range(2):
        for model in S.models:
            try:
                resp = _groq(model, messages, tools)
                return model, resp
            except RateLimited as e:
                last = e
                time.sleep(1)
        if attempt == 0:
            time.sleep(S.retry_wait_s)
    raise last or RateLimited('no models configured')


def slackify(text: str) -> str:
    """Models drift into markdown; Slack wants mrkdwn."""
    text = re.sub(r'\*\*([^*\n]+)\*\*', r'*\1*', text)          # **bold** → *bold*
    text = re.sub(r'^#{1,6}\s+(.+)$', r'*\1*', text, flags=re.M)  # headers → bold line
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.M)         # - bullets → •
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<\2|\1>', text)  # md links → slack links
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _log_gap(question: str, reason: str | None, who: str | None, channel: str | None, ts: str | None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('INSERT INTO gaps(question,reason,asked_by,channel,ts) VALUES(%s,%s,%s,%s,%s)',
                    (question[:1000], (reason or '')[:500], who, channel, ts))
        conn.commit()


def answer(question: str, history: list[dict] | None = None, who: str | None = None,
           channel: str | None = None, ts: str | None = None) -> dict:
    """history: [{'role': 'user'|'assistant', 'text': ...}] — earlier turns of the Slack thread."""
    t0 = time.time()
    idx = page_index()
    idx_lines = '\n'.join(f"- {p['title']} — {p['path']}" for p in idx[:60])
    system = SYSTEM.replace('{page_index}', idx_lines)

    retrieval_q = question if not history else (history[0]['text'][:200] + ' ' + question)
    chunks = search(retrieval_q)
    chunk_ids = [c['id'] for c in chunks]
    figures = []
    for c in chunks[:3]:
        for f in c['figures']:
            if f not in figures:
                figures.append(f)

    messages = [{'role': 'system', 'content': system}]
    for h in (history or [])[-6:]:
        messages.append({'role': h['role'], 'content': h['text'][:1200]})
    messages.append({'role': 'user', 'content': f"Question: {question}\n\nWiki excerpts:\n\n{_fmt_chunks(chunks)}"})

    tool_log, model_used, usage = [], None, {'in': 0, 'out': 0}
    for _round in range(S.max_tool_rounds + 1):
        model_used, resp = _call(messages, TOOLS if _round < S.max_tool_rounds else None)
        u = resp.get('usage', {})
        usage['in'] += u.get('prompt_tokens', 0); usage['out'] += u.get('completion_tokens', 0)
        msg = resp['choices'][0]['message']
        calls = msg.get('tool_calls') or []
        if not calls:
            text = (msg.get('content') or '').strip()
            break
        messages.append({'role': 'assistant', 'content': msg.get('content') or '', 'tool_calls': calls})
        for call in calls:
            name = call['function']['name']
            try:
                args = json.loads(call['function']['arguments'] or '{}')
            except json.JSONDecodeError:
                args = {}
            if name == 'search_wiki':
                res = [c for c in search(args.get('query', question), S.top_k) if c['id'] not in chunk_ids][:4]
                chunk_ids.extend(c['id'] for c in res)
                result = _fmt_chunks(res, 900) if res else 'Nothing new beyond the excerpts you already have.'
            elif name == 'read_page':
                p = read_page(args.get('path', ''))
                result = f"{p['title']} — {p['url']}\n\n{p['content'][:4500]}" if p else 'No such page.'
            elif name == 'log_gap':
                _log_gap(args.get('question', question), args.get('reason'), who, channel, ts)
                result = 'Logged.'
            else:
                result = 'Unknown tool.'
            tool_log.append({'tool': name, 'args': args})
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'name': name, 'content': result[:7000]})
    else:
        text = (msg.get('content') or '').strip() or "I couldn't put an answer together. Try rephrasing, or ask Brian."

    if not text:
        text = "I couldn't put an answer together. Try rephrasing, or ask Brian."
    text = slackify(text)
    latency = int((time.time() - t0) * 1000)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('''INSERT INTO qa_log(channel,ts,asked_by,question,answer,model,chunk_ids,tool_calls,tokens_in,tokens_out,latency_ms)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (channel, ts) DO UPDATE SET answer=EXCLUDED.answer, model=EXCLUDED.model
                       RETURNING id''',
                    (channel, ts, who, question, text, model_used, chunk_ids, json.dumps(tool_log),
                     usage['in'], usage['out'], latency))
        qa_id = cur.fetchone()[0]
        conn.commit()
    show_figs = [S.digico_public_url + f for f in figures[:2]] if 'Source:' in text else []
    return {'text': text, 'figures': show_figs, 'model': model_used, 'qa_id': qa_id,
            'chunk_ids': chunk_ids, 'tool_calls': tool_log, 'tokens': usage, 'latency_ms': latency}
