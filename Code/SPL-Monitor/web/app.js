"use strict";

const $ = (id) => document.getElementById(id);

// ---- venues & overlays --------------------------------------------------
let lastStateMs = 0;
let venuesMeta = {};
let currentVenue = null;

function isComingSoon(v) { return !!(venuesMeta[v] && venuesMeta[v].comingSoon); }
function firstLoggingVenue() { return Object.keys(venuesMeta).find((v) => !venuesMeta[v].comingSoon) || null; }

// coming-soon venues (e.g. Memorial Hall) show the under-construction screen
function applyVenueView() {
  const c = $("construction");
  if (isComingSoon(currentVenue)) {
    const cv = $("cnVenue"); if (cv) cv.textContent = currentVenue;
    if (c) c.classList.remove("hidden");
    const e = $("standby"); if (e) e.classList.add("hidden");
  } else if (c) {
    c.classList.add("hidden");
  }
}

function showStandby() { if (isComingSoon(currentVenue)) return; const e = $("standby"); if (e) e.classList.remove("hidden"); }
function hideStandby() { const e = $("standby"); if (e) e.classList.add("hidden"); }
function onStatus(m) { if (isComingSoon(currentVenue)) return; if (m && m.live) hideStandby(); else showStandby(); }

const state = {
  longSecs: 360,
  shortSecs: 10,
  history: [], // {t, inst, long}
  red: null,
  yellow: null,
};

// ---- WebSocket ----------------------------------------------------------
let ws = null;
let reconnectTimer = null;

function connect() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${proto}//${location.host}/ws`);
  ws.onopen = () => setConn(true);
  ws.onclose = () => { setConn(false); showStandby(); scheduleReconnect(); };
  ws.onerror = () => { try { ws.close(); } catch (e) {} };
  ws.onmessage = (ev) => {
    let m;
    try { m = JSON.parse(ev.data); } catch (e) { return; }
    if (m.type === "hello") onHello(m);
    else if (m.type === "history") onHistory(m);
    else if (m.type === "state") onState(m);
    else if (m.type === "status") onStatus(m);
    else if (m.type === "venue") { $("venue").value = m.venue; currentVenue = m.venue; applyVenueView(); }
    else if (m.type === "showinfo") onShowInfo(m);
    else if (m.type === "alertsToggle") { const t = $("slackToggle"); if (t) t.checked = !!m.enabled; }
  };
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => { reconnectTimer = null; connect(); }, 1500);
}

function setConn(up) {
  const el = $("conn");
  el.textContent = up ? "live" : "offline";
  el.className = "conn " + (up ? "up" : "down");
}

function onHello(m) {
  state.longSecs = m.longSecs || 360;
  state.shortSecs = m.shortSecs || 10;
  $("bigWin").textContent = fmtWin(state.shortSecs);   // hero = 10-s LAeq
  $("longLabel").textContent = fmtWin(state.longSecs); // tile = 6-min compliance
  $("predHorizon").textContent = m.horizonSeconds || 60;
  const st = $("slackToggle"); if (st) st.checked = m.alertsEnabled !== false;
  venuesMeta = m.venues || {};
  const sel = $("venue");
  sel.innerHTML = "";
  Object.keys(venuesMeta).forEach((name) => {
    const o = document.createElement("option");
    o.value = name;
    o.textContent = name + (venuesMeta[name].comingSoon ? " (soon)" : "");
    sel.appendChild(o);
  });
  if (m.venue) { sel.value = m.venue; const sv = $("sbVenue"); if (sv) sv.textContent = m.venue; }
  currentVenue = sel.value;
  sel.onchange = () => {
    currentVenue = sel.value;
    applyVenueView();
    if (!isComingSoon(currentVenue)) ws && ws.send(JSON.stringify({ type: "setVenue", venue: currentVenue }));
  };
  const fb = firstLoggingVenue();
  const cb = $("cnBack");
  if (cb && fb) { cb.textContent = "← View " + fb; cb.onclick = () => { sel.value = fb; sel.onchange(); }; }
  applyVenueView();
}

