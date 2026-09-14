# DigiBot — Q225 help desk in Slack

Slack bot the crew @mentions (or DMs, or just talks to in #digico-help) with Quantum 225 questions.
Answers come from the DiGiCo wiki (digico.tinydoorstudios.com — manual mirror, how-to pages, venue
pages) plus ten Live Sound KB pages, with a link to the page and the figure when there is one.
Runs on the n8n VM. Plan and reasoning: `PLAN.md`.

## Pieces

| Piece | Where | What |
|---|---|---|
| `service/` | `/opt/digibot` on the n8n VM, container `digibot-api` (:8098) | FastAPI brain: indexer, hybrid search, Groq agent loop, teachings, gaps. Never touches Slack. |
| `digibot-db` | same compose stack, `pgvector/pgvector:pg16` | pages, chunks (bge-small 384-d vectors + tsvector), teachings, gaps, qa_log |
| n8n `DigiBot — Slack` | n8n, webhook `/webhook/digibot-slack-events/webhook` | Slack Events → route → thread history → `/answer` → post reply in thread. Reactions → `/reaction`. |
| n8n `DigiBot — Nightly Reindex` | 03:40 daily | `POST /index` then `POST /inbox/rebuild` |
| n8n `DigiBot — Weekly Gaps Digest` | Monday 08:00 | `GET /gaps/digest` → DM to Brian |
| n8n credential `DigiBotSlack` | type `slackApi` | the bot token + signing secret — the only place the Slack token lives |

Model: Groq free tier, `openai/gpt-oss-120b` first, then `qwen/qwen3.8-27b`, then `openai/gpt-oss-20b`
(Groq retires models without notice; `DIGIBOT_MODELS` in `.env` is the list). Embeddings are local
(fastembed / bge-small-en-v1.5 on CPU) — no key, no outside call.

## Deploy / update

```bash
Code/DigicoBot/deploy/install.sh          # ship service + rebuild image + up (keeps .env)
Code/DigicoBot/deploy/install.sh --n8n    # also re-import the three workflows + placeholder credential, restart n8n
```

Secrets are filled into `/opt/digibot/.env` only when empty, server-to-server: the DiGiCo wiki key
from CT 101, the KB key from `kb-secrets.sh`, the Groq key from the n8n Triage LLM credential.
Edit anything else in `.env` on the VM, then `cd /opt/digibot && sudo docker compose up -d`.

Regenerate workflow JSON after editing `n8n/gen_workflows.py`: `python3 n8n/gen_workflows.py`.

## Slack app (one-time, Brian)

1. api.slack.com/apps → Create New App → **From a manifest** → 3CDC workspace → paste `slack-manifest.json`.
2. Install to workspace. Copy **Bot User OAuth Token** (`xoxb-…`) and, from Basic Information, the **Signing Secret**.
3. n8n → Credentials → *DigiBot Slack (bot token + signing secret)* → paste both → Save.
4. Slack app → Event Subscriptions → the Request URL should already read
   `https://n8n.tinydoorstudios.com/webhook/digibot-slack-events/webhook`; press Retry / Verify. It only
   verifies once step 3 is saved (n8n checks the signature).
5. Put the bot's user id (`U…`, from the app's install page or `users.list`) and the #digico-help channel id
   into `/opt/digibot/.env` as `DIGIBOT_BOT_USER_ID` / `DIGIBOT_HOME_CHANNEL`, then `sudo docker compose up -d`.
6. Invite `@DigiBot` to #digico-help.

## Using it

- `@DigiBot how do I ripple patch a run of inputs` — anywhere it's invited. DMs work. In #digico-help no @ needed.
- Follow-ups go in the thread; it reads the thread.
- **Teach it (Brian only):** reply in a thread with `@DigiBot teach: <what's true>`, or put 📌 on any message.
  Searchable immediately at the top tier; collected nightly on
  digico.tinydoorstudios.com/venue/teachings-inbox until folded into a real page.
- 👍 / 👎 on an answer is recorded against it (`qa_log.feedback`).
- Weekly DM lists what it couldn't answer.

## Free-tier limits (Groq)

Per-minute token caps are tight: a question that needs a tool round is ~8–9K tokens, which is about
one question a minute on the 120b model before it falls through to the smaller ones, then waits 20 s
and retries the chain. If the crew start asking faster than that, the answer is Groq's pay-as-you-go
tier (pennies) or a Claude key — nothing else changes.

## Eval

```bash
python3 eval/run_eval.py             # retrieval only: expected page in top 6?  (40 questions)
python3 eval/run_eval.py --answers   # also runs the model — 40 Groq calls, eats the daily quota
```

## Handy

```bash
curl -s localhost:8098/stats
curl -s 'localhost:8098/search?q=ripple+patch'
curl -s -X POST localhost:8098/index
sudo docker exec digibot-db psql -U digibot -d digibot -c "select question, model, latency_ms, feedback from qa_log order by id desc limit 20"
sudo docker exec digibot-db psql -U digibot -d digibot -c "update teachings set folded=true where id=N"
```

## Gotchas met during the build

- The api container OOM'd at 700 MB while embedding with batch 32; batch 4 + `mem_limit: 1100m` fixed it.
- Wiki paths for the I/O pages are `hardware/…`, not `io/…` (build_site.py maps them).
- Groq dropped `llama-3.3-70b-versatile` and `llama-3.1-8b-instant` (404). **Gear Tickets' `TRIAGE_MODEL` in
  `/opt/n8n/.env` still names the 70b — its triage is failing until that is changed.**
- n8n mounts a freshly imported webhook only after a restart; `install.sh --n8n` restarts it.
