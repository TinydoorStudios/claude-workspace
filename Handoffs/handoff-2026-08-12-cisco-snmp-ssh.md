# Context Handoff — 2026-08-12
**Session topic:** Cisco switch fleet — factory wipes, SNMP enablement for Auvik, and one SSH/Auvik-backup fix
**Console / Venue:** N/A — network gear (FSQ / 3CDC HQ, 192.168.0.0/24 + one on 192.168.1.x)

---

## What We Did
Worked through a batch of Cisco small-business/Catalyst switches for Auvik monitoring. Re-enabled SNMP on two Catalyst 1200/1300 boxes whose config had been wiped, factory-wiped two more Catalyst 1200s over the USB-C console, set up SNMP from scratch on the freshly-wiped ones, and chased an Auvik SSH-backup failure on the SG300 at .248 down to a single switch-side toggle. Everything is driven from the Mac (in-app Chrome + Bash) and the Broadcast PC over AnyDesk; the Auvik collector is `192.168.0.56`.

---

## Current State

- **Done:**
  - **.230 LittleFloat (C1200-8FP-2G)** — SNMP on, community set, saved to startup. Was wiped; rebuilt.
  - **.231 BigFloat (C1300-24FP-4G)** — SNMP on, community set, saved. Factory-reset then rebuilt. Verified config-side over AnyDesk (SNMP Service Enabled, community row present, two successful running→startup saves in the log).
  - **New C1200 #1** — factory-wiped over USB-C (S/N PVN29281C6K), verified `Unit factory default` + `CDBITEMSNUM: 0`.
  - **New C1200 #2 "switch882752"** — factory-wiped (S/N... this is the one now at **192.168.1.254**), then SNMP set up from scratch: service on, community `192.168.0.56 · Basic · fsq-auvik-ro-K7m2Qx · Read Only · Default`, saved to startup.
  - **.248 SG300 SSH for Auvik** — enabled SSH service + host keys, and fixed the real blocker: **"SSH User Authentication by Password"** was unchecked, so Auvik's SSH login failed at auth even though the port was open. Enabled it, saved. Mgmt Access Auth for Secure Telnet (SSH) already = Local. Auvik already has the `brian` login credential (its session showed in the SSH Active User Table).

