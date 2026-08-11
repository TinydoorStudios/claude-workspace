# memory.md
*Last consolidation: 2026-08-11 — log in memory-archive-2026H2.md*

*Living document — newest entries at the top of Session Notes. Never delete — archive instead.*
*SIZE RULE (2026-08-11): this file loads in full at every session start, so it stays under ~30KB. Keep the current month of session notes here; roll anything older into `memory-archive-2026H2.md`. Consolidation passes log to the archive, not here, unless the pass actually found something.*

---

## How This File Works

This file is the persistent memory system for Brian Lloyd's sessions. It tracks:
- Active projects and their current state
- Decisions made and why
- Unresolved issues and open questions
- Things to remember for next time

**Rules for updating:**
- Append new entries under the relevant project or create a new section if it's a new topic.
- If updating an existing entry, edit in place and update the date.
- Mark completed items `[DONE]` and resolved issues `[RESOLVED]`.
- Never rewrite history — if something changed, add a note below the original entry.

---

## Active Projects

Canonical project state (active shows, tools & infrastructure, open issues, completed shows) lives in the KB: `Live Sound KB/Wiki/active-projects.md`. This section used to duplicate it verbatim (both frozen at "Last updated May 16, 2026" since the original entry) — trimmed to this pointer 2026-07-08 to stop the drift. SPL Monitor's project-state summary (features, next steps) was also moved there the same day; its build history stays below in Session Notes, which is where it belongs.

---

## Open Issues

*(none)*

---

## Resolved / Done

Archived 2026-08-11 to `memory-archive-2026H2.md` — everything in it was May 2026, dismissed or shipped.

---

## Seventh Heaven Pro

Reference notes moved to the KB 2026-08-11 — canonical source is `Live Sound KB/Wiki/reverb-reference-memo.md` (Early/Late behavior, the Memo preset list, VLF rule). The old copy here is in `memory-archive-2026H2.md`.

---

---

## Session Notes

*Trimmed 2026-08-11: entries before 2026-08-01 and all consolidation-pass stubs live in `memory-archive-2026H2.md`. Keep this file lean — it loads in full at every session start. Consolidation passes should log to the archive, not here, unless the pass actually found something.*

### 2026-08-08 — FSQ 2nd Wind rev 2, a phone patch sheet, and one-question-at-a-time

Built the 2026-08-08 Fountain Square show for 2nd Wind (Fifth & Vine Live, 7–10pm) as Rev 2.0 off last week's conclave build. Seven of twenty units changed mic or source, so every EQ value was re-derived rather than carried: Beta 52A replaced the D6 on kick out, the D6 moved to floor tom, D4 to rack 2, SM81 onto hat/ride/toys, an EV N/D 408 on a new bottom-snare channel, bass became mic-plus-DI (PG52 on the cab, the amp's post-EQ XLR out), and a new under-ride mic. The congas, bongos and talkback all came off. 24 channels.

The weather inverted last week's high-frequency call, which moved three real values. Last week ran 50% RH climbing to 77%; this show is 92.9°F at 38% RH at downbeat, dry the whole set. Dry air eats HF over the plaza throw and never gives it back, so baked-peak trims got LIGHTER, not deeper — snare 5.5k from −4 to −3, overheads 9k from −4 to −2 with the LPF opened 16k→18k, toys 8k from −3 to −2. Deliberately did NOT apply it to the D4's 5k tom trim (ring outlives air loss in a way snare crack doesn't) or to the vocal de-essers (they're dynamic, so they self-regulate as the humidity climbs 22 points across the set).

**Process change, made permanent:** Brian wants every fork and question asked ONE AT A TIME with an interactive prompt, his answer collected before the next — never a batched list dumped in prose. A batch makes him hold every answer in his head and lets a skipped item turn silently into a guess. Written into CLAUDE.md standing instructions, auto-memory, and the show-deep-build skill, which previously mandated the opposite ("batch the round", locked 2026-07-05, now superseded).

