---
name: memory-consolidation
description: >
  Daily reflective pass over Brian's memory system — about-me/memory.md, KB active-projects.md,
  and Cowork auto-memory. Scans recent session activity for corrections/preferences/decisions,
  merges findings, resolves contradictions with dates, and prunes/re-indexes so memory stays
  under size limits and free of stale or duplicated entries. Runs automatically once a day via
  a scheduled task; can also be run on demand — Brian saying "run memory consolidation" or
  "consolidate memory" triggers it directly.
---

# Memory Consolidation

A daily reflective pass over what's been learned this session and recent ones. The goal: any
future session should be able to orient fast — active shows, open questions, standing
preferences, recent decisions — without re-asking or re-deriving.

Built 2026-07-06, informed by a public "dream" skill for Claude Code (JSONL transcript scan +
Stop-hook auto-trigger) and Brian's existing `consolidate-memory` skill. This version is built
for how Brian's memory actually works: canonical project state lives in the KB, not in a single
flat file, and there's no CLI hook to piggyback on — the trigger is a real Cowork scheduled task.

## Where memory lives (read this first, every run)

- `about-me/memory.md` — session history, decisions, resolved/open notes. **Not** project state.
  Canonical file: `~/Documents/Claude/about-me/memory.md`. The copies at `audio/about-me/` and
  `~/.claude/about-me/` are symlinks to it (re-unified 2026-07-14 after the audio copy forked a
  second time) — always resolves to the same file, but if a symlink ever breaks, fix the link;
  never write a second real memory.md.
- `about-me/memory-archive-YYYYHn.md` — rotated-out session notes (see the rolling window in
  Phase 4). Read-only history; nothing loads it at session start.
- `Live Sound KB/Wiki/active-projects.md` — canonical current project state. This is the file
  most consolidation work touches.
- `Live Sound KB/Wiki/questions.md` — open questions / gaps. Anything uncertain goes here, never
  guessed into an answer.
