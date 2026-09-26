import json
def B(b,g,f,q,t="BELL",deq=None): return {"b":b,"gain":g,"freq":f,"q":q,"type":t,"deq":deq}
GROUP = ("PIANO GROUP EQ (dial by hand, linked stereo; the patcher writes input EQ only): HPF 40 · B4 FLAT · B3 FLAT · "
         "B2 −3 @ 300 Hz Q2.0 · B1 −3 @ 125 Hz Q2.0. COMP (group): Purple | thr for 2–3 dB GR | ratio 2:1 | atk 30ms | rel 300ms.")
ch = []
ch.append(dict(ch=1,name="Piano Hi",instrument="Yamaha C3 grand, treble (RH)",mic="DPA 4099 CORE+ Extreme SPL",section="PIANO",
  phantom=True,ribbon=False,tour=False,stand="Clip",patch="Millennia HV-3D-8 ch 1 → R1 (line)",
  notes="P-clip on the plate around G5, just past the dampers, 25–30 cm over the strings, rear null up at the lid. 48V at the HV-3, not the stagebox; stagebox input LINE, console gain unity. Pan LEFT (audience view, matches the MK4 pair). PA + multitrack. "+GROUP,
  hpf=100,lpf=None,bands=[B(4,-2,10000,1.0),B(3,-3,2500,2.0,deq={"thr":-20,"atk_ms":5,"rel_ms":150}),B(2,-3,500,1.5)],
  mic_notes="Near-flat supercardioid: 80 Hz–17 kHz ±3 dB with a +2 dB soft boost at 10–12 kHz (SOS). R16 lanes: Hi owns the right hand, hammer and top; Lo owns everything under ~200. Mono-sum with ch 2 at line check before touching EQ; flip one if the centre thins.",
  eq_summary="This is the half of the piano Phoebe's voice lives on top of. The −2 at 10k takes back the capsule's own +2 so a bright C3 reads as the warm Tapestry piano, not a classical sparkle. The dynamic −3 at 2.5k only bites when she digs in or the lid throws her wedge and vocal back into the mic, which is where this mic hears them most. −3 at 500 clears the treble-side honk. HPF 100 leaves the left hand to ch 2. Room treatment (125, 300) sits once on the piano group, not twice on the channels."))
ch.append(dict(ch=2,name="Piano Lo",instrument="Yamaha C3 grand, bass (LH)",mic="DPA 4099 CORE+ Extreme SPL",section="PIANO",
  phantom=True,ribbon=False,tour=False,stand="Clip",patch="Millennia HV-3D-8 ch 2 → R2 (line)",
  notes="P-clip over C2–G2, a third of the way down the strings past the dampers, same height and angle as ch 1, at least 30 cm from it. 48V at the HV-3; stagebox LINE, gain unity. Pan RIGHT. PA + multitrack. See ch 1 for the piano group EQ.",
  hpf=50,lpf=10000,bands=[B(2,-4,250,1.5)],
  mic_notes="Same capsule as ch 1. Lo owns the bottom; the LPF 10k hands the top to ch 1 so the hammer and vocal bleed aren't counted twice. At 25–30 cm proximity is barely in play (it only rises inside 20 cm, SOS).",
  eq_summary="Carole King's left hand is the bass player in this show: rolling octaves under 'I Feel the Earth Move' and 'It's Too Late'. So the HPF stays at 50 and nothing gets boosted. The one cut is −4 at 250, the wound-string box that stacks on Memo's 250–315 mode. The group's −3 at 125 and −3 at 300 do the room work."))
ch.append(dict(ch=3,name="Piano Mon",instrument="Yamaha C3, plate hole H2",mic="Shure SM57",section="PIANO",
  phantom=False,ribbon=False,tour=False,stand="—",patch="R3",
  notes="WEDGES ONLY: Mix 1 (Phoebe) and Mix 2 (Dan) as needed. Unassign from LR. Pointing down into plate hole H2 (see C3 Placement PDF); try H3 if the treble is thin. No 48V.",
  hpf=160,lpf=12000,bands=[B(2,-4,500,1.5),B(1,-5,250,1.5)],
  mic_notes="Shure: presence rise around 4–6 kHz (~+5 dB) and 6–10 dB of proximity below 100 Hz up close. Down in the plate hole the soundboard makes it boomy. Leave the top alone; the capsule already gives the hammers.",
  eq_summary="This channel only has to give Phoebe pitch and time in her wedges without ever feeding back through the DPAs. HPF 160 and −5 at 250 remove the soundboard boom and the hardwood stage's build-up. −4 at 500 is the honk a dynamic makes inside a grand. Nothing is added at 4–6k because the 57 already carries its own +5 there."))
