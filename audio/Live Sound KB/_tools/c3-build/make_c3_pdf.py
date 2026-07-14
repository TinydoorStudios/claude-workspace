#!/usr/bin/env python3
"""DPA 4099 (Extreme SPL) on the Yamaha C3 — deep-dive PDF."""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, Flowable, NextPageTemplate)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
import sys, os, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
# regenerate the C3 diagrams alongside this script (self-contained rebuild)
subprocess.run([sys.executable, os.path.join(BASE, "make_c3_diagrams.py")], cwd=BASE, check=True)
sys.path.insert(0, os.path.join(BASE, os.pardir))  # _tools/ holds embed_refs.py
from embed_refs import ref_flowables, has_images
REFS_DIR = os.path.abspath(os.path.join(BASE, os.pardir, os.pardir, "_refs", "dpa-4099-c3"))
REFS_DISPLAY = "Live Sound KB/_refs/dpa-4099-c3/"
OUT_DIR = os.path.abspath(os.path.join(BASE, os.pardir, os.pardir, "Outputs"))

P = dict(header="#1A1A2E", sub="#0F3460", accent="#E94560", drums="#D4E8D4",
         bass="#D4D4E8", keys="#E8D4E8", warn="#FFE4B5", tour="#FFF3CD",
         alt="#E8EEF7", paper="#FBFAF6", ink="#22232b", grey="#6b7280",
         teal="#0F7A6B", amber="#FFB347")
C = {k: colors.HexColor(v) for k, v in P.items()}
PAGE = landscape(letter); LW, LH = PAGE; M = 0.55*inch; CW = LW-2*M
ss = getSampleStyleSheet()
def stl(n, **k):
    base = k.pop("parent", ss["Normal"]); return ParagraphStyle(n, parent=base, **k)
H1=stl("H1",fontName="Helvetica-Bold",fontSize=24,textColor=C["header"],leading=28)
H3=stl("H3",fontName="Helvetica-Bold",fontSize=12,textColor=C["sub"],leading=15,spaceBefore=6,spaceAfter=3)
BODY=stl("BODY",fontName="Helvetica",fontSize=10.2,textColor=C["ink"],leading=14.5,spaceAfter=6)
BODYS=stl("BODYS",fontName="Helvetica",fontSize=9.3,textColor=C["ink"],leading=12.8)
LEAD=stl("LEAD",fontName="Helvetica",fontSize=12,textColor=C["sub"],leading=16.5)
CELL=stl("CELL",fontName="Helvetica",fontSize=8.7,textColor=C["ink"],leading=11)
CELLB=stl("CELLB",fontName="Helvetica-Bold",fontSize=8.7,textColor=C["header"],leading=11)
CELLW=stl("CELLW",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white,leading=11)
CAP=stl("CAP",fontName="Helvetica-Oblique",fontSize=8.6,textColor=C["grey"],leading=11)

class HRule(Flowable):
    def __init__(s,w,color=C["accent"],t=2): s.w=w;s.c=color;s.t=t;Flowable.__init__(s)
    def wrap(s,*a): return (s.w,s.t+2)
    def draw(s): s.canv.setStrokeColor(s.c);s.canv.setLineWidth(s.t);s.canv.line(0,1,s.w,1)

class Band(Flowable):
    def __init__(s,title,text,fill):
        Flowable.__init__(s); s.fill=fill
        s.p1=Paragraph(f"<b>{title}</b>",stl("bt",fontName="Helvetica-Bold",fontSize=10.5,textColor=C["header"],leading=13))
        s.p2=Paragraph(text,stl("bx",fontName="Helvetica",fontSize=9.4,textColor=C["ink"],leading=12.5))
    def wrap(s,aw,ah):
        s.w=aw; w=s.w-18
        _,h1=s.p1.wrap(w,1000); _,h2=s.p2.wrap(w,1000); s.h=h1+h2+16; return (s.w,s.h)
    def draw(s):
        s.canv.setFillColor(s.fill); s.canv.roundRect(0,0,s.w,s.h,5,fill=1,stroke=0)
        s.canv.setFillColor(C["accent"]); s.canv.rect(0,0,4,s.h,fill=1,stroke=0)
        w=s.w-18; _,h1=s.p1.wrap(w,1000)
        s.p1.drawOn(s.canv,12,s.h-8-h1); s.p2.drawOn(s.canv,12,8)

