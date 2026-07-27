/* Patchbay — page renderers. One function per route; renderPage() dispatches.
   Tables are painted once per navigation and mutated in place afterwards. */

const OPTIONAL_COLS = {
  instrument: 'Instrument',
  stand: 'Stand',
  section: 'Section',
  box: 'Device',
  split: 'Split',
  alt: 'Alt input',
  insert_a: 'Insert A',
  insert_b: 'Insert B',
  direct: 'Direct out',
  ms: 'M/S',
  link: 'L/R link',
  notes: 'Notes',
};
const DEFAULT_COLS = ['instrument', 'stand', 'section', 'box', 'split', 'notes'];
const cols = () => JSON.parse(localStorage.getItem('patchbay.cols') || 'null') || DEFAULT_COLS;
const setCols = (list) => localStorage.setItem('patchbay.cols', JSON.stringify(list));

function renderPage() {
  const main = $('#main');
  const page = S.route.page;
  const fn = {
    dashboard: pageDashboard,
    overview: pageOverview,
    sheet: pageDoc,
    location: pageLocation,
    contacts: pageContacts,
    'stage-io': pageStageIO,
    devices: pageDevices,
    'device-patch': pageDevicePatch,
    power: pagePower,
    revisions: pageRevisions,
    export: pageExport,
    'console-info': pageConsoleInfo,
    'console-inputs': pageConsoleInputs,
    'console-patch': pageEasyPatch,
    'console-outputs': pageConsoleOutputs,
  }[page] || pageOverview;
  main.innerHTML = '';
  fn(main);
  if (isLocked()) applyLock(main);
}

/* A locked template is read-only: fields disabled, mutating buttons off, matrix
   inert. Export, duplicate and navigation stay live — that's how you use it. */
const LOCK_SAFE = /export|duplicate|copyJson|setLock|go\(|docsec|open=/;

function applyLock(main) {
  const wrap = $('.wrap', main) || main;
  wrap.insertAdjacentHTML('afterbegin', `
    <div class="card lockbar">
      <span class="lockicon">🔒</span>
      <div>
        <div style="font-weight:600">This template is locked</div>
        <div class="hint">Locked so a show build can't drift the house rig. Clone it into a show sheet to work, or unlock to edit the template itself.</div>
      </div>
      <span class="spacer"></span>
      <button class="btn" onclick="duplicate('event')">New event from this</button>
      <button class="btn primary" onclick="setLock(false)">Unlock</button>
    </div>`);
  $$('input, select, textarea', main).forEach((el) => (el.disabled = true));
  $$('button', main).forEach((b) => {
    const src = (b.getAttribute('onclick') || '') + b.id + b.className;
    if (!LOCK_SAFE.test(src)) b.disabled = true;
  });
  $$('.matrix, [data-cell]', main).forEach((el) => (el.style.pointerEvents = 'none'));
}

/* ------------------------------------------------------- dashboard */
function pageDashboard(main) {
  main.innerHTML = `
    <div class="wrap">
      <div class="toolbar">
        <h1 class="page" style="margin:0">Patch Sheets</h1>
        <span class="spacer"></span>
        <label class="btn">Import sheet…<input type="file" id="imp-sheet" accept=".json" hidden></label>
        <label class="btn">Import brief…<input type="file" id="imp-brief" accept=".json" hidden></label>
        <button class="btn primary" onclick="newSheet()">+ New Patch Sheet</button>
      </div>
      ${S.sheets.length ? `<div class="cardgrid">${S.sheets.map(sheetCard).join('')}</div>`
        : `<div class="card" style="text-align:center;padding:48px">
             <p class="empty-note">No patch sheets yet</p>
             <button class="btn primary" onclick="newSheet()">+ Create your first patch sheet</button></div>`}
    </div>`;

  $('#imp-sheet').onchange = (e) => readJson(e.target, async (data) => {
    const sheet = await api('/api/sheets', { method: 'POST', body: { name: data.name || 'Imported sheet' } });
    data.id = sheet.id;
    await api(`/api/sheets/${sheet.id}`, { method: 'PUT', body: { sheet: data, bump: false } });
    await refreshList(); go(`#/s/${sheet.id}`);
  });
  $('#imp-brief').onchange = (e) => readJson(e.target, async (brief) => {
    const sheet = await api('/api/import/brief', { method: 'POST', body: { brief } });
    await refreshList(); go(`#/s/${sheet.id}`);
  });
}

const sheetCard = (s) => `
  <div class="card link" onclick="go('#/s/${s.id}')">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
      <span class="nm" style="font-weight:600">${esc(s.name)}</span>
      <span class="pill ${s.kind === 'event' ? 'on' : ''}">${s.kind === 'event' ? 'Event' : 'Template'}</span>
      ${s.locked ? '<span class="pill" title="Locked template">🔒</span>' : ''}
    </div>
    <div class="mt hint">${esc(s.venue_label || '—')} · ${esc(consoleDef(s.console).label)}</div>
    <div class="mt hint">${s.inputs} ch · ${s.consoles || 1} console${(s.consoles || 1) > 1 ? 's' : ''} · rev ${s.rev} · ${esc((s.updated || '').replace('T', ' '))}</div>
  </div>`;

function readJson(input, cb) {
  const file = input.files[0];
  if (!file) return;
  const fr = new FileReader();
  fr.onload = async () => {
    try { await cb(JSON.parse(fr.result)); } catch (err) { alert('Import failed: ' + err.message); }
    input.value = '';
  };
  fr.readAsText(file);
}

/* -------------------------------------------------------- overview */
function pageOverview(main) {
  const sh = S.sheet;
  const devices = sh.devices.filter((d) => d.kind !== 'network');
  const net = sh.devices.filter((d) => d.kind === 'network');
  const problems = S.analyses.flatMap((a) => a.problems || []);
  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, sh.name)}
      <h1 class="page">${esc(sh.name)}</h1>
      <p class="lede">${esc([sh.venue_label, sh.date, sh.meta.artist].filter(Boolean).join(' · '))}</p>
      <div class="toolbar">
        <button class="btn primary" onclick="go('${sheetPath('/sheet')}')">View Patch Sheet</button>
        <button class="btn" onclick="exportPdf()">Export PDF…</button>
      </div>
      ${problems.length ? `<div class="card" style="border-color:color-mix(in oklab,var(--bad) 45%,transparent)">
        <div class="cardhead">Open conflicts</div>
        ${problems.map((p) => `<div class="problem ${p.level === 'warn' ? 'warn' : ''}">${esc(p.where)} — ${esc(p.msg)}</div>`).join('')}
      </div>` : ''}

      <h2 class="sec">Consoles <span class="pill">${sh.consoles.length}</span></h2>
      <div class="cardgrid">
        ${sh.consoles.map((c, i) => `
          <div class="card link" onclick="go('#/s/${sh.id}/c/${i}/info')">
            <div style="font-weight:600">${esc(c.name || 'Console')}</div>
            <div class="hint">${esc([c.manufacturer, c.model].filter(Boolean).join(' ') || consoleDef(c.preset).label)}</div>
            <div class="hint">${c.channels.length} ch · ${c.outputs.length} outputs</div>
          </div>`).join('')}
      </div>

      <h2 class="sec">I/O devices <span class="pill">${devices.length}</span>
        <button class="btn sm ghost" onclick="go('${sheetPath('/devices')}')">Manage devices</button></h2>
      ${devices.length ? devices.map((d) => `
        <div class="card row"><span class="nm">${esc(d.name)}</span>
          <span class="spacer"></span>
          <span class="mt mono">${d.inputs}in · ${d.outputs}out</span></div>`).join('')
        : '<p class="empty-note">No I/O devices yet.</p>'}

      ${net.length ? `<h2 class="sec">Network devices <span class="pill">${net.length}</span></h2>
        ${net.map((d) => `<div class="card row"><span class="nm">${esc(d.name)}</span>
          <span class="spacer"></span><span class="mt mono">${esc(d.protocol || '')} ${esc(d.ip || '')}</span></div>`).join('')}` : ''}

      <h2 class="sec">Stage positions <span class="pill">${sh.positions.length}</span>
        <button class="btn sm ghost" onclick="go('${sheetPath('/stage-io')}')">Manage stage I/O</button></h2>
      ${sh.positions.length ? sh.positions.map((p) => `
        <div class="card row"><span class="nm">${esc(p.name)}</span><span class="spacer"></span>
          <span class="mt">${p.runs.length} run${p.runs.length === 1 ? '' : 's'}</span></div>`).join('')
        : '<p class="empty-note">No stage positions added yet.</p>'}

      <h2 class="sec">Contacts <span class="pill">${sh.contacts.length}</span>
        <button class="btn sm ghost" onclick="go('${sheetPath('/contacts')}')">Manage contacts</button></h2>
      ${sh.contacts.length ? sh.contacts.map((c) => `
        <div class="card row"><span class="nm">${esc(c.name)}</span><span class="mt">${esc(c.role)}</span>
          <span class="spacer"></span><span class="mt mono">${esc(c.phone || '')}</span></div>`).join('')
        : '<p class="empty-note">No contacts added yet.</p>'}
    </div>`;
}

/* -------------------------------------------- printable sheet view */
function pageDoc(main) {
  const sh = S.sheet;
  const section = (title, count, body) => `
    <details class="docsec" open>
      <summary>${esc(title)}${count != null ? ` (${count})` : ''}<span class="line"></span></summary>
      ${body}
    </details>`;

  const chTable = (con) => {
    const rows = con.channels.filter((r) => r.name || r.mic || r.instrument);
    if (!rows.length) return '<p class="empty-note">No channels filled in yet.</p>';
    return `<div class="tablewrap"><table class="grid2"><thead><tr>
      <th class="w-ch">CH</th><th>Name</th><th class="w-tiny">48V</th><th class="w-port">Port</th>
      <th>Mic / DI</th><th class="w-sm">Stand</th><th class="w-box">Device</th><th>Notes</th></tr></thead>
      <tbody>${rows.map((r) => `<tr class="${r.tour ? 'tour' : ''}">
        <td class="ctr mono">${esc(r.ch)}</td><td>${esc(r.name || r.instrument)}</td>
        <td class="ctr">${r.ribbon ? '<span class="badge-ribbon">NO 48V</span>' : (r.phantom ? '✓' : '')}</td>
        <td class="mono">${esc(r.port)}</td><td>${esc(r.mic)}${r.tour ? ' <span class="pill">⚑ TOUR</span>' : ''}</td>
        <td>${esc(r.stand)}</td><td>${esc(r.box)}</td><td class="hint">${esc(r.notes)}</td></tr>`).join('')}
      </tbody></table></div>`;
  };

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Patch Sheet')}
      <div class="toolbar">
        <button class="btn" onclick="copyJson()">Copy JSON</button>
        <button class="btn primary" onclick="exportPdf()">Export PDF…</button>
        <span class="spacer"></span>
        <button class="btn sm" onclick="$$('.docsec').forEach(d=>d.open=true)">Expand All</button>
        <button class="btn sm" onclick="$$('.docsec').forEach(d=>d.open=false)">Collapse All</button>
      </div>
      <div class="eyebrow">Patch sheet</div>
      <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:12px">
        <h1 class="page">${esc(sh.name)}</h1>
        <div style="text-align:right">
          <div>${esc(consoleDef(sh.console).vendor)}</div>
          <div class="hint mono">${esc(sh.date)}</div>
        </div>
      </div>
      <div class="doc">
        ${sh.consoles.map((c) => section(`${c.name || 'Console'} — Input Channels`, c.channels.length, chTable(c))).join('')}
        ${section('I/O Devices', sh.devices.length, sh.devices.length
          ? `<div class="cardgrid">${sh.devices.map((d) => `<div class="card"><div style="font-weight:600">${esc(d.name)}</div>
             <div class="hint">${d.inputs}in · ${d.outputs}out${d.ip ? ' · ' + esc(d.ip) : ''}</div></div>`).join('')}</div>`
          : '<p class="empty-note">None.</p>')}
        ${section('Stage I/O', sh.positions.length, sh.positions.length
          ? sh.positions.map((p) => `<div class="card"><div style="font-weight:600">${esc(p.name)}</div>
              ${p.runs.map((r) => `<div class="hint">${esc(r.label)} → ${esc(r.device)} ${esc(r.port)}</div>`).join('') || '<div class="hint">No runs.</div>'}</div>`).join('')
          : '<p class="empty-note">None.</p>')}
        ${section('Contacts', sh.contacts.length, sh.contacts.length
          ? `<div class="cardgrid">${sh.contacts.map((c) => `<div class="card"><div style="font-weight:600">${esc(c.name)}</div>
             <div class="hint">${esc(c.role)}</div><div class="hint mono">${esc(c.phone)} ${esc(c.email)}</div></div>`).join('')}</div>`
          : '<p class="empty-note">None.</p>')}
      </div>
    </div>`;
}

