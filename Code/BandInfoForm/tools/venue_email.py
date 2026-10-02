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
- Content: family-friendly only. No foul language or gestures, including in prerecorded tracks, live vocals and sound check.
- Performer safety: stay on the stage. No crowd surfing, climbing, jumping off the stage, or stepping on sound equipment.
- Audience safety: don't throw or shoot anything into the crowd (confetti, T-shirts, bottles, merch, CDs, etc.).
- Weather: rain or shine. We check the weather about 3 hours before start; if you don't hear otherwise, the show goes on.
- Weather holds: if 3CDC calls a lightning hold, stop and clear the stage right away. The stage stays dark until we get the all-clear, then we pick the show back up.
- Payment: all groups are paid after the performance, not before."""

# Spanish translation of COMMON_REQUIREMENTS — draft, 2026-09-12. Kept as a
# parallel constant rather than folded into VENUE_EMAIL_ES so a future
# language-aware render_email() (not yet wired — see advance_es.md.j2) can
# pick requirements + COMMON_REQUIREMENTS_ES the same way the English path
# picks blocks_for(...) + COMMON_REQUIREMENTS.
COMMON_REQUIREMENTS_ES = """\
- Contenido: solo apto para toda la familia. No se permite lenguaje soez ni gestos obscenos, incluyendo las pistas pregrabadas, las voces en vivo y la prueba de sonido.
- Seguridad de los artistas: permanezcan en el escenario. No se permite lanzarse al público, trepar, saltar del escenario ni pisar el equipo de sonido.
- Seguridad del público: no lancen ni disparen nada hacia el público (confeti, camisetas, botellas, mercancía, CD, etc.).
- Clima: el show se hace con lluvia o con sol. Revisamos el clima unas 3 horas antes del inicio; si no les avisamos otra cosa, el show sigue adelante.
- Pausas por clima: si 3CDC anuncia una pausa por rayos, dejen de tocar y despejen el escenario de inmediato. El escenario permanece apagado hasta que recibamos el aviso de que ya pasó el peligro, y entonces retomamos el show.
- Pago: todos los grupos reciben su pago después de la presentación, no antes."""

# Memorial Hall is indoors: no rain-or-shine or lightning-hold lines, and Brian
# dropped the content/age, performer-safety, audience-safety and payment lines
# from Memo's email (2026-09-29), so its common block is empty.
COMMON_REQUIREMENTS_INDOOR = ""   # Brian, 2026-09-29: no performer-safety, audience-safety or payment lines for Memo

# "Stand-Alone Internal" is a booking-page placeholder, not a show name; the
# welcome titles itself with the event name instead.
def is_standalone_series(series):
    return (series or "").strip().lower().startswith("stand-alone")


MEMO_BACKLINE_DEFAULT = "tell us on the form if you need backline arranged."
MEMO_BACKLINE_ARRANGED = "your backline is arranged. Check the details on the form."
MEMO_CREW_DEFAULT = "house crew covers sound, lighting and stagehand duties from load-in to load-out."


MEMO_PARKING_DEFAULT = ("Load-in details are in the attached tech packet. Tell us on the form which "
                        "vehicles you're bringing and we'll follow up on parking.")
_MEMO_PARKING_TEXT = {
    "Washington Park": ("The attached Load-In and Garage Parking sheet shows the freight door and how "
                        "parking works at the Washington Park Garage, directly across Elm Street. We'll "
                        "email your validation QR code ahead of the show."),
    "SP+ Lot": ("The attached Load-In and Reserved Lot Parking sheet shows the freight door and the "
                "reserved spaces in the lot behind the building. Enter the lot from Elm Street."),
    "No": "The attached Load-In sheet shows the freight door.",
}


def memo_parking_text(acts):
    """The Memo welcome's parking lines, matching the sheet parking_sheet_name() attaches
    (nothing attached when Parking is blank, so the generic ask stays)."""
    name = parking_sheet_name("Memorial Hall", None, acts)
    for choice, sheet in MEMO_PARKING_SHEETS.items():
        if sheet == name:
            return _MEMO_PARKING_TEXT[choice]
    return MEMO_PARKING_DEFAULT


def memo_backline_text(acts):
    """Per artist: 'ordered' in any act's backline notes means staff already
    arranged it; otherwise the standard ask."""
    for a in acts or []:
        if "ordered" in str(a.get("backline_notes") or "").lower():
            return MEMO_BACKLINE_ARRANGED
    return MEMO_BACKLINE_DEFAULT


def memo_crew_text(items):
    """Crew from the show's cost model: `items` is [(type, description)] for its
    Technicians rows plus Stage Support. No names, hours or money."""
    if not items:
        return MEMO_CREW_DEFAULT
    parts, support = [], []
    for typ, desc in items:
        typ, desc = str(typ).strip(), str(desc or "").strip()
        if typ.lower() == "stage support":
            support.append(desc)
            continue
        words = typ.split()
        first = words[0] if words else ""
        # 'an audio', 'a lighting'; a leading acronym goes by its spoken letter ('an FOH', 'an LX')
        vowel = first[:1].lower() in ("aefhilmnorsx" if len(first) > 1 and first.isupper() else "aeiou")
        a = "an" if vowel else "a"
        typ = " ".join(w if len(w) > 1 and w.isupper() else w.lower() for w in words)   # keep FOH / LX upper
        if desc[1:2].islower():      # 'Spot op' -> 'spot op'; leave FOH / LX / Video-style acronyms alone
            desc = desc[:1].lower() + desc[1:]
        parts.append(f"{a} {typ}" + (f" ({desc})" if desc else ""))
    if support:
        rooms = sorted(re.sub(r"^DR\s+", "", d, flags=re.I) for d in support)
        if all(re.fullmatch(r"[A-Za-z]", r) for r in rooms) and len(rooms) > 1:
            parts.append(f"stage support for dressing rooms {', '.join(rooms[:-1])} and {rooms[-1]}")
        else:
            parts.append(f"{len(support)} stage support staff" + (f" ({', '.join(d for d in support if d)})" if any(support) else ""))
    if len(parts) > 1:
        body = ", ".join(parts[:-1]) + " and " + parts[-1]
    else:
        body = parts[0]
    return f"your house crew is {body}."


MEMO_SCHEDULE_NOTE = ("  *Please confirm this schedule works or tell us what to adjust, including set lengths. "
                      "Don't arrive before your load-in time unless we've arranged it in advance.")


def memo_schedule_rows(ev):
    """The full Memo day as email rows, from the merged event answers
    (memo_doc.values_for's `event`: times already 7:30p style, curfew filled).
    Only what's actually filled in; [] when staff have typed no schedule at all.
    Crew call and backline load-in are left off (crew-side times, Brian 2026-09-29)."""
    def t(k):
        return str(ev.get(k) or "").strip()
    out = []

    def row(when, label):
        if when:
            out.append(f"  {when:<14}{label}")
    row(t("artist_load_in"), "Artist Load-In")
    row(t("sound_check"), "Sound Check")
    row(t("crew_break"), "Crew Break")
    row(t("security_meeting"), "Security Meeting")
    row(t("doors"), "Doors")
    row(t("house"), "House")

    def span(a, b):
        return f"{a}–{b}" if a and b else a
    row(span(t("set_1"), t("set_1_end")), "Set 1")
    if str(ev.get("intermission") or "").strip().lower() == "yes" and t("set_1_end") and t("set_2"):
        row(span(t("set_1_end"), t("set_2")), "Intermission")
    row(span(t("set_2"), t("set_2_end")), "Set 2")
    row(t("end_of_show"), "End of Show / Load-Out")
    row(t("curfew"), "Curfew")
    return out if len(out) >= 3 else []


INDOOR_VENUES = {"Memorial Hall"}


def common_requirements_for(venue, lang="en"):
    """The 3CDC-wide policy block for this venue: the indoor set for Memorial
    Hall (English only — no Spanish Memo email exists), the standard set for
    everyone else."""
    if lang == "en" and (venue or "").strip() in INDOOR_VENUES:
        return COMMON_REQUIREMENTS_INDOOR
    return COMMON_REQUIREMENTS_ES if lang == "es" else COMMON_REQUIREMENTS


# Generic, safe-to-send blocks for a venue we haven't customized yet (no FSQ specifics).
DEFAULT = {
    "location": None,   # falls back to the venue name in the template
    "load_in": """\
Load-In & Parking:
Your day-of contact will coordinate load-in and parking with you. Text or call them when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive. Note any large-vehicle needs on the form.""",
    "technical": """\
Technical:
- Backline / instrumentation: you provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors. Coordinate in advance if you're bringing your own engineer.
- On the form: stage plot / input list, stage layout, monitor count, and any scenic elements.""",
    "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; ask your day-of contact about a table.
- Hospitality: we provide water for all performers and crew.""",
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
- Backline / instrumentación: ustedes proporcionan todos los instrumentos, incluyendo amplificadores y cables de 1/4".
- Audio: proporcionamos un ingeniero que mezcla el FOH y los monitores. Coordinen con anticipación si van a traer su propio ingeniero.
- En el formulario: plano de escenario / lista de entradas, distribución del escenario, cantidad de monitores y cualquier elemento escenográfico.""",
    "hospitality": """\
Hospitalidad y sitio:
- Mercancía: si van a vender, ustedes proporcionan el vendedor, el punto de venta y el fondo de caja; pregúntenle a su contacto del día del evento sobre una mesa.
- Hospitalidad: proporcionamos agua para todos los artistas y el equipo de trabajo.""",
    "requirements": "",
}

VENUE_EMAIL = {
    "Fountain Square": {
        "location": "Fountain Square – Mainstage; 520 Vine St. Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
The load-in process at Fountain Square has changed — please review the attached document and acknowledge understanding on the form. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
We'll send QR codes that serve as your Fountain Square Garage validations. Each vehicle needs its own QR code before arriving. Scan it at the kiosk when you enter or exit (please don't pay). Garage clearance is 6'8". Need more validations or large-vehicle parking? Note it on the form.""",
        # 3rd-party version (Brian, 2026-09-16): same load-in line and the
        # attached document, but no garage-QR/validation paragraph — that
        # process is for a touring band's own vehicles, and a 3rd-party event
        # doesn't have one. See blocks_for's `third_party` swap.
        "load_in_third_party": """\
Load-In & Parking:
The load-in process at Fountain Square has changed — please review the attached document and acknowledge understanding on the form. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.""",
        "technical": """\
Technical:
- Backline / instrumentation: you provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own engineer. All engineers mix within the 95 dBA-Slow ordinance, and the Fountain Square engineer may baffle amps to reduce stage volume if needed.
- Lighting: we provide a house LD.
- On the form: stage plot / input list, flat vs. drum riser, monitor count, and any scenic elements.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms, but on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: we provide drink tickets and water for all performers and crew.""",
        # 3rd-party (Brian, 2026-09-25): no drink tickets for a 3rd-party event.
        "hospitality_third_party": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms, but on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: we provide water for all performers and crew.""",
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
We'll follow up with parking validations.""",
        # 3rd-party (Brian, 2026-09-25): no parking-validation line.
        "load_in_third_party": """\
Load-In & Parking:
Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.""",
        "technical": """\
Technical:
- Backline / instrumentation: you provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own engineer. All engineers mix within the 95 dBA-Slow ordinance, and the Washington Park engineer may baffle amps to reduce stage volume if needed.{lighting_line}
- On the form: stage plot / input list, {riser_phrase}monitor count, and any scenic elements.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms, but on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: we provide drink tickets and water for all performers and crew.""",
        # 3rd-party (Brian, 2026-09-25): no drink tickets for a 3rd-party event.
        "hospitality_third_party": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms, but on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: we provide water for all performers and crew.""",
        "requirements": "- Sound limit: strict 95 dBA-Slow at the FOH position, for all engineers (house or talent).",
    },
    # Elm Street Plaza (Brian, 2026-10-01): rebuilt from his old Blues & Brews welcome,
    # winter edition — basic stuff only, so no PA specs, no lighting, no site details beyond
    # unload + garage. Parking follows Fountain Square's rules (one QR per vehicle, validations
    # emailed ahead; staff typed counts reach the same daily parking digest), but the garage is
    # 84.51 (100 W 5th St), next to Court Street Plaza. Load-in documents come later.
    "Elm Street Plaza": {
        "location": "Elm Street Plaza; 620 Elm St, Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
You can unload on 6th St., north of Elm Street Plaza. This is 15-minute unloading only, so the vehicle must be moved before you go into sound check. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
We'll send QR codes that serve as your validations for the 84.51 garage (100 W 5th St, Cincinnati, OH 45202). Each vehicle needs its own QR code before arriving. You can scan it from your phone or print it, at the kiosk when you enter or exit, depending on what mode the garage is in (please don't pay). Need more validations or large-vehicle parking? Note it on the form.""",
        # 3rd-party: no touring-band validations (same rule as FSQ and WP, 2026-09-16/25).
        "load_in_third_party": """\
Load-In & Parking:
You can unload on 6th St., north of Elm Street Plaza. This is 15-minute unloading only, so the vehicle must be moved before you go into sound check. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.""",
        "technical": """\
Technical:
- Stage: your band must fit a 20' wide x 12' deep footprint.
- Backline / instrumentation: you provide all instruments, including your own amps and 1/4" cables.
- Audio: we provide a house engineer who mixes FOH and monitors. We provide power, mics, 2 wedges, stands, cables and a sound system. Coordinate in advance if you're bringing your own engineer.
- On the form: stage plot / input list, monitor count, and any scenic elements.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; ask your day-of contact about a table.
- Hospitality: we provide drink tickets and water for the band. Please confirm your total number of band members on the form.""",
        # 3rd-party: no drink tickets.
        "hospitality_third_party": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; ask your day-of contact about a table.
- Hospitality: we provide water for all performers and crew.""",
        "requirements": "",
    },
    # Memorial Hall (2026-09-29) — rebuilt from Brian's old Memo advance email
    # (the "Hi Feliks" one) plus the Memo tech specs. DRAFT: Brian reviews it
    # before Memo welcomes are un-paused. Indoor theater, so no tents or drink
    # tickets; the piano, house LD and crew lines are Memo's own. The
    # venue tech packet is an `_attachment*` file in Series Email Templates/
    # Memorial Hall/ (Brian uploads it separately; the "attached" lines assume it's there).
    "Memorial Hall": {
        "location": "Memorial Hall – Theater; 1225 Elm St, Cincinnati, OH 45202",
        # Replaces the "it replaces the questions we used to ask" sentence (advance.md.j2).
        "intro_tail": "It takes about five minutes.",
        # Printed under the form link (advance.md.j2), before the details.
        "review_note": "We've filled in what we already have from your contract and rider, below and on the form. Please check it for accuracy and add anything we're missing.",
        "load_in": """\
Load-In & Parking:
Load in on Grant Street, on the south side of the building. It's a street-level door (2'7" W × 6'10" H) into a freight elevator; there's no dock. The doors are locked at all times, so call your day-of contact when you arrive and they'll let you in.
{parking_text}
Please also give us a day-of contact for your team.""",
        # {backline_text} / {crew_text} / {parking_text} are set per show by draft_emails.py
        # (memo_backline_text / memo_crew_text / memo_parking_text below); it always supplies all three.
        "technical": """\
