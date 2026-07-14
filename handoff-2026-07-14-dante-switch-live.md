# Context Handoff — 2026-07-14
**Session topic:** Live execution of the Dante switch runbook on the work network (Cisco plant, 4 switches + 1 new one incoming)
**Console / Venue:** Work theater plant — venue unconfirmed (likely Memo; Tech Table / FOH / BigRack / Attic naming, Paradigm lighting VLAN)

---

## What We Did

Audited the four Cisco switch config backups from Brian's work plant, deep-researched Dante-on-Cisco best practice (Audinate official admin PDF, Yamaha/Audinate SG300 guide, Biamp, Shure), wrote the standard into the KB, and built a per-switch remediation runbook. Nothing has been applied to the switches yet — that's THIS session's job, live on the management VLAN.

Read these two before touching anything:
- `audio/Live Sound KB/Wiki/dante-cisco-switch-config.md` — the standard and the reasoning (one querier per VLAN, unregistered multicast stays Forwarding, sACN VLAN stays un-snooped, Smartport trap, DSCP 56/46/8 strict-priority map)
- `audio/Live Sound KB/Outputs/Dante-Switch-Runbook-2026-07-14.pdf` — exact per-switch CLI, execution order, verification checklist. This is the script for the session. Follow its order: BigRack → FOH → Tech Table → Attic.

## The Plant

| Switch | Mgmt IP | Platform / queues | Role | Notes |
|---|---|---|---|---|
| BigRack | 192.168.0.254 | SG500X-class, fw 1.4.8.6 / 4 queues | Core — all trunks (gi45–47, 49, 50) | Gets the ONLY querier (VLAN 200, v3) |
| FOH | 192.168.0.251 | CBS350-class, fw 2.5.9.54 / 8 queues | Edge | gi10 trunk missing allowed-VLAN list — verify live before fixing |
| Tech Table | 192.168.0.253 | CBS350-class, fw 2.5.9.54 / 8 queues | Edge | Currently the only live querier — demote it |
| Attic | 192.168.0.252 | SG500-class, fw 1.3.5.58 / 4 queues | Edge | No multicast config, no user account, banner says "cisco" |

VLANs: 1 = management (192.168.0.0/24), 100 = Data, 200 = Dante, 300 = sACN, 101 = Paradigm (Attic-local, stays that way). Dante devices self-assign 169.254/16 on VLAN 200 — normal.

Access: Brian connects this session to the management VLAN and supplies credentials at runtime (Tech Table has user `brian`; FOH/BigRack use `cisco`; Attic is probably factory cisco/cisco). SSH is only confirmed enabled on Attic — first contact with the others may be via web GUI; expect interactive password prompts (Brian types them, or sshpass with creds he provides in-session — never store them in files that get committed).

---

## Current State

- **Done:** Audit, research, KB article (`dante-cisco-switch-config.md`, established), runbook PDF, all committed (`c9a3b71`).
- **In progress:** Nothing applied to hardware. All four switches still run their audited (possibly stale) configs.
- **Up next (this session, in order):**
  1. **BACKUPS FIRST — hard gate.** Capture the running config of ALL switches (including the new fifth one) into `audio/Network/backups/2026-07-14/` (create the folder), one file per switch, before ANY change. Via SSH `show running-config` capture where SSH works; otherwise Brian downloads via GUI (Administration → File Management → Download/Backup, source = Running) and drops the files in that folder. Do not proceed until every switch has a backup file on disk.
  2. **Probe before prescribing.** Backups may be stale. On each switch confirm live: `show ip igmp snooping vlan 200`, `show interfaces switchport GigabitEthernet10` (FOH), `show qos`, `show spanning-tree` summary, Smartport state, Unregistered Multicast = Forwarding, firmware version. Adjust the runbook steps to live reality — fix what IS wrong, skip what isn't.
  3. Execute the runbook per switch: BigRack (querier + static trunks + QoS + RSTP root) → FOH (gi10 trunk, multicast, QoS) → Tech Table (demote querier, QoS, port parking) → Attic (multicast, credentials — see watch-outs, VLAN rename, static uplink trunk).
  4. **Fifth switch:** Brian will provide its config file mid-session BEFORE any fix command is run for it. Audit it against the standard first and report; integrate only after Brian confirms. Integration checklist: unique mgmt IP on VLAN 1 (not .251–.254), hostname set, VLANs 100/200/300 created, static trunk with `allowed vlan add 100,200,300` on BOTH ends (BigRack side too — pick the port with Brian), bridge multicast filtering + global + VLAN 200 IGMP snooping, **NO querier** (BigRack owns it), Unregistered Multicast = Forwarding, QoS Basic/trust DSCP with the queue map for its queue count (4-queue: 56→4, 46→3, 8→2 · 8-queue: 56→8, 46→7, 8→2), `no eee enable` + Green Ethernet off, RSTP, no Auto Smartport, real user account, no default creds.
  5. Verify (runbook §5): snooping operational on all, querier = BigRack only, trunks carry 1,100,200,300; Brian checks Dante Controller (all devices, ONE clock leader, 10-min clean watch, audio pass). Then `copy running-config startup-config` everywhere and capture POST-change backups alongside the pre-change ones.
  6. Log the session: memory.md session note, KB CHANGELOG entry, close/update the article's Open Questions (venue confirm, FOH gi10 stale-backup question), git commit.

