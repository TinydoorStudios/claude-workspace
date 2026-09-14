# Context Handoff — 2026-08-12
**Session topic:** Auvik "free Dream Machine SE" trial-qualification check + finishing SNMP on the Cisco switch fleet
**Console / Venue:** N/A — network gear (FSQ / 3CDC HQ, 192.168.0.0/24, one stranded switch on 192.168.1.x)

---

## What We Did
Set up SNMP for Auvik on the new switch at **192.168.0.235** (turned out to be a **Cisco SG350-10**, hostname now "Road-Hog4" in Auvik), then verified the previously-wiped **C1200 "switch882752"** at 192.168.1.254 already had its SNMP config. Then pivoted to the real goal: logged into Brian's Auvik account and checked whether he **qualifies for the free Ubiquiti Dream Machine SE** promo tied to the Auvik trial. He does — but sits exactly on the 8-device threshold.

---

## Current State

- **Done:**
  - **.235 (SG350-10, "Road-Hog4")** — SNMP set up from scratch and saved. Enabled SNMP Service (Security → TCP/UDP Services), added community `192.168.0.56 / Basic / fsq-auvik-ro-K7m2Qx / Read Only / Default`, saved running→startup. Already showing **Up + managed** in Auvik.
  - **switch882752 (C1200-8FP-2G) at 192.168.1.254** — verified SNMP is already correct: service enabled, same community row present, active (no inactive asterisk). **NOT yet visible in Auvik** because it's on the wrong subnet (collector can't reach 192.168.1.x).
  - **Auvik qualification check** — read the promo terms and Brian's account (`fsqcinci.lnx.my.auvik.com`, site "Brian Lloyd 3CDC Headquarters" / `fsqcincihq`). Collector 1-of-1 online, trial active with **7 days left**, **Billable Network Devices = 8**.

- **In progress / needs Brian:**
  - Adding margin above the 8-device line (see Open Items). Right now he's *exactly* at 8 online/managed.
  - Auvik banner: **"SNMP credentials are needed for 1 new device"** — not yet actioned. Offered to run Discovery → Manage Credentials → Retry and identify that device; Brian hadn't answered when we broke for the handoff.

- **Up next:**
  - Bring **switch882752 onto 192.168.0.x** so Auvik discovers it (pushes managed count to 9–10 for safety). SNMP already configured on it; just needs a mgmt IP on the .0 subnet under IPv4 Configuration. (This was also the leftover task from the 2026-08-12 cisco-snmp handoff.)
  - Optionally get **Digico (.250, SRW2008)** back online — it's discovered but currently **Down**.
  - Clear the 1 pending-SNMP device in Auvik.

---

## Key Decisions (Locked)

- **The promo's qualifying milestone** = collector deployed to the site + **≥ 8 physical devices in a *managed* state**, of type router / switch / firewall / controller. pfSense, virtual, and simulated devices do NOT count. Auvik's own "Billable Network Devices" number is the metric that maps to this.
- **Eligibility gates all clear:** US resident (Cincinnati), IT role at 3CDC (11+ employees), business email domain 3cdc.org, trial activated well before the **Aug 31, 2026 4:59 PM ET** deadline. Auvik confirms qualification by **Sept 30, 2026**.
- **Do not let the trial lapse or remove devices** before Auvik takes its qualification snapshot. Keep collector + all 8+ switches up through the trial window (~ends Aug 19).
- **Community string stays `fsq-auvik-ro-K7m2Qx`**, station 192.168.0.56, Read Only, View Default — same across the whole fleet. Recover it off any switch's SNMP → Communities table (not written in the runbook).
- **Credentials rule this session:** I do NOT type login passwords into switch or Auvik login pages — Brian logs in, then I drive. (The switch GUIs also bind the session to the tab it was opened in.)

---

## Open Items

- **He's at EXACTLY 8 managed/billable devices — zero margin.** One switch (Digico .250) is already Down, and the trial has ~7 days left. If a second switch drops before Auvik's snapshot he could fall to 7. Fix: get switch882752 onto .0 subnet and/or bring Digico back up.
- **switch882752 still stranded at 192.168.1.254** (wrong subnet; also collides with the SG350 that was previously at .254 — note "Broadcast" SG350-52P now lives at 192.168.0.254). Needs a real mgmt IP on 192.168.0.x. SNMP already done.
- **Digico (.250, Cisco SRW2008) is Down** in Auvik — same box that didn't answer ping last session.
- **"1 new device needs SNMP credentials"** banner in Auvik — unidentified; needs a Manage Credentials retry to resolve.