Technical:
- PA: full specs are in the attached tech packet.
- Audio: our house engineer mixes FOH and monitors from the house DiGiCo Quantum 225, in the house-right corner of the balcony. Coordinate in advance if you're bringing your own engineer or console.
- Monitors, mics, stage plot and input list: tell us what you need on the form, and upload your plot, input list and riders there.
- Lighting: we provide a house LD on the house lighting console. Tell us on the form if you have specific requests or are bringing your own LD.
- Scenic and projection: tell us on the form about any scenic or projection elements.
- Backline: {backline_text}
- Crew: {crew_text}""",
        "hospitality": """\
Hospitality & Site:
- Merch: the house takes no cut. You provide your own point of sale and bank. If you'd like us to coordinate a seller, note it on the form and we'll send you their rate.
- Meet & greet: any pre- or post-show meet & greet must be approved through your advance so we can plan for it.
- Photo / video: tell us on the form your policy on patron photography and video.
- Dressing rooms: up to four dressing rooms and a black box studio/meeting room. Details are in the attached tech packet.
- Hospitality, hotel, runner and ground transportation: note what you need on the form.""",
        "requirements": """\
- Sound limit: 95 dB LAeq,6min (A-weighted, 6-minute average) measured at balcony center, per city ordinance, for all engineers (house or talent).
- Building curfew: 90 minutes after the scheduled end of the show. All touring personnel, artists and gear must be out by then.""",
    },
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
Les enviaremos códigos QR que funcionan como sus validaciones del estacionamiento Fountain Square Garage. Cada vehículo necesita su propio código QR antes de llegar. Escaneen el código en el quiosco al entrar o al salir (por favor no paguen). La altura máxima del estacionamiento es de 6'8". ¿Necesitan más validaciones o espacio para vehículos grandes? Indíquenlo en el formulario.""",
        # 3rd-party version — see load_in_third_party in VENUE_EMAIL (English) above.
        "load_in_third_party": """\
Carga y estacionamiento:
El proceso de carga en Fountain Square ha cambiado — por favor revisen el documento adjunto y confirmen que lo entendieron en el formulario. Llamen o envíen un mensaje de texto a su contacto del día del evento cuando estén a unos 5 minutos de llegar, y preséntense en persona en cuanto lleguen.""",
        "technical": """\
Técnico:
- Backline / instrumentación: ustedes proporcionan todos los instrumentos, incluyendo amplificadores y cables de 1/4".
- Audio: proporcionamos un ingeniero que mezcla el FOH y los monitores desde el FOH. Coordinen con anticipación si van a traer su propio ingeniero. Todos los ingenieros mezclan dentro del límite de la ordenanza de 95 dBA-Slow, y el ingeniero de Fountain Square puede poner baffles a los amplificadores para reducir el volumen del escenario si es necesario.
- Iluminación: proporcionamos un diseñador de iluminación (LD) de la casa.
- En el formulario: plano de escenario / lista de entradas, escenario plano o con plataforma para batería, cantidad de monitores y cualquier elemento escenográfico.""",
        "hospitality": """\
Hospitalidad y sitio:
- Mercancía: si van a vender, ustedes proporcionan el vendedor, el punto de venta y el fondo de caja; nosotros proporcionamos una carpa junto al escenario con una mesa y sillas.
- Camerinos: no contamos con camerinos bajo techo, pero a solicitud podemos proporcionar una carpa de 10×10 pies con paredes laterales como espacio privado para la banda.
- Hospitalidad: proporcionamos vales de bebida y agua para todos los artistas y el equipo de trabajo.""",
        # 3rd-party — see hospitality_third_party in VENUE_EMAIL (English) above.
        "hospitality_third_party": """\
Hospitalidad y sitio:
- Mercancía: si van a vender, ustedes proporcionan el vendedor, el punto de venta y el fondo de caja; nosotros proporcionamos una carpa junto al escenario con una mesa y sillas.
- Camerinos: no contamos con camerinos bajo techo, pero a solicitud podemos proporcionar una carpa de 10×10 pies con paredes laterales como espacio privado para la banda.
- Hospitalidad: proporcionamos agua para todos los artistas y el equipo de trabajo.""",
        "requirements": "- Límite de sonido: máximo estricto de 95 dBA-Slow en la posición de FOH, para todos los ingenieros (de la casa o de la banda).",
    },
    # Add other venues here as Brian asks for them in Spanish.
}

