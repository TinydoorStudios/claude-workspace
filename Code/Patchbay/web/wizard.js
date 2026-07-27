/* Patchbay — New Patch Sheet wizard.

   Four steps: Location → Console → I/O Devices → Confirm. Each step renders
   into #wizard; state lives in W.data until "Create patch sheet" POSTs it to
   /api/sheets as {wizard: …}. Nothing is written server-side before that.

   Same table rule as the rest of the app applies here: field handlers write to
   W.data only — they never re-render the step they're being typed into. Steps
   repaint on navigation. */

const W = {
  step: 0,
  data: null,
  onDone: null,
  busy: false,
};

const STEPS = ['Location', 'Console', 'I/O Devices', 'Confirm'];

function blankWizard() {
  return {
    location: { project: '', client: '', site: '', room: '', address: '', city: '', state: '', zip: '' },
    kind: 'install',
    venue: '',
    from_template: '',
    console: {
      preset: '', manufacturer: '', model: '', fw: '',
      ip: '', subnet: '', gateway: '', dns: '',
      channels: '', busses: '', auxes: '', dcas: '', mutes: '', matrix: '',
      local_in: '', local_out: '',
    },
    devices: [{ name: '', inputs: '', outputs: '', ip: '' }],
  };
}

function openWizard(onDone) {
  W.data = blankWizard();
  W.step = 0;
  W.onDone = onDone;
  W.busy = false;
  const venue = S.kb.venues[0];
  if (venue) { W.data.venue = venue.id; applyPreset(venue.console); }
  $('#wizard').hidden = false;
  document.body.style.overflow = 'hidden';
  renderWizard();
  setTimeout(() => $('#pw-first')?.focus(), 0);
}

function closeWizard() {
  $('#wizard').hidden = true;
  document.body.style.overflow = '';
}

/* Desk preset → manufacturer/model/counts, straight off knowledge/consoles.json. */
function applyPreset(consoleId) {
  const c = consoleDef(consoleId);
  if (!c) return;
  const b = c.buses || {};
  const count = (groups) => groups.reduce((n, g) => n + (g.analog ? g.count : 0), 0);
  Object.assign(W.data.console, {
    preset: c.id,
    manufacturer: c.vendor,
    model: c.label.replace(new RegExp('^' + c.vendor + '\\s*'), ''),
    channels: c.channels,
    busses: b.aux_group ?? b.bus ?? '',
    auxes: b.aux ?? '',
    dcas: b.dca ?? '',
    mutes: b.mute_groups ?? '',
    matrix: b.matrix_out ?? b.matrix ?? '',
    local_in: count(c.input_ports),
    local_out: count(c.output_ports),
  });
}

/* ------------------------------------------------------------ render */
function renderWizard() {
  const steps = STEPS.map((name, i) => `
    <div class="pw-step ${i === W.step ? 'on' : ''} ${i < W.step ? 'done' : ''}">
      <div class="pw-label">
        <span class="pw-num">${i < W.step ? '✓' : i + 1}</span>
        <span class="pw-name">${name}</span>
      </div>
      ${i < STEPS.length - 1 ? '<div class="pw-line"></div>' : ''}
    </div>`).join('');

  $('#wizard').innerHTML = `
    <div class="pw-shell">
      <header class="pw-header">
        <span class="pw-brand">Patchbay</span>
        <span class="pw-slash">/</span>
        <span class="pw-crumb">New Patch Sheet</span>
      </header>
      <main class="pw-main">
        <div class="pw-steps">${steps}</div>
        <div class="pw-body">${[stepLocation, stepConsole, stepDevices, stepConfirm][W.step]()}</div>
        <div class="pw-foot">
          ${W.step === 0
            ? '<button class="pw-btn" id="pw-cancel">Cancel</button>'
            : '<button class="pw-btn" id="pw-back">Back</button>'}
          <button class="pw-btn primary" id="pw-next">
            ${W.step === 3 ? (W.busy ? 'Creating…' : 'Create Patch Sheet') : 'Continue'}
            <span class="pw-arrow">→</span>
          </button>
        </div>
      </main>
    </div>`;

  wireWizard();
}

