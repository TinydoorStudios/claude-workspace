"""Translate a Spanish-submitted band advance form's free-text answers to
English, in place, before anything downstream (disk JSON, Postgres, the
notify email, the filed advance/daysheet doc) ever sees them.

Brian, 2026-09-12: the Spanish form (i18n.py) lets a band answer in
Spanish, but everything Brian actually reads from a submission — the
notify email, the filed advance doc, the daysheet — needs English. Only
the free-text TEXTAREA fields need this; every select/radio/number field's
stored value is already English on both language variants of the form (see
i18n.py's header note — only the on-screen label changes), and
band_name/contact_name are proper nouns, left untouched.

Uses Groq's OpenAI-compatible chat completions API (Brian, 2026-09-12:
free tier, no billing to set up — swapped in from an initial Anthropic-API
draft for exactly that reason). Same `response_format: json_object`
pattern already proven in Code/GearTickets' own Groq triage call — see
that project's n8n/01_intake.json for the sibling usage. Needs
GROQ_API_KEY in the environment (advance.env on the VM); see
advance.env.example. This is a SEPARATE key from GearTickets' own — that
one lives inside n8n's own encrypted credential store, not a plain env
var this Flask app could read, so it isn't reusable here.

Model is `openai/gpt-oss-120b`, not GearTickets' `llama-3.3-70b-versatile`
— that one no longer exists on Groq as of 2026-09-12 (confirmed via
GET /v1/models against the live key; Groq retires model names without
much notice, per GearTickets' own README). gpt-oss-120b is a reasoning
model: its response puts the actual answer in `message.content` and its
scratchpad in a separate `message.reasoning` field we never read, so no
extra parsing is needed — but if this model is ever retired too, checking
`/v1/models` with the live key is the fastest way to find its replacement,
faster than guessing from Groq's docs.

Fails soft, always: if the key isn't set, the call times out, or the
response doesn't parse as expected, the ORIGINAL Spanish text is left in
the record untouched rather than blocking or corrupting the submission —
same "the live form can never break" rule the DB layer follows (app.py's
own module docstring). A field the model returns blank or omits is
likewise left as its original Spanish rather than dropped.

Shells out to `curl` instead of using `urllib`/`requests` (Brian,
2026-09-12) — confirmed on the actual VM that Groq's Cloudflare front door
returns a bot-fingerprint block (error code 1010, HTTP 403) against
Python's own TLS/HTTP client stack specifically, while `curl` from the
same host to the same endpoint with the same key succeeds every time.
Not a key or model problem — a client-fingerprint one. If this ever
needs revisiting, verify with a raw `curl` call against the VM before
assuming the key/model is at fault; `urllib` will look like the request
failed when it's actually being told apart from curl and blocked.
"""
import json
import os
import subprocess

MODEL = os.environ.get("ADVANCE_TRANSLATE_MODEL", "openai/gpt-oss-120b")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT = float(os.environ.get("ADVANCE_TRANSLATE_TIMEOUT", "15"))

# The only fields a band can write free text into, on either language
# variant of the form. Everything else (venue, stage_type, merch, etc.) is
# a fixed select/radio whose stored value is already English by design.
FREE_TEXT_FIELDS = [
    "changed_notes", "stage_plot_desc", "backline", "scenic", "lighting", "additional",
]

SYSTEM_PROMPT = """\
You translate short Spanish answers from a touring band's show-advance \
form into natural, accurate English, for a live-event production team \
(3CDC, a Cincinnati arts/events organization) who need to read them.

Rules:
- Translate the MEANING naturally — don't produce a stiff, literal translation.
- Keep the original register: a casual answer stays casual, a terse one stays terse.
- Leave live-sound / audio-production jargon as the band wrote it if it's \
already an English loanword or abbreviation in Spanish usage — FOH, \
backline, IEM, LD, soundcheck, and similar terms — translate ordinary \
words around it normally (e.g. "monitores" -> "monitors").
- Keep proper nouns unchanged: people's names, band names, brand/product names.
- If a value is empty, whitespace, already in English, or just punctuation, \
return it completely unchanged.
- Reply with JSON only, no prose. A single object with EXACTLY the same \
keys you were given, each value replaced by its English translation."""


