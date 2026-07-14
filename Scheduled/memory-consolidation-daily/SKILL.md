---
name: memory-consolidation-daily
description: Daily memory consolidation pass over Brian Lloyd's audio-project memory (memory.md, active-projects.md, questions.md) — gathers signal from recent sessions, merges/resolves contradictions, prunes and re-indexes.
---

You are running a scheduled daily memory-consolidation pass for Brian Lloyd (live sound/recording engineer, Cincinnati). His full working folder is `~/Documents/Claude/audio/` (in Cowork this is the connected/mounted folder — read and write directly).

Do not do any show/EQ/production work in this run. This is purely a memory-hygiene pass.

Step 1: Read the process spec at `~/Documents/Claude/audio/_skills/memory-consolidation/SKILL.md` in full and follow it exactly — it defines all four phases (orient, gather signal, consolidate, prune & index), the file locations, the contradiction-resolution format, and the safety rules (never delete without replacement, dry-run-and-confirm-with-Brian on the very first-ever run only, log a one-line summary every run).

Step 2: Execute the four phases against:
- `~/Documents/Claude/audio/about-me/memory.md` (session history)
- `~/Documents/Claude/audio/Live Sound KB/Wiki/active-projects.md` (canonical project state)
- `~/Documents/Claude/audio/Live Sound KB/Wiki/questions.md` (open questions)
Use `list_sessions` / `read_transcript` for the gather-signal phase, best-effort — if those tools aren't available or don't reach far enough back, skip that step and rely on re-reading the memory files for staleness/contradictions instead; don't block the run on it.

Step 3: Find the last "Memory Consolidation — YYYY-MM-DD" entry in memory.md's Session Notes section to know the watermark (how far back to look). If this is the very first run (no such entry exists yet), only report what you would change and stop — do not write anything — then wait for Brian to confirm before any future run applies changes.

Step 4: On every run after the first, write the changes directly (append/edit — never delete without replacement, per the SKILL.md safety rules) and end by appending the one-line run summary to memory.md's Session Notes exactly in the format specified in the SKILL.md (date, scanned range, added/updated/archived counts, anything flagged to questions.md).

If you find nothing to consolidate, just log a one-line "nothing to consolidate" note and stop — don't manufacture busywork or make speculative edits.

Keep the completion notification brief: one or two sentences summarizing what changed, in Brian's usual concise/direct style — no corporate tone, no bullet-heavy recap.