# Gear Tickets

QR-code problem reporting for the 3CDC crew. Somebody scans a sticker, describes
what's broken, adds photos, and it lands on the Monday Projects board with Brian
alerted in Slack.

Built 2026-08-02. Runs entirely on free tiers.

---

## How it moves

```
QR sticker  →  n8n form (crew picks venue)  →  photos staged to disk
                                                     ↓
                                        ticket id  →  Postgres write
                                                     ↓
                                    photos moved into /photos/<TICKET>/
                                                     ↓
                                              AI triage (dedupe, severity)
                                                     ↓
                                Monday item  +  post to #gear-repair
                                                     ↓
                                   7am daily: reconcile against the board
```

The Postgres write happens **before** any AI touches the ticket. If the model is
down, the API is rate-limited, or Monday is having a day, the ticket still
exists and still alerts — it just arrives untriaged.

## Where things live

| Piece | Where |
|---|---|
| Form | n8n Form Trigger on the VM, `/form/gear-ticket` |
| Ledger of record | `tickets` database in the n8n stack's Postgres |
| Photo originals | `/opt/gear-tickets/photos/<TICKET>/N.jpg` on the VM |
| Photos served at | `https://tickets.tinydoorstudios.com/p/<TICKET>/N.jpg` |
| Working queue | Monday board `18405931866`, group `group_mm5vwbn1`, view `🎫 Tickets` (273197456) |
| Log / archive | Google Sheet `Gear Tickets Log` — `1NbUaOk_G190KHEoY2lwdcgo6WqvcZ-W-9RdCuqgEt_A` (owner tinydoorstudios@gmail.com) |
| Alerts | Slack `#gear-repair` (`C0BMLG10FAQ`) |

`tickets.tinydoorstudios.com` is a fourth vhost inside the existing `landing`
nginx container, which runs host-network on :8088 alongside tinydoorstudios.com,
kb., and n8n. It splits the hostname — `/form` and `/webhook` proxy to n8n on
:5678, `/p/` serves photos from `/gear-photos` (bind-mounted read-only from
`/opt/gear-tickets/photos`). Deliberately no `auth_basic`: the n8n vhost is
password-protected, the crew scanning a QR has no login, so the form gets its
own hostname exposing only the form paths.

## Live IDs on the VM

| Thing | Value |
|---|---|
| Intake workflow | `GearTixIntake001` — published |
| Nightly workflow | `GearTixNightly01` — published, runs 7am; **digest node disabled** |
| Sheet sync workflow | `GearTixSheetSync` — published, every 15 min + a manual **Run Now** trigger |
| Postgres credential | `GearTixPostgres1` "Tickets Postgres" |
| LLM credential | `GearTixTriageLLM` "Triage LLM (Groq) - value = Bearer gsk_..." |
| Monday credential | `GearTixMondayAPI` "Monday API - raw token, NO Bearer" |
| Slack credential | `3xjCpEYkIsnToSko` "Slack account" (OAuth2) — posts to `#gear-repair` |
| Form path | `/form/gear-ticket` — must match `webhookId`, not the `path` param |

Both Header Auth credentials carry their format in the credential *name*, which
is not decoration. The two panels are visually identical apart from the title,
and during setup the Monday token got pasted over a working Groq key — costing a
round of confused debugging, since Groq then returned `Invalid API Key` while
Monday still returned `Not authenticated`. Groq wants `Bearer gsk_...`; Monday
wants the raw token with no prefix. If you ever need to tell which credential
was actually edited, compare `updatedAt` against `createdAt` in
`credentials_entity` — the masked field length tells you nothing.

## Triage model

Groq, `llama-3.3-70b-versatile`, at `https://api.groq.com/openai/v1/chat/completions`.
Chosen because the `AI Triage` node already speaks native OpenAI chat-completions
and Groq's endpoint is that shape exactly — same JSON body, and `Apply Triage`
already parses `choices[0].message.content`. Free plan is 30 req/min and 1,000
req/day on that model with no card, which is roughly a hundred times this
system's expected volume.

Both the URL and the model are env vars (`TRIAGE_API_URL`, `TRIAGE_MODEL`), so
Groq retiring a model name is a one-line change plus a restart. `AI Triage` also
has `neverError: true`, so a dead provider yields an untriaged ticket, never a
lost one — the Postgres write is already done by then.

