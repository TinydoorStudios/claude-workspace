#!/usr/bin/env bash
#
# debloat_lenovo.sh — ADB debloater for the Lenovo Tab P11 / P11 Plus (TB-J616F)
#
# No root. Uses per-user package removal, which is reversible:
#   pm uninstall -k --user 0 <pkg>   -> app gone for user 0, APK still on /system
#   cmd package install-existing <pkg> -> brings it back
#
# Everything is dry-run until you pass --apply.
#
# Usage:
#   ./debloat_lenovo.sh --list                 dump what's actually on the tablet
#   ./debloat_lenovo.sh                        dry run (shows what WOULD go)
#   ./debloat_lenovo.sh --disable --apply      pass 1: disable, fully reversible
#   ./debloat_lenovo.sh --apply                pass 2: uninstall for user 0
#   ./debloat_lenovo.sh --restore <backup.txt> put everything back
#
# !! 2026-07-27 — THIS TABLET FACTORY RESET ITSELF !!
#
# A `--disable --apply` run over the then-default bloat+oem tiers wiped the
# device: boot_count reset, device_provisioned null, all accounts gone, all
# user-installed apps gone. Only com.android.nfc was still disabled afterward.
#
# com.lenovo.ue.device was protected and untouched, so this build has at least
# one MORE reset tripwire beyond the documented one. The culprit is somewhere in
# the 8 Lenovo-branded packages that run touched — most likely com.lenovo.lsf /
# com.lenovo.lsf.device (Service Framework) or com.motorola.demo (retail demo
# mode, whose whole job is wiping devices on a timer). Not narrowed down, and
# narrowing it down costs a factory reset per guess.
#
# Every Lenovo-branded package is therefore quarantined in the `risky` tier and
# is NOT run by default. Do not add it back without deciding the tablet is
# expendable.
#
# Tiers (default: safe,oem):
#   safe      Amazon Music. That's it. Nothing Lenovo-branded.
#   oem       MediaTek / ODM factory-test + logging leftovers
#   apps      preloaded Google/Microsoft apps — your call
#   optional  real tradeoffs (face unlock, Dolby, camera, desktop mode)
#   risky     Lenovo-branded — ONE OF THESE WIPED THE TABLET. See above.
#   unsure    Lenovo packages I can't identify. Also suspect. Not run.
#   --tiers safe,oem,apps
#
# Lists are tuned to Brian's actual TB-J616F_S240253_241016_ROW (Android 12,
# MediaTek) inventory from 2026-07-27, not a generic P11 list.
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/backups"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
ADB="${ADB:-adb}"

MODE="uninstall"      # uninstall | disable
APPLY=0
TIERS="safe,oem"
RESTORE_FILE=""
DO_LIST=0

# ---------------------------------------------------------------------------
# NEVER TOUCH. Removing anything here breaks a function, the tablet, or one of
# Brian's own apps.
#
# com.lenovo.ue.device is the big one — pulling it has triggered a full system
#   reset on P11-family tablets (UAD issue #713).
# com.tblenovo.launcher is THE home screen on this build. Removing it with no
#   replacement launcher installed leaves you staring at a black screen.
# com.lenovo.styluspen / com.lenovo.inputdevices drive the Precision Pen and
#   the keyboard folio.
# The com.mediatek.*ResOverlay* packages are runtime resource overlays — they
#   patch how Settings and SystemUI render. Removing them causes weird UI bugs.
# ---------------------------------------------------------------------------
PROTECTED=(
  # --- core Android ---
  com.android.systemui
  com.android.settings
  com.android.settings.intelligence
  com.android.providers.settings
  com.android.providers.media
  com.android.providers.downloads
  com.android.providers.contacts
  com.android.permissioncontroller
  com.android.packageinstaller
  com.android.certinstaller
  com.android.keychain
  com.android.shell
  com.android.bluetooth
  com.android.nfc
  com.android.se
  com.android.inputmethod.latin
  # --- Google core ---
  com.google.android.gms
  com.google.android.gsf
  com.google.android.packageinstaller
  com.google.android.permissioncontroller
  com.google.android.webview
  com.google.android.contactkeys
  com.google.android.inputmethod.latin
  com.android.vending
  # --- Lenovo core / this device ---
  com.lenovo.ota                                    # OTA updater
  com.lenovo.ue.device                              # removing = system reset
  com.lenovo.tab_p11_plus                           # device config overlay
  com.lenovo.launcher.provider
  com.lenovo.styluspen                              # Precision Pen
  com.lenovo.inputdevices                           # keyboard folio / pen input
  com.tblenovo.launcher                             # THE home screen
  com.tblenovo.setup                                # setup wizard
  com.tblenovo.wallpaper                            # launcher dependency
  com.tblenovo.landscapevision.lenovolandscapevision
  # --- MediaTek platform (overlays + location) ---
  com.mediatek
  com.mediatek.FrameworkResOverlayExt
  com.mediatek.MtkSettingsResOverlay
  com.mediatek.SettingsProviderResOverlay
  com.mediatek.frameworkresoverlay
  com.mediatek.systemuiresoverlay
  com.mediatek.systemuiwmshellresoverlay
  com.mediatek.cellbroadcastuiresoverlay
  com.mediatek.batterywarning
  com.mediatek.capctrl.service
  com.mediatek.gnss.nonframeworklbs
  com.mediatek.location.lppe.main
  # --- Brian's own installs, not bloat ---
  com.squareup
  com.peek.peekpro
  com.steadfastinnovation.android.projectpapyrus    # Squid
  com.microsoft.office.onenote
)

