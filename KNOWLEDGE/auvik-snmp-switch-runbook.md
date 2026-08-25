# Auvik SNMP Enable — Cisco Small Business Switch Runbook

Per-switch procedure to bring a Cisco SG300/SG500/CBS350 under Auvik monitoring.
Written 2026-08-05, first executed on the SG300-10 at 192.168.0.248 (FSQ / 3CDC HQ site).

**Collector:** 192.168.0.56 (Auvik collector runs on the AnyDesk PC)
**Community string:** deliberately not written down here. Recover it by reading it off any already-configured switch — **SNMP → Communities**, the Community String column shows it in plaintext, no clicks needed. (Auvik's own copy is masked and uncopyable; the switches are the source of truth.) Brian doesn't remember it between sessions, so read it first rather than asking.
**Auvik side is already done.** The credential "FSQ Cisco SNMP RO" (v1/2c) is scoped to *all devices on the network*, so every additional switch only needs the switch half below.

---

## Preconditions (Brian)

- AnyDesk connected, remote Chrome open, logged into the target switch GUI with a privilege-15 account.
- **AnyDesk menu → Keyboard → Local.** If this is on Auto, typed text silently never lands in the remote browser's fields — the form just errors "Empty value is invalid". Check this first, every session.
- Tell me the switch's mgmt IP so I can confirm I'm on the right box before touching anything.

---

## Steps (Claude executes)

### 1. Confirm the box
Read the header — model and firmware. Note which family it is; the menu tree differs:

| Family | Firmware | Menu notes |
|---|---|---|
| SG300 / SG500 | 1.3.x / 1.4.x | Tree as written below; save page is **Copy/Save Configuration** |
| SG500X | 1.4.x | Same as SG500 |
| SG350 / CBS350 | 2.x (© 2011-2021) | Has a **Display Mode** selector; save page is **File Operations** — see step 4b |
| Catalyst 1200 / 1300 | 4.x (URL path `/cat1k/`) | Same as CBS350 — Display Mode selector, File Operations save. Nav is a flat left tree; clicking a section header expands it but lands you on its *first* child, so click the child you actually want afterward. Toasts stack bottom-right and cover nothing important. |

### 1b. Display Mode → Advanced (SG350 / CBS350 only)
If the header has a **Display Mode** dropdown set to **Basic**, switch it to **Advanced**. In Basic the entire SNMP section is hidden from the left nav — there is no SNMP menu to click. This is the first thing to check on a 2.x box.

### 2. Enable the SNMP service
**Security → TCP/UDP Services** → tick **SNMP Service / Enable** → **Apply**.

Verify: the UDP Service Table gains a row `SNMP · UDP · All · 161`. That row is the proof — without it nothing is listening and Auvik will never see the device.

Note anything else on that page worth reporting: whether SSH and Telnet are enabled (SSH off = no Auvik config backups; Telnet on = flag it to Brian).

**Check the Save icon BEFORE changing anything.** If it is already lit on arrival, this switch has pre-existing unsaved running-config edits from someone else. Say so and get Brian's call before step 4 — saving would commit those unknown changes permanently along with ours. Do not assume.

### 3. Add the read-only community
**SNMP → Communities → Add…**

The left-nav SNMP header is a toggle — clicking it twice collapses the tree. If the page doesn't change, re-expand and click the child link again.

Set in the popup:

| Field | Value |
|---|---|
| SNMP Management Station | **User Defined** |
| IP Version | Version 4 |
| IP Address | `192.168.0.56` |
| Community String | the shared string (ask Brian if not in session) |
| Basic / Access Mode | **Read Only** |
| View Name | leave unticked (defaults to Default) |

**Apply.** Then verify the Community Table row reads: `192.168.0.56 · Basic · <string> · Read Only · Default`.

Never use All for the management station, and never `public` or `private` as the string.

### 4a. Save to startup — SG300 / SG500 (1.x)
**Administration → File Management → Copy/Save Configuration** — Source = Running, Destination = Startup → **Apply** → **OK** on the "navigation will abort the copy" warning.

Wait for `Status: Copy finished`.

### 4b. Save to startup — SG350 / CBS350 (2.x)
**Administration → File Management → File Operations** — Operation Type = **Duplicate**, Source = Running Configuration, Destination = Startup Configuration → **Apply**. Wait through "Processing Data" for **Success**.

There is no Copy/Save Configuration page on this firmware. Duplicate is the save.

**Do not try to click the red blinking `Save` link in the header.** It only exists on screen during its visible blink phase, so clicks land on nothing roughly half the time and it looks like the page is ignoring you. Always use the menu path. Use the icon only as a *state indicator*: sample it two or three times a few seconds apart — if it never reappears, running == startup and the save took.

### 5. Verify in Auvik
Auvik tab → **Discovery → Manage Credentials**. The "Devices (Need SNMP Credentials)" count should drop to 0 (or drop by one). That's the authentication proof.

Then the device's page: **Manage Device ✓** and **Monitoring ✓**.

Expect **Make & Model = Generic Device / Unknown** for up to an hour — the identification poll is on its own cycle and lags the credential check. Do not treat that as a failure. Expect **Backups ✗** on any switch with SSH disabled.

**Auvik will not retry promptly on its own.** A just-configured switch sits at Monitoring ✗ / SNMP "—" for a while. Force it: Manage Credentials → **Retry All SNMP Credentials**. Then **reload the page** — the Have/Need/Trying counters do not live-update, so a stale "Trying 4" for minutes on end usually means the page hasn't refreshed, not that anything is stuck. The clean confirmation is the Discovery Dashboard table: a green ✓ in the SNMP column for that IP.

---

## Report back per switch

One line: model, mgmt IP, SNMP enabled, community row confirmed, saved to startup, Auvik status. Plus anything odd — Telnet on, default credentials, firmware old enough to matter.

---

## Known traps

- **Keyboard mode.** Covered above. It is the single most likely reason a step appears to do nothing.
- **Auvik's own generated community string cannot be copied** — it's a masked field and Chrome blocks copy from it (ctrl+A/ctrl+C returns the page URL). Always push our own string outward to the switch; never try to pull Auvik's.
- **Chrome offers to save the community string** to Google Password Manager after the Auvik form. Decline.
- **`%SNMP-W-SNMPAUTHFAIL: Access attempted by unauthorized NMS: 192.168.0.56` in the switch log is expected.** Auvik holds four credentials and tries them in order; the three that don't match log a failure before ours succeeds. Not a misconfiguration — confirm by checking the device in Auvik rather than reacting to the syslog toast.
- **The left nav can stop responding** after one of those syslog toasts fires — every click on a section header does nothing. Reload the page (F5). The session survives and the nav comes back. Don't keep clicking; you'll waste minutes.
- **Don't touch VLAN 1 / mgmt IP settings** on a switch you're managing in-band — that's how you lock yourself out mid-session.
- If a switch goes unreachable after a change, stop and tell Brian; he has physical access.

---

## Done so far

| Switch | Model | Mgmt IP | Result |
|---|---|---|---|
| oldcontrol | SG300-10 | 192.168.0.248 | SNMP on, community set, saved. Auvik resolved it: Cisco, s/n PSZ19471BH4, 490 days uptime. SSH off. |
| Stage | SG350-28P PoE | 192.168.0.253 | SNMP on, community set, saved. Auvik named it. Telnet + SSH both off. |
| Broadcast | SG350-52P PoE | 192.168.0.254 | SNMP on, community set, saved. Auvik SNMP ✓. Telnet + SSH both off. Banner reads "Master Control brian 24". |
| Lightmast Room | SG300-10 | 192.168.0.251 | SNMP on, community set, Auvik SNMP ✓. Telnet + SSH off. **NOT saved to startup — deliberate.** The Save icon was already lit before any of our changes, meaning pre-existing unsaved running-config edits of unknown origin; Brian chose not to commit them (2026-08-05). SNMP here is lost on reboot until someone saves. |
| Digico | SG300-10 | 192.168.0.250 | SNMP on, community set, saved. Auvik SNMP ✓, resolved as Cisco. Telnet + SSH off. Banner reads "digico 21". |

| LittleFloat | C1200-8FP-2G | 192.168.0.230 | SNMP on, community set, saved to startup (2026-08-08). Telnet + SSH both off. Was configured earlier and **got wiped** — see below. |

| BigFloat | C1300-24FP-4G | 192.168.0.231 | SNMP on, community set, saved to startup (2026-08-08). Telnet + SSH both off. Factory-reset the same day, so this is a from-scratch config. |
| switch882752 | C1200-8FP-2G | 192.168.1.254 (default) | SNMP on, community set, saved to startup (2026-08-11). Factory-wiped same day; still on the default IP 192.168.1.254 and default hostname. **Note the different subnet** — collector is 192.168.0.56, this box is on 192.168.1.x; confirm Auvik can route/reach it. SSH enabled earlier on .248 for Auvik backups (needed the "SSH User Authentication by Password" toggle — see below). |

All five original switches on 192.168.0.0/24 are done. Auvik: Have Credentials 5, Need 0.

---

## The .230 wipe (2026-08-08)

LittleFloat came back with SNMP Service off and an empty Community Table — the earlier config was gone, not just unsaved. Redone from scratch and saved.

Two things to know if it happens again:

- **Do the browser work from a tab you control.** These switch GUIs bind the session to the tab it was opened in; logging in on one tab does not authenticate another, even in the same Chrome profile. Navigating a fresh tab to the switch root after Brian logs in elsewhere does pick the session up on the SG300s, but not reliably — expect to ask him to log in and then re-navigate.
- **`.250` (Digico SG300) did not answer ping** during this session, and `.56` (the Auvik collector) doesn't answer ping either — but the collector *is* alive: its polls show up on the switch as `%SNMP-W-SNMPAUTHFAIL` toasts within seconds. Don't diagnose the collector with ping.
