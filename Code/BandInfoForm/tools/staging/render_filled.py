"""Local check: draw realistic, heavy filled Memo docs (1 and 2 artists) so a
Word export can prove they still fit one page.

    python3 staging/render_filled.py /private/tmp/memo-pages && staging/pages.sh f1 f2
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_memo_template as T  # noqa: E402

ev = {"_date": "Saturday, October 4, 2026", "_event": "Holly Bowling", "presenter": "JBM Productions",
      "event_type": "Third Party Event", "crew_call": "2:00p", "backline_load_in": "2:30p",
      "artist_load_in": "3:00p", "sound_check": "4:30p", "crew_break": "5:30p",
      "security_meeting": "6:15p", "doors": "7:00p", "house": "7:30p", "set_1": "8:00p",
      "set_1_end": "8:55p", "intermission": "Yes", "set_2": "9:15p", "set_2_end": "10:15p", "end_of_show": "10:15p", "curfew": "11:45p",
      "stage_support_rooms": ["A", "Studio"], "settlement": "Yes", "settlement_contact": "Tour manager"}
act = {"_name": "Holly Bowling Band", "set_length": "Two 50-minute sets with a 20-minute intermission",
       "_stage_plot": "See folder — 10.04.26 Holly Bowling Band Stage Plot.pdf, "
                      "10.04.26 Holly Bowling Band Stage Plot 2.pdf",
       "own_foh": "Yes", "engineer_foh": "Mike Smith", "own_mon": "House", "console_foh": "Tour",
       "console_mon": "House", "wedges": "4", "iems": "Yes", "iem_count": "3", "own_iems": "Yes",
       "split_snake": "Yes",
       "input_notes": "Piano needs 2 x KM184 inside lid; playback from laptop stereo DI; click to "
                      "drummer IEM only; talkback at FOH.",
       "backline": "Yes", "backline_notes": "Steinway D tuned to 440 day of show, Ampeg SVT with 8x10",
       "ld": "Artist LD", "lx_console": "Tour", "ground_package": "No",
       "lighting_notes": "Warm washes only, no haze. Their LD will busk on our console.",
       "risers": "Yes", "riser_count": "2", "grand_piano": "Yes",
       "scenic_notes": "Two backdrop banners, hung from the upstage pipe.",
       "dressing_rooms": ["A", "B"], "performers": "5", "hospitality": "Yes", "hospitality_amount": "250",
       "buyout": "Yes", "buyout_amount": "150", "parking": "SP+ Lot", "dashboard_passes": "3",
       "veh_personal": "2", "veh_sprinter": "1", "hotel": "No", "merch": "They sell", "runner": "No",
       "ground_transport": "No", "meet_greet": "Yes", "photography": "Yes",
       "photo_restrictions": "No flash, first three songs only, no photo pit.",
       "contact_name": "Pat Tester", "contact_phone": "513-555-0100",
       "contact_email": "pat.tester@example.com",
       "additional_info": "Staffing sheet (Other): Debbie Hosp + Merch. Artist arrives by 2:45."}
crew = [("FOH", "Brian Lloyd"), ("Monitors", "Alex D."), ("LX", "Roy"), ("Stage Hand", "Chris K."),
        ("Stage Hand", "Jen M."), ("Video", "Sam"), ("Stage Support", "Ann"),
        ("Stage Support", "Bo"), ("Stage Support", "Cy, Di"), ("Memo Lead", "Joe · 216-288-7269")]
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
T.build_advance(out / "f1.docx", 1, T.Values(ev, [act], crew))
T.build_advance(out / "f2.docx", 2, T.Values(ev, [dict(act, _name="Opener Duo"), act], crew))
