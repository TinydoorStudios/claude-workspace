from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
import math
D="/Applications/Microsoft Word.app/Contents/Resources/DFonts/"
pdfmetrics.registerFont(TTFont("Cal",D+"Calibri.ttf")); pdfmetrics.registerFont(TTFont("CalB",D+"Calibrib.ttf"))
NAVY=HexColor("#1A3A5C"); BLUE=HexColor("#2E6DA4"); GREY=HexColor("#9AA6B2")
GOLD=HexColor("#E9D9A6"); RED=HexColor("#C0392B"); GRN=HexColor("#2E8B57"); ORG=HexColor("#D9822B"); PUR=HexColor("#7D4EA0")
W,H=landscape(letter); c=canvas.Canvas("C3_Piano_Mic_Placement.pdf",pagesize=(W,H))
S=2.0; OX=135; OY=150   # pt per cm, origin = key front / treble corner
def P(x,y): return OX+x*S, OY+y*S
# Bezier helpers for treble bend
B1=[(62,0),(100,0),(118,40),(148,72)]
B2=[(148,72),(172,97),(192,120),(184,140)]
def bz(b,t):
    return tuple((1-t)**3*b[0][i]+3*(1-t)**2*t*b[1][i]+3*(1-t)*t*t*b[2][i]+t**3*b[3][i] for i in (0,1))
def bzd(b,t):
    return tuple(3*(1-t)**2*(b[1][i]-b[0][i])+6*(1-t)*t*(b[2][i]-b[1][i])+3*t*t*(b[3][i]-b[2][i]) for i in (0,1))
def case_path():
    p=c.beginPath(); p.moveTo(*P(18,0)); p.lineTo(*P(*B1[0]))
    p.curveTo(*P(*B1[1]),*P(*B1[2]),*P(*B1[3])); p.curveTo(*P(*B2[1]),*P(*B2[2]),*P(*B2[3]))
    p.curveTo(*P(178,149),*P(172,149),*P(165,149)); p.lineTo(*P(18,149)); p.close(); return p
c.setFont("CalB",18); c.setFillColor(NAVY); c.drawString(36,H-42,"Yamaha C3 piano mics, top-down view")
c.setFont("Cal",10.5); c.setFillColor(HexColor("#333333"))
c.drawString(36,H-58,"Carole King & James Taylor Story  ·  full-stick lid  ·  side wedges  ·  approx. scale, 186 × 149 cm case  ·  plate holes placed from a real C3 photo · mic spots finalized by ear on site")
# case
c.setLineWidth(2); c.setStrokeColor(NAVY); c.setFillColor(GOLD); c.drawPath(case_path(),fill=1,stroke=1)
# strings (schematic): treble straight, bass overstrung
c.setLineWidth(0.4); c.setStrokeColor(HexColor("#B59A55"))
for i in range(0,26):
    y=8+i*3.4; L=40+i*3.6; c.line(*P(30,y),*P(30+L,y+ i*0.25))
for i in range(0,14):
    y=100+i*3.2; c.line(*P(34,y),*P(150+i*1.2,y+8))
# damper / hammer lines
c.setStrokeColor(GREY); c.setDash(4,3); c.setLineWidth(1)
c.line(*P(24,6),*P(24,143)); c.line(*P(31,6),*P(31,143)); c.setDash()
c.setFont("Cal",8); c.setFillColor(HexColor("#555555"))
c.drawCentredString(P(24,0)[0]+6,P(0,146)[1]-16,"hammers"); c.drawCentredString(P(31,0)[0]+12,P(0,146)[1]-26,"dampers")
# keyboard
c.setFillColor(white); c.setStrokeColor(NAVY); c.setLineWidth(1)
c.rect(*P(0,12),16*S,125*S,fill=1,stroke=1)
c.setFillColor(HexColor("#222222"))
for k in range(52):
    y=12+k*125/52
    c.setLineWidth(0.3); c.line(*P(0,y),*P(16,y))
    if k%7 not in (2,6): c.rect(*P(6,y+125/52*0.65),10*S,125/52*0.7*S,fill=1,stroke=0)
c.setFillColor(NAVY); c.rect(*P(0,137),18*S,12*S,fill=1,stroke=0); c.rect(*P(0,0),18*S,12*S,fill=1,stroke=0)
# key labels
def keyy(n): return 137-(n-1)/87*125   # A0 = key1 top (bass), C8 bottom (treble)
c.setFont("Cal",7.5); c.setFillColor(NAVY)
for n,lab in ((40,"middle C"),(59,"G5"),(20,"E2")):
    x,y=P(0,keyy(n)); c.drawRightString(x-3,y-2.5,lab+" –")
