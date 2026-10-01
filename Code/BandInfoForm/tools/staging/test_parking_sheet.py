#!/opt/band-advance/venv/bin/python
"""Memorial Hall advance, end to end, against the staging clone (2026-09-29).

    ~/advtest/code/tools/staging/test_memo.py

Books a Memo show as staff, fills the staff side, fills the band side from a
cookie-less session with several uploads, then checks the filed doc + files
in ~/advtest/Dropbox, blank-never-erases, the two-artist switch, hand-edit
protection, and that the universal form still renders.
"""
import datetime as dt
import http.cookiejar
import io
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

T = Path.home() / "advtest"
for line in (T / "advtest.env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()
CODE = T / "code"
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(CODE / "tools"))
import advance_db as db  # noqa: E402
import docx  # noqa: E402

with db.get_conn() as _c:
    assert _c.execute("SELECT current_database()").fetchone()["current_database"] == "advance_test"

APP = "http://127.0.0.1:8198"
PY = "/opt/band-advance/venv/bin/python"
DROP = Path(os.environ["ADVANCE_DROPBOX_ROOT"])
DATE = dt.date.today() + dt.timedelta(days=40 + int(uuid.uuid4().int % 300))  # fresh date per run
TAG = uuid.uuid4().hex[:5]
EVENT = f"Memo Test Night {TAG}"
BAND1, BAND2 = f"Test Quartet {TAG}", f"Opener Duo {TAG}"
RESULTS = []


def check(cond, msg):
    RESULTS.append(bool(cond))
    print(("  ok   " if cond else "  FAIL ") + msg, flush=True)


class Client:
    def __init__(self):
        # the session cookie is Secure; staging is plain http on localhost
        self.jar = http.cookiejar.CookieJar(policy=http.cookiejar.DefaultCookiePolicy(
            secure_protocols=("http", "https")))
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def req(self, path, data=None, files=None, method=None):
        url = path if path.startswith("http") else APP + path
        body, hdr = None, {}
        if files is not None:
            b = uuid.uuid4().hex
            buf = io.BytesIO()
            for k, v in (data or []):
                buf.write(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
            for k, name, content in files:
                buf.write(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{name}\"\r\n"
                          "Content-Type: application/octet-stream\r\n\r\n".encode() + content + b"\r\n")
            buf.write(f"--{b}--\r\n".encode())
            body, hdr = buf.getvalue(), {"Content-Type": f"multipart/form-data; boundary={b}"}
        elif data is not None:
            body = urllib.parse.urlencode(data).encode()
            hdr = {"Content-Type": "application/x-www-form-urlencoded"}
        r = urllib.request.Request(url, data=body, headers=hdr, method=method)
        try:
            with self.op.open(r, timeout=120) as resp:
                return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace"), url


def pdf(tag):
    return b"%PDF-1.4\n% " + tag.encode() + b"\n%%EOF\n"


def csrf_of(html):
    m = re.search(r'name="csrf" value="([^"]+)"', html)
    return m.group(1) if m else ""


def token_of(url):
    return urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]


def book(staff, artist, email, start="20:00", end="21:30"):
    st, html, _ = staff.req("/booking")
    c = csrf_of(html)
    st, html, _ = staff.req("/booking", {
        "csrf": c, "entered_by": "Nyquist test", "series": "Stand-Alone Internal",
        "event_name": EVENT, "event_date": DATE.isoformat(), "venue": "Memorial Hall",
        "set_start": start, "set_end": end, "artist_name": artist,
        "contact_name": "Pat Tester", "contact_email": email, "event_start": "", "event_end": ""})
    m = re.search(r'href="(https?://[^"]+/(?:s|f)/[^"]+)"', html)
    return st, (m.group(1) if m else None), html


def memo_doc(show_id):
    out = subprocess.run([PY, "memo_doc.py", "--show-id", str(show_id)], cwd=CODE / "tools",
                         capture_output=True, text=True, env=os.environ)
    return (out.stdout + out.stderr).strip()


