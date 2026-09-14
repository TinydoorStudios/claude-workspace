# Runs ON the VM inside the n8n container's stdout pipe: prints the Groq key (no "Bearer ") from the
# decrypted export of the Triage LLM header credential. Nothing else is printed.
import json, re, sys
raw = sys.stdin.read(); i = raw.find('[')
d = json.loads(raw[i:]) if i >= 0 else []
v = d[0].get('data', {}).get('value', '') if d else ''
print(re.sub(r'^Bearer\s+', '', v).strip(), end='')