The triage request deliberately does **not** send `submitter_name`,
`submitter_email` or `submitter_phone`. The model doesn't need crew contact
details to classify a ticket, and this keeps them off a third-party free tier.
The dedupe list it also receives never contained contact fields.

**n8n gotchas learned the hard way here.** `import:workflow` fails outright
unless the JSON has a top-level `id`. It also silently drops active state, so
every re-import needs a re-publish *and* an `n8n restart` before the webhook
registers — and the command is `publish:workflow --id=<id>`; `update:workflow
--active=true` is gone and just prints a pointer to the new one. The Form
Trigger serves at `/form/<webhookId>` — the node's `path` parameter is not what
ends up in the URL.

**Query Parameters on the Postgres node split the *resolved* value on commas.**
A field written as `{{ $json.a }},{{ $json.b }}` evaluates each expression and
then runs the result through a comma-splitter, so one comma inside a description
shifts every parameter after it into the wrong column — silently, no error. A
test ticket landed with the venue in `submitter_name` and half the description
in `raw_venue`. The fix is to make the whole field a single expression that
returns an array — `{{ [ $json.a, $json.b ] }}` — which takes a different code
path and is never split. Every Postgres node here uses the array form; keep it
that way.

**Binary data is only reachable from the node it arrives at.** `Stage Photos`
sits directly after the form trigger for exactly this reason.
`helpers.getBinaryDataBuffer` reads binary off the *current* node's input, and
anything downstream of a Postgres node has none — binary doesn't survive. The
two obvious escapes are both blocked in the Code sandbox: `helpers.getBinaryStream`
and `helpers.getBinaryPath` each throw "not supported in the Code Node". Binary
also isn't inline base64 to fall back on, since this instance stores it as
`filesystem-v2`. Hence staging by execution id first, then moving into the
ticket folder once the ID exists.

**`$json` after a Postgres node is only what that query RETURNED.** `Store
Triage` is an `UPDATE ... RETURNING ticket_id`, so downstream `$json` holds
exactly one field. `Create Monday Item` was reading `$json.title`, `$json.venue`
and the rest off it — all undefined — and Monday rejected the mutation with
`Variable "$n" of required type "String!" was not provided`. Anything needing
the full ticket must reach back explicitly: `$('Apply Triage').first().json`.

**A node that returns zero items ends the branch, silently, as a "success".**
`Fetch Open Tickets (for dedupe)` excludes the current ticket, so on an empty
ledger it matched nothing and the execution simply stopped there — no triage, no
Monday item, no Slack, and a green tick in the executions list. This is a
first-ticket-only bug and it stayed hidden the whole build because there was
always older test data to match against; clearing the test data is what exposed
it. `alwaysOutputData: true` on that node emits one empty item so the chain
continues, and `AI Triage` filters the dedupe list to entries that actually have
a `ticket_id` so the empty item never reaches the model. Verified against a
genuinely empty database.

**`$env` in an expression needs `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`.** Without
it `AI Triage` fails with "access to env vars denied" and never reaches the
model — and because the node is `neverError`, that failure looks like a
successful-but-untriaged ticket rather than an error.

**The n8n service passes env through an explicit `environment:` list**, so a var
added to `/opt/n8n/.env` alone never reaches the container. Every new var goes
in both files. Same trap in the other direction for the photo dir: `Save Photos
to Disk` writes to `/opt/gear-tickets/photos` from *inside* the container, so
that host path must be bind-mounted into the n8n service or the files land in
the container's own filesystem — invisible to the nginx that serves `/p/`, and
discarded on the next `compose up`. `NODE_FUNCTION_ALLOW_BUILTIN=fs,path` is
what lets that Code node call `require('fs')` in the first place.

Monday is the interface. Postgres is the truth. That split is what makes the
nightly reconcile possible — if the board drifts, there's something
authoritative to correct it against.

## Monday column IDs

Hard-coded in both workflows. If a column is renamed the ID stays the same; if a
column is deleted and remade, update these.

| Column | ID | Type |
|---|---|---|
| Venue | `dropdown_mm5v46m2` | dropdown |
| Category | `color_mm5v67cy` | status |
| Severity | `color_mm5vz074` | status |
| Submitted By | `text_mm5vavpx` | text |
| Contact | `text_mm5vhr68` | text |
| Submitted | `date_mm5vyxxq` | date |
| Ticket ID | `text_mm5vaz0` | text |
| Photo Links | `long_text_mm5v24v2` | long text |
| Status (reused) | `project_status` | status |
| Files (reused) | `file_mm1w17pd` | file |