ch.append(dict(ch=4,name="Dan Gtr",instrument="Acoustic guitar (Dan, fingerstyle)",mic="Rupert Neve Designs RNDI",section="GUITAR",
  phantom=False,ribbon=False,tour=True,stand="DI",patch="2-ch sub 1",
  notes="RNDI on INSTRUMENT. Guitar and pickup are Dan's; pickup type confirm at load-in (assumed undersaddle piezo).",
  hpf=80,lpf=15000,bands=[B(4,-3,4000,2.0),B(3,-5,1700,2.0),B(2,-4,250,1.5)],
  mic_notes="The RNDI is ±0.25 dB from 28 Hz to 60 kHz (RND/SOS), so the curve is all pickup. Assumed piezo. If it turns out to be a mic or blend system, halve the 1.7k cut. COMP: Blue | in | thr for 3–4 dB GR | ratio 3:1 | atk 15ms | rel 150ms. A Neve-style comp rounds the piezo quack peaks (Gearspace piezo thread), and the 15 ms attack lets the pick transient through.",
  eq_summary="In Dan's half of the show this guitar is the whole band. Taylor's alternating thumb carries the bass line, so the HPF sits at 80, not the 120 you'd use in a band. The primary cut is −5 at 1.7k, the piezo quack (R13). −3 at 4k removes the zing, and −4 at 250 clears the box that Memo's 250–315 would otherwise make worse."))
ch.append(dict(ch=5,name="Stomp",instrument="Stomp box (Dan's foot)",mic="Rupert Neve Designs RNDI",section="DRUMS",
  phantom=False,ribbon=False,tour=True,stand="DI",patch="2-ch sub 2",
  notes="RNDI on INSTRUMENT. Dan's stomp box, piezo assumed, confirm at load-in. Dial the HPF at 24 dB/oct.",
  hpf=50,lpf=5000,bands=[B(3,-5,350,1.5),B(2,-4,130,3.0),B(1,3,85,2.5)],
  mic_notes="The RNDI is flat, so the piezo is the whole voice. Piezo stomp boxes lack real thump and read as cardboard at 300–400 (AGF piezo-stomp thread; Kopf). GATE: Gate | in | thr just above foot-rest noise | atk 1ms | hold 60ms | rel 150ms | range=20. That keeps shuffling and floor handling out of the sub region between hits.",
  eq_summary="The only kick in the show, and it should be felt, not heard. The +3 at 85 (Q 2.5) is the one boost, placed in the gap between Memo's 63 and 125 modes. The piezo's documented lack of low thump clears it under R15. −4 at 130 (Q 3) keeps the 125 mode from blooming. −5 at 350 removes the cardboard. The LPF at 5k takes off the piezo click so nobody hears a clacky box. If the room still booms at 63, slope the HPF steeper rather than cutting more."))
voc_comp = "COMP: Purple | in | thr for 3–5 dB GR | ratio 3:1 | atk 10ms | rel 200ms."
ch.append(dict(ch=6,name="Dan",instrument="Male lead vocal (James Taylor role)",mic="Wireless 1 (Shure Beta 58A)",section="VOCALS",
  phantom=False,ribbon=False,tour=False,stand="—",patch="Wireless 1",
  notes="House Wireless 1, multed to fader 41. Mix 2.",
  hpf=90,lpf=14000,bands=[B(4,-3,4500,2.0),B(3,-4,500,1.8),B(2,-3,250,2.0),{"b":1,"gain":None,"type":"FLAT"}],
  mic_notes="Shure: rise above 3k with peaks near 4k and 10k, lows rolled off for proximity. "+voc_comp+" Optical because a soft crooner wants smoothing, not grab.",
  eq_summary="Dan sings like Taylor, soft and close. His warmth is in 200–350, so this curve protects it. The male slot is HPF 90, the lowest of the three vocals. −4 at 500 is his box lane, deliberately different from Phoebe's 700 on ch 8 so duets don't share a notch. −3 at 250 is only there because Memo's 250–315 mode doubles it. −3 at 4.5k trims the Beta's presence peak, which goes steely on a quiet voice with the gain up. B1 is written FLAT so the wireless template curve doesn't leak in. Cuts only (R9)."))
