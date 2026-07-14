"""
AC Infinity cloud API client.

Wraps the (community-reverse-engineered) cloud endpoints the phone app uses.
There is no local/LAN API on the hardware — everything routes through
acinfinityserver.com. Confirmed working against Brian's account 2026-06-29
for login, device list, per-port settings read, on all three controllers
including the Controller AI (devType 20).

WRITE SAFETY: writes use read-modify-write of the WHOLE mode payload — we fetch
the port's current settings, change only the requested fields, and post the full
set back (same as Brian's "never partially rewrite a .env" rule). The field
spellings are quirky on purpose (`onSpead`, `acitveTimerOn`) — they're echoed
verbatim from the API, so we never have to hand-type them.
"""

import asyncio
import json
import time

import aiohttp

BASE = "http://www.acinfinityserver.com"
UA = ("ACController/1.8.2 (com.acinfinity.humiture; build:489; iOS 16.5.1) "
      "Alamofire/5.4.4")

# Active-mode enum (atType / curMode) -> label  [basic per-port layer]
MODE_LABELS = {
    1: "Off", 2: "On", 3: "Auto", 4: "Timer to On", 5: "Timer to Off",
    6: "Cycle", 7: "Schedule", 8: "VPD",
}

# --- Advance Automation ("Groups", v2.0 API) --------------------------------
# Confirmed from captured app traffic: currentMode 3=Cycle, 4=Auto.
GROUP_MODE_LABELS = {3: "Cycle", 4: "Auto"}
# Device-type of the group's attached load.
GROUP_DEV_TYPES = {1: "Light", 2: "Humidifier", 6: "Fan"}

# Exact field set the app posts to updateGroupsById (69 keys). All but the
# handful of port/lang fields come straight from the getGroups response;
# read-modify-write preserves everything and overrides only what's asked.
GROUP_UPDATE_KEYS = [
    "advId", "advName", "devId", "currentMode", "isOn", "grouptDevType",
    "portType", "portState", "templateType", "setSelect", "sortType",
    "groupNums", "subNumber", "subNumberSort", "isFlag", "isDel",
    "onSpeed", "offSpeed", "runState",
    "autoHighTempF", "autoHighTempC", "autoLowTempF", "autoLowTempC",
    "autoHighTempSwitch", "autoLowTempSwitch",
    "autoHighHumi", "autoLowHumi", "autoHighHumiSwitch", "autoLowHumiSwitch",
    "highVpd", "lowVpd", "highVpdSwitch", "lowVpdSwitch",
    "targetTemp", "targetTempF", "targetHumi", "targetVpd",
    "targetTSwitch", "targetHumiSwitch", "targetVpdSwitch",
    "beginTime", "endTime", "cycleOn", "cycleOff", "switchTime",
    "settingMode", "onTime", "onTimeSwitch", "isOnMinMaxTime",
    "onMinTime", "onMaxTime", "isOpenDoseTime", "onDoseTime", "offDoseTime",
    "photocellSwitch", "dualZoneSwitch",
    "temperatureFTrans", "humidityTrans", "vpdTrans",
    "temperatureFBuff", "humidityBuff", "vpdBuff",
    "switchTemperatureFBuff", "switchHumidityBuff", "switchVpdBuff",
]
# Update-only fields not present in the getGroups response; the app sends these.
GROUP_UPDATE_DEFAULTS = {
    "insidePort": 0, "insideType": 0, "outsidePort": 0, "outsideType": 0,
    "portSetHex": "", "portStateHex": "", "nameLangKey": "", "remarkLangKey": "",
}
# Only these fields may be changed via the dashboard — keeps writes to the
# well-understood, reversible settings and never touches mode/device wiring.
GROUP_WRITABLE = {
    "isOn", "onSpeed", "offSpeed",
    "autoHighTempF", "autoLowTempF", "autoHighTempSwitch", "autoLowTempSwitch",
    "autoHighHumi", "autoLowHumi", "autoHighHumiSwitch", "autoLowHumiSwitch",
    "targetTempF", "targetHumi", "targetVpd",
    "targetTSwitch", "targetHumiSwitch", "targetVpdSwitch",
    "beginTime", "endTime", "cycleOn", "cycleOff",
}

# Keys that make up a mode-settings write. Values are pulled from the live
# fetch and selectively overridden; this mirrors the known-good payload the
# phone app and the Home Assistant integration send to addDevMode.
MODE_PAYLOAD_KEYS = [
    "atType", "onSpead", "offSpead", "onSelfSpead",
    "devHt", "devLt", "devHh", "devLh", "devHtf", "devLtf",
    "activeHt", "activeLt", "activeHh", "activeLh",
    "targetTSwitch", "targetHumiSwitch", "targetTemp", "targetTempF",
    "targetHumi", "settingMode", "vpdSettingMode",
    "targetVpd", "targetVpdSwitch",
    "activeHtVpd", "activeLtVpd", "activeHtVpdNums", "activeLtVpdNums",
    "acitveTimerOn", "acitveTimerOff", "activeCycleOn", "activeCycleOff",
    "schedStartTime", "schedEndtTime", "surplus", "modeType",
    "vpdStatus", "ecOrTds", "isUpdateVpdNums",
]


