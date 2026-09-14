#!/usr/bin/env python3
"""Generate the three DigiBot n8n workflows + the placeholder Slack credential.
Run after any edit:  python3 n8n/gen_workflows.py   (writes n8n/*.json next to this file)

Why generated: n8n's JSON is verbose and the node shapes repeat; one Python file is easier to keep
correct than three hand-edited exports. Every Slack call is an HTTP Request node using the
predefined `slackApi` credential (bot token) so the token lives only inside n8n.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
API = 'http://192.168.200.84:8098'
CRED = {'slackApi': {'id': 'DigiBotSlack', 'name': 'DigiBot Slack (bot token + signing secret)'}}
OWNER = 'UHSLD08SV'
WEBHOOK_ID = 'digibot-slack-events'


def node(name, typ, ver, params, pos, extra=None):
    n = {'parameters': params, 'name': name, 'type': typ, 'typeVersion': ver, 'position': pos, 'id': name.lower().replace(' ', '-')}
    if extra:
        n.update(extra)
    return n


def http(name, method, url, pos, body=None, slack=False, timeout=60000, query=None, cont=False):
    p = {'method': method, 'url': url, 'options': {'timeout': timeout}}
    if slack:
        p['authentication'] = 'predefinedCredentialType'; p['nodeCredentialType'] = 'slackApi'
    if body is not None:
        p.update({'sendBody': True, 'specifyBody': 'json', 'jsonBody': body})
    if query:
        p.update({'sendQuery': True, 'queryParameters': {'parameters': [{'name': k, 'value': v} for k, v in query.items()]}})
    extra = {'credentials': CRED} if slack else {}
    if cont:
        extra['onError'] = 'continueRegularOutput'
    return node(name, 'n8n-nodes-base.httpRequest', 4.2, p, pos, extra)


def code(name, js, pos):
    return node(name, 'n8n-nodes-base.code', 2, {'jsCode': js}, pos)


def wf(wid, name, nodes, connections, active=True):
    return {'id': wid, 'name': name, 'nodes': nodes, 'connections': connections, 'active': active,
            'settings': {'executionOrder': 'v1', 'saveManualExecutions': True, 'saveDataErrorExecution': 'all'}, 'pinData': {}}


def link(conns, a, b, out=0):
    conns.setdefault(a, {'main': []})
    while len(conns[a]['main']) <= out:
        conns[a]['main'].append([])
    conns[a]['main'][out].append({'node': b, 'type': 'main', 'index': 0})


# ------------------------------------------------------------------------------------------------
# 1. DigiBot — Slack (events in, replies out)
# ------------------------------------------------------------------------------------------------
ROUTE = r"""
// Slack Trigger emits the raw event. Drop junk here; the service applies the DM / home-channel /
// mention rules (it knows the bot's user id and the home channel from its own .env).
const ev = $input.first().json;
const t = ev.type;
if (t === 'reaction_added') {
  const ok = ['pushpin','round_pushpin','+1','thumbsup','-1','thumbsdown'].includes(ev.reaction);
  if (!ok || !ev.item || ev.item.type !== 'message') return [];
  return [{ json: { kind: 'reaction', reaction: ev.reaction, user: ev.user, channel: ev.item.channel, ts: ev.item.ts, item_user: ev.item_user || '' } }];
}
if (t !== 'message' && t !== 'app_mention') return [];
if (ev.bot_id || (ev.subtype && ev.subtype !== 'file_share')) return [];
const text = (ev.text || '').trim();
if (!text) return [];
return [{ json: { kind: 'question', event_type: t, text, user: ev.user, channel: ev.channel, channel_type: ev.channel_type || '',
                  ts: ev.ts, thread_ts: ev.thread_ts || ev.ts, is_thread: !!ev.thread_ts } }];
