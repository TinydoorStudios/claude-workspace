// Paste this into the "Normalize" Code node (mode: Run Once for Each Item is fine,
// but "Run Once for All Items" also works since we read explicit node refs).
// Input to this node = the "Render DOCX → Dropbox" HTTP response.
// Original form payload = the webhook body.

const body = $node['Form Webhook'].json.body || {};
const f = body.fields || {};
const render = $json || {};

const num = (v) => {
  const n = parseInt(String(v ?? '').replace(/[^0-9-]/g, ''), 10);
  return Number.isFinite(n) ? n : null;
};
const detail = (yn, det) => {
  const a = f[yn] || '';
  const b = f[det] || '';
  return b ? `${a} — ${b}` : a;
};

const acks = {};
for (const k of Object.keys(f)) {
  if (k.startsWith('ACK:') && f[k]) acks[k.replace('ACK: ', '')] = true;
}

const email = body.email || f['__email'] || '';
const venue = body.venue || f['Venue'] || '';
const act = body.act || f['Act / band name'] || '';
const showDate = body.date || f['Show date'] || '';
const advanceDoc = render.dropbox_link || render.dropbox_path || '';

// $1..$20 — must match the INSERT column order in Insert Submission
const q = [
  email,
  venue,
  act,
  showDate,
  f['Advancing contact — your name'] || '',
  f['Best phone to reach the band day-of'] || '',
  num(f['Total number of performers']),
  detail('Do you need large-vehicle parking?', 'If yes — vehicle type / size'),
  f['Stage plot / input list — link (optional)'] || '',
  f['Monitor needs'] || '',
  detail('Are you bringing your own engineer?', 'If yes — engineer name & what they’re mixing (FOH/MON)'),
  f['Are you selling merch?'] || '',
  f['Would you like a 10x10 private tent with sidewalls?'] || '',
  num(f['Total wristbands needed']),
  f['Band representative with stage-escort ability — name'] || '',
  detail('Any special guest performers?', 'If yes — who, and doing what?'),
  f['Notes / questions'] || '',
  JSON.stringify(acks),
  JSON.stringify(body),
  advanceDoc,
];

// $1..$4 for the "Match & Flip Show → Received" update
const match = [advanceDoc, email, act, venue];

return [{ json: { q, match, act, venue, show_date: showDate, advance_doc: advanceDoc } }];