const field = (path, label, ph, { span = 2, type = 'text', help = '', first = false } = {}) => `
  <div class="pw-field c${span}">
    <label for="pw-${path}">${label}</label>
    <input class="pw-input" id="${first ? 'pw-first' : 'pw-' + path}" data-path="${path}"
      type="${type}" placeholder="${esc(ph)}" value="${esc(get(path) ?? '')}">
    ${help ? `<span class="pw-help">${help}</span>` : ''}
  </div>`;

const get = (path) => path.split('.').reduce((o, k) => (o == null ? o : o[k]), W.data);
const set = (path, v) => {
  const keys = path.split('.');
  const last = keys.pop();
  keys.reduce((o, k) => o[k], W.data)[last] = v;
};

function stepLocation() {
  const venues = S.kb.venues.map((v) => `<option value="${esc(v.id)}"${v.id === W.data.venue ? ' selected' : ''}>${esc(v.label)}</option>`).join('');
  const tpls = S.sheets.filter((s) => s.kind === 'install')
    .map((s) => `<option value="${esc(s.id)}"${s.id === W.data.from_template ? ' selected' : ''}>${esc(s.name)}</option>`).join('');
  return `
    <h1 class="pw-h1">Location Information</h1>
    <div class="pw-grid">
      ${field('location.project', 'Project Name', 'e.g. Memorial Hall FOH', { first: true })}
      ${field('location.client', 'Client / Organization', 'e.g. Jazz At The Memo')}
      ${field('location.site', 'Site Name', 'e.g. Memorial Hall')}
      ${field('location.room', 'Site Room', 'e.g. FOH, Amp Room')}
      ${field('location.address', 'Site Address', '1225 Elm St', { span: 4 })}
      ${field('location.city', 'City', 'Cincinnati')}
      ${field('location.state', 'State', 'OH', { span: 1 })}
      ${field('location.zip', 'Zip', '45202', { span: 1 })}
    </div>
    <hr class="pw-rule">
    <div>
      <p class="pw-section">Patchbay</p>
      <div class="pw-grid">
        <div class="pw-field c2">
          <label for="pw-venue">Venue</label>
          <select class="pw-select" id="pw-venue" data-path="venue"><option value="">— none —</option>${venues}</select>
          <span class="pw-help">Sets the desk preset on the next step.</span>
        </div>
        <div class="pw-field c2">
          <label for="pw-kind">Sheet type</label>
          <select class="pw-select" id="pw-kind" data-path="kind">
            <option value="install"${W.data.kind === 'install' ? ' selected' : ''}>Template — installed rig</option>
            <option value="event"${W.data.kind === 'event' ? ' selected' : ''}>Event — one-off show</option>
          </select>
        </div>
        <div class="pw-field c4">
          <label for="pw-tpl">Start from <span class="pw-opt">(optional)</span></label>
          <select class="pw-select" id="pw-tpl" data-path="from_template"><option value="">Blank sheet</option>${tpls}</select>
          <span class="pw-help">Copies an existing rig — console, boxes, outputs and power come with it.</span>
        </div>
      </div>
    </div>`;
}

