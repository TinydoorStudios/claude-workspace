#!/usr/bin/env python3
"""Local stand-in for n8n's internal-send-outlook + advance-notify webhooks.

Listens on 127.0.0.1:8199 (the only URL app/mailer.py will talk to while
ADVANCE_STAGING=1). Every POST is appended as one JSON line to MAILLOG
(default ~/advtest/mail.jsonl) so tests can assert exactly what would have
been sent — nothing ever leaves this box.

Behaviour knobs, to exercise the app's failure paths:
  - X-Advance-Token header must equal STUB_TOKEN (env, default "test-token")
    or the stub answers 500 like the real workflow does now (review H3).
  - a subject containing "[FAIL]" answers 500 (Graph rejection).
  - a subject containing "[NOSTATUS]" answers 200 with an empty body (an
    older workflow with no `sent` key — must count as sent).
  - an empty body answers {"sent": false, "blocked": "empty body"}.

    python3 mailstub.py [--port 8199] [--log PATH]
"""
import argparse
import json
import os
import datetime as dt
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ.get("STUB_TOKEN", "test-token")
LOG = os.environ.get("MAILLOG", os.path.expanduser("~/advtest/mail.jsonl"))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _reply(self, code, obj=None):
        body = (json.dumps(obj) if obj is not None else "").encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace")
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            payload = {"_raw": raw}
        rec = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "path": self.path,
               "token_ok": self.headers.get("X-Advance-Token") == TOKEN, "payload": payload}
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if self.path.endswith("/internal-send-outlook"):
            if not rec["token_ok"]:
                return self._reply(500, {"message": "Error in workflow: bad X-Advance-Token"})
            subj = str(payload.get("subject") or "")
            content = payload.get("html") or payload.get("body") or ""
            if not str(content).strip():
                return self._reply(200, {"sent": False, "status": 202, "blocked": "empty body"})
            if "[FAIL]" in subj:
                return self._reply(500, {"message": "Graph did not accept the message: HTTP 400"})
            if "[NOSTATUS]" in subj:
                return self._reply(200)
            return self._reply(200, {"sent": True, "status": 202})
        return self._reply(200, {"ok": True})


def main():
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8199)
    ap.add_argument("--log", default=LOG)
    a = ap.parse_args()
    LOG = a.log
    print(f"mailstub on 127.0.0.1:{a.port}, logging to {LOG}", flush=True)
    HTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