**Two shorthand/inventory corrections that had been costing question rounds.** A bare "408" is ALWAYS the EV N/D 408, on any source including a snare — the Lauten LS-408 is "the Lauten" or "snare mic". The old CLAUDE.md rule said the opposite and had burned a question on two consecutive builds. And the SM81 row in mic-library had no quantity marker so it read as one mic; Brian has three, which is why hat, ride and toys can all run SM81s.

**New deliverable:** a phone-first patch sheet for the stage crew — `audio/_shared/make_mobile_patch_sheet.py`, driven off the show's spec.json so it can't drift from the packet. Writes a self-contained offline HTML (dark mode for a night show, tap to check off channels, 48V/to-do filters, split-patch zone legend) plus a phone-shaped PDF for texting. Verified at 375px in both colour schemes. Its first run caught a genuinely dangerous bug in my own flag detector: it read `mic_notes` as well as `notes` and so flagged POLARITY INVERT on the snare TOP, because ch 3's note explains that ch 4 inverts against it. Now scans the actionable `notes` field only.

Also worth knowing: **WeasyPrint is broken on this Mac** — pango isn't installed, so the HTML→PDF path errors on `libpango-1.0-0`. `brew install pango` would fix it. The show packet is unaffected (it renders via reportlab).

Four KB write-backs applied (SM81 quantity, the 408 rule, the D6 twin-peak refinement, and four new eq-starting-points rows for post-EQ amp bass DI / emulated guitar feed / sampling pad / backing-track playback). The fifth staged item — the SM57 presence peak — was found already corrected on 2026-07-26. Everything is committed locally; the wiki deployment is waiting on Brian's go.


*Rolling window: keep roughly the last 30 days here. Older entries rotate to `memory-archive-2026H1.md` (new archive file per half-year) — the memory-consolidation pass handles rotation. Anything durable must be promoted (CLAUDE.md / KB / auto-memory) before it rotates out.*

### 2026-08-06 — FSQ 2026-08-07 double bill (Bright Light Social Hour + J Roddy Walston): full deep build, plus an FSQ template/patcher rescue
Two bands, one night, one Q225. Built two complete packets and two `.ses` files in `Fountain Square/2026-08-07 Bright Light Social Hour + J Roddy Walston/`, plus the thing Brian actually asked for on top: a **Band Changeover sheet** deriving the input differences mechanically from the two spec files (9 struck, 5 added, 2 changed in place, 12 untouched), bound into a combined 72-page `FSQ 2026-08-07 - MASTER.pdf`.

**The mistake that shaped the session, corrected at the end of it.** `main` was still on the retired 3,779,766-byte FSQ template with a patcher calibrated to match, and its packet builder had no EQ response card. I concluded the newer work "lived on the Cowork side and never made it into this repo" and rebuilt both from scratch. **That was wrong and I never checked.** It is all committed in this repo on branch **`show-pipeline-2026-07-26`** — 10 commits ahead, `main` strictly behind and fast-forwardable — including the recalibrated patcher (`d206792`), the EQ card (`522ddc6`, `eq_curve_card()`), the preset browser, and every show folder from 2026-07-24 to 2026-08-02. Brian caught it by asking "what do you mean it exists on the cowork side". Standing lesson: **`git log --all` / `git branch -a` before declaring a feature missing** — "not in the working tree" is not "does not exist". So the following was redundant re-derivation, not discovery — kept only because it is verified and because it documents the method. Installed the current template (archived the old to `_TEMPLATE/_retired/`) and recalibrated `apply_show_TEMPLATE_FSQ.py`: `template_size=39_910_700`, `surf_base=0x231A42C`, `scan_lo=0x2547EBB`, `scan_hi=0x25B3EBB`, four renamed `expected_names`. Vetted by **parsed value, not bytes** — the July save is a pure resave, uniform +0x2274EBB shift, all 64 block spans still 5,944 bytes, all 56 resolvable faders identical on EQ/DEQ/HPF/LPF/Mustard. Brian then re-dropped a newer save of the same size mid-session (md5 `8723eda8` → `6e1bb3b4`): 18,305 raw byte diffs, **zero** parsed parameter differences — object-ID churn, exactly what the value-diff method exists to see through. Test builds on both drops: 20 name copies per fader, 0 stray bytes, 0 do-not-write tags, full readback PASS, size identical, tripwire correctly rejects the retired template.

