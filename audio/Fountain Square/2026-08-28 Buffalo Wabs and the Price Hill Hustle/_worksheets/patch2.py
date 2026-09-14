p="_worksheets/build_spec.py"; s=open(p).read()
reps=[]
reps.append(('{"ch":"15","finding":"Resonator:', '{"ch":"14","finding":"Resonator:'))
reps.append((
'  {"ch":"14","finding":"Electric mandolin pickup has far less piezo quack than an acoustic mando — lighter shaping.","sources":"Gearspace piezo vs magnetic threads","verdict":"THIN",\n   "trace":{"base":"magnetic/active tone → light quack trim only","equip":"electric mando — the equip layer IS the difference vs ch13","genre":"kept present to cut on leads","artist":"no change","venue":"FSQ — −4@2.5k, −4@400, top left present"}},',
'  {"ch":"15","finding":"Shared electric-mando / electric-GUITAR channel. Electric guitar arrives as a cab-simulated XLR direct feed (Quilter/modeler) — amp-sim fizz lives 3-5 k and above 10-12 k; the IR bakes the cab voicing so it is treated as a mic’d cab, cuts only (REV 2 change).","sources":"Sweetwater amp-modeler FOH, Waves amp-sim EQ, HomeMusicCreator; KB capsule-gate-covers-cab-IRs","verdict":"THIN",\n   "trace":{"base":"cab-sim direct = mic’d cab, IR bakes voicing → CUTS ONLY","equip":"electric guitar modeler/cab-sim feed is the new element vs the old electric-mando-only channel","genre":"Americana lead electric = warm/moderate gain, not metal — tame bark keep body","artist":"Matt’s lead electric shares the channel with a bright electric mando — middle-ground curve","venue":"FSQ outdoor — LPF 11k for fizz, -3@3.5k harsh, -4@350 box, -2@1500 nasal; retune per active instrument"}},'))
reps.append((
'  {"ch":"16","finding":"Banjo piezo is bright + feedback-prone; EQ fix = 250 boom, 1–2 k honk, 4–6 k brightness.","sources":"Banjo Hangout, HomeRecording banjo EQ","verdict":"AGREE",\n   "trace":{"base":"bright/feedback-prone piezo","equip":"tenor banjo pickup — no change","genre":"banjo ring wanted but controlled outdoors","artist":"Scott’s tenor banjo — feedback margin matters at level","venue":"FSQ — boom −5@250, honk −4@1.5k, brightness −3@5k, HPF 120"}},',
'  {"ch":"17 (doubling)","finding":"Banjo piezo is bright + feedback-prone; EQ fix = 250 boom, 1–2 k honk, 4–6 k brightness. REV 2: the dedicated banjo channel was dropped — the 5-string banjo now shares the doubling channel, so this research applies there.","sources":"Banjo Hangout, HomeRecording banjo EQ","verdict":"AGREE",\n   "trace":{"base":"bright/feedback-prone piezo","equip":"5-string banjo now on the shared doubling channel","genre":"banjo ring wanted but controlled outdoors","artist":"Scott’s banjo — feedback margin matters at level","venue":"FSQ — boom −5@250, honk −4@1.5k, brightness −3@5k when banjo is active"}},'))
reps.append(('{"ch":"17/18","finding":"Piezo acoustic five-fix', '{"ch":"16/17","finding":"Piezo acoustic five-fix'))
reps.append(('"artist":"Matt’s acoustic (17); Scott’s doubling utility (18)"','"artist":"Matt’s acoustic (16); Scott’s doubling utility (17)"'))
reps.append((
'"reconciliation":["No web↔KB disagreements — every unit AGREE except the electric mandolin (THIN: the KB has no electric-mando row and web piezo-vs-magnetic guidance is general, so the light-touch curve is a reasoned starting point to confirm at line check)."]',
'"reconciliation":["No web↔KB disagreements — every unit AGREE except the shared electric-mando/electric-guitar channel (THIN: a cab-sim direct feed shared by two different instruments, no KB row for either, so the cuts-only middle-ground curve is a reasoned starting point to retune per the active instrument at line check)."]'))
reps.append((
'"changes":[\n  "Overheads mapped',
'"changes":[\n  "REV 2 (revised input list 2026-08-28): string section reworked — dedicated Banjo channel dropped (5-string banjo now shares the doubling channel); old Electric Mandolin channel became a shared Electric Mandolin / Electric GUITAR channel (new cab-sim electric-guitar feed, treated as a mic’d cab, cuts-only + LPF 11k); resonator/acoustic/doubling renumbered. Drums, bass, overheads, vocals and wireless UNCHANGED — only the changed sources were re-researched.",\n  "Overheads mapped'))
reps.append((
'"decisions":[\n  "Date confirmed',
'"decisions":[\n  "REV 2: Brian supplied a revised input list — banjo dropped as a dedicated channel (folds into doubling), electric guitar added on the shared electric-mando channel. Per his instruction only the changed sources were re-researched.",\n  "Date confirmed'))
for a,b in reps:
    assert a in s, "NOT FOUND: "+a[:60]
    s=s.replace(a,b)
open(p,"w").write(s); print("all",len(reps),"reps applied")
