#!/usr/bin/env python3
"""Per-venue (and per-series) advance-email content blocks.

The advance email's body is venue-specific — Fountain Square's garage QR codes and
95 dBA-Slow ordinance have no business in a Washington Park or Memorial Hall email. This
keeps one email skeleton (greeting, form link, schedule, common rules) and swaps the
venue-specific blocks: location, load-in/parking, technical, hospitality, and any
venue-only performance rules.

To add a venue: copy the FSQ dict, replace the prose. Anything you leave out falls
back to DEFAULT (a generic, non-FSQ-specific block that is safe to send as-is).
COMMON_REQUIREMENTS is the 3CDC-wide policy and appends to every venue.

A series can override any of those same blocks on top of its venue's content.
That content lives as files in Dropbox, not in this module (Brian, 2026-09-09:
"one central location" he edits directly, no code deploy needed) —
~/Dropbox/Nyquist/Series Email Templates/<Venue>/<Series>.md, read live on
every call. A series with no file there, or no series on the booking at all,
falls straight through to the plain venue email. See the README in that
folder for the file format.

A block's prose can reference `{some_key}` placeholders — draft_emails.py fills
them per show via blocks_for's **dynamic kwargs (e.g. WP's {location}/{stage_size},
sourced from the booking's Location field and forms_config.WP_LOCATIONS). Only
blocks containing the referenced placeholder are touched; everything else is a
plain string, unaffected by the substitution pass.
"""
import re
import sys
from pathlib import Path

# 3CDC-wide, appended under Performance Requirements for every venue.
COMMON_REQUIREMENTS = """\
- Content: family-friendly only — no foul language or gestures, including prerecorded tracks, live vocals, and sound check.
- Performer safety: stay on the stage. No crowd surfing, climbing, jumping off stage, or stepping on sound equipment.
- Audience safety: do not throw or shoot anything into the crowd (confetti, t-shirts, bottles, merch/CDs, etc.).
- Weather: rain or shine. Booking evaluates weather about 3 hours before start; if you don't hear otherwise, assume the show goes on.
- Payment: all groups are paid after the performance, not before."""

# Spanish translation of COMMON_REQUIREMENTS — draft, 2026-09-12. Kept as a
# parallel constant rather than folded into VENUE_EMAIL_ES so a future
# language-aware render_email() (not yet wired — see advance_es.md.j2) can
# pick requirements + COMMON_REQUIREMENTS_ES the same way the English path
# picks blocks_for(...) + COMMON_REQUIREMENTS.
COMMON_REQUIREMENTS_ES = """\
- Contenido: solo apto para toda la familia — no se permite lenguaje ni gestos obscenos, incluyendo pistas pregrabadas, voces en vivo y la prueba de sonido.
- Seguridad de los artistas: permanezcan en el escenario. No se permite lanzarse al público, trepar, saltar del escenario ni pisar el equipo de sonido.
- Seguridad del público: no lancen ni disparen nada hacia el público (confeti, camisetas, botellas, mercancía/CDs, etc.).
- Clima: el show se realiza con lluvia o con sol. El equipo de producción evalúa las condiciones climáticas aproximadamente 3 horas antes del inicio; si no reciben aviso contrario, asuman que el show continúa.
- Pago: todos los grupos reciben su pago después de la presentación, no antes."""

# Generic, safe-to-send blocks for a venue we haven't customized yet (no FSQ specifics).
DEFAULT = {
    "location": None,   # falls back to the venue name in the template
    "load_in": """\
Load-In & Parking:
Your day-of contact will coordinate load-in and parking with you. Text or call them when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive. Note any large-vehicle needs on the form.""",
    "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors. Coordinate in advance if you're bringing your own.
- Stage plot / input list, stage layout, monitor count, and any scenic elements — all on the form.""",
    "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; ask your day-of contact about a table.
- Hospitality: water is provided for all performers and crew.""",
    "requirements": "",   # venue-specific rule lines (optional)
}

