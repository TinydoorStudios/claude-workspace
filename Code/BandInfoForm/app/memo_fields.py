"""Memorial Hall advance: the one field spec (2026-09-29).

Memo runs its own form (templates/memo_form.html) and its own doc
(tools/build_memo_template.py + tools/memo_doc.py) instead of the universal
band form and day-sheet. Everything that needs to know "what does the Memo
advance ask" reads this module: the form renderer, the /memo/submit parser,
and the doc filler.

Audience: "band" fields show on the artist's link; "staff" fields only show
to a signed-in staff member (Brian fills them himself, or the artist never
sees them: schedule, crew, money, rooms, routing). A staff member sees every
field, so one person can fill a show end to end.

Several people fill the same show. Every save is a new submission holding
only what that person sent; memo_state() layers them oldest to newest, so a
later non-blank answer wins and a blank never wipes anyone else's.

Kinds:
  text / textarea / number / time   free entry
  choice      radio group, `options`; the doc ticks the chosen box
  multi       checkbox group, `options`
  yesno       choice with options ("Yes", "No") — Brian: no N/A anywhere
"""

VENUE = "Memorial Hall"
FORM_KEY = "memo"          # submissions.data->>'_form'
YN = ("Yes", "No")

# House defaults the doc prints when nobody has entered anything.
DEFAULTS = {
    "memo_lead": "Joe · 216-288-7269",
    "console_foh": "House Q225",
    "console_mon": "House",
    "ld": "House LD",
    "lx_console": "Memo",
}

# Curfew = End of Show + 90 min when nobody typed one (Brian, 2026-09-29).
CURFEW_AFTER_END_MIN = 90


def F(key, label, kind="text", audience="band", options=None, help=None, per_act=True,
      placeholder=None, show_if=None):
    """show_if=(other_key, value): only shown (and only sent) while that
    question is answered `value` — the FSQ form's conditional pattern."""
    return {"key": key, "label": label, "kind": kind, "audience": audience,
            "options": tuple(options) if options else (YN if kind == "yesno" else ()),
            "help": help, "per_act": per_act, "placeholder": placeholder, "show_if": show_if}


