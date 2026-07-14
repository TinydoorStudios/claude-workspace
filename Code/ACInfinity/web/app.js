"use strict";

let PC = new URLSearchParams(location.search).get("pc")
  || localStorage.getItem("aci_pc") || "";
if (new URLSearchParams(location.search).get("pc")) {
  localStorage.setItem("aci_pc", PC); // remember pc from a one-time link
}
const hdr = () => (PC ? { "X-Passcode": PC } : {});

function promptPasscode(msg) {
  let ov = document.getElementById("pcgate");
  if (!ov) {
    ov = document.createElement("div");
    ov.id = "pcgate";
    ov.className = "drawer";
    ov.innerHTML = `<div class="drawer-card" style="margin:auto;max-width:340px;height:auto">
      <h2 style="margin:0 0 4px">Passcode</h2>
      <p class="grp-detail" id="pcmsg"></p>
      <input id="pcin" type="password" autocomplete="off"
        style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:10px;margin:10px 0">
      <button class="save" id="pcgo">Enter</button></div>`;
    document.body.append(ov);
    const go = () => {
      PC = document.getElementById("pcin").value.trim();
      localStorage.setItem("aci_pc", PC);
      ov.remove();
      refresh();
    };
    ov.querySelector("#pcgo").onclick = go;
    ov.querySelector("#pcin").addEventListener("keydown", (e) => {
      if (e.key === "Enter") go();
    });
  }
  ov.querySelector("#pcmsg").textContent = msg || "Enter the dashboard passcode.";
  setTimeout(() => ov.querySelector("#pcin").focus(), 50);
}

const ICON = { 1: "💡", 2: "💧", 6: "🌀" }; // light, humidifier, fan
const $ = (s, r = document) => r.querySelector(s);
const el = (t, props = {}, kids = []) => {
  const n = Object.assign(document.createElement(t), props);
  for (const k of [].concat(kids)) if (k != null) n.append(k);
  return n;
};

let REFRESHING = false;

async function getState() {
  const r = await fetch("/api/state", { headers: hdr() });
  if (r.status === 401) { promptPasscode("Wrong or missing passcode."); throw new Error("locked"); }
  if (!r.ok) throw new Error((await r.json()).error || r.statusText);
  return r.json();
}

async function groupControl(devId, advId, overrides) {
  const r = await fetch("/api/groupcontrol", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...hdr() },
    body: JSON.stringify({ devId, advId, overrides }),
  });
  if (r.status === 401) { promptPasscode("Wrong or missing passcode."); throw new Error("locked"); }
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}

function toast(msg, isErr = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast" + (isErr ? " err" : "");
  setTimeout(() => t.classList.add("hidden"), 3400);
}

function renderDevice(d) {
  const card = el("div", { className: "dev" });
  card.append(el("div", { className: "dev-head" }, [
    el("h2", { textContent: d.name || "Controller" }),
    el("span", {
      className: "badge " + (d.online ? "on" : "off"),
      textContent: d.online ? "online" : "offline",
    }),
  ]));

  const r = d.reading || {};
  const cell = (label, val, unit) => el("div", {}, [
    el("b", { textContent: val == null ? "—" : val + unit }),
    document.createTextNode(label),
  ]);
  card.append(el("div", { className: "readout" }, [
    cell("Temp", r.tempF, "°F"),
    cell("Humidity", r.humidity, "%"),
    cell("VPD", r.vpd, " kPa"),
  ]));

  if (!d.online) {
    card.append(el("div", { className: "offline-note",
      textContent: "Controller offline — automation not reachable." }));
    return card;
  }

  if (!d.groups.length) {
    card.append(el("div", { className: "offline-note",
      textContent: "No Advance automation rules on this controller." }));
    return card;
  }

  const list = el("div", { className: "ports" });
  for (const g of d.groups) list.append(renderGroup(d, g));
  card.append(list);
  return card;
}

function renderGroup(d, g) {
  const wrap = el("div", { className: "port" });
  const enabled = !!g.isOn;
  wrap.append(el("div", { className: "port-top" }, [
    el("div", { className: "port-name" }, [
      el("span", { className: "ic", textContent: ICON[g.devType] || "⚙️" }),
      document.createTextNode(g.devTypeLabel),
      el("small", { textContent: `${g.modeLabel}` }),
    ]),
    el("label", { className: "switch" }, [
      Object.assign(document.createElement("input"), {
        type: "checkbox", checked: enabled,
        onchange: async (e) => {
          try {
            await groupControl(d.devId, g.advId, { isOn: e.target.checked ? 1 : 0 });
            toast(`${g.devTypeLabel}: ${e.target.checked ? "enabled" : "disabled"}`);
            scheduleRefresh();
          } catch (err) { toast(err.message, true); e.target.checked = enabled; }
        },
      }),
      el("span", { className: "slider" }),
    ]),
  ]));

  const dur = (m) => m % 60 ? `${Math.floor(m / 60)}h${m % 60}m` : `${m / 60}h`;
  const detail = [];
  if (g.mode === 3) detail.push(`on ${dur(g.cycleOnMin)} / off ${dur(g.cycleOffMin)}`);
  else if (g.triggers.length) detail.push(g.triggers.join("  ·  "));
  detail.push(`speed ${g.offSpeed}–${g.onSpeed}`);
  if (g.schedBegin) detail.push(`active ${g.schedBegin}–${g.schedEnd}`);
  wrap.append(el("div", { className: "grp-detail" }, [
    document.createTextNode(detail.join("   ")),
    el("button", { className: "linklike", textContent: "edit",
      onclick: () => openDrawer(d, g) }),
  ]));
  return wrap;
}