function stepConsole() {
  const presets = S.kb.consoles.map((c) => `<option value="${esc(c.id)}"${c.id === W.data.console.preset ? ' selected' : ''}>${esc(c.label)}</option>`).join('');
  return `
    <h1 class="pw-h1">Console Information</h1>
    <hr class="pw-rule">
    <div>
      <p class="pw-section">Console</p>
      <div class="pw-grid">
        <div class="pw-field c4">
          <label for="pw-preset">Desk</label>
          <select class="pw-select" id="pw-preset" data-preset><option value="">— custom —</option>${presets}</select>
          <span class="pw-help">Picking a desk fills the fields below from Patchbay's console data. Edit anything after.</span>
        </div>
        ${field('console.manufacturer', 'Manufacturer', 'e.g. DiGiCo', { span: 2, first: true })}
        ${field('console.model', 'Model', 'e.g. Quantum 225')}
        ${field('console.fw', 'FW Version', 'e.g. 2.4.1', { span: 4 })}
      </div>
    </div>
    <hr class="pw-rule">
    <div>
      <p class="pw-section">Networking</p>
      <div class="pw-grid">
        ${field('console.ip', 'IP Address', '192.168.1.101', { span: 1 })}
        ${field('console.subnet', 'Subnet', '255.255.255.0', { span: 1 })}
        ${field('console.gateway', 'Gateway', '192.168.1.1', { span: 1 })}
        ${field('console.dns', 'DNS Server', '8.8.8.8', { span: 1 })}
      </div>
    </div>
    <hr class="pw-rule">
    <div>
      <p class="pw-section">Channel Configuration</p>
      <div class="pw-grid">
        ${field('console.channels', 'Input Channels', '0', { span: 1, type: 'number' })}
        ${field('console.busses', 'Busses', '0', { span: 1, type: 'number' })}
        ${field('console.auxes', 'Auxes', '0', { span: 1, type: 'number' })}
        ${field('console.dcas', 'DCAs / VCAs', '0', { span: 1, type: 'number' })}
        ${field('console.mutes', 'Mute Groups', '0', { span: 1, type: 'number' })}
        ${field('console.matrix', 'Matrix', '0', { span: 1, type: 'number' })}
      </div>
    </div>
    <hr class="pw-rule">
    <div>
      <p class="pw-section">I/O</p>
      <p class="pw-help" style="margin:-6px 0 12px">Console local I/O — adds the desk itself as a patchable I/O source.</p>
      <div class="pw-grid">
        ${field('console.local_in', 'Console Inputs', '0', { span: 2, type: 'number' })}
        ${field('console.local_out', 'Console Outputs', '0', { span: 2, type: 'number' })}
      </div>
    </div>`;
}

function stepDevices() {
  const cards = W.data.devices.map((d, i) => `
    <div class="pw-card">
      <p class="pw-cardhead">Device ${i + 1}
        ${W.data.devices.length > 1 ? `<button class="pw-linkbtn" data-rmdev="${i}" style="float:right">Remove</button>` : ''}</p>
      <div class="pw-devgrid">
        <div class="pw-field c2">
          <label>I/O Device Name</label>
          <input class="pw-input" data-dev="${i}" data-k="name" placeholder="e.g. SD-Rack, DL32, StageConnect"
            value="${esc(d.name)}"${i === 0 ? ' id="pw-first"' : ''}>
        </div>
        <div class="pw-field c1">
          <label># Inputs</label>
          <input class="pw-input" type="number" data-dev="${i}" data-k="inputs" placeholder="0" value="${esc(d.inputs)}">
        </div>
        <div class="pw-field c1">
          <label># Outputs</label>
          <input class="pw-input" type="number" data-dev="${i}" data-k="outputs" placeholder="0" value="${esc(d.outputs)}">
        </div>
        <div class="pw-field c2">
          <label>IP Address <span class="pw-opt">(optional)</span></label>
          <input class="pw-input" data-dev="${i}" data-k="ip" placeholder="192.168.1.x" value="${esc(d.ip)}">
        </div>
      </div>
    </div>`).join('');
  return `
    <div class="pw-h1row">
      <h1 class="pw-h1">I/O Devices</h1>
      <button class="pw-btn" id="pw-adddev">+ Add I/O</button>
    </div>
    ${cards}`;
}

function stepConfirm() {
  const l = W.data.location;
  const c = W.data.console;
  const venue = S.kb.venues.find((v) => v.id === W.data.venue);
  const tpl = S.sheets.find((s) => s.id === W.data.from_template);
  const devices = W.data.devices.filter((d) => d.name || d.inputs || d.outputs);
  const site = [l.site, l.room].filter(Boolean).join(' · ');
  const addr = [l.address, l.city, l.state, l.zip].filter(Boolean).join(', ');
  const kv = (k, v) => (v ? `<span class="pw-dim">${k}:</span> ${esc(v)}` : '');
  return `
    <h1 class="pw-h1">New Patch Sheet Confirmation</h1>
    <div class="pw-card pw-summary">
      <div class="pw-blk">
        <div class="pw-k">Location</div>
        <div class="pw-v"><span class="pw-pill">${esc(l.project || 'Untitled rig')}</span></div>
        ${l.client ? `<div class="pw-v">${esc(l.client)}</div>` : ''}
        ${site ? `<div class="pw-v">${esc(site)}</div>` : ''}
        ${addr ? `<div class="pw-v pw-dim">${esc(addr)}</div>` : ''}
      </div>
      <div class="pw-blk">
        <div class="pw-k">Console</div>
        <div class="pw-v">${[kv('Mfr', c.manufacturer), kv('Model', c.model), kv('FW', c.fw)].filter(Boolean).join(' &nbsp; ') || '<span class="pw-dim">not specified</span>'}</div>
        <div class="pw-v">${[kv('Inputs', c.channels), kv('Busses', c.busses), kv('Auxes', c.auxes), kv('DCAs', c.dcas), kv('Matrix', c.matrix)].filter(Boolean).join(' &nbsp; ')}</div>
        ${c.ip ? `<div class="pw-v">${kv('IP', c.ip)} &nbsp; ${kv('GW', c.gateway)}</div>` : ''}
      </div>
      <div class="pw-blk">
        <div class="pw-k">I/O Devices</div>
        ${devices.length
          ? devices.map((d) => `<div class="pw-v">${esc(d.name || 'Unnamed')} — <span class="pw-dim">${esc(d.inputs || 0)}in / ${esc(d.outputs || 0)}out${d.ip ? ' · ' + esc(d.ip) : ''}</span></div>`).join('')
          : '<div class="pw-v pw-dim">None</div>'}
      </div>
      <div class="pw-blk">
        <div class="pw-k">Patchbay</div>
        <div class="pw-v">${W.data.kind === 'event' ? 'Event — one-off show' : 'Template — installed rig'}${venue ? ' · ' + esc(venue.label) : ''}</div>
        ${tpl ? `<div class="pw-v pw-dim">Copied from ${esc(tpl.name)}</div>` : ''}
      </div>
    </div>`;
}

/* -------------------------------------------------------------- wire */
function wireWizard() {
  $$('#wizard [data-path]').forEach((el) => {
    const write = (e) => {
      set(el.dataset.path, e.target.value);
      if (el.dataset.path === 'venue') {
        const v = S.kb.venues.find((x) => x.id === e.target.value);
        if (v) applyPreset(v.console);
      }
    };
    el.oninput = write;
    el.onchange = write;
  });

  const preset = $('#wizard [data-preset]');
  if (preset) preset.onchange = (e) => { if (e.target.value) { applyPreset(e.target.value); renderWizard(); } };

  $$('#wizard [data-dev]').forEach((el) => (el.oninput = (e) => {
    W.data.devices[+el.dataset.dev][el.dataset.k] = e.target.value;
  }));
  const add = $('#pw-adddev');
  if (add) add.onclick = () => { W.data.devices.push({ name: '', inputs: '', outputs: '', ip: '' }); renderWizard(); };
  $$('#wizard [data-rmdev]').forEach((b) => (b.onclick = () => {
    W.data.devices.splice(+b.dataset.rmdev, 1); renderWizard();
  }));

  const back = $('#pw-back');
  if (back) back.onclick = () => { W.step--; renderWizard(); };
  const cancel = $('#pw-cancel');
  if (cancel) cancel.onclick = closeWizard;
  $('#pw-next').onclick = nextStep;
}

async function nextStep() {
  if (W.step < 3) { W.step++; renderWizard(); return; }
  if (W.busy) return;
  W.busy = true; renderWizard();
  try {
    const d = W.data;
    const sheet = await api('/api/sheets', {
      method: 'POST',
      body: {
        name: d.location.project || 'Untitled rig',
        kind: d.kind,
        venue: d.venue,
        console: d.console.preset || 'q225',
        channels: parseInt(d.console.channels || '32', 10),
        from_template: d.from_template || null,
        wizard: {
          location: d.location,
          console_info: d.console,
          devices: d.devices.filter((x) => x.name || x.inputs || x.outputs),
        },
      },
    });
    closeWizard();
    W.onDone?.(sheet);
  } catch (err) {
    W.busy = false; renderWizard();
    alert('Could not create the sheet: ' + err.message);
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !$('#wizard').hidden) closeWizard();
});
