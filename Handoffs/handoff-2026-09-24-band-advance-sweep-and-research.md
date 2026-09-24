# Context Handoff — 2026-09-24
**Session topic:** Band Advance — the 122-fix correctness sweep, then the product improvements from the 2026-09-16 research pass
**System:** `Code/BandInfoForm` → `/opt/band-advance` on the n8n VM (192.168.200.84), live at advance.tinydoorstudios.com

---

## What We Did

Two batches, both deployed.

**Batch 1 — the correctness sweep (committed 09-22 as `b0e4d3a`, staged + deployed 09-23 as `67e02ca`).** Fourteen reviewers read every line of `app/`, `tools/`, `db/`, `n8n/`, `ops/`, `backup/` and the staging harness: 184 raw findings → 127 after dedup → 124 confirmed under adversarial review → 122 fixed, plus 10 regressions the diff-reviewers caught in the new code and repaired. The session hit the usage limit mid-run; the fix stage was restructured into six parallel lanes and resumed from cache, so only the fixes were paid for twice.

**Batch 2 — the research improvements (committed 09-24 as `ea47c71`, deployed same day).** Implemented from `Handoffs/band-advance-audit-2026-09-16/report-research.md` section (d): the reminder ladder rebuilt (#1, #2, #4), T-7 turned into the confirmed-schedule send (#3), set length in every band email (#7), open tracking (#11), artist notes (#12), the subject convention (#14), a lightning-hold clause (#15), and two new form questions from the field-gap table (b).

---

## Current State

- **Done:** Both batches deployed. VM `.deployed_commit` = `ea47c71`, service active, healthz ok, public form 200, every deployed `.py` parses under the VM's 3.11, and the four new DB columns are live (`submissions.trailer`, `submissions.crew_count`, `short_links.first_opened_at`/`open_count`, `artists.advance_rating`). `n8n/advance_lifecycle.json` redeployed and active — its summary node would otherwise have mailed nothing at all on a run whose only sends were schedules.
- **Staging (fresh clone, both suites):** 158/158 and 620/620.
- **In progress:** nothing.
- **Up next:** the open items below. Research #8 (the send outbox) is the one with real operational value left in the list.

### The band-facing ladder as it now stands

| Touch | Subject | Body |
|---|---|---|
| welcome (at booking) | `Welcome to <series> — Band · Venue · M/D` | venue block + form link + deadline + set line |
| T-10 | `Reminder — we need your show details by <deadline> — …` | first firm chase, names what's missing |
| T-7 | `Your schedule — …` or `Your schedule and what we still need — …` | confirmed schedule to **every** show; chase folded in underneath only if unanswered |
| T-3 | `Three days out — …` | your engineer builds from this tomorrow; no plot = generic patch |
| T-1 | `Last call — …` | reply today or it's ad hoc on the day |
| day-before | `Tomorrow — …` | schedule, responded shows only |
| thank-you | `You're All Set — …` / `Thanks for playing — …` | — |

One deadline everywhere: `min(show − 7d, booking + 14d)`, clamped to `[tomorrow, show − 1d]`.

---

## Key Decisions (Locked)

- **No phone escalation anywhere.** Research #4 proposed a call at ~10 days; Brian: "remove the phone option. everything needs to be my email as much as possible." The 10-day tier became an email tier on the existing ladder, no band email asks anyone to phone, and the internal row shows the band's email address, not a number. The staff link reads "type their answers →".
- **The "not needed here" line is out of the email.** Research #15's guest-list/credentials/settlement line was written into the hospitality blocks and then pulled back out at Brian's word. The weather/lightning-hold clause stayed — that's a rule, not a list of what we don't offer.
- **Form: two of the four gap fields only** — trailer and crew count. No arrival ETA, no playback/click.
- **The trailer question is optional and conditional** — it only renders once the large-vehicle count is above 0, and clears if the count goes back to 0.
- **`performers` keeps its exact meaning and every downstream use**, including `drink tix = performers × 2`.
- **T-7 reuses the `advance_reminders` row** (`days_before = 7`) rather than a new tier or table, which is what guarantees a show can't get both a schedule and a chase.
- Research-driven changes are tagged `2026-09-24 research #N:` in the code; sweep fixes are tagged `2026-09-21 sweep (ID):`.

---

## Open Items

- **Drink tickets — Brian dismissed the question, unresolved.** Splitting crew out of `performers` means a 4-piece with 2 techs now generates 8 drink tickets where the old combined question produced 12. The code currently does `performers × 2` (crew excluded), while the form's help text still promises "drink tickets and water for all performers and crew". One or the other should move.
- **Research #8 — the send outbox.** One row per send with an idempotency key, written in the same transaction as the tier stamp, so there's a durable record of exactly what went out and a re-run can't double-send. Was scoped for this session and not started. Highest-value item left.
- **Research #5 — structured input-list capture** (ch / source / player / mic-or-DI / stand / phantom / notes) feeding `advance_bridge.py` → the deep build. Biggest win for show builds, biggest ask of the band. M–L.
- **Research #6 — the other two form fields** (arrival ETA, playback/click) plus the on-stage-contact help-text tightening. Turned down for now, not refused outright.
- **Research #9** — band-side edit link so a resubmission is a diff, not a new record. **#10** — advancing board on the dashboard. **#13** — hold-for-review only where wording risk lives (needs #8 first).
- **Research #16 — ten minutes of Brian's:** claim the free Master Tour Venue tech pack for FSQ and WP.
- **`ADVANCE_SCHEDULE_CC`** — the week-out schedule CCs nobody today, because neither the staffing sheet nor `bookings` carries a staff email address (phones only). The env var takes a comma list if a crew address should see it. Unset = no CC. Full-file rewrite of `advance.env` if you set it — never a partial.
- Still open from earlier sessions, Brian only: the Cloudflare WAF rule for `/internal/*`, a real `ADVANCE_GATE_PASS_2`, and recording the backup passphrase + the three `DROPBOX_*` vars in `TDS_Credentials_CheatSheet.md`.

---

## Corrections / Watch-Outs

- **A staging test that asserts "these are the only acts on this bill" must take its date from `free_date(venue, n)`.** The clone carries real bookings, so a hardcoded `TODAY + timedelta(days=n)` eventually lands on a live show: a real Salsa act holding 7:00p refused two fixtures through the set-start guard (correctly), and a third live act shifted another's columns. Seven failures in batch 1 and one in batch 2 were all this, not code. `free_date` also steps over every hardcoded offset in the suite — the first cut of it stole x-h's day.
- **Two more test-only traps found:** Jinja escapes the apostrophe, so `can't` in help text won't match a raw string assertion; and a series with a locked `## Schedule` block (Salsa) supplies its own row labels, so don't assert the default English rows. The English venue-doc links ride under *both* halves of a bilingual email by design — cut them before asserting "no English in the Spanish half".
- **Research output is a deliverable.** The research findings were implemented before they were ever shown; Brian: "nowhere did you show research findings and suggestions. i asked for that." Show the findings, then build.
- The auto-mode classifier denies remote shell **writes** over ssh (`setup.sh`, pipeline runs). Reads are fine. Batch 1 stalled on this until Brian approved it.
- Running the pipeline by hand still sends real band-facing email. `ADVANCE_MAIL_DISABLED=1` when the goal is only the data side.

---

## How to Run Staging / Deploy

```bash
# staging: rsync the repo to the VM, build the clone, run both suites, tear down
rsync -az --delete -e "ssh -J tds -i ~/.ssh/proxmox_tds" \
  --exclude __pycache__ --exclude data --exclude output --exclude drafts --exclude filled \
  ~/Documents/Claude/Code/BandInfoForm/{app,tools,ops,db} brian@192.168.200.84:advsrc/
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'advsrc/tools/staging/setup.sh advsrc'
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'advtest/code/tools/staging/run_tests.py'
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'advtest/code/tools/staging/run_tests_extra.py'
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'advtest/code/tools/staging/teardown.sh'

# deploy (from the Mac, main checked out and clean)
cd ~/Documents/Claude/Code/BandInfoForm && ./deploy_app.command
./deploy_n8n_workflows.command advance_lifecycle.json   # only when an n8n/*.json changed
```

Staging runs against a clone of the live DB with a mail stub on :8199 — nothing it does can reach a band. The suites are stateful: rebuild the clone before a full run, or you get false failures from the previous run's fixtures.

---

## Resume Prompt

> Picking up from the 2026-09-24 session on the Band Advance pipeline. Two batches are deployed: the 122-fix correctness sweep (`67e02ca`, 09-23) and the research-driven product improvements (`ea47c71`, 09-24). VM is at `ea47c71`, staging green at 158/158 + 620/620. Read `Handoffs/handoff-2026-09-24-band-advance-sweep-and-research.md`.
>
> Next task: research #8 — the email outbox. One row per send (`show_id`, kind, tier, to, subject, body, body_sha, status, attempts, `idem_key UNIQUE`), inserted in the same transaction that stamps the tier, so there's a durable record of what went out and a re-run can't double-send. Do the idempotency check in Flask before the webhook POST rather than in n8n — lower risk, no workflow edit. `send_failures` can become a view over it. Full spec in `Handoffs/band-advance-audit-2026-09-16/report-research.md` item 8.
>
> Also open and worth raising: the drink-ticket question. Splitting crew out of `performers` means a band with crew now gets fewer tickets than the same band got last month, while the form still promises tickets for performers and crew. Brian dismissed the question once — ask it again only with a recommendation attached, or just tell him which way it's going.
>
> Constraints that aren't obvious: everything reaches bands through Brian's email, never a phone call; staging fixtures must use `free_date()`; and running the pipeline by hand sends real band email.