**Correction to auto-memory:** `fsq-template-current` claimed faders 6/7/8 ship the native gate enabled. Read straight out of the file, **D2 is off on all three** — no tom gate. Entry fixed, and the real vocal/wireless baseline (HPF 184.4, B4 −18 @5024 Q20, B2 −6.3 @335, B1 +0.5 @189) recorded from the same read.

**Intake mattered more than usual.** The Backstage Backline quote (26-0645) turned up a mismatch the input sheets hide: the sheets say "Rack 1 / Rack 2 / Floor" but the backline ships ONE 13" rack and TWO floor toms (16" and 18"). So ch 7 is a D2 — a small/mid-tom mic — on a 16" floor tom, and it is built as a floor tom with a +3/+4 @ 100 low bell (legitimate: the D2's bump is at ~150 and its documented weakness is deep lows, so 100 Hz is on the falling side, not on top of a voiced region). The quote also gave the conga trio sizes (Quinto 11" / Conga 11.75" / Tumba 12.5", so three genuinely different fundamentals to slot against), both guitar amps (bright blackface Twin vs tweed Blues Deluxe — the basis of J Roddy's two-guitar slot), the Ampeg SVT-CL/410HLF rig, and the fact that both bands bring their own cymbals and that keyboards/keys amps are artist-supplied.

**Weather drove real decisions.** Open-Meteo for the actual window: 82% RH at the 7pm downbeat climbing to 94% by 20:00, gusts 19 mph. That is the no-HF-boost end of [[humidity-inverts-outdoor-hf]] — zero HF boosts across both bands, every baked presence peak trimmed instead, and the reflex 8–10 kHz cymbal/shimmer lift on hat and overheads INVERTED into a cut. Gusts put the overhead pair at HPF 300. All vocal de-essers dynamic because the humidity keeps climbing across the two sets.

**Question round** (one batch, as the rule says): Brian confirmed "Zepp meets '50s rock" applies to J Roddy only, the J Roddy keys rig is a touring keyboard + amp (NOT his famous upright — that was the single most consequential answer), Roddy 1/Roddy 2 are two positions on one singer, BLSH vocals are wired SM58s, and ch 24 is an SPD pad. Three locker forks raised and left open (bass cab SM57→PG52, congas e604→DPA 4099, BLSH vocals SM58→Beta 58A contingent on wired ones existing); built to the sheet in all three cases.

**Reconciled the same session (Brian: "do that reconcilliation now").** `main` fast-forwarded to `show-pipeline-2026-07-26` — my four redundant edits reverted first so his committed versions win (patcher `scan_lo=0x2548000`/`scan_hi=0x25A3200`, `eq_curve_card()`, the 1153-line `build_packet.py`, the committed template `cb3f85be`). Tonight's re-dropped template was value-diffed against the committed one before deciding: parametrically identical on all 56 resolvable faders, so it was NOT reinstalled — a changed md5 alone is not a reason to churn the repo. My redundant `_retired/` copies deleted; his properly-dated archives kept. The show folder was then rebuilt on his tooling: specs converted from the legacy `research_summary` to the structured `research` object (17 and 15 units, verdicts, five-layer TRACE), packets re-rendered with quick-links + `eq_curve_card`, both `.ses` rebuilt (0 stray bytes, readback PASS), MASTER now 81 pp. The two `_worksheets/` and the changeover sheet carried across unchanged.

**Then a mistake worth remembering, because it nearly went into the KB as fact.** I "corrected" the documented FSQ tom gate to say it doesn't exist, having read `TAG_D2_EN` (the **Mustard** block) and seen 0.0. Wrong — the gate is the console's **native** dynamics at `0x05xx` bidx 3 (`0x50E/3` enable = 1.0 on faders 6/7/8, thr −36.2353, rel 0.2273 s). Reverted the patcher docstring and the auto-memory. What the check DID turn up, and nobody had noticed: **the 2026-08-01 drop is not the rename-only resave it is documented as** — threshold and release held, but the gate sidechains were re-tuned per drum (Rack 1 216.9–262.2 · Rack 2 152.5–241.8 · Floor 96.2–116.3 Hz, against a shared 129.7–317.0 on 2026-07-26). The existing vetting sweep missed it because it only diffs EQ/DEQ/filter/Mustard tags. New auto-memory [[fsq-tom-gate-native-block]]. Standing lesson: **"the tag I know reads zero" is not "the feature is off"** — diff the whole block against a channel known not to have the feature before contradicting a documented fact.

