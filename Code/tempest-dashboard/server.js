require('dotenv').config();
const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const TOKEN = process.env.TEMPEST_TOKEN;
const PORT = process.env.PORT || 3001;
const POLL_INTERVAL = parseInt(process.env.POLL_INTERVAL_MS) || 30000;

if (!TOKEN) {
  console.error('TEMPEST_TOKEN not set in .env — exiting.');
  process.exit(1);
}

// deviceId = the station's Tempest (ST) sensor. Lightning comes from the
// per-device feed, NOT the station rollup (which reports distance in km even
// when miles are requested, and only ever exposes the single last strike).
const STATIONS = [
  { id: 215217, name: 'Fountain Square', deviceId: 1217262 },
  { id: 211956, name: 'Elm Street Plaza', deviceId: 1208440 },
  { id: 216868, name: 'Zeigler Park',     deviceId: 1220691 },
];

const HISTORY_FILE = path.join(__dirname, 'history.json');
const HISTORY_WINDOW = 24 * 60 * 60 * 1000;   // 24 hours in ms
const MIN_HISTORY_GAP = 60 * 1000;              // one point per minute max

// Lightning rings: a strike within N miles in the last 30 min keeps that ring
// active. "Clear" = no strike inside 30 mi for a full 30 min. The 30-min device
// window is the resetting clock — old strikes age out, no server state needed.
const LIGHTNING_THRESHOLDS_MI = [1, 5, 30];     // red / orange / not-clear gates
const LIGHTNING_WINDOW_S = 30 * 60;             // resetting-clock window
const KM_TO_MI = 0.621371;
const DEV_LTNG_DIST = 14;  // Tempest obs_st array index: lightning avg distance (km)
const DEV_LTNG_COUNT = 15; // Tempest obs_st array index: lightning strike count

const stationData = {};
const history = {};          // { "stationId": [{t: ms, f: tempF}, ...] }
const lightningByStation = {}; // { stationId: {within:{1,5,30}, closestMi, lastEpoch, count1hr} }

// ── History persistence ────────────────────────────────────────────────────

function loadHistory() {
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      const raw = fs.readFileSync(HISTORY_FILE, 'utf8');
      const loaded = JSON.parse(raw);
      const cutoff = Date.now() - HISTORY_WINDOW;
      Object.entries(loaded).forEach(([id, points]) => {
        history[id] = Array.isArray(points) ? points.filter(p => p.t >= cutoff) : [];
      });
      const total = Object.values(history).reduce((s, pts) => s + pts.length, 0);
      console.log(`[startup] History loaded — ${Object.keys(history).length} stations, ${total} points`);
    }
  } catch (e) {
    console.warn(`[startup] Could not load history: ${e.message}`);
  }
}

function saveHistory() {
  try {
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(history), 'utf8');
  } catch (e) {
    console.warn(`[history] Save failed: ${e.message}`);
  }
}

function appendHistory(id, tempC) {
  if (tempC == null) return;
  const tempF = Math.round((tempC * 9 / 5 + 32) * 10) / 10;
  const now   = Date.now();
  const key   = String(id);

  if (!history[key]) history[key] = [];
  const last = history[key][history[key].length - 1];
  if (last && now - last.t < MIN_HISTORY_GAP) return; // throttle to 1/min

  history[key].push({ t: now, f: tempF });
  const cutoff = now - HISTORY_WINDOW;
  history[key] = history[key].filter(p => p.t >= cutoff);
}

// ── Lightning (per-device, true 30-min sliding window) ──────────────────────

// Reduce a device obs series to per-ring activity, closest strike, and counts.
// Device distance is kilometers — convert to miles here.
function computeLightning(devObs) {
  const now = Math.floor(Date.now() / 1000);
  const strikes = (devObs || [])
    .filter(o => Array.isArray(o) && o.length > DEV_LTNG_COUNT && (o[DEV_LTNG_COUNT] || 0) > 0
                 && o[DEV_LTNG_DIST] != null)
    .map(o => ({ ep: o[0], mi: o[DEV_LTNG_DIST] * KM_TO_MI, n: o[DEV_LTNG_COUNT] }));

  const win30 = strikes.filter(s => now - s.ep <= LIGHTNING_WINDOW_S);
  const win60 = strikes.filter(s => now - s.ep <= 3600);

  const within = {};
  LIGHTNING_THRESHOLDS_MI.forEach(r => {
    const inRing = win30.filter(s => s.mi <= r);
    within[r] = inRing.length ? Math.max(...inRing.map(s => s.ep)) : 0;
  });

  return {
    within,                                                                   // last in-range strike epoch per ring (0 = none)
    closestMi: win30.length ? Math.round(Math.min(...win30.map(s => s.mi))) : null,
    lastEpoch: win30.length ? Math.max(...win30.map(s => s.ep)) : null,
    count1hr:  win60.reduce((a, s) => a + s.n, 0),
  };
}