def img(path,maxw,maxh):
    from PIL import Image as PI
    iw,ih=PI.open(path).size; r=min(maxw/iw,maxh/ih); return Image(path,iw*r,ih*r)

def bg(canv,doc):
    canv.saveState(); canv.setFillColor(C["paper"]); canv.rect(0,0,LW,LH,fill=1,stroke=0)
    canv.setStrokeColor(C["header"]); canv.setLineWidth(0.6); canv.line(M,0.42*inch,LW-M,0.42*inch)
    canv.setFont("Helvetica",8); canv.setFillColor(C["grey"])
    canv.drawString(M,0.28*inch,"DPA 4099 on the Yamaha C3  ·  Live Sound KB  ·  Brian Lloyd")
    canv.drawRightString(LW-M,0.28*inch,"Extreme SPL · stereo 4099P · 2026-06-03")
    canv.drawCentredString(LW/2,0.28*inch,f"{doc.page}"); canv.restoreState()

def cover_bg(canv,doc):
    canv.saveState(); canv.setFillColor(C["header"]); canv.rect(0,0,LW,LH,fill=1,stroke=0)
    canv.setFillColor(C["accent"]); canv.rect(0,LH-0.32*inch,LW,0.32*inch,fill=1,stroke=0)
    canv.setFillColor(C["accent"]); canv.rect(0,0,LW,0.18*inch,fill=1,stroke=0)
    canv.setFillColor(C["tour"]); canv.rect(M,LH-3.05*inch,1.5*inch,0.13*inch,fill=1,stroke=0)
    canv.restoreState()

story=[]
# ---------- COVER ----------
cv=[Spacer(1,1.3*inch),
    Paragraph("DPA 4099 ON THE YAMAHA C3",stl("ct",fontName="Helvetica-Bold",fontSize=33,textColor=colors.white,leading=37)),
    Spacer(1,6),
    Paragraph("A deep dive on your usual case — 6 ft 1 in grand, stereo 4099P, open lid &amp; closed lid",
              stl("cs",fontName="Helvetica",fontSize=15,textColor=C["tour"],leading=20)),
    Spacer(1,0.5*inch),
    Paragraph("Mics: 2 &#215; 4099 CORE+ <font color='#FFF3CD'><b>Extreme SPL</b></font> (yellow band) in the 4099P piano kit",
              stl("ck",fontName="Helvetica",fontSize=13,textColor=colors.white,leading=18)),
    Paragraph("Why this is the <i>best</i> home for the Extreme SPL: a grand exceeds 130 dB near the hammers.",
              stl("ck2",fontName="Helvetica",fontSize=11,textColor=C["amber"],leading=16)),
    Spacer(1,1.4*inch),
    Paragraph("Live Sound KB  ·  companion to article mic-dpa-4099 (C3 section)",
              stl("cf",fontName="Helvetica-Oblique",fontSize=10,textColor=C["grey"],leading=14))]
story+= [KeepTogether(cv), NextPageTemplate("main"), PageBreak()]

# ---------- PAGE 2: anatomy + why extreme spl ----------
story+=[Paragraph("The C3, and why your Extreme SPL pair belongs in it",H1),HRule(CW),Spacer(1,6)]
left=[Paragraph("The Yamaha C3 is a 6 ft 1 in (186 cm) conservatory grand — 88 keys from A0 (27.5 Hz) "
      "to C8 (4186 Hz), duplex-scaled, with the bass strings crossing over the tenor break and a short, dense "
      "treble section. Two soundholes sit in the plate. Up close it is enormous dynamically: DPA measures more "
      "than <b>130 dB peak near the hammers</b>.",LEAD),
   Spacer(1,4),
   Band("This is the best room for your Extreme SPL mics",
        "On a quiet solo violin the Extreme SPL's 28 dB(A) floor shows. Inside a C3 it's the opposite story — the "
        "instrument is loud right where the capsules sit, so the noise floor disappears and the <b>152 dB headroom "
        "gets used</b> on every hard fortissimo strike. Close, directional, loud source = exactly what the Extreme "
        "SPL was built for. Your usual gig is the ideal gig for these mics.",C["tour"]),
   Spacer(1,4),
   Paragraph("Close + directional = percussive + isolated",H3),
   Paragraph("Clip mics inside the piano capture mostly direct sound and very little room, which reads as more "
      "percussive and attack-forward than a pair out in front. That's a feature on a band stage (cuts through, "
      "resists feedback) and something to soften with placement and a room blend when you want natural. The "
      "supercardioid pattern is what buys you the isolation in both your lid positions.",BODYS)]