class ACIError(Exception):
    pass


class ACInfinity:
    def __init__(self, email, password):
        self._email = email
        self._password = password[:25]  # cloud truncates to 25 chars
        self._token = None
        self._session = None

    async def _client(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": UA}, timeout=aiohttp.ClientTimeout(total=20))
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _post(self, path, data, auth=True):
        sess = await self._client()
        headers = {"Content-Type":
                   "application/x-www-form-urlencoded; charset=utf-8"}
        if auth:
            if not self._token:
                await self.login()
            headers["token"] = self._token
        async with sess.post(BASE + path, data=data, headers=headers) as r:
            text = await r.text()
        try:
            payload = json.loads(text)
        except ValueError:
            raise ACIError(f"{path}: non-JSON response: {text[:200]}")
        if payload.get("code") != 200:
            # token expired -> re-login once
            if auth and payload.get("code") in (-200, 401, 10001):
                self._token = None
                return await self._post(path, data, auth=auth)
            raise ACIError(f"{path}: {payload.get('msg')!r} "
                           f"(code {payload.get('code')})")
        return payload

    async def login(self):
        resp = await self._post(
            "/api/user/appUserLogin",
            {"appEmail": self._email, "appPasswordl": self._password},
            auth=False)
        self._token = resp["data"]["appId"]
        return self._token

    async def devices(self):
        """Full device list with live sensor readings and port states."""
        resp = await self._post("/api/user/devInfoListAll",
                                {"userId": self._token or await self.login()})
        return resp.get("data") or []

    async def port_settings(self, dev_id, port):
        resp = await self._post("/api/dev/getdevModeSettingList",
                                {"devId": str(dev_id), "port": str(port)})
        return resp["data"]

    # --- Advance Automation (groups) ---------------------------------------

    async def get_groups(self, dev_id):
        """Read the Advance automation rules ('groups') for a device."""
        resp = await self._post("/api/version=2.0/dev/getGroups",
                                {"devId": str(dev_id)})
        return resp.get("data") or []

    async def update_group(self, group, overrides):
        """Read-modify-write one automation group.

        `group` is a group object from get_groups(); `overrides` is a dict of
        GROUP_WRITABLE keys -> new int value. Builds the exact 69-field payload
        the app sends, preserving everything not overridden.
        """
        for key in overrides:
            if key not in GROUP_WRITABLE:
                raise ACIError(f"refusing to write protected group field {key!r}")
        payload = dict(GROUP_UPDATE_DEFAULTS)
        for key in GROUP_UPDATE_KEYS:
            val = group.get(key)
            if isinstance(val, bool):
                val = 1 if val else 0
            payload[key] = "" if val is None else val
        # keep the °C trigger in sync if °F is being changed
        if "autoHighTempF" in overrides:
            overrides.setdefault(
                "autoHighTempC", round((overrides["autoHighTempF"] - 32) * 5 / 9))
        if "autoLowTempF" in overrides:
            overrides.setdefault(
                "autoLowTempC", round((overrides["autoLowTempF"] - 32) * 5 / 9))
        payload.update(overrides)
        return await self._post(
            "/api/version=2.0/dev/updateGroupsById", payload)

    async def set_port_mode(self, dev_id, port, overrides):
        """Read current mode settings, apply `overrides`, post the whole set.

        `overrides` is a dict of MODE_PAYLOAD_KEYS -> new int value
        (e.g. {"atType": 2} to turn a port On, {"onSpead": 5} for speed 5).
        """
        current = await self.port_settings(dev_id, port)
        payload = {
            "devId": str(dev_id),
            "externalPort": current.get("externalPort", port),
            "modeSetid": current.get("modeSetid"),
        }
        for key in MODE_PAYLOAD_KEYS:
            if key in current and current[key] is not None:
                payload[key] = current[key]
        for key, val in overrides.items():
            if key not in MODE_PAYLOAD_KEYS:
                raise ACIError(f"refusing to write unknown mode key {key!r}")
            payload[key] = val
        # normalize bools the API sometimes returns as JSON true/false
        for k, v in list(payload.items()):
            if isinstance(v, bool):
                payload[k] = 1 if v else 0
        return await self._post("/api/dev/addDevMode", payload)


# ---- value decoding helpers (API stores hundredths) -------------------------

def _hund(v):
    return None if v is None else round(v / 100, 2)


def decode_reading(info):
    """Pull human-readable live readings off a deviceInfo block."""
    return {
        "tempF": _hund(info.get("temperatureF")),
        "tempC": _hund(info.get("temperature")),
        "humidity": _hund(info.get("humidity")),
        "vpd": _hund(info.get("vpdnums")),
    }