# Where Brian's per-series email content actually lives — see that folder's
# own README.md for the exact file format (## Location / Load-In / Technical
# / Hospitality / Requirements sections, only fill in what you want to
# override). One subfolder per venue, one .md file per series within it.
import os as _os
SERIES_EMAIL_ROOT = Path(_os.environ.get("ADVANCE_DROPBOX_ROOT") or (Path.home() / "Dropbox")) / "Nyquist" / "Series Email Templates"


def attachment_display_name(filename):
    """The name an `_attachment*` file goes out under. `_attachment Memorial
    Hall Tech-Pack 2026.pdf` -> `Memorial Hall Tech-Pack 2026.pdf`: the
    `_attachment` marker and an optional `-N` ordering digit are stripped.
    A bare `_attachment.pdf` has nothing left to show, so it keeps its name."""
    import re
    stem, ext = _os.path.splitext(filename)
    m = re.match(r"^_attachment(?:-\d+)?[ _-]*(.+)$", stem)
    return m.group(1) + ext if m else filename


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
        out.append((attachment_display_name(path.name), ctype, base64.b64encode(data).decode("ascii")))
    return out


PARKING_SHEET_NAME = "Washington Park Garage Parking.pdf"      # Washington Park's own events
# Memorial Hall: one packet per Parking answer on the advance form (Brian, 2026-10-01).
# Each opens with the load-in page; tools/parking/memodocs.py builds them.
MEMO_PARKING_SHEETS = {
    "Washington Park": "Memorial Hall Load-In and Garage Parking.pdf",
    "SP+ Lot": "Memorial Hall Load-In and Reserved Lot Parking.pdf",
    "No": "Memorial Hall Load In Instructions.pdf",
}
PARKING_SHEET_FILES = {PARKING_SHEET_NAME, *MEMO_PARKING_SHEETS.values()}