_STATUS_MARKER = "\n__ES_TRANSLATE_HTTP_STATUS__:"


def _post_json(url, headers, body_bytes, timeout):
    """POST via curl (see module docstring for why not urllib) — returns the
    response body (str) on a 2xx, raises RuntimeError otherwise (curl
    process failure, or an HTTP error status with the response body
    included in the message for logging)."""
    import tempfile
    # Headers (including the API key) go through a private temp file, never
    # the command line, so the key isn't visible in the process list.
    with tempfile.NamedTemporaryFile("w", prefix="es-hdr-", delete=False) as hf:
        os.chmod(hf.name, 0o600)
        for k, v in headers.items():
            hf.write(f"{k}: {v}\n")
        hdr_path = hf.name
    cmd = ["curl", "-sS", "--max-time", str(int(timeout)), "-X", "POST", url,
           "-w", _STATUS_MARKER + "%{http_code}", "-H", f"@{hdr_path}",
           "--data-binary", "@-"]
    try:
        proc = subprocess.run(cmd, input=body_bytes, capture_output=True, timeout=timeout + 10)
    finally:
        try:
            os.unlink(hdr_path)
        except OSError:
            pass
    if proc.returncode != 0:
        raise RuntimeError(f"curl exit {proc.returncode}: "
                            f"{proc.stderr.decode('utf-8', 'replace')[:300]}")
    out = proc.stdout.decode("utf-8", "replace")
    body, _, status = out.rpartition(_STATUS_MARKER)
    status = int(status.strip())
    if status >= 400:
        raise RuntimeError(f"HTTP {status}: {body[:300]}")
    return body


def _strip_code_fence(text):
    text = text.strip()
    if not text.startswith("```"):
        return text
    text = text.strip("`")
    if "\n" in text:
        first, rest = text.split("\n", 1)
        if first.strip().lower() in ("", "json"):
            return rest.strip()
    return text.strip()


def translate_es_fields(rec, log=None):
    """Mutates `rec` in place: every non-empty FREE_TEXT_FIELDS value is
    replaced by its English translation; the original Spanish is kept
    alongside under `<field>_es_original` so nothing is lost. Returns rec
    either way. `log(context, err)` — matching app.py's _log_db_error
    signature — is called (never raised) on any failure; the original
    Spanish values stay in place untouched in that case."""
    # audit 2026-09-16 security #7: form_lang=es is client-controlled, so
    # every POST claiming it used to trigger a real Groq call (up to
    # TIMEOUT seconds, in the request thread) regardless of whether the
    # text needed translating at all — plain ASCII/English text, or
    # nothing but a number, still made the round trip. Only bother when a
    # field actually contains a non-ASCII character, and cap what's sent.
    to_translate = {k: rec[k][:6000] for k in FREE_TEXT_FIELDS
                    if (rec.get(k) or "").strip() and not rec[k].isascii()}
    if not to_translate:
        return rec

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        if log:
            log("es_translate", RuntimeError(
                "GROQ_API_KEY not set — submission kept in Spanish"))
        return rec

    body = json.dumps({
        "model": MODEL,
        "temperature": 0.1,
        "max_tokens": 1536,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(to_translate, ensure_ascii=False)},
        ],
    }).encode("utf-8")
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    try:
        raw = _post_json(API_URL, headers, body, TIMEOUT)
        resp_json = json.loads(raw)
        text = resp_json["choices"][0]["message"]["content"]
        translated = json.loads(_strip_code_fence(text))
    except (RuntimeError, OSError, ValueError, KeyError, IndexError,
            subprocess.TimeoutExpired) as e:
        if log:
            log("es_translate", e)
        return rec

    for key, original in to_translate.items():
        new_val = translated.get(key) if isinstance(translated, dict) else None
        if isinstance(new_val, str) and new_val.strip():
            rec[f"{key}_es_original"] = original
            rec[key] = new_val
        elif log:
            log("es_translate", RuntimeError(f"no usable translation for {key!r} — kept Spanish"))
    return rec
