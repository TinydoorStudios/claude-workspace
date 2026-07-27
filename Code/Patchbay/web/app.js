/* Patchbay — app core: state, API, hash router, sidebar, autosave.
   Page renderers live in pages.js; the new-sheet wizard in wizard.js.

   Two rules this codebase learned the hard way:
     • never put draggable on a <tr> — WebKit swallows clicks into its fields
     • never re-render a table from a change handler — it eats what's being typed
   Edit handlers mutate S.sheet and call touch(); repaints happen on navigation. */

const S = {
  kb: null,
  sheets: [],
  sheet: null,
  analyses: [],
  route: { page: 'dashboard', id: null, ci: 0 },
  dirty: false,
  saving: false,
  pending: false,
  editSeq: 0,
  theme: 'dark',
  matrix: { dir: 'inputs', field: 'port' },
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const uid = () => Math.random().toString(16).slice(2, 10);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const api = async (url, opts = {}) => {
  const r = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!r.ok) throw Object.assign(new Error(await r.text()), { status: r.status });
  return r.headers.get('content-type')?.includes('json') ? r.json() : r.text();
};

/* ------------------------------------------------------------ boot */
async function boot() {
  setTheme(localStorage.getItem('patchbay.theme') || 'dark');
  $('#theme').onclick = () => setTheme(S.theme === 'light' ? 'dark' : 'light');
  S.kb = await api('/api/bootstrap');
  fillDatalist('#miclist', S.kb.mics.map((m) => m.name));
  fillDatalist('#standlist', S.kb.stands);
  fillDatalist('#venuelist', S.kb.venues.map((v) => v.label));
  await refreshList();
  window.addEventListener('hashchange', () => route());
  await route();
}

function fillDatalist(sel, values) {
  $(sel).innerHTML = values.map((v) => `<option value="${esc(v)}">`).join('');
}
const consoleDef = (id) => S.kb.consoles.find((c) => c.id === id) || S.kb.consoles[0];
const venueDef = (id) => S.kb.venues.find((v) => v.id === id);

function setTheme(mode) {
  S.theme = mode;
  document.documentElement.dataset.theme = mode;
  localStorage.setItem('patchbay.theme', mode);
  $('#theme').textContent = mode === 'light' ? '☀' : '☾';
}