- `Live Sound KB/CHANGELOG.md` — dated log of KB content changes (newest entry at the top).
- `_system/IMPROVEMENTS.md` — dated log of workflow/structural changes to the project itself.
- Cowork auto-memory (the platform's own memory layer) — operational preferences/feedback:
  read what's there, but don't duplicate it into these files.

## Phase 1 — Orient

- Read `about-me/memory.md` and `Live Sound KB/Wiki/active-projects.md` in full.
- Skim `questions.md` and the tail of `CHANGELOG.md` for anything still open.
- Note: entries that look stale (relative dates, no anchor), obvious duplicates between
  `memory.md` and `active-projects.md`, and anything marked `[DONE]`/`[RESOLVED]` that could be
  trimmed or archived.

## Phase 2 — Gather signal

Before assuming memory.md is complete, check what's happened since the last consolidation that
hasn't been written down yet.

1. Read the `*Last consolidation: YYYY-MM-DD*` line near the top of `about-me/memory.md` — that's
   the watermark (see Phase 4). Missing or unreadable: fall back to the newest
   `### Memory Consolidation` entry in the current `memory-archive-YYYYHn.md`. First run ever:
   look back 7 days.
2. Call `list_sessions` to see recent Cowork sessions. For any session active since the
   watermark that this run can inspect, pull the transcript and scan for:
   - **Corrections** — Brian saying something was wrong, backwards, or not what he meant.
   - **Preferences/standing rules** — "always," "never," "from now on," "default to."
   - **Decisions** — a choice made and why (console picked, approach locked, rejected alternative).
   - **Recurring friction** — the same clarifying question coming up more than once (a sign it
     belongs in a reference doc, not just memory).
   This is best-effort — `list_sessions` won't always reach every session from every device, and
   that's fine. It's a supplement to Brian's own session-end recap, not the sole source.
3. For each finding, note the fact, the date, and whether it was explicit (high confidence) or
   inferred (medium — flag these, don't merge them in as if certain).

## Phase 3 — Consolidate

The delicate phase. Follow the rules memory.md and active-projects.md already use — this just
makes them explicit and consistent:

1. **Never duplicate.** Check both `memory.md` and `active-projects.md` before adding anything.
   Project state → `active-projects.md`. Session history/decisions/why → `memory.md`.
2. **Absolute dates only.** Convert "yesterday," "last week" to `YYYY-MM-DD` using the source
   session's date.
3. **Contradictions get resolved, not silently overwritten.** If a new finding conflicts with an
   existing entry: update the entry and append `(Updated YYYY-MM-DD, previously: <old value>)`
   rather than deleting the history. This matches the "never rewrite history" rule already in
   `memory.md`.
4. **Source attribution on anything new:** `(from session YYYY-MM-DD)` so a future read can tell
   a consolidated fact from something Brian typed directly into the file.
5. **Never delete without replacement.** An entry only goes away if it was superseded (newer
   entry written) or moved (to `_ARCHIVE/`-style status like `[DONE]`/`[RESOLVED]`, or into a KB
   article if it's durable knowledge rather than a log line).
6. Genuinely uncertain items — a contradiction that can't be resolved from context, a finding
   that's ambiguous — go to `questions.md` under the right section. Don't guess.

## Phase 4 — Prune & index, then log

- Keep `memory.md`'s "Session Notes" section chronological and don't let old resolved entries
  bloat it — items fully superseded by KB content can be trimmed to a one-line pointer.
- **Rolling window (tightened 2026-08-25): Session Notes keep a TRAILING ~2 weeks from today, and
  `memory.md` stays under 18KB.** Not the calendar month — the calendar rule sawtoothed the file
  up to the cap by month-end (it sat at 27.6KB of all-August notes on 2026-08-25, under the old
  30KB bar, so the janitor correctly did nothing while startup cost stayed high). A trailing
  window holds the size flat instead. Each run, move older entries to
  `about-me/memory-archive-YYYYHn.md` (one archive file per half-year; create the next one when
  the half rolls over; append, keep chronological order). If the file is still over 18KB after
  the window cut, keep cutting oldest-first until it isn't. Check the byte count every run — the
  old "roughly 30 days" wording was never enforced and the file reached 117KB (~29K tokens
  re-billed on every turn of every session) before the 2026-08-11 cleanup.
  Before an entry rotates out, confirm anything durable in it (standing rule, correction,
  infrastructure fact) was promoted to CLAUDE.md, the KB, or auto-memory — promote it now if
  not. memory.md is loaded at every session start; the archive never is, so the window is what
  keeps startup cost flat.
- **Auto-memory dedupe:** if a Cowork auto-memory entry restates what a CLAUDE.md file or the KB
  already carries in full, trim the auto-memory entry to a one-line pointer (or delete it) — a
  fact stated in two places is a contradiction waiting to happen. Same rule in reverse: don't
  copy auto-memory facts into these files.
- Confirm `active-projects.md` entries marked `[DONE]` actually have their paperwork/output filed
  where `NEW-SHOW.md`/`ROUTING.md` says it should be; flag mismatches to `questions.md` rather
  than moving files yourself (file moves are a stop-and-ask action per Brian's rules).
- End every run by logging in two places (changed 2026-08-11 — the old rule appended a full stub
  to `memory.md` every single day, and 30 of them had accumulated into 29.5KB of pure bookkeeping
  that loaded at every session start):
  1. **Overwrite** the watermark line near the top of `memory.md` — one line, never appended to:
     ```
     *Last consolidation: YYYY-MM-DD — log in memory-archive-YYYYHn.md*
     ```
     This is the watermark Phase 2 reads next time.
  2. Append the full run log to the current `memory-archive-YYYYHn.md`, not to `memory.md`:
     ```
     ### Memory Consolidation — YYYY-MM-DD
     - Scanned: [N sessions / M days back]
     - Added: X entries · Updated: Y (Z contradictions resolved) · Archived/trimmed: W
     - Flagged to questions.md: [list, or "none"]
     ```
  If a run found nothing, the watermark line is the only write — don't log an empty pass anywhere.

## Safety

- **First run:** do a dry run — list what you'd change, don't write anything — and confirm with
  Brian before applying. After that, daily runs proceed automatically; this is additive/editorial
  work (append, edit-in-place, or move-to-archive-status), not destructive.
- **Never touch files outside the memory system** (show packets, .ses files, KB articles other
  than the ones named above) during a consolidation run. If something there looks wrong, flag it
  to `questions.md` — don't fix it here.
- If a scheduled run finds nothing to change, log a one-line "nothing to consolidate" note and
  stop. Don't manufacture busywork.

## Why this instead of the generic "/dream" pattern

The public version this is modeled on scans Claude Code's local JSONL session files and
auto-triggers off a CLI Stop hook — neither of which exists in Cowork. This version uses Cowork's
own session-inspection tools for signal-gathering and a real scheduled task for the daily
trigger, and it targets Brian's actual two-tier memory (KB = canonical project state, memory.md
= history) instead of a single generic memory file. It also adds the contradiction-tracking
format and mandatory backup-before-first-run/dry-run habits that the generic version has but
Brian's existing `consolidate-memory` skill didn't.
