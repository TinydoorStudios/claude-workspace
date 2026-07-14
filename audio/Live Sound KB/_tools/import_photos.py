#!/usr/bin/env python3
"""
import_photos.py — drop-and-distribute mic photos into the KB.

You save product photos ONCE into a single folder, named by slug (the manifest
lists every slug). This copies each into its assets/mics/<slug>/ folder as the
full-size <slug>.jpg, builds the gallery thumbnail, and you publish. No per-mic
fiddling.

    # 1. Save images into ~/Downloads/mic-photos/ named <slug>.jpg (or .png/.jpeg/.webp)
    #    e.g. shure-sm57.jpg, audix-d6.png, sennheiser-md421.jpg
    # 2. Run:
    python3 import_photos.py
    # 3. Publish (Publish to Wiki.command)

Options:
    --src PATH     source folder (default ~/Downloads/mic-photos)
    --force        overwrite existing photos/thumbs

Slugs are the same ones in PHOTO-MANIFEST.md / mic_data.json.
"""
import os, argparse, shutil
from PIL import Image, ImageOps

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(KB, "Wiki", "assets", "mics")
EXTS = (".jpg", ".jpeg", ".png", ".webp")
TW, TH = 300, 220

def valid_slugs():
    return {d for d in os.listdir(ASSETS) if os.path.isdir(os.path.join(ASSETS, d))}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.expanduser("~/Downloads/mic-photos"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.src):
        raise SystemExit(f"source folder not found: {a.src}\n"
                         f"Make it and drop images named <slug>.jpg inside, then rerun.")
    slugs = valid_slugs()
    done, skipped, unknown = 0, 0, []
    for fn in sorted(os.listdir(a.src)):
        base, ext = os.path.splitext(fn)
        if ext.lower() not in EXTS:
            continue
        slug = base.strip().lower()
        if slug not in slugs:
            unknown.append(fn)
            continue
        dest_dir = os.path.join(ASSETS, slug)
        full = os.path.join(dest_dir, f"{slug}.jpg")
        thumb = os.path.join(dest_dir, f"{slug}-thumb.jpg")
        if os.path.exists(full) and not a.force:
            skipped += 1
            continue
        try:
            im = Image.open(os.path.join(a.src, fn)).convert("RGB")
            im.save(full, "JPEG", quality=90)
            ImageOps.fit(im, (TW, TH), Image.LANCZOS).save(thumb, "JPEG", quality=85)
            done += 1
            print(f"imported: {slug}")
        except Exception as e:
            print(f"skip {fn}: {e}")
    print(f"\ndone — {done} imported, {skipped} already present")
    if unknown:
        print("unrecognized filenames (name them <slug>.jpg — see PHOTO-MANIFEST.md):")
        for u in unknown:
            print("  ", u)

if __name__ == "__main__":
    main()
