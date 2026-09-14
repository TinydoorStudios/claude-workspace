#!/usr/bin/env python3
"""Send Brian an internal alert from a shell script: alert.py "<subject>" "<text>".
Goes through app/mailer.py (same kill switch / confirmation rules)."""
import sys
sys.path.insert(0, "/opt/band-advance")
import mailer

subject, text = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
ok, err = mailer.alert(subject, "<pre>" + mailer.esc(text) + "</pre>")
print("sent" if ok else f"not sent: {err}")
sys.exit(0 if ok else 1)