ch.append(dict(ch=7,name="Phoebe Pno",instrument="Female lead vocal at piano (Carole King role)",mic="Neumann KMS 105",section="VOCALS",
  phantom=True,ribbon=False,tour=False,stand="Boom",patch="R4",
  notes="Input list said 'KSM105'; Brian confirmed Neumann KMS 105. 48V. Boom over the C3 keyboard. Mix 1.",
  hpf=120,lpf=16000,bands=[B(4,-4,8000,3.0,deq={"thr":-20,"atk_ms":2,"rel_ms":100}),B(3,-4,1600,2.0),B(2,-3,315,2.0),{"b":1,"gain":None,"type":"FLAT"}],
  mic_notes="Flat 500 Hz–7 kHz with about +5 dB at 12 kHz (RecordingHacks, higherhz); internal HPF −3 dB at 120 Hz. "+voc_comp+" Gentle, because breathiness is her sound.",
  eq_summary="Reviews describe Phoebe as breathy and light, so the KMS's 12k air stays: it carries her. Sibilance only gets a dynamic −4 at 8k when it's actually there. −4 at 1.6k is the nasal band on this capsule (KB). −3 at 315 does double duty: Memo's mode, and the piano's low-mids bouncing off the open lid into her mic. The HPF at 120 slots her above Dan (90) and matches the capsule's own roll-off. Cuts only."))
ch.append(dict(ch=8,name="Phoebe DS",instrument="Female lead vocal, standing downstage",mic="Wireless 2 (Shure Beta 58A)",section="VOCALS",
  phantom=False,ribbon=False,tour=False,stand="—",patch="Wireless 2",
  notes="House Wireless 2, multed to fader 42. Mix 1 (her wedges travel with her or add a DS wedge; confirm at load-in).",
  hpf=120,lpf=15000,bands=[B(4,-4,4000,2.0),B(3,-3,1600,2.0),B(2,-3,700,1.8),{"b":1,"gain":None,"type":"FLAT"}],
  mic_notes="Same Beta 58A data as ch 6: peaks near 4k and 10k. "+voc_comp,
  eq_summary="Same singer as ch 7 on a different capsule. The goal is for her to sound like one voice when she walks off the piano. The KMS has air on top and a flat 4k; the Beta 58A peaks at 4k, so this curve trims −4 at 4k and leaves 10k for the breath. −3 at 1.6k matches her nasal cut on ch 7. −3 at 700 is the Beta's box, kept away from Dan's 500 on ch 6. HPF 120, same as ch 7. Cuts only."))
rec = "RECORD ONLY: unassign from LR and all mixes; multitrack pre-EQ. MK4 ORTF bar at the bend, 17 cm / 110°, 15–20 cm inside the rim under the lid edge, 30–40 cm over the strings (C3 Placement PDF). 48V at the HV-3; stagebox LINE, gain unity."
for c,n,inst,side,port in ((13,"Pno Rec Hi","Yamaha C3 record pair, treble side (L)","L","ch 3 → R5"),(14,"Pno Rec Lo","Yamaha C3 record pair, bass side (R)","R","ch 4 → R6")):
  ch.append(dict(ch=c,name=n,instrument=inst,mic="Schoeps CMC6 + MK4",section="PIANO",phantom=True,ribbon=False,tour=False,stand="Boom",
    patch=f"Millennia HV-3D-8 {port} (line)",notes=rec+f" Pan {side} (audience view, highs left).",hpf=30,lpf=None,
    bands=[{"b":i,"gain":None,"type":"FLAT"} for i in (4,3,2,1)],
    mic_notes="Schoeps: flat with a slight rise around 10 kHz (~+2 dB) to offset room HF loss; very consistent off-axis. Blended with ch 1/2 in post. Time-align by ear; the pair sits within about 1 ms of the DPAs.",
    eq_summary="Record-only. The multitrack takes it pre-EQ, so any EQ here would only colour a solo check. HPF 30 for rumble and nothing else. Its job in post is the natural whole-instrument piano under the close DPAs."))
