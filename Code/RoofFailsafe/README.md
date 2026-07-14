# Roof Display Failsafe — DMP-8000 VDCP trigger

A dashboard/Companion button that forces the **D8Roof-P** roof display to the
**Carbonite → DeckLink** live feed **even when the Daktronics Show Control PC is
off or won't boot.**

## Why this exists

Today the "Switcher" button in Display Studio runs one command:

```
Play "DeckLink Duo (1).dpf" Continuously on D8Roof-P: Roof Display/Content
```

Display Studio is the *only* thing that tells the DMP to show that feed. If the
Show Control PC dies, that button is gone. But the **DMP-8000 player
(192.168.200.121)** and the **Carbonite** are separate boxes that stay alive.
The DMP accepts **VDCP** over a TCP/UDP socket — the same protocol an automation
controller/switcher uses — so we command it directly and skip the dead PC.

```
[TDS dashboard button] ─┐
                        ├─HTTP─▶ roof-failsafe service ─VDCP▶ DMP-8000 ─▶ roof shows DeckLink
[Companion button]  ────┘        (n8n VM, 192.168.200.84)     (192.168.200.121)
```

The Carbonite keeps feeding SDI into the DeckLink exactly as it does now — this
only replaces *who tells the DMP to display it*.

## Files

| File | What |
|---|---|
| `vdcp.py` | VDCP (Louth) frame builder + TCP/UDP sender. `--selftest` verifies frames; runs standalone to fire a clip. |
| `server.py` | aiohttp service. Both triggers hit `GET/POST /fire/{cue}`. |
| `config.example.json` | Copy to `config.json`; fill 3 values from the DMP. |
| `roof-failsafe.service` | systemd unit for the n8n VM. |
| `n8n_roof_failsafe.json` | Optional n8n webhook wrapper (logging/Slack alert). |
| `RUNBOOK.md` | Step-by-step: DMP config, deploy, wire buttons, off-show test. |

## Status

- Protocol engine: **done and verified** (`python3 vdcp.py --selftest` → PASS).
- Service + configs + trigger wiring: **built.**
- Three site values still needed from the DMP (all in `RUNBOOK.md` step 1):
  **VDCP port**, **signal/output port number**, **content ID** for the DeckLink cue.
- Enabling VDCP on the DMP + the power-off validation must happen in an
  **off-show window** — see RUNBOOK. Nothing here has been pushed to the live
  player yet.

Quick local check (safe, no network):
```
python3 vdcp.py --selftest
```
