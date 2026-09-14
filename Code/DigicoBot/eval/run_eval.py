#!/usr/bin/env python3
"""Retrieval eval: does the expected page land in the top-k for each question?
    python3 eval/run_eval.py [--answers]   (--answers also runs the LLM and prints the reply; costs Groq quota)
Against the live service on the VM (DIGIBOT_URL, default http://192.168.200.84:8098)."""
import json, os, sys, urllib.request, urllib.parse
URL = os.environ.get('DIGIBOT_URL', 'http://192.168.200.84:8098')
answers = '--answers' in sys.argv
hits = 0; rows = [json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), 'questions.jsonl')) if l.strip()]
for r in rows:
    res = json.load(urllib.request.urlopen(f"{URL}/search?q={urllib.parse.quote(r['q'])}&k=6", timeout=60))['results']
    paths = [x['path'] for x in res]
    rank = next((i + 1 for i, p in enumerate(paths) if p.endswith(r['expect'])), None)
    hits += bool(rank)
    print(f"{'ok ' if rank else 'MISS'} @{rank or '-'}  {r['q']}   → {paths[0] if paths else '-'}")
    if answers:
        req = urllib.request.Request(f'{URL}/answer', data=json.dumps({'question': r['q'], 'event_type': 'app_mention', 'user': 'eval', 'channel': 'eval', 'ts': str(hash(r['q']))}).encode(), headers={'Content-Type': 'application/json'})
        a = json.load(urllib.request.urlopen(req, timeout=180))
        print('    ', (a.get('text') or a.get('reason') or '')[:400].replace('\n', '\n     '), '\n')
print(f'\n{hits}/{len(rows)} expected pages in top 6')
