"""Reference data: console I/O surfaces, sections, mic library."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
# Prefer ShowBuilder's live mic library so the two tools never drift.
SHOWBUILDER_MICS = ROOT.parent / "ShowBuilder" / "knowledge" / "mics.json"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class Knowledge:
    def __init__(self) -> None:
        data = _load(KNOWLEDGE / "consoles.json")
        self.consoles = {c["id"]: c for c in data["consoles"]}
        self.sections = data["sections"]
        self.stands = data["stands"]
        self.venues = data["venues"]
        self.mics = self._load_mics()

    def _load_mics(self) -> list[dict]:
        path = SHOWBUILDER_MICS if SHOWBUILDER_MICS.exists() else KNOWLEDGE / "mics.json"
        mics = _load(path)["mics"]
        return [
            {
                "name": m["name"],
                "aka": m.get("aka") or [],
                "type": m.get("type", ""),
                "phantom": bool(m.get("phantom")),
                "ribbon": bool(m.get("ribbon")),
            }
            for m in mics
        ]

    def console(self, console_id: str) -> dict:
        if console_id not in self.consoles:
            raise KeyError(f"unknown console: {console_id}")
        return self.consoles[console_id]

    def ports(self, console_id: str, direction: str = "in") -> list[dict]:
        """Expand a console's port groups into concrete port names."""
        key = "input_ports" if direction == "in" else "output_ports"
        groups = []
        for grp in self.console(console_id)[key]:
            names = [grp["fmt"].format(n=i) for i in range(1, grp["count"] + 1)]
            groups.append({**grp, "ports": names})
        return groups

    def mic(self, name: str) -> dict | None:
        if not name:
            return None
        needle = name.strip().lower()
        for m in self.mics:
            if m["name"].lower() == needle or needle in [a.lower() for a in m["aka"]]:
                return m
        for m in self.mics:
            if needle and needle in m["name"].lower():
                return m
        return None

    def bootstrap(self) -> dict:
        return {
            "consoles": [
                {
                    "id": c["id"],
                    "label": c["label"],
                    "vendor": c["vendor"],
                    "accent": c["accent"],
                    "title_color": c["title_color"],
                    "channels": c["channels"],
                    "channel_label": c["channel_label"],
                    "buses": c["buses"],
                    "input_ports": self.ports(c["id"], "in"),
                    "output_ports": self.ports(c["id"], "out"),
                    "bus_seed": c["bus_seed"],
                }
                for c in self.consoles.values()
            ],
            "sections": self.sections,
            "stands": self.stands,
            "venues": self.venues,
            "mics": self.mics,
        }