Carried into the show: ch 7 is physically a 16" floor tom, so the template's 152–242 Hz rack-tom sidechain on that fader is aimed wrong — flagged in both specs' `changes` and the ch 6/7/8 notes as a soundcheck move, not patched.

Brian confirmed both files load and work on the console, so `verified` is stamped and the show is published to the wiki.

Not committed (Brian commits).

### 2026-08-06 — One-off blank patch sheet: 48 inputs, red subsnake only

Brian asked for a one-off blank built on the Design 2 Two-Up Split template (`audio/Other/Master Patch Sheet 2026 Revamp.xlsx`), scaled to 48 inputs with only the red zone. Answered on two points: red stays at 16 locations (R-1…R-16), and the Wireless 1–4 block comes out entirely. Green/Blue/Orange stripped with it.

Output: `audio/Other/Blank Patch Sheet - 48ch Red Subsnake.xlsx`. Channel grid is two-up 24/24 (rows 5–28, ch 1–24 left / 25–48 right), hidden helper columns P/Q normalise the typed code to `Red-<n>`, CF colors the Split Patch cell `E06666` on any entry starting with R, and the snake sheet at the bottom two-ups locations 1–8 / 9–16 pulling instrument, mic, **console channel** and notes back out of either block. Added a dropdown of R-1…R-16 on the Split Patch columns (non-blocking, `showErrorMessage=False`) on top of the free-typing the master allowed. Kept the 8 mixes.

Two build gotchas worth keeping: dxf (conditional-format) fills need **both** `fgColor` and `bgColor` or Excel ignores the color — `PatternFill("solid", start_color=…, end_color=…)`, not `fgColor=` alone. And all ARGB strings want the `FF` alpha prefix; a bare 6-digit hex writes as `00RRGGBB`. Generator script kept in the session scratchpad, not the repo — it's a one-off.

### 2026-08-04 — Watermark chain found broken since 2026-07-19 (this file + KB CHANGELOG both stalled for ~2 weeks)

This run's Phase 2 (find the last watermark) turned up a real gap, not just an unlogged session. Findings, checked directly against the live files, not inferred:

- **This file's Session Notes has no "Memory Consolidation" entry after 2026-07-19** — the entry directly above this one. Yet `active-projects.md`'s header lists `memory-consolidation 2026-07-22, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30, 2026-07-31, 2026-08-01, 2026-08-02, 2026-08-03` as sources, and `list_sessions` shows roughly 15 "Memory consolidation daily" sessions completed in that window (all idle/finished, none crashed). So the daily task has clearly been running and clearly has been editing `active-projects.md` — it just stopped writing its own watermark entry here after 2026-07-19.
- **`Live Sound KB/CHANGELOG.md` has zero entries dated after 2026-07-19** (grepped directly: no line matches any date 2026-07-20 through 2026-08-04, and no match for any of the distinctive show/feature names from that window — FSQ double-header, Gear Tickets, XPR 3500, Echoes T7E mkII factory library, the locker-fork gate, house-wireless mult rule, EQ response card, FSQ preset browser, the two FSQ template resaves). `active-projects.md` cites "source: memory.md + KB CHANGELOG 2026-07-XX" for a dozen-plus entries in that range — none of those citations resolve to anything in either file.
- **A specific false claim got written into `questions.md` by the 2026-08-03 pass**, and is corrected there today: that pass asserted the `## 2026-08-02 — FSQ double-header built (The Shades + Ric Sexton)` CHANGELOG entry "is present... just appended out of order." It is not present anywhere in the file (verified by direct read, grep, and an md5/mtime check to rule out a stale mount). The 2026-08-03 pass appears to have trusted an earlier claim without actually re-reading the file.
- **What's NOT lost:** `active-projects.md` itself has been kept current and reads as accurate — every show, tool change, and open item from 2026-07-22 through 2026-08-03 is there in full narrative detail, it's just not cross-referenced correctly (the memory.md/CHANGELOG citations inside it are the broken part, not the content). Canonical project state is intact; the session-history trail and the KB change-log trail are the two things that went dark.
- **Not attempted in this run:** reconstructing ~2 weeks of `memory.md` Session Notes or `CHANGELOG.md` entries from `active-projects.md`'s own summaries. That's a real option (the source material already exists in readable form) but it's a bigger, more error-prone job than a daily hygiene pass, and editing `CHANGELOG.md` has been explicitly out of this skill's file scope in every prior run. Flagged to `questions.md` (Memory / Automation, High Priority) for Brian's call on how to handle it.
- Corrected `active-projects.md`'s header note, which claimed the 2026-08-03 pass had the "watermark chain restored" — it didn't; that pass fixed one questions.md flag but never touched this file, which is why the chain is still broken as of today.