- **In progress / needs Brian:**
  - **Auvik has NOT confirmed green** on .230, .231, or the SSH fix on .248. All the retries need a signed-in Auvik session (I don't enter credentials). .231's switch log showed **zero** SNMP polls landing — Auvik hadn't reached it yet at last check.

- **Up next:**
  - In Auvik: Discovery → Manage Credentials → **Retry All SNMP Credentials**, then reload the page, and confirm green SNMP ✓ for .230 and .231, and SSH ✓ / Backups starting on .248.
  - Decide the new C1200 "switch882752" management IP (see Open Items — it's on the wrong subnet).

---

## Key Decisions (Locked)

- **Community string is `fsq-auvik-ro-K7m2Qx`** for all switches, station `192.168.0.56`, Version 4, Read Only, View Default. It is deliberately NOT written in the runbook — recover it by reading it off any configured switch's SNMP → Communities table (plaintext there). Brian doesn't remember it between sessions.
- **Reusable wipe tool lives at `Code/CiscoReset/reset_catalyst.py`** (+ README). Arm it, THEN power-cycle the switch. It fires ESC / `2` / `Y` off the console re-enumeration; then send ONE more Esc by hand (`printf '\033' > /dev/cu.usbmodem*`) to exit the menu and boot. Catalyst 1200 and 1300 behave identically.
- **The one-Esc rule:** the bootloader buffers input; a stream of Esc self-cancels. Single keystrokes only, driven on timing, never by parsing the console stream.
- **Auvik SSH backups on SG300 need "SSH User Authentication by Password" ENABLED** — not just the SSH service. This was the whole .248 fix.
- **SG300-10 cannot do TrafficInsights** — no sFlow/NetFlow support at all. Only SG350/SG550 (e.g. .253, .254) have sFlow. Confirmed by the menu.
- **Save on Catalyst 1200/1300 (4.x):** Administration → File Management → File Operations → Duplicate, Running → Startup. On SG300 (1.x): Copy/Save Configuration.
- Preference set this session: **stop using full screenshots** — use `zoom` on the relevant region instead.

---

## Open Items

- **New C1200 "switch882752" is on the wrong subnet.** It's at the factory-default `192.168.1.254` on `192.168.1.x`, but the Auvik collector is `192.168.0.56` and the other five switches are all `192.168.0.x`. SNMP is configured but Auvik likely can't route to it where it sits. Brian needs to decide its real mgmt IP on `192.168.0.x` (I can set it under IPv4 Configuration). Also note `192.168.1.254` collides with the SG350 that was there earlier.
- **`.250` (Digico SG300)** did not answer ping during the session — worth a look, it's the one switch that was unreachable.
- **`.251` Lightmast Room SG300** SNMP was set earlier (2026-08-05) but deliberately **NOT saved to startup** (pre-existing unknown unsaved edits). Still lost on reboot until someone saves.
- Auvik confirmation for everything above is pending a signed-in Auvik session.

---

## Corrections / Watch-Outs

- **The Auvik collector `192.168.0.56` does NOT answer ping** — but it IS alive. Its SNMP polls show up as `%SNMP-W-SNMPAUTHFAIL` toasts on the target switch within seconds (Auvik cycles 4 credentials; the 3 misses log failures before ours succeeds). Don't diagnose the collector with ping.
- **These switch GUIs bind the session to the tab they were opened in** — logging in on one tab doesn't authenticate another, even same Chrome profile. Expect to have Brian log in, then navigate.
- **Catalyst 1200/1300 nav quirk:** clicking a left-nav section header expands it AND lands you on its first child, which shifts everything below — click the child you actually want afterward.
- Community string is masked/uncopyable in Auvik itself; the switches are the source of truth.

---

## Files Delivered / Touched This Session

| File | Format | Description |
|------|--------|-------------|
| `Code/CiscoReset/reset_catalyst.py` | Python | Reusable Catalyst 1200/1300 USB-C factory-reset catcher |
| `Code/CiscoReset/README.md` | md | How to run the reset: arm → power-cycle → one-Esc rule, verification, dead ends |
| `KNOWLEDGE/auvik-snmp-switch-runbook.md` | md | Updated: per-switch procedure, added .230/.231/switch882752 rows, Catalyst family row, community-recovery note, wipe/subnet caveats |
| `~/.claude/.../memory/catalyst-1200-usbc-console-reset.md` | md | Updated: 1300 verified identical, extra exit-Esc step, script path |

---

## Resume Prompt

> Picking up from the 2026-08-12 Cisco switch session. We factory-wiped and/or set up SNMP on four Catalyst 1200/1300 boxes and fixed Auvik SSH backups on the .248 SG300.
>
> **Next:** confirm Auvik actually sees them. Once I'm signed into Auvik, run Discovery → Manage Credentials → Retry All SNMP Credentials, reload, and check green SNMP ✓ on .230 and .231, plus SSH ✓ / Backups on .248. .231 had shown zero SNMP polls landing, so it may need a poll cycle.
>
> **Also decide:** the newly-wiped C1200 "switch882752" is stuck on the factory-default 192.168.1.254 (wrong subnet — collector and the other 5 switches are on 192.168.0.x). Its SNMP is already configured (community fsq-auvik-ro-K7m2Qx → 192.168.0.56). It needs a real mgmt IP on 192.168.0.x before Auvik can reach it — set it under IPv4 Configuration.
>
> **Key context not in standing memory:** community string is `fsq-auvik-ro-K7m2Qx` (read it off any switch's SNMP→Communities, not written in the runbook). Collector 192.168.0.56 doesn't answer ping but is alive. Wipe tool is `Code/CiscoReset/reset_catalyst.py`. Don't use full screenshots — zoom on regions.
