#!/usr/bin/env python3
"""C3-specific placement diagrams for the 4099 deep-dive."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Ellipse, Rectangle, FancyBboxPatch, Polygon, Arc, PathPatch
from matplotlib.path import Path
import numpy as np

NAVY="#1A1A2E"; BLUE="#0F3460"; ACCENT="#E94560"; WOOD="#E8E4D4"; GOLD="#C9A24B"
BRASS="#E8D4A0"; PAPER="#FBFAF6"; GREY="#9AA0AB"; INK="#22232b"; TEAL="#0F7A6B"
AMBER="#FFB347"

plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11})

def newfig(w=7.4,h=4.6):
    fig,ax=plt.subplots(figsize=(w,h),dpi=200)
    ax.set_xlim(0,10); ax.set_ylim(0,6.4); ax.axis("off")
    fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
    return fig,ax

def mic(ax,x,y,r=0.15,color=ACCENT):
    ax.add_patch(Circle((x,y),r,fc=color,ec="white",lw=1.3,zorder=8))
    ax.add_patch(Circle((x,y),r*2.0,fc="none",ec=color,lw=0.9,ls=(0,(2,2)),zorder=7))

def aim(ax,x0,y0,x1,y1,color=ACCENT,ls="-",lw=2.0):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle="-|>",mutation_scale=14,
                 lw=lw,color=color,ls=ls,zorder=6))

def title(ax,t,sub=None):
    ax.text(0.2,6.1,t,fontsize=15.5,color=NAVY,weight="bold",va="top")
    if sub: ax.text(0.2,5.62,sub,fontsize=10.5,color=BLUE,va="top")

def cap(ax,t,y=0.18):
    ax.text(0.2,y,t,fontsize=8.6,color=GREY,style="italic",va="bottom")

# ============================================== A: top-view spaced pair
def c3_topview():
    fig,ax=newfig(7.8,5.4)
    ax.set_xlim(0,10); ax.set_ylim(0,7.2)
    ax.text(0.2,6.95,"C3 spaced pair — top view (lid removed for clarity)",fontsize=15,color=NAVY,weight="bold",va="top")
    ax.text(0.2,6.5,"Your two 4099P over the strings: one bass, one treble",fontsize=10.5,color=BLUE,va="top")
    lbl=dict(boxstyle="round,pad=0.3",fc="white",ec=ACCENT,lw=1.3)
    nbl=dict(boxstyle="round,pad=0.25",fc="white",ec=NAVY,lw=1.0)

    # piano case lower-center, leaving white margins for labels
    case=Polygon([(2.0,1.5),(7.6,1.5),(8.3,3.0),(7.9,4.3),(6.2,5.1),(2.0,5.1)],
                 closed=True,fc=NAVY,ec=NAVY,zorder=1)
    ax.add_patch(case)
    plate=Polygon([(2.25,1.75),(7.3,1.75),(7.95,3.0),(7.6,4.15),(6.1,4.85),(2.25,4.85)],
                  closed=True,fc=GOLD,ec="#9c7c34",lw=1.2,zorder=2)
    ax.add_patch(plate)
    # keyboard strip
    ax.add_patch(Rectangle((2.25,1.28),5.05,0.42,fc="white",ec=NAVY,lw=1,zorder=3))
    for kx in np.linspace(2.4,7.2,26):
        ax.plot([kx,kx],[1.28,1.70],color=NAVY,lw=0.5,zorder=4)
    ax.text(4.6,1.05,"keyboard / hammers (strike line)",ha="center",fontsize=8,color=NAVY)
    # dampers line
    ax.plot([2.4,7.1],[2.15,2.15],color="#6b5a2a",lw=2,zorder=4)
    ax.text(2.35,2.26,"dampers",fontsize=7.2,color="#6b5a2a")
    # bass strings
    for yy in np.linspace(2.35,4.4,8):
        ax.plot([2.5,6.4],[yy,2.45+(yy-2.35)*0.12],color="#6e6e78",lw=1.0,zorder=3,alpha=0.75)
    # treble strings
    for xx in np.linspace(5.2,7.1,18):
        ax.plot([xx,xx*0.97+0.2],[2.3,4.1],color="#8a909b",lw=0.5,zorder=3,alpha=0.65)
    # soundholes
    ax.add_patch(Circle((6.0,3.4),0.14,fc=NAVY,ec="#6b5a2a",lw=1,zorder=4))
    ax.add_patch(Circle((6.4,2.95),0.11,fc=NAVY,ec="#6b5a2a",lw=1,zorder=4))
    ax.text(3.3,4.55,"bass strings (cross over)",fontsize=7.4,color="white",ha="center",zorder=5)
    ax.text(6.7,4.3,"treble",fontsize=7.4,color=NAVY,ha="center")

    # MICS
    bx,by=3.3,3.1
    tx,ty=5.5,2.8
    mic(ax,bx,by); mic(ax,tx,ty)
    aim(ax,bx,by,bx-0.15,by-0.55); aim(ax,tx,ty,tx+0.1,ty-0.55)
    # labels in white margin (top), leader lines to mics
    ax.annotate("BASS mic\nover C2–G2, ~⅓ down the strings",
                xy=(bx,by),xytext=(2.0,6.0),fontsize=8.4,color=INK,ha="center",
                bbox=lbl,arrowprops=dict(arrowstyle="-",color=ACCENT,lw=1.2),zorder=9)
    ax.annotate("TREBLE mic\n~oct-and-a-half above middle C (~G5)",
                xy=(tx,ty),xytext=(7.7,5.9),fontsize=8.4,color=INK,ha="center",
                bbox=lbl,arrowprops=dict(arrowstyle="-",color=ACCENT,lw=1.2),zorder=9)
    # spacing bracket between mics
    ax.annotate("",xy=(bx,by-0.78),xytext=(tx,ty-0.78),arrowprops=dict(arrowstyle="<->",color=NAVY,lw=1.3))
    ax.text((bx+tx)/2,3.55,"≥ 30 cm",ha="center",fontsize=8.6,color=NAVY,weight="bold",
            bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none"),zorder=8)
    ax.text((bx+tx)/2+0.1,0.55,"closer → comb filter      too far → hole in the middle",
            ha="center",fontsize=8,color=ACCENT,weight="bold")
    ax.text(0.2,0.18,"Height ~25–30 cm (10–12 in) over the strings, angled down toward the soundboard. Always mono-sum the pair and check phase.",
            fontsize=8.4,color=GREY,style="italic")
    fig.savefig("c3_topview.png",bbox_inches="tight",facecolor=PAPER); plt.close(fig)

# ============================================== B: open vs closed lid
def c3_lids():
    fig,ax=newfig(7.6,4.4)
    title(ax,"Your two cases — open lid vs closed lid (side view)","Same spaced pair; the lid changes everything")
    # ---- OPEN (left) ----
    ox=2.6
    ax.add_patch(Rectangle((ox-1.7,1.3),3.0,0.5,fc=NAVY,ec=NAVY))      # case
    ax.add_patch(Rectangle((ox-1.7,1.8),3.0,0.18,fc=GOLD,ec="#9c7c34"))# plate/strings top
    # open lid on full stick
    ax.add_patch(Polygon([(ox-1.7,1.98),(ox-1.5,4.4),(ox+0.2,4.0)],closed=True,fc="#0d0d18",ec=NAVY))
    ax.plot([ox+0.2,ox+0.25],[4.0,1.98],color=NAVY,lw=2)  # stick
    # mic over strings
    mic(ax,ox-0.2,2.5); aim(ax,ox-0.2,2.5,ox-0.2,2.0)
    # reflection arrows off lid to audience (right)
    aim(ax,ox-0.2,2.15,ox-1.3,3.6,color=AMBER,lw=1.6)
    aim(ax,ox-1.3,3.6,ox+2.3,2.6,color=AMBER,lw=1.6,ls=(0,(3,2)))
    ax.text(ox-0.1,4.6,"FULL STICK / OPEN",ha="center",fontsize=10,color=NAVY,weight="bold")
    ax.text(ox-0.1,1.0,"natural & open · max projection",ha="center",fontsize=8,color=INK)
    ax.text(ox-0.1,0.75,"most bleed + feedback risk",ha="center",fontsize=8,color=ACCENT)
    # ---- CLOSED (right) ----
    cx=7.3
    ax.add_patch(Rectangle((cx-1.7,1.3),3.0,0.5,fc=NAVY,ec=NAVY))
    ax.add_patch(Rectangle((cx-1.7,1.8),3.0,0.18,fc=GOLD,ec="#9c7c34"))
    # closed lid flat on top
    ax.add_patch(Rectangle((cx-1.75,2.45),3.1,0.18,fc="#0d0d18",ec=NAVY))
    ax.add_patch(Polygon([(cx-1.75,2.45),(cx-1.55,2.0),(cx+1.35,2.0),(cx+1.35,2.45)],closed=True,fc="#0d0d18",ec=NAVY,alpha=0.6))
    # mic on frame magnet, low profile under lid
    mic(ax,cx-0.2,2.18); aim(ax,cx-0.2,2.18,cx-0.2,2.0)
    ax.text(cx-0.2,2.72,"lid closed",ha="center",fontsize=7.5,color="white")
    # trapped reflections (bouncing arrows inside)
    aim(ax,cx-0.6,2.1,cx+0.4,2.35,color=AMBER,lw=1.3,ls=(0,(2,2)))
    aim(ax,cx+0.4,2.35,cx-0.3,2.05,color=AMBER,lw=1.3,ls=(0,(2,2)))
    ax.text(cx-0.1,4.6,"CLOSED / LID DOWN",ha="center",fontsize=10,color=NAVY,weight="bold")
    ax.text(cx-0.1,1.0,"max isolation · darker & boxier",ha="center",fontsize=8,color=INK)
    ax.text(cx-0.1,0.75,"comb-filter risk · phase-check",ha="center",fontsize=8,color=ACCENT)
    cap(ax,"Closed lid traps reflections under the lid → boxiness (200–400 Hz) and comb filtering. Wider mic spacing + EQ tame it.",y=0.05)
    fig.savefig("c3_lids.png",bbox_inches="tight",facecolor=PAPER); plt.close(fig)

# ============================================== C: tone/distance axis
def c3_tone():
    fig,ax=newfig(7.6,4.2)
    title(ax,"Where you aim sets the tone","Distance from hammers and height over strings")
    # axes box
    ax.add_patch(Rectangle((1.6,1.2),6.6,3.4,fc="white",ec=NAVY,lw=1.2))
    # x axis: hammers -> tail
    ax.annotate("",xy=(8.1,1.2),xytext=(1.6,1.2),arrowprops=dict(arrowstyle="-|>",color=NAVY,lw=1.4))
    ax.text(2.0,0.9,"NEAR HAMMERS / strike line",fontsize=8.2,color=NAVY,weight="bold")
    ax.text(6.4,0.9,"TOWARD TAIL / soundboard",fontsize=8.2,color=NAVY,weight="bold")
    ax.text(2.0,0.62,"attack, bite, >130 dB peaks",fontsize=7.4,color=ACCENT)
    ax.text(6.4,0.62,"body, warmth, blend",fontsize=7.4,color=TEAL)
    # y axis: close -> far (height)
    ax.annotate("",xy=(1.6,4.8),xytext=(1.6,1.2),arrowprops=dict(arrowstyle="-|>",color=NAVY,lw=1.4))
    ax.text(1.5,4.95,"higher / further = more blend, less proximity",fontsize=7.6,color=NAVY,ha="left")
    ax.text(0.35,1.4,"closer",fontsize=7.6,color=NAVY,rotation=90)
    ax.text(0.35,3.9,"further",fontsize=7.6,color=NAVY,rotation=90)
    # plotted sweet spots
    pts=[(2.6,2.0,"Percussive jazz comp\n(close, near hammers)",ACCENT),
         (4.6,3.0,"Balanced live\n(mid, ~25–30 cm up)",BLUE),
         (6.6,3.8,"Natural / classical\n(back, higher, open lid)",TEAL)]
    for x,y,lab,c in pts:
        ax.add_patch(Circle((x,y),0.13,fc=c,ec="white",lw=1.2,zorder=6))
        ax.text(x,y+0.45,lab,ha="center",fontsize=7.8,color=c,weight="bold")
    # extreme spl flag
    ax.text(2.6,1.55,"Extreme SPL\nheadroom lives here",ha="center",fontsize=7.2,color=ACCENT,style="italic")
    cap(ax,"Closer + nearer the hammers = attack and proximity bass (HPF harder). Back and higher = body and room blend.",y=0.04)
    fig.savefig("c3_tone.png",bbox_inches="tight",facecolor=PAPER); plt.close(fig)

for fn in (c3_topview,c3_lids,c3_tone):
    fn()
print("c3 diagrams done")
