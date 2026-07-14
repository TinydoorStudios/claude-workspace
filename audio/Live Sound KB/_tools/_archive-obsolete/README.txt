These scripts are OBSOLETE as of 2026-06-14.

They tried to fix the KB SOP 404 problem by editing local cloudflared config.yml
(on the n8n VM and inside CT 101) and nginx config. The tunnel is REMOTE-managed
(config_src: cloudflare) — those local files are ignored by the live tunnel, which
is why none of these worked.

The real fix lives in the Cloudflare API. See the two scripts kept in the parent
_tools folder:
  - KB-Diagnose-API.command  (pulls authoritative tunnel config + live tests)
  - KB-Fix-Tunnel-API.command (applies the /assets -> nginx ingress rule)

Kept here for history only. Do not run.
