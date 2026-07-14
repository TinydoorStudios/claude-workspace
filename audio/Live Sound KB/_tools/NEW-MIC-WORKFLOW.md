# NEW-MIC — the standard for "add a mic to the locker/KB"

This is the framework. Every time Brian says **"add a mic"** (or "put this mic in the
locker / in the KB"), run this exact flow. The output is always the same shape as the
Audio-Technica PRO 6L and DPA 4099 pages: a detailed spec page, a reference PDF, a
thumbnail on the Mic Library gallery, and a full-size photo on the page.

## The flow

1. **Research the specs.** Pull real numbers — type, polar pattern, frequency response,
   impedance, sensitivity, phantom/ribbon, connector, weight, what's in the box. Sources
   = manufacturer product page first, then reputable reviews. Never invent a spec; if a
   value can't be confirmed, leave it out and note it.

2. **Write the record.** Append one object to `mic_data.json` (schema below). Reuse the
   character/EQ-tendency and use-case language already in `Wiki/mic-library.md` so the KB
   stays consistent, then add the hard specs from step 1.

3. **Generate.** From `_tools/`:
   ```bash
   python3 mic_page_gen.py --data mic_data.json --slug <slug> --wire
   ```
   That writes `Wiki/mic-<slug>.md`, builds `assets/mics/<slug>/mic-<slug>.pdf`,
   creates the photo drop folder, and rebuilds the Locker Gallery + table links.

4. **Photo.** Put two files in `assets/mics/<slug>/`:
   - `<slug>.jpg` — full-size, shown on the page
   - `<slug>-thumb.jpg` — square-ish thumbnail for the gallery (≈300×220 crops well)
   Source is a manufacturer product shot (URL recorded in the record's
   `photo_source_url`). Note: image binaries can't be script-downloaded from the
   Cowork sandbox — Brian drops them in, or a browser step saves them. The page and
   gallery render the instant the files exist; until then they show a navy placeholder.
   `make_thumbs.py` will batch-generate the `-thumb.jpg` from any full-size `.jpg`.
   Fastest bulk path: save photos into one folder named `<slug>.jpg`, then
   `python3 import_photos.py` distributes them into the right asset folders and
   builds thumbnails in one shot (see PHOTO-MANIFEST.md for the slug list).

5. **Publish.** Run the publisher (double-click `_tools/Publish to Wiki.command`, or
   `kb-publish.sh`). Push → rsync assets → force Wiki.js sync → verify 200.

6. **Verify.** Open `https://kb.tinydoorstudios.com/mic-<slug>` and the PDF under
   `/assets/mics/<slug>/`. Confirm the gallery thumbnail links correctly.

## Record schema (`mic_data.json`)

```json
{
  "slug": "shure-sm57",                     // kebab-case, becomes /mic-<slug>
  "name": "Shure SM57",
  "category": "Dynamic",                    // Dynamic | Small Diaphragm Condenser |
                                            // Large Diaphragm Condenser | Ribbon |
                                            // Lavalier | DI
  "owned": true,                            // false = reference only (faded gallery ring)
  "status": "Owned — in locker",
  "tags": ["mic","dynamic","cardioid","shure","owned"],
  "description": "one-line, shows in Wiki.js listing + search",
  "summary": "one to two sentences",
  "sources": "Manufacturer product page; <review>",
  "photo_source_url": "https://...",        // where the product photo comes from
  "intro": "opening paragraph, house voice",
  "specs": { "Type": "Dynamic", "Polar pattern": "Cardioid",
             "Frequency response": "40 Hz – 15 kHz", "...": "..." },
  "sound": "sound + placement paragraph",
  "bestfit": ["Guitar cab — ...", "Snare — ..."],
  "notes": ["...", "..."],
  "comparable": [["Sennheiser MD421","Step up for toms"], ["...","..."]],
  "related": [["Mic Library","/mic-library"], ["DiGiCo Quantum 225","/console-digico-q225"]]
}
```

## Rules

- House voice (warm, direct, no AI tells — see `writing-rules.md`). Match PRO 6L / DPA 4099.
- Slugs are permanent — renaming one breaks its URL. Confirm before any rename.
- `owned:false` mics still get a page (they're EQ references), but the gallery ring is
  faded and status reads "Reference — not in locker."
- Ribbons: every spec table and notes block must carry the **NO 48V** warning.
- Re-running `--wire` is safe; the gallery block regenerates between its markers.