// Backfill the rolling chart on (re)connect so a refresh keeps the full window
// instead of starting empty. Points are already {t, inst, long}.
function onHistory(m) {
  if (!m || !Array.isArray(m.points)) return;
  state.history = m.points.filter((p) => p && p.t != null);
}

// ---- show/engineer banner ------------------------------------------------
function onShowInfo(m) {
  const banner = $("showBanner");
  if (!banner) return;
  if (!m || (!m.show && !m.engineer)) { banner.classList.add("hidden"); return; }
  const nameEl = $("showName"), engEl = $("showEngineer");
  if (nameEl) nameEl.textContent = m.show || "—";
  if (engEl) engEl.textContent = m.engineer || "—";
  banner.classList.remove("hidden");
}

// ---- state render -------------------------------------------------------
function onState(s) {
  lastStateMs = Date.now();
  if (isComingSoon(currentVenue)) return;  // under-construction venue selected — ignore live data
  hideStandby();
  if (s.venue) { const sv = $("sbVenue"); if (sv) sv.textContent = s.venue; }
  state.red = s.red;
  state.yellow = s.yellow;

  $("source").textContent = s.deviceName || "";
  $("instLabel").textContent = metricLabel(s.instantMetric);
  $("bigVal").textContent = fmt(s.laeqShort);       // hero = 10-s LAeq
  $("bigLimit").textContent = s.red != null ? s.red : "--";
  $("instVal").textContent = fmt(s.instant);
  $("longTileVal").textContent = fmt(s.laeqLong);  // tile = 6-min compliance

  const panel = $("bigpanel");
  panel.className = "bigpanel " + (s.light || "idle");

  // prediction
  const p = s.prediction || {};
  $("predVal").textContent = fmt(p.projected);
  const ttlLine = $("ttlLine");
  if (ttlLine) {
    if (p.timeToLimitSeconds == null) {
      ttlLine.textContent = "↓ stable";
      ttlLine.className = "ttl dim";
    } else if (p.timeToLimitSeconds <= 0) {
      ttlLine.textContent = "OVER LIMIT";
      ttlLine.className = "ttl crit";
    } else {
      const t = p.timeToLimitSeconds;
      ttlLine.textContent = "↑ limit in " + mmss(t);
      ttlLine.className = "ttl" + (t < 60 ? " crit" : t < 180 ? " warn" : "");
    }
  }

  // Davidson C-A
  const davidsonCard = (s.virtualLocations || []).find(l => l.name === "The Davidson");
  const caEl = $("davidsonCA");
  if (caEl) {
    caEl.textContent = davidsonCard && davidsonCard.ca != null ? davidsonCard.ca.toFixed(1) : "--.-";
  }

  // flags
  const flags = $("flags");
  flags.innerHTML = "";
  if (s.violation) flags.appendChild(badge("VIOLATION", "violation"));
  if (s.overload) flags.appendChild(badge("OVERLOAD", "overload"));

  // fill state
  const fillEl = $("fill");
  if (s.longFill != null && s.longFill < 0.999) {
    fillEl.textContent = `${fmtWin(state.longSecs)} window filling… ${Math.round(s.longFill * 100)}%`;
  } else {
    fillEl.textContent = `${fmtWin(state.longSecs)} window full`;
  }
  $("device").textContent = s.channelName ? `${s.deviceName} · ${s.channelName}` : "";

  updateHeadroomBar(s.headroom);
  renderLimitsStrip(s);
  renderBass(s);
  renderAllMetrics(s.allMetrics);
  renderVirtualLocations(s.virtualLocations);
  renderOrdinance(s.soundOrdinance);
  renderViolations(s.violations);

  // history for chart
  const now = s.t || (Date.now() / 1000);
  state.history.push({ t: now, inst: s.instant, long: s.laeqLong });
  const cutoff = now - state.longSecs;
  while (state.history.length && state.history[0].t < cutoff) state.history.shift();
}