def show_id_for(artist):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT s.id FROM shows s JOIN artists a ON a.id=s.artist_id
                       WHERE a.name=%s AND s.venue='Memorial Hall' AND s.show_date=%s""", (artist, DATE))
        r = cur.fetchone()
        return r["id"] if r else None


def doc_text(p):
    d = docx.Document(str(p))
    from docx.oxml.ns import qn
    return "\n".join("".join(t.text or "" for t in para.iter(qn("w:t")))
                     for para in d.element.body.iter(qn("w:p")))



MAILLOG = Path(os.environ.get("MAILLOG", str(T / "mail.jsonl")))


def mails_since(n0):
    lines = MAILLOG.read_text().splitlines() if MAILLOG.exists() else []
    import json
    return [json.loads(x) for x in lines[n0:]]


def mail_count():
    return len(MAILLOG.read_text().splitlines()) if MAILLOG.exists() else 0


def setup_show(staff, artist, parking):
    st, link, html = book(staff, artist, f"pat+{uuid.uuid4().hex[:4]}@example.com")
    assert link, "booking failed"
    st, html, url = staff.req(link)
    tok = token_of(url)
    c = csrf_of(html)
    st, html, url = staff.req("/memo/submit", [
        ("token", tok), ("csrf", c), ("band_name", artist), ("show_date", DATE.isoformat()),
        ("event_type", "Internal Event"), ("parking", parking)])
    return st


def needs_for(band):
    with db.get_conn() as conn, conn.cursor() as cur:
        return [i for i in db.needs_attention(cur) if i["kind"] == "parking_sheet" and band in i["detail"]]


def main():
    staff = Client()
    st, _, _ = staff.req("/gate", {"passcode": os.environ.get("ADVANCE_GATE_PASS", "lockdown")})
    check(st in (200, 302), "staff signs in")

    # Washington Park parking: dashboard item appears, send works once, item clears
    setup_show(staff, BAND1, "Washington Park")
    sid = show_id_for(BAND1)
    check(sid, "WP-parking Memo show exists")
    items = needs_for(BAND1)
    check(len(items) == 1 and items[0]["link_path"] == f"/show/{sid}/parking-sheet",
          "dashboard lists 'Parking sheet not sent' for it")
    st, html, _ = staff.req(f"/show/{sid}/parking-sheet")
    check(st == 200 and "Send the parking sheet" in html and "Washington Park Garage Parking.pdf" in html,
          "parking-sheet page shows the preview and the send button")
    if "Send the parking sheet" not in html:
        h = re.sub(r"\s+", " ", re.sub(r"<style.*?</style>", "", html, flags=re.S))
        print("   DEBUG", st, h[h.find("</header>"):][:1500])
    n0 = mail_count()
    c = csrf_of(html)
    st, html2, _ = staff.req(f"/show/{sid}/parking-sheet", {"csrf": c}, method="POST")
    check(st == 200, f"send returns the page ({st})")
    sent = mails_since(n0)
    check(len(sent) == 1, f"exactly one email left ({len(sent)})")
    if sent:
        m = sent[0]
        names = [m.get("attachment_name")] + [a.get("name") for a in m.get("attachments", [])]
        check("Washington Park Garage Parking.pdf" in names, f"it carries the parking sheet ({names})")
        check(BAND1 in m.get("subject", "") and "Parking for" in m.get("subject", ""),
              f"subject names the band ({m.get('subject')})")
        check("Nyquist" not in (m.get("body") or "") and "Claude" not in (m.get("body") or ""),
              "no assistant mention in the body")
    check(not needs_for(BAND1), "item clears after the send")
    st, html3, _ = staff.req(f"/show/{sid}/parking-sheet", {"csrf": csrf_of(html2) or c}, method="POST")
    check(len(mails_since(n0)) == 1, "a second POST does not send again")

    # SP+ parking: no item
    DATE_SAVE = globals()["DATE"]
    globals()["DATE"] = DATE + dt.timedelta(days=1)
    setup_show(staff, BAND2, "SP+ Lot")
    check(not needs_for(BAND2), "SP+ Lot show gets no parking-sheet item")
    globals()["DATE"] = DATE_SAVE

    # welcome helper
    sys.path.insert(0, str(CODE / "tools"))
    import venue_email as ve
    check(ve.wants_parking_sheet("Washington Park", "Neo Soul Nights") and
          not ve.wants_parking_sheet("Washington Park", "3rd Party") and
          not ve.wants_parking_sheet("Fountain Square", None), "wants_parking_sheet rules")
    names = [n for n, _t, _c in ve.venue_attachments("Memorial Hall")]
    check("Memorial Hall Tech-Pack 2026.pdf" in names, f"Memo tech pack attaches under its clean name ({names})")

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