### 2026-08-02 — FSQ double-header deep build: The Shades + Ric Sexton
Two xlsx input lists arrived for the same FSQ night. Both were the SAME unfilled master template
apart from one cell (CH19 sax), with **zero vocal channels** on either — raised as a blocker
rather than guessed at, along with the two-Beta-52 conflict, the blank Guitar 2–4 / Keys / Misc
rows, and the OH-on-9/10 conflict with the reserved SNARE PL8 return. Brian answered in one round:
two separate shows, three wireless vocals each, no snare bottom, one guitar, IMP DIs on keys,
20–32 dead, D6 to kick out with the Beta 52A on the floor tom, and Sexton swaps alto/soprano on
one channel through his own mic and pedal. He then **delegated two decisions back to me** — the
snare locker fork (chose the Audix i5 over the specified e604: +5 dB @150 Hz body wins outdoors
where the e604 is documented thin, and its 5.5 k liability was being trimmed on a humid night
anyway) and the vocal slotting (voice types are genuinely unresearchable — built as role slots
with the template's 184 Hz HPF overridden to 90/110/120 and three non-overlapping B2 nasal lanes,
with a documented swap procedure). Genres verified with named evidence first: Shades = live-
instrument soul/alt-R&B (CincyMusic, shadestheband.com, Spectrum News); Sexton = smooth jazz
(WYSO, ricsexton.com, *Fruition*). He spells it **Ric**, not Rick. Weather fetched: 87–94% RH,
so no HF boost anywhere in either show and the hat's shimmer lift inverted to a cut — second
consecutive saturated-air FSQ night, so that rule is now promotable. Both packets validated 0
warnings, md_lint PASS, both .ses built with 0 bytes changed outside mic'd blocks and readback
PASS on all 17 faders. Neither published — waiting on Brian's go. Logged to eq-advisor-log,
active-projects Completed Shows, CHANGELOG. Not committed (Brian commits).

### 2026-08-02 — Gear Tickets: finished the build and put it live

Picked up the QR ticket-submission project part-built and took it to production.
Repo `Code/GearTickets/`, full runbook in its README.

**What was missing when I picked it up.** `tickets.tinydoorstudios.com` had no
DNS record at all, so nothing outside the VM could reach the form — added the
tunnel ingress rule and the proxied CNAME by API (routing is remote-managed;
local config.yml is ignored). Then credentials, env vars, and a lot of debugging.

**Six real defects, all found by submitting actual tickets through the public URL
rather than by reading the workflow.** Worth remembering because most were
silent:

1. **Postgres Query Parameters split the resolved value on commas.** Any
   description containing a comma shifted every parameter after it into the wrong
   column — the first test ticket stored the venue as the submitter's name. Fix
   is a single array expression `{{ [ a, b ] }}`, which takes a different code
   path in the node and is never split. Applies to every n8n Postgres node, not
   just this project.
