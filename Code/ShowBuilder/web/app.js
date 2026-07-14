"use strict";
let BOOT = {venues: [], instruments: [], mics: [], genres: []};
let MIC_BY_NAME = {};
let INST_BY_KEY = {};
let lastVenue = null;        // for reverting an accidental venue switch
let tableTouched = false;    // channel table has user-entered data
const DRAFT_KEY = "sb_draft_v1";
const DEFAULT_CH_COUNT = 32; // every show starts at 32 channels (crowd rig not included)

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const busy = (on, msg) => { $("#busy").classList.toggle("on", on); if (msg) $("#busyMsg").textContent = msg; };

function showStep(n) {
  $$(".step").forEach(s => s.classList.remove("on"));
  $("#step" + n).classList.add("on");
  $$(".steps span").forEach(s => {
    const k = +s.dataset.step;
    s.classList.toggle("on", k === n);
    s.classList.toggle("done", k < n);
  });
  window.scrollTo(0, 0);
}

async function boot() {
  const r = await fetch("/api/bootstrap");
  BOOT = await r.json();
  MIC_BY_NAME = {};
  BOOT.mics.forEach(m => MIC_BY_NAME[m.name.toLowerCase()] = m);
  INST_BY_KEY = {};
  BOOT.instruments.forEach(i => INST_BY_KEY[i.key] = i);

  $("#roleTag").textContent = BOOT.config.write_enabled ? "Mac · writes to show folder" : "package · downloads the brief";
  $("#export").textContent = BOOT.config.write_enabled ? "Export brief ✓" : "Download brief ↓";
  $("#venue").innerHTML = BOOT.venues.map(v =>
    `<option value="${v.key}">${v.name}</option>`).join("");
  $("#instList").innerHTML = BOOT.instruments.map(i => `<option value="${i.label}">${i.section}</option>`).join("");
  $("#micList").innerHTML = BOOT.mics.map(m => `<option value="${m.name}">${m.type}${m.ribbon ? " · NO 48V" : ""}</option>`).join("");
  $("#genreList").innerHTML = BOOT.genres.map(g => `<option value="${esc(g.key)}">`).join("");
  $("#foh").value = "Brian Lloyd";
  $("#showDate").value = new Date().toISOString().slice(0, 10);
  lastVenue = $("#venue").value;
  venueHint();
  applyVenueDefaults();
  maybeOfferDraft();
  if (!BOOT.config.write_enabled) refreshInbox();
}

function applyVenueDefaults() {
  const d = (BOOT.defaults || {})[$("#venue").value];
  if (d && d.channels && d.channels.length) {
    $("#chCount").value = d.count || d.channels.length;
    const body = $("#chBody");
    body.innerHTML = "";
    d.channels.forEach(c => body.insertAdjacentHTML("beforeend",
      rowHTML(0, {ch: c.ch, name: c.name, instrument: c.instrument})));
    wireRows();
  } else {
    $("#chCount").value = DEFAULT_CH_COUNT;
    genRows();
  }
  tableTouched = false;
}

function venueObj() { return BOOT.venues.find(v => v.key === $("#venue").value) || {}; }
function venueHint() {
  const v = venueObj();
  $("#venueHint").textContent =
    `${v.name} · ${v.console_label || ""} — the brief is the input to the deep build; it carries facts only, no EQ.`;
  $("#crowdHint").textContent = v.key === "memo"
    ? "Memo crowd rig (OM1 / Deity S2 / CM4) is added automatically with blank CH."
    : "";
}

// ---- channel rows ----------------------------------------------------------
function rowHTML(i, data = {}) {
  return `<tr>
    <td class="mv" data-label=""><button data-mv="up">▲</button><button data-mv="down">▼</button></td>
    <td class="ch" data-label="Ch"><input value="${esc(data.ch ?? "")}" placeholder="#"></td>
    <td data-label="Console name"><input class="cname" value="${esc(data.name ?? "")}" placeholder="e.g. Kick"></td>
    <td data-label="Instrument"><input class="cinst" list="instList" value="${esc(data.instrument ?? "")}" placeholder="instrument"></td>
    <td data-label="Mic / DI"><input class="cmic" list="micList" value="${esc(data.mic ?? "")}" placeholder="mic / DI"></td>
    <td class="p48" data-label="48V" title="48V"></td>
    <td data-label="Patch"><input class="cpatch" value="${esc(data.patch ?? "")}" placeholder="Local ${data.ch ?? "n"}" style="width:6.5rem"></td>
    <td data-label="Stand"><input class="cstand" value="${esc(data.stand ?? "")}" placeholder="—" style="width:5rem"></td>
    <td data-label="Notes"><input class="cnotes" value="${esc(data.notes ?? "")}" placeholder=""></td>
    <td class="rowdel" data-label=""><button class="del" title="remove">✕</button></td>
  </tr>`;
}