function badge(text, cls) {
  const b = document.createElement("span");
  b.className = "badge " + cls;
  b.textContent = text;
  return b;
}

// ---- plain-language limits strip ---------------------------------------
function renderLimitsStrip(s) {
  const y = $("lsYellow"), r = $("lsRed");
  if (y) y.textContent = s.yellow != null ? s.yellow : "--";
  if (r) r.textContent = s.red != null ? s.red : "--";
  const b = $("lsBass");
  if (b) {
    b.textContent = (s.subArmed && s.subRed != null)
      ? "warn " + (s.subYellow != null ? s.subYellow : "--") + " / limit " + s.subRed
      : "watch";
  }
  const ord = s.soundOrdinance || {};
  const ordItem = $("lsOrdItem"), ordSep = $("lsOrdSep"), o = $("lsOrd");
  if (ord.currentLimit != null) {
    if (ordItem) ordItem.style.display = "";
    if (ordSep) ordSep.style.display = "";
    if (o) o.textContent = ord.currentLimit;
  } else {
    if (ordItem) ordItem.style.display = "none";
    if (ordSep) ordSep.style.display = "none";
  }
}

// ---- low-frequency "bass cop" — 63 Hz octave ----------------------------
function renderBass(s) {
  const sec = $("bassSection");
  if (!sec) return;
  // lamp keys off the 63 Hz octave 10-s Leq (subLight); WATCH until subRed set
  sec.className = "bass-section " + (s.subLight || "idle");
  $("bassShort").textContent = fmt(s.subShort);   // big = 63 Hz 10-s Leq (lamp metric)
  $("bassLong").textContent = fmt(s.subLong);     // tile = 63 Hz 1-min Leq
  $("bassInst").textContent = fmt(s.laeqLongC);   // secondary = full-band 6-min LCeq
  const ca = $("bassCA");
  if (ca) ca.textContent = s.caTilt != null ? (s.caTilt > 0 ? "+" : "") + Number(s.caTilt).toFixed(1) : "--.-";
  $("bassLimit").textContent = s.subRed != null ? s.subRed + " dB" : "—";
  const band = s.subBandLabel ? " · " + s.subBandLabel : "";
  const note = $("bassNote");
  if (note) {
    if (s.subArmed) {
      note.textContent = "63 Hz octave · building-transmission / complaint band · 10-s limit " + s.subRed + " dB" + band;
    } else if (s.subLong != null || s.subShort != null) {
      note.textContent = "63 Hz octave · 10-s Leq is the live number · WATCH mode — no limit set yet" + band;
    } else {
      note.textContent = "63 Hz octave · waiting for the band metric from Smaart…";
    }
  }
}

// ---- headroom bar -------------------------------------------------------
function updateHeadroomBar(headroom) {
  // headroom: positive = dB under limit, negative = dB over limit
  // Left segs (0-4): light red when OVER. Seg 4 = 0-2 over, seg 0 = 8-10 over.
  // Right segs (5-9): light green/yellow when UNDER. Seg 5 = 0-2 headroom, seg 9 = 8-10.
  // Each segment = 2 dB.

  const valEl = $("hbarVal");
  if (valEl) {
    valEl.textContent = headroom != null
      ? (headroom > 0 ? "+" : "") + Number(headroom).toFixed(1)
      : "--";
    valEl.className = "hbar-num" + (
      headroom == null ? "" :
      headroom > 4  ? " hbar-ok" :
      headroom > 0  ? " hbar-warn" :
                      " hbar-over");
  }

  // pick color for right (headroom) segs based on overall headroom
  const rightCls = headroom == null ? "" :
    headroom > 6 ? "hbar-green" :
    headroom > 3 ? "hbar-lgreen" :
    headroom > 0 ? "hbar-yellow" : "";

  for (let i = 0; i < 10; i++) {
    const seg = document.getElementById("hs" + i);
    if (!seg) continue;
    let cls = "hbar-seg";
    if (headroom != null) {
      if (i < 5) {
        // left (over) zone: seg 4 fires first (just over), seg 0 fires last (10 dB over)
        // threshold: seg lights when headroom < -(2*(4-i)) = 2*(i-4)
        const thresh = 2 * (i - 4); // seg4=-0, seg3=-2, seg2=-4, seg1=-6, seg0=-8
        if (headroom <= thresh) {
          cls += i >= 3 ? " hbar-orange" : " hbar-red";
        }
      } else {
        // right (headroom) zone: seg 5 fires first (any headroom), seg 9 fires last (8+)
        const thresh = 2 * (i - 5); // seg5=0, seg6=2, seg7=4, seg8=6, seg9=8
        if (headroom > thresh) cls += " " + rightCls;
      }
    }
    seg.className = cls;
  }
}