def parking_sheet_name(venue, series=None, acts=None, parking=None):
    """Which parking/load-in sheet this show gets, or None.
    Memorial Hall: from the Parking answer on the advance form (`parking`, or the
    acts' answers; Washington Park wins over SP+ Lot wins over No when a bill mixes
    them). A blank answer gets nothing. Washington Park's own advanced events get the
    garage sheet unless the event is 3rd-party, which gets no validations."""
    venue = (venue or "").strip()
    if venue == "Washington Park":
        return None if (series or "").strip().lower() == "3rd party" else PARKING_SHEET_NAME
    if venue == "Memorial Hall":
        answers = [parking] if parking else [((a or {}).get("parking") or "") for a in acts or []]
        for choice in ("Washington Park", "SP+ Lot", "No"):
            if choice in answers:
                return MEMO_PARKING_SHEETS[choice]
    return None


def parking_sheet_attachment(name=None):
    """[(name, type, base64)] for a parking sheet (default: the Washington Park garage
    sheet), or [] if the file isn't there. tools/parking/ writes them into
    brand/parking/; local runs find that under app/brand, the VM under brand/."""
    import base64
    name = name or PARKING_SHEET_NAME
    if name not in PARKING_SHEET_FILES:
        return []
    here = Path(__file__).resolve()
    for d in (_os.environ.get("ADVANCE_BRAND_DIR"), here.parent.parent / "brand",
              here.parent.parent / "app" / "brand"):
        path = Path(d) / "parking" / name if d else None
        if path and path.is_file():
            return [(name, "application/pdf", base64.b64encode(path.read_bytes()).decode("ascii"))]
    return []