# Spanish translation of DEFAULT — draft, 2026-09-12, so a Spanish-language
# render for an unconfigured venue still gets grammatical, safe-to-send
# copy instead of an empty block.
DEFAULT_ES = {
    "location": None,
    "load_in": """\
Carga y estacionamiento:
Su contacto del día del evento coordinará la carga y el estacionamiento con ustedes. Llámenlo o envíenle un mensaje de texto cuando estén a unos 5 minutos de llegar, y preséntense en persona en cuanto lleguen. Indiquen en el formulario si necesitan espacio para vehículos grandes.""",
    "technical": """\
Técnico:
- Backline / instrumentación: los artistas proporcionan todos los instrumentos, incluyendo amplificadores y cables de 1/4 de pulgada.
- Audio: proporcionamos un ingeniero que mezcla el FOH y los monitores. Coordinen con anticipación si van a traer su propio ingeniero.
- El plano de escenario / lista de entradas, la distribución del escenario, la cantidad de monitores y cualquier elemento escenográfico — todo se indica en el formulario.""",
    "hospitality": """\
Hospitalidad y sitio:
- Mercancía: si van a vender, ustedes proporcionan el vendedor, el punto de venta y el banco; pregúntenle a su contacto del día del evento sobre una mesa.
- Hospitalidad: se proporciona agua para todos los artistas y el equipo de trabajo.""",
    "requirements": "",
}