// ---- all metrics --------------------------------------------------------
const AM_ORDER = [
  "SPL A Slow", "SPL A Fast", "SPL C Slow", "SPL C Fast", "SPL Slow", "SPL Fast",
  "LAeq 1s", "LAeq 1", "LAeq 3", "LAeq 6", "LAeq 10s",
  "LCeq 1", "LCeq 3", "LCeq 10s", "Leq 1", "Leq 10s C-A",
  "Peak C", "FS Peak", "Exposure O", "Exposure N",
];
const AM_UNIT = { "Exposure O": "Pa²h", "Exposure N": "Pa²h", "FS Peak": "dBFS" };

function renderAllMetrics(metrics) {
  if (!metrics) return;
  const grid = $("amGrid");
  // AM_ORDER first, then any streamed key not already listed (e.g. the
  // auto-detected 63 Hz octave labels) so new metrics surface without a code change.
  const extra = Object.keys(metrics).filter((k) => !AM_ORDER.includes(k)).sort();
  const order = AM_ORDER.concat(extra);
  const sig = order.join("|");
  if (grid._sig !== sig) {
    grid.innerHTML = "";
    order.forEach((key) => {
      const cell = document.createElement("div");
      cell.className = "am-cell";
      cell.id = "am-" + key.replace(/[\s.]/g, "_");
      const unit = AM_UNIT[key] || "dB";
      cell.innerHTML = `<span class="am-label">${key}</span><span class="am-val">--</span><span class="am-unit">${unit}</span>`;
      grid.appendChild(cell);
    });
    grid._sig = sig;
  }
  order.forEach((key) => {
    const el = document.getElementById("am-" + key.replace(/[\s.]/g, "_"));
    if (!el) return;
    const v = metrics[key];
    el.querySelector(".am-val").textContent = (v != null && !Number.isNaN(v)) ? Number(v).toFixed(2) : "--";
  });
}

// ---- virtual locations --------------------------------------------------
let _virtBuilt = false;
let _virtNames = [];

function renderVirtualLocations(locs) {
  if (!locs || !locs.length) return;
  const section = $("virtSection");
  const grid = $("virtGrid");
  section.style.display = "";

  const names = locs.map((l) => l.name);
  if (!_virtBuilt || names.join("|") !== _virtNames.join("|")) {
    grid.innerHTML = "";
    locs.forEach((loc) => {
      const card = document.createElement("div");
      card.className = "virt-card idle";
      card.id = "vc-" + loc.name.replace(/[^a-zA-Z0-9]/g, "_");
      const sign = (n) => (n >= 0 ? "+" : "") + n.toFixed(2);
      card.innerHTML = `
        <div class="vc-name">${loc.name}</div>
        <div class="vc-main"><span class="vc-val">--.-</span><span class="vc-unit">dBA</span></div>
        <div class="vc-sub">LAeq 10s est.</div>
        <div class="vc-lceq">LCeq: <span class="vc-lceq-val">--.-</span> dBC</div>
        <div class="vc-offset dim">${sign(loc.offsetA)}A / ${sign(loc.offsetC)}C</div>
        <div class="vc-badge">SPL COMPENSATION · REFERENCE ONLY</div>`;
      grid.appendChild(card);
    });
    _virtBuilt = true;
    _virtNames = names;
  }

  locs.forEach((loc) => {
    const card = document.getElementById("vc-" + loc.name.replace(/[^a-zA-Z0-9]/g, "_"));
    if (!card) return;
    card.className = "virt-card " + (loc.light || "idle");
    card.querySelector(".vc-val").textContent = fmt(loc.laeq10s);
    card.querySelector(".vc-lceq-val").textContent = fmt(loc.lceq10s);
  });
}