## Install

1. Tailscale up on the Mac.
2. `deploy/deploy-tickets.command` — schema, photo dir, nginx route.
3. Wire credentials and import both workflows in the n8n UI (the script prints
   the checklist when it finishes).
4. Cloudflare route for `tickets.tinydoorstudios.com`. **Routing is
   remote-managed** — use the API script in `audio/Live Sound KB/_tools/`, not
   `/etc/cloudflared/config.yml`, which is ignored.
5. `qr/make_qr.py` → one page, print as many as you need, laminate, stick.
   Needs `qrcode`, `pillow`, `reportlab` — `.venv/` in this folder has them.

## What the agent may and may not do

Decides: title, category, severity, gear guess, duplicate detection, digest
wording. All cheap to be wrong about and trivially reversible.

Never: closes a ticket, deletes anything, messages a coworker, touches any
Monday board but this one, escalates to anyone but Brian. If it thinks something
is urgent it tells Brian louder — it doesn't call people.

## Severity, in crew language

| Label | Means |
|---|---|
| Show-stopper | Breaks a show tonight or tomorrow |
| Fix before next use | Works now, don't roll it out again like this |
| Annoying but working | Live with it, fix when there's a gap |
| Note for the record | Nothing to do, just logging it |

The nightly job chases show-stoppers after a day, fix-before-next-use after a
week, everything else after a month.

## Cost

Free. n8n community, Postgres, Cloudflare tunnel, nginx, the VM, Slack, and
Monday's free tier — which allows 10,000 items on this board, so the item cap
that the pricing blogs warn about isn't a real constraint here.

The only paid step is when a second person needs to triage in Monday: free caps
at 2 seats, and Basic is about $9/seat/month. That's the upgrade trigger to
watch for, and it means the thing worked.

## Known soft spots

- Free LLM tiers rotate. Wire a paid fallback before this becomes load-bearing.
- HEIC uploads from iPhones may need converting before Monday will preview them.
- There is no gate on the form at all. The old QR URLs carried `k=fsq26` and
  `make_qr.py` claimed n8n checked it; nothing ever did. Dropped with the
  single-code rewrite rather than left as decoration. If the form starts
  attracting junk, add a real check.

## State — 2026-08-02

Live and verified: Cloudflare route + DNS (`tickets` CNAME → the n8n tunnel,
proxied; ingress rule inserted ahead of the 404 catch-all, other seven hostnames
re-checked 200 after), the public form at
`https://tickets.tinydoorstudios.com/form/gear-ticket` answering 200, the three
ticket tables, the photo dir bind-mounted and confirmed writable from inside the
n8n container, the Postgres credential, and `TRIAGE_API_URL` / `TRIAGE_MODEL` /
`NODE_FUNCTION_ALLOW_BUILTIN` present in the container's environment. Outbound
HTTPS from the container to `api.groq.com` answers 401 without a key, which is
the proof that the network path works. Venue prefill was tested against all five
real QR URLs — every one comes back with the right `<option … selected>`,
including `Shop / Storage` with its slash. Intake is published; exactly one
placeholder is left in it.

**End to end, all fifteen nodes green, and the degraded path is tested too.**
A real submission through the public form produces: a ticket row with every
field in the right column, the photo staged and moved to
`/photos/<TICKET>/1.jpg` and served over HTTPS, dedupe against open tickets,
Groq triage returning real category, severity and notes, a Monday item on board
`18405931866` with its ID written back to Postgres, the full detail posted as an
update on that item, and a Slack DM.

Monday failures are soft. Both Monday nodes run `onError: continueRegularOutput`,
`Alert Brian` optional-chains the item so the title simply doesn't hyperlink when
there's no item, and the alert gains a line telling Brian it's in Postgres only
and needs adding to the board by hand. `Link + Log Event` leaves `monday_item_id`
and `monday_synced_at` alone rather than stamping nulls. Verified by pointing the
Monday nodes at a deliberately broken URL: the ticket saved, triaged, kept its
photo, and the DM still arrived — then the real URL was restored and a clean run
confirmed.

Slack posts to **`#gear-repair`** (`C0BMLG10FAQ`) — both the real-time ticket
post and the 7am digest. The post leads with the severity as its header
(`:rotating_light: SHOW-STOPPER`), then the title hyperlinked to the Monday item,
then the model's one-line summary, then a single facts line of ticket / venue /
category / gear / reporter, then photo links. Both workflows are published.

