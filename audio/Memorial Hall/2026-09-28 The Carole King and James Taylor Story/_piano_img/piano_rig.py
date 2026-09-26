from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from PIL import Image as PI
D="/Applications/Microsoft Word.app/Contents/Resources/DFonts/"
pdfmetrics.registerFont(TTFont("Cal",D+"Calibri.ttf")); pdfmetrics.registerFont(TTFont("CalB",D+"Calibrib.ttf"))
NAVY=HexColor("#1A3A5C"); BLUE=HexColor("#2E6DA4")
H1=ParagraphStyle("h1",fontName="CalB",fontSize=18,textColor=NAVY,spaceAfter=6)
H2=ParagraphStyle("h2",fontName="CalB",fontSize=12.5,textColor=BLUE,spaceBefore=10,spaceAfter=4)
P=ParagraphStyle("p",fontName="Cal",fontSize=10,leading=13.5,spaceAfter=5)
C=ParagraphStyle("c",fontName="Cal",fontSize=8.5,leading=11,textColor=HexColor("#555555"),spaceAfter=8)
T=ParagraphStyle("t",fontName="Cal",fontSize=9,leading=11.5)
TB=ParagraphStyle("tb",parent=T,fontName="CalB",textColor=HexColor("#FFFFFF"))
def img(p,w):
    a,b=PI.open(p).size; return Image(p,width=w,height=w*b/a)
