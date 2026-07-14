#!/usr/bin/env python3
"""
make_thumbs.py — batch-generate gallery thumbnails from full-size mic photos.

For every assets/mics/<slug>/<slug>.jpg that lacks a matching <slug>-thumb.jpg
(or with --force), write a center-cropped ~300x220 thumbnail. Run after dropping
full-size product photos in, then publish.

    python3 make_thumbs.py            # only missing thumbs
    python3 make_thumbs.py --force    # rebuild all
"""
import os, argparse
from PIL import Image, ImageOps

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(KB, "Wiki", "assets", "mics")
TW, TH = 300, 220

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    made = 0
    for slug in sorted(os.listdir(ASSETS)):
        d = os.path.join(ASSETS, slug)
        if not os.path.isdir(d):
            continue
        full = os.path.join(d, f"{slug}.jpg")
        thumb = os.path.join(d, f"{slug}-thumb.jpg")
        if not os.path.exists(full):
            continue
        if os.path.exists(thumb) and not a.force:
            continue
        try:
            im = Image.open(full).convert("RGB")
            im = ImageOps.fit(im, (TW, TH), Image.LANCZOS)
            im.save(thumb, "JPEG", quality=85)
            made += 1
            print(f"thumb: {slug}")
        except Exception as e:
            print(f"skip {slug}: {e}")
    print(f"done — {made} thumbnail(s)")

if __name__ == "__main__":
    main()