def wants_parking_sheet(venue, series=None, acts=None):
    return parking_sheet_name(venue, series, acts) is not None


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

    def label(i, name):
        shown = attachment_display_name(name)
        if "tech" in shown.lower():
            return "Tech pack"
        return labels.get(i, shown) if shown == name else shown

    lines = [f"{label(i, name)}: {url}" for i, (name, url) in enumerate(links)]
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


# A locked-schedule series' fixed times, for the booking form to pre-fill —
# Brian, 2026-09-17: those raw fields aren't just email input (schedule_block_for
# always wins there regardless); staffing/crew_report read them directly, so a
# locked series shouldn't leave them blank. NOT parsed from a series .md
# file's free-text "## Schedule" section — that prose isn't a reliable
# field-by-field source — so keep this BY HAND in sync with the times in
# that section. A locked series with no entry here just falls back to the
# old behavior (the booking form hides the fields instead of filling them).
#
# set_start/set_end (24h "HH:MM", the native <input type=time> format) are
# the top-of-form REQUIRED fields — fix #1, 2026-09-17: the first cut of this
# only filled the five "More detail" fields below them (load_in/soundcheck/
# event_start/event_end), so Set Start/Set End stayed blank and the form
# still couldn't submit. The booking form's own calcSetTimes() derives those
# four (plus Set Length) from set_start/set_end the same way it always has
# for Set Start/End typed by hand — so they aren't repeated here; only
# curfew needs its own entry, since nothing derives that one.
SERIES_SCHEDULE_DEFAULTS = {
    "Salsa On The Square": {
        "set_start": "19:00", "set_end": "22:00", "curfew": "11:00p",
    },
}