function genRows() {
  const n = Math.max(1, Math.min(64, +$("#chCount").value || DEFAULT_CH_COUNT));
  const body = $("#chBody");
  body.innerHTML = "";
  for (let i = 1; i <= n; i++) body.insertAdjacentHTML("beforeend", rowHTML(i, {ch: i}));
  wireRows();
}
function addRow() {
  $("#chBody").insertAdjacentHTML("beforeend", rowHTML(0, {ch: $("#chBody").children.length + 1}));
  wireRows();
}
function wireRows() {
  $$("#chBody tr").forEach(tr => {
    tr.querySelector(".del").onclick = () => { tr.remove(); tableTouched = true; saveDraft(); };
    tr.querySelectorAll("[data-mv]").forEach(b => b.onclick = () => { moveRow(tr, b.dataset.mv); saveDraft(); });
    const inst = tr.querySelector(".cinst"), mic = tr.querySelector(".cmic"),
          name = tr.querySelector(".cname");
    inst.onchange = () => {
      const m = matchInst(inst.value);
      if (m) {
        if (!name.value) name.value = m.label;
        if (!mic.value && m.default_mic) mic.value = m.default_mic;
      }
      refresh48(tr);
    };
    mic.onchange = () => refresh48(tr);
    name.onchange = () => refresh48(tr);
    refresh48(tr);
  });
}
function matchInst(text) {
  if (!text) return null;
  const t = text.toLowerCase().trim();
  return BOOT.instruments.find(i => i.label.toLowerCase() === t)
      || BOOT.instruments.find(i => i.key === t)
      || BOOT.instruments.find(i => t.includes(i.label.toLowerCase())) || null;
}
function refresh48(tr) {
  const mic = MIC_BY_NAME[(tr.querySelector(".cmic").value || "").toLowerCase().trim()];
  const cell = tr.querySelector(".p48");
  cell.innerHTML = !mic ? ""
    : mic.ribbon ? `<span class="tag-ribbon">NO 48V</span>`
    : (mic.phantom ? `<span class="led48" title="48V on"></span>` : "");
  // section stripe follows the derived section (locked input-list palette)
  const m = matchInst(tr.querySelector(".cinst").value) || matchInst(tr.querySelector(".cname").value);
  if (m) tr.dataset.section = m.section; else delete tr.dataset.section;
}
function moveRow(tr, dir) {
  if (dir === "up" && tr.previousElementSibling) tr.parentNode.insertBefore(tr, tr.previousElementSibling);
  if (dir === "down" && tr.nextElementSibling) tr.parentNode.insertBefore(tr.nextElementSibling, tr);
}

// ---- collect payload -------------------------------------------------------
function collectPayload() {
  const channels = $$("#chBody tr").map(tr => {
    const mic = tr.querySelector(".cmic").value.trim();
    const m = MIC_BY_NAME[mic.toLowerCase()];
    return {
      ch: tr.querySelector(".ch input").value.trim(),
      name: tr.querySelector(".cname").value.trim(),
      instrument: tr.querySelector(".cinst").value.trim(),
      mic,
      phantom: m ? (m.phantom && !m.ribbon) : false,
      ribbon: m ? !!m.ribbon : false,
      patch: tr.querySelector(".cpatch").value.trim(),
      stand: tr.querySelector(".cstand").value.trim(),
      notes: tr.querySelector(".cnotes").value,    // verbatim — no trim
    };
  }).filter(c => c.name || c.instrument);
  const v = venueObj();
  return {
    venue: $("#venue").value,
    venue_label: v.name || "",
    console_label: v.console_label || "",
    show_name: $("#showName").value.trim(), artist: $("#artist").value.trim(),
    genre: $("#genre").value.trim(),
    show_date: $("#showDate").value, show_time: $("#showTime").value.trim(),
    foh_engineer: $("#foh").value.trim(), mon_engineer: $("#mon").value.trim(),
    rev: $("#rev").value.trim(),
    show_notes: $("#showNotes").value,             // verbatim — no trim
    channels,
  };
}