// ── API polling ────────────────────────────────────────────────────────────

function httpGetJson(url) {
  return new Promise((resolve) => {
    https.get(url, (res) => {
      let raw = '';
      res.on('data', chunk => (raw += chunk));
      res.on('end', () => { try { resolve(JSON.parse(raw)); } catch (e) { resolve(null); } });
    }).on('error', () => resolve(null));
  });
}

async function fetchStation(station) {
  const params = new URLSearchParams({
    token: TOKEN, units_temp: 'f', units_wind: 'mph',
    units_pressure: 'inhg', units_precip: 'in', units_distance: 'mi',
  });
  const json = await httpGetJson(`https://swd.weatherflow.com/swd/rest/observations/station/${station.id}?${params}`);
  return { id: station.id, name: station.name, obs: json?.obs?.[0] ?? null, fetched: Date.now(),
           error: json ? null : 'fetch/parse error' };
}

// Raw device obs for the last ~65 min (covers the 30-min ring window + the
// 1-hr strike count). Distance comes through in km regardless of units.
async function fetchDevice(deviceId) {
  if (!deviceId) return [];
  const now = Math.floor(Date.now() / 1000);
  const params = new URLSearchParams({ token: TOKEN, time_start: String(now - 3900), time_end: String(now) });
  const json = await httpGetJson(`https://swd.weatherflow.com/swd/rest/observations/device/${deviceId}?${params}`);
  return Array.isArray(json?.obs) ? json.obs : [];
}

async function pollAll() {
  await Promise.allSettled(STATIONS.map(async (station) => {
    const [stRes, devObs] = await Promise.all([fetchStation(station), fetchDevice(station.deviceId)]);
    stationData[station.id] = stRes;
    appendHistory(station.id, stRes.obs?.air_temperature ?? null);
    lightningByStation[station.id] = computeLightning(devObs);
  }));
  saveHistory();
  broadcast();
  console.log(`[${new Date().toISOString()}] Poll complete — ${Object.keys(stationData).length} stations`);
}

// ── WebSocket ──────────────────────────────────────────────────────────────

// Cluster-wide lightning: FSQ / ESP / ZP are within a block of each other, and
// Tempest's single-sensor per-strike distance is noisy — one unit can miss a
// close strike its neighbor logged. For lightning-hold decisions we take the
// most-conservative (closest / most-recent) reading across all stations and
// apply it to every card, so any station detecting a close strike lights up
// the whole cluster. Temp / wind / rain stay per-station; only lightning shares.
function clusterLightning() {
  const all = Object.values(lightningByStation);
  const within = {};
  LIGHTNING_THRESHOLDS_MI.forEach(r => {
    within[r] = Math.max(0, ...all.map(L => (L.within && L.within[r]) || 0));
  });
  const closest = all.map(L => L.closestMi).filter(v => v != null);
  const lastEp  = Math.max(0, ...all.map(L => L.lastEpoch || 0));
  return {
    within,
    closestMi: closest.length ? Math.min(...closest) : null,
    lastEpoch: lastEp || null,
    count1hr:  Math.max(0, ...all.map(L => L.count1hr || 0)),
  };
}

function buildPayload() {
  const C = clusterLightning();
  return JSON.stringify(
    Object.values(stationData).map(s => {
      return {
        ...s,
        history: history[String(s.id)] || [],
        lightningWithin: C.within,
        lightningClosestMi: C.closestMi,
        lightningLastEpoch: C.lastEpoch,
        lightningCount: C.count1hr,
      };
    })
  );
}

function broadcast() {
  const payload = buildPayload();
  wss.clients.forEach((client) => {
    if (client.readyState === 1) client.send(payload);
  });
}

wss.on('connection', (ws) => {
  ws.send(buildPayload());
});

app.use(express.static('public'));

loadHistory();
pollAll();
setInterval(pollAll, POLL_INTERVAL);

server.listen(PORT, () => {
  console.log(`Tempest dashboard running on http://localhost:${PORT}`);
  console.log(`Poll interval: ${POLL_INTERVAL / 1000}s`);
});