async function exportPdf() {
  try {
    const r = await fetch(`/api/sheets/${S.sheet.id}/export.pdf`);
    if (r.status === 409) {
      const win = window.open(`/api/sheets/${S.sheet.id}/export.html`, '_blank');
      setTimeout(() => win?.print(), 700);
      return;
    }
    const blob = await r.blob();
    download(URL.createObjectURL(blob), `${S.sheet.name} - Patch Sheet.pdf`);
  } catch (err) { alert('Export failed: ' + err.message); }
}
function download(href, name) {
  const a = document.createElement('a');
  a.href = href; a.download = name; a.click();
}
function copyJson() {
  navigator.clipboard.writeText(JSON.stringify(S.sheet, null, 1));
  setSaveState('saved', 'Copied');
}

/* --------------------------------------------------------- location */
function pageLocation(main) {
  const sh = S.sheet;
  const l = sh.location;
  main.innerHTML = `
    <div class="wrap narrow">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Location Information')}
      <div class="eyebrow">Patch sheet</div>
      <h1 class="page">Location Information</h1>
      <p class="lede">Name the sheet and fill in the venue details. This prints in the rig information block at the top of the patch sheet.</p>
      <div class="card">
        <div class="cardhead">Location details</div>
        <div class="grid">
          <div class="field c4"><label>Patch Sheet Name <span class="req">*</span></label>
            <input class="in" data-bind="name" value="${esc(sh.name)}"></div>
          ${fieldHTML('location.client', 'Client', 'e.g. Jazz At The Memo', { span: 4, value: l.client })}
          ${fieldHTML('location.site', 'Site / Venue Name', 'e.g. Memorial Hall', { span: 2, value: l.site })}
          ${fieldHTML('location.room', 'Room', 'e.g. FOH, Amp Room', { span: 2, value: l.room })}
          ${fieldHTML('location.address', 'Address', '1225 Elm St', { span: 4, value: l.address })}
          ${fieldHTML('location.city', 'City', 'Cincinnati', { span: 2, value: l.city })}
          ${fieldHTML('location.state', 'State', 'OH', { span: 1, value: l.state })}
          ${fieldHTML('location.zip', 'Zip', '45202', { span: 1, value: l.zip })}
        </div>
      </div>
      <div class="card">
        <div class="cardhead">Show details</div>
        <div class="grid">
          <div class="field c2"><label>Venue preset</label>
            <input class="in" list="venuelist" data-bind="venue_label" value="${esc(sh.venue_label || '')}"></div>
          <div class="field c1"><label>Date</label><input class="in" type="date" data-bind="date" value="${esc(sh.date)}"></div>
          <div class="field c1"><label>Show time</label><input class="in" data-bind="meta.showtime" value="${esc(sh.meta.showtime || '')}"></div>
          ${fieldHTML('meta.artist', 'Artist', '—', { span: 2, value: sh.meta.artist })}
          ${fieldHTML('meta.foh', 'FOH', '—', { span: 1, value: sh.meta.foh })}
          ${fieldHTML('meta.mon', 'MON', '—', { span: 1, value: sh.meta.mon })}
          <div class="field c4"><label>Notes</label>
            <textarea class="in" data-bind="meta.notes">${esc(sh.meta.notes || '')}</textarea></div>
        </div>
      </div>
    </div>`;
  bind(main, sh);
}

