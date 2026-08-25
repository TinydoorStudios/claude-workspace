#!/usr/bin/env bash
# Rebuild the Cowork .skill packages from their live source dirs.
#
# Cowork runs FROZEN uploaded snapshots — editing audio/_skills/<name>/ does NOT
# update what Cowork runs until the .skill zip is rebuilt AND re-uploaded in Cowork
# settings. Forgetting the rebuild has silently shipped stale skills three times
# (stale 06-23/06-25 copies, a reverb-dropping build_packet.py, a month-stale
# show-deep-build found 2026-08-25). This script + the pre-commit hook that calls it
# keep the committed .skill in lockstep with source so that half can never drift again.
# The re-UPLOAD into Cowork is still a manual UI step — this only guarantees the
# artifact you upload is current.
#
# Usage:
#   build-packages.sh            rebuild all packages unconditionally
#   build-packages.sh --staged   rebuild only packages whose source is git-staged,
#                                 and `git add` the rebuilt zip (pre-commit hook mode)
#
# Only skills Cowork actually runs are packaged. show-wiki-push / tds-infrastructure /
# memory-consolidation do LAN/server/memory work and run in Claude Code (live symlink),
# so they need no snapshot.
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SKILLS_DIR="$ROOT/audio/_skills"
PACKAGED=(show-deep-build fable-parity)   # the Cowork-relevant skills, add here if that changes

MODE="${1:-all}"

rebuild() {
  local name="$1"
  local src="$SKILLS_DIR/$name"
  local out="$SKILLS_DIR/$name.skill"
  [ -d "$src" ] || { echo "skip $name (no source dir)"; return 0; }
  rm -f "$out"
  # zip from inside the dir so paths are relative (SKILL.md, references/..., scripts/...),
  # matching the layout Cowork expects; -X drops extra attrs, exclude dotfiles like .DS_Store
  ( cd "$src" && zip -r -X -q "$out" . -x '.*' -x '*/.*' )
  echo "rebuilt $name.skill"
}

staged_files() { git -C "$ROOT" diff --cached --name-only; }

if [ "$MODE" = "--staged" ]; then
  changed=0
  files="$(staged_files)"
  for name in "${PACKAGED[@]}"; do
    if printf '%s\n' "$files" | grep -q "^audio/_skills/$name/"; then
      rebuild "$name"
      git -C "$ROOT" add "audio/_skills/$name.skill"
      changed=1
    fi
  done
  [ "$changed" = 1 ] && echo "(.skill package(s) rebuilt and staged — remember to re-upload in Cowork)"
  exit 0
fi

for name in "${PACKAGED[@]}"; do rebuild "$name"; done
