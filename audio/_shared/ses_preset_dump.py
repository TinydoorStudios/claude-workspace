#!/usr/bin/env python3
"""
Dump the channel-EQ preset library out of a DiGiCo Q225 .ses console save and
render it as a single searchable HTML page.

The preset library sits at the FRONT of a console save, before the scene data.
Each preset is a channel block followed by a trailer:

    FF FF FF FF 01 <u16 name_len> <name> <u16 group_len> <group>

Everything between the previous trailer and this one is that preset's channel
data, so the same tag/value records the patch engine reads for a fader read
here too — value-then-tag framing, bidx 0 = console Band 4 (HF) .. bidx 3 =
Band 1 (LF). See audio/_shared/q225_ses_engine.py for the tag map.

Presets with no EQ window (FX, graphic EQ, matrix, media) are skipped and
counted separately — they carry no parametric EQ.

Usage:
    python3 ses_preset_dump.py <file.ses> -o <out.html> [--json out.json]
"""

import argparse, json, os, re, struct, sys

TAG_EQ_GAIN, TAG_EQ_FREQ, TAG_EQ_Q, TAG_EQ_TYPE = 0x0403, 0x0406, 0x0407, 0x040B
TAG_DEQ_EN, TAG_DEQ_THR, TAG_DEQ_ATK, TAG_DEQ_REL = 0x040E, 0x0411, 0x0412, 0x0410
TAG_LPF = 0x0703
LPF_SCALE, HPF_SCALE = 1.25, 0.8
PRINTABLE = re.compile(rb'^[\x20-\x7e]+$')


def parse(buf):
    def records(lo, hi, tag, bidx):
        sig = struct.pack('<HH', tag, bidx)
        out, i = [], lo
        while True:
            j = buf.find(sig, i, hi)
            if j < 0:
                break
            out.append(j - 4)
            i = j + 1
        return out

    def fl(o):
        return struct.unpack_from('<f', buf, o)[0]

    # ── locate every preset trailer ───────────────────────────────────────────
    trailers, i = [], 0
    while True:
        j = buf.find(b'\xff\xff\xff\xff\x01', i)
        if j < 0:
            break
        i = j + 1
        p = j + 5
        nlen = struct.unpack_from('<H', buf, p)[0]
        if not 1 <= nlen <= 40:
            continue
        name = buf[p + 2:p + 2 + nlen]
        if not PRINTABLE.match(name):
            continue
        q = p + 2 + nlen
        glen = struct.unpack_from('<H', buf, q)[0]
        if not 1 <= glen <= 40:
            continue
        grp = buf[q + 2:q + 2 + glen]
        if not PRINTABLE.match(grp):
            continue
        trailers.append((j, name.decode('latin1'), grp.decode('latin1'), q + 2 + glen))

    presets, no_eq, prev_end = [], 0, 0
    for j, name, grp, end in trailers:
        lo, hi, prev_end = prev_end, j, end

        win = None
        for vo in records(lo, hi, TAG_EQ_FREQ, 0):
            if 20 <= fl(vo) <= 25000:
                win = (vo - 0x30, vo + 0x240)
                break
        if win is None:
            no_eq += 1
            continue
        w0, w1 = win

        bands = []
        for b in range(4):
            g = records(w0, w1, TAG_EQ_GAIN, b)
            f = records(w0, w1, TAG_EQ_FREQ, b)
            qq = records(w0, w1, TAG_EQ_Q, b)
            ty = records(w0, w1, TAG_EQ_TYPE, b)
            if not (g and f and qq and ty):
                bands.append(None)
                continue
            tv = fl(ty[0])
            en = records(w0, w1, TAG_DEQ_EN, b)
            dyn = bool(en and fl(en[0]) >= 0.5)
            deq = None
            if dyn:
                thr = records(w0, w1, TAG_DEQ_THR, b)
                atk = records(w0, w1, TAG_DEQ_ATK, b)
                rel = records(w0, w1, TAG_DEQ_REL, b)
                deq = [round(fl(thr[0]), 1) if thr else None,
                       round(fl(atk[0]) * 1000, 1) if atk else None,
                       round(fl(rel[0]) * 1000, 1) if rel else None]
            bands.append([round(fl(g[0]), 2), round(fl(f[0]), 1), round(fl(qq[0]), 2),
                          # 1.0 = shelf, 2.0 = bell; DEQ bands carry an off-integer
                          # value in this slot, so anything >= 1.5 draws as a bell.
                          1 if tv < 1.5 else 2, deq])

        if not any(bands):
            # window anchored but no band records — layout/name presets, not EQ
            no_eq += 1
            continue

        hpf = lpf = None
        for vo in records(lo, hi, TAG_LPF, 1):
            v = fl(vo)
            if 20 <= v <= 25001:
                lpf = None if v >= 24999 else round(v / LPF_SCALE, 1)
                tagw, = struct.unpack_from('<H', buf, vo + 0x14)
                if tagw == 0xFFFF:
                    h = fl(vo + 0x10) / HPF_SCALE
                    hpf = round(h, 1) if 20 < h <= 2000 else None
                break

        presets.append({'g': grp, 'n': name, 'o': j, 'hpf': hpf, 'lpf': lpf, 'b': bands})

    return presets, no_eq, len(trailers)


# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{
  --header:#1A3A5C; --accent:#2E6DA4; --bg:#f4f6f9; --card:#fff; --ink:#111827;
  --muted:#6b7280; --line:#d5dce6; --cut:#b3261e; --boost:#1f7a3d; --grid:#e3e8ef;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#0f1419;--card:#161c24;--ink:#e6edf3;--muted:#8b97a6;--line:#2a3441;
        --grid:#232c37;--header:#111820;--accent:#5b9bd5;--cut:#ff7b6b;--boost:#5fd18a;}
}
:root[data-theme=light]{--bg:#f4f6f9;--card:#fff;--ink:#111827;--muted:#6b7280;
  --line:#d5dce6;--grid:#e3e8ef;--header:#1A3A5C;--accent:#2E6DA4;--cut:#b3261e;--boost:#1f7a3d;}
:root[data-theme=dark]{--bg:#0f1419;--card:#161c24;--ink:#e6edf3;--muted:#8b97a6;
  --line:#2a3441;--grid:#232c37;--header:#111820;--accent:#5b9bd5;--cut:#ff7b6b;--boost:#5fd18a;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Calibri,Arial,sans-serif}
header{position:sticky;top:0;z-index:10;background:var(--header);color:#fff;padding:14px 18px 12px}
header h1{margin:0 0 2px;font-size:17px;font-weight:700;letter-spacing:.2px;color:#fff}
header .sub{font-size:12px;opacity:.75}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
.controls input[type=search],.controls select{
  font:13px inherit;padding:7px 10px;border:1px solid rgba(255,255,255,.25);border-radius:6px;
  background:rgba(255,255,255,.10);color:#fff;min-width:0}
.controls input[type=search]{flex:1 1 240px}
.controls select{max-width:230px}
.controls option{color:#111}
.controls label{font-size:12px;opacity:.85;display:flex;gap:5px;align-items:center;cursor:pointer;white-space:nowrap}
#count{font-size:12px;opacity:.8;margin-left:auto;white-space:nowrap}
main{padding:16px;display:grid;gap:12px;
     grid-template-columns:repeat(auto-fill,minmax(300px,1fr));max-width:1800px;margin:0 auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 11px 8px;
      overflow:hidden}
.ttl{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px}
.nm{font-weight:700;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gp{font-size:10.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;
    color:#fff;background:var(--accent);padding:2px 7px;border-radius:20px;white-space:nowrap;flex:none}
svg{display:block;width:100%;height:auto}
table{width:100%;border-collapse:collapse;font:11.5px/1.3 Consolas,Menlo,monospace;margin-top:6px}
th{text-align:left;font-weight:600;color:var(--muted);font-size:10px;letter-spacing:.3px;
   text-transform:uppercase;padding:2px 4px;border-bottom:1px solid var(--line)}
td{padding:2px 4px;border-bottom:1px solid var(--grid);white-space:nowrap}
td:first-child{color:var(--muted)}
tr.off td{opacity:.4}
.cut{color:var(--cut);font-weight:700}.boost{color:var(--boost);font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.chip{font:10.5px/1 Consolas,Menlo,monospace;padding:3px 6px;border-radius:4px;
      background:var(--grid);color:var(--muted)}
.chip.on{background:var(--accent);color:#fff}
#more{grid-column:1/-1;text-align:center;color:var(--muted);padding:20px;font-size:13px}
#empty{grid-column:1/-1;text-align:center;color:var(--muted);padding:60px 20px}
footer{padding:10px 18px 30px;color:var(--muted);font-size:11.5px;max-width:1800px;margin:0 auto}
/* ── cull workflow ── */
.act{border:none;border-radius:5px;cursor:pointer;font:600 11px/1 inherit;padding:5px 8px;
     background:var(--grid);color:var(--muted);flex:none}
.act:hover{background:var(--cut);color:#fff}
.act:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.card.gone{opacity:.45;border-style:dashed;border-color:var(--cut)}
.card.gone .nm{text-decoration:line-through}
.card.gone .act{background:var(--boost);color:#fff}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px;
     padding-top:8px;border-top:1px solid rgba(255,255,255,.15)}
.bar button{border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.10);color:#fff;
            font:600 12px/1 inherit;padding:7px 11px;border-radius:6px;cursor:pointer}
.bar button:hover{background:rgba(255,255,255,.2)}
.bar button:focus-visible{outline:2px solid #fff;outline-offset:2px}
.bar .danger:hover{background:var(--cut);border-color:var(--cut)}
.bar .sep{flex:1}
.bar .grp2{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
#tally{font:12px/1 Consolas,Menlo,monospace;opacity:.85;white-space:nowrap}
#tally b{font-size:13px}
</style></head><body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__SUB__</div>
  <div class="controls">
    <input type="search" id="q" placeholder="Search preset or group name…" autocomplete="off">
    <select id="grp"></select>
    <select id="sort">
      <option value="file">Sort: file order</option>
      <option value="group">Sort: group, then name</option>
      <option value="name">Sort: name</option>
    </select>
    <select id="view">
      <option value="keep">Show: keeping</option>
      <option value="all">Show: everything</option>
      <option value="cut">Show: marked to cut</option>
    </select>
    <select id="flat">
      <option value="">Empty presets: show</option>
      <option value="hide">Empty presets: hide</option>
      <option value="only">Empty presets: only these</option>
    </select>
    <label><input type="checkbox" id="dyn"> DEQ only</label>
    <span id="count"></span>
  </div>
  <div class="bar">
    <button id="cutAll" class="danger" type="button">Cut everything shown</button>
    <button id="keepAll" type="button">Keep everything shown</button>
    <button id="undo" type="button">Undo last</button>
    <span class="sep"></span>
    <span class="grp2">
      <span id="tally"></span>
      <button id="expCsv" type="button">Export master list (.csv)</button>
      <button id="expTxt" type="button">Export cull list</button>
      <button id="expJson" type="button">Export marks (.json)</button>
      <button id="reset" class="danger" type="button">Clear all marks</button>
    </span>
  </div>
</header>
<main id="grid"></main>
<footer>__FOOT__</footer>
<script>
const DATA = __DATA__;
const FS = 48000, CHUNK = 90;

/* ---- biquad magnitude ---- */
function mag(c, w){
  const [b0,b1,b2,a0,a1,a2] = c;
  const cw = Math.cos(w), sw = Math.sin(w), c2 = Math.cos(2*w), s2 = Math.sin(2*w);
  const nr = b0 + b1*cw + b2*c2, ni = -(b1*sw + b2*s2);
  const dr = a0 + a1*cw + a2*c2, di = -(a1*sw + a2*s2);
  return Math.sqrt((nr*nr+ni*ni)/(dr*dr+di*di));
}
function peak(f,g,q){
  const A=Math.pow(10,g/40), w=2*Math.PI*f/FS, al=Math.sin(w)/(2*Math.max(q,.1)), cw=Math.cos(w);
  return [1+al*A,-2*cw,1-al*A,1+al/A,-2*cw,1-al/A];
}
function shelf(f,g,q,high){
  const A=Math.pow(10,g/40), w=2*Math.PI*f/FS, cw=Math.cos(w), sw=Math.sin(w);
  const al=sw/2*Math.sqrt((A+1/A)*(1/Math.max(q,.1)-1)+2), tsa=2*Math.sqrt(A)*al;
  if(high) return [A*((A+1)+(A-1)*cw+tsa), -2*A*((A-1)+(A+1)*cw), A*((A+1)+(A-1)*cw-tsa),
                   (A+1)-(A-1)*cw+tsa, 2*((A-1)-(A+1)*cw), (A+1)-(A-1)*cw-tsa];
  return [A*((A+1)-(A-1)*cw+tsa), 2*A*((A-1)-(A+1)*cw), A*((A+1)-(A-1)*cw-tsa),
          (A+1)+(A-1)*cw+tsa, -2*((A-1)+(A+1)*cw), (A+1)+(A-1)*cw-tsa];
}
function pole(f,hp){   /* 12 dB/oct Butterworth — slope isn't stored in the file */
  const w=2*Math.PI*f/FS, cw=Math.cos(w), al=Math.sin(w)/(2*0.7071);
  if(hp) return [(1+cw)/2, -(1+cw), (1+cw)/2, 1+al, -2*cw, 1-al];
  return [(1-cw)/2, 1-cw, (1-cw)/2, 1+al, -2*cw, 1-al];
}

const W=300,H=118,PADL=22,PADR=4,TOP=6,BOT=14,FMIN=20,FMAX=20000,DBR=18;
const lo=Math.log10(FMIN), span=Math.log10(FMAX)-lo;
const xOf=f=>PADL+(Math.log10(f)-lo)/span*(W-PADL-PADR);
const yOf=d=>TOP+(DBR-d)/(2*DBR)*(H-TOP-BOT);

function curve(p){
  const cs=[];
  (p.b||[]).forEach((b,i)=>{
    if(!b) return;
    const [g,f,q,t]=b;
    if(!g || Math.abs(g)<0.05) return;
    cs.push(t===1 ? shelf(f,g,q,i<2) : peak(f,g,q));
  });
  if(p.hpf) cs.push(pole(p.hpf,true));
  if(p.lpf) cs.push(pole(p.lpf,false));
  let d='';
  for(let i=0;i<=140;i++){
    const f=Math.pow(10, lo+span*i/140), w=2*Math.PI*f/FS;
    let m=1; for(const c of cs) m*=mag(c,w);
    let db=20*Math.log10(Math.max(m,1e-6));
    db=Math.max(-DBR,Math.min(DBR,db));
    d+=(i?'L':'M')+xOf(f).toFixed(1)+' '+yOf(db).toFixed(1);
  }
  let g='';
  [100,1000,10000].forEach(f=>{g+=`<line x1="${xOf(f).toFixed(1)}" y1="${TOP}" x2="${xOf(f).toFixed(1)}" y2="${H-BOT}" stroke="var(--grid)"/>`});
  [12,-12].forEach(d2=>{g+=`<line x1="${PADL}" y1="${yOf(d2).toFixed(1)}" x2="${W-PADR}" y2="${yOf(d2).toFixed(1)}" stroke="var(--grid)"/>`});
  g+=`<line x1="${PADL}" y1="${yOf(0).toFixed(1)}" x2="${W-PADR}" y2="${yOf(0).toFixed(1)}" stroke="var(--line)"/>`;
  let lab='';
  [[100,'100'],[1000,'1k'],[10000,'10k']].forEach(([f,s])=>{
    lab+=`<text x="${xOf(f).toFixed(1)}" y="${H-3}" font-size="9" fill="var(--muted)" text-anchor="middle">${s}</text>`});
  lab+=`<text x="2" y="${(yOf(12)+3).toFixed(1)}" font-size="8" fill="var(--muted)">+12</text>`;
  lab+=`<text x="2" y="${(yOf(0)+3).toFixed(1)}" font-size="8" fill="var(--muted)">0</text>`;
  lab+=`<text x="2" y="${(yOf(-12)+3).toFixed(1)}" font-size="8" fill="var(--muted)">-12</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${g}${lab}<path d="${d}" fill="none" stroke="var(--accent)" stroke-width="2"/></svg>`;
}

const BN=['Band 4 (HF)','Band 3','Band 2','Band 1 (LF)'];
const hz=f=>f>=1000?(f/1000).toFixed(f>=10000?1:2).replace(/\.?0+$/,'')+'k':Math.round(f);
function card(p){
  let rows='';
  (p.b||[]).forEach((b,i)=>{
    if(!b){rows+=`<tr class="off"><td>${BN[i]}</td><td colspan="4">—</td></tr>`;return}
    const [g,f,q,t,deq]=b, flat=Math.abs(g)<0.05;
    const gs=g>0.05?`<span class="boost">+${g.toFixed(1)}</span>`:g<-0.05?`<span class="cut">${g.toFixed(1)}</span>`:'0.0';
    rows+=`<tr class="${flat?'off':''}"><td>${BN[i]}</td><td>${gs}</td><td>${hz(f)}</td>`+
          `<td>${q.toFixed(2)}</td><td>${t===1?'Shf':'Bell'}${deq?' <b>D</b>':''}</td></tr>`;
  });
  let chips=`<span class="chip ${p.hpf?'on':''}">HPF ${p.hpf?hz(p.hpf):'off'}</span>`+
            `<span class="chip ${p.lpf?'on':''}">LPF ${p.lpf?hz(p.lpf):'off'}</span>`;
  const dq=(p.b||[]).map((b,i)=>b&&b[4]?`B${4-i} ${b[4][0]}dB ${b[4][1]}/${b[4][2]}ms`:null).filter(Boolean);
  dq.forEach(s=>chips+=`<span class="chip on">DEQ ${s}</span>`);
  const el=document.createElement('div');
  el.className='card'+(CUT.has(p.o)?' gone':'');
  el.dataset.o=p.o;
  el.innerHTML=`<div class="ttl"><span class="nm" title="${esc(p.n)}">${esc(p.n)}</span>`+
    `<span class="gp" title="${esc(p.g)}">${esc(p.g)}</span>`+
    `<button class="act" type="button" title="${CUT.has(p.o)?'Keep this preset':'Mark this preset to cut'}">`+
    `${CUT.has(p.o)?'keep':'cut'}</button></div>${curve(p)}`+
    `<table><thead><tr><th>Band</th><th>Gain</th><th>Freq</th><th>Q</th><th>Type</th></tr></thead>`+
    `<tbody>${rows}</tbody></table><div class="chips">${chips}</div>`;
  el.querySelector('.act').addEventListener('click',()=>toggle(p,el));
  return el;
}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---- flags ---- */
DATA.forEach((p,i)=>{
  p.i=i;
  p.flat=!(p.hpf||p.lpf||(p.b||[]).some(b=>b&&Math.abs(b[0])>=0.05));
  p.dyn=(p.b||[]).some(b=>b&&b[4]);
  p.s=(p.n+' '+p.g).toLowerCase();
});

const grid=document.getElementById('grid'), qEl=document.getElementById('q'),
      gEl=document.getElementById('grp'), sEl=document.getElementById('sort'),
      fEl=document.getElementById('flat'), dEl=document.getElementById('dyn'),
      vEl=document.getElementById('view'), cEl=document.getElementById('count'),
      tEl=document.getElementById('tally');

/* ---- cull marks: a set of file offsets, persisted in this browser ---- */
const KEY='ses-cull:'+document.title;
const CUT=new Set(load());
let UNDO=[];
/* First visit starts with every EMPTY preset already marked to cut — no bands
   moved, no HPF, no LPF, nothing to lose. Undo or "Clear all marks" reverses it.
   Marks already saved in this browser are never overwritten. */
function load(){
  let saved=null;
  try{ saved=localStorage.getItem(KEY) }catch(e){}
  if(saved!==null){ try{ return JSON.parse(saved) }catch(e){ return [] } }
  const seed=DATA.filter(p=>!(p.hpf||p.lpf||(p.b||[]).some(b=>b&&Math.abs(b[0])>=0.05)))
                 .map(p=>p.o);
  try{ localStorage.setItem(KEY, JSON.stringify(seed)) }catch(e){}
  return seed;
}
function save(){ try{ localStorage.setItem(KEY, JSON.stringify([...CUT])) }catch(e){} tally() }
function tally(){
  const cut=CUT.size, keep=DATA.length-cut;
  tEl.innerHTML=`keeping <b>${keep}</b> · cutting <b>${cut}</b>`;
}
function toggle(p,el){
  UNDO.push([p.o, CUT.has(p.o)]);
  if(UNDO.length>500) UNDO.shift();
  setCut(p.o, !CUT.has(p.o), el);
  save();
}
function setCut(o,on,el){
  on ? CUT.add(o) : CUT.delete(o);
  if(!el) el=grid.querySelector(`.card[data-o="${o}"]`);
  if(!el) return;
  const v=vEl.value;
  if((v==='keep'&&on)||(v==='cut'&&!on)){ el.remove(); return }
  el.classList.toggle('gone',on);
  const b=el.querySelector('.act');
  b.textContent=on?'keep':'cut';
  b.title=on?'Keep this preset':'Mark this preset to cut';
}
/* confirm() can be blocked in a sandboxed frame — treat that as a yes, Undo covers it */
const ask=m=>{ try{ return confirm(m) }catch(e){ return true } };
function bulk(on){
  const n=shown.filter(p=>CUT.has(p.o)!==on).length;
  if(!n) return;
  if(n>25 && !ask(`${on?'Cut':'Keep'} ${n} preset${n>1?'s':''}?`)) return;
  UNDO.push(shown.map(p=>[p.o,CUT.has(p.o)]));
  shown.forEach(p=>on?CUT.add(p.o):CUT.delete(p.o));
  save(); apply();
}
document.getElementById('cutAll').onclick=()=>bulk(true);
document.getElementById('keepAll').onclick=()=>bulk(false);
document.getElementById('undo').onclick=()=>{
  const u=UNDO.pop(); if(!u) return;
  (typeof u[0]==='number'?[u]:u).forEach(([o,was])=>was?CUT.add(o):CUT.delete(o));
  save(); apply();
};
document.getElementById('reset').onclick=()=>{
  if(!CUT.size||!ask(`Clear all ${CUT.size} marks?`)) return;
  UNDO.push(DATA.map(p=>[p.o,CUT.has(p.o)]));
  CUT.clear(); save(); apply();
};

/* ---- exports ---- */
function dl(name,text,type){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([text],{type:type||'text/plain'}));
  a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),4000);
}
document.getElementById('expJson').onclick=()=>{
  const cut=DATA.filter(p=>CUT.has(p.o)).map(p=>({off:p.o,group:p.g,name:p.n}));
  dl('preset-cull-marks.json', JSON.stringify(
    {source:document.title, generated:new Date().toISOString(),
     total:DATA.length, cut:cut.length, keep:DATA.length-cut.length, presets:cut}, null, 1),
    'application/json');
};
document.getElementById('expCsv').onclick=()=>{
  const cell=v=>{ const s=String(v==null?'':v);
    return /[",\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s };
  const head=['Status','Group','Preset','HPF Hz','LPF Hz'];
  ['Band 4 (HF)','Band 3','Band 2','Band 1 (LF)'].forEach(b=>
    head.push(b+' Gain dB', b+' Freq Hz', b+' Q', b+' Type', b+' Dyn'));
  head.push('DEQ Thr dB','DEQ Atk ms','DEQ Rel ms','File Offset');
  const rows=[head.map(cell).join(',')];
  DATA.forEach(p=>{
    const r=[CUT.has(p.o)?'cut':'keep', p.g, p.n, p.hpf||'', p.lpf||''];
    let dq=['','',''];
    (p.b||[]).forEach(b=>{
      if(!b){ r.push('','','','',''); return }
      r.push(b[0].toFixed(2), b[1], b[2].toFixed(2), b[3]===1?'Shelf':'Bell', b[4]?'yes':'');
      if(b[4]&&!dq[0]) dq=[b[4][0], b[4][1], b[4][2]];
    });
    r.push(dq[0],dq[1],dq[2],'0x'+p.o.toString(16));
    rows.push(r.map(cell).join(','));
  });
  dl('preset-master-list.csv', '﻿'+rows.join('\r\n'), 'text/csv');
};
document.getElementById('expTxt').onclick=()=>{
  const byG={};
  DATA.forEach(p=>{ (byG[p.g]=byG[p.g]||[]).push(p) });
  const whole=[], part=[], keep=[];
  Object.keys(byG).sort((a,b)=>a.localeCompare(b)).forEach(g=>{
    const all=byG[g], cut=all.filter(p=>CUT.has(p.o));
    if(!cut.length){ keep.push(`  ${g} (${all.length})`); return }
    if(cut.length===all.length) whole.push(`  ${g} (${all.length})`);
    else{
      part.push(`  ${g} — cut ${cut.length} of ${all.length}:`);
      cut.forEach(p=>part.push(`      ${p.n}`));
    }
  });
  const L=['PRESET CULL LIST — '+document.title,
    new Date().toString(),
    `${CUT.size} of ${DATA.length} presets marked to cut · ${DATA.length-CUT.size} kept`,
    '','Work these in the console Preset Manager. Whole groups first — that is one',
    'delete each instead of dozens.','',
    `DELETE ENTIRE GROUP  (${whole.length})`, whole.length?whole.join('\n'):'  (none)','',
    `DELETE INDIVIDUAL PRESETS  (${part.filter(l=>!l.endsWith(':')).length})`,
    part.length?part.join('\n'):'  (none)','',
    `GROUPS UNTOUCHED  (${keep.length})`, keep.length?keep.join('\n'):'  (none)',''];
  dl('preset-cull-list.txt', L.join('\n'));
};

const groups=[...new Set(DATA.map(p=>p.g))].sort((a,b)=>a.localeCompare(b));
gEl.innerHTML='<option value="">All groups ('+groups.length+')</option>'+
  groups.map(g=>`<option value="${esc(g)}">${esc(g)} (${DATA.filter(p=>p.g===g).length})</option>`).join('');

let shown=[], drawn=0, sentinel=null;
function apply(){
  const q=qEl.value.trim().toLowerCase(), g=gEl.value, hf=fEl.value, dy=dEl.checked,
        v=vEl.value;
  shown=DATA.filter(p=>(!g||p.g===g)&&(!dy||p.dyn)&&(!q||p.s.includes(q))
                    &&(hf==='hide'?!p.flat:hf==='only'?p.flat:true)
                    &&(v==='all'||(v==='cut')===CUT.has(p.o)));
  const s=sEl.value;
  if(s==='group') shown.sort((a,b)=>a.g.localeCompare(b.g)||a.n.localeCompare(b.n));
  else if(s==='name') shown.sort((a,b)=>a.n.localeCompare(b.n)||a.g.localeCompare(b.g));
  else shown.sort((a,b)=>a.i-b.i);
  cEl.textContent=shown.length+' of '+DATA.length;
  tally();
  grid.innerHTML=''; drawn=0;
  if(!shown.length){grid.innerHTML='<div id="empty">Nothing matches that filter.</div>';return}
  draw();
}
function draw(){
  const frag=document.createDocumentFragment();
  const end=Math.min(drawn+CHUNK, shown.length);
  for(;drawn<end;drawn++) frag.appendChild(card(shown[drawn]));
  if(sentinel) sentinel.remove();
  grid.appendChild(frag);
  if(drawn<shown.length){
    sentinel=document.createElement('div');
    sentinel.id='more'; sentinel.textContent='loading '+(shown.length-drawn)+' more…';
    grid.appendChild(sentinel); io.observe(sentinel);
  } else sentinel=null;
}
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){io.unobserve(e.target);draw()}})},{rootMargin:'600px'});
[qEl,gEl,sEl,fEl,dEl,vEl].forEach(el=>el.addEventListener('input',apply));
apply();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ses')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--json')
    ap.add_argument('--title')
    ap.add_argument('--fragment', action='store_true',
                    help='emit body content only (for the Artifact publisher, '
                         'which supplies its own doctype/head/body skeleton)')
    a = ap.parse_args()

    buf = open(a.ses, 'rb').read()
    presets, no_eq, total = parse(buf)

    groups = sorted({p['g'] for p in presets})
    flat = sum(1 for p in presets
               if not (p['hpf'] or p['lpf'] or any(b and abs(b[0]) >= 0.05 for b in p['b'])))
    dyn = sum(1 for p in presets if any(b and b[4] for b in p['b']))

    title = a.title or f"EQ Presets — {os.path.basename(a.ses)}"
    sub = (f"{len(presets)} channel presets with parametric EQ across {len(groups)} groups · "
           f"{len(presets)-flat} with non-default EQ · {dyn} with dynamic EQ · "
           f"{no_eq} FX/graphic/matrix presets skipped (no parametric EQ)")
    foot = ("Opens with every empty preset — no band moved, no HPF, no LPF — already marked "
            "to cut; \"Clear all marks\" reverses that. "
            "Cut marks are a worklist, not an edit — this page never touches the .ses. "
            "Marks are saved in this browser, so the same browser picks up where you left off; "
            "a different device or a cleared cache starts empty. Export the cull list and work "
            "it in the console's Preset Manager, whole groups first. "
            "Read straight out of the .ses byte stream — tags 0x0403/0x0406/0x0407/0x040B, "
            "bidx 0 = console Band 4 (HF) … bidx 3 = Band 1 (LF); LPF 0x0703 bidx 1 "
            "(stored 1.25 × display Hz), HPF the float 0x10 past it (0.8 × display Hz). "
            "Curves are drawn at 48 kHz with RBJ biquads; HPF/LPF are drawn at 12 dB/oct "
            "because the file does not store the slope. \"D\" on a band = dynamic EQ armed. "
            "Bands are shown in console order: Band 4 (HF) → Band 1 (LF).")

    tpl = HTML
    if a.fragment:
        tpl = (tpl.replace('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
                           '<meta name="viewport" content="width=device-width,initial-scale=1">\n', '')
                  .replace('</head><body>', '')
                  .replace('</script></body></html>', '</script>'))

    html = (tpl.replace('__DATA__', json.dumps(presets, separators=(',', ':')))
               .replace('__TITLE__', title).replace('__SUB__', sub).replace('__FOOT__', foot))
    open(a.out, 'w').write(html)
    if a.json:
        json.dump(presets, open(a.json, 'w'), indent=1)

    print(f"{total} preset trailers · {len(presets)} with EQ · {no_eq} without · "
          f"{len(groups)} groups · {flat} flat · {dyn} dynamic")
    print(f"→ {a.out} ({os.path.getsize(a.out)/1024:.0f} KB)")


if __name__ == '__main__':
    main()