/* --------------------------------------------------------- contacts */
function pageContacts(main) {
  const sh = S.sheet;
  main.innerHTML = `
    <div class="wrap narrow">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Contacts')}
      <h1 class="page">Contacts</h1>
      <p class="lede">Key people for this show — client contacts, A1s, A2s, venue contact. Contacts print on the patch sheet.</p>
      <div id="contactlist">${sh.contacts.map(contactCard).join('') || '<p class="empty-note">No contacts added yet.</p>'}</div>
      <button class="btn" onclick="addContact()">+ Add Contact</button>
    </div>`;
  sh.contacts.forEach((c, i) => bind($(`[data-contact="${i}"]`, main), c));
  $$('[data-rmcontact]', main).forEach((b) => (b.onclick = () => {
    sh.contacts.splice(+b.dataset.rmcontact, 1); touch(); renderPage();
  }));
}

const contactCard = (c, i) => `
  <div class="card" data-contact="${i}">
    <div class="cardhead">Contact ${i + 1}<button class="iconbtn danger" data-rmcontact="${i}">Remove</button></div>
    <div class="grid">
      ${fieldHTML('name', 'Name', 'e.g. Brian Lloyd', { span: 2, value: c.name })}
      ${fieldHTML('role', 'Role', 'FOH / MON / A2 / Venue', { span: 2, value: c.role })}
      ${fieldHTML('phone', 'Phone', '(555) 555-5555', { span: 2, value: c.phone })}
      ${fieldHTML('email', 'Email', 'name@venue.com', { span: 2, value: c.email })}
      ${fieldHTML('notes', 'Notes', '', { span: 4, value: c.notes })}
    </div>
  </div>`;

function addContact() {
  S.sheet.contacts.push({ id: uid(), name: '', role: '', phone: '', email: '', notes: '' });
  touch(); renderPage();
}

/* --------------------------------------------------------- stage io */
function pageStageIO(main) {
  const sh = S.sheet;
  const devOptions = (sel) => `<option value=""></option>` + sh.devices.filter((d) => d.kind !== 'network')
    .map((d) => `<option ${d.name === sel ? 'selected' : ''}>${esc(d.name)}</option>`).join('');

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Stage I/O')}
      <h1 class="page">Stage I/O</h1>
      <p class="lede">Define your stage positions and map each run to a device input or output. This builds the signal path from stage to console and prints as the Stage I/O section of the patch sheet.</p>
      ${sh.positions.length ? sh.positions.map((p, i) => `
        <div class="card" data-pos="${i}">
          <div class="cardhead">Position ${i + 1}<button class="iconbtn danger" data-rmpos="${i}">Remove</button></div>
          <div class="grid">
            ${fieldHTML('name', 'Position', 'e.g. Stage Left, Downstage Center', { span: 2, value: p.name })}
            ${fieldHTML('note', 'Note', 'e.g. under the deck', { span: 2, value: p.note })}
          </div>
          <div class="tablewrap" style="margin-top:14px"><table class="grid2"><thead><tr>
            <th>Run</th><th class="w-box">Device</th><th class="w-port">Port</th><th>Notes</th><th class="w-x"></th>
          </tr></thead><tbody>
            ${p.runs.map((r, j) => `<tr data-run="${i}:${j}">
              <td><input value="${esc(r.label)}" data-k="label" placeholder="e.g. Sub-snake A 1–8"></td>
              <td><select data-k="device">${devOptions(r.device)}</select></td>
              <td class="mono"><input value="${esc(r.port)}" data-k="port" placeholder="1–8"></td>
              <td><input value="${esc(r.notes || '')}" data-k="notes"></td>
              <td class="ctr"><button class="iconbtn danger" data-rmrun="${i}:${j}">×</button></td></tr>`).join('')}
          </tbody></table></div>
          <div style="margin-top:10px"><button class="btn sm" data-addrun="${i}">+ Add run</button></div>
        </div>`).join('') : '<p class="empty-note">No stage positions added yet.</p>'}
      <button class="btn" onclick="addPosition()">+ Add Position</button>

      <h2 class="sec">Stage data connections <span class="hint">— data runs and drops on stage</span></h2>
      <div class="tablewrap"><table class="grid2"><thead><tr>
        <th>Label</th><th class="w-box">Type</th><th class="w-x"></th></tr></thead><tbody>
        ${sh.data_runs.map((d, i) => `<tr data-drun="${i}">
          <td><input value="${esc(d.label)}" data-k="label" placeholder="Stage Left Drop 1, FOH Internet…"></td>
          <td><input value="${esc(d.type)}" data-k="type" placeholder="Cat6, Fiber…"></td>
          <td class="ctr"><button class="iconbtn danger" data-rmdrun="${i}">×</button></td></tr>`).join('')}
      </tbody></table></div>
      <div style="margin-top:10px"><button class="btn sm" onclick="addDataRun()">+ Add connection</button></div>
    </div>`;

  sh.positions.forEach((p, i) => bind($(`[data-pos="${i}"] .grid`, main), p));
  $$('[data-run]', main).forEach((tr) => {
    const [i, j] = tr.dataset.run.split(':').map(Number);
    $$('[data-k]', tr).forEach((el) => (el.oninput = el.onchange = () => {
      sh.positions[i].runs[j][el.dataset.k] = el.value; touch();
    }));
  });
  $$('[data-drun]', main).forEach((tr) => {
    const i = +tr.dataset.drun;
    $$('[data-k]', tr).forEach((el) => (el.oninput = () => { sh.data_runs[i][el.dataset.k] = el.value; touch(); }));
  });
  $$('[data-addrun]', main).forEach((b) => (b.onclick = () => {
    sh.positions[+b.dataset.addrun].runs.push({ id: uid(), label: '', device: '', port: '', notes: '' });
    touch(); renderPage();
  }));
  $$('[data-rmrun]', main).forEach((b) => (b.onclick = () => {
    const [i, j] = b.dataset.rmrun.split(':').map(Number);
    sh.positions[i].runs.splice(j, 1); touch(); renderPage();
  }));
  $$('[data-rmpos]', main).forEach((b) => (b.onclick = () => { sh.positions.splice(+b.dataset.rmpos, 1); touch(); renderPage(); }));
  $$('[data-rmdrun]', main).forEach((b) => (b.onclick = () => { sh.data_runs.splice(+b.dataset.rmdrun, 1); touch(); renderPage(); }));
}

function addPosition() { S.sheet.positions.push({ id: uid(), name: '', note: '', runs: [] }); touch(); renderPage(); }
function addDataRun() { S.sheet.data_runs.push({ id: uid(), label: '', type: '' }); touch(); renderPage(); }

/* ---------------------------------------------------------- devices */
function pageDevices(main) {
  const sh = S.sheet;
  const io = sh.devices.filter((d) => d.kind !== 'network');
  const net = sh.devices.filter((d) => d.kind === 'network');

  const deviceCard = (d) => {
    const i = sh.devices.indexOf(d);
    return `
      <div class="card" data-dev="${i}">
        <div class="cardhead">${d.kind === 'network' ? 'Network device' : 'I/O device'}
          <button class="iconbtn danger" data-rmdev="${i}">Remove</button></div>
        <div class="grid">
          ${fieldHTML('name', 'Device name', d.kind === 'network' ? 'e.g. Cisco SG350, Ubiquiti AP' : 'e.g. SD-Rack, DL32', { span: 2, value: d.name })}
          ${d.kind === 'network' ? '' : `
            ${fieldHTML('inputs', '# Inputs', '0', { span: 1, type: 'number', value: d.inputs })}
            ${fieldHTML('outputs', '# Outputs', '0', { span: 1, type: 'number', value: d.outputs })}`}
          ${fieldHTML('protocol', 'Protocol', 'Dante, Waves, AVB, MADI, AES50…', { span: 2, value: d.protocol })}
          ${fieldHTML('ip', 'IP address', '192.168.1.x', { span: 2, value: d.ip })}
          ${d.kind === 'network' ? '' : `
            ${fieldHTML('location', 'Location', 'Stage left, FOH…', { span: 2, value: d.location })}
            ${fieldHTML('format', 'Format', 'AES50 A, Optocore…', { span: 2, value: d.format })}`}
          ${fieldHTML('notes', 'Notes', '', { span: 4, value: d.notes })}
        </div>
        ${d.kind === 'network' ? '' : `
          <div class="hint" style="margin-top:12px">Assign to console
            ${sh.consoles.map((c) => `<label class="pill" style="margin-left:6px">
              <input type="checkbox" data-assign="${i}:${c.id}" ${d.consoles?.includes(c.id) ? 'checked' : ''}> ${esc(c.name || 'Console')}
            </label>`).join('')}
          </div>`}
      </div>`;
  };

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Devices')}
      <h1 class="page">Devices</h1>
      <p class="lede">Add and configure the I/O and network devices in this system. Assign I/O devices to consoles so they show up as patch destinations in Easy Patch.</p>
      <h3 class="sub">I/O Devices</h3>
      <p class="hint">Stage racks, expansion cards, Dante devices, and any other audio I/O.</p>
      ${io.map(deviceCard).join('') || '<p class="empty-note">No I/O devices yet.</p>'}
      <button class="btn" onclick="addDevice('io')">+ Add Device</button>
      <h3 class="sub">Network Devices</h3>
      <p class="hint">Switches, wireless access points, routers, and other network infrastructure.</p>
      ${net.map(deviceCard).join('') || '<p class="empty-note">No network devices added yet.</p>'}
      <button class="btn" onclick="addDevice('network')">+ Add Network Device</button>
    </div>`;

  sh.devices.forEach((d, i) => {
    const card = $(`[data-dev="${i}"] .grid`, main);
    if (card) bind(card, d);
  });
  $$('[data-assign]', main).forEach((cb) => (cb.onchange = () => {
    const [i, cid] = cb.dataset.assign.split(':');
    const dev = sh.devices[+i];
    dev.consoles = dev.consoles || [];
    if (cb.checked) { if (!dev.consoles.includes(cid)) dev.consoles.push(cid); }
    else dev.consoles = dev.consoles.filter((x) => x !== cid);
    touch();
  }));
  $$('[data-rmdev]', main).forEach((b) => (b.onclick = () => {
    if (!confirmed('Remove this device? Patches that point at it stay on the channels.')) return;
    sh.devices.splice(+b.dataset.rmdev, 1); touch(); renderPage();
  }));
}

