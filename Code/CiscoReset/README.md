# Catalyst 1200 / 1300 factory reset over USB-C console

Verified on a C1200 (2026-08-07) and a C1300 (2026-08-08). Same bootloader, same timing.

## Run it

```bash
python3 reset_catalyst.py 900
```

Arm it first, **then** pull power on the switch and plug it back in. The script idles until the
USB gadget console disappears, sets T0 when it re-enumerates, and fires:

| T+ | key | what it does |
|---|---|---|
| 4.0s | `Esc` | aborts autoboot, draws the Startup Menu |
| 6.5s | `2` | Restore Factory Defaults |
| 8.5s | `Y⏎` | confirms |

Then send **one** more Esc by hand to leave the menu and boot:

```bash
printf '\033' > /dev/cu.usbmodem11301
```

## The one rule

Send exactly one Esc at a time. The bootloader buffers console input — a stream of Esc means the
first aborts autoboot and the second is read as "exit", dropping you into a normal boot. Rate makes
no difference. This burned four attempts the first time.

Don't try to parse the console stream to drive the menu either; it drops bytes and interleaves
lines badly, so detection never fires inside the ~2s window. Drive on timing, log raw bytes.

## Proof the wipe took

In the boot output: banner reads `Unit factory default`, and `%SNMP-I-CDBITEMSNUM` reports **0**
running and **0** startup config items, followed by fresh SSH key and self-signed cert generation.

Login afterward is `cisco` / `cisco` with a forced password change.

## Dead ends

The recessed reset button never took across many attempts. Cisco FindIt doesn't discover this
series at all.
