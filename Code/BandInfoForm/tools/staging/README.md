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

Two rules keep the live and staging environments apart (2026-09-21 sweep):

Start `setup.sh`, `run_tests.py` and `run_tests_extra.py` from a fresh shell, e.g.
`ssh VM "/opt/band-advance/tools/staging/setup.sh && ~/advtest/code/tools/staging/run_tests.py"`,
and never from a shell that sourced `/opt/band-advance/advance.env`. Staging inherits
whatever that shell exported; `advtest.env` blanks the live-only keys it knows about
(Dropbox API creds, the Slack webhook, Groq), but anything it doesn't name passes through.

Run any manual tool against the clone inside a subshell, so the staging env can't
linger into a later live run:

```bash
( set -a; . ~/advtest/advtest.env; set +a; cd ~/advtest/code/tools && /opt/band-advance/venv/bin/python <tool>.py ... )
```

The reverse hazard is real: a later `. advance.env` in the same shell swaps in the
live DB URL but keeps `ADVANCE_STAGING=1` and `ADVANCE_DROPBOX_ROOT=~/advtest/Dropbox`,
so a live tool run would read the live database and file into the staging folders.
