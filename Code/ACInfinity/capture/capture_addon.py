"""mitmproxy addon: log only AC Infinity cloud calls to a JSONL file."""
import json
from pathlib import Path
from mitmproxy import http

OUT = Path(__file__).with_name("aci_flows.jsonl")


def response(flow: http.HTTPFlow):
    if "acinfinityserver.com" not in flow.request.pretty_host:
        return
    rec = {
        "method": flow.request.method,
        "host": flow.request.pretty_host,
        "path": flow.request.path,
        "req_body": flow.request.get_text(),
        "status": flow.response.status_code if flow.response else None,
        "resp_body": flow.response.get_text() if flow.response else None,
    }
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
