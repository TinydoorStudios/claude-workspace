# FSQ Filter Calibration — RESOLVED 2026-06-10, no console check needed

This kit is obsolete. Brian's offline-editor save-diff (`klaud edited.ses` vs
`brian fsq start.ses`, kept in `~/.wine/drive_c/Projects/`) settled the encoding
the same day this was built:

- **HPF stored = 0.8 × displayed Hz** (display 84.1 → stored 67.243)
- **LPF stored = 1.25 × displayed Hz** (display 5.75 kHz → stored 7191; off = 25000)

Both writes are enabled in `Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py`.
`FSQ_Filter_Cal.ses` is kept only as a harmless artifact — do not load it for a
show. Full findings: the 2026-06-10 addendum in
`Q225 SES Patcher SOP/FSQ SES Patcher - Claude Code Handoff.md`.
