#!/usr/bin/env python3
"""3CDC Band Advance Form — self-hosted, even spacing + inline conditional logic."""
import json
import re
import datetime as dt
from pathlib import Path

from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
UPLOADS = DATA / "uploads"
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB cap on the stage-plot upload

VENUES = [
    "Fountain Square", "Washington Park", "Elm Street Plaza",
    "Court Street Plaza", "Zeigler Park", "Imagination Alley",
]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "band").lower()).strip("-")[:40] or "band"


@app.get("/")
def form():
    return render_template("form.html", venues=VENUES)


@app.post("/submit")
def submit():
    f = request.form
    if not f.get("band_name"):
        abort(400, "Band name is required.")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = _slug(f.get("band_name"))
    rec = {k: v for k, v in f.items()}
    rec["_submitted_at"] = dt.datetime.now().isoformat(timespec="seconds")

    upload = request.files.get("stage_plot_file")
    if upload and upload.filename:
        safe = secure_filename(upload.filename)
        stored = f"{stamp}__{slug}__{safe}"
        upload.save(UPLOADS / stored)
        rec["stage_plot_file"] = stored

    (DATA / f"{stamp}__{slug}.json").write_text(json.dumps(rec, indent=2))
    return render_template("thanks.html", band=f.get("band_name"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8097)