c.setFont("CalB",9); x,y=P(-2,146); c.drawRightString(x-4,y,"BASS (player's L)")
x,y=P(-2,3); c.drawRightString(x-4,y,"TREBLE (player's R)")
# lid hinge
c.setStrokeColor(NAVY); c.setLineWidth(3); c.line(*P(40,151),*P(160,151))
c.setFont("Cal",8); c.setFillColor(NAVY); c.drawString(P(62,153)[0],P(0,153)[1]+2,"lid hinge (straight side), lid opens toward treble side / house")
def dot(x,y,col,r=6.5):
    c.setFillColor(col); c.setStrokeColor(white); c.setLineWidth(1.2); c.circle(*P(x,y),r,fill=1,stroke=1)
def arrow(x1,y1,x2,y2,col,w=1.4):
    c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(w)
    a,b=P(x1,y1); d,e=P(x2,y2); c.line(a,b,d,e); ang=math.atan2(e-b,d-a)
    p=c.beginPath(); p.moveTo(d,e); p.lineTo(d-7*math.cos(ang-0.4),e-7*math.sin(ang-0.4)); p.lineTo(d-7*math.cos(ang+0.4),e-7*math.sin(ang+0.4)); p.close(); c.drawPath(p,fill=1,stroke=0)
def tag(x,y,txt,col,dx=10,dy=-3,bold=True):
    c.setFont("CalB" if bold else "Cal",9); c.setFillColor(col); c.drawString(P(x,y)[0]+dx,P(x,y)[1]+dy,txt)
# DPA Hi / Lo
hi=(38,keyy(59)); lo=(74,118)
c.setStrokeColor(RED); c.setDash(2,2); c.setLineWidth(0.8); c.line(*P(*hi),*P(*lo)); c.setDash()
mx,my=P((hi[0]+lo[0])/2,(hi[1]+lo[1])/2); c.setFont("Cal",7.5); c.setFillColor(RED); c.drawString(mx+5,my,"≥ 30 cm apart (~65 cm here)")
arrow(hi[0]+9,hi[1]-3,hi[0]+1.5,hi[1]-0.5,RED); dot(*hi,RED); tag(*hi,"1  Piano Hi – DPA 4099",RED,dx=-8,dy=-17)
arrow(lo[0]+9,lo[1]-3,lo[0]+1.5,lo[1]-0.5,RED); dot(*lo,RED); tag(*lo,"2  Piano Lo – DPA 4099",RED,dx=10,dy=6)
# plate holes (from photo): 4 along the rim arc, smallest toward the tail
def inset(b,t,d):
    x,y=bz(b,t); dx,dy=bzd(b,t); n=math.hypot(dx,dy); return (x-dy/n*d, y+dx/n*d)
holes=[(B2,0.55,4.2,"H1"),(B2,0.18,5.2,"H2"),(B1,0.93,5.6,"H3"),(B1,0.80,5.6,"H4")]
c.setStrokeColor(HexColor("#B59A55")); c.setLineWidth(5)
a=inset(B1,0.72,30); b=inset(B2,0.75,12); c.line(*P(*a),*P(*b))
for b_,t_,r,lab in holes:
    hx,hy=inset(b_,t_,13); c.setFillColor(HexColor("#6B5A2E")); c.setStrokeColor(HexColor("#B59A55")); c.setLineWidth(1.5)
    c.circle(*P(hx,hy),r*S,fill=1,stroke=1)
    c.setFont("CalB",7); c.setFillColor(white); c.drawCentredString(P(hx,hy)[0],P(hx,hy)[1]-2.5,lab) if lab!="H2" else None