# ---------------------------------------------------------------------------
# TIER: safe — survived the 2026-07-27 reset investigation as non-Lenovo and
# non-system. This is a short list on purpose.
# ---------------------------------------------------------------------------
TIER_safe=(
  com.amazon.mp3               # Amazon Music
)

# ---------------------------------------------------------------------------
# TIER: risky — QUARANTINED 2026-07-27. One of these packages factory-reset the
# tablet when disabled. Not identified; identifying it costs one wipe per guess.
#
# Do not run this tier on a tablet you care about. If you ever do, run it ONE
# package at a time with --tiers is not enough granularity — edit this list down
# to a single entry, reboot, and use the device for a day between each.
# ---------------------------------------------------------------------------
TIER_risky=(
  com.lenovo.lsf                           # Lenovo Service Framework — account,
  com.lenovo.lsf.device                    # push, device-ID reporting. PRIME SUSPECT.
  com.motorola.demo                        # retail demo mode — exists to wipe
                                           # devices on a schedule. SUSPECT.
  android.autoinstalls.config.lenovo.p522  # preload auto-installer config
  com.lenovo.tbengine                      # Lenovo content/push engine
  com.tblenovo.center                      # "Lenovo Tab Center" promo hub
  com.tblenovo.lenovowhatsnew              # "What's New" ad screen
  com.lmsa.app.lmsapad                     # device-side agent for Lenovo's PC
                                           # Rescue & Smart Assistant tool
)

# ---------------------------------------------------------------------------
# TIER: oem — MediaTek / ODM factory-test and logging leftovers that shipped on
# the retail image by accident of the build process.
# ---------------------------------------------------------------------------
TIER_oem=(
  com.debug.loggerui           # MTK debug log capture UI
  com.longcheertel.midtest     # ODM factory line-test app
  com.mediatek.engineermode    # MTK engineer mode
  com.mediatek.lbs.em2.ui      # MTK location engineer-mode UI
  com.mediatek.duraspeed       # background-app killer — kills long-running apps
  com.mediatek.miravision.ui   # MTK display tuning UI
)

# ---------------------------------------------------------------------------
# TIER: apps — preloaded Google/Microsoft apps. NOT run by default; these are
# real apps, just ones you may not want on this tablet. Anything you kill here
# reinstalls from the Play Store in 30 seconds if you change your mind.
# ---------------------------------------------------------------------------
TIER_apps=(
  com.google.android.apps.magazines          # Google News
  com.google.android.apps.podcasts           # Google Podcasts (dead product)
  com.google.android.apps.fitness            # Google Fit
  com.google.ar.core                         # ARCore
  com.google.android.apps.chromecast.app     # Google Home
  com.google.android.apps.docs.editors.docs
  com.google.android.apps.docs.editors.sheets
  com.google.android.apps.docs.editors.slides
  com.microsoft.office.officehubrow          # Microsoft 365 hub (NOT OneNote)
)

# ---------------------------------------------------------------------------
# TIER: optional — each of these costs you a real feature. Read before running.
# ---------------------------------------------------------------------------
TIER_optional=(
  com.lenovo.tablet.lenovofacedetectprovider     # face unlock
  com.lenovo.tablet.lenovoqcomfacedetectprovider # Qualcomm face unlock — this is
                                                 # a MediaTek tablet, so it's dead
                                                 # weight either way
  com.tbsmart.levision                           # Lenovo Levision (face/eye-care)
  com.dolby.daxservice                           # Dolby Atmos processing engine
  com.dolby.daxappui2                            # Dolby settings UI
  com.tblenovo.soundrecorder                     # stock voice recorder
  com.lenovotab.camera                           # stock camera app
  com.tblenovo.desktoplauncher                   # desktop/PC mode
  com.lenovo.productivity.service                # desktop/PC mode backend
)

# ---------------------------------------------------------------------------
# TIER: unsure — Lenovo packages I could not identify with confidence. Disable
# these (--disable --apply), live with it a few days, and only then decide.
# ---------------------------------------------------------------------------
TIER_unsure=(
  com.lenovo.dsa
  com.lenovo.ocpl
  com.huaqin.lenovoprivacy     # Huaqin is the ODM that builds this tablet
)

# ---------------------------------------------------------------------------

usage() { awk 'NR>1 && /^#/ {sub(/^# ?/,""); print; next} NR>1 {exit}' "${BASH_SOURCE[0]}"; exit 0; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)    APPLY=1 ;;
    --disable)  MODE="disable" ;;
    --list)     DO_LIST=1 ;;
    --tiers)    TIERS="$2"; shift ;;
    --restore)  RESTORE_FILE="$2"; shift ;;
    -h|--help)  usage ;;
    *) echo "unknown option: $1"; exit 1 ;;
  esac
  shift
done

command -v "$ADB" >/dev/null || { echo "adb not found. brew install --cask android-platform-tools"; exit 1; }

echo "Waiting for device (USB debugging on, tablet unlocked, RSA prompt accepted)..."
"$ADB" wait-for-device

DEV_MODEL="$("$ADB" shell getprop ro.product.model | tr -d '\r')"
DEV_NAME="$("$ADB" shell getprop ro.product.device | tr -d '\r')"
DEV_REL="$("$ADB" shell getprop ro.build.version.release | tr -d '\r')"
DEV_BUILD="$("$ADB" shell getprop ro.build.display.id | tr -d '\r')"
echo "Device: $DEV_MODEL ($DEV_NAME) — Android $DEV_REL — $DEV_BUILD"
echo

mkdir -p "$BACKUP_DIR"

# --- current package inventory ----------------------------------------------
INSTALLED="$("$ADB" shell pm list packages -u | tr -d '\r' | sed 's/^package://' | sort)"
ENABLED="$("$ADB" shell pm list packages | tr -d '\r' | sed 's/^package://' | sort)"

# --- --restore ---------------------------------------------------------------
if [[ -n "$RESTORE_FILE" ]]; then
  [[ -f "$RESTORE_FILE" ]] || { echo "no such backup: $RESTORE_FILE"; exit 1; }
  echo "Restoring every package listed in $(basename "$RESTORE_FILE")..."
  n=0
  while read -r pkg; do
    [[ -z "$pkg" || "$pkg" == \#* ]] && continue
    "$ADB" shell cmd package install-existing "$pkg" >/dev/null 2>&1
    "$ADB" shell pm enable --user 0 "$pkg" >/dev/null 2>&1
    n=$((n+1))
  done < "$RESTORE_FILE"
  echo "Restore attempted on $n packages. Reboot the tablet."
  exit 0
fi

# --- always snapshot before anything else ------------------------------------
SNAP="$BACKUP_DIR/packages_${DEV_NAME:-device}_$STAMP.txt"
printf '%s\n' "$INSTALLED" > "$SNAP"
echo "Full package snapshot saved: ${SNAP/#$HOME/~}"

# --- --list ------------------------------------------------------------------
if [[ $DO_LIST -eq 1 ]]; then
  REVIEW="$BACKUP_DIR/review_${DEV_NAME:-device}_$STAMP.txt"
  {
    echo "# $DEV_MODEL / $DEV_NAME — Android $DEV_REL — $DEV_BUILD"
    echo "# Generated $STAMP"
    echo
    echo "## Third-party / user-installed (pm list packages -3)"
    "$ADB" shell pm list packages -3 | tr -d '\r' | sed 's/^package://' | sort
    echo
    echo "## Lenovo / ZUI system packages"
    printf '%s\n' "$INSTALLED" | grep -E '^(com\.(lenovo|zui|tblenovo|motorola))' || true
    echo
    echo "## Non-Google, non-AOSP system packages (review these by hand)"
    printf '%s\n' "$INSTALLED" | grep -vE '^(android|com\.android\.|com\.google\.|com\.qualcomm\.|com\.qti\.|org\.|vendor\.|com\.lenovo|com\.zui|com\.tblenovo)' || true
  } > "$REVIEW"
  echo "Review file: ${REVIEW/#$HOME/~}"
  echo
  echo "Send me that file and I'll tighten the lists to what your tablet actually ships."
  exit 0
fi

# --- build the target list ---------------------------------------------------
is_protected() { local p="$1"; for x in "${PROTECTED[@]}"; do [[ "$x" == "$p" ]] && return 0; done; return 1; }
is_installed() { grep -qxF "$1" <<< "$INSTALLED"; }

TARGETS=()
IFS=',' read -ra TIER_LIST <<< "$TIERS"
for t in "${TIER_LIST[@]}"; do
  t="$(echo "$t" | tr -d ' ')"
  varname="TIER_$t[@]"
  [[ -z "${!varname+x}" ]] && { echo "unknown tier: $t"; exit 1; }
  for pkg in "${!varname}"; do
    is_protected "$pkg" && { echo "  [protected, skipped] $pkg"; continue; }
    is_installed "$pkg" && TARGETS+=("$pkg")
  done
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "Nothing from tiers [$TIERS] is present on this device. Run --list."
  exit 0
fi

# de-dup
TARGETS=($(printf '%s\n' "${TARGETS[@]}" | sort -u))

PLAN="$BACKUP_DIR/removed_${DEV_NAME:-device}_$STAMP.txt"

echo
echo "Tiers: $TIERS"
echo "Mode : $MODE"
echo "Found ${#TARGETS[@]} package(s) present on the device:"
printf '  %s\n' "${TARGETS[@]}"
echo

if [[ $APPLY -eq 0 ]]; then
  printf '%s\n' "${TARGETS[@]}" > "$PLAN"
  echo "DRY RUN — nothing changed. Plan written to ${PLAN/#$HOME/~}"
  echo "Re-run with --disable --apply first (fully reversible), then --apply."
  exit 0
fi

# --- guard: the tiers that wiped the tablet once already ---------------------
if [[ ",$TIERS," == *,risky,* || ",$TIERS," == *,unsure,* ]]; then
  cat <<'WARN'

  ****************************************************************
  *  STOP. One of the packages in the risky/unsure tiers factory  *
  *  reset this tablet on 2026-07-27. It has not been identified. *
  *                                                              *
  *  Everything on the device will likely be wiped. Back up and   *
  *  sign out first. Disabling is NOT safer than uninstalling —   *
  *  the reset happened on a --disable run.                       *
  ****************************************************************

WARN
  printf 'Type WIPE to continue: '
  read -r confirm
  [[ "$confirm" == "WIPE" ]] || { echo "Aborted."; exit 1; }
fi

# --- execute -----------------------------------------------------------------
: > "$PLAN"
ok=0; fail=0
for pkg in "${TARGETS[@]}"; do
  if [[ "$MODE" == "disable" ]]; then
    out="$("$ADB" shell pm disable-user --user 0 "$pkg" 2>&1 | tr -d '\r')"
  else
    out="$("$ADB" shell pm uninstall -k --user 0 "$pkg" 2>&1 | tr -d '\r')"
  fi
  if [[ "$out" == *Success* || "$out" == *"new state: disabled-user"* ]]; then
    echo "  OK    $pkg"
    echo "$pkg" >> "$PLAN"
    ok=$((ok+1))
  else
    echo "  FAIL  $pkg  ($out)"
    fail=$((fail+1))
  fi
done

echo
echo "$ok changed, $fail failed."
echo "Undo list: ${PLAN/#$HOME/~}"
echo "To undo:  $0 --restore \"$PLAN\""
echo "Reboot the tablet, then use it normally for a day before doing a second pass."
