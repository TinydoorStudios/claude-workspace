"""One-off: the Holly Bowling (Memo, 10/4/26) advance drawn in the new Memo
layout, from the old MEMO Adv doc, the event paperwork xlsx, both riders and
the live staffing sheet (2026-09-29 draft for Brian). Not a pipeline piece.

    python3 staging/render_holly.py && staging/pages.sh holly
"""
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIF = Path.home() / "Documents/Claude/Code/BandInfoForm"
sys.path[:0] = [str(BIF / "tools"), str(BIF / "app")]
import build_memo_template as T  # noqa: E402
import memo_doc as MD  # noqa: E402

d = dt.date(2026, 10, 4)
roles, other = MD.crew_for(d, ["Holly Bowling"])
crew = MD.crew_rows(roles, "", "Joe · 216-288-7269")
ev = {"_date": d.strftime("%A, %B %-d, %Y"), "_event": "Holly Bowling (Solo Piano)",
      "event_type": "Internal Event", "crew_call": "3:00p", "backline_load_in": "3:00p",
      "artist_load_in": "4:00p", "sound_check": "4:30p", "crew_break": "5:30p",
      "security_meeting": "5:30p", "doors": "6:00p", "house": "6:30p", "set_1": "7:00p",
      "set_1_end": "8:15p", "intermission": "Yes", "set_2": "8:35p", "set_2_end": "9:45p", "end_of_show": "9:45p",
      "curfew": MD._plus("9:45p", 90), "stage_support_rooms": ["A", "B"], "settlement": "No"}
pre = "10.04.26 Holly Bowling"
act = {"_name": "Holly Bowling", "set_length": "Two sets, 20-min intermission",
       "_stage_plot": f"See folder — {pre} Tech Rider.pdf (plot + input list)",
       "own_foh": "Yes", "engineer_foh": "Daniel Thiels (tour)",
       "own_mon": "Yes", "engineer_mon": "Daniel Thiels (from FOH)",
       "console_foh": "House Q225", "console_mon": "House",
       "wedges": "0", "iems": "Yes", "iem_count": "1", "own_iems": "Yes", "split_snake": "No",
       "input_notes": "6 in: piano L/R DPA 4099 + piano L/R extra pair (tour-carried), talk vox SM58 "
                      "on boom w/ sandbag, Kaleidaloop looper SM57 or mono DI. Hardwired stereo IEM.",
       "backline": "Yes",
       "backline_notes": "MH Yamaha C3 tuned day of show (touch-up at crew break); 2nd bench for FX "
                         "pedals; 3 tall booms",
       "ld": "House LD", "lx_console": "Memo", "ground_package": "No",
       "risers": "No", "grand_piano": "Yes", "scenic_notes": "Solo grand piano, two benches.",
       "dressing_rooms": ["A"], "performers": "1 (+1 crew)", "hospitality": "Yes",
       "hospitality_amount": "50", "buyout": "Yes", "buyout_amount": "50 ($25 x 2)",
       "parking": "SP+ Lot", "dashboard_passes": "1", "veh_personal": "1", "hotel": "No",
       "merch": "Memo sells", "runner": "No", "ground_transport": "No", "meet_greet": "Yes",
       "contact_name": "Daniel Thiels (DOS, FOH)", "contact_phone": "615-454-0413",
       "contact_email": "drew@dodomgmt.com (Drew Granchelli, advance)",
       "additional_info": "Staffing sheet (Other): " + ", ".join(other)
                          + ". Hospitality rider on file; merch seller: Ken."}
out = Path("/private/tmp/memo-pages") / "holly.docx"
out.parent.mkdir(parents=True, exist_ok=True)
T.build_advance(out, 1, T.Values(ev, [act], crew))
print(out)