function addDevice(kind) {
  S.sheet.devices.push({
    id: uid(), kind, name: '', inputs: 0, outputs: 0, ip: '', protocol: '',
    location: '', format: '', notes: '', consoles: kind === 'network' ? [] : [S.sheet.consoles[0].id],
  });
  touch(); renderPage();
}

/* ---------------------------------------------------- patch devices */
function pageDevicePatch(main) {
  const sh = S.sheet;
  sh.device_patches = sh.device_patches || [];
  const netCapable = sh.devices.filter((d) => d.protocol || d.kind === 'network');
  const opts = (sel) => netCapable.map((d) => `<option value="${d.id}" ${d.id === sel ? 'selected' : ''}>${esc(d.name || 'Device')}</option>`).join('');
  const state = pageDevicePatch.state ||= { from: netCapable[0]?.id || '', to: netCapable[1]?.id || netCapable[0]?.id || '' };
  const from = sh.devices.find((d) => d.id === state.from);
  const to = sh.devices.find((d) => d.id === state.to);

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Patch Devices')}
      <h1 class="page">Patch Devices</h1>
      <p class="lede">Route audio between Dante, Waves, AVB and Milan devices, and patch snake splits to their destination racks. Pick a send and a receive device, then click a cell to patch.</p>
      ${netCapable.length < 1
        ? `<div class="card" style="text-align:center;padding:36px">
             <div style="font-weight:600;margin-bottom:6px">No network-protocol devices configured</div>
             <div class="hint">Open a device in <a href="${sheetPath('/devices')}" style="color:var(--primary)">Devices</a> and set its protocol (Dante, Waves, AVB, Milan…).</div>
           </div>`
        : `<div class="toolbar">
             <div class="field" style="min-width:200px"><label>Send device</label><select class="in" id="dp-from">${opts(state.from)}</select></div>
             <div class="field" style="min-width:200px"><label>Receive device</label><select class="in" id="dp-to">${opts(state.to)}</select></div>
           </div>
           ${devicePatchMatrix(from, to)}`}
    </div>`;

  const fromSel = $('#dp-from', main);
  if (fromSel) {
    fromSel.onchange = () => { state.from = fromSel.value; renderPage(); };
    $('#dp-to', main).onchange = (e) => { state.to = e.target.value; renderPage(); };
    $$('[data-dp]', main).forEach((td) => (td.onclick = () => {
      const [o, i] = td.dataset.dp.split(':').map(Number);
      const key = `${state.from}:${o}>${state.to}:${i}`;
      const hit = sh.device_patches.findIndex((p) => p.key === key);
      if (hit >= 0) sh.device_patches.splice(hit, 1);
      else sh.device_patches.push({ key, from: state.from, out: o, to: state.to, in: i });
      td.classList.toggle('on');
      touch();
    }));
  }
}

function devicePatchMatrix(from, to) {
  if (!from || !to) return '<p class="empty-note">Pick two devices.</p>';
  const outs = Math.min(from.outputs || 0, 64);
  const ins = Math.min(to.inputs || 0, 64);
  if (!outs || !ins) return `<p class="empty-note">${esc(from.name)} has ${outs} outputs and ${esc(to.name)} has ${ins} inputs — set the counts in Devices.</p>`;
  const patched = new Set(S.sheet.device_patches.map((p) => p.key));
  const head = Array.from({ length: ins }, (_, i) => `<th class="port">${to.name} ${i + 1}</th>`).join('');
  const rows = Array.from({ length: outs }, (_, o) => `
    <tr><td class="chcol"><span class="n">${o + 1}</span><span class="l">${esc(from.name)} out</span></td>
    ${Array.from({ length: ins }, (_, i) =>
      `<td class="cell ${patched.has(`${from.id}:${o}>${to.id}:${i}`) ? 'on' : ''}" data-dp="${o}:${i}"><span class="dot"></span></td>`).join('')}
    </tr>`).join('');
  return `<div class="matrix"><table class="mx"><thead><tr><th class="chhead">Sends</th>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

/* ----------------------------------------------------- console info */
function pageConsoleInfo(main) {
  const sh = S.sheet;
  const con = currentConsole();
  const i = S.route.ci;
  const assigned = sh.devices.filter((d) => d.kind !== 'network' && d.consoles?.includes(con.id));
  main.innerHTML = `
    <div class="wrap narrow">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, con.name || 'Console', 'Console Info')}
      <div class="eyebrow">Console</div>
      <h1 class="page">Console Information</h1>
      <p class="lede">Set up this console — make, model, channel counts, the connections that carry signal in and out, and its network settings.</p>
      <div class="card" id="con-form">
        <div class="cardhead">Console details</div>
        <div class="grid">
          <div class="field c4"><label>Console name</label>
            <input class="in" data-bind="name" value="${esc(con.name)}">
            <span class="help">Shown in the sidebar — FOH Console, Monitor World…</span></div>
          <div class="field c4"><label>Desk preset</label>
            <select class="in" id="con-preset">${S.kb.consoles.map((c) =>
              `<option value="${c.id}" ${c.id === con.preset ? 'selected' : ''}>${esc(c.label)}</option>`).join('')}</select>
            <span class="help">Drives the port surface used by Easy Patch and the exports.</span></div>
          ${fieldHTML('manufacturer', 'Manufacturer', 'e.g. DiGiCo', { span: 2, value: con.manufacturer })}
          ${fieldHTML('model', 'Model', 'e.g. Quantum 225', { span: 2, value: con.model })}
          ${fieldHTML('fw', 'Firmware version', 'e.g. 2.4.1', { span: 4, value: con.fw })}
        </div>
      </div>

      <div class="card" id="con-counts">
        <div class="cardhead">Channel counts</div>
        <p class="hint" style="margin:-8px 0 12px">Raising the input count adds rows. Lowering it removes rows from the end, along with their patch data.</p>
        <div class="grid">
          ${fieldHTML('counts.inputs', 'Inputs', '0', { span: 1, type: 'number', value: con.counts.inputs })}
          ${fieldHTML('counts.busses', 'Busses', '0', { span: 1, type: 'number', value: con.counts.busses })}
          ${fieldHTML('counts.auxes', 'Auxes', '0', { span: 1, type: 'number', value: con.counts.auxes })}
          ${fieldHTML('counts.dcas', 'DCAs', '0', { span: 1, type: 'number', value: con.counts.dcas })}
          ${fieldHTML('counts.mutes', 'Mute groups', '0', { span: 1, type: 'number', value: con.counts.mutes })}
          ${fieldHTML('counts.matrix', 'Matrix', '0', { span: 1, type: 'number', value: con.counts.matrix })}
          ${fieldHTML('counts.outputs', 'Outputs', '0', { span: 2, type: 'number', value: con.counts.outputs })}
        </div>
        <div style="margin-top:12px"><button class="btn sm" id="applycount">Apply input count</button>
          <span class="hint">${con.channels.length} channel rows right now.</span></div>
      </div>

      <div class="card">
        <div class="cardhead">Connections</div>
        <p class="hint" style="margin:-8px 0 12px">Physical or network I/O slots on this console — Dante, AES, MADI, analog cards — that carry signal to and from the desk.</p>
        <div class="tablewrap"><table class="grid2"><thead><tr>
          <th>Name</th><th class="w-box">Type</th><th class="w-tiny">Ch</th><th class="w-x"></th></tr></thead><tbody>
          ${con.connections.map((c, j) => `<tr data-conn="${j}">
            <td><input value="${esc(c.name)}" data-k="name" placeholder="DMI 1, MADI A, Local XLR…"></td>
            <td><input value="${esc(c.type)}" data-k="type" placeholder="Dante / MADI / AES"></td>
            <td><input value="${esc(c.channels ?? '')}" data-k="channels" type="number"></td>
            <td class="ctr"><button class="iconbtn danger" data-rmconn="${j}">×</button></td></tr>`).join('')}
        </tbody></table></div>
        <div style="margin-top:10px"><button class="btn sm" id="addconn">+ Add Connection</button></div>
      </div>

      <div class="card">
        <div class="cardhead">Assigned I/O devices</div>
        ${assigned.length ? assigned.map((d) => `<div class="card row"><span class="nm">${esc(d.name)}</span>
          <span class="spacer"></span><span class="mt mono">${d.inputs} in / ${d.outputs} out</span></div>`).join('')
          : '<p class="empty-note">None assigned. Assign devices in Devices.</p>'}
      </div>

      <div class="card" id="con-net">
        <div class="cardhead">Networking</div>
        <div class="grid">
          ${fieldHTML('network.ip', 'IP address', '192.168.1.101', { span: 2, value: con.network.ip })}
          ${fieldHTML('network.subnet', 'Subnet mask', '255.255.255.0', { span: 2, value: con.network.subnet })}
          ${fieldHTML('network.gateway', 'Gateway', '192.168.1.1', { span: 2, value: con.network.gateway })}
          ${fieldHTML('network.dns', 'DNS server', '8.8.8.8', { span: 2, value: con.network.dns })}
        </div>
      </div>

      ${sh.consoles.length > 1 ? `<div class="card" style="border-color:color-mix(in oklab,var(--bad) 45%,transparent)">
        <div class="cardhead">Danger zone</div>
        <p class="hint">Deleting this console removes its channels, outputs and patch data. A revision is snapshotted first.</p>
        <button class="btn danger" id="delcon">Delete console</button></div>` : ''}
    </div>`;

  bind($('#con-form', main), con);
  bind($('#con-counts', main), con);
  bind($('#con-net', main), con);
  $('#con-preset', main).onchange = (e) => {
    con.preset = e.target.value;
    const def = consoleDef(con.preset);
    con.manufacturer = con.manufacturer || def.vendor;
    S.sheet.console = S.sheet.consoles[0].preset;
    touch(); renderPage();
  };
  $('#applycount', main).onclick = () => {
    const want = Math.max(0, Math.min(256, parseInt(con.counts.inputs || 0, 10)));
    if (want < con.channels.length && !confirmed(`Remove ${con.channels.length - want} channel rows from the end?`)) return;
    while (con.channels.length < want) con.channels.push(blankChannel(con.channels.length + 1));
    con.channels.length = want;
    touch(); saveNow(true); renderPage();
  };
  $('#addconn', main).onclick = () => { con.connections.push({ id: uid(), name: '', type: '', channels: '' }); touch(); renderPage(); };
  $$('[data-conn]', main).forEach((tr) => {
    const j = +tr.dataset.conn;
    $$('[data-k]', tr).forEach((el) => (el.oninput = () => { con.connections[j][el.dataset.k] = el.value; touch(); }));
  });
  $$('[data-rmconn]', main).forEach((b) => (b.onclick = () => { con.connections.splice(+b.dataset.rmconn, 1); touch(); renderPage(); }));
  const del = $('#delcon', main);
  if (del) del.onclick = async () => {
    if (!confirmed(`Delete ${con.name || 'this console'} and its ${con.channels.length} channels?`)) return;
    sh.consoles.splice(i, 1);
    await saveNow(true);
    go(`#/s/${sh.id}`);
  };
}

/* --------------------------------------------------- console inputs */
function pageConsoleInputs(main) {
  const sh = S.sheet;
  const con = currentConsole();
  const shown = cols();
  const devNames = sh.devices.filter((d) => d.kind !== 'network' && d.consoles?.includes(con.id)).map((d) => d.name);
  const ports = portList(con);

  const head = ['<th class="w-ch">CH</th>', '<th>Name</th>', '<th class="w-tiny">48V</th>',
    '<th class="w-tiny">TOUR</th>', '<th>Mic / DI</th>', '<th class="w-port">Port</th>']
    .concat(shown.map((k) => `<th class="${k === 'notes' ? '' : 'w-sm'}">${OPTIONAL_COLS[k]}</th>`))
    .concat(['<th class="w-x"></th>']).join('');

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, con.name || 'Console', 'Console Inputs')}
      <h1 class="page">Console Inputs</h1>
      <p class="lede">A modern take on the classic patch sheet. Name each channel, set its I/O, write in the mic or DI. Saves automatically.</p>
      <div class="toolbar">
        <button class="btn sm" id="add-ch">+ Channel</button>
        <button class="btn sm" id="add-8">+ 8</button>
        <button class="btn sm" id="renumber">Renumber 1…n</button>
        <button class="btn sm" id="autopatch">Auto-patch free ports</button>
        <button class="btn sm danger" id="clear-rows">Clear rows…</button>
        <span class="spacer"></span>
        <span class="hint">${con.channels.filter((r) => r.name || r.mic).length} used · ${con.channels.length} rows</span>
        <div class="field"><select class="in" id="fieldpick">
          <option value="">Fields…</option>
          ${Object.entries(OPTIONAL_COLS).map(([k, v]) =>
            `<option value="${k}">${shown.includes(k) ? '✓ ' : '   '}${v}</option>`).join('')}
        </select></div>
      </div>
      <div class="tablewrap"><table class="grid2" id="chgrid"><thead><tr>${head}</tr></thead><tbody>
        ${con.channels.map((r, i) => channelRow(r, i, shown, ports, devNames)).join('')}
      </tbody></table></div>
    </div>`;

  wireChannelRows(main, con, shown);
  $('#fieldpick', main).onchange = (e) => {
    const k = e.target.value;
    if (!k) return;
    const list = cols();
    setCols(list.includes(k) ? list.filter((x) => x !== k) : [...list, k]);
    renderPage();
  };
  $('#add-ch', main).onclick = () => { addChannels(con, 1); };
  $('#add-8', main).onclick = () => { addChannels(con, 8); };
  $('#renumber', main).onclick = () => { con.channels.forEach((r, i) => (r.ch = i + 1)); touch(); renderPage(); };
  $('#autopatch', main).onclick = () => {
    const used = new Set(con.channels.map((r) => r.port).filter(Boolean));
    const free = ports.filter((p) => !used.has(p.port));
    con.channels.forEach((r) => {
      if ((r.name || r.mic) && !r.port && free.length) r.port = free.shift().port;
    });
    touch(); renderPage();
  };
  $('#clear-rows', main).onclick = async () => {
    if (!confirmed('Clear every channel row on this console? A revision is snapshotted first.')) return;
    await saveNow(true);
    con.channels = con.channels.map((r, i) => ({ ...blankChannel(i + 1), id: r.id }));
    touch(); renderPage();
  };
}

function addChannels(con, n) {
  const start = con.channels.length ? Math.max(...con.channels.map((r) => r.ch || 0)) : 0;
  for (let i = 1; i <= n; i++) con.channels.push(blankChannel(start + i));
  con.counts.inputs = con.channels.length;
  touch(); renderPage();
}

function channelRow(r, i, shown, ports, devNames) {
  const cell = (k, extra = '') => `<td><input value="${esc(r[k] ?? '')}" data-k="${k}" ${extra}></td>`;
  const optional = shown.map((k) => {
    if (k === 'section') {
      return `<td><select data-k="section">${S.kb.sections.map((s) =>
        `<option value="${esc(s.id)}" ${s.id === r.section ? 'selected' : ''}>${esc(s.label)}</option>`).join('')}</select></td>`;
    }
    if (k === 'box') {
      return `<td><input list="devlist" value="${esc(r.box || '')}" data-k="box"></td>`;
    }
    if (k === 'stand') return `<td><input list="standlist" value="${esc(r.stand || '')}" data-k="stand"></td>`;
    return cell(k);
  }).join('');
  return `<tr data-row="${i}" class="${r.tour ? 'tour' : ''}">
    <td class="chcell"><span class="handle" draggable="true" data-drag="${i}">⠿</span>
      <input value="${esc(r.ch ?? '')}" data-k="ch" inputmode="numeric"></td>
    <td><input value="${esc(r.name)}" data-k="name" placeholder="—"></td>
    <td class="ctr">${r.ribbon ? '<span class="badge-ribbon">NO</span>'
      : `<input type="checkbox" data-k="phantom" ${r.phantom ? 'checked' : ''} style="width:auto">`}</td>
    <td class="ctr"><input type="checkbox" data-k="tour" ${r.tour ? 'checked' : ''} style="width:auto"></td>
    <td><input list="miclist" value="${esc(r.mic)}" data-k="mic"></td>
    <td class="mono"><input list="portlist" value="${esc(r.port)}" data-k="port"></td>
    ${optional}
    <td class="ctr"><button class="iconbtn danger" data-rm="${i}">×</button></td></tr>`;
}

function wireChannelRows(main, con, shown) {
  // Port + device datalists for the grid.
  const ports = portList(con);
  const devNames = S.sheet.devices.filter((d) => d.kind !== 'network').map((d) => d.name);
  main.insertAdjacentHTML('beforeend',
    `<datalist id="portlist">${ports.map((p) => `<option value="${esc(p.port)}">`).join('')}</datalist>
     <datalist id="devlist">${devNames.map((d) => `<option value="${esc(d)}">`).join('')}</datalist>`);

  $$('#chgrid tbody tr', main).forEach((tr) => {
    const row = con.channels[+tr.dataset.row];
    $$('[data-k]', tr).forEach((el) => {
      const k = el.dataset.k;
      el.oninput = el.onchange = async () => {
        row[k] = el.type === 'checkbox' ? el.checked : (k === 'ch' ? (el.value === '' ? null : +el.value) : el.value);
        if (k === 'mic') await micLookup(row, tr);
        if (k === 'tour') tr.classList.toggle('tour', row.tour);
        touch();
      };
    });
    $('[data-rm]', tr).onclick = () => {
      con.channels.splice(+tr.dataset.row, 1); touch(); renderPage();
    };
    const handle = $('[data-drag]', tr);
    handle.ondragstart = (e) => e.dataTransfer.setData('text/plain', tr.dataset.row);
    tr.ondragover = (e) => e.preventDefault();
    tr.ondrop = (e) => {
      e.preventDefault();
      const from = +e.dataTransfer.getData('text/plain');
      const to = +tr.dataset.row;
      if (from === to) return;
      con.channels.splice(to, 0, con.channels.splice(from, 1)[0]);
      touch(); renderPage();
    };
  });
}

/* Mic library lookup — sets phantom/ribbon in place, never repaints the table. */
async function micLookup(row, tr) {
  const { mic, section } = await api('/api/guess', { method: 'POST', body: { mic: row.mic, name: row.name, instrument: row.instrument } });
  if (!mic) return;
  row.ribbon = mic.ribbon;
  row.phantom = mic.ribbon ? false : mic.phantom;
  if (row.section === 'SPARE' && section) row.section = section;
  const cell = tr.children[2];
  cell.innerHTML = row.ribbon ? '<span class="badge-ribbon">NO</span>'
    : `<input type="checkbox" data-k="phantom" ${row.phantom ? 'checked' : ''} style="width:auto">`;
  const box = $('[data-k="phantom"]', cell);
  if (box) box.onchange = () => { row.phantom = box.checked; touch(); };
  const secSel = $('[data-k="section"]', tr);
  if (secSel) secSel.value = row.section;
}

function portList(con) {
  const def = consoleDef(con.preset);
  const out = [];
  def.input_ports.forEach((g) => g.ports.forEach((p) => out.push({ group: g.label, port: p })));
  S.sheet.devices.filter((d) => d.kind !== 'network' && d.consoles?.includes(con.id)).forEach((d) => {
    for (let i = 1; i <= Math.min(d.inputs || 0, 64); i++) out.push({ group: d.name, port: `${d.name} ${i}` });
  });
  return out;
}

/* ------------------------------------------------------- easy patch */
function pageEasyPatch(main) {
  const sh = S.sheet;
  const con = currentConsole();
  const field = S.matrix.field;
  const groups = matrixGroups(con);
  const used = new Map();
  con.channels.forEach((r) => { if (r[field]) used.set(r[field], (used.get(r[field]) || 0) + 1); });

  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, con.name || 'Console', 'Easy Patch')}
      <h1 class="page">Easy Patch</h1>
      <p class="lede">Rows are console channels, columns are I/O. Click a cell to patch it; click it again to clear. Shift-click a cell to patch that channel and everything below it sequentially (1:1).</p>
      <div class="mxtabs">
        <div class="seg">
          ${[['port', 'I/O'], ['alt', 'Alt Input'], ['insert_a', 'Insert A'], ['insert_b', 'Insert B'], ['direct', 'Direct Out']]
            .map(([k, l]) => `<button class="${field === k ? 'on' : ''}" data-field="${k}">${l}</button>`).join('')}
        </div>
        <span class="spacer"></span>
        <span class="hint">${con.channels.filter((r) => r[field]).length} of ${con.channels.length} patched</span>
      </div>
      ${groups.length ? matrixHTML(con, groups, field, used)
        : '<p class="empty-note">No ports available — pick a desk preset in Console Info, or assign an I/O device to this console.</p>'}
    </div>`;

  $$('[data-field]', main).forEach((b) => (b.onclick = () => { S.matrix.field = b.dataset.field; renderPage(); }));
  $$('[data-cell]', main).forEach((td) => (td.onclick = (e) => {
    const [ri, port] = [+td.dataset.row, td.dataset.port];
    const row = con.channels[ri];
    if (row[field] === port) row[field] = '';
    else if (e.shiftKey) {
      // Sequential fill from here down, following the port order.
      const all = groups.flatMap((g) => g.ports);
      let p = all.indexOf(port);
      for (let i = ri; i < con.channels.length && p < all.length; i++, p++) con.channels[i][field] = all[p];
    } else row[field] = port;
    touch();
    renderPage();
  }));
}