/* ---------------------------------------------------------- routing */
async function route() {
  const hash = location.hash.replace(/^#\/?/, '');
  const parts = hash.split('/').filter(Boolean);
  let r = { page: 'dashboard', id: null, ci: 0 };

  if (parts[0] === 's' && parts[1]) {
    r.id = parts[1];
    if (parts[2] === 'c') {
      r.ci = parseInt(parts[3] || '0', 10) || 0;
      r.page = 'console-' + (parts[4] || 'info');
    } else {
      r.page = parts[2] || 'overview';
    }
  }
  S.route = r;

  if (r.id && (!S.sheet || S.sheet.id !== r.id)) {
    try {
      await openSheet(r.id);
    } catch {
      location.hash = '#/';
      return;
    }
  }
  if (!r.id) S.sheet = null;
  renderSidebar();
  renderPage();
}

const go = (path) => { location.hash = path; };
const sheetPath = (sub = '') => `#/s/${S.sheet.id}${sub}`;

async function openSheet(id) {
  const { sheet, analyses } = await api(`/api/sheets/${id}`);
  S.sheet = sheet;
  S.analyses = analyses || [];
  S.dirty = false;
  localStorage.setItem('patchbay.last', id);
  setSaveState('');
}

async function refreshList() {
  const { sheets } = await api('/api/sheets');
  S.sheets = sheets;
}

/* ------------------------------------------------------------ save */
const isLocked = () => !!S.sheet?.locked;

async function setLock(locked) {
  const res = await api(`/api/sheets/${S.sheet.id}/lock`, { method: 'POST', body: { locked } });
  S.sheet = res.sheet;
  S.analyses = res.analyses || [];
  await refreshList();
  renderSidebar();
  renderPage();
  setSaveState('saved', locked ? 'Template locked' : 'Unlocked for editing');
}

function touch() {
  // A locked template takes no edits — the server refuses them anyway.
  if (isLocked()) return;
  S.dirty = true;
  S.editSeq++;
  setSaveState('dirty', 'Unsaved changes');
  clearTimeout(touch._t);
  touch._t = setTimeout(saveNow, 700);
}

async function saveNow(bump = false) {
  if (!S.sheet) return;
  if (S.saving) { S.pending = true; return; }
  S.saving = true;
  const seq = S.editSeq;
  setSaveState('', 'Saving…');
  try {
    const res = await api(`/api/sheets/${S.sheet.id}`, { method: 'PUT', body: { sheet: S.sheet, bump } });
    S.analyses = res.analyses || [];
    // Never swap S.sheet for the server's copy — the painted rows hold references
    // into the live object, and replacing it strands every one of them (and eats
    // whatever was typed while the save was in flight). Only bookkeeping comes back.
    S.sheet.rev = res.sheet.rev;
    S.sheet.updated = res.sheet.updated;
    S.sheet.created = res.sheet.created;
    if (seq === S.editSeq) {
      S.dirty = false;
      setSaveState('saved', 'All changes saved');
    }
    await refreshList();
  } catch (err) {
    setSaveState('dirty', 'Save failed');
    console.error(err);
  } finally {
    S.saving = false;
    if (S.pending) { S.pending = false; saveNow(); }
  }
}

function setSaveState(cls, text) {
  const el = $('#savestate');
  el.className = 'savestate ' + (cls || '');
  el.textContent = S.sheet ? (text || '') : '';
  const t = $('#toast');
  if (cls === 'saved') {
    t.innerHTML = '<span class="ok">✓</span> All changes saved';
    t.hidden = false;
    clearTimeout(setSaveState._t);
    setSaveState._t = setTimeout(() => (t.hidden = true), 2200);
  }
}

/* --------------------------------------------------------- sidebar */
const ICONS = {
  compass: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20m4.2 5.8-1.8 5.4-5.4 1.8 1.8-5.4z',
  grid: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
  file: 'M6 2h8l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zM14 2v5h5M8 13h8M8 17h8',
  pin: 'M20 10c0 5-8 12-8 12s-8-7-8-12a8 8 0 0 1 16 0zM12 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.9',
  sliders: 'M4 6h16M4 12h16M4 18h16M8 4v4M15 10v4M11 16v4',
  map: 'M9 3 3 6v15l6-3 6 3 6-3V3l-6 3zM9 3v15M15 6v15',
  plug: 'M12 2v6M8 8h8v4a4 4 0 0 1-8 0zM12 16v6',
  table: 'M3 4h18v16H3zM3 10h18M9 10v10',
  power: 'M12 3v9M6 6a9 9 0 1 0 12 0',
  clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 2',
  down: 'M12 3v12M7 11l5 5 5-5M4 21h16',
};
const icon = (name) =>
  `<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round"><path d="${ICONS[name] || ICONS.grid}"/></svg>`;

function renderSidebar() {
  const side = $('#sidebar');
  if (!S.sheet) {
    side.innerHTML = `
      <div class="side-top"><span class="side-back">Patch sheets</span></div>
      <nav class="side-nav">
        <div class="side-link on" onclick="go('#/')">${icon('grid')}<span>All sheets</span></div>
        <div class="side-group">Sheets</div>
        ${S.sheets.map((s) => `<div class="side-link" onclick="go('#/s/${s.id}')">${icon('file')}<span>${esc(s.name)}</span></div>`).join('')}
      </nav>
      <div class="side-foot"><button class="btn primary sm" onclick="newSheet()">+ New Patch Sheet</button></div>`;
    $('#kindtag').hidden = true;
    return;
  }

  const p = S.route.page;
  const link = (page, label, ic, sub = '') =>
    `<div class="side-link ${p === page ? 'on' : ''}" onclick="go('${sheetPath(sub)}')">${icon(ic)}<span>${label}</span></div>`;

  const consoles = S.sheet.consoles.map((c, i) => {
    const open = S.route.ci === i && p.startsWith('console');
    const subLink = (key, label) =>
      `<div class="side-link sub ${p === 'console-' + key ? 'on' : ''}"
        onclick="go('#/s/${S.sheet.id}/c/${i}/${key}')"><span>${label}</span></div>`;
    return `
      <div class="side-link ${open ? 'on' : ''}" onclick="go('#/s/${S.sheet.id}/c/${i}/info')">
        ${icon('sliders')}<span>${esc(c.name || 'Console')}</span></div>
      ${open ? subLink('info', 'Console Info') + subLink('patch', 'Easy Patch') +
               subLink('inputs', 'Console Inputs') + subLink('outputs', 'Busses &amp; Outputs') : ''}`;
  }).join('');

  side.innerHTML = `
    <div class="side-top"><a class="side-back" href="#/">← Main Menu</a></div>
    <nav class="side-nav">
      <div class="side-title">${esc(S.sheet.name)}</div>
      ${link('overview', 'Overview', 'grid')}
      ${link('sheet', 'Patch Sheet', 'file', '/sheet')}
      ${link('location', 'Location', 'pin', '/location')}
      ${link('contacts', 'Contacts', 'users', '/contacts')}
      <div class="side-group">Consoles</div>
      ${consoles}
      <div class="side-link" onclick="addConsole()">${icon('plug')}<span>Add Console</span></div>
      <div class="side-group">Signal Chain</div>
      ${link('stage-io', 'Stage I/O', 'map', '/stage-io')}
      ${link('devices', 'Devices', 'plug', '/devices')}
      ${link('device-patch', 'Patch Devices', 'table', '/device-patch')}
      <div class="side-group">Sheet</div>
      ${link('power', 'Power', 'power', '/power')}
      ${link('revisions', 'Revisions', 'clock', '/revisions')}
      ${link('export', 'Export', 'down', '/export')}
    </nav>
    <div class="side-foot"><button class="btn sm" onclick="newSheet()">+ New Patch Sheet</button></div>`;

  const tag = $('#kindtag');
  tag.hidden = false;
  tag.textContent = (S.sheet.kind === 'event' ? 'Event' : 'Template') + (isLocked() ? ' · 🔒' : '');
}

function newSheet() {
  openWizard(async (sheet) => { await refreshList(); go(`#/s/${sheet.id}`); });
}

function addConsole() {
  const c = blankConsole(S.sheet.console || 'q225', `Console ${S.sheet.consoles.length + 1}`);
  S.sheet.consoles.push(c);
  touch();
  go(`#/s/${S.sheet.id}/c/${S.sheet.consoles.length - 1}/info`);
}

function blankConsole(preset, name) {
  const def = consoleDef(preset);
  return {
    id: uid(), name, preset,
    manufacturer: def.vendor, model: def.label.replace(def.vendor, '').trim(), fw: '',
    counts: { inputs: 0, busses: def.buses?.aux_group || 0, auxes: 0, dcas: 0, mutes: 0, matrix: def.buses?.matrix_out || 0, outputs: 0 },
    network: { ip: '', subnet: '', gateway: '', dns: '' },
    connections: [], tielines: false, channels: [], outputs: [], notes: '',
  };
}

function blankChannel(ch) {
  return {
    id: uid(), ch, name: '', instrument: '', mic: '', stand: '', phantom: false, ribbon: false,
    tour: false, ms: '', link: '', section: 'SPARE', port: '', alt: '', insert_a: '', insert_b: '',
    direct: '', box: '', split: '', notes: '',
  };
}

const currentConsole = () => S.sheet.consoles[Math.min(S.route.ci, S.sheet.consoles.length - 1)];
const currentAnalysis = () => S.analyses[Math.min(S.route.ci, S.analyses.length - 1)] || { problems: [], counts: {} };

/* --------------------------------------------------------- helpers */
/* Bind every [data-bind] input in a container to a path on an object.
   Handlers write and touch() — they never repaint the container. */
function bind(root, obj) {
  $$('[data-bind]', root).forEach((el) => {
    const path = el.dataset.bind;
    const write = () => {
      const keys = path.split('.');
      const last = keys.pop();
      const target = keys.reduce((o, k) => (o[k] ??= {}), obj);
      target[last] = el.type === 'checkbox' ? el.checked : (el.type === 'number' ? (el.value === '' ? '' : +el.value) : el.value);
      touch();
    };
    el.oninput = write;
    el.onchange = write;
  });
}

const fieldHTML = (path, label, ph = '', { span = 2, type = 'text', help = '', value = '' } = {}) => `
  <div class="field c${span}">
    <label>${label}</label>
    <input class="in" data-bind="${path}" type="${type}" placeholder="${esc(ph)}" value="${esc(value)}">
    ${help ? `<span class="help">${help}</span>` : ''}
  </div>`;

const crumbs = (...bits) => `<div class="crumbs">${bits.map((b, i) =>
  (i ? '<span>›</span>' : '') + (typeof b === 'string' ? `<span class="now">${esc(b)}</span>` : `<a href="${b.href}">${esc(b.label)}</a>`)
).join('')}</div>`;

function confirmed(msg) { return window.confirm(msg); }
