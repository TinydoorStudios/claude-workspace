"""
spec.py — the ShowSpec package: the single source of truth for a show.

One ShowSpec serializes to one JSON file. The wizard (Mac now, Proxmox in
phase 2) fills it in; build.py consumes it to render the locked MD, drive the
patcher, and build the paperwork. Keeping everything in one model means the
phase-2 Proxmox instance emits exactly the JSON the Mac reads — no rework.

Bands are stored keyed by console band number (1=low .. 4=high), matching the
locked FOH Channel Processing .md convention.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional

APP_VERSION = "1.0"


@dataclass
class Band:
    """One EQ band, console numbering (1=low .. 4=high)."""
    b: int                     # 1..4
    gain: float                # dB (+boost / -cut)
    freq: float                # Hz (display)
    q: float
    type: str                  # "BELL" | "SHELF"
    deq: Optional[dict] = None  # {"thr": dB, "atk_ms": ms, "rel_ms": ms} or None

    def md_line(self) -> str:
        g = f"{int(round(self.gain)):+d}"
        line = f"B{self.b}: {g} | {int(round(self.freq))} | {self.q:g} | {self.type}"
        if self.deq:
            line += (f" | DEQ: thr={int(round(self.deq['thr']))} "
                     f"atk={int(round(self.deq['atk_ms']))}ms "
                     f"rel={int(round(self.deq['rel_ms']))}ms")
        return line


@dataclass
class Channel:
    ch: Optional[int]          # console channel number; None for unnumbered crowd mics
    name: str                  # console display name
    instrument: str            # instrument key or free text
    mic: str = ""
    section: str = "SPARE"
    phantom: bool = False
    ribbon: bool = False
    stand: str = "—"
    notes: str = ""
    hpf: Optional[float] = None
    lpf: Optional[float] = None     # None or >=20000 means OFF
    bands: list = field(default_factory=list)   # list[Band]
    comp: Optional[dict] = None      # {"thr","ratio","atk_ms","rel_ms"} or None
    gate: bool = False
    is_crowd: bool = False
    mic_notes: str = ""
    eq_summary: str = ""
    research: str = ""          # live per-source web research note (Nyquist research pass)

    def to_dict(self):
        d = asdict(self)
        d["bands"] = [asdict(b) if isinstance(b, Band) else b for b in self.bands]
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        d["bands"] = [Band(**b) for b in d.get("bands", [])]
        return cls(**d)


@dataclass
class ReverbRec:
    bank: str
    num: str
    name: str
    decay_s: Optional[float] = None
    predelay_ms: Optional[float] = None
    vlf: str = ""
    early_late: str = ""
    late_rolloff: str = ""
    use: str = ""
    rationale: str = ""

    def line(self) -> str:
        """The locked reverb line format from the KB."""
        bits = []
        if self.decay_s is not None:
            bits.append(f"Decay {self.decay_s:g}s")
        if self.predelay_ms is not None:
            bits.append(f"PreDelay {int(round(self.predelay_ms))}ms")
        if self.vlf:
            bits.append(f"VLF {self.vlf}")
        if self.early_late:
            bits.append(f"E/L {self.early_late}")
        if self.late_rolloff:
            bits.append(f"Late Rolloff {self.late_rolloff}")
        settings = " • ".join(bits)
        head = f"{self.bank} / #{self.num} {self.name}"
        tail = f" — {self.rationale}" if self.rationale else ""
        return f"Preset: {head} | {settings}{tail}"


@dataclass
class ShowSpec:
    venue: str = "memo"
    show_name: str = ""
    artist: str = ""
    genre: str = ""
    show_date: str = field(default_factory=lambda: date.today().isoformat())
    foh_engineer: str = "Brian Lloyd"
    mon_engineer: str = "TBD"
    show_time: str = "TBD"
    rev: str = "Rev 1.0"
    eq_on: bool = True
    comp_on: bool = False
    channels: list = field(default_factory=list)     # list[Channel]
    reverbs: list = field(default_factory=list)       # list[ReverbRec]
    reverb_note: str = ""                             # venue context note for the reverb set
    new_mics: list = field(default_factory=list)      # mics typed in the wizard, queued for the KB
    artist_profile: str = ""                          # performance-sound profile from the artist research pass
    research_summary: str = ""                        # what the research pass found + sources (per build)
    app_version: str = APP_VERSION

    # ---- serialization -------------------------------------------------
    def to_dict(self):
        return {
            "venue": self.venue,
            "show_name": self.show_name,
            "artist": self.artist,
            "genre": self.genre,
            "show_date": self.show_date,
            "foh_engineer": self.foh_engineer,
            "mon_engineer": self.mon_engineer,
            "show_time": self.show_time,
            "rev": self.rev,
            "eq_on": self.eq_on,
            "comp_on": self.comp_on,
            "channels": [c.to_dict() for c in self.channels],
            "reverbs": [asdict(r) for r in self.reverbs],
            "reverb_note": self.reverb_note,
            "new_mics": self.new_mics,
            "artist_profile": self.artist_profile,
            "research_summary": self.research_summary,
            "app_version": self.app_version,
        }

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        d["channels"] = [Channel.from_dict(c) for c in d.get("channels", [])]
        d["reverbs"] = [ReverbRec(**r) for r in d.get("reverbs", [])]
        known = cls.__dataclass_fields__.keys()
        return cls(**{k: v for k, v in d.items() if k in known})

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    # ---- helpers -------------------------------------------------------
    def slug(self) -> str:
        import re
        s = re.sub(r"[^A-Za-z0-9]+", "_", self.show_name).strip("_")
        return s or "Untitled_Show"

    def folder_name(self) -> str:
        return f"{self.show_date} {self.show_name}".strip()
