from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
D="/Applications/Microsoft Word.app/Contents/Resources/DFonts/"
pdfmetrics.registerFont(TTFont("Cal",D+"Calibri.ttf")); pdfmetrics.registerFont(TTFont("CalB",D+"Calibrib.ttf"))
NAVY=HexColor("#1A3A5C"); BLUE=HexColor("#2E6DA4"); GREY=HexColor("#9AA6B2")
H1=ParagraphStyle("h1",fontName="CalB",fontSize=18,textColor=NAVY,spaceAfter=4)
H2=ParagraphStyle("h2",fontName="CalB",fontSize=12.5,textColor=BLUE,spaceBefore=10,spaceAfter=4)
P=ParagraphStyle("p",fontName="Cal",fontSize=10,leading=13.5,spaceAfter=5)
T=ParagraphStyle("t",fontName="Cal",fontSize=9,leading=11.3); TB=ParagraphStyle("tb",parent=T,fontName="CalB",textColor=HexColor("#FFFFFF"))
rows=[["Save as","Load factory","Decay","PreDelay","VLF","Early / Late","Late Rolloff","Return filter","Ducker","Send from / use"],
["CKJT Vox Sunset","Chambers 1 / #17 Sunset Chamber","1.3 s (factory 2.15)","25 ms","−20 dB (factory)","Max Early · Late −12 dB","6 kHz","LC 200 Hz","Reverb mode, thr −22 dB","Phoebe ch 7/8; both voices on duets. Ballads."],
["CKJT Vox Chamber","Chambers 1 / #10 Vocal Chamber","1.0 s (factory 1.60)","20 ms","−18 dB (from −10 factory)","Max Early · Late −14 dB","7 kHz","LC 200 Hz","Reverb mode, thr −22 dB","All vocals on up-tempo tunes."],
["CKJT Gtr Wood","Rooms 1 / #10 Large Wooden","0.75 s (factory 1.20)","10 ms","−15 dB","Max Early · Late −16 dB","7 kHz","LC 150 Hz","off","Dan Gtr ch 4, low send."],
["CKJT Piano Hall","Halls 1 / #32 Piano Hall","1.2 s (factory 2.00)","24 ms (factory)","−18 dB (from −8 factory)","Max Early · Late −14 dB","6 kHz","LC 200 Hz","off","Piano group (stereo send), low."]]
t=Table([[Paragraph(x,TB if i==0 else T) for x in r] for i,r in enumerate(rows)],colWidths=[1.0*inch,1.35*inch,0.85*inch,0.7*inch,0.95*inch,1.05*inch,0.65*inch,0.75*inch,0.95*inch,1.75*inch],repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,GREY),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#FFFFFF"),HexColor("#EEF3F8")])]))
s=[Paragraph("Seventh Heaven Pro — Memo presets",H1),
 Paragraph("The Carole King &amp; James Taylor Story · 09-28 + 09-30 · every instance 100% wet on its own FX return, level from the sends",P),
 Paragraph("Load the factory preset, set the values in the row, and save it under the name in the first column. LiquidSonics encrypts its preset files, so these can't be generated like the CLA Epic ones; dial them once and they load like any factory preset afterward.",P),
 t,
 Paragraph("Why these settings",H2),
 Paragraph("Memo adds about 1.6 s of its own decay, so every factory decay is pulled 30–40%: the room does the long tail, the reverb adds placement. VLF is cut hard and every return is low-cut at 150–250 Hz so nothing feeds the room's 125 Hz mode. Early stays at max and Late comes down, because the room supplies the late field. Pre-delay stays at 20–25 ms on the vocals to keep the words ahead of the tail. The ducker (Reverb mode) holds the early reflections between phrases while the tail ducks under the singing.",P),
 Paragraph("How they pair with CLA Epic",H2),
 Paragraph("Phoebe's songs run Sunset Chamber. Dan's run CLA Epic Slap → Plate for the 1970s tape slap. Vocal Chamber takes over on the up-tempo tunes from both of them. On duets, both vocals feed Sunset Chamber and the slap drops out. Large Wooden sits under the guitar and Piano Hall under the piano group at low sends. The Epic Throw is a button, not a bed.",P),
 Paragraph("Save location (Mac): ~/Library/Application Support/LiquidSonics/Seventh Heaven Professional/User Presets/ — copy the saved files to the same folder on the Memo rack. Preset names and factory values from the Live Sound KB reverb-reference-memo.",ParagraphStyle("c",parent=P,fontSize=8.5,textColor=HexColor("#555555")))]
SimpleDocTemplate("The Carole King and James Taylor Story - Seventh Heaven Presets.pdf",pagesize=landscape(letter),leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=0.5*inch,bottomMargin=0.5*inch,title="Seventh Heaven Presets").build(s)