// ---- draft autosave --------------------------------------------------------
let draftTimer = null;
function saveDraft() {
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ts: Date.now(), payload: collectPayload()}));
    } catch (e) { /* storage full/blocked — autosave is best-effort */ }
  }, 400);
}
function clearDraft() { clearTimeout(draftTimer); try { localStorage.removeItem(DRAFT_KEY); } catch (e) {} }
function draftMeaningful(p) {
  return !!(p && (p.show_name || p.artist || p.show_notes ||
    (p.channels || []).some(c => c.mic || c.notes || c.patch)));
}
function maybeOfferDraft() {
  let d = null;
  try { d = JSON.parse(localStorage.getItem(DRAFT_KEY)); } catch (e) {}
  if (!d || !draftMeaningful(d.payload)) return;
  const when = new Date(d.ts).toLocaleString();
  $("#draftBanner").innerHTML =
    `<div class="banner warn">Unsaved draft from ${esc(when)}` +
    (d.payload.show_name ? ` — <b>${esc(d.payload.show_name)}</b>` : "") +
    ` <button id="draftRestore">Restore</button> <button id="draftDiscard">Discard</button></div>`;
  $("#draftRestore").onclick = () => { restorePayload(d.payload); $("#draftBanner").innerHTML = ""; };
  $("#draftDiscard").onclick = () => { clearDraft(); $("#draftBanner").innerHTML = ""; };
}

// ---- restore / import ------------------------------------------------------
function restorePayload(p) {
  if (p.venue && BOOT.venues.some(v => v.key === p.venue)) {
    $("#venue").value = p.venue;
    lastVenue = p.venue;
    venueHint();
  }
  $("#showName").value = p.show_name || "";
  $("#artist").value = p.artist || "";
  $("#genre").value = p.genre || "";
  if (p.show_date) $("#showDate").value = p.show_date;
  $("#showTime").value = p.show_time === "TBD" ? "" : (p.show_time || "");
  $("#foh").value = p.foh_engineer || "Brian Lloyd";
  $("#mon").value = p.mon_engineer === "TBD" ? "" : (p.mon_engineer || "");
  $("#rev").value = p.rev || "Rev 1.0";
  $("#showNotes").value = p.show_notes || "";
  const body = $("#chBody");
  body.innerHTML = "";
  const chans = (p.channels || []).filter(c => !c.is_crowd);
  chans.forEach(c => body.insertAdjacentHTML("beforeend", rowHTML(0, c)));
  // pad back up to the 32-channel baseline with blank numbered rows
  let nextCh = Math.max(0, ...chans.map(c => +c.ch || 0)) + 1;
  while (body.children.length < DEFAULT_CH_COUNT && nextCh <= 64)
    body.insertAdjacentHTML("beforeend", rowHTML(0, {ch: nextCh++}));
  if (!body.children.length) { genRows(); }
  else { $("#chCount").value = body.children.length; wireRows(); }
  tableTouched = true;
  saveDraft();
}

function importBriefFile(file) {
  const rd = new FileReader();
  rd.onload = () => {
    let b;
    try { b = JSON.parse(rd.result); } catch (e) { $("#step1err").textContent = "Not valid JSON."; return; }
    if (!b || !Array.isArray(b.channels)) { $("#step1err").textContent = "Not a ShowBuilder brief (no channels)."; return; }
    // drop auto-injected crowd rows and implicit "Local <ch>" patches so they
    // stay implicit on re-export
    b.channels = b.channels.filter(c => !c.is_crowd).map(c => ({
      ...c, patch: (c.patch === `Local ${c.ch}` ? "" : c.patch)
    }));
    restorePayload(b);
    $("#step1err").textContent = "";
    $("#draftBanner").innerHTML =
      `<div class="banner ok">Imported <b>${esc(b.show_name || file.name)}</b> — ${b.channels.length} channel(s). Bump the Rev if this is a revision.</div>`;
  };
  rd.readAsText(file);
}