---

## Key Decisions (Locked)

- One IGMP querier per VLAN, on BigRack, IGMPv3, query interval 30s, election left ENABLED. Snooping without a querier is worse than none (registrations age out ~5 min).
- Unregistered Multicast stays **Forwarding** everywhere — mDNS 224.0.0.251 and Dante control 224.0.0.230–233 are link-local, never IGMP-joined; filtering them kills discovery.
- VLAN 300 (sACN) stays **un-snooped** until every node is confirmed IGMP-capable.
- QoS Basic mode + trust DSCP on all switches, strict priority, map above. Never a VoIP template.
- All trunks static (`switchport mode trunk` + explicit allow-list), Auto Smartport disabled. Dynamic Smartport config vanishes on link-down.
- RSTP everywhere, BigRack root (priority 4096).
- VLAN 101 (Paradigm) stays Attic-local.
- Backups before any change; save running→startup after verify; fresh backups after.

---

## Open Items

- Which venue is this plant? (Confirm with Brian — tag the KB article.)
- FOH gi10: was it really VLAN-1-only, or was the backup stale? Resolve live, note the answer in the article.
- Fifth switch: model/config unknown until Brian provides the file. Where it uplinks on BigRack — ask.
- Are VLAN 300 sACN nodes IGMP-capable? (Not needed today; snooping stays off there.)
- Parked: BigRack/Attic firmware upgrades, BigRack expired HTTPS cert, standardizing the `brian` account everywhere — separate dark day.

---

## Corrections / Watch-Outs

- **Do not lock yourself out.** On Attic: create `username brian ... privilege 15`, log out, PROVE the new login works, THEN `no username cisco`. Same rule for any credential change anywhere.
- **Never change VLAN 1 / mgmt IP settings on the switch you're connected through.** You're managing in-band on the same VLAN you could cut off.
- Trunk edits are link-risk. One switch at a time, confirm reachability after each block. If a switch goes unreachable, STOP and tell Brian — he has physical access.
- These backups showed no global `ip igmp snooping` on any switch — snooping was likely never actually operational anywhere. Verify live; don't assume the audit's readings still hold.
- Old firmware (Attic 1.3.5.58) may reject some CLI keywords — every runbook step has a GUI path; use it rather than improvising syntax.
- No config-file uploads to running switches — incremental CLI/GUI changes only. (Same spirit as the .env rule: no wholesale rewrites of live device state.)
- Escape hatch if a device drops off Dante after snooping goes live: Multicast → Forward All → Static on that port only. Don't tear snooping out.
- Brian's standing rules apply: no narration, step-by-step with confirmation when troubleshooting, never assume — verify.

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| `audio/Live Sound KB/Wiki/dante-cisco-switch-config.md` | md (KB article) | Dante-on-Cisco standard: the why behind every runbook step |
| `audio/Live Sound KB/Outputs/Dante-Switch-Runbook-2026-07-14.pdf` | PDF | Per-switch CLI runbook — the execution script |
| `handoff-2026-07-14-dante-switch-live.md` | md | This handoff |

---

## Resume Prompt

> Picking up from a previous session (handoff-2026-07-14-dante-switch-live.md — read it fully, plus the KB article `dante-cisco-switch-config.md` and the runbook PDF in `audio/Live Sound KB/Outputs/`). We audited my four work Cisco switches and built a Dante remediation runbook; nothing is applied yet. You are now connected to the management VLAN (192.168.0.0/24).
>
> Task: bring the network to the locked standard — optimal and stable per the KB article, runbook order BigRack → FOH → Tech Table → Attic.
>
> Hard gates: (1) Back up every switch's running config to `audio/Network/backups/2026-07-14/` before ANY change — no exceptions. (2) Probe live state first; the backups may be stale — fix what's actually wrong. (3) One switch at a time, confirm reachability after each change block, stop and ask if anything looks off. (4) I'll hand you a fifth switch's config file during the session — audit it against the standard and wait for my go before touching it. (5) After verification: save running→startup on all switches, take post-change backups, log to memory.md + KB CHANGELOG, commit.
>
> I'll supply switch credentials when you need them. Attic is the credential-fix switch — new account proven working before the old one is removed.
