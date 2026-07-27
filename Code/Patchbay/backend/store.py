"""Sheet persistence: JSON files on disk, with a revision snapshot on every save.

data/
  sheets/<id>.json          current state
  revisions/<id>/r0007.json snapshot of the state that was replaced
  trash/<id>.json           deleted sheets (nothing is ever hard-deleted here)
"""
from __future__ import annotations

import json
import re
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHEETS = DATA / "sheets"
REVS = DATA / "revisions"
TRASH = DATA / "trash"


def _now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", (text or "sheet")).strip("-").lower()
    return s or "sheet"


class Store:
    def __init__(self) -> None:
        for d in (SHEETS, REVS, TRASH):
            d.mkdir(parents=True, exist_ok=True)

    # ---- paths -------------------------------------------------------
    def _path(self, sheet_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", sheet_id or ""):
            raise ValueError("bad sheet id")
        return SHEETS / f"{sheet_id}.json"

    # ---- read --------------------------------------------------------
    def list(self) -> list[dict]:
        out = []
        for p in SHEETS.glob("*.json"):
            try:
                s = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            consoles = s.get("consoles") or []
            channels = sum(len(c.get("channels", [])) for c in consoles) if consoles else len(s.get("inputs", []))
            out.append(
                {
                    "id": s["id"],
                    "name": s.get("name", ""),
                    "kind": s.get("kind", "install"),
                    "locked": bool(s.get("locked")),
                    "console": (consoles[0].get("preset") if consoles else s.get("console")),
                    "consoles": len(consoles) or 1,
                    "venue_label": s.get("venue_label", ""),
                    "date": s.get("date", ""),
                    "rev": s.get("rev", 1),
                    "updated": s.get("updated", ""),
                    "inputs": channels,
                    "from_template": s.get("from_template"),
                }
            )
        out.sort(key=lambda r: (r["kind"] != "install", r["updated"]), reverse=False)
        out.sort(key=lambda r: r["updated"], reverse=True)
        return out

    def get(self, sheet_id: str) -> dict:
        from .schema import migrate  # imported here: schema imports new_id from this module

        return migrate(json.loads(self._path(sheet_id).read_text(encoding="utf-8")))

    def exists(self, sheet_id: str) -> bool:
        return self._path(sheet_id).exists()

    # ---- write -------------------------------------------------------
    def create(self, sheet: dict) -> dict:
        base = _slug(sheet.get("name"))
        sheet_id = base
        n = 2
        while (SHEETS / f"{sheet_id}.json").exists():
            sheet_id = f"{base}-{n}"
            n += 1
        sheet["id"] = sheet_id
        sheet.setdefault("rev", 1)
        sheet["created"] = sheet["updated"] = _now()
        self._path(sheet_id).write_text(json.dumps(sheet, indent=1), encoding="utf-8")
        return sheet

    def save(self, sheet_id: str, sheet: dict, bump: bool = True) -> dict:
        """bump=True marks a revision: the state being replaced is snapshotted and
        the rev number goes up. Autosaves pass bump=False and just overwrite."""
        path = self._path(sheet_id)
        if path.exists():
            prev = json.loads(path.read_text(encoding="utf-8"))
            if bump:
                rev_dir = REVS / sheet_id
                rev_dir.mkdir(parents=True, exist_ok=True)
                (rev_dir / f"r{int(prev.get('rev', 1)):04d}-{int(time.time())}.json").write_text(
                    json.dumps(prev, indent=1), encoding="utf-8"
                )
            sheet["created"] = prev.get("created", _now())
            sheet["rev"] = int(prev.get("rev", 1)) + (1 if bump else 0)
        else:
            sheet.setdefault("rev", 1)
            sheet.setdefault("created", _now())
        sheet["id"] = sheet_id
        sheet["updated"] = _now()
        path.write_text(json.dumps(sheet, indent=1), encoding="utf-8")
        return sheet

    def duplicate(self, sheet_id: str, name: str, kind: str | None = None) -> dict:
        src = self.get(sheet_id)
        clone = json.loads(json.dumps(src))
        clone["name"] = name
        clone["kind"] = kind or src.get("kind", "install")
        clone["from_template"] = sheet_id if clone["kind"] == "event" else src.get("from_template")
        clone["rev"] = 1
        clone["locked"] = False  # copies are working sheets, never locked templates
        clone.pop("id", None)
        return self.create(clone)

    def delete(self, sheet_id: str) -> None:
        path = self._path(sheet_id)
        if path.exists():
            shutil.move(str(path), str(TRASH / f"{sheet_id}-{int(time.time())}.json"))

    # ---- revisions ---------------------------------------------------
    def revisions(self, sheet_id: str) -> list[dict]:
        rev_dir = REVS / sheet_id
        if not rev_dir.exists():
            return []
        out = []
        for p in sorted(rev_dir.glob("*.json"), reverse=True):
            try:
                s = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            cons = s.get("consoles") or []
            out.append(
                {
                    "file": p.name,
                    "rev": s.get("rev", 1),
                    "updated": s.get("updated", ""),
                    "inputs": sum(len(c.get("channels", [])) for c in cons) or len(s.get("inputs", [])),
                    "outputs": sum(len(c.get("outputs", [])) for c in cons) or len(s.get("outputs", [])),
                }
            )
        return out

    def revision(self, sheet_id: str, filename: str) -> dict:
        if "/" in filename or ".." in filename:
            raise ValueError("bad revision name")
        return json.loads((REVS / sheet_id / filename).read_text(encoding="utf-8"))

    def restore(self, sheet_id: str, filename: str) -> dict:
        old = self.revision(sheet_id, filename)
        old["restored_from"] = filename
        return self.save(sheet_id, old)


def new_id() -> str:
    return uuid.uuid4().hex[:8]
