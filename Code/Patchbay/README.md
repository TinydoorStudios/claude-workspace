# Patchbay

A patch sheet tool for the desks I actually use — **DiGiCo Quantum 225, Midas M32,
Behringer Wing**. Same idea as Patchy, but self-hosted, offline, and it knows my
venues, my mic library and my paperwork format.

## Launch

**Patchbay** lives in `/Applications` — Spotlight it, Launchpad it, or keep it in the
Dock. It starts the server, shows the sheets in a Cocoa window, and shuts the server
down when you quit. If a server is already running (`./run.sh` in a terminal) it
attaches to that one instead of starting a second.

Rebuild after changing `mac/main.swift` — the build script reinstalls to
`/Applications` for you:

```bash
cd ~/Documents/Claude/Code/Patchbay/mac
./build_app.sh
```

The source bundle stays at `mac/Patchbay.app`; `/Applications/Patchbay.app` is the
copy you launch.

First launch may need right-click → Open (ad-hoc signed, no Developer ID). The repo
path and port are constants at the top of `main.swift` — update them if Patchbay
ever moves.

Terminal + browser still works if you prefer it:

```bash
cd ~/Documents/Claude/Code/Patchbay
./run.sh                 # http://localhost:8096
```

No install step: `run.sh` uses ShowBuilder's venv (aiohttp + openpyxl) if Patchbay
doesn't have its own. The app pins the server to `127.0.0.1` — it never listens on
the network.

The UI is **dark by default**; the ☀︎ button in the top bar flips to light and the
choice sticks. Printed sheets stay light regardless — they're paper.

## What it does

**New Patch Sheet wizard** — "+ New" opens a full-screen four-step build: **Location**
(project, client, site/room, address) → **Console** (manufacturer/model/FW, networking,
channel counts, console local I/O) → **I/O Devices** (name, in/out counts, IP — these
land as stage boxes) → **Confirm**. Picking a venue on step 1 sets the desk on step 2,
and picking a desk fills the console fields from `knowledge/consoles.json`; every field
stays editable. Nothing is written until "Create Patch Sheet". The wizard's own styling
lives in `web/wizard.css` under a `.pw-*` token scope, separate from the app chrome.
What it captures prints: the stage PDF opens with a **Rig information** block (Location ·
Console, side by side) above the input list, and the xlsx gets a **Rig Info** tab with
location, console and I/O devices. Both print only the fields that are filled in.

**The shell** — a sheet opens into a sidebar: Overview, Patch Sheet, Location,
Contacts, then a group per console, then the signal chain (Stage I/O, Devices, Patch
Devices), then Power, Revisions and Export. Everything autosaves; the top bar and a
corner toast both say when it's saved.

**Overview** — consoles, I/O and network devices, stage positions and contacts at a
glance, plus any open conflicts across every console on the sheet.

**Patch Sheet** — the read-only document view: collapsible sections per console plus
devices, stage I/O and contacts. Expand All / Collapse All, Export PDF, Copy JSON.

**Console Inputs** — the channel grid: CH, name, 48V, TOUR, mic/DI, port, and any
optional columns you switch on from the Fields picker (instrument, stand, section,
device, split, alt input, insert A/B, direct out, M/S, L/R link, notes). Type a mic
name and it pulls phantom/ribbon from the mic library; a ribbon locks 48V off and
prints **NO 48V** in red. Drag the ⠿ handle to reorder. "Auto-patch free ports" fills
unpatched rows in order.

**Easy Patch** — the crosspoint matrix: rows are channels, columns are I/O grouped by
source (the desk's own port groups — Local, AES, MADI, DMI on the Q225 — plus every
I/O device assigned to that console). Click a cell to patch, click again to clear,
shift-click to patch sequentially from there down. Double patches go red. Tabs switch
which field you're patching: I/O, Alt Input, Insert A, Insert B, Direct Out.

**Multiple consoles** — Add Console gives FOH and monitor world their own info,
channels, patch and outputs on one sheet. Devices get assigned to whichever consoles
they feed.

**Busses & Outputs** — bus, what it feeds, output port, device, location. "Seed
console buses" drops in the standard bus grouping (Drums / Rhythm / Piano / Strings /
Horns / Vocals / FOH Ambient) plus wedges and PA matrices.

**Devices** — I/O devices (racks, splits, expansion cards, Dante boxes) with counts,
protocol, IP, location and format, plus network devices (switches, APs). I/O devices
assigned to a console become patch columns in Easy Patch and drive the cross-patch page.

**Stage I/O** — stage positions with their runs mapped to a device and port, plus the
stage data connections (Cat6, fiber drops). Both print on the patch sheet.

**Patch Devices** — network routing between anything with a protocol set: pick a send
and a receive device, then click the crosspoints.

**Power** — distros, feeds, circuits, what's on each one, listed load per distro.

**Revisions** — autosave overwrites quietly; **Mark revision** snapshots the current
state and bumps the rev number. Restore any snapshot (the current state is
snapshotted first, so restoring is never destructive).

**Templates vs events** — a template is an installed rig you re-use. "New event from
this" clones it into a one-off show sheet that can drift without touching the rig.