VENUE_EMAIL = {
    "Fountain Square": {
        "location": "Fountain Square – Mainstage; 520 Vine St. Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
The load-in process at Fountain Square has changed — please review the attached document and acknowledge understanding on the form. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
We will follow up with QR codes that serve as your Fountain Square Garage validations. Each vehicle needs its own QR code before arriving; scan at the kiosk on entry or exit (please don't pay). Garage clearance is 6'8". Need more validations or large-vehicle parking? Note it on the form.""",
        # 3rd-party version (Brian, 2026-09-16): same load-in line and the
        # attached document, but no garage-QR/validation paragraph — that
        # process is for a touring band's own vehicles, and a 3rd-party event
        # doesn't have one. See blocks_for's `third_party` swap.
        "load_in_third_party": """\
Load-In & Parking:
The load-in process at Fountain Square has changed — please review the attached document and acknowledge understanding on the form. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.""",
        "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own. All engineers mix within the 95 dBA-Slow ordinance; the FSQ engineer may baffle amps to reduce stage volume if needed.
- Lighting: we provide a house LD.
- Stage plot / input list, flat vs. drum riser, monitor count, and any scenic elements — all on the form.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms; on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: drink tickets and water are provided for all performers and crew.""",
        "requirements": "- Sound limit: strict 95 dBA-Slow at the FOH position, for all engineers (house or talent).",
    },
    # WP copy adapted from the Fountain Square block (Brian, 2026-09-11): FSQ→WP
    # wording, the "load-in process has changed / review attached doc" section
    # removed, and the garage-QR-code paragraph replaced with the validations
    # follow-up line. {location} is filled per show; {lighting_line} and
    # {riser_phrase} are set by draft_emails.py and are EMPTY for Porch/Bandstand
    # — lighting and a drum riser exist only at the Main Stage, so those shows
    # must mention neither.
    "Washington Park": {
        "location": "Washington Park – {location}; 1230 Elm St, Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
We will follow-up with parking validations.""",
        "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own. All engineers mix within the 95 dBA-Slow ordinance; the Washington Park engineer may baffle amps to reduce stage volume if needed.{lighting_line}
- Stage plot / input list, {riser_phrase}monitor count, and any scenic elements — all on the form.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms; on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: drink tickets and water are provided for all performers and crew.""",
        "requirements": "- Sound limit: strict 95 dBA-Slow at the FOH position, for all engineers (house or talent).",
    },
    # Add Memorial Hall / etc. here as Brian supplies the content.
}

# Spanish translation of VENUE_EMAIL — draft, 2026-09-12, Fountain Square
# only (Brian's ask). Same dict shape, same {placeholder} substitution keys
# (blocks_for applies dynamic kwargs identically regardless of language).
# Not yet wired into draft_emails.py's render path — see advance_es.md.j2's
# header note for what full wiring would need (a --lang flag threading
# through draft_emails.py's Python-built strings: set_line, schedule_block,
# bill_block, summarize_submission's labels).
VENUE_EMAIL_ES = {
    "Fountain Square": {
        "location": "Fountain Square – Mainstage; 520 Vine St. Cincinnati, OH 45202",
        "load_in": """\
Carga y estacionamiento:
El proceso de carga en Fountain Square ha cambiado — por favor revisen el documento adjunto y confirmen que lo entendieron en el formulario. Llamen o envíen un mensaje de texto a su contacto del día del evento cuando estén a unos 5 minutos de llegar, y preséntense en persona en cuanto lleguen.
Les enviaremos códigos QR que funcionan como sus validaciones del estacionamiento Fountain Square Garage. Cada vehículo necesita su propio código QR antes de llegar; escaneen en el quiosco al entrar o salir (por favor no paguen). La altura máxima del estacionamiento es de 6'8". ¿Necesitan más validaciones o espacio para vehículos grandes? Indíquenlo en el formulario.""",
        # 3rd-party version — see load_in_third_party in VENUE_EMAIL (English) above.
        "load_in_third_party": """\
Carga y estacionamiento:
El proceso de carga en Fountain Square ha cambiado — por favor revisen el documento adjunto y confirmen que lo entendieron en el formulario. Llamen o envíen un mensaje de texto a su contacto del día del evento cuando estén a unos 5 minutos de llegar, y preséntense en persona en cuanto lleguen.""",
        "technical": """\
Técnico:
- Backline / instrumentación: los artistas proporcionan todos sus instrumentos, incluyendo amplificadores y cables de 1/4".
- Audio: proporcionamos un ingeniero que mezcla el FOH y los monitores desde el FOH. Coordinen con anticipación si van a traer su propio ingeniero. Todos los ingenieros deben mezclar dentro del límite de la ordenanza de 95 dBA-Slow; el ingeniero de Fountain Square puede reducir el volumen de los amplificadores en el escenario si es necesario.
- Iluminación: proporcionamos un LD (diseñador de iluminación) de la casa.
- El plano de escenario / lista de entradas, escenario plano o con plataforma para batería, cantidad de monitores y cualquier elemento escenográfico — todo se indica en el formulario.""",
        "hospitality": """\
Hospitalidad y sitio:
- Mercancía: si van a vender, ustedes proporcionan el vendedor, el punto de venta y el banco; nosotros proporcionamos una carpa junto al escenario con una mesa y sillas.
- Camerinos: no contamos con camerinos bajo techo; a solicitud podemos proporcionar una carpa de 10×10 con paredes laterales para un espacio privado de la banda.
- Hospitalidad: se proporcionan boletos de bebida y agua para todos los artistas y el equipo de trabajo.""",
        "requirements": "- Límite de sonido: estricto 95 dBA-Slow en la posición de FOH, para todos los ingenieros (de la casa o del talento).",
    },
    # Add other venues here as Brian asks for them in Spanish.
}

# Where Brian's per-series email content actually lives — see that folder's
# own README.md for the exact file format (## Location / Load-In / Technical
# / Hospitality / Requirements sections, only fill in what you want to
# override). One subfolder per venue, one .md file per series within it.
import os as _os
SERIES_EMAIL_ROOT = Path(_os.environ.get("ADVANCE_DROPBOX_ROOT") or (Path.home() / "Dropbox")) / "Nyquist" / "Series Email Templates"


def venue_attachments(venue, root=None):
    """Every standing attachment for this venue — all files named
    `_attachment*` in its Series Email Templates folder, in name order
    (review 2026-09-14, E4: `_attachment.pdf` = load-in doc,
    `_attachment-2 tech pack.pdf` = tech pack, and so on). [] if none."""
    if not venue:
        return []
    vdir = (Path(root) if root else SERIES_EMAIL_ROOT) / venue.strip()
    if not vdir.is_dir():
        return []
    import base64
    import mimetypes
    out = []
    for path in sorted(p for p in vdir.glob("_attachment*") if p.is_file()):
        try:
            data = path.read_bytes()
        except Exception as e:  # noqa: BLE001
            print(f"[venue_email] couldn't read attachment {path}: {e!r}", file=sys.stderr)
            continue
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        out.append((path.name, ctype, base64.b64encode(data).decode("ascii")))
    return out


def venue_attachment_links(venue, root=None):
    """Same standing files as venue_attachments(), as (filename, url) pairs
    instead of base64 content — for a reminder or day-before email, which
    links instead of re-attaching the same PDF the welcome already carried
    (audit 2026-09-16 #17: the welcome is the only email that attaches it;
    every FSQ email was carrying its own copy of a 1.4 MB file). Served by
    app.py's /venue-doc/<venue>/<filename> route."""
    if not venue:
        return []
    vdir = (Path(root) if root else SERIES_EMAIL_ROOT) / venue.strip()
    if not vdir.is_dir():
        return []
    public_url = _os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
    from urllib.parse import quote
    return [(path.name, f"{public_url}/venue-doc/{quote(venue.strip())}/{quote(path.name)}")
            for path in sorted(p for p in vdir.glob("_attachment*") if p.is_file())]


def venue_doc_links_text(venue, root=None):
    """Plain-text block linking this venue's standing docs, for a reminder
    or day-before body — '' if there are none. Friendly label for the two
    conventional files (load-in doc / tech pack); anything past that just
    gets its filename."""
    links = venue_attachment_links(venue, root=root)
    if not links:
        return ""
    labels = {0: "Load-in doc", 1: "Tech pack"}
    lines = [f"{labels.get(i, name)}: {url}" for i, (name, url) in enumerate(links)]
    return "\n".join(lines)


# Section-header aliases a series file's "## Heading" can use, matched after
# lowercasing and folding "&", "/", "-" to spaces — e.g. "Load-In & Parking"
# and "load in" both normalize to "load in" and hit load_in. Deliberately not
# exhaustive: an unrecognized header is skipped with a log line rather than
# guessed at, so a typo never silently drops content into the wrong block.
_BLOCK_HEADER_ALIASES = {
    "location": "location",
    "load in": "load_in",
    "load in parking": "load_in",
    "technical": "technical",
    "hospitality": "hospitality",
    "hospitality site": "hospitality",
    "requirements": "requirements",
    "performance requirements": "requirements",
    "schedule": "schedule",
    "day schedule": "schedule",
    "crew schedule": "crew_schedule",
}


# A "## Schedule" section is free text, same as every other section — it
# becomes the email's whole "Day Schedule:" block verbatim, not just a fill
# for the 5 generic fields. For a series with a fixed schedule that never
# changes (Brian, 2026-09-09: Salsa On The Square is the first) this is a
# hard override of what a staffer typed on the booking, not a blank-filler —
# see schedule_block_for().


def _norm_series(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def norm_header(s):
    s = re.sub(r"[&/\-]+", " ", s.strip().lower())
    return re.sub(r"\s+", " ", s).strip().rstrip(":")


# A header ending in "(Español)"/"(Espanol)"/"(ES)" (any case) is that same
# section's SPANISH translation, not a new section — 2026-09-12, for
# bilingual series (Salsa On The Square is the first). "## Technical
# (Español)" parses to the same `technical` key as "## Technical", but
# lands under `technical_es` — see blocks_for's lang handling. Strip it
# before the ordinary alias lookup so "Technical" and "Technical (Español)"
# resolve to the same base section.
_ES_HEADER_SUFFIX = re.compile(r"\s*\((?:espa[nñ]ol|es)\)\s*$", re.IGNORECASE)


def _parse_series_email_file(text, label=""):
    """A series .md file's text -> {block_key: content}, where a block_key
    ending in `_es` (from a "## <Section> (Español)" header) is that
    section's Spanish translation. See SERIES_EMAIL_ROOT's README for the
    section-header format."""
    blocks, current_key, buf = {}, None, []

    def commit():
        if not current_key:
            return
        # Trim blank lines off each edge (the blank line right after a "##
        # Header" and right before the next one) WITHOUT touching a real
        # line's own leading whitespace — a block like Schedule relies on
        # indentation to line up, and str.strip() on the joined text would
        # have eaten only the first line's indent, not the rest.
        lines = list(buf)
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            blocks[current_key] = "\n".join(lines)

    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if not m:
            buf.append(line)
            continue
        commit()
        buf = []
        raw_header = m.group(1)
        stripped, n_subs = _ES_HEADER_SUFFIX.subn("", raw_header)
        is_es = n_subs > 0
        header = norm_header(stripped if is_es else raw_header)
        key = _BLOCK_HEADER_ALIASES.get(header)
        if key is None:
            for alias, block_key in _BLOCK_HEADER_ALIASES.items():
                if header.startswith(alias + " "):
                    key = block_key
                    break
        if key is None:
            print(f"[venue_email] {label}: unrecognized section {raw_header!r}, skipped",
                  file=sys.stderr)
        else:
            key = f"{key}_es" if is_es else key
        current_key = key
    commit()
    return blocks


def _load_series_block(venue, series, root=None):
    """{block_key: content} for this exact venue + series, read fresh from
    <root>/<Venue>/<Series>.md — {} if the venue has no folder, no filename
    matches (case/whitespace-insensitive, since series is freeform text
    typed per booking), or the file can't be read. Never raises — a missing
    or malformed template just means that series renders the plain venue
    email, same as no series at all.

    Exact match wins; failing that, a PREFIX match (2026-09-12, for 513
    Airwaves) — some recurring series get the week's guest act appended
    right into the `series` field itself ('513 Airwaves w/ Inhaler Radio'
    one week, a different act the next), so a file named '513 Airwaves.md'
    matches any series value that starts with '513 airwaves '. Longest
    matching stem wins if more than one file could prefix-match."""
    if not venue or not series:
        return {}
    vdir = (Path(root) if root else SERIES_EMAIL_ROOT) / venue.strip()
    if not vdir.is_dir():
        return {}
    target = _norm_series(series)
    best_prefix = None
    for path in sorted(vdir.glob("*.md")):
        stem = _norm_series(path.stem)
        if stem == target:
            best_prefix = path
            break
        if target.startswith(stem + " ") and (best_prefix is None or
                len(stem) > len(_norm_series(best_prefix.stem))):
            best_prefix = path
    for path in ([best_prefix] if best_prefix else []):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001 — an unreadable template isn't fatal
            print(f"[venue_email] couldn't read {path}: {e!r}", file=sys.stderr)
            return {}
        return _parse_series_email_file(text, label=str(path))
    return {}


def schedule_block_for(venue, series, root=None, lang="en"):
    """The whole 'Day Schedule:' block, verbatim, for this venue + series —
    None if the series file has no Schedule section (or no series/file at
    all), meaning the generic per-show schedule fields apply as usual.
    Callers should let a non-None result WIN over whatever a booking's own
    schedule fields say — that's the point of a series whose schedule never
    changes (Brian, 2026-09-09: Salsa On The Square is the first).

    lang='es' looks for a "## Schedule (Español)" section instead (see
    _parse_series_email_file) and returns None if the series file doesn't
    have one — even if the English "## Schedule" does — rather than ever
    falling back to English prose inside an otherwise-Spanish email. A
    caller sending a bilingual email should treat that None as "build the
    generic Spanish schedule instead," not "reuse the English block." """
    blocks = _load_series_block(venue, series, root)
    return blocks.get("schedule_es" if lang == "es" else "schedule") or None


def crew_schedule_for(venue, series, root=None):
    """[(label, time), ...] in file order for this venue + series' locked
    crew schedule — the day-sheet DOCX's own small crew table (top-left of
    the advance, normally Crew Call / Load In-Sound Check / Performance /
    Load-out / Curfew) gets its rows REPLACED wholesale with exactly this
    list when present, one row per entry, instead of trying to cram a
    multi-set series into the template's default 5 rows (Brian, 2026-09-09:
    'each time change should have its own cell in the table' — a prior cut
    that crammed Salsa On The Square's 3 sets + 2 breaks into one
    Performance cell as multiple lines wasn't readable enough). [] if the
    series file has no Crew Schedule section.

    Each non-blank line is 'Label: time' — the label becomes that row's
    right-hand cell, the time (which may be blank, e.g. 'Crew Call:' with
    nothing after it — the row still appears, just unfilled, same as any
    other show) becomes the left-hand cell. Labels are whatever the file
    says, not constrained to the template's original 5 names — write
    'Set #1', 'Dance Instruction #1', etc. and daysheet.py builds exactly
    that many rows."""
    blocks = _load_series_block(venue, series, root)
    raw = blocks.get("crew_schedule")
    if not raw:
        return []
    out = []
    for line in raw.splitlines():
        if ":" not in line:
            continue
        label, _, value = line.partition(":")
        label = label.strip()
        if label:
            out.append((label, value.strip()))
    return out


def locked_schedule_series(root=None):
    """Every series name (flat across all venues) that has a locked '##
    Schedule' section — used by the booking form to hide the schedule-time
    fields entirely for a series whose times are fixed in code, rather than
    silently accepting and ignoring whatever gets typed there (Brian,
    2026-09-09). Flat rather than venue-scoped: on the rare chance the same
    series name is ever locked at one venue and free at another, this errs
    toward hiding the fields — a UI nicety, not the actual enforcement
    (schedule_block_for stays properly venue-scoped and authoritative
    regardless of what the form shows). Never raises — a missing folder or
    an unreadable file just means nothing's reported as locked."""
    root = Path(root) if root else SERIES_EMAIL_ROOT
    out = set()
    if not root.is_dir():
        return []
    for vdir in root.iterdir():
        if not vdir.is_dir():
            continue
        for path in vdir.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001 — best-effort, skip a bad file
                continue
            if _parse_series_email_file(text, label=str(path)).get("schedule"):
                out.add(path.stem)
    return sorted(out)


# Series whose advance email goes out English-then-Spanish in ONE message
# (draft_emails.py), with two form links — Brian, 2026-09-12, Salsa On The
# Square is the first and so far only one. Every other series is completely
# unaffected: English-only, exactly as before. Add a series name here (as
# it's literally typed in the advance-list sheet's `series` column) once
# its email content override file has "(Español)" sections for every block
# it customizes — see blocks_for's docstring.
BILINGUAL_SERIES = {"Salsa On The Square"}


def is_bilingual_series(series):
    return _norm_series(series) in {_norm_series(s) for s in BILINGUAL_SERIES}


# Spanish equivalents of the handful of short labels draft_emails.py builds
# in PYTHON rather than in the template (advance_es.md.j2's header note
# lists these) — used only when rendering the Spanish half of a bilingual
# send. Values, not the labels, still come from the booking (times, names,
# numbers); these are purely the surrounding words.
SCHEDULE_ROW_LABELS_ES = {
    "load_in": "Carga", "soundcheck": "Prueba de sonido",
    "event_start": "Inicio del evento", "event_end": "Fin del evento",
    "curfew": "Hora límite",
}
SET_LENGTH_LABEL_ES = "Duración del set"
BILL_HEADER_ES = "Cartelera:"
# SLOT_LABELS_ES retired 2026-09-15 with the slots themselves — the Spanish
# bill block lists each artist by set time now, the same as the English one.
TIME_TBC_ES = "hora por confirmar"
# summarize_submission's labels (draft_emails.py), for a returning artist's
# "here's what we have on file" block in the Spanish half.
SUMMARY_LABELS_ES = {
    "Last show": "Último show", "Performers + crew": "Artistas y equipo de trabajo",
    "Monitors": "Monitores", "Own IEMs": "IEM propios", "Stage": "Escenario",
    "Own engineer": "Ingeniero propio", "Merch": "Mercancía",
    "Band tent": "Carpa de la banda", "Large vehicle": "Vehículo grande",
    "Backline": "Backline",
}


# "Text or call your day-of contact when you're about 5 minutes out, and
# introduce yourself..." only makes sense when the email names a day-of
# contact (audit #15). Without one, drop the texting clause and keep the
# introduce-yourself instruction.
_TEXT_ON_ARRIVAL = {
    "en": re.compile(r"Text or call your day-of contact when you're about 5 minutes out,\s*and\s*", re.I),
    "es": re.compile(r"Llamen o envíen un mensaje de texto a su contacto del día del evento cuando "
                     r"estén a unos 5 minutos de llegar,\s*y\s*", re.I),
}


def without_text_on_arrival(blocks, lang="en"):
    pat = _TEXT_ON_ARRIVAL["es" if lang == "es" else "en"]
    cap = re.compile(pat.pattern + r"(\w)", pat.flags)
    out = dict(blocks)
    for k, v in out.items():
        if isinstance(v, str) and pat.search(v):
            out[k] = cap.sub(lambda m: m.group(1).upper(), v)
    return out


class _SafeDict(dict):
    """str.format_map backing that renders an unsupplied placeholder as '' rather
    than raising — so one missing key can't turn a whole block into literal braces."""
    def __missing__(self, key):
        return ""


def blocks_for(venue, series=None, lang="en", third_party=False, **dynamic):
    """lang='es' swaps in VENUE_EMAIL_ES/DEFAULT_ES (draft, 2026-09-12,
    Fountain Square only so far — other venues fall back to DEFAULT_ES's
    generic Spanish copy, same as the English path falls back to DEFAULT).

    third_party=True (Brian, 2026-09-16): a 3rd-party event has no touring
    band's own vehicles, so the garage-QR/validation paragraph doesn't apply
    — swaps in a venue's own `<key>_third_party` block wherever one exists
    (today: Fountain Square's load_in) and leaves every other block as-is.
    A venue with no such override just keeps its normal block, third_party
    or not.

    A series override file (Series Email Templates/<Venue>/<Series>.md) is
    language-aware per BLOCK, not per file: for lang='es' this applies only
    that file's `<key>_es` sections (from a "## <Section> (Español)"
    header) on top of the Spanish venue defaults — an English-only section
    in that same file (no "(Español)" counterpart) is skipped rather than
    dropping untranslated English prose into an otherwise-Spanish email.
    Write a "(Español)" counterpart for every section a bilingual series
    overrides — see Salsa On The Square's file for the pattern."""
    table = VENUE_EMAIL_ES if lang == "es" else VENUE_EMAIL
    default = DEFAULT_ES if lang == "es" else DEFAULT
    v = table.get((venue or "").strip(), {})
    out = dict(default)
    out.update({k: val for k, val in v.items() if val is not None})
    if third_party:
        for k in list(out):
            tp = v.get(f"{k}_third_party")
            if tp is not None:
                out[k] = tp
    if series:
        override = _load_series_block(venue, series)
        if lang == "es":
            es_override = {k[:-3]: val for k, val in override.items()
                            if k.endswith("_es") and val is not None}
            out.update(es_override)
        else:
            out.update({k: val for k, val in override.items()
                        if val is not None and not k.endswith("_es")})
    if dynamic:
        safe = _SafeDict(dynamic)
        for k, text in out.items():
            if isinstance(text, str) and "{" in text:
                try:
                    # format_map with a blank-defaulting dict: a missing
                    # placeholder renders empty instead of leaving the WHOLE
                    # block's {braces} literal in the email (Brian, 2026-09-11).
                    out[k] = text.format_map(safe)
                except (IndexError, ValueError):
                    pass  # positional/malformed braces — leave as-is
    return out