// ---- sound ordinance ----------------------------------------------------
let _ordBuilt = false;
let _ordNames = [];

function renderOrdinance(ord) {
  if (!ord || !ord.cards || !ord.cards.length) return;
  const section = $("ordSection");
  const grid = $("ordGrid");
  section.style.display = "";

  const limitEl = $("ordLimit");
  if (limitEl) limitEl.textContent = ord.currentLimit != null ? ord.currentLimit : "--";

  const locs = ord.cards;
  const names = locs.map((l) => l.name);
  if (!_ordBuilt || names.join("|") !== _ordNames.join("|")) {
    grid.innerHTML = "";
    locs.forEach((loc) => {
      const card = document.createElement("div");
      card.className = "ord-card idle";
      card.id = "orc-" + loc.name.replace(/[^a-zA-Z0-9]/g, "_");
      card.innerHTML = `
        <div class="orc-name">${loc.name}</div>
        <div class="orc-main"><span class="orc-val">--.-</span><span class="orc-unit">dBA</span></div>
        <div class="orc-sub">LAeq 6-min</div>
        ${loc.virtual ? '<div class="orc-tag dim">Estimated</div>' : '<div class="orc-tag live">Live FOH</div>'}`;
      grid.appendChild(card);
    });
    _ordBuilt = true;
    _ordNames = names;
  }

  locs.forEach((loc) => {
    const card = document.getElementById("orc-" + loc.name.replace(/[^a-zA-Z0-9]/g, "_"));
    if (!card) return;
    card.className = "ord-card " + (loc.light || "idle");
    card.querySelector(".orc-val").textContent = fmt(loc.laeq6);
  });
}

function renderViolations(v) {
  if (!v) return;
  $("violCount").textContent = v.count;
  $("violBox").classList.toggle("hit", v.count > 0);
  $("violRule").textContent = (v.sustainSeconds > 0)
    ? ("≥" + v.threshold + " dBA · " + v.sustainSeconds + "s")
    : (metricLabel(v.metric) + " ≥ " + v.threshold + " dBA");
  const row = $("violRow");
  const st = $("violStatus");
  if (v.inViolation) {
    st.textContent = "OVER NOW · " + mmss(v.currentDurationSec);
    st.className = "viol-status over";
    row.classList.add("alarm");
  } else {
    st.textContent = "clear";
    st.className = "viol-status clear";
    row.classList.remove("alarm");
  }
  $("violTotal").textContent = mmss(v.totalTimeOverSec);
  const lv = v.lastViolation;
  $("violLast").textContent = lv ? ("#" + lv.number + " · " + mmss(lv.durationSec) + " · " + lv.peak + " dBA") : "—";
  $("violPolicy").textContent =
    "Slack from violation " + v.alertFromViolation + " · and any over " + Math.round(v.longSeconds / 60) + " min";
}

// ---- chart --------------------------------------------------------------
const canvas = $("chart");
const ctx = canvas.getContext("2d");

