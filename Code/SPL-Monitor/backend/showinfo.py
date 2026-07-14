"""Show/engineer banner — pulled from Brian's public 3CDC scheduling Google Sheets.

Three public "publish to web" CSVs, no auth needed:
  - schedule sheet: day-by-venue grid (FSQ block = date/DOTW/event/mix-code columns)
  - codes sheet: mix-code -> full name lookup (second tab of the same spreadsheet)
  - band sheet: date/location/performer rows — gives the actual band/event name
    when the schedule-sheet event is just a placeholder ("TBD", "Reggae (4-11)", etc.)

Refreshed on a timer (not per-request) for the live dashboard banner, since it's a
Google Sheets export and the data only changes when someone edits the sheet.
`for_date()` re-fetches on demand for the nightly email, which may be asked for a
report day other than "today".
"""

import asyncio
import csv
import datetime
import io
from zoneinfo import ZoneInfo

import aiohttp

TZ = ZoneInfo("America/New_York")


def _export_url(sheet_id, gid):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _parse_date(s):
    s = (s or "").strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _lookup(schedule_rows, codes_rows, band_rows, date_obj, schedule_col, band_col, band_location):
    codes = {}
    for row in codes_rows[1:]:
        if len(row) < 3 or not row[0].strip():
            continue
        name = f"{row[1].strip()} {row[2].strip()}".strip()
        if name:
            codes[row[0].strip()] = name

    sc = schedule_col
    need = max(sc.values())
    event, mix_code = None, None
    for row in schedule_rows:
        if len(row) <= need:
            continue
        if _parse_date(row[sc["date"]]) == date_obj:
            event = (row[sc["event"]] or "").split("\n")[0].strip() or None
            mix_code = (row[sc["mix"]] or "").strip() or None
            break

    bc = band_col
    need_b = max(bc.values())
    loc_want = band_location.strip().upper()
    band = None
    for row in band_rows:
        if len(row) <= need_b:
            continue
        if row[bc["location"]].strip().upper() != loc_want:
            continue
        if _parse_date(row[bc["date"]]) == date_obj:
            band = (row[bc["performer"]] or "").strip() or None
            break

    engineer = codes.get(mix_code, mix_code) if mix_code else None
    return {
        "date": date_obj.isoformat(),
        "show": band or event,
        "event": event,
        "band": band,
        "engineer": engineer,
        "engineerCode": mix_code,
    }


class ShowInfoTracker:
    def __init__(self, cfg):
        si = cfg.get("showInfo", {}) or {}
        self.enabled = bool(si.get("enabled", False))
        self.refresh_seconds = int(si.get("refreshSeconds", 300))
        self.schedule_url = None
        self.codes_url = None
        self.band_url = None
        if self.enabled:
            self.schedule_url = _export_url(si["scheduleSheetId"], si["scheduleGid"])
            self.codes_url = _export_url(si["scheduleSheetId"], si["codesGid"])
            self.band_url = _export_url(si["bandSheetId"], si["bandGid"])
        self.schedule_col = si.get(
            "scheduleColumns", {"date": 6, "dotw": 7, "event": 8, "mix": 9})
        self.band_col = si.get(
            "bandColumns", {"date": 1, "location": 2, "performer": 4})
        self.band_location = si.get("bandLocation", "FSQ")
        self.current_data = {
            "date": None, "show": None, "event": None, "band": None,
            "engineer": None, "engineerCode": None, "updatedAt": None,
        }

    async def _fetch_csv(self, session, url):
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = await resp.text()
        return list(csv.reader(io.StringIO(text)))

    async def _fetch_all(self):
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(
                self._fetch_csv(session, self.schedule_url),
                self._fetch_csv(session, self.codes_url),
                self._fetch_csv(session, self.band_url),
            )

    async def refresh(self):
        """Pull all three sheets and recompute today's show/engineer. Returns True if changed."""
        if not self.enabled:
            return False
        try:
            rows = await self._fetch_all()
        except Exception as e:  # noqa: BLE001
            print(f"[showinfo] fetch failed: {e!r}", flush=True)
            return False

        today = datetime.datetime.now(TZ).date()
        data = _lookup(*rows, today, self.schedule_col, self.band_col, self.band_location)
        data["updatedAt"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

        changed = (data["show"] != self.current_data.get("show")
                   or data["engineer"] != self.current_data.get("engineer")
                   or data["date"] != self.current_data.get("date"))
        self.current_data = data
        return changed

    async def for_date(self, day):
        """Look up show/band/engineer for an arbitrary report day — used by the
        nightly email, which may be regenerated for a day other than 'today'.
        day: 'YYYY-MM-DD' string, a date object, or None (= today)."""
        if not self.enabled:
            return {}
        if isinstance(day, str):
            date_obj = datetime.date.fromisoformat(day)
        elif isinstance(day, datetime.date):
            date_obj = day
        else:
            date_obj = datetime.datetime.now(TZ).date()
        try:
            rows = await self._fetch_all()
        except Exception as e:  # noqa: BLE001
            print(f"[showinfo] for_date fetch failed: {e!r}", flush=True)
            return {}
        return _lookup(*rows, date_obj, self.schedule_col, self.band_col, self.band_location)

    def current(self):
        return dict(self.current_data)