function matrixGroups(con) {
  const def = consoleDef(con.preset);
  const groups = def.input_ports.map((g) => ({ name: `${def.vendor} ${g.label}`, ports: g.ports }));
  S.sheet.devices.filter((d) => d.kind !== 'network' && d.consoles?.includes(con.id)).forEach((d) => {
    const n = Math.min(d.inputs || 0, 64);
    if (n) groups.push({ name: d.name || 'Device', ports: Array.from({ length: n }, (_, i) => `${d.name} ${i + 1}`) });
  });
  return groups.filter((g) => g.ports.length);
}

function matrixHTML(con, groups, field, used) {
  const devRow = groups.map((g) => `<th class="dev" colspan="${g.ports.length}">${esc(g.name)}</th>`).join('');
  const portRow = groups.flatMap((g) => g.ports.map((p) => `<th class="port">${esc(p)}</th>`)).join('');
  const rows = con.channels.map((r, i) => `
    <tr>
      <td class="chcol"><span class="n">${esc(r.ch ?? i + 1)}</span>
        <span class="l ${r.name ? '' : 'empty'}">${esc(r.name || `Ch ${i + 1}`)}</span></td>
      ${groups.flatMap((g) => g.ports.map((p) => {
        const on = r[field] === p;
        const clash = on && used.get(p) > 1;
        return `<td class="cell ${on ? 'on' : ''} ${clash ? 'conflict' : ''}" data-cell data-row="${i}" data-port="${esc(p)}"><span class="dot"></span></td>`;
      })).join('')}
    </tr>`).join('');
  return `<div class="matrix"><table class="mx">
    <thead><tr><th class="chhead" rowspan="2">Channels</th>${devRow}</tr><tr>${portRow}</tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

/* ------------------------------------------------ console outputs */
function pageConsoleOutputs(main) {
  const sh = S.sheet;
  const con = currentConsole();
  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, con.name || 'Console', 'Busses & Outputs')}
      <h1 class="page">Busses &amp; Outputs</h1>
      <p class="lede">Bus, what it feeds, the output port, and the box on the other end.</p>
      <div class="toolbar">
        <button class="btn sm" id="add-out">+ Output</button>
        <button class="btn sm" id="seed-out">Seed console buses</button>
        <span class="hint">${esc(consoleDef(con.preset).buses?.note || '')}</span>
      </div>
      <div class="tablewrap"><table class="grid2" id="outgrid"><thead><tr>
        <th class="w-sm">Bus</th><th>Feeds</th><th class="w-port">Port</th><th>Device</th>
        <th class="w-box">Location</th><th>Notes</th><th class="w-x"></th></tr></thead><tbody>
        ${con.outputs.map((o, i) => `<tr data-out="${i}">
          <td class="mono"><input value="${esc(o.bus)}" data-k="bus"></td>
          <td><input value="${esc(o.name)}" data-k="name"></td>
          <td class="mono"><input value="${esc(o.port)}" data-k="port"></td>
          <td><input value="${esc(o.device)}" data-k="device"></td>
          <td><input value="${esc(o.location)}" data-k="location"></td>
          <td><input value="${esc(o.notes)}" data-k="notes"></td>
          <td class="ctr"><button class="iconbtn danger" data-rmout="${i}">×</button></td></tr>`).join('')}
      </tbody></table></div>
    </div>`;

  $$('[data-out]', main).forEach((tr) => {
    const o = con.outputs[+tr.dataset.out];
    $$('[data-k]', tr).forEach((el) => (el.oninput = () => { o[el.dataset.k] = el.value; touch(); }));
  });
  $$('[data-rmout]', main).forEach((b) => (b.onclick = () => { con.outputs.splice(+b.dataset.rmout, 1); touch(); renderPage(); }));
  $('#add-out', main).onclick = () => { con.outputs.push({ id: uid(), bus: '', name: '', port: '', device: '', location: '', notes: '' }); touch(); renderPage(); };
  $('#seed-out', main).onclick = () => {
    const seed = consoleDef(con.preset).bus_seed || [];
    seed.forEach((b) => {
      if (!con.outputs.some((o) => o.bus === b.bus)) con.outputs.push({ id: uid(), bus: b.bus, name: b.name, port: '', device: '', location: '', notes: '' });
    });
    touch(); renderPage();
  };
}