SECTIONS = [
    ("Event", "staff", [
        F("presenter", "Presenter", audience="staff", per_act=False,
          help="Third-party presenter, e.g. JBM Productions."),
        F("event_type", "Event type", "choice", "staff", ("Internal Event", "Third Party Event"),
          per_act=False),
    ]),
    ("Schedule", "staff", [
        F("crew_call", "Crew call", "time", "staff", per_act=False),
        F("backline_load_in", "Backline load-in", "time", "staff", per_act=False),
        F("artist_load_in", "Artist load-in", "time", "staff", per_act=False),
        F("sound_check", "Sound check", "time", "staff", per_act=False),
        F("crew_break", "Crew break", "time", "staff", per_act=False),
        F("security_meeting", "Security meeting", "time", "staff", per_act=False),
        F("doors", "Doors", "time", "staff", per_act=False),
        F("house", "House", "time", "staff", per_act=False),
        F("set_1", "Set 1 start", "time", "staff", per_act=False),
        F("set_1_end", "Set 1 end", "time", "staff", per_act=False),
        F("intermission", "Intermission (20 min)", "yesno", "staff", per_act=False),
        F("set_2", "Set 2 start", "time", "staff", per_act=False),
        F("set_2_end", "Set 2 end", "time", "staff", per_act=False),
        F("end_of_show", "End of show / load-out", "time", "staff", per_act=False),
        F("curfew", "Curfew", "time", "staff", per_act=False,
          help="Leave blank for end of show + 90 minutes."),
    ]),
    ("Crew", "staff", [
        F("video", "Video", audience="staff", per_act=False),
        F("memo_lead", "Memo lead", audience="staff", per_act=False,
          placeholder=DEFAULTS["memo_lead"]),
        F("crew_override", "Crew override", "textarea", "staff", per_act=False,
          help="FOH, Monitors, LX, Stage Hands and Stage Support fill from the staffing "
               "sheet's Memorial Hall block. Only type here to override it, one per line, "
               "e.g. \"LX: Roy\" or \"Stage Hand: Jen, Sam\"."),
    ]),
    ("Audio", "band", [
        F("set_length", "Set length", placeholder="e.g. two 45-min sets"),
        F("own_foh", "Are you bringing your own FOH engineer?", "choice",
          options=("Yes", "House")),
        F("engineer_foh", "FOH engineer's name", show_if=("own_foh", "Yes")),
        F("own_mon", "Are you bringing your own monitor engineer?", "choice",
          options=("Yes", "House")),
        F("engineer_mon", "Monitor engineer's name", show_if=("own_mon", "Yes")),
        F("console_foh", "FOH console", "choice", options=("House Q225", "Tour")),
        F("console_mon", "Monitor console", "choice", options=("House", "Tour")),
        F("wedges", "Number of wedges", "number"),
        # mirrors the Fountain Square IEM question chain (Brian, 2026-09-29)
        F("iems", "Do you use in-ear monitors?", "yesno"),
        F("iem_count", "How many in-ear systems do you need?", "number", show_if=("iems", "Yes")),
        F("own_iems", "Are you bringing your own in-ear system?", "yesno", show_if=("iems", "Yes")),
        F("split_snake", "Are you providing a split snake for front of house?", "yesno",
          show_if=("own_iems", "Yes"),
          help="Since you're bringing your own in-ear system, let us know if you're providing the split."),
        F("input_notes", "Input notes", "textarea",
          help="Anything the input list doesn't say: DIs, playback, click, talkback."),
        F("backline", "Do you need backline from us?", "yesno"),
        F("backline_notes", "Backline requested", "textarea", show_if=("backline", "Yes")),
    ]),
    ("Lighting", "band", [
        F("ld", "Lighting designer", "choice", options=("House LD", "Artist LD")),
        F("lx_console", "Lighting console", "choice", options=("Memo", "Tour")),
        F("ground_package", "Bringing a ground package?", "yesno"),
        F("lighting_notes", "Lighting notes", "textarea"),
    ]),
    ("Scenic", "band", [
        F("risers", "Do you need risers?", "yesno",
          help="Each riser is 4' x 8' x 1' tall."),
        F("riser_count", "How many risers?", "number", show_if=("risers", "Yes")),
        F("grand_piano", "House grand piano", "yesno"),
        F("scenic_notes", "Scenic notes", "textarea"),
    ]),
    ("Hospitality & logistics", "band", [
        F("performers", "Number of performers", "number"),
        F("dressing_rooms", "Dressing rooms", "multi", "staff",
          ("A", "B", "C", "D", "Studio", "Any")),
        F("stage_support_rooms", "Stage support rooms", "multi", "staff",
          ("A", "B", "C", "D", "Studio", "None"), per_act=False),
        F("hospitality", "Hospitality", "yesno", "staff"),
        F("hospitality_amount", "Hospitality amount ($)", audience="staff"),
        F("buyout", "Buyout", "yesno", "staff"),
        F("buyout_amount", "Buyout amount ($)", audience="staff"),
        F("parking", "Parking", "choice", "staff", ("SP+ Lot", "Washington Park", "No")),
        F("veh_personal", "Personal vehicles", "number", help="How many of each are you bringing?"),
        F("veh_sprinter", "Sprinter vans", "number"),
        F("veh_bus", "Tour buses", "number"),
        F("veh_semi", "Semis", "number"),
        F("dashboard_passes", "SP+ dashboard passes", "number", "staff"),
        F("wp_passes", "Washington Park passes", "number", "staff"),
        F("hotel", "Do you need a hotel?", "yesno"),
        F("merch", "Merch", "choice", options=("They sell", "Memo sells", "No"),
          help="\"They sell\" = you run your own table."),
        F("runner", "Do you need a runner?", "yesno"),
        F("ground_transport", "Do you need ground transportation?", "yesno"),
        F("meet_greet", "Meet & greet?", "yesno"),
        F("photography", "Photography allowed?", "yesno"),
        F("photo_restrictions", "Photo restrictions", "textarea",
          help="No flash, first three songs only, no photo pit, etc."),
        F("settlement", "Settlement", "yesno", "staff", per_act=False),
        F("settlement_contact", "Settlement contact", audience="staff", per_act=False),
    ]),
    ("Internal notes", "staff", [
        F("internal_notes", "Internal notes", "textarea", "staff", per_act=False,
          help="Budgets, deals, anything for us only. Prints on the advance doc; "
               "the band never sees it."),
    ]),
    ("Day-of contact", "band", [
        F("contact_name", "Name"),
        F("contact_phone", "Cell"),
        F("contact_email", "Email"),
        F("additional_info", "Anything else we should know?", "textarea", audience="both"),
    ]),
]

