# I/O overview: what plugs into the Q225

## On the console

The Q225 rear panel carries 8 mic/line inputs and 8 line outputs, 2 AES/EBU inputs and 2 AES/EBU outputs (4 channels each way), 4 sets of MADI BNC I/O (up to 4 interfaces at 48kHz, 2 at 96kHz), USB audio (the "UB MADI" device the recording machine sees, up to 48 channels), MIDI in/thru/out, GPIs and GPOs, word clock I/O, 4 switched Ethernet ports, 2 DisplayPorts, and **two DMI slots**. Everything beyond that comes through the DMI cards.

![Q225 rear panel](/figures/gs-p008-1.png)
*Q225 rear panel, port by port — Quantum 2 Getting Started Guide, Issue A.*

## DMI cards

Two slots, not hot-swappable (power the console off to fit or remove a card; see [Fitting DMI cards](/hardware/09-fitting-dmi-cards)). The cards in play here:

| Card | Channels | What it does |
|---|---|---|
| [DMI-Dante 64@96](/hardware/02-dmi-dante-64-96) | 64 in / 64 out at 48 or 96 kHz | Dante network: DQ-Rack, A168D Stage, any Dante device. Auto SRC. Controls DQ/A168D preamps. |
| [DMI-KLANG](/hardware/06-dmi-klang) | 64 sends in, 16 stereo binaural mixes + stereo solo back | Immersive IEM mixing inside the console. |
| [DMI-Waves](/hardware/07-dmi-waves) | 64 in / 64 out at 48 or 96 kHz | SoundGrid: Waves plugins via SuperRack, or a SoundGrid recorder. |
| [DMI-MADI](/hardware/08-dmi-madi) | 64 in / 64 out (BNC or Cat5e) | Extra MADI port for a rack or a recorder. Manual SRC. |

The [DMI card compatibility sheet](/downloads/digico-dmi-card-compatibility-sheet.pdf) lists which cards work in which host.

## Stage racks

| Rack | I/O | Link |
|---|---|---|
| [DQ-Rack](/hardware/03-dq-rack) | 48 mic/line in, 24 out (4 switchable AES) | Dante, primary + secondary |
| [MQ-Rack](/hardware/04-mq-rack) | 48 mic/line in, 24 out (4 switchable AES) | MADI, main + aux BNC pairs |
| [A168D Stage](/hardware/05-a168d-stage) | 16 mic/line in, 8 out | Dante |

Gain, pad and phantom on all three are controlled from the console once the rack is conformed (Dante racks also need the routing made in Dante Controller).

## Which port is which in Audio I/O

Setup > Audio I/O lists a port per connection: *Local I/O*, the console MADI, *USB Audio*, and one per DMI card, plus any rack ports you add. See [Conform the I/O racks](/how-to/09-conform-the-io-racks).

![Setup > Audio I/O: one port per connection](/figures/q2-audio-io.png)
*Setup > Audio I/O: one port per connection — Quantum 2 offline software, V22.*

Venue-specific patching (which rack is on which card, what's on the USB audio port at Memo and FSQ) goes on the venue pages, to be added.