**Locked templates** — the four house rigs (Memo, FSQ, WP, Wing) ship locked: fields
go read-only, mutating buttons switch off, and the server refuses the write with a
423 so nothing can drift them by accident. A locked sheet still exports, duplicates
and reads normally. Unlock from the banner or Export → Unlock, edit, lock again.
Clones are never locked.

## Template intake

The house templates carry defaults — venue, client, address, desk make/model/counts,
contacts — so a new show starts filled in. To fill in the rest (or fix anything):

```bash
cd ~/Documents/Claude/Code/Patchbay
../ShowBuilder/.venv/bin/python -m tools.make_template_intake     # writes the workbook
# fill in the amber cells, then:
../ShowBuilder/.venv/bin/python -m tools.import_intake "Patchbay Template Intake.xlsx" --dry-run
../ShowBuilder/.venv/bin/python -m tools.import_intake "Patchbay Template Intake.xlsx"
```

`Patchbay Template Intake.xlsx` has one tab per locked template, split into `## `
blocks — LOCATION, CONSOLES, CONNECTIONS, DEVICES, STAGE POSITIONS, DATA RUNS,
OUTPUTS, POWER, CONTACTS, CHANNELS — each pre-filled with what the template holds
today. The importer only touches blocks you actually filled in, snapshots a revision
first, and re-locks the template afterwards. `tools/seed_defaults.py` is what put the
known defaults in; it only writes empty fields, so it's safe to re-run.

## Exports

| Export | Notes |
|---|---|
| Stage PDF | 3 pages: rig information + input list (color-coded by section), patching by port, cross-patch by device + outputs + stage I/O + network devices + power + contacts + notes. Opens print-ready and fires the print dialog — Save as PDF, Letter landscape. Rendered server-side by weasyprint instead when it's installed. |
| Input List xlsx | The usual columns/widths/colors, plus Rig Info and Outputs & Power tabs. |
| Sheet JSON | The whole sheet, for backup or hand-off. Re-importable. |

Open conflicts (double patches, ribbon with 48V on, over channel count) print in a
warning block at the top of the PDF — the sheet never hides a problem from the stage.

## Imports

- **Import brief…** — a ShowBuilder `<Show>.brief.json` becomes an event sheet with
  channels, mics, phantom/ribbon and notes carried over verbatim.
- **Import sheet…** — a Patchbay JSON export.

## Console data

`knowledge/consoles.json` holds each desk's channel/bus/matrix counts and port
groups, taken from the manufacturers' published specs. Anything that depends on how
a desk is optioned (DMI cards, MADI mode, Wing expansion slot) is marked
`configurable` rather than asserted — check it against the actual rack.

| Desk | Channels | Buses | Local I/O |
|---|---|---|---|
| Quantum 225 | 72 | 36 aux/group, 12×12 matrix, LR/LCR | 8 in / 8 out, 2 AES I/O, 2 MADI, 2 DMI slots |
| M32 | 32 mic (+6 aux) | 16 mix, 6 matrix, LR/C | 32 XLR in / 16 out, 6 aux, AES50 A/B |
| Wing | 48 stereo | 16 bus, 8 matrix, 4 main (28 stereo) | 8 in / 8 out, AES/EBU, AES50 A/B/C, StageConnect, USB 48×48 |

Mic data is read live from `../ShowBuilder/knowledge/mics.json` when it's there, so
the two tools can't drift; `knowledge/mics.json` is the standalone fallback.

## Storage

```
data/sheets/<id>.json        current state
data/revisions/<id>/*.json   snapshots
data/trash/                  deleted sheets — nothing is hard-deleted
```

Sheets are **schema 2**: one sheet holds `consoles[]` (each with its own channels,
outputs, connections, counts and networking), plus sheet-level `devices[]`,
`positions[]`, `data_runs[]`, `contacts[]`, `location{}` and `power[]`. Older
single-console files migrate on read (`backend/schema.py`) — nothing to convert by
hand. Exports and the conflict analyzer see one console at a time through
`schema.flatten()`, which is why the paperwork format didn't change.

Seed the house rigs (Memo, FSQ, WP, Wing) with
`../ShowBuilder/.venv/bin/python -m backend.seed` — safe to re-run, it skips names
that already exist.

## The Mac app

| File | Role |
|---|---|
| `mac/main.swift` | the app — server lifecycle, WKWebView window, export routing |
| `mac/Info.plist` | bundle metadata (`com.tinydoor.patchbay`, loopback ATS) |
| `mac/make_icon.swift` / `make_icon.sh` | draws `AppIcon.icns` (a jack field with one patched pair) |
| `mac/build_app.sh` | one-shot build |

Inside the app, exports are handed to the system rather than the web view: the PDF
opens in your default browser (where Cmd-P → Save as PDF works), and xlsx/JSON
download to `~/Downloads` and get revealed in Finder. The app menu has **Open Sheets
Folder**, **Open in Browser** (⌘B) and **Open Server Log** (⌘L); View → Reload is ⌘R.

## Not this tool's job

EQ, dynamics, show research, `.ses` building. Patchbay documents the rig; the
`show-deep-build` skill still owns the show packet and the console file.
