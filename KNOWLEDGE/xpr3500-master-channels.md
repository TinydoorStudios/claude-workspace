# XPR3500 MASTER 2026-07-29 — extracted channel data
Source: CPS 2.0 Channels Summary report (model H02RDH9VA1AN, s/n 867TTF2205)
All channels: TX freq == RX freq (simplex), TX DPL == RX DPL, Power High, TOT 60 s, TOT rekey 0,
DPL Invert No, DPL Turn-Off Code Yes, VOX No, Voice Emphasis De & Pre, Squelch Normal,
ARTS Disabled, Audio Enhancement None, Scrambling No, RX Only No, Bandwidth 12.5 kHz.

## Zone 1 — 3CDC (11 ch, Analog)
| # | Name | Freq MHz | DPL | Admit | Notes |
|---|---|---|---|---|---|
| 1 | FSQ-OPS | 451.0375 | 043 | Always | |
| 2 | FSQ-PROD | 451.2125 | 116 | Always | |
| 3 | FSQ-GARAGE | 451.5375 | 143 | Always | |
| 4 | WP-OPS | 451.6875 | 174 | Always | Scan List = ScanItems/List1, Auto Scan No |
| 5 | WP-PROD | 451.8875 | 331 | Always | |
| 6 | WP-GARAGE | 452.3375 | 465 | Always | |
| 7 | OTR-DIST | 452.4625 | 734 | Always | |
| 8 | MEM-PROD | 451.2125 | 244 | Always | |
| 9 | MEM-FOH | 451.5375 | 125 | Always | |
| 10 | ZIEGLER | 451.0375 | 546 | Always | |
| 11 | BBB | 451.6875 | 172 | Channel Free | RSSI -124 |

## Zone 2 — AMERICAN FIREWRK (10 ch, Analog) — all DPL 225, Admit Channel Free, RSSI -124
| # | Name | Freq MHz |
|---|---|---|
| 1 | AFX 1i | 462.8625 |
| 2 | AFX 2i | 467.8625 |
| 3 | AFX 3i | 456.8000 |
| 4 | AFX 4i | 464.5500 |
| 5 | AFX 5i | 462.8375 |
| 6 | AFX 6 - Cinci | 464.8250 |
| 7 | AFX 7 - Cinci | 469.8250 |
| 8 | AFX 8 - Cinci | 464.1250 |
| 9 | AFX 9 - Cinci | 469.1250 |
| 10 | AFX 10 - Cinci | 467.8500 |

## Zone 3 — Rozzi (16 ch, Analog) — all DPL 023, Admit Channel Free, RSSI -124
| # | Name | Freq MHz |
|---|---|---|
| 1 | Rozzi 1 | 464.5500 |
| 2 | Rozzi 2 | 456.7870 |
| 3 | Rozzi 3 | 456.8120 |
| 4 | Rozzi 4 | 456.8570 |
| 5 | Rozzi 5 | 456.8620 |
| 6 | Rozzi 6 | 456.8870 |
| 7 | Rozzi 7 | 469.5500 |
| 8 | Rozzi 8 | 469.5000 |
| 9 | Rozzi 9 | 467.9250 |
| 10 | Rozzi 10 | 467.9000 |
| 11 | Rozzi 11 | 467.8750 |
| 12 | Rozzi 12 | 467.8750 |  <-- DUPLICATE of Rozzi 11 in the master
| 13 | Rozzi 13 | 467.8120 |
| 14 | Rozzi 14 | 467.7620 |
| 15 | Rozzi 15 | 464.8250 |
| 16 | Rozzi 16 | 467.7120 |

## Zone 4 — Event One FX (4 ch, DIGITAL)
Color Code 4, Repeater/Time Slot 1, Contact Name "EVENT ONE FX", Admit Always,
Privacy No, ARS Disabled, Group List None, Text Message Type Advantage, Data Call Confirmed Yes.
| # | Name | Freq MHz |
|---|---|---|
| 1 | Channel1 | 464.5000 |
| 2 | Channel2 | 464.5500 |
| 3 | Channel3 | 469.5000 |
| 4 | Channel4 | 469.5500 |

## Discrepancy vs the in-progress CPS 16 "Untitled1"
Untitled1 Zone1 currently holds 9: FSQ-OPS, FSQ-PROD, FSQ-GARAGE, WP-OPS, WP-PROD,
WP-GARAGE, OTR-DIST, **F/R-LLC**, **Memo FOH**.
Master 3CDC holds 11: ...OTR-DIST, **MEM-PROD**, **MEM-FOH**, **ZIEGLER**, **BBB**.
=> position 8 differs (F/R-LLC not in master), 9 renamed, 10-11 missing. Needs Brian's call.

## VERIFIED 2026-08-05 — Event One FX digital contact
Cross-checked two codeplugs, both agree:
- XPR3500 MASTER 2026-07-29.xctb (s/n 867TTF2205): contact **EVENT ONE FX** = Digital Calls-Group Call, **Call ID 10010**
- Event One FX CP200 4 Channel Digital.xctb (s/n 752TVH1767, their own radio): contact **Call1** = Digital Calls-Group Call, **Call ID 10010**
CP200 zone confirms channel params: Digital, Color Code 4, Repeater/Time Slot 1, ARS Disabled,
Group List None, Admit Always, Data Call Confirmed Yes, Power High, TOT 60, RX==TX,
freqs 464.5000 / 464.5500 / 469.5000 / 469.5500.

## Brian's rulings 2026-08-05 for the non-e 3500 build
- DROP ZIEGLER and BBB
- DROP anything "garage" (FSQ-GARAGE, WP-GARAGE deleted)
- KEEP MEM-PROD (451.2125, DPL 244) — must be added
- KEEP his own F/R-LLC (451.6875 DPL 265) and Memo FOH (451.6875 DPL 067)
- NO scan lists anywhere (List1 emptied — CPS 16 forbids deleting the last list; all channels set to None)