function resize() {
  // Canvas is position:absolute (out of flow), so the wrapper's size is
  // independent of the canvas — no feedback loop. Size the canvas explicitly.
  const wrap = canvas.parentElement;
  const cw = Math.max(1, wrap.clientWidth - 16);
  const ch = Math.max(1, wrap.clientHeight - 16);
  if (canvas._cw === cw && canvas._ch === ch) return;
  canvas._cw = cw; canvas._ch = ch;
  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = cw + "px";
  canvas.style.height = ch + "px";
  canvas.width = Math.floor(cw * dpr);
  canvas.height = Math.floor(ch * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener("resize", resize);

function draw() {
  resize(); // self-healing against late layout / viewport changes
  const W = canvas._cw, H = canvas._ch;
  ctx.clearRect(0, 0, W, H);

  const padL = 38, padR = 10, padT = 10, padB = 18;
  const x0 = padL, x1 = W - padR, y0 = padT, y1 = H - padB;

  // y scale: fixed 70–100 dB (per Brian — nothing below 70 needed).
  // Clamp to the plot box so the rare >100 peak rides the top edge instead of
  // drawing up into the axis labels.
  const lo = 70, hi = 100;
  const yOf = (v) => {
    const y = y1 - (v - lo) / (hi - lo) * (y1 - y0);
    return Math.max(y0, Math.min(y1, y));
  };

  // grid + y labels
  ctx.strokeStyle = "#222a34"; ctx.fillStyle = "#6b7686";
  ctx.font = "11px -apple-system, sans-serif";
  ctx.lineWidth = 1;
  for (let v = lo; v <= hi; v += 5) {
    const y = yOf(v);
    ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
    ctx.fillText(String(v), 6, y + 3);
  }

  // time scale across longSecs
  const now = state.history.length ? state.history[state.history.length - 1].t : Date.now() / 1000;
  const tStart = now - state.longSecs;
  const xOf = (t) => x0 + (t - tStart) / state.longSecs * (x1 - x0);

  // limit lines (labeled at the right edge)
  if (state.yellow != null) limitLine(yOf(state.yellow), "#f1c40f", x0, x1, "warn " + state.yellow);
  if (state.red != null) limitLine(yOf(state.red), "#e74c3c", x0, x1, "limit " + state.red);

  // instant (faint)
  line(state.history, "inst", xOf, yOf, "#5b6675", 1);
  // long LAeq (bold)
  line(state.history, "long", xOf, yOf, "#4aa3ff", 2.4);
}

function line(hist, key, xOf, yOf, color, width) {
  ctx.strokeStyle = color; ctx.lineWidth = width;
  ctx.beginPath();
  let started = false;
  for (const p of hist) {
    if (p[key] == null) continue;
    const x = xOf(p.t), y = yOf(p[key]);
    if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
  }
  ctx.stroke();
}

function limitLine(y, color, x0, x1, label) {
  ctx.save();
  ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.setLineDash([6, 5]);
  ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
  if (label) {
    ctx.setLineDash([]);
    ctx.fillStyle = color;
    ctx.font = "10px -apple-system, sans-serif";
    ctx.textAlign = "right";
    ctx.fillText(label, x1 - 3, y - 3);
    ctx.textAlign = "left";
  }
  ctx.restore();
}

function tick() { draw(); requestAnimationFrame(tick); }

// ---- helpers ------------------------------------------------------------
function fmt(v) { return (v == null || Number.isNaN(v)) ? "--.-" : Number(v).toFixed(1); }
function mmss(s) {
  s = Math.max(0, Math.round(s));
  const m = Math.floor(s / 60), ss = s % 60;
  return m > 0 ? `${m}:${String(ss).padStart(2, "0")}` : `${ss}s`;
}
function fmtWin(secs) {
  if (secs % 60 === 0) return `${secs / 60}-min`;
  return `${secs}-s`;
}

function metricLabel(m) {
  const map = {
    "SPL A Slow": "dBA Slow", "SPL A Fast": "dBA Fast",
    "SPL C Slow": "dBC Slow", "SPL C Fast": "dBC Fast",
    "SPL Slow": "dBZ Slow", "SPL Fast": "dBZ Fast",
  };
  return map[m] || m || "";
}

function clockTick() {
  const t = new Date().toLocaleTimeString("en-US", { timeZone: "America/New_York" });
  $("clock").textContent = t;
  const sc = $("sbClock"); if (sc) sc.textContent = t;
}

// ---- reset modal --------------------------------------------------------
(function () {
  const modal = $("resetModal");
  const input = $("resetInput");
  const err   = $("resetErr");

  function openModal() {
    input.value = "";
    err.classList.add("hidden");
    modal.classList.remove("hidden");
    setTimeout(() => input.focus(), 40);
  }

  function closeModal() {
    modal.classList.add("hidden");
    input.value = "";
  }

  function shake() {
    input.classList.add("shake");
    setTimeout(() => input.classList.remove("shake"), 500);
  }

  async function doReset() {
    const code = input.value;
    if (!code) { shake(); return; }
    err.classList.add("hidden");
    try {
      const r = await fetch("/api/reset-strikes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ passcode: code }),
      });
      if (r.ok) {
        closeModal();
      } else {
        err.classList.remove("hidden");
        shake();
        input.value = "";
        setTimeout(() => input.focus(), 10);
      }
    } catch (e) {
      err.textContent = "Connection error — try again.";
      err.classList.remove("hidden");
    }
  }

  $("resetBtn").addEventListener("click", openModal);
  $("resetCancel").addEventListener("click", closeModal);
  $("resetConfirm").addEventListener("click", doReset);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") doReset();
    if (e.key === "Escape") closeModal();
  });
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
})();

