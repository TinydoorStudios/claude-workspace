from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
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
T=ParagraphStyle("t",fontName="Cal",fontSize=9.2,leading=11.5); TB=ParagraphStyle("tb",parent=T,fontName="CalB",textColor=HexColor("#FFFFFF"))
def tbl(rows,w=(1.35*inch,1.85*inch,3.9*inch)):
    t=Table([[Paragraph(str(x),TB if i==0 else T) for x in r] for i,r in enumerate(rows)],colWidths=w,repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,GREY),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#FFFFFF"),HexColor("#EEF3F8")])])); return t
H=["Section","Control","Setting"]
glob=lambda comp:[["Global","Component",comp],["Global","Input fader","0 dB (set the send so the input meter peaks around −12)"],["Global","Wet/Dry","100% wet, LOCK on (it's a return)"],["Global","Output fader","0 dB"]]
s=[Paragraph("CLA Epic — Memo settings",H1),
 Paragraph("The Carole King &amp; James Taylor Story · 09-28 + 09-30 · three instances, each on its own FX return, 100% wet, level set by the sends",P),
 Paragraph("<b>Mute every processor you aren't using.</b> Per the Waves guide, if nothing is routed, the input feeds all four delays and all four reverbs, so an unmuted, unrouted module is live. Epic has no ducker; if the vocal returns crowd the words, put a light sidechain compressor on the return, keyed from the vocal. Sync follows the host's tempo, and Epic isn't hosted at Memo yet, so every delay below has Sync OFF and fixed ms.",P),
 Paragraph("Instance 1 — DAN SLAP (Slap → Plate)",H2),
 Paragraph("Send: Dan (ch 6) on his numbers. Pull the send down on the duets, where Sunset Chamber carries both voices. Gives the 1970s tape slap on the JT vocal plus a record-style plate.",P),
 tbl([H]+glob("Mono-to-Stereo")+[
  ["Slap","VSO","15 IPS = 166 ms (loads that speed's EQ curve)"],
  ["Slap","Sync","OFF"],["Slap","Feedback","0%"],["Global","Master Mod (dly/vrb)","0 / 0"],
  ["Slap","HP / LP","200 Hz / 8 kHz"],["Slap","Fader","0 dB"],
  ["Slap","Routing","OUT on (level 0 dB) + A (Plate) on, send −10 dB in the Routing panel"],
  ["Plate (A)","Pre-delay","30 ms"],["Plate (A)","Reverb Time","1.2 s"],["Plate (A)","RT Low","position 1 of 3 (lowest, least LF decay)"],["Plate (A)","RT High","position 2 of 3 (middle)"],
  ["Plate (A)","HP / LP","200 Hz / 8 kHz"],["Plate (A)","Fader","−4 dB"],
  ["Mute","","Tape, Throw, Crowd, Room (B), Hall (C), Space (D)"]]),
 Paragraph("Instance 2 — VOCAL THROW (Throw → Hall)",H2),
 Paragraph("Send: ch 6, 7 and 8 all feed it at a moderate level. Nothing comes out until you hold Trigger. Use it on the last line of a chorus ('you've got a friend'), then let go.",P),
 tbl([H]+glob("Mono-to-Stereo")+[
  ["Throw","Tap 1 / Tap 2","375 ms / 500 ms"],["Throw","Sync","OFF"],["Throw","Feedback","25% (both taps)"],
  ["Throw","Offset","0%"],["Throw","Trigger","turn ON after loading, then re-save (see note)"],["Global","Master Delay Mod","10"],
  ["Throw","HP / LP","250 Hz / 6 kHz"],["Throw","Fader","0 dB"],
  ["Throw","Routing","OUT on (level 0 dB) + C (Hall) on, send −12 dB"],
  ["Hall (C)","Pre-delay","40 ms"],["Hall (C)","Reverb Time","1.8 s"],["Hall (C)","RT Low","position 1 of 3 (lowest)"],["Hall (C)","RT High","position 2 of 3 (middle)"],
  ["Hall (C)","HP / LP","250 Hz / 6 kHz"],["Hall (C)","Fader","−6 dB"],
  ["Mute","","Tape, Slap, Crowd, Plate (A), Room (B), Space (D)"]]),
 Paragraph("Instance 3 — DUO WIDTH (Crowd) · audition at soundcheck",H2),
 Paragraph("Send: Dan and Phoebe vocals plus a little guitar. Crowd builds a cluster of early reflections that widen and thicken without a tail, which can open up a two-voice show on Memo's PA without adding wash. It isn't in the Rev 1.0 packet; keep it only if it earns its place.",P),
 tbl([H]+glob("Stereo")+[
  ["Crowd","Tight ↔ Wide","About 25% of the way from Tight (short taps; Wide gets smeary in a 1.6 s room)"],
  ["Crowd","HP / LP","300 Hz / 10 kHz"],["Crowd","Fader","−6 dB"],["Crowd","Routing","OUT only (no reverb)"],
  ["Mute","","Tape, Throw, Slap, all four reverbs"]]),
 Paragraph("Soundcheck order",H2),
 Paragraph("Bring up Instance 1 on Dan alone and set the slap send until you notice it when you mute it, not before. Fire the Throw on a held phrase and adjust Hall (C) fader to taste. Solo-in-place Instance 3, then A/B it on a duet. If any return reads as mud in the room, raise that processor's HP before touching the send. All times are fixed ms; if Epic later lands on a host with tap tempo, switch the Throw to Sync 1/4 + dotted 1/8 and keep everything else.",P),
 Paragraph("Loadable presets: 'CLA Epic Presets' folder in the show folder and on the Desktop (CKJT Dan Slap / Vocal Throw / Duo Width, plus one file with all three), built on the plug-in's own parameter map (ParamXML) and Brian's CLA #1 preset. The Throw's Trigger mode is the one switch that couldn't be confirmed from the file format: after loading, turn Trigger ON and re-save. Source: Waves CLA Epic User Guide v2 (control names, ranges and routing behavior). Values are custom; Waves doesn't publish its factory preset names.",ParagraphStyle("c",parent=P,fontSize=8.5,textColor=HexColor("#555555")))]
SimpleDocTemplate("The Carole King and James Taylor Story - CLA Epic Settings.pdf",pagesize=letter,leftMargin=0.6*inch,rightMargin=0.6*inch,topMargin=0.6*inch,bottomMargin=0.6*inch,title="CLA Epic Settings").build(s)