h=inset(B2,0.18,13)
dot(*h,GRN,5.5); tag(*h,"3  Piano Mon – SM57 in hole H2",GRN,dx=-150,dy=-3)
# Schoeps ORTF at the bend
t=0.40; bx,by=bz(B1,t); dx,dy=bzd(B1,t); n=math.hypot(dx,dy); nx,ny=dy/n,-dx/n   # outward normal
inx,iny=-nx,-ny
stand=(bx+nx*22,by+ny*22); ctr=(bx+inx*18,by+iny*18)
c.setStrokeColor(PUR); c.setLineWidth(2); c.line(*P(*stand),*P(*ctr))
c.setFillColor(PUR); c.circle(*P(*stand),5,fill=1,stroke=0)
tx,ty=dx/n,dy/n; half=8.5
cL=(ctr[0]-tx*half,ctr[1]-ty*half); cR=(ctr[0]+tx*half,ctr[1]+ty*half)
c.setLineWidth(3); c.line(*P(*cL),*P(*cR))
base=math.atan2(iny,inx)
for cc,s in ((cL,1),(cR,-1)):
    a=base+s*math.radians(55); arrow(cc[0],cc[1],cc[0]+math.cos(a)*15,cc[1]+math.sin(a)*15,PUR,1.2); dot(*cc,PUR,4.5)
tag(*stand,"4/5  Piano Rec L/R – Schoeps MK4, ORTF",PUR,dx=10,dy=-4)
c.setFont("Cal",7.5); c.setFillColor(PUR); x,y=P(*stand); c.drawString(x+10,y-15,"17 cm / 110°, 15–20 cm inside rim, under lid edge, 30–40 cm over strings")
# player, vocal, wedges
pl=(-24,80)
c.setFillColor(HexColor("#555555")); c.circle(*P(*pl),9,fill=1,stroke=0); c.setFont("Cal",8); c.drawCentredString(P(*pl)[0],P(*pl)[1]-19,"pianist / vocal")
for wy,lab in ((166,"wedge L"),(-12,"wedge R")):
    wx=-32; x,y=P(wx,wy); c.setFillColor(ORG); c.setStrokeColor(ORG)
    c.saveState(); c.translate(x,y); c.rotate(math.degrees(math.atan2(pl[1]-wy,pl[0]-wx))-90)
    p=c.beginPath(); p.moveTo(-16,-8); p.lineTo(16,-8); p.lineTo(11,8); p.lineTo(-11,8); p.close(); c.drawPath(p,fill=1,stroke=0); c.restoreState()
    c.setFont("CalB",8.5); c.drawString(x+20,y-3,lab)
# house arrow
arrow(95,-26,95,-44,NAVY,2); c.setFont("CalB",10); c.setFillColor(NAVY); c.drawCentredString(P(95,-44)[0],P(0,-44)[1]-14,"HOUSE")
# notes panel
X0=W-228; Y=H-92
c.setFont("CalB",11); c.setFillColor(NAVY); c.drawString(X0,Y,"Channels and placement")
rows=[(RED,"1 Piano Hi · DPA 4099 · PA",["P-clip magnet on plate, just past the","dampers around G5 (1.5 oct above mid C).","25–30 cm over strings, angled down.","Rear null faces up at the lid."]),
(RED,"2 Piano Lo · DPA 4099 · PA",["Over C2–G2, about 1/3 down the strings","past the dampers, well into the case.","Same height and angle as Hi."]),
(GRN,"3 Piano Mon · SM57 · wedges only",["Plate holes run along the rim at the","tail end (H1 smallest to H4). Start in H2,","try H3. Pointing down.","Mon: HPF 150–180, scoop 300–500."]),
(PUR,"4/5 Piano Rec · MK4 ORTF · multitrack",["Boom from outside the bend, bar","under the lid edge, aimed at mid-","soundboard behind the dampers, not","the hammers. Too wide? Narrow to 90°."])]
Y-=18
for col,h1,lines in rows:
    c.setFillColor(col); c.circle(X0+4,Y+3,4,fill=1,stroke=0)
    c.setFont("CalB",9.5); c.setFillColor(NAVY); c.drawString(X0+13,Y,h1); Y-=12
    c.setFont("Cal",8.8); c.setFillColor(HexColor("#333333"))
    for l in lines: c.drawString(X0+13,Y,l); Y-=11
    Y-=7
c.setFont("CalB",9.5); c.setFillColor(NAVY); c.drawString(X0,Y,"Line-check order"); Y-=12
c.setFont("Cal",8.8); c.setFillColor(HexColor("#333333"))
for l in ["Each DPA alone with EQ flat, then mono-sum.","Center thins: flip one or move Lo a few inches.","Keep DPA cables along the rim, clear of the","57 hole and the Schoeps bar. Needs 2× P-clips."]:
    c.drawString(X0,Y,l); Y-=11
c.setFont("Cal",7.5); c.setFillColor(GREY); c.drawString(36,22,"Nyquist · 2026-09-26 · refs: SOS \"Miking Up A Piano Concert With DPA\"; DPA mic-university 4099 mounting guide")
c.save()
