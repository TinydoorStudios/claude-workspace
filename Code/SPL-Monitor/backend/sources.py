"""Data sources. Both yield normalized frames so they're interchangeable:

    {
      "timestamp": "<ISO8601>",
      "deviceName": "...",
      "channelName": "...",
      "metrics": { "SPL A Fast": 86.2, "SPL A Slow": 85.1, ... },  # flat dict
      "violation": bool,   # optional — Smaart alarm exceeded
      "overload": bool,    # optional — input clip
    }

SimulatorSource fabricates a lively SPL curve so the whole app can be built and
demoed with no Smaart present. SmaartSource is the real adapter: it speaks the
Smaart API v3 WebSocket protocol (see docs/SmaartAPI_v3_notes.md) and is a
drop-in swap — flip "source.type" to "smaart" in config.json.
"""

import asyncio
import datetime
import json
import math
import os
import random
import urllib.parse


def make_source(cfg):
    stype = cfg.get("source", {}).get("type", "simulator").lower()
    if stype == "smaart":
        return SmaartSource(cfg)
    return SimulatorSource(cfg)


def _now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")


class SimulatorSource:
    """Generates a believable A-weighted SPL stream at ~8 fps.

    A slow multi-minute ramp lets the 6-min LAeq climb toward the limit so the
    traffic light and the time-to-limit prediction visibly do their thing, then
    it eases back off.

    Scenes (env var SPL_SIM_SCENE) let you pin the stream for screenshots:
      - "green" : holds ~74 dBA, everything comfortably under the 80 dBA yellow.
                  Solid green light, zero strikes.
      - "hot"   : sits hot and pulses above/below the 90 dBA red every ~40 s so
                  the red light latches and the strike counter climbs.
      - unset / "default" / "demo" : the original slow swinging ramp.
    """

    def __init__(self, cfg, fps=8):
        self.fps = fps
        self.base = 84.0
        self.slow = 84.0
        self.phase = random.random() * math.tau
        self.scene = os.environ.get("SPL_SIM_SCENE", "default").strip().lower()
        if self.scene == "green":
            self.base = self.slow = 74.0
        elif self.scene == "hot":
            self.base = self.slow = 90.0

    def _inst_for_scene(self, t):
        """Return the instantaneous SPL A value for the active scene."""
        if self.scene == "green":
            # gentle program material well under the 80 dBA yellow
            phrase = 2.5 * math.sin(t / 11.0 + self.phase)
            return 74.0 + phrase + random.gauss(0.0, 1.2)
        if self.scene == "hot":
            # ~40 s pulse: half the cycle sits above the 90 dBA red, half below,
            # so the 10 s LAeq crosses the line each cycle and racks up strikes.
            pulse = math.sin(t / 40.0 * math.tau)
            level = 92.0 + 6.0 * pulse           # swings ~86 -> ~98
            return level + random.gauss(0.0, 1.3)
        # default demo ramp: build over ~3 min to ~+9 dB, hold, ease off (~7 min)
        ramp = 9.0 * (0.5 - 0.5 * math.cos(min(t, 420.0) / 420.0 * math.tau))
        phrase = 3.5 * math.sin(t / 13.0 + self.phase)
        return self.base + ramp + phrase + random.gauss(0.0, 2.0)

    async def frames(self):
        dt = 1.0 / self.fps
        loop = asyncio.get_event_loop()
        t0 = loop.time()
        while True:
            t = loop.time() - t0
            inst = self._inst_for_scene(t)
            inst = max(55.0, min(110.0, inst))

            self.slow += (inst - self.slow) * 0.18
            spl_a_fast = inst
            spl_a_slow = self.slow
            spl_c_fast = inst + random.uniform(2.5, 4.5)
            spl_c_slow = self.slow + 3.5
            spl_fast = inst + 1.4
            spl_slow = self.slow + 1.4
            peak_c = spl_c_fast + random.uniform(6.0, 12.0)
            fs_peak = max(-90.0, -64.0 + (inst - 55.0) * 0.45)
            # 63 Hz octave band — sits a few dB under broadband C, wandering with
            # its own slow phrase so the bass watch has something live to show.
            sub63 = spl_c_slow - 4.0 + 2.5 * math.sin(t / 9.0 + self.phase) + random.gauss(0.0, 1.0)

            metrics = {
                "FS Peak": round(fs_peak, 2),
                "Peak C": round(peak_c, 2),
                "SPL Fast": round(spl_fast, 2),
                "SPL A Fast": round(spl_a_fast, 2),
                "SPL C Fast": round(spl_c_fast, 2),
                "SPL Slow": round(spl_slow, 2),
                "SPL A Slow": round(spl_a_slow, 2),
                "SPL C Slow": round(spl_c_slow, 2),
                "LZeq 10s 63 Hz": round(sub63, 2),
                "LZeq 1 63 Hz": round(self.slow - 4.0, 2),
            }
            yield {
                "timestamp": _now_iso(),
                "deviceName": "Simulator",
                "channelName": "Sim Mic",
                "metrics": metrics,
                "overload": fs_peak >= -1.0,
            }
            await asyncio.sleep(dt)