def schedule_defaults_for(series):
    """{field: value} for this series' pre-filled booking-form schedule — {}
    if none configured. Case/whitespace-insensitive, same as every other
    series lookup in this module. `field` is 'set_start' / 'set_end' (native
    time-input format) or 'curfew' (free text) — see SERIES_SCHEDULE_DEFAULTS'
    docstring for why load_in/soundcheck/event_start/event_end aren't here."""
    if not series:
        return {}
    key = next((s for s in SERIES_SCHEDULE_DEFAULTS if _norm_series(s) == _norm_series(series)), None)
    return dict(SERIES_SCHEDULE_DEFAULTS.get(key, {}))


def all_schedule_defaults():
    """{series: {field: value}} for every series with defaults configured —
    the whole table at once, for the booking form's JS to look up client-side
    without a round trip per series pick."""
    return {k: dict(v) for k, v in SERIES_SCHEDULE_DEFAULTS.items()}


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


# Series whose band-facing emails (welcome, reminder, thank-you) always carry
# an extra recipient on top of the band's own contact — Brian, 2026-09-17:
# Salsa On The Square's day-of contact (Nick Radina) gets a copy of every one
# of these so he sees exactly what the band was told. Keyed the same way as
# BILINGUAL_SERIES (as the series is literally typed in the advance-list
# sheet's `series` column); the value is a list so a series can ever need
# more than one extra recipient.
SERIES_EXTRA_RECIPIENTS = {
    "Salsa On The Square": ["NRadina@gmail.com"],
}