# Upload buckets. Every one takes several files (Brian: artists must be able
# to upload multiple files); all of them land in the show's Dropbox folder.
UPLOADS = [
    ("up_stage_plot", "Stage plot", "stage_plot"),
    ("up_input_list", "Input list", "input_list"),
    ("up_tech_rider", "Tech rider", "tech_rider"),
    ("up_hospitality", "Hospitality rider", "hospitality_rider"),
    ("up_lighting", "Lighting plot / notes", "lighting"),
    ("up_video", "Video / projection content", "video"),
    ("up_other", "Anything else", "other"),
]
# Filed as "<MM.DD.YY> <Act> <name>.<ext>" (Brian, 2026-09-29); "other" keeps
# the name it was sent with.
FILED_NAME = {
    "stage_plot": "Stage Plot", "input_list": "Input List", "tech_rider": "Tech Rider",
    "hospitality_rider": "Hospitality Rider", "lighting": "Lighting Plot and Notes",
    "video": "Video Projection Content",
}
UPLOAD_KINDS = {kind: label for _f, label, kind in UPLOADS}

FIELDS = {f["key"]: f for _s, _a, fs in SECTIONS for f in fs}
BAND_KEYS = [k for k, f in FIELDS.items() if f["audience"] in ("band", "both")]
STAFF_KEYS = [k for k, f in FIELDS.items() if f["audience"] in ("staff", "both")]
EVENT_KEYS = [k for k, f in FIELDS.items() if not f["per_act"]]


def parse(form, staff):
    """The fields this person may set, from a submitted form. Blank text is
    dropped (blank never wipes); a multi group is kept even when empty only
    if the person could see it and marked it touched (its hidden `_seen`)."""
    out = {}
    for k, f in FIELDS.items():
        if f["audience"] == "staff" and not staff:
            continue
        if f["show_if"] and (form.get(f["show_if"][0]) or "") != f["show_if"][1]:
            continue        # its question isn't answered that way: it wasn't asked
        if f["kind"] == "multi":
            if form.get(f"{k}__seen"):
                picks = [o for o in form.getlist(k) if o in f["options"]]
                out[k] = picks
            continue
        v = (form.get(k) or "").strip()
        if not v:
            continue
        if f["options"] and v not in f["options"]:
            continue
        out[k] = v[:4000] if f["kind"] == "textarea" else v[:300]
    return out


def merge(datas):
    """Layer submissions oldest -> newest: non-blank values win, blanks don't
    erase. File lists accumulate (every upload stays on the show)."""
    state, files = {}, []
    for d in datas:
        d = d or {}
        for k in FIELDS:
            v = d.get(k)
            if v in (None, "") or (isinstance(v, list) and not v and FIELDS[k]["kind"] != "multi"):
                continue
            state[k] = v
        for fi in d.get("memo_files") or []:
            if fi not in files:
                files.append(fi)
    state["memo_files"] = files
    return state


def display(v):
    """How a stored answer reads to a person (a multi group joins)."""
    if isinstance(v, (list, tuple)):
        return ", ".join(v) if v else "(none)"
    return "" if v is None else str(v)


def _same(a, b):
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return sorted(a or []) == sorted(b or [])
    return str(a or "").strip() == str(b or "").strip()


def split_changes(current, new):
    """(apply, held) for a band save (Brian, 2026-09-29: changes to the advance
    are asked, not applied). A field already answered on this show whose new
    value differs is held for Brian's call; everything else applies."""
    apply, held = {}, {}
    for k, v in new.items():
        cur = current.get(k)
        answered = cur not in (None, "") and not (isinstance(cur, list) and not cur)
        if answered and not _same(cur, v):
            held[k] = v
        else:
            apply[k] = v
    return apply, held
