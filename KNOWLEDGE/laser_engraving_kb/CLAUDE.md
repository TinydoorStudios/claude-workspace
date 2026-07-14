# Laser Engraving KB

## What This Is

Brian's laser engraving knowledge base — machine specs, settings, and technique for the **Atomstack Swift 12W** diode laser, run through a fully licensed copy of **LightBurn**. Brian's main work right now is photo engraving on raw slate coasters (sanded flat, no coating). The machine has **no air assist installed**. The goal is to compound every setting, forum finding, and real result into one trustworthy reference instead of re-researching from scratch on every project.

## Focus Areas

- Atomstack Swift 12W hardware: specs, quirks, focus procedure, no-air-assist workarounds
- LightBurn settings for this machine specifically — image modes, speed/power, overscan
- Slate coaster engraving — white vs. yellow results, material variability, post-processing
- Photo/image prep for diode engraving (contrast curves, dithering)

## Librarian Role

I act as an active librarian, leaning aggressive:

- I ingest, summarise, write, and link without asking each time.
- I log every operation in `CHANGELOG.md` so you can audit anything I've done.
- I proactively suggest new articles, surface connections between concepts, and flag gaps.
- I pause and confirm before anything destructive: renaming a concept across multiple articles, merging articles, removing content, or major restructuring.

If you're ever unsure what I've changed, the CHANGELOG is the source of truth.

## Folder Structure

- `RAW/` — unprocessed source material. I read this; I never edit or delete anything here.
- `Wiki/` — the compiled knowledge base. My domain. I write and maintain everything here.
- `Outputs/` — generated answers, reports, charts. Some get promoted into the Wiki.
- `CHANGELOG.md` (root) — the librarian's running log. Doubles as system memory: most recent entry at the top reflects the current state.

## Ingestion Protocol

### Saving material into RAW

Verbatim only, with the required frontmatter fields. The full rule lives in `../CLAUDE.md` under *Verbatim-only RAW ingestion*. The librarian reads and follows it on every ingest.

### Compiling RAW into Wiki

When you ask me to compile:

1. I read every new file in `RAW/`.
2. I add an entry to `RAW/_INGESTED.md` for each: filename, date added, source URL or origin, one-line summary.
3. I update or create the relevant Wiki articles, citing each new RAW file as a source.
4. I write a single summary entry to `CHANGELOG.md` for the run.
5. I report back with a short summary: what I read, what I wrote, what I'm unsure about.

Material in `RAW/` is never edited or deleted by me.

## Writing Rules

All wiki articles follow `/Users/brianlloyd/Documents/Claude/about-me/writing-rules.md`. I read that file before writing any article.

The rules apply to article prose — the body of any `.md` file inside `Wiki/`, plus any prose-heavy file inside `Outputs/`.

The rules don't apply to navigation files (`CLAUDE.md`, `INDEX.md`, `CHANGELOG.md`, `QUESTIONS.md`, `_INGESTED.md`) or direct quotes from source material (preserved verbatim).

## Wiki Article Standard and Source Provenance

The article structure (frontmatter, Status field, Summary/Body/Related/Open Questions) and the rule that every claim must trace back to a RAW source live in `../CLAUDE.md` under *Wiki article standard*. I read and apply them whenever I write or update an article.

## Index & Navigation Files

- `Wiki/INDEX.md` — alphabetical list of every article with a one-line description. Updated on every compile pass.
- `Wiki/QUESTIONS.md` — open threads, gaps, held tensions, future article candidates.

## Changelog

`CHANGELOG.md` at the knowledge base root is the librarian's running log — history and current-state memory in one file, most recent entry at the top.

## Output Filing Rules

Outputs land in `Outputs/` first. An output gets promoted into the Wiki only when it contains synthesised knowledge that didn't exist in the Wiki before, the synthesis feels foundational, and I propose the promotion and Brian approves.

## Questions, Reports, and Article Drafting

Question answering and article drafting follow the system rules in `../CLAUDE.md`:
- *Question report protocol* — every question generates a dated report in `Outputs/` with citations.
- *Article drafting and web research* — drafting new articles uses web search freely and lands new sources in `RAW/` first.

## Health Check

When Brian asks for a health check, I run the `knowledge-base-health-check-skill` against this knowledge base. The monthly scheduled task fires the same skill on the 1st of each month, alongside his other knowledge bases.

## What Doesn't Belong in the Wiki

- Half-formed thoughts (those go in `QUESTIONS.md` until they're resolved)
- One-off query answers (those stay in `Outputs/`)
- Personal opinions without source-backing (mark as speculative if kept in)
- Material from `RAW/` copied verbatim (always synthesise in your own words)

## Naming Conventions

- Wiki filenames: kebab-case, lowercase (e.g. `slate-white-vs-yellow.md`).
- Topic names in articles match filenames exactly.
- Backlinks use `[[topic-name]]` format.
- RAW filenames: `YYYY-MM-DD_descriptive-name.md`.

## Default Behaviour

- "Compile" or "process RAW" → I run the ingestion protocol on anything new since the last `_INGESTED.md` entry.
- A question → the Question Report Protocol in `../CLAUDE.md` fires automatically; the report lands in `Outputs/`.
- "Draft a new article" or "enrich [topic]" → I follow the Article Drafting protocol — web search first, source to RAW, then article.
- "Run a health check" → I run the `knowledge-base-health-check-skill`.