// ---- edit drawer -----------------------------------------------------------

function openDrawer(d, g) {
  const drawer = $("#drawer");
  $("#d-title").textContent = `${d.name} · ${g.devTypeLabel} (${g.modeLabel})`;
  const body = $("#d-body");
  body.innerHTML = "";

  const fields = {};
  const num = (key, label, val) => {
    const inp = el("input", { type: "number", value: val ?? 0 });
    fields[key] = inp;
    return el("div", { className: "field" }, [el("label", { textContent: label }), inp]);
  };
  const toggle = (key, label, val) => {
    const inp = el("input", { type: "checkbox", checked: !!val });
    fields[key] = inp;
    return el("div", { className: "field toggle" }, [inp, el("label", { textContent: label })]);
  };
  const hhmmToMin = (s) => { const [h, m] = s.split(":").map(Number); return h * 60 + m; };

  body.append(el("div", { className: "field row" }, [
    num("onSpeed", "On speed (0-10)", g.onSpeed),
    num("offSpeed", "Off speed (0-10)", g.offSpeed),
  ]));

  if (g.mode === 4) { // Auto
    body.append(el("div", { className: "hr" }));
    body.append(el("p", { className: "grp-detail", textContent: "Temperature triggers (°F)" }));
    body.append(el("div", { className: "field row" }, [
      num("autoHighTempF", "High temp", g.raw.autoHighTempF),
      toggle("autoHighTempSwitch", "on", g.raw.autoHighTempSwitch),
    ]));
    body.append(el("div", { className: "field row" }, [
      num("autoLowTempF", "Low temp", g.raw.autoLowTempF),
      toggle("autoLowTempSwitch", "on", g.raw.autoLowTempSwitch),
    ]));
    body.append(el("p", { className: "grp-detail", textContent: "Humidity triggers (%)" }));
    body.append(el("div", { className: "field row" }, [
      num("autoHighHumi", "High RH", g.raw.autoHighHumi),
      toggle("autoHighHumiSwitch", "on", g.raw.autoHighHumiSwitch),
    ]));
    body.append(el("div", { className: "field row" }, [
      num("autoLowHumi", "Low RH", g.raw.autoLowHumi),
      toggle("autoLowHumiSwitch", "on", g.raw.autoLowHumiSwitch),
    ]));
  }

  if (g.mode === 3) { // Cycle
    body.append(el("div", { className: "hr" }));
    body.append(el("p", { className: "grp-detail", textContent: "Cycle (minutes)" }));
    body.append(el("div", { className: "field row" }, [
      num("cycleOnMin", "On for", g.cycleOnMin),
      num("cycleOffMin", "Off for", g.cycleOffMin),
    ]));
  }

  body.append(el("div", { className: "hr" }));
  body.append(el("p", { className: "grp-detail", textContent: "Active window (HH:MM, 24h)" }));
  const beg = el("input", { type: "time", value: g.schedBegin || "00:00" });
  const end = el("input", { type: "time", value: g.schedEnd || "00:00" });
  body.append(el("div", { className: "field row" }, [
    el("div", {}, [el("label", { textContent: "From" }), beg]),
    el("div", {}, [el("label", { textContent: "To" }), end]),
  ]));

  const save = el("button", { className: "save", textContent: "Apply to controller" });
  save.onclick = async () => {
    save.disabled = true;
    try {
      const ov = {};
      for (const [k, inp] of Object.entries(fields)) {
        ov[k] = inp.type === "checkbox" ? (inp.checked ? 1 : 0) : parseInt(inp.value, 10);
      }
      if ("cycleOnMin" in ov) { ov.cycleOn = ov.cycleOnMin * 60; delete ov.cycleOnMin; }
      if ("cycleOffMin" in ov) { ov.cycleOff = ov.cycleOffMin * 60; delete ov.cycleOffMin; }
      ov.beginTime = hhmmToMin(beg.value);
      ov.endTime = hhmmToMin(end.value);
      await groupControl(d.devId, g.advId, ov);
      toast("Settings applied");
      drawer.classList.add("hidden");
      scheduleRefresh();
    } catch (e) {
      toast(e.message, true);
    } finally {
      save.disabled = false;
    }
  };
  body.append(save);
  drawer.classList.remove("hidden");
}

// ---- refresh ---------------------------------------------------------------

async function refresh() {
  if (REFRESHING) return;
  REFRESHING = true;
  try {
    const { devices } = await getState();
    const main = $("#devices");
    main.innerHTML = "";
    if (!devices.length) main.append(el("p", { textContent: "No controllers on this account." }));
    for (const d of devices) main.append(renderDevice(d));
    $("#updated").textContent = "updated " + new Date().toLocaleTimeString();
  } catch (e) {
    if (e.message !== "locked") toast(e.message, true);
  } finally {
    REFRESHING = false;
  }
}

let refreshTimer = null;
function scheduleRefresh() {
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(refresh, 2500);
}

$("#refresh").onclick = refresh;
$("#d-close").onclick = () => $("#drawer").classList.add("hidden");
$("#drawer").onclick = (e) => { if (e.target.id === "drawer") $("#drawer").classList.add("hidden"); };

refresh();
setInterval(refresh, 30000);
