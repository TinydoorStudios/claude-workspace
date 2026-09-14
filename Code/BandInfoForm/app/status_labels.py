"""One label set for every status surface (2026-09-13 audit #17): the live
dashboard, artist page, daily digest, Show Status Log and the advance-list
sheet's STATUS block all read from here, so they can never disagree again.

state key (advance_status.state) -> (label, css class, fill hex, text hex)
"""
STATE = {
    "queued":           ("Queued",                "queued",    "E5E7EB", "1F2937"),
    "awaiting":         ("Sent — Awaiting Reply", "ready",     "C7D2FE", "1E3A5F"),
    "ready_to_send":    ("Sent — Awaiting Reply", "ready",     "C7D2FE", "1E3A5F"),
    "followup_due":     ("Follow-up Due",         "due",       "FFE4B5", "7C2D12"),
    "followup_drafted": ("Follow-up Sent",        "followup",  "DBEAFE", "1E3A5F"),
    "responded":        ("Advancing In Progress", "responded", "E9D8FD", "44337A"),
    "finalized":        ("Finalized",             "finalized", "C6EFCE", "14532D"),
    "held":             ("On Hold",               "held",      "FDE68A", "78350F"),
    "cancelled":        ("Cancelled",             "cancelled", "FECACA", "7F1D1D"),
}

MEANINGS = {
    "Queued": "Booked; the welcome email hasn't gone out yet (it sends once the show is within 21 days).",
    "Sent — Awaiting Reply": "Welcome email sent via Outlook; the band hasn't submitted the form yet.",
    "Follow-up Due": "No response and the show is inside its next reminder (7 / 3 / 1 days out).",
    "Follow-up Sent": "At least one reminder has gone out; still no response.",
    "Advancing In Progress": "The band submitted. Waiting on a human to review and Mark Finalized.",
    "Finalized": "Reviewed and signed off.",
    "On Hold": "Missing from the advance sheet (or a possible typo correction). Nothing sends until you "
               "cancel, restore or merge it.",
    "Cancelled": "Cancelled. Kept for the record; nothing sends and its doc is left as-is.",
}


def label(state):
    return STATE.get(state, (state or "—",))[0]


def css(state):
    return STATE.get(state, (None, "queued"))[1]


def fill(state):
    return STATE.get(state, (None, None, "E5E7EB"))[2]


def text_color(state):
    return STATE.get(state, (None, None, None, "374151"))[3]


def dashboard_map():
    """{state: (label, css)} — the shape app.py/templates already use."""
    return {k: (v[0], v[1]) for k, v in STATE.items()}