---

## The 9 discovered switches (Auvik inventory, this session)

All real physical Cisco switches, recognized model + serial, so all qualifying type:

| Device (Auvik name) | Model | IP | Status |
|---|---|---|---|
| BigFloat | Cisco C1300-24FP-4G | .231 | Up |
| Broadcast | Cisco SG350-52P | .254 | Up |
| LightMast-Room | Cisco SRW2008 | .251 | Up |
| LittleBlink | Cisco C1200-8FP-2G | .22 | Up |
| LittleFloat | Cisco C1200-8FP-2G | .230 | Up |
| oldcontrol | Cisco SRW2008 | .248 | Up |
| Road-Hog4 | Cisco SG350-10 | .235 | Up (set up today) |
| Stage | Cisco SG350-28P | .253 | Up |
| Digico | Cisco SRW2008 | .250 | **Down** |

8 Up + managed = meets the ≥8 requirement. Digico is the flapping 9th. switch882752 is NOT in this list (unreachable on .1.254).

---

## Corrections / Watch-Outs

- **The .235 switch is an SG350-10, not a Catalyst 1200** — so its GUI is the SG3xx style (iframe-based), and its **Add community dialog opens as a window.open popup that Chrome blocks/hides**. Coordinate-clicking "Add..." does nothing visible. The fix that worked: capture the popup window handle via JS (`window.open` override on the mainFrame), then fill and submit its form through the popup's DOM (`txtIp`, `txtCommunity`, `rdoUser`, `rbVer4`, `rdoBasicMode`, `rdoAccessMode` value 1, `chkView` + view `Default`, then `#defaultButton`). Same trick will be needed on any other SG3xx.
- **SG350 "Save":** the top-right red **Save** badge briefly not-rendering is misleading — it can look cleared and still be unsaved. Clicking the Save link runs a "Processing Data" copy running→startup; confirm the badge is gone AFTER that completes.
- **In-app browser (Claude_Browser) can't reach the LAN** — had to drive Brian's real Chrome (claude-in-chrome) for all switch + Auvik work.
- Auvik collector **192.168.0.56 does not answer ping but is alive** (carried over from prior session).

---

## Files Touched This Session

None delivered. Config changes live on the switches and in Auvik (see above). This handoff + the prior `handoff-2026-08-12-cisco-snmp-ssh.md` cover the fleet state.

---

## Resume Prompt

> Picking up from the 2026-08-12 Auvik / Dream Machine session. We confirmed Brian **qualifies** for the free Ubiquiti Dream Machine SE promo — collector online, trial active (~7 days left), and **8 managed physical Cisco switches** discovered in Auvik (site `fsqcincihq`, tenant `fsqcinci.lnx.my.auvik.com`). But he's sitting **exactly on the 8-device minimum** with one switch (Digico, 192.168.0.250) already Down.
>
> **Next:** add safety margin above 8 before Auvik's qualification snapshot. Two moves: (1) bring the wiped C1200 "switch882752" from its stranded 192.168.1.254 onto the 192.168.0.x subnet — SNMP is already configured on it (community `fsq-auvik-ro-K7m2Qx` → 192.168.0.56), it just needs a mgmt IP on .0 under IPv4 Configuration; (2) get Digico (.250, Cisco SRW2008) back online. Also clear the Auvik "SNMP credentials needed for 1 new device" banner via Discovery → Manage Credentials → Retry and identify what that device is.
>
> **Key context not in standing memory:** I don't type login passwords — Brian logs into switches/Auvik, then I drive his real Chrome (in-app browser can't reach the LAN). The .235 switch is an SG350-10 whose community "Add" dialog is a Chrome-blocked popup — drive it via the window.open-handle JS trick. Community string `fsq-auvik-ro-K7m2Qx` is the fleet standard (read it off any switch, not in the runbook). Don't let the trial lapse or remove devices before Auvik confirms qualification (by Sept 30, 2026); activation deadline was Aug 31.