2. **A node returning zero items ends the branch and still reports success.**
   The dedupe SELECT excludes the current ticket, so on an empty ledger it
   matched nothing and the execution stopped dead with a green tick — no triage,
   no Monday, no Slack. First-ticket-only, and invisible the whole build because
   there was always old test data to match. Clearing the test data is what
   exposed it. `alwaysOutputData: true` fixes it.
3. **Binary data is only reachable from the node it arrives at.** The photo
   writer sat downstream of a Postgres node, so the buffer call returned
   undefined and killed the run. `getBinaryStream` and `getBinaryPath` are both
   blocked in the Code sandbox, and this instance stores binary as
   `filesystem-v2` so there's no inline base64 either. Restructured to stage
   photos straight off the form trigger, then move them once the ticket ID exists.
4. **`$json` after a Postgres node is only what that query RETURNED.** Monday
   rejected the create mutation because the node was reading its fields off an
   `UPDATE ... RETURNING ticket_id`.
5. **`$env` in expressions needs `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`** — without
   it the triage node fails with "access to env vars denied", and since it's
   `neverError` that reads as a successful-but-untriaged ticket.
6. **Compose passes env through an explicit `environment:` list**, so adding a
   var to `/opt/n8n/.env` alone never reaches the container. Same class of trap
   as the missing photo bind-mount.

**Decisions Brian made along the way.** Groq (`llama-3.3-70b-versatile`) for
triage over Gemini — Google no longer publishes free-tier limits, and Groq's
endpoint is already the exact OpenAI shape the node speaks. One QR code instead
of five venue-prefilled ones, because gear moves between sites and stickers
don't. Slack to a new `#gear-repair` channel rather than a DM, message leading
with the severity. Monday failures made soft so a Monday outage can't take the
Slack post down with it — tested by pointing the nodes at a broken URL.

**Two things I got wrong and had to correct.** I created an n8n API key that
turned out to be useless (SSH + the n8n CLI already covered everything) — left to
expire on Brian's call. And I told Brian I'd written this memory entry before I
actually had; corrected in the same session.

Auto-memory [[gear-tickets-system]].

### 2026-08-01 — New FSQ template drop: rename-only, patcher recalibrated

Brian dropped a new FSQ .ses at the usual path (`~/.wine/drive_c/Projects/brian fsq start july 2026.ses` — same filename every drop). 39,910,700 bytes, md5 `cb3f85be…`, +82 bytes over the 2026-07-26 template.

Vetted it before touching a constant, same method as the last drop. Surface table read clean at the calibrated offsets. `block_bounds` + `_eq_window` + `_lpf_value_offset` computed on all 64 faders in both files came back identical. Then diffed every EQ / DEQ / filter / Mustard / do-not-write tag by parsed value rather than by byte — zero parameter changes anywhere in the channel blocks. Byte diffs are 3,100-odd six-byte object-ID runs the desk renumbers on every save; reading those as content is how you'd talk yourself into a recalibration you don't need. (difflib on 40 MB never finishes — binary-search the shifted alignment point instead.)

Actual changes: fader 57 `Ch 57` → **`Click - Tempo`**, fader 58 `Ch 58` → **`FOH Playback`** (20 name copies each), and the +82 bytes are a new macro **`Auto Tempo`** at 0x260F569 in the macro/panel table, well past every patcher write path. Name slots are fixed width, so the longer names shifted nothing.

Installed the template (old one archived to `_TEMPLATE/_retired/` as "retired 2026-08-01"), updated `apply_show_TEMPLATE_FSQ.py` — `template_size` 39_910_618 → 39_910_700 and the two `expected_names` entries, nothing else. Calibration test on ch 1/13/25 PASS: 0 stray bytes, 0 do-not-write tags, 0 unmapped Mustard, full readback OK. Confirmed the tripwire now rejects the retired template. Regenerated the preset-library HTML (unchanged — presets live at the front of the save).

Two things for Brian: the FSQ **spare range is now 47–56**, not 47–58, and `rename_fsq.py` is still calibrated to the retired 3.78 MB template (stale since 2026-07-25, will abort on anything current). Auto-memory [[fsq-template-current]] replaces the old 07-26 entry.