def with_extra_recipients(to, series):
    """`to` (a single address, or an already comma-joined string — see
    ADVANCE_FSQ_PARKING_NOTICE_TO for the existing convention this follows)
    with this series' SERIES_EXTRA_RECIPIENTS appended, comma-joined the same
    way. A series with no entry, or no `to` to start with, returns `to`
    unchanged — never invents a send to nobody. Case/whitespace-insensitive
    on the series name, same as every other series lookup in this module,
    and never adds an address already present. Every call site that emails a
    band for a welcome, reminder, or thank-you should route its `to` through
    this before handing it to mailer.send / the Outlook-draft path, so a new
    blanket recipient for a series is a one-line addition here, not a hunt
    through every send site."""
    if not to or not series:
        return to
    key = next((s for s in SERIES_EXTRA_RECIPIENTS if _norm_series(s) == _norm_series(series)), None)
    extra = SERIES_EXTRA_RECIPIENTS.get(key, []) if key else []
    if not extra:
        return to
    have = {a.strip().lower() for a in to.split(",") if a.strip()}
    add = [a for a in extra if a.strip().lower() not in have]
    return to if not add else ", ".join([to] + add)


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
    "Last show": "Último show", "Performers": "Artistas", "Crew": "Equipo de trabajo",
    "Monitors": "Monitores", "Own IEMs": "IEM propios", "Stage": "Escenario",
    "Own engineer": "Ingeniero propio", "Merch": "Mercancía",
    "Band tent": "Carpa de la banda", "Large vehicle": "Vehículo grande",
    "Backline": "Backline",
}


# ── band-facing shared bits (2026-09-24 research #7 + #14) ─────────────────
# Every email a BAND gets — welcome, reminders, day-before, thank-you,
# "info changed" — renders its set length and its subject through these, so
# the four tools that send band mail can't drift apart again.

def band_date(d, lang="en"):
    """A date the way band-facing copy writes one: 'Monday, October 6' in
    English, DD/MM/YYYY in the Spanish half (the convention every existing
    Spanish block already uses). '' for None."""
    if not d:
        return ""
    return d.strftime("%d/%m/%Y") if lang == "es" else d.strftime("%A, %B %-d")


