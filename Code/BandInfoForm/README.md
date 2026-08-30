# 3CDC Band Advance Form

Blanket band advance / show-details intake form for 3CDC venues. Venue-neutral (venue is a
dropdown); no login required for bands; stage plot can be uploaded **or** described/linked.

## Live app

Small Flask app — this is the deliverable.

- Source: `app/app.py`, `app/templates/form.html`, `app/templates/thanks.html`
- Host: n8n VM `192.168.200.84`, deployed at `/opt/band-advance/`
- Service: systemd **`band-advance`** (gunicorn, `0.0.0.0:8097`, auto-restart)
- Test URL (Tailscale/LAN): http://192.168.200.84:8097
- Submissions: JSON in `/opt/band-advance/data/`, uploads in `/opt/band-advance/data/uploads/`

## Redeploy

Edit files under `app/`, then run `deploy_app.command` (scps the app + templates to the VM and
restarts the service). Or manually: `scp` the changed file to `/opt/band-advance/...` then
`sudo systemctl restart band-advance`.

## Design notes

- One `--gap` CSS variable drives even spacing between every question.
- Inline JS: the "split snake" question only appears (and is required) when
  "bringing your own IEMs" = Yes.
- All copy says **3CDC**, never Fountain Square / FSQ (except the venue dropdown option).

## Open items

- **Public URL** — Tailscale-only today. Needs a Cloudflare tunnel ingress rule (run from the
  Mac/VM; the sandbox can't reach the CF API). Options: `tinydoorstudios.com/bands` (nginx path,
  no DNS change) or a `bands.tinydoorstudios.com` subdomain.
- **Submission routing** — currently disk-only; email / Slack / NAS / Monday not yet wired.

## `_superseded/`

First-approach dead ends, kept for reference: the Google Apps Script (`build_form.gs` — abandoned
because Google Forms file upload requires a Google login) and the n8n Form Trigger workflow
(`band_advance_form.json` + `deploy_band_form.command` — abandoned because n8n forms can't do even
spacing or inline conditional fields).