"""

BUILD_Q = r'''
// Turn the thread replies into history and package the request for the service.
const r = $('Route').first().json;
const msgs = ($input.first().json.messages || []);
const history = [];
for (const m of msgs) {
  if (m.ts === r.ts) continue;                                   // the message we are answering
  const txt = (m.text || '').replace(/<@[A-Z0-9]+>/g, '').trim();
  if (!txt) continue;
  history.push({ role: m.bot_id ? 'assistant' : 'user', text: txt.slice(0, 1200), user: m.user || '' });
}
return [{ json: { question: r.text, user: r.user, channel: r.channel, channel_type: r.channel_type, event_type: r.event_type, ts: r.ts, history: history.slice(-8) } }];
'''

COMPOSE = r'''
const a = $input.first().json;
if (a.skip) return [];
const r = $('Route').first().json;
const blocks = [{ type: 'section', text: { type: 'mrkdwn', text: (a.text || '').slice(0, 2900) } }];
for (const f of (a.figures || []).slice(0, 2)) blocks.push({ type: 'image', image_url: f, alt_text: 'wiki figure' });
return [{ json: { channel: r.channel, thread_ts: r.thread_ts, text: (a.text || '').slice(0, 2900), blocks, unfurl_links: false, unfurl_media: false, qa_id: a.qa_id || null } }];
'''

POSTED = r'''
const posted = $input.first().json;
const qa = $('Compose Reply').first().json.qa_id;
if (!posted.ok || !qa) return [];
return [{ json: { qa_id: qa, reply_ts: posted.ts } }];
'''

BUILD_R = r'''
const r = $('Route').first().json;
const m = ($input.first().json.messages || [])[0] || {};
return [{ json: { reaction: r.reaction, user: r.user, channel: r.channel, ts: r.ts,
  message_text: (m.text || '').replace(/<@[A-Z0-9]+>/g, '').trim(), message_user: m.user || '', is_bot_message: !!m.bot_id,
  thread_root_text: null, slack_link: r.channel + '/' + r.ts } }];
'''

TEACH_ACK = r'''
const a = $input.first().json;
if (a.mode !== 'teach' || !a.text) return [];
const r = $('Route').first().json;
return [{ json: { channel: r.channel, thread_ts: r.ts, text: a.text } }];
'''

nodes = [
    node('Slack Events', 'n8n-nodes-base.slackTrigger', 1,
         {'trigger': ['app_mention', 'message', 'reaction_added'], 'watchWorkspace': True, 'options': {}},
         [0, 300], {'webhookId': WEBHOOK_ID, 'credentials': CRED}),
    code('Route', ROUTE, [240, 300]),
    node('Is Reaction?', 'n8n-nodes-base.if', 2.2,
         {'conditions': {'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'loose', 'version': 2},
                         'conditions': [{'id': 'c1', 'leftValue': '={{ $json.kind }}', 'rightValue': 'reaction',
                                         'operator': {'type': 'string', 'operation': 'equals'}}], 'combinator': 'and'},
          'options': {}}, [480, 300]),
    # question branch
    http('Get Thread', 'GET', 'https://slack.com/api/conversations.replies', [740, 420], slack=True,
         query={'channel': '={{ $json.channel }}', 'ts': '={{ $json.thread_ts }}', 'limit': '20'}),
    code('Build Question', BUILD_Q, [980, 420]),
    http('Ask DigiBot', 'POST', API + '/answer', [1220, 420], body='={{ JSON.stringify($json) }}', timeout=180000),
    code('Compose Reply', COMPOSE, [1460, 420]),
    http('Post Reply', 'POST', 'https://slack.com/api/chat.postMessage', [1700, 420], slack=True,
         body='={{ JSON.stringify({channel:$json.channel, thread_ts:$json.thread_ts, text:$json.text, blocks:$json.blocks, unfurl_links:false, unfurl_media:false}) }}'),
    code('Reply Posted', POSTED, [1940, 420]),
    http('Record Reply Ts', 'POST', API + '/answer/posted', [2180, 420], body='={{ JSON.stringify($json) }}', cont=True),
    # reaction branch
    http('Get Reacted Message', 'GET', 'https://slack.com/api/conversations.replies', [740, 160], slack=True,
         query={'channel': '={{ $json.channel }}', 'ts': '={{ $json.ts }}', 'limit': '1', 'inclusive': 'true'}),
    code('Build Reaction', BUILD_R, [980, 160]),
    http('Send Reaction', 'POST', API + '/reaction', [1220, 160], body='={{ JSON.stringify($json) }}', cont=True),
    code('Teach Ack', TEACH_ACK, [1460, 160]),
    http('Post Teach Ack', 'POST', 'https://slack.com/api/chat.postMessage', [1700, 160], slack=True,
         body='={{ JSON.stringify({channel:$json.channel, thread_ts:$json.thread_ts, text:$json.text}) }}'),
]
c = {}
link(c, 'Slack Events', 'Route'); link(c, 'Route', 'Is Reaction?')
link(c, 'Is Reaction?', 'Get Reacted Message', 0); link(c, 'Is Reaction?', 'Get Thread', 1)
for a, b in [('Get Thread', 'Build Question'), ('Build Question', 'Ask DigiBot'), ('Ask DigiBot', 'Compose Reply'),
             ('Compose Reply', 'Post Reply'), ('Post Reply', 'Reply Posted'), ('Reply Posted', 'Record Reply Ts'),
             ('Get Reacted Message', 'Build Reaction'), ('Build Reaction', 'Send Reaction'), ('Send Reaction', 'Teach Ack'),
             ('Teach Ack', 'Post Teach Ack')]:
    link(c, a, b)
slack_wf = wf('digibot_slack', 'DigiBot — Slack', nodes, c)

# ------------------------------------------------------------------------------------------------
# 2. Nightly re-index + inbox page (03:40)
# ------------------------------------------------------------------------------------------------
n2 = [
    node('Every night 03:40', 'n8n-nodes-base.scheduleTrigger', 1.2,
         {'rule': {'interval': [{'field': 'cronExpression', 'expression': '40 3 * * *'}]}}, [0, 300]),
    http('Reindex Wikis', 'POST', API + '/index', [260, 300], body='{}', timeout=900000, cont=True),
    http('Rebuild Inbox Page', 'POST', API + '/inbox/rebuild', [520, 300], body='{}', timeout=120000, cont=True),
]
c2 = {}; link(c2, 'Every night 03:40', 'Reindex Wikis'); link(c2, 'Reindex Wikis', 'Rebuild Inbox Page')
nightly_wf = wf('digibot_nightly', 'DigiBot — Nightly Reindex', n2, c2)

# ------------------------------------------------------------------------------------------------
# 3. Weekly gaps digest to Brian (Monday 08:00)
# ------------------------------------------------------------------------------------------------
n3 = [
    node('Monday 08:00', 'n8n-nodes-base.scheduleTrigger', 1.2,
         {'rule': {'interval': [{'field': 'cronExpression', 'expression': '0 8 * * 1'}]}}, [0, 300]),
    http('Get Digest', 'GET', API + '/gaps/digest', [260, 300], timeout=60000),
    http('DM Brian', 'POST', 'https://slack.com/api/chat.postMessage', [520, 300], slack=True,
         body='={{ JSON.stringify({channel:"' + OWNER + '", text:$json.text, unfurl_links:false}) }}'),
]
c3 = {}; link(c3, 'Monday 08:00', 'Get Digest'); link(c3, 'Get Digest', 'DM Brian')
weekly_wf = wf('digibot_weekly', 'DigiBot — Weekly Gaps Digest', n3, c3)

# ------------------------------------------------------------------------------------------------
creds = [{'id': 'DigiBotSlack', 'name': CRED['slackApi']['name'], 'type': 'slackApi',
          'data': {'accessToken': 'xoxb-PASTE-THE-BOT-TOKEN', 'signatureSecret': 'PASTE-THE-SIGNING-SECRET'}}]

for fn, obj in [('digibot_slack.json', slack_wf), ('digibot_nightly.json', nightly_wf), ('digibot_weekly.json', weekly_wf),
                ('credentials_digibot.json', creds)]:
    json.dump(obj, open(os.path.join(HERE, fn), 'w'), indent=2)
    print('wrote', fn)