def subject_key(band, venue, show_date):
    """'Band · Venue · 10/6' — 2026-09-24 research #14. Every band-facing
    subject ends with this (see band_subject), so one show's thread is
    findable in Outlook, in the band's own inbox, and by any future
    inbound-reply parsing. tourmanager.info's 'ARTIST – DATE – CITY, ST –
    VENUE' is the same idea; this is the short version. Blank parts are
    dropped rather than left as empty separators."""
    when = show_date.strftime("%-m/%-d") if show_date else ""
    return " · ".join(p for p in ((band or "").strip(), (venue or "").strip(), when) if p)


def band_subject(base, band, venue, show_date):
    """The human prefix, then the show key: 'Reminder — … — Band · Venue · 10/6'."""
    key = subject_key(band, venue, show_date)
    return f"{base} — {key}" if key else base


def _clock_minutes(v):
    """Minutes past midnight, via advance_db.parse_clock so there's exactly
    one clock parser in the codebase. Imported lazily — this module is pure
    content and shouldn't need the DB layer to import."""
    try:
        import advance_db
    except Exception:  # noqa: BLE001 — no DB layer on the path: no set times, not a crash
        return None
    return advance_db.parse_clock(v)


def _fmt_clock(mins, meridiem=True):
    h, m = divmod(mins % 1440, 60)
    ap = "am" if h < 12 else "pm"
    h = h % 12 or 12
    return f"{h}:{m:02d}" + (f" {ap}" if meridiem else "")


def _setlen(v):
    """'90' -> '90 min'; anything a human typed ('2 x 45') passes through."""
    v = str(v or "").strip()
    if not v:
        return ""
    return f"{v} min" if v.isdigit() else v


def set_line(set_start, set_end, set_time, lang="en"):
    """'Set: 8:00–9:30 pm (90 min)' — 2026-09-24 research #7. Set length is
    the one thing every source says a band must be told and Brian's emails
    never printed; the booking already has it. Same arithmetic as the booking
    page's calcSetTimes (end − start, rolling past midnight), and a hand-typed
    Set Length still wins over the derived one, exactly as it does there.

    Blank-safe: times only -> 'Set: 8:00–9:30 pm'; a length with no times ->
    'Set length: 90 min'; nothing on file -> ''."""
    s, e = _clock_minutes(set_start), _clock_minutes(set_end)
    span = ""
    if s is not None and e is not None:
        same_half = (s % 1440 < 720) == (e % 1440 < 720)
        span = f"{_fmt_clock(s, meridiem=not same_half)}–{_fmt_clock(e)}"
    elif s is not None:
        span = _fmt_clock(s)
    dur = _setlen(set_time)
    if not dur and s is not None and e is not None:
        d = e - s
        if d <= 0:
            d += 1440
        dur = f"{d} min"
    if span and dur:
        return f"Set: {span} ({dur})"
    if span:
        return f"Set: {span}"
    if dur:
        return f"{SET_LENGTH_LABEL_ES if lang == 'es' else 'Set length'}: {dur}"
    return ""


# "Text or call your day-of contact when you're about 5 minutes out, and
# introduce yourself..." only makes sense when the email names a day-of
# contact (audit #15). Without one, drop the texting clause and keep the
# introduce-yourself instruction.
# 2026-09-21 sweep (PRIOR-15): covers the venue blocks ("your day-of contact") AND the
# generic DEFAULT/DEFAULT_ES blocks ("them" / "Llámenlo o envíenle"), which used to slip through.
_TEXT_ON_ARRIVAL = {
    "en": re.compile(r"Text or call (?:your day-of contact|them) when you're about 5 minutes out,\s*and\s*",
                     re.I),
    "es": re.compile(r"(?:Llamen o envíen un mensaje de texto a su contacto del día del evento"
                     r"|Llámenlo o envíenle un mensaje de texto) cuando "
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
    (today: FSQ + WP load_in and hospitality — no parking validations, no drink tickets) and leaves every other block as-is.
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
    # review 2026-10-01 #1: run the substitution pass even with no dynamics —
    # a caller that passes none (the day-before email for most venues) used to
    # ship Memo's "{parking_text}" literally.
    safe = _SafeDict(dynamic or {})
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