// ---- review (client-side, no server round trip) ----------------------------
function toReview() {
  const p = collectPayload();
  if (!p.show_name) { $("#step2err").textContent = "Set a show name (step 1)."; return; }
  if (!p.channels.length) { $("#step2err").textContent = "Add at least one channel."; return; }
  $("#step2err").textContent = "";
  renderReview(p);
  showStep(3);
}

function renderReview(p) {
  const v = venueObj();
  $("#reviewMeta").innerHTML =
    `<b>${esc(p.show_name)}</b> — ${esc(v.name || p.venue)} · ${esc(v.console_label || "")}<br>
     ${esc(p.artist || "—")}${p.genre ? " · " + esc(p.genre) : ""} · ${esc(p.show_date)} · ${esc(p.show_time)}<br>
     FOH ${esc(p.foh_engineer)} · MON ${esc(p.mon_engineer || "TBD")} · ${esc(p.rev)}`;
  const warn = [];
  const nums = p.channels.map(c => c.ch).filter(x => x !== "");
  const dups = [...new Set(nums.filter((x, i) => nums.indexOf(x) !== i))];
  if (dups.length) warn.push(`Duplicate channel number(s): ${dups.join(", ")} — fix before export.`);
  const unnumbered = p.channels.filter(c => !c.ch).length;
  if (unnumbered) warn.push(`${unnumbered} channel(s) have no CH number.`);
  if (p.venue === "memo") warn.push("Memo crowd rig (OM1 / Deity / CM4) will be appended as facts-only channels.");
  if (p.channels.some(c => c.ribbon)) warn.push("Ribbon mic(s) present — flagged NO 48V in the brief.");
  $("#reviewWarn").innerHTML = warn.map(t => `<div class="banner warn">${esc(t)}</div>`).join("");

  $("#revBody").innerHTML = p.channels.map(c => {
    const sec = sectionFor(c);
    return `<tr data-section="${esc(sec)}">
      <td data-label="Ch">${esc(c.ch || "")}</td>
      <td data-label="Name">${esc(c.name || "")}</td>
      <td data-label="Instrument">${esc(c.instrument || "—")}</td>
      <td data-label="Mic">${esc(c.mic || "—")}${c.ribbon ? ' <span class="tag-ribbon">NO 48V</span>' : ""}</td>
      <td data-label="48V">${c.ribbon ? '<span class="tag-ribbon">NO 48V</span>' : (c.phantom ? '<span class="led48" title="48V on"></span>' : "")}</td>
      <td data-label="Patch">${esc(c.patch || (c.ch ? `Local ${c.ch}` : ""))}</td>
      <td data-label="Section"><span class="secchip">${esc(sec)}</span></td>
      <td data-label="Stand">${esc(c.stand || "—")}</td>
      <td class="notes" data-label="Notes">${esc(c.notes || "")}</td></tr>`;
  }).join("");
}
function sectionFor(c) {
  const m = matchInst(c.instrument) || matchInst(c.name);
  return m ? m.section : "SPARE";
}