wl = [(41,"Dan W1","Wireless 1 (Shure Beta 58A)",6),(42,"Phoebe W2","Wireless 2 (Shure Beta 58A)",8)]
for c,n,m,src in wl:
  s=[x for x in ch if x["ch"]==src][0]
  ch.append(dict(ch=c,name=n,instrument=s["instrument"]+" (receiver home fader)",mic=m,section="VOCALS",phantom=False,ribbon=False,tour=False,stand="—",
    patch=s["patch"],notes=f"Receiver home fader, multed to ch {src}. Same curve; ride the digital trim here. Keep it OUT of LR (ch {src} carries the PA) unless ch {src} is lost.",
    hpf=s["hpf"],lpf=s["lpf"],bands=s["bands"],mic_notes=f"Mult of ch {src}, same capsule notes.",eq_summary=f"Identical to ch {src} so a swap mid-show is seamless."))
crowd=[(57,"Above Stage","Line Audio OM1 (pair)",80,None,[B(3,-3,800,1.5),B(2,-6,315,2.0),B(1,-5,200,2.0)],"Flown 18' above stage, 12' apart."),
       (58,"Floor Crowd","Deity S-Mic 2 (pair)",100,16000,[B(4,-3,2400,1.8),B(2,-5,315,2.0),B(1,-5,200,2.0)],"Under the main-floor PA, aimed into the audience."),
       (59,"Balcony Crwd","Line Audio CM4 (pair)",120,14000,[B(4,-4,400,1.5),B(3,-5,315,2.0),B(2,-6,200,2.0),B(1,-5,63,2.5)],"Balcony, rear-facing ORTF, 34' from the Deity pair.")]
for c,n,m,h,l,b,where in crowd:
  ch.append(dict(ch=c,name=n,instrument="Memo crowd rig",mic=m,section="AMBIENT",phantom=True,ribbon=False,tour=False,stand="—",patch="House crowd rig",
    notes=where+" Fixed Memo crowd EQ from the KB (R35). Record; not in LR.",hpf=h,lpf=l,bands=b,
    mic_notes="Fixed house rig. EQ is locked in venue-memorial-hall, not re-derived.",eq_summary="KB crowd curve as written: it treats Memo's 200/315 build-up in the room air. Unchanged show to show."))
