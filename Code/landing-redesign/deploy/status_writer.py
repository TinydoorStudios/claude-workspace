#!/usr/bin/env python3
"""status-writer — writes /opt/landing/html/rack/status.json for the /rack/ dashboard.

Runs as root on the n8n VM via systemd timer (every 30s). The output lives under
/rack/ which nginx gates with basic auth (tds / lockdown) — no VM data is public.

Collects:
  - VM stats: load, mem, disk, uptime
  - systemd unit states (spl-monitor, tempest-dashboard, showbuilder, acinfinity, cloudflared)
  - docker container states (landing, n8n, postgres)
  - defined systems from /opt/status-writer/rack.json (ping / http checks; add
    VMs there — one JSON entry each, picked up on the next run)
  - PVE host + guest stats, IF /opt/status-writer/pve.json is fresh (<120s).
    That file is pushed by the pve host (see pve-status-push.sh); absent/stale
    is fine — the page shows "host telemetry offline" and everything else works.

Atomic write: tmp file + rename (html dir is bind-mounted into the landing container).
"""
import json, os, subprocess, time, urllib.request

OUT = "/opt/landing/html/rack/status.json"
RACK_CFG = "/opt/status-writer/rack.json"
PVE_PUSH = "/opt/status-writer/pve.json"
SYSD_UNITS = ["spl-monitor", "tempest-dashboard", "showbuilder", "acinfinity", "cloudflared"]


def run(cmd, timeout=10):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except Exception:
        return ""


def vm_stats():
    with open("/proc/loadavg") as f:
        load = float(f.read().split()[0])
    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":", 1)
            mem[k] = int(v.split()[0])  # kB
    with open("/proc/uptime") as f:
        up = float(f.read().split()[0])
    st = os.statvfs("/")
    disk_tot = st.f_blocks * st.f_frsize
    disk_used = disk_tot - st.f_bfree * st.f_frsize
    return {
        "loadavg": load,
        "cores": os.cpu_count(),
        "memUsedMb": round((mem["MemTotal"] - mem["MemAvailable"]) / 1024),
        "memTotMb": round(mem["MemTotal"] / 1024),
        "diskUsedGb": round(disk_used / 1e9, 1),
        "diskTotGb": round(disk_tot / 1e9, 1),
        "uptime": int(up),
    }


def services():
    out = {}
    for u in SYSD_UNITS:
        out[u] = run(["systemctl", "is-active", u]) or "unknown"
    return out


def docker_ps():
    raw = run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"])
    return [{"name": n, "status": s} for n, s in
            (line.split("\t", 1) for line in raw.splitlines() if "\t" in line)]


def check_http(url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, method="HEAD")
        urllib.request.urlopen(req, timeout=4)
        return True, round((time.time() - t0) * 1000)
    except Exception:
        return False, None


def check_ping(host):
    t0 = time.time()
    ok = subprocess.run(["ping", "-c", "1", "-W", "2", host],
                        capture_output=True).returncode == 0
    return ok, round((time.time() - t0) * 1000) if ok else None


def systems():
    try:
        with open(RACK_CFG) as f:
            cfg = json.load(f)
    except Exception:
        return []
    out = []
    for sys_ in cfg.get("systems", []):
        entry = {k: sys_.get(k) for k in ("id", "name", "role", "check", "vmid")}
        up, ms = None, None
        if sys_.get("check") == "http" and sys_.get("target"):
            up, ms = check_http(sys_["target"])
        elif sys_.get("check") == "ping" and sys_.get("target"):
            up, ms = check_ping(sys_["target"])
        entry["up"], entry["ms"] = up, ms
        out.append(entry)
    return out


def pve_push():
    """Host stats pushed by pve; only trusted if fresh."""
    try:
        if time.time() - os.path.getmtime(PVE_PUSH) > 120:
            return {}
        with open(PVE_PUSH) as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    data = {
        "generated": int(time.time()),
        "vm": vm_stats(),
        "services": services(),
        "docker": docker_ps(),
        "systems": systems(),
    }
    data.update(pve_push())  # adds "pve" and "guests" keys when fresh
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    os.replace(tmp, OUT)


if __name__ == "__main__":
    main()
