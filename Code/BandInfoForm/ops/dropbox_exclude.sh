#!/bin/bash
# Sets the n8n VM's headless Dropbox client (~/dropbox.py) to sync ONLY the
# Nyquist cockpit + the real 3CDC venue folders the advance pipeline files
# into. Everything else at the Dropbox root (loose legacy files, FSQ/FSQ
# Archive/FSQ SPL, Production, 3CDC - BUDGETS, 3CDC - All Sites Folder, etc.)
# stays excluded from the VM — Brian's explicit call, 2026-09-12.
#
# Safe to re-run any time (e.g. a new top-level Dropbox item shows up): it
# reconciles the CURRENT exclude list against KEEP, excluding what should be
# excluded and un-excluding what should be kept, rather than assuming either
# starts from a blank slate. Live copy: ~/dropbox_exclude.sh on the VM
# (192.168.200.84). This file is the checked-in reference copy — redeploy by
# copying it over (see deploy_app.command's pattern) and running it there.
set -e
cd ~

KEEP=(
  "Nyquist"
  "3CDC Court Street"
  "3CDC Elm Street Plaza"
  "3CDC Fountain Square"
  "3CDC Imagination Alley"
  "3CDC Memorial Hall"
  "3CDC Washington Park"
  "3CDC Ziegler Park"
)

is_kept() {
  local base="$1"
  for k in "${KEEP[@]}"; do
    [ "$base" = "$k" ] && return 0
  done
  return 1
}

# TO_INCLUDE always runs against the full KEEP list directly (not derived from
# `find`) — a currently-excluded folder has NO local placeholder at all, so it
# can never show up in `find ~/Dropbox`. `exclude remove` on an already-synced
# or nonexistent-but-real path is a safe no-op either way.
TO_INCLUDE=()
for k in "${KEEP[@]}"; do
  TO_INCLUDE+=("$HOME/Dropbox/$k")
done

# TO_EXCLUDE only makes sense from `find`: anything that should be excluded
# and isn't already IS physically present locally (it hasn't been excluded
# yet), so this correctly catches new top-level items that show up over time.
TO_EXCLUDE=()
while IFS= read -r -d '' entry; do
  base="$(basename "$entry")"
  is_kept "$base" || TO_EXCLUDE+=("$entry")
done < <(find ~/Dropbox -mindepth 1 -maxdepth 1 -print0)

echo "Keeping synced: ${KEEP[*]}"
echo "Un-excluding ${#TO_INCLUDE[@]} keep-list item(s) (no-op for any already synced)."
python3 ~/dropbox.py exclude remove "${TO_INCLUDE[@]}"
echo "Excluding ${#TO_EXCLUDE[@]} other top-level item(s)."
if [ "${#TO_EXCLUDE[@]}" -gt 0 ]; then
  python3 ~/dropbox.py exclude add "${TO_EXCLUDE[@]}"
fi

echo "--- current exclude list ---"
python3 ~/dropbox.py exclude list