/* ------------------------------------------------------------ power */
function pagePower(main) {
  const sh = S.sheet;
  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Power')}
      <h1 class="page">Power</h1>
      <p class="lede">Distros, feeds, circuits and what's on them.</p>
      ${sh.power.map((d, i) => `
        <div class="card" data-distro="${i}">
          <div class="cardhead">Distro ${i + 1}<button class="iconbtn danger" data-rmdistro="${i}">Remove</button></div>
          <div class="grid">
            ${fieldHTML('name', 'Name', 'e.g. Distro A', { span: 2, value: d.name })}
            ${fieldHTML('location', 'Location', 'Stage right', { span: 1, value: d.location })}
            ${fieldHTML('feed', 'Feed', '100A 3ø', { span: 1, value: d.feed })}
          </div>
          <div class="tablewrap" style="margin-top:14px"><table class="grid2"><thead><tr>
            <th class="w-sm">Circuit</th><th>Load</th><th class="w-tiny">Amps</th><th>Notes</th><th class="w-x"></th>
          </tr></thead><tbody>
            ${(d.circuits || []).map((c, j) => `<tr data-ckt="${i}:${j}">
              <td class="mono"><input value="${esc(c.ckt)}" data-k="ckt"></td>
              <td><input value="${esc(c.load)}" data-k="load"></td>
              <td><input value="${esc(c.amps ?? '')}" data-k="amps" type="number"></td>
              <td><input value="${esc(c.notes || '')}" data-k="notes"></td>
              <td class="ctr"><button class="iconbtn danger" data-rmckt="${i}:${j}">×</button></td></tr>`).join('')}
          </tbody></table></div>
          <div style="margin-top:10px"><button class="btn sm" data-addckt="${i}">+ Circuit</button>
            <span class="hint">Listed load: ${(d.circuits || []).reduce((n, c) => n + (+c.amps || 0), 0)} A</span></div>
        </div>`).join('') || '<p class="empty-note">No distros yet.</p>'}
      <button class="btn" onclick="addDistro()">+ Distro</button>
    </div>`;

  sh.power.forEach((d, i) => bind($(`[data-distro="${i}"] .grid`, main), d));
  $$('[data-ckt]', main).forEach((tr) => {
    const [i, j] = tr.dataset.ckt.split(':').map(Number);
    $$('[data-k]', tr).forEach((el) => (el.oninput = () => { sh.power[i].circuits[j][el.dataset.k] = el.value; touch(); }));
  });
  $$('[data-addckt]', main).forEach((b) => (b.onclick = () => {
    const d = sh.power[+b.dataset.addckt];
    (d.circuits ||= []).push({ id: uid(), ckt: '', load: '', amps: '', notes: '' });
    touch(); renderPage();
  }));
  $$('[data-rmckt]', main).forEach((b) => (b.onclick = () => {
    const [i, j] = b.dataset.rmckt.split(':').map(Number);
    sh.power[i].circuits.splice(j, 1); touch(); renderPage();
  }));
  $$('[data-rmdistro]', main).forEach((b) => (b.onclick = () => { sh.power.splice(+b.dataset.rmdistro, 1); touch(); renderPage(); }));
}
function addDistro() { S.sheet.power.push({ id: uid(), name: '', location: '', feed: '', circuits: [] }); touch(); renderPage(); }

/* -------------------------------------------------------- revisions */
async function pageRevisions(main) {
  const sh = S.sheet;
  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Revisions')}
      <h1 class="page">Revisions</h1>
      <p class="lede">Autosaves overwrite quietly. Marking a revision snapshots the current state and bumps the rev number — restoring is never destructive, the current state is snapshotted first.</p>
      <div class="toolbar"><button class="btn primary" id="mark">Mark revision</button>
        <span class="hint">Currently rev ${sh.rev}</span></div>
      <div id="revlist" class="hint">Loading…</div>
    </div>`;
  $('#mark', main).onclick = async () => { await saveNow(true); renderPage(); };

  const { revisions } = await api(`/api/sheets/${sh.id}/revisions`);
  $('#revlist', main).innerHTML = revisions.length
    ? revisions.map((r) => `<div class="revrow"><span class="rv">Rev ${r.rev}</span>
        <span>${esc(r.updated.replace('T', ' '))}</span>
        <span class="hint">${r.inputs} channels · ${r.outputs} outputs</span>
        <span class="spacer"></span>
        <button class="btn sm" data-file="${esc(r.file)}">Restore</button></div>`).join('')
    : '<p class="empty-note">No snapshots yet.</p>';
  $$('#revlist [data-file]', main).forEach((b) => (b.onclick = async () => {
    if (!confirmed('Restore this revision? The current state is snapshotted first.')) return;
    const { sheet, analyses } = await api(`/api/sheets/${sh.id}/restore`, { method: 'POST', body: { file: b.dataset.file } });
    S.sheet = sheet; S.analyses = analyses || []; renderSidebar(); renderPage();
  }));
}

