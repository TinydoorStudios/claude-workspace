#!/bin/bash
# Import Mic Photos — copies product photos from a Downloads folder into the KB
# asset folders (full-size <slug>.jpg + downscaled <slug>-thumb.jpg) via macOS
# `sips` (no Python). Accepts friendly filenames (e.g. "D4", "Beta 27") and
# resolves them to the matching mic page. Logs to _tools/_import_photos_out.txt.

MICS="$HOME/Documents/Claude/audio/Live Sound KB/Wiki/assets/mics"
OUT="$HOME/Documents/Claude/audio/Live Sound KB/_tools/_import_photos_out.txt"
ALIASES="$HOME/Documents/Claude/audio/Live Sound KB/_tools/mic_aliases.txt"

# find the source folder (support a couple of names)
SRC=""
for cand in "$HOME/Downloads/mic downloads" "$HOME/Downloads/mic-photos" "$HOME/Downloads/mic-downloads"; do
  [ -d "$cand" ] && SRC="$cand" && break
done

resolve_slug() {  # $1 = normalized token -> echoes matching folder slug or nothing
  local t="$1"
  if [ -d "$MICS/$t" ]; then echo "$t"; return; fi
  # alias table (friendly shorthands like 57, b58, 421, v7x)
  if [ -f "$ALIASES" ]; then
    local hit
    hit="$(awk -F'\t' -v k="$t" 'tolower($1)==tolower(k){print $2; exit}' "$ALIASES")"
    if [ -n "$hit" ] && [ -d "$MICS/$hit" ]; then echo "$hit"; return; fi
  fi
  # last resort: unique folder ending in -token
  local matches=()
  for d in "$MICS"/*/; do
    local s="$(basename "$d")"
    if [ "$s" = "$t" ] || [[ "$s" == *"-$t" ]]; then matches+=("$s"); fi
  done
  [ "${#matches[@]}" -eq 1 ] && echo "${matches[0]}"
}

{
  echo "===== Import Mic Photos $(date) ====="
  if [ -z "$SRC" ]; then
    echo "! no source folder found in ~/Downloads (looked for 'mic downloads', 'mic-photos')."
    exit 1
  fi
  echo "source: $SRC"
  shopt -s nullglob nocaseglob
  n=0
  for f in "$SRC"/*.jpg "$SRC"/*.jpeg "$SRC"/*.png "$SRC"/*.webp "$SRC"/*.tiff "$SRC"/*.heic; do
    base="$(basename "$f")"
    token="$(echo "${base%.*}" | tr '[:upper:]' '[:lower:]' | tr ' _' '--')"
    slug="$(resolve_slug "$token")"
    if [ -z "$slug" ]; then
      echo "? no unique page match for '$base' (token '$token') — skipping. See PHOTO-MANIFEST.md."
      continue
    fi
    dest="$MICS/$slug"
    if sips -s format jpeg "$f" --out "$dest/$slug.jpg" >/dev/null 2>&1 \
       && sips -Z 500 -s format jpeg "$f" --out "$dest/$slug-thumb.jpg" >/dev/null 2>&1; then
      echo "OK  $base  ->  $slug"
      n=$((n+1))
    else
      echo "!   sips failed on $base"
    fi
  done
  echo "----- imported $n photo(s) -----"
  echo "Next: publish (Publish to Wiki.command)."
} 2>&1 | tee "$OUT"

echo ""
echo "Done. You can close this window."
