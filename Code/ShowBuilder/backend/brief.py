"""
brief.py — the facts-only Show Brief: the single thing ShowBuilder exports.

The app captures the input list + show metadata and rounds-tripped free-text
notes; it does NOT compute EQ. One Brief serializes to one <Show>.brief.json,
which the `show-deep-build` skill reads to research the artist + every source
and produce the EQ, the paperwork, and the .ses downstream.

Hard contract (see docs/HANDOFF.md):
  * no EQ fields — no hpf/lpf/bands/comp/gate/mic_notes/eq_summary, ever
  * `notes` and `show_notes` are unconstrained free text, preserved verbatim —
    they are the deep build's research hooks (amps, miking techniques, etc.)
  * a true spare channel is omitted entirely, not emitted blank
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional

APP_VERSION = "brief-1.0"

# sections used downstream for color-coding / grouping
SECTIONS = ("DRUMS", "BASS", "RHYTHM", "GUITAR", "KEYS", "PIANO",
            "STRINGS", "HORNS", "VOCALS", "AMBIENT")


@dataclass
class BriefChannel:
    ch: Optional[int]            # console channel; None for unnumbered crowd mics
    name: str                    # fader label
    instrument: str = ""
    mic: str = ""                # full name, no shorthand
    section: str = "SPARE"
    phantom: bool = False
    ribbon: bool = False         # true -> downstream flags NO 48V red
    stand: str = "—"             # Short/Tall/Boom/Bar/Clip/DI/—
    patch: str = ""              # optional; defaults to "Local <ch>" downstream
    notes: str = ""              # free text, mined verbatim — NEVER normalized
    is_crowd: bool = False

    def to_dict(self):
        d = {
            "ch": self.ch,
            "name": self.name,
            "instrument": self.instrument,
            "mic": self.mic,
            "section": self.section,
            "phantom": self.phantom,
            "ribbon": self.ribbon,
            "stand": self.stand,
            "patch": self.patch or (f"Local {self.ch}" if self.ch else ""),
            "notes": self.notes,
        }
        if self.is_crowd:
            d["is_crowd"] = True
        return d


@dataclass
class Brief:
    show_name: str = ""
    artist: str = ""
    genre: str = ""               # free-text genre hint — a fact, not EQ
    venue: str = "memo"
    venue_label: str = ""
    console_label: str = ""
    show_date: str = field(default_factory=lambda: date.today().isoformat())
    foh_engineer: str = "Brian Lloyd"
    mon_engineer: str = "TBD"
    show_time: str = "TBD"
    rev: str = "Rev 1.0"
    show_notes: str = ""          # free text, mined
    channels: list = field(default_factory=list)   # list[BriefChannel]
    app_version: str = APP_VERSION

    # ---- serialization -------------------------------------------------
    def to_dict(self):
        return {
            "show_name": self.show_name,
            "artist": self.artist,
            "genre": self.genre,
            "venue": self.venue,
            "venue_label": self.venue_label,
            "console_label": self.console_label,
            "show_date": self.show_date,
            "foh_engineer": self.foh_engineer,
            "mon_engineer": self.mon_engineer,
            "show_time": self.show_time,
            "rev": self.rev,
            "show_notes": self.show_notes,
            "channels": [c.to_dict() for c in self.channels],
            "app_version": self.app_version,
        }

    def json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.json())

    # ---- helpers -------------------------------------------------------
    def slug(self) -> str:
        s = re.sub(r"[^A-Za-z0-9]+", "_", self.show_name).strip("_")
        return s or "Untitled_Show"

    def folder_name(self) -> str:
        return f"{self.show_date} {self.show_name}".strip()
