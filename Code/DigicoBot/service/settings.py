"""All configuration comes from the environment (/opt/digibot/.env via docker compose)."""
import os


def _list(v: str) -> list[str]:
    return [x.strip() for x in v.split(',') if x.strip()]


class S:
    db_dsn = os.environ.get('DIGIBOT_DB_DSN', 'postgresql://digibot:digibot@db:5432/digibot')

    digico_wiki_url = os.environ.get('DIGICO_WIKI_URL', 'http://192.168.200.126:3002')
    digico_wiki_key = os.environ.get('DIGICO_WIKI_KEY', '')
    digico_public_url = os.environ.get('DIGICO_PUBLIC_URL', 'https://digico.tinydoorstudios.com')
    exclude_paths = set(_list(os.environ.get('DIGICO_EXCLUDE_PATHS', 'venue/teachings-inbox')))
    inbox_path = os.environ.get('DIGIBOT_INBOX_PATH', 'venue/teachings-inbox')

    kb_wiki_url = os.environ.get('KB_WIKI_URL', 'http://192.168.200.126:3000')
    kb_wiki_key = os.environ.get('KB_WIKI_KEY', '')
    kb_public_url = os.environ.get('KB_PUBLIC_URL', 'https://kb.tinydoorstudios.com')
    kb_paths = _list(os.environ.get('KB_PATHS', ''))

    groq_key = os.environ.get('GROQ_API_KEY', '')
    groq_url = os.environ.get('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    models = _list(os.environ.get('DIGIBOT_MODELS', 'openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b'))
    max_tool_rounds = int(os.environ.get('DIGIBOT_MAX_TOOL_ROUNDS', '3'))
    top_k = int(os.environ.get('DIGIBOT_TOP_K', '5'))
    chunk_chars_in_prompt = int(os.environ.get('DIGIBOT_CHUNK_CHARS', '1200'))
    retry_wait_s = int(os.environ.get('DIGIBOT_RETRY_WAIT_S', '20'))

    teachers = set(_list(os.environ.get('DIGIBOT_TEACHERS', 'UHSLD08SV')))
    brian_user = os.environ.get('DIGIBOT_OWNER', 'UHSLD08SV')
    home_channel = os.environ.get('DIGIBOT_HOME_CHANNEL', '')
    bot_user_id = os.environ.get('DIGIBOT_BOT_USER_ID', '')

    embed_model = os.environ.get('DIGIBOT_EMBED_MODEL', 'BAAI/bge-small-en-v1.5')
