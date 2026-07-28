# Lenovo Tab P11 Plus debloater (TB-J616F)

> ## ⚠ This tablet factory reset itself on 2026-07-27
>
> A `--disable --apply` run over the then-default tiers wiped the device. Every
> user-installed app, all accounts, all app data — gone. `com.lenovo.ue.device`
> was protected and never touched, so this build has **at least one more reset
> tripwire** that isn't the documented one.
>
> The culprit is one of the 8 Lenovo-branded packages that run touched. It has
> not been identified, and identifying it costs one factory reset per guess.
> Prime suspects: `com.lenovo.lsf` / `com.lenovo.lsf.device` (Service Framework)
> and `com.motorola.demo` (retail demo mode exists to wipe devices on a timer).
>
> All Lenovo-branded packages are now quarantined in the `risky` tier, which is
> not run by default and requires typing `WIPE` to proceed. **Disabling is not
> safer than uninstalling — the reset happened on a `--disable` run.**
>
> Honest assessment: the remaining upside here is seven packages of MediaTek
> factory-test junk. That is not worth a second wipe. Consider this tool done.

ADB-based, no root, reversible. `adb` is already installed on this Mac
(`/opt/homebrew/bin/adb`, from the `android-platform-tools` cask).

Lists are tuned to the actual device inventory taken 2026-07-27:
**TB-J616F, Android 12, build `TB-J616F_S240253_241016_ROW`, MediaTek** — not a
generic P11 list.

## One-time tablet setup

1. Settings → About tablet → tap **Build number** 7 times.
2. Settings → System → Developer options → **USB debugging** on.
3. Plug into the Mac, unlock, accept the RSA prompt, tick *Always allow*.
4. Confirm: `adb devices` shows a serial with `device` next to it.

## Run order

```bash
cd ~/Documents/Claude/Code/AndroidDebloat

./debloat_lenovo.sh                   # dry run — shows what would go
./debloat_lenovo.sh --disable --apply # pass 1: disable only (fully reversible)
# ...use the tablet for a day...
./debloat_lenovo.sh --apply           # pass 2: uninstall for user 0
```

## Tiers

| Tier | Default | What's in it |
|---|---|---|
| `safe` | yes | Amazon Music. That's the whole list. |
| `oem` | yes | MediaTek/ODM factory-test leftovers: debug logger, midtest, engineer mode, DuraSpeed, MiraVision |
| `apps` | no | Google News, Podcasts, Fit, ARCore, Home, Docs/Sheets/Slides, Microsoft 365 hub |
| `optional` | no | Face unlock, Levision, Dolby Atmos, stock camera, sound recorder, desktop/PC mode |
| `risky` | **no — wiped the tablet** | All Lenovo-branded: Service Framework, Motorola demo, Tab Center, What's New, tbengine, LMSA, preload config |
| `unsure` | no | `com.lenovo.dsa`, `com.lenovo.ocpl`, `com.huaqin.lenovoprivacy` — also Lenovo, also suspect |

```bash
./debloat_lenovo.sh --tiers safe,oem,apps
```

## Undo

Every run writes an undo list to `backups/removed_*.txt` and snapshots the full
package list to `backups/packages_*.txt`.

```bash
./debloat_lenovo.sh --restore backups/removed_TB-J616F_2026-07-27_175230.txt
```

Restore uses `cmd package install-existing`, which works because
`pm uninstall --user 0` never deletes the APK from `/system` — it only unlinks
it from user 0. A factory reset also brings everything back.

## What it refuses to touch

The `PROTECTED` array at the top of the script:

- **`com.lenovo.ue.device`** — removing it has triggered a full system reset on
  P11-family tablets ([UAD issue #713](https://github.com/0x192/universal-android-debloater/issues/713)).
- **`com.tblenovo.launcher`** — the home screen on this build. Remove it with no
  replacement launcher and you get a black screen.
- **`com.lenovo.styluspen`, `com.lenovo.inputdevices`** — Precision Pen and the
  keyboard folio.
- **`com.mediatek.*ResOverlay*`** — runtime resource overlays that patch how
  Settings and SystemUI render. Pulling them causes UI glitches.
- **`com.lenovo.ota`**, Play Services/Store, WebView, SystemUI, Settings.
- Brian's own installs: `com.squareup`, `com.peek.peekpro`,
  `com.steadfastinnovation.android.projectpapyrus` (Squid),
  `com.microsoft.office.onenote`.

## Notes

- Dolby (`com.dolby.daxservice`) is in `optional`, not `bloat`. It's system-wide
  playback DSP — killing it gets you flat output, which may be what you want on
  a tablet you listen critically on, but it also kills the speaker voicing the
  hardware was tuned around. Disable it first and listen before uninstalling.
- `com.mediatek.duraspeed` is worth killing regardless — it's an aggressive
  background-app reaper that terminates long-running apps.
- Removal is per-user. A major OTA can restore some packages — re-run after big
  updates.