// ---- Slack alert toggle --------------------------------------------------
(function () {
  const toggle = $("slackToggle");
  if (!toggle) return;
  const modal = $("slackModal");
  const input = $("slackInput");
  const err   = $("slackErr");

  async function postToggle(enabled, passcode) {
    const body = passcode != null ? { enabled, passcode } : { enabled };
    return fetch("/api/toggle-alerts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  function closeModal() { modal.classList.add("hidden"); input.value = ""; }
  function shake() {
    input.classList.add("shake");
    setTimeout(() => input.classList.remove("shake"), 500);
  }

  async function confirmOff() {
    const code = input.value;
    if (!code) { shake(); return; }
    err.classList.add("hidden");
    try {
      const r = await postToggle(false, code);
      if (r.ok) {
        closeModal();               // server broadcasts the toggled state
      } else {
        err.classList.remove("hidden");
        shake();
        input.value = "";
        setTimeout(() => input.focus(), 10);
      }
    } catch (e) {
      err.textContent = "Connection error — try again.";
      err.classList.remove("hidden");
    }
  }

  function cancelOff() {
    closeModal();
    toggle.checked = true;          // it stays ON until a valid passcode disables it
  }

  toggle.addEventListener("change", async () => {
    // turning OFF requires the passcode; turning ON is free
    if (!toggle.checked) {
      input.value = "";
      err.classList.add("hidden");
      modal.classList.remove("hidden");
      setTimeout(() => input.focus(), 40);
      return;
    }
    try {
      const r = await postToggle(true);
      if (!r.ok) throw new Error("bad response");
    } catch (e) {
      toggle.checked = false; // revert on failure
    }
  });

  $("slackCancel").addEventListener("click", cancelOff);
  $("slackConfirm").addEventListener("click", confirmOff);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") confirmOff();
    if (e.key === "Escape") cancelOff();
  });
  modal.addEventListener("click", (e) => { if (e.target === modal) cancelOff(); });
})();

// ---- boot ---------------------------------------------------------------
resize();
requestAnimationFrame(tick);
setInterval(clockTick, 1000); clockTick();
setInterval(() => { if (Date.now() - lastStateMs > 10000) showStandby(); }, 2000);
connect();