class SmaartSource:
    """Real Smaart API v3 client. Read-only: only `get` + stream subscription."""

    def __init__(self, cfg):
        s = cfg["source"]["smaart"]
        self.host = s.get("host", "127.0.0.1")
        self.port = s.get("port", 26000)
        self.password = s.get("password")
        self.device = s.get("deviceName")
        self.channel = s.get("channelName")
        self.target_fps = s.get("targetFps", 8)

    @property
    def _root(self):
        return f"ws://{self.host}:{self.port}/api/v3/"

    def _abs(self, endpoint):
        # endpoint is URL-encoded path like /api/v3/devices/.../channels/...
        return f"ws://{self.host}:{self.port}{endpoint}"

    async def frames(self):
        import aiohttp  # imported here so the simulator path needs no network stack

        while True:
            try:
                async for frame in self._run_once(aiohttp):
                    yield frame
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001 — reconnect on any failure
                print(f"[smaart] connection error: {e!r} — retrying in 3s")
                await asyncio.sleep(3)

    async def _run_once(self, aiohttp):
        timeout = aiohttp.ClientTimeout(total=None)
        # force_close: never pool/reuse a connection. Reusing the closed discovery
        # socket for the stream causes ws_connect to hang forever on this rig.
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # 1. resolve the calibrated channel's stream endpoint via the root socket
            stream_endpoint = None
            dev_name = self.device
            chan_name = self.channel
            async with session.ws_connect(self._root) as root:
                if self.password:
                    await self._send(root, {"action": "set",
                                            "properties": [{"password": self.password}]})
                    await root.receive()
                await self._send(root, {"action": "get",
                                        "target": "activeCalibratedInputs"})
                resp = await self._recv_json(root)
                devices = (resp.get("response") or {}).get("devices", [])
                stream_endpoint, dev_name, chan_name = self._pick_channel(devices)
                if not stream_endpoint:
                    raise RuntimeError(
                        "no calibrated, actively-logging input found in Smaart "
                        "(check the input is calibrated and SPL logging is running)")
                print(f"[smaart] streaming {dev_name} / {chan_name}")

            # 2. open the instantaneous metric stream.
            # NOTE: do not send a targetFPS command here — on at least one v8.5 rig
            # that silences the stream. The server pushes at its own rate (~3s).
            async with session.ws_connect(self._abs(stream_endpoint), heartbeat=20) as stream:
                if os.environ.get("SMAART_DEBUG"):
                    print(f"[smaart-dbg] stream opened url={self._abs(stream_endpoint)} closed={stream.closed}", flush=True)
                while True:
                    # Watchdog: the rig pushes every ~3s. If it goes silent for 20s
                    # the connection has stalled — drop it and let frames() reconnect.
                    try:
                        msg = await asyncio.wait_for(stream.receive(), timeout=20)
                    except asyncio.TimeoutError:
                        raise RuntimeError("stream idle 20s — reconnecting")
                    if os.environ.get("SMAART_DEBUG"):
                        print(f"[smaart-dbg] {msg.type.name} {str(msg.data)[:50]!r}", flush=True)
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
                        continue
                    try:
                        data = json.loads(msg.data)
                    except (ValueError, TypeError):
                        continue
                    frame = self._normalize(data, dev_name, chan_name)
                    if frame:
                        yield frame

    @staticmethod
    def _pick_channel(devices):
        """Return (streamEndpoint, deviceName, channelName) for the first
        calibrated channel, honoring config device/channel if set elsewhere."""
        for dev in devices:
            for ch in dev.get("activeCalibratedChannels", []):
                ep = ch.get("streamEndpoint")
                if ep:
                    return ep, dev.get("deviceName"), ch.get("channelName")
        return None, None, None

    @staticmethod
    def _normalize(data, dev_name, chan_name):
        raw = data.get("metrics")
        if raw is None:
            return None
        metrics = {}
        violation = False
        for item in raw:
            for k, v in item.items():
                if k == "violation":
                    violation = violation or bool(v)
                else:
                    metrics[k] = v
            if item.get("violation"):
                violation = True
        return {
            "timestamp": data.get("timestamp") or _now_iso(),
            "deviceName": data.get("deviceName") or dev_name,
            "channelName": data.get("channelName") or chan_name,
            "metrics": metrics,
            "violation": violation,
            "overload": bool(data.get("overload")),
        }

    @staticmethod
    async def _send(ws, obj):
        await ws.send_str(json.dumps(obj))

    @staticmethod
    async def _recv_json(ws):
        msg = await ws.receive()
        return json.loads(msg.data)