right=[img("c3_tone.png",CW*0.46,3.6*inch),
       Spacer(1,3),
       Paragraph("Closer and nearer the hammers buys attack and proximity bass; back and higher buys body and "
                 "blend. Pick your spot on this map before you touch EQ.",CAP)]
t=Table([[left,right]],colWidths=[CW*0.52,CW*0.48])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(1,0),(1,0),14)]))
story+=[t,PageBreak()]

# ---------- PAGE 3: spaced pair positions ----------
story+=[Paragraph("Your stereo pair — where the two mics go",H1),HRule(CW),Spacer(1,5)]
story+=[img("c3_topview.png",CW,3.7*inch),Spacer(1,5)]
recipe=[["Step","Bass (low) mic","Treble (high) mic"],
 ["Position","Over C2–G2, ~1/3 of the way down the strings, well into the casing","~An octave-and-a-half above middle C (~G5)"],
 ["Height","25–30 cm (10–12 in) over the strings, angled down","25–30 cm over the strings, angled down"],
 ["Mount","4099P magnet to the plate; shape with the gooseneck","Same — magnet on the plate"],
 ["Spacing","30 cm+ (12 in) between the two — closer combs, too far leaves a hole in the middle","—"]]
rt=[[Paragraph(c,CELLW) for c in recipe[0]]]+[[Paragraph(r[0],CELLB),Paragraph(r[1],CELL),Paragraph(r[2],CELL)] for r in recipe[1:]]
tb=Table(rt,colWidths=[1.1*inch,5.0*inch,3.8*inch],repeatRows=1)
st=[("BACKGROUND",(0,0),(-1,0),C["header"]),("GRID",(0,0),(-1,-1),0.5,C["sub"]),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("LEFTPADDING",(0,0),(-1,-1),5),("SPAN",(2,4),(2,4))]
for i in range(1,len(rt)):
    if i%2==0: st.append(("BACKGROUND",(0,i),(-1,i),C["alt"]))
tb.setStyle(TableStyle(st))
story+=[tb,Spacer(1,5),
   Band("Set-up order that works",
     "Mount both, HPF in, then bring the mics up <b>one at a time</b> with EQ flat. Mono-sum the pair and listen — "
     "if the center thins, flip polarity on one. Get a balance you like, then leave it alone. The real-world rule "
     "from engineers who live on these: once it sounds like the piano (just louder), stop touching it.",C["bass"])]
story+=[PageBreak()]

# ---------- PAGE 4: open vs closed ----------
story+=[Paragraph("Your two lids — open and closed",H1),HRule(CW),Spacer(1,4)]
story+=[img("c3_lids.png",CW,3.0*inch),Spacer(1,5)]
oc=[["","Full stick / OPEN","Closed / LID DOWN"],
 ["Tone","Most natural and open; lid reflects to the room","Darker, more boxed-in; reflections trapped under the lid"],
 ["Use it for","Solo, classical, vocal accompaniment, quieter stages","Loud bands, pit, max separation, monitors blasting"],
 ["Watch for","Bleed and feedback — most of both","Boxiness (200–400 Hz) and comb filtering"],
 ["Placement tweak","Mics a touch lower/closer for gain-before-feedback; let them catch a little lid reflection for air","Low-profile on the plate; widen the pair spacing to fight combing"],
 ["Feedback move","Aim the supercardioid null at the nearest wedge/PA","Lid itself is the isolation; null still helps with spill"]]
ot=[[Paragraph(c,CELLW) for c in oc[0]]]+[[Paragraph(r[0],CELLB),Paragraph(r[1],CELL),Paragraph(r[2],CELL)] for r in oc[1:]]
otb=Table(ot,colWidths=[1.3*inch,4.3*inch,4.3*inch],repeatRows=1)
ost=[("BACKGROUND",(0,0),(-1,0),C["header"]),("GRID",(0,0),(-1,-1),0.5,C["sub"]),
     ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
     ("LEFTPADDING",(0,0),(-1,-1),5),("BACKGROUND",(1,1),(1,-1),C["tour"]),("BACKGROUND",(2,1),(2,-1),C["alt"])]
