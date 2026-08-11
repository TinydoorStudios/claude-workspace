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

Step 3: Read the `*Last consolidation: YYYY-MM-DD*` line near the top of memory.md to know the watermark (how far back to look). If it's missing, fall back to the newest "Memory Consolidation — YYYY-MM-DD" entry in the current `memory-archive-YYYYHn.md`. If this is the very first run (neither exists), only report what you would change and stop — do not write anything — then wait for Brian to confirm before any future run applies changes.

Step 4: On every run after the first, write the changes directly (append/edit — never delete without replacement, per the SKILL.md safety rules) and finish with the two-part log in SKILL.md Phase 4: overwrite the one-line watermark at the top of memory.md, and append the full run summary to the current `memory-archive-YYYYHn.md` — NOT to memory.md's Session Notes. memory.md loads in full at every session start, so nothing routine goes in it.

Also enforce the size rule every run: memory.md keeps the current calendar month of session notes and stays under 30KB. Check the byte count; if it's over, roll the oldest entries into the archive until it isn't.

If you find nothing to consolidate, update the watermark line and stop — do not write a "nothing to consolidate" note anywhere, and don't manufacture busywork or make speculative edits.

Keep the completion notification brief: one or two sentences summarizing what changed, in Brian's usual concise/direct style — no corporate tone, no bullet-heavy recap.