/* ----------------------------------------------------------- export */
function pageExport(main) {
  const sh = S.sheet;
  main.innerHTML = `
    <div class="wrap">
      ${crumbs({ href: '#/', label: 'Dashboard' }, { href: sheetPath(), label: sh.name }, 'Export')}
      <h1 class="page">Export</h1>
      <p class="lede">Show-day paperwork in the house format — rig information, input list, patching by port, cross-patch by device, outputs, stage I/O, power and contacts.</p>
      <div class="cardgrid">
        <div class="card"><h3 class="sub" style="margin-top:0">Stage PDF</h3>
          <p class="hint">Letter landscape, show-doc palette. Opens the print-ready sheet if weasyprint isn't installed here.</p>
          <button class="btn primary" onclick="exportPdf()">Open / save PDF</button></div>
        <div class="card"><h3 class="sub" style="margin-top:0">Input List xlsx</h3>
          <p class="hint">The usual column order and colors, plus Rig Info and Outputs &amp; Power tabs.</p>
          <button class="btn" onclick="location.href='/api/sheets/${sh.id}/export.xlsx'">Download xlsx</button></div>
        <div class="card"><h3 class="sub" style="margin-top:0">Sheet JSON</h3>
          <p class="hint">The whole sheet — back it up, move it to another machine, or diff it.</p>
          <button class="btn" onclick="location.href='/api/sheets/${sh.id}/export.json'">Download JSON</button></div>
        <div class="card"><h3 class="sub" style="margin-top:0">Duplicate</h3>
          <p class="hint">Clone this rig as a one-off event sheet, or as another template.</p>
          <button class="btn" onclick="duplicate('event')">New event from this</button>
          <button class="btn" onclick="duplicate('install')">Duplicate as template</button></div>
        <div class="card"><h3 class="sub" style="margin-top:0">${S.sheet.locked ? 'Unlock template' : 'Lock as template'}</h3>
          <p class="hint">${S.sheet.locked
            ? 'Unlocking lets you edit the house rig itself. Lock it again when you\'re done.'
            : 'Locking makes this sheet read-only — the house rig stays put and shows get cloned off it. Unlock any time.'}</p>
          <button class="btn ${S.sheet.locked ? '' : 'primary'}" onclick="setLock(${!S.sheet.locked})">
            ${S.sheet.locked ? 'Unlock' : 'Lock template'}</button></div>
        <div class="card" style="border-color:color-mix(in oklab,var(--bad) 45%,transparent)">
          <h3 class="sub" style="margin-top:0">Delete sheet</h3>
          <p class="hint">Moves the sheet to <code>data/trash/</code>. Nothing is hard-deleted.</p>
          <button class="btn danger" onclick="deleteSheet()">Delete sheet</button></div>
      </div>
    </div>`;
}

async function duplicate(kind) {
  const name = prompt('Name for the copy', S.sheet.name + (kind === 'event' ? ' — show' : ' copy'));
  if (!name) return;
  const sheet = await api(`/api/sheets/${S.sheet.id}/duplicate`, { method: 'POST', body: { name, kind } });
  await refreshList(); go(`#/s/${sheet.id}`);
}

async function deleteSheet() {
  if (!confirmed(`Delete ${S.sheet.name}? It moves to data/trash/.`)) return;
  await api(`/api/sheets/${S.sheet.id}`, { method: 'DELETE' });
  S.sheet = null;
  await refreshList();
  go('#/');
}
