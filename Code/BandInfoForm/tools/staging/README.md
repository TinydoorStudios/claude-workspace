# Staging harness (review 2026-09-14)

An isolated copy of the whole system on the VM, so nothing run here can touch
the live database, the live Dropbox folders, or n8n. Same recipe the
2026-09-13 audit used by hand, scripted:

| Piece | Staging | Live |
|---|---|---|
| Database | `advance_test` (cloned from `advance` at setup) | `advance` |
| Dropbox root | `~/advtest/Dropbox` (rsync copy of Nyquist + current month folders) | `~/Dropbox` |
| Code | `~/advtest/code` (rsync of /opt/band-advance) | `/opt/band-advance` |
| Mail | `mailstub.py` on 127.0.0.1:8199, logs to `~/advtest/mail.jsonl` | n8n → Graph |
| App | gunicorn on 127.0.0.1:8198 | :8097 |

`ADVANCE_STAGING=1` makes `mailer.py` refuse any URL but the stub. Notify,
lifecycle-now and Groq are pointed at the stub or blanked.

```bash
ssh VM
/opt/band-advance/tools/staging/setup.sh        # build it (idempotent: tears down first)
/opt/band-advance/tools/staging/run_tests.py    # the suite
/opt/band-advance/tools/staging/teardown.sh     # remove everything
```

Never run any tool from `~/advtest/code` without `set -a; . ~/advtest/advtest.env; set +a`
— the env file is what points it at the clone.