// ---- export ----------------------------------------------------------------
async function exportBrief(overwrite = false) {
  $("#step3err").textContent = "";
  const payload = collectPayload();
  if (overwrite) payload.overwrite = true;
  busy(true, "Writing brief…");
  const blobMode = !BOOT.config.write_enabled;
  try {
    const r = await fetch("/api/brief", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    if (blobMode) {
      if (!r.ok) {
        let msg = `Export failed (HTTP ${r.status}).`;
        if (r.status === 401) msg = "Session expired — reload the page and re-enter the passcode.";
        else { try { msg = (await r.json()).error || msg; } catch (e) {} }
        $("#step3err").textContent = msg;
        return;
      }
      const cd = r.headers.get("Content-Disposition") || "";
      const fn = (cd.match(/filename="(.+?)"/) || [])[1] || "show.brief.json";
      const blob = await r.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = fn; a.click();
      clearDraft();
      $("#exportOut").innerHTML = `<div class="banner ok">Brief downloaded: <code>${esc(fn)}</code> — a copy is saved on this server (list below).</div>
        <p class="hint">Drop it into the show folder, then run the deep build in Cowork.</p>`;
      refreshInbox();
      return;
    }
    const res = await r.json().catch(() => null);
    if (r.status === 409 && res && res.exists) {
      busy(false);
      if (confirm(`${res.message}\n\nOverwrite it?`)) return exportBrief(true);
      return;
    }
    if (!r.ok || !res || res.error) {
      $("#step3err").textContent = (res && res.error) || `Export failed (HTTP ${r.status}).`;
      return;
    }
    clearDraft();
    renderExport(res);
  } catch (e) {
    $("#step3err").textContent = "Export failed: " + (e.message || e);
  } finally { busy(false); }
}

function renderExport(r) {
  const json = JSON.stringify(r.brief, null, 2);
  $("#exportOut").innerHTML =
    `<div class="banner ok">✓ Brief written — ${r.channel_count} channel(s)${r.crowd_count ? ` + ${r.crowd_count} crowd` : ""}, facts only.</div>
     <p class="hint">File: <code>${esc(r.path)}</code></p>
     <p class="hint">${esc(r.next || "")}</p>
     <details><summary>${esc(r.filename)} — contents</summary><pre id="briefJson">${esc(json)}</pre></details>
     <div class="actions"><button id="copyJson">Copy JSON</button><button id="restart">New show</button></div>`;
  $("#copyJson").onclick = () => navigator.clipboard.writeText(json);
  $("#restart").onclick = () => { clearDraft(); location.reload(); };
}

// ---- inbox (package role: recent briefs saved on the server) ---------------
async function refreshInbox() {
  const el = $("#inboxList");
  if (!el) return;
  try {
    const r = await fetch("/api/briefs");
    if (!r.ok) return;
    const d = await r.json();
    if (!d.briefs || !d.briefs.length) { el.innerHTML = ""; return; }
    el.innerHTML = `<h3>Recent briefs on this server</h3><ul class="files">` +
      d.briefs.map(b =>
        `<li><a href="/api/briefs/${encodeURIComponent(b.name)}">${esc(b.name)}</a>` +
        `<span class="sz">${esc(b.mtime)} · ${(b.size / 1024).toFixed(1)} KB</span></li>`).join("") +
      `</ul>`;
  } catch (e) { /* list is a convenience — never block the wizard */ }
}

function esc(s) { return (s == null ? "" : String(s)).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c])); }

// ---- wire up ---------------------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
  boot();
  $("#venue").onchange = () => {
    if (tableTouched && !confirm("Switching venues replaces the channel table. Your typed channels will be lost. Continue?")) {
      $("#venue").value = lastVenue;
      return;
    }
    lastVenue = $("#venue").value;
    venueHint();
    applyVenueDefaults();
    saveDraft();
  };
  $$(".steps span").forEach(s => {
    s.style.cursor = "pointer";
    s.onclick = () => {
      const k = +s.dataset.step;
      if (k === 1 || k === 2) showStep(k);
      else if (k === 3) toReview();
    };
  });
  $("#toStep2").onclick = () => {
    if (!$("#showName").value.trim()) { $("#showName").focus(); return; }
    showStep(2);
  };
  $("#genRows").onclick = () => {
    if (tableTouched && !confirm("Regenerating rows replaces the channel table. Continue?")) return;
    genRows();
    tableTouched = false;
    saveDraft();
  };
  $("#addRow").onclick = addRow;
  $("#backTo1").onclick = () => showStep(1);
  $("#toReview").onclick = toReview;
  $("#backTo2").onclick = () => showStep(2);
  $("#export").onclick = () => exportBrief(false);
  $("#importBrief").onclick = () => $("#importFile").click();
  $("#importFile").onchange = () => {
    if ($("#importFile").files.length) importBriefFile($("#importFile").files[0]);
    $("#importFile").value = "";
  };
  // autosave everything typed anywhere in the wizard; track table edits
  $("main").addEventListener("input", e => {
    if (e.target.closest("#chBody")) tableTouched = true;
    saveDraft();
  });
});