otb.setStyle(TableStyle(ost))
story+=[otb,PageBreak()]

# ---------- PAGE 5: EQ + recording/live ----------
story+=[Paragraph("EQ, recording &amp; feedback",H1),HRule(CW),Spacer(1,4)]
story+=[Paragraph("Start flat. A real engineer micing a grand with 4099Ps on open/short stick left the desk "
   "essentially flat except a low-end roll-off (~90 Hz on the bass mic, a little higher on the treble). Cut only "
   "what the room shows you. The mic's built-in +2 dB at 10–12 kHz means you almost never add air. Whole-dB values.",BODYS),Spacer(1,5)]
eq=[["Move","Open lid","Closed lid"],
 ["HPF — bass mic","90 Hz","90 Hz"],
 ["HPF — treble mic","~110 Hz","~110 Hz"],
 ["Boxiness (lid)","none, or gentle -2 @ 300 Q1.4","-3 to -4 @ 250–400 Q1.5 (expect this)"],
 ["Low-mid tub","-2 @ 200 Q1.5 only if boomy","-3 @ 200 Q1.5"],
 ["Honk","-2 @ 500 Q1.5 if present","-3 @ 500 Q1.5"],
 ["Air (10–12 kHz)","leave it — it's built in","leave it; if closed-lid-dull, gentle +2 @ 8 kHz shelf"]]
et=[[Paragraph(c,CELLW) for c in eq[0]]]+[[Paragraph(r[0],CELLB),Paragraph(r[1],CELL),Paragraph(r[2],CELL)] for r in eq[1:]]
etb=Table(et,colWidths=[2.3*inch,3.2*inch,4.4*inch],repeatRows=1)
est=[("BACKGROUND",(0,0),(-1,0),C["header"]),("GRID",(0,0),(-1,-1),0.5,C["sub"]),
     ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),2.6),("BOTTOMPADDING",(0,0),(-1,-1),2.6),
     ("LEFTPADDING",(0,0),(-1,-1),5),("BACKGROUND",(1,1),(1,-1),C["tour"]),("BACKGROUND",(2,1),(2,-1),C["alt"])]
etb.setStyle(TableStyle(est))
story+=[etb,Spacer(1,12)]
colL=[Paragraph("Recording &amp; post",H3),
   Paragraph("The 4099 pair is dry and internal by design. For your multitrack/post work, capture each mic to its "
     "own track and blend a room layer underneath — a spaced room pair, or at the Memo your crowd rig — to put the "
     "instrument back in a space. The dry close pair gives you control; the room gives you air.",BODYS)]
colR=[Paragraph("Feedback &amp; bleed",H3),
   Paragraph("Supercardioid rejects best at its rear/sides — point that null at the nearest monitor or PA stack. "
     "HPF clears proximity rumble and stage thumps. Closed lid is your biggest single isolation win on a loud stage; "
     "open lid leans on placement and the null instead.",BODYS)]
two=Table([[colL,colR]],colWidths=[CW*0.5,CW*0.5])
two.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(1,0),(1,0),16)]))
story+=[two,PageBreak()]

# ---------- PAGE: real-world reference photos (embedded from drop folder) ----------
story+=[Paragraph("Real-world reference photos",H1),HRule(CW),Spacer(1,5)]
if has_images(REFS_DIR):
    story+=[Paragraph(f"Photos dropped into <b>{REFS_DISPLAY}</b>, embedded at full fidelity with your captions.",BODYS),Spacer(1,7)]
else:
    story+=[Paragraph("This page fills itself from the drop folder. Add photos and ask me to rebuild — see below.",BODYS),Spacer(1,7)]
story+=ref_flowables(REFS_DIR,CW,cols=2,
   empty_note=("No reference photos dropped yet. Save image files — DPA pages, Sound On Sound, your own C3 rig "
     f"shots — into <b>{REFS_DISPLAY}</b>, then ask me to rebuild and they embed here, cropped and captioned. "
     "Optional captions go in captions.tsv (filename &lt;tab&gt; caption &lt;tab&gt; credit); prefix files 01_, 02_ to set order."))
story+=[PageBreak()]