units=[
 dict(ch="1/2",source="C3 piano (Hi/Lo)",mic="DPA 4099 CORE+ Extreme SPL",finding="80 Hz–17 kHz ±3 dB at 20 cm with a +2 dB soft boost at 10–12 kHz; proximity rises inside 20 cm",
  sources="Sound On Sound, DPA 4060 & 4099 Core+ review; SOS 'Miking Up A Piano Concert With DPA'; Gearspace pair-vs-bus EQ thread",verdict="AGREE",
  trace=dict(base="flat capsule; box 250 on Lo (−4), honk 500 on Hi (−3)",equip="C3 bright top + capsule +2 @ 10–12k → Hi −2 @ 10k",genre="70s singer-songwriter piano = warm, LH kept: Lo HPF 50, no boosts",artist="Phoebe's vocal/wedge off the lid → Hi dynamic −3 @ 2.5k",venue="Memo 125/300 moved to the piano group (−3/−3), not doubled on channels")),
 dict(ch="3",source="C3 plate hole (wedges)",mic="Shure SM57",finding="Presence rise ~+5 dB around 4–6 kHz; proximity +6–10 dB below 100 Hz up close",
  sources="Shure SM57 user guide; ProSoundWeb piano-miking articles (cut ~250 for boom)",verdict="THIN",
  trace=dict(base="boom from soundboard proximity → −5 @ 250",equip="inside a grand = honk → −4 @ 500",genre="wedge intelligibility, no tone work: HPF 160",artist="Phoebe needs pitch/time only — no top added",venue="hardwood stage build-up covered by the 250 cut; no change beyond")),
 dict(ch="4",source="Acoustic guitar DI",mic="Rupert Neve Designs RNDI",finding="RNDI ±0.25 dB 28 Hz–60 kHz; piezo quack is the fix, notch it",
  sources="Sound On Sound RNDI review; Rupert Neve Designs spec; Gearspace 'EQ'ing piezo pickups'",verdict="AGREE",
  trace=dict(base="piezo quack −5 @ 1.7k, zing −3 @ 4k",equip="pickup unknown, piezo assumed; halve 1.7k if a mic/blend system",genre="acoustic folk (R13): quack is the primary cut",artist="Taylor alternating-thumb bass → HPF 80, not 120",venue="Memo 250–315 → −4 @ 250")),
 dict(ch="5",source="Stomp box DI",mic="Rupert Neve Designs RNDI",finding="Piezo stomp boxes lack deep thump; cardboard box at 300–400 Hz; weight 60–100 Hz",
  sources="Acoustic Guitar Forum piezo stomp-box thread; Kopf Percussion ToeKicker notes; RND spec",verdict="THIN",
  trace=dict(base="−5 @ 350 cardboard",equip="piezo thin lows → +3 @ 85 Q2.5 (R15 cleared)",genre="folk pulse felt, not heard → LPF 5k",artist="Dan's quarter-note pulse on up-tempo JT tunes only",venue="Memo 63/125: boost placed between modes, −4 @ 130 Q3, HPF 50 steep")),
 dict(ch="6",source="Dan vocal",mic="Shure Beta 58A (Wireless 1)",finding="Rise above 3 kHz with peaks near 4 kHz and 10 kHz; bass rolled off for proximity",
  sources="Shure Beta 58A spec sheet; Gearspace 'Fitting baritone vocals'",verdict="AGREE",
  trace=dict(base="trim capsule 4k peak −3 @ 4.5k; box −4 @ 500",equip="house wireless — template curve overridden, B1 FLAT",genre="soft singer-songwriter: warmth 200–350 protected",artist="JT baritone, close and quiet → HPF 90",venue="Memo 250 → −3 @ 250")),
 dict(ch="7",source="Phoebe vocal at piano",mic="Neumann KMS 105",finding="Flat 500 Hz–7 kHz, about +5 dB at 12 kHz; internal HPF −3 dB at 120 Hz",
  sources="RecordingHacks KMS 105; higherhz KMS 105 review",verdict="AGREE",
  trace=dict(base="nasal −4 @ 1.6k; 12k air kept",equip="none notated — no change",genre="cuts only; air is part of the style",artist="breathy voice (BroadwayWorld) → sibilance only dynamic −4 @ 8k",venue="Memo 315 + lid bleed → −3 @ 315")),
 dict(ch="8",source="Phoebe vocal downstage",mic="Shure Beta 58A (Wireless 2)",finding="Peaks near 4 kHz and 10 kHz (same Shure data as ch 6)",
  sources="Shure Beta 58A spec sheet",verdict="AGREE",
  trace=dict(base="4k peak −4 @ 4k; box −3 @ 700",equip="house wireless — B1 FLAT",genre="cuts only",artist="match her KMS tone: nasal −3 @ 1.6k, HPF 120",venue="no change (no band below 400 needed)")),
 dict(ch="13/14",source="C3 record pair",mic="Schoeps CMC6 + MK4",finding="Flat with a slight rise around 10 kHz (about +2 dB); consistent off-axis",
  sources="Schoeps MK 4 product page",verdict="AGREE",
  trace=dict(base="flat, record-only",equip="HV-3 transparent — no change",genre="no change",artist="no change",venue="no change (multitrack pre-EQ); HPF 30 rumble only")),
]
reverbs=[
 dict(role="vocal",preset="Chambers 1 / #17 Sunset Chamber",settings="Decay 1.3s (factory 2.15s) · PreDelay 25ms · VLF −20dB (factory) · E/L Max Early · Late −12dB · Late Rolloff 6kHz",
  plugin_eq="Master Filter LC 200 Hz on the return; Ducker Reverb mode, thr −22dB",why="The KB's first pick for an acoustic lead vocal, and the warm, era-right sound for 'You've Got a Friend' and 'Fire and Rain'. Decay pulled about 40% because Memo supplies 1.6 s of its own."),
 dict(role="vocal",preset="Chambers 1 / #10 Vocal Chamber",settings="Decay 1.0s (factory 1.60s) · PreDelay 20ms · VLF −18dB (from −10dB factory) · E/L Max Early · Late −14dB · Late Rolloff 7kHz",
  plugin_eq="LC 200 Hz; Ducker Reverb mode thr −22dB",why="Tighter and more present, for the up-tempo tunes ('I Feel the Earth Move', 'Country Road') where Sunset would blur the words."),
 dict(role="vocal",preset="CLA Epic — Slap → Plate (custom, no factory anchor)",settings="Slap: VSO 15 IPS (≈ 110–120 ms, EQ curve loads with the speed) · Feedback 0% · Mod off · Out + route to Plate A at −10 dB. Plate: Pre-delay 30 ms · RT 1.2 s · RT Low ×0.8 · RT High ×0.9. HP 200 Hz / LP 8 kHz on both. Mono-to-Stereo component, Wet 100%.",
  plugin_eq="Processor HP/LP as listed; no ducker in Epic, so put a light sidechain duck on the return from the vocal groups if needed",why="1970s records put a tape slap on the JT vocal. This gives Dan that sound, and the Plate adds the record sheen without the room's length. Use it on Dan's numbers, with Sunset Chamber for Phoebe's."),
 dict(role="instrument",preset="Rooms 1 / #10 Large Wooden",settings="Decay 0.75s (factory 1.20s) · PreDelay 10ms · VLF −15dB · E/L Max Early · Late −16dB · Late Rolloff 7kHz",
  plugin_eq="LC 150 Hz on the return",why="The KB pick for acoustic guitar and folk instruments. It gives the DI'd guitar the air a mic would have picked up, short enough to keep the fingerpicking articulate."),
 dict(role="instrument",preset="Halls 1 / #32 Piano Hall",settings="Decay 1.2s (factory 2.00s) · PreDelay 24ms (factory) · VLF −18dB (from −8dB factory) · E/L Max Early · Late −14dB · Late Rolloff 6kHz",
  plugin_eq="LC 200 Hz; stereo send from the piano group",why="The close DPAs hear almost no room. Piano Hall puts the C3 back in the hall at a low send, with VLF cut hard so the left hand doesn't stack on Memo's 125."),
 dict(role="general",preset="CLA Epic — Throw (custom, no factory anchor)",settings="Throw: Tap 1 375 ms / Tap 2 500 ms (fixed ms until a tempo host exists) · Feedback 25% · Offset 10% · Trigger ON · route Out + Hall C at −12 dB. Hall: Pre-delay 40 ms · RT 1.8 s · RT Low ×0.7 · RT High ×0.8. HP 250 Hz / LP 6 kHz.",
  plugin_eq="HP/LP on the Throw processor; Trigger fires only on held button",why="Word throws on the last line of a chorus ('you've got a friend'). Trigger means nothing gets delayed unless you ask for it, which keeps a soft duo clean."),
]
spec=dict(venue="memo",venue_label="Memorial Hall",console_label="DiGiCo Quantum 225",show_name="The Carole King and James Taylor Story",
 artist="The Carole King & James Taylor Story (Phoebe Katis, Dan Clews)",genre="1970s singer-songwriter folk-pop (acoustic duo)",
 show_date="2026-09-28",foh_engineer="Brian Lloyd",mon_engineer="Brian Lloyd (wedges from FOH)",rev="Rev 1.0 Deep Think",app_version="deep-think-1.0",
 artist_profile="Phoebe Katis (piano, vocals) and Dan Clews (fingerstyle acoustic, vocals) have toured this 'show-umentary' for ten years, framed around King and Taylor's 1970 Troubadour sets. The set is the hits: Fire and Rain, Sweet Baby James, I Feel the Earth Move, Natural Woman, You've Got a Friend. Reviews call Phoebe 'breathy and formal' beside King's chest voice, and say Dan channels Taylor's soft baritone and picking convincingly. For the mix: two quiet voices, a piano that is the whole band in her half, a guitar that is the whole band in his. Nothing is loud, so gain before feedback and bleed off the open lid drive every choice.",
 room_context="Memo, 556 seats, RT60 about 1.6 s. The 125 and 250–315 modes are treated once, on the piano group and the vocal low-mids. The room supplies the long tail, so every reverb decay is pulled 30–40%.",
 style_note="Two nights, 09-28 and 09-30. Two voices, one C3, one guitar. Keep it warm, keep it dry-ish, let the room sing.",
 changes=["Ch 7 mic: input list 'KSM105' → Neumann KMS 105 (Brian confirmed).",
  "Ch 13/14 renamed Pno Rec Hi / Pno Rec Lo; the ORTF pair runs highs left from the bend, so the piano group pans audience view (Hi left) to match.",
  "Piano EQ split: per-mic correction on ch 1/2, Memo room EQ + comp on the linked piano group (hand-dialed, documented on ch 1).",
  "Ch 6/8 on house Wireless 1/2, multed to faders 41/42; wireless template curve overridden, B1 written FLAT.",
  "Reverbs: 7th Heaven + CLA Epic only (new Memo standard, Brian 2026-09-26)."],
 decisions=["Locker: piano = DPA 4099 pair (PA) + SM57 plate hole (wedges) + Schoeps MK4 ORTF (record) — Brian, this session.",
  "Preamps: all four piano condensers on Millennia HV-3D-8 ch 1–4; SM57 on the DQ stagebox — Brian.",
  "Q: ch 7 'KSM105'? → Brian: Neumann KMS 105.",
  "Q: ch 6/8 wired or wireless? → Brian: house Wireless 1 / 2.",
  "Q: ch 13/14 naming → Brian: ORTF puts highs on the left and lows on the right; names Hi/Lo kept as Pno Rec Hi / Lo.",
  "Q: piano group pan → Brian: audience view, Hi left.",
  "Q: SM57 plate-hole THIN → Brian: research + KB update.",
  "Q: stomp box THIN → Brian: research + KB update (narrow +3 @ 85 between modes).",
  "Q: crowd rig EQ into MD → Brian: yes, KB as-is.",
  "Q: CLA Epic host → Brian: not set up yet; delays written in fixed ms.",
  "Locker forks ch 6/7/8: specified mics are first-call locker matches — silent pass. Ch 4/5 DI exempt; crowd rig exempt."],
 monitors=[{"mix":"MIX 1","who":"Phoebe","type":"wedge ×2 (L/R of piano bench)","note":"ch 3 piano mon + her vocal; no DPAs in wedges"},
           {"mix":"MIX 2","who":"Dan","type":"wedge","note":"guitar + his vocal + a little ch 3"}],
 research=dict(genre_verified="1970s singer-songwriter folk-pop — Night Owl Shows show page (Troubadour 1970 framing), BroadwayWorld BroadStage review 2026-05-08, Harris Center listing, Kent Stage live video.",
  gig="Two nights at Memo: 2026-09-28 and 2026-09-30, seated theatre show with history segments between songs.",
  units=units,
  reconciliation=["SM57 piano plate hole: KB has no row → THIN; web consensus used, KB row queued (Brian: research + update).",
   "Stomp box DI: KB has no row → THIN; web values used with Memo mode placement, KB row queued.",
   "No other web↔KB disagreements."],
  kb_writeback=["mic-shure-sm57: piano plate-hole monitor row (HPF 160, −5 @ 250, −4 @ 500, no top).",
   "eq-starting-points: stomp box (piezo) DI row (+3 @ 85 between Memo modes, −4 @ 130, −5 @ 350, LPF 5k).",
   "eq-starting-points: high/low spaced piano pair — per-mic correction on channels, room EQ on the linked group.",
   "reverb-reference-memo: CLA Epic section (controls from Waves user guide v2; Slap/Plate vocal, Throw with Trigger; no ducker) + 7th Heaven/Epic as the only Memo reverbs.",
   "mic-library: Millennia HV-3D-8 (8 ch) as an outboard front end; no KB page yet."]),
 reverbs=reverbs,
 reverb_pairing="Phoebe's songs run Sunset Chamber, and Dan's run CLA Epic Slap → Plate for the era slap. Vocal Chamber takes over on the up-tempo tunes from both of them. On the duets, both vocals feed Sunset Chamber and the slap drops out. Large Wooden sits under the guitar and Piano Hall under the piano group at low sends. Everything is VLF-cut and 150–250 Hz low-cut on the returns, so none of it feeds Memo's 125. The Epic Throw is a button, not a bed.",
 reverb_note="CLA Epic is not yet hosted at Memo. Delay times are fixed ms until a tempo host with tap tempo exists. Epic has no ducker, so duck its return from the console if needed.",
 channels=ch)
json.dump(spec,open("The Carole King and James Taylor Story.spec.json","w"),indent=1,ensure_ascii=False)
print("ok",len(ch))