The Slack credential is a **user** token, so posts appear as Brian rather than as
a bot. Switching to a bot credential is a credential swap on that node, nothing
more.

Everything is clean and ready for real traffic: zero ticket rows, zero photos,
zero events, no files under `/opt/gear-tickets`, `ticket_seq` reset so the first
real ticket is TDS-0001, and the 🎫 Gear Tickets group on the Monday board empty
— the two test items and the hand-written `SAMPLE — FSQ stage-left wedge` demo
item are all deleted. Nothing on that board outside the To-Do group was touched.


## The Google Sheet log

`Gear Tickets Log` in Brian's Drive (`tinydoorstudios@gmail.com`) is the flat,
sortable archive — Monday is where work happens, this is where it's all written
down. One row per ticket, sixteen columns: Ticket ID, Submitted, Venue, Gear,
Category, Severity, Summary, Already Tried, Reported By, Contact, Photos, Monday
Item, Status, Completed, Days Open, Last Synced.

`GearTixSheetSync` runs every 15 minutes: pulls the Monday board, pulls the full
ledger from Postgres, and writes with the Sheets node's `appendOrUpdate` matching
on Ticket ID. That one operation covers both cases — a ticket that isn't in the
sheet gets appended, a ticket that is gets its row updated in place. Nothing is
diffed by hand and nothing is duplicated, so the sync is safe to re-run and will
backfill anything it missed.

**Monday is the authority on "finished."** Brian works the board, not the
database, so `Status` and `Completed` come from the board's status column. The
completion date prefers Postgres `resolved_at` (exact, stamped by the nightly
reconcile) and falls back to the Monday item's `updated_at` (approximate) in the
window before the nightly has run. `Days Open` counts to `resolved_at` once
closed, and to now while open.

**Live.** It uses the existing `Google Sheets account` credential, which is
healthy and authorized as **`rivetheadsound@gmail.com`** — not the account the
credential's name or its neighbours suggest. Brian owns the sheet as
`tinydoorstudios@gmail.com` and shared it with that account as Editor;
ownership never moved. Do **not** re-point that credential to a different Google
account: Show Reports is live and writes seven nodes' worth of logging into
`3CDC Tech Production Report (Responses)`, which `tinydoorstudios@gmail.com`
cannot see at all.

To find out which Google account any n8n Google credential is really using, run
an HTTP Request node against `https://www.googleapis.com/drive/v3/about?fields=user`
with `predefinedCredentialType` set to that credential. The `oauth2/v2/userinfo`
endpoint returns `Authorization failed` because the granted scopes don't include
it — that failure means nothing about the credential's health.

Two traps in the Sheets node itself. The **Sheet Name** resource locator in `id`
mode wants the bare numeric gid (`2051872321`), not the `gid=` form copied out of
the browser URL — the `gid=` version fails with "Sheet with ID ... not found".
And a CSV uploaded to Drive does not become `gid=0`; check the real tab id.

The sync **never deletes rows** — append or update only. That's right for an
audit log, but it means a ticket removed from Postgres keeps its sheet row
forever. Delete those by hand.

## The "what have you already tried" field

Added at Brian's request. It sits on the form between "What gear?" and "How bad
is it?", optional, with a placeholder that makes "nothing yet" an acceptable
answer.

It threads all the way through: stored in `tickets.troubleshooting`, shown on the
Monday item's update as **Already tried**, on the Slack post as a 🔍 line, and in
the sheet's own column. The triage prompt is explicitly told not to repeat steps
the submitter already listed and to pick up where they left off — so a report
saying "swapped the battery, moved the antenna, rescanned" gets a note about
checking the antenna cable and the receiver, not a suggestion to swap the battery.


## Why there's no daily digest

The `Morning Digest` node in the nightly caretaker is disabled, at Brian's call.
The workflow still runs at 7am and still reconciles — that half is what closes
tickets marked Done on the board, stamps `resolved_at`, and follows severity
changes, and the sheet's Completed date depends on it.

The digest became noise once tickets started posting to `#gear-repair` the moment
they arrive and the Google Sheet started refreshing every 15 minutes. A daily
recap of things you already saw is a message you learn to skip, which is worse
than no message — it trains you to ignore the channel the show-stoppers arrive
in.

Re-enable by clearing `disabled` on that node if the queue ever grows past what
the channel alone keeps visible.