# ---------- PAGE 6: checklist + reference gallery ----------
story+=[Paragraph("C3 quick-rig &amp; real-world references",H1),HRule(CW),Spacer(1,5)]
chk=[("1","Magnets to the plate. Bass mic over C2–G2 (~1/3 down the strings); treble mic ~G5."),
 ("2","Both 25–30 cm above strings, angled down toward the soundboard. Pair 30 cm+ apart."),
 ("3","HPF in — adapter 80 Hz plus console ~90 Hz bass / ~110 Hz treble."),
 ("4","Mono-sum, phase-check, flip one if the center thins."),
 ("5","Bring up one mic at a time, EQ flat. Cut only what's boxy/honky."),
 ("6","Closed lid: widen the spacing, expect to pull 250–400 Hz. Open lid: mind feedback, aim the null."),
 ("7","Set &amp; forget. Light level rides only. Record each mic to its own track + a room layer.")]
cr=[[Paragraph(f"<b>{n}</b>",CELLB),Paragraph(t,CELL)] for n,t in chk]
ctb=Table(cr,colWidths=[0.4*inch,CW-0.4*inch])
ctb.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,C["sub"]),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
   ("BACKGROUND",(0,0),(0,-1),C["alt"]),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
   ("LEFTPADDING",(0,0),(-1,-1),6)]))
story+=[ctb,Spacer(1,8)]
story+=[Band("Getting real photos into this doc",
   f"Drop image files into <b>{REFS_DISPLAY}</b> (DPA, Sound On Sound, your own rig shots) and ask me to rebuild — "
   "they embed on the Real-World Reference Photos page, cropped and captioned. The diagrams in this doc are drawn "
   "faithfully from the real references; the links below go straight to the genuine photos and DPA's how-to videos.",C["warn"])]
story+=[Spacer(1,6),Paragraph("Real-world reference gallery (click through)",H3)]
refs=[["Reference","What it shows","Link"],
 ["DPA — How to mic a piano","Grand/upright methods + 4099 piano video; the stereo set-up diagram these drawings follow","dpamicrophones.com/mic-university/how-to-mic/how-to-mic-a-piano"],
 ["DPA — 4099 piano mounting video","4099P magnet mounts seated in the frame, real piano","youtu.be/k19mByCajDo"],
 ["DPA — 4099 stereo piano video","Most popular ways to mic a piano with a 4099 pair","youtu.be/otj4M3j_pWo"],
 ["Sound On Sound — Miking a piano concert with DPA","Real gig: 4099Ps on a grand, magnet on the gold frame, in-situ placement photos","soundonsound.com/techniques/miking-piano-concert-dpa"],
 ["SOS — How loud is a concert grand?","Backs the >130 dB-near-the-hammers figure","soundonsound.com/sound-advice/q-how-loud-concert-grand-piano"],
 ["DPK4099 CORE+ piano kit","The piano stereo kit page (clips, mounts, specs)","dpamicrophones.com/microphones/kits/dpk4099"]]
rr=[[Paragraph(c,CELLW) for c in refs[0]]]+[[Paragraph(r[0],CELLB),Paragraph(r[1],CELL),Paragraph(f"<a href='https://{r[2]}'><font color='#0F3460'>{r[2]}</font></a>",CELL)] for r in refs[1:]]
rtb=Table(rr,colWidths=[2.7*inch,4.5*inch,2.7*inch],repeatRows=1)
rst=[("BACKGROUND",(0,0),(-1,0),C["header"]),("GRID",(0,0),(-1,-1),0.5,C["sub"]),
     ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
     ("LEFTPADDING",(0,0),(-1,-1),5)]
for i in range(1,len(rr)):
    if i%2==0: rst.append(("BACKGROUND",(0,i),(-1,i),C["alt"]))
rtb.setStyle(TableStyle(rst))
story+=[rtb]

out=os.path.join(OUT_DIR,"DPA-4099-on-Yamaha-C3.pdf")
doc=SimpleDocTemplate(out,pagesize=PAGE,leftMargin=M,rightMargin=M,topMargin=0.55*inch,
    bottomMargin=0.6*inch,title="DPA 4099 on the Yamaha C3",author="Brian Lloyd / Live Sound KB")
frame=Frame(M,0.6*inch,CW,LH-1.15*inch,id="main",leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="cover",frames=[Frame(M,0.6*inch,CW,LH-1.15*inch)],onPage=cover_bg),
                      PageTemplate(id="main",frames=[frame],onPage=bg)])
doc.build(story)
print("built",out)