def tbl(rows,widths):
    d=[[Paragraph(str(x),TB if i==0 else T) for x in r] for i,r in enumerate(rows)]
    t=Table(d,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,HexColor("#9AA6B2")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#FFFFFF"),HexColor("#EEF3F8")])]))
    return t
s=[]
s.append(Paragraph("Piano Rig — Yamaha C3",H1))
s.append(Paragraph("The Carole King &amp; James Taylor Story · Memorial Hall · 09-28 + 09-30 · full-stick lid · Phoebe's wedges left and right of the bench",P))
s.append(tbl([["Ch","Mic","Position","Preamp","Feeds"],
 ["1 Piano Hi","DPA 4099 CORE+ Extreme SPL","P-clip on the plate around G5, just past the dampers, 25–30 cm over the strings, angled down, rear null up at the lid","Millennia HV-3D-8 ch 1 → R1 LINE","PA + multitrack · pan L"],
 ["2 Piano Lo","DPA 4099 CORE+ Extreme SPL","P-clip over C2–G2, a third of the way down the strings past the dampers, same height, at least 30 cm from Hi","HV-3D-8 ch 2 → R2 LINE","PA + multitrack · pan R"],
 ["3 Piano Mon","Shure SM57","Pointing down into plate hole H2 (try H3 if the treble is thin); no 48V","DQ stagebox R3","Wedges only"],
 ["13 Pno Rec Hi","Schoeps CMC6 + MK4","ORTF bar (17 cm / 110°) on a boom from outside the bend, 15–20 cm inside the rim under the lid edge, 30–40 cm over the strings, aimed at mid-soundboard behind the dampers","HV-3D-8 ch 3 → R5 LINE","Multitrack only · L (treble)"],
 ["14 Pno Rec Lo","Schoeps CMC6 + MK4","other capsule of the same bar","HV-3D-8 ch 4 → R6 LINE","Multitrack only · R (bass)"]],
 [0.85*inch,1.1*inch,2.75*inch,1.2*inch,1.1*inch]))
s.append(Paragraph("HV-3 channels: 48V ON at the HV-3, OFF at the stagebox; stagebox inputs on LINE, console gain at unity; set the HV-3 stepped gain on her hardest playing with 15–20 dB of headroom. Needs two DPA P-clips (the clip inventory isn't logged in the KB, so check before load-in) and ideally the DAO4099 double cable.",P))
s.append(Paragraph("Why this rig",H2))
for t in [
 "<b>DPA pair for the PA, not the Schoeps MK5 in omni.</b> With a full-stick lid and wedges beside the bench, the lid throws the wedge and vocal straight into the case. Omni inside the piano picks up as much wedge as piano, so it would run out of gain before feedback early and put a smeared, vocal-heavy piano on the multitrack. The 4099's supercardioid pattern at 25–30 cm gives the most direct piano for the gain, with its rear null aimed at the lid. It's near-flat: 80 Hz–17 kHz ±3 dB with a +2 dB soft boost at 10–12 kHz (Sound On Sound).",
 "<b>SM57 in a plate hole for the wedges.</b> Dropped into a plate opening, it sits under the strings, loud at the mic and shielded by the iron frame, with its null facing up at the lid. That makes it very hard to feed back. It sounds boomy and honky, which doesn't matter in a wedge: HPF 160, −5 at 250, −4 at 500, and nothing added on top because the 57 already has a presence rise around 4–6k. With the DPAs out of the wedges entirely, the piano can't ring through monitors.",
 "<b>Schoeps MK4 ORTF for the record.</b> Tucked under the lid edge at the bend: the lid acts as a roof, the rim shields it from the stage and the wedges fall about 90° off-axis. ORTF gets its width from level differences, so it sums to mono and blends with the spaced DPAs in post without combing. It sits within about 1 ms of the DPAs, so time-align it by ear. The MK4 is the purpose-built cardioid, where the MK5 in cardioid would be a switch-position compromise.",
 "<b>Millennia HV-3 over the AEA TRP2.</b> The HV-3D-8 gives four matched, transformerless channels with large headroom for close-miked hammer transients, so the PA pair and record pair share one clean front end. The TRP2's high-impedance input and 85 dB of gain are built for passive ribbons and don't help condensers with active outputs. It also only has two channels. Keep it for the R88.",
 "<b>EQ split: channels vs piano group.</b> A high/low spaced pair isn't a true stereo pair, so each mic's own fix goes on its channel. Ch 1 gets −2 at 10k, a dynamic −3 at 2.5k for the lid bleed and −3 at 500. Ch 2 gets −4 at 250. The shared room work goes once on the linked piano group: HPF 40, −3 at 300, −3 at 125, and a Purple optical comp at 2:1 (attack 30 ms, release 300 ms) for 2–3 dB of gain reduction. Set the group by hand. The piano pans from the audience's view, Hi left, to match the MK4s."]:
    s.append(Paragraph(t,P))
s.append(Paragraph("Line check",H2))
s.append(Paragraph("Bring each DPA up alone with the EQ flat, then sum them to mono. If the centre thins, flip polarity on one mic or slide the Lo mic a few inches, then leave it alone. For the ORTF pair, have her play a C-major run across the keyboard: highs should come from the left, lows from the right, with a solid centre. If the middle is thin, rotate the bar a few degrees toward the tail. Keep the DPA cables along the rim, clear of the 57's plate hole and the Schoeps bar.",P))
s.append(PageBreak())
s.append(Paragraph("Reference photos",H1))
s.append(img("_piano_img/c3_plate.jpg",6.6*inch)); s.append(Paragraph("A real Yamaha C3 plate, shot from above the bend looking toward the tail. The plate holes (H1–H4 on the placement diagram) run in an arc along the rim at the tail end. The SM57 goes in the middle hole, H2. Photo supplied by Brian.",C))
s.append(KeepTogether([img("_piano_img/sos07.jpg",4.6*inch),Paragraph("A 4099 pair being positioned inside a Yamaha CFX on a live stage, lid on full stick: treble side just behind the dampers, where the Piano Hi mic goes. Photo: Sound On Sound, 'Miking Up A Piano Concert With DPA'.",C)]))
s.append(KeepTogether([img("_piano_img/sos08.jpg",4.6*inch),Paragraph("A P-clip magnet mount seated on the plate beside a frame bolt. This is how both DPAs attach. Photo: Sound On Sound (same article).",C)]))
s.append(KeepTogether([img("_piano_img/dpa_header.jpg",5.6*inch),Paragraph("The 4099 gooseneck angle and height over the strings. DPA's studio shot has both mics in the treble; our pair is spread high/low per the table above. Photo: DPA Microphones, 'How to mic a piano'.",C)]))
SimpleDocTemplate("The Carole King and James Taylor Story - Piano Rig.pdf",pagesize=letter,leftMargin=0.6*inch,rightMargin=0.6*inch,topMargin=0.6*inch,bottomMargin=0.6*inch,title="Piano Rig").build(s)
