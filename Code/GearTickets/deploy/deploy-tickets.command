#!/bin/bash
# Gear Tickets — VM install / re-install
#
# This is the record of what was actually done on 2026-08-02, made re-runnable.
# Run from Brian's Mac with Tailscale UP. Everything is idempotent.
#
# What it does NOT do: create the Monday and LLM credentials (they need tokens
# only Brian has) or add the Cloudflare route. Both are printed at the end.

set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$REPO/deploy/deploy-$(date +%Y%m%d-%H%M%S).log"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY -o ConnectTimeout=15"
N8N="sudo docker compose -f /opt/n8n/docker-compose.yml"

exec > >(tee "$LOG") 2>&1
echo "=== Gear Tickets deploy — $(date) ==="
echo

# --- 0. reachable? ---------------------------------------------------------
echo "--- path to the VM ---"
if ! $SSH "$VM" 'echo reachable' 2>&1 | grep -q reachable; then
    echo "CANNOT REACH THE VM. Is Tailscale running? Connect it and re-run."
    exit 1
fi
echo "ok"; echo

# --- 1. Postgres schema ----------------------------------------------------
# The tickets DB lives beside n8n's own DB in the same Postgres container.
echo "--- ticket schema ---"
$SSH "$VM" "$N8N exec -T postgres psql -U n8n -d n8n -v ON_ERROR_STOP=0" \
    < "$REPO/sql/01_schema.sql" 2>&1 | grep -vE "^NOTICE|already exists" | tail -8
echo

# --- 2. photo storage ------------------------------------------------------
# uid/gid 101 is the nginx user inside nginx:alpine, which serves these read-only.
echo "--- photo directory ---"
$SSH "$VM" '
  sudo mkdir -p /opt/gear-tickets/photos
  sudo chown -R 101:101 /opt/gear-tickets/photos
  sudo chmod -R 755 /opt/gear-tickets
  df -h /opt | tail -1
'
echo

# --- 3. nginx vhost --------------------------------------------------------
# The `landing` container runs nginx on host-network :8088 and name-vhosts
# tinydoorstudios.com, kb., and n8n. This adds tickets. as a fourth, with no
# auth_basic (the crew has no login) and only the form paths exposed.
echo "--- tickets vhost ---"
cat "$REPO/deploy/nginx-tickets.conf" | $SSH "$VM" '
  set -e
  cat > /tmp/tickets-vhost.conf
  TS=$(date +%Y%m%d%H%M%S)
  sudo cp /opt/landing/nginx.conf /opt/landing/nginx.conf.bak-$TS
  sudo cp /opt/landing/docker-compose.yml /opt/landing/docker-compose.yml.bak-$TS

  if sudo grep -q "tickets.tinydoorstudios.com" /opt/landing/nginx.conf; then
      echo "  vhost already present"
  else
      printf "\n" | sudo tee -a /opt/landing/nginx.conf > /dev/null
      sudo tee -a /opt/landing/nginx.conf < /tmp/tickets-vhost.conf > /dev/null
      echo "  vhost appended"
  fi

  if sudo grep -q "gear-photos" /opt/landing/docker-compose.yml; then
      echo "  photo mount already present"
  else
      sudo sed -i "s|      - /opt/kb-assets:/kb-assets:ro|      - /opt/kb-assets:/kb-assets:ro\n      - /opt/gear-tickets/photos:/gear-photos:ro|" /opt/landing/docker-compose.yml
      echo "  photo mount added"
  fi

  # Test in a throwaway container before touching the live one.
  if sudo docker run --rm \
       -v /opt/landing/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
       -v /opt/landing/html:/usr/share/nginx/html:ro \
       -v /opt/landing/.htpasswd:/etc/nginx/.htpasswd:ro \
       -v /opt/kb-assets:/kb-assets:ro \
       -v /opt/gear-tickets/photos:/gear-photos:ro \
       nginx:alpine nginx -t 2>&1 | grep -q successful; then
      cd /opt/landing && sudo docker compose up -d > /dev/null 2>&1
      echo "  config ok, landing container recreated"
  else
      echo "  CONFIG TEST FAILED — restoring backups, nothing changed"
      sudo cp /opt/landing/nginx.conf.bak-$TS /opt/landing/nginx.conf
      sudo cp /opt/landing/docker-compose.yml.bak-$TS /opt/landing/docker-compose.yml
      exit 1
  fi
'
echo

# --- 4. n8n Postgres credential -------------------------------------------
# Built on the VM so the DB password never crosses the wire or hits a log.
echo "--- n8n credential ---"
$SSH "$VM" '
  if sudo docker compose -f /opt/n8n/docker-compose.yml exec -T postgres \
       psql -U n8n -d n8n -tAc "SELECT 1 FROM credentials_entity WHERE id='"'"'GearTixPostgres1'"'"';" | grep -q 1; then
      echo "  Tickets Postgres credential already exists"
  else
      sudo python3 -c "
import json
env = {}
for line in open(\"/opt/n8n/.env\"):
    line = line.strip()
    if line and not line.startswith(\"#\") and \"=\" in line:
        k, v = line.split(\"=\", 1); env[k] = v.strip().strip(chr(34)).strip(chr(39))
json.dump([{\"id\":\"GearTixPostgres1\",\"name\":\"Tickets Postgres\",\"type\":\"postgres\",
  \"data\":{\"host\":\"postgres\",\"port\":5432,\"database\":\"tickets\",
  \"user\":env.get(\"POSTGRES_USER\",\"n8n\"),\"password\":env.get(\"POSTGRES_PASSWORD\",\"\"),
  \"ssl\":\"disable\",\"allowUnauthorizedCerts\":False,\"maxConnections\":100,\"sshTunnel\":False}}],
  open(\"/tmp/gear-cred.json\",\"w\"))
"
      sudo docker cp /tmp/gear-cred.json n8n-n8n-1:/tmp/gear-cred.json
      sudo docker compose -f /opt/n8n/docker-compose.yml exec -T n8n n8n import:credentials --input=/tmp/gear-cred.json 2>&1 | grep -i success
      sudo rm -f /tmp/gear-cred.json
      sudo docker exec -u root n8n-n8n-1 rm -f /tmp/gear-cred.json
  fi
'
echo

# --- 4b. container env, photo mount, credential shells ---------------------
# The n8n service passes env through an explicit `environment:` list, so putting
# a var in .env alone does NOT reach the container — it has to be in both.
# The photo dir also has to be bind-mounted: `Save Photos to Disk` writes to
# /opt/gear-tickets/photos from *inside* the container, and without the mount
# those files land in the container's own filesystem where nginx can't see them
# and a `compose up` throws them away. NODE_FUNCTION_ALLOW_BUILTIN is what lets
# that Code node require('fs') at all.
echo "--- container env + photo mount ---"
$SSH "$VM" '
  set -e
  TS=$(date +%Y%m%d%H%M%S)
  sudo cp /opt/n8n/.env /opt/n8n/.env.bak-$TS
  sudo cp /opt/n8n/docker-compose.yml /opt/n8n/docker-compose.yml.bak-$TS

  for kv in "TRIAGE_API_URL=https://api.groq.com/openai/v1/chat/completions" \
            "TRIAGE_MODEL=llama-3.3-70b-versatile" \
            "NODE_FUNCTION_ALLOW_BUILTIN=fs,path"; do
    k="${kv%%=*}"
    if sudo grep -q "^${k}=" /opt/n8n/.env; then
        sudo sed -i "s|^${k}=.*|${kv}|" /opt/n8n/.env
    else
        echo "$kv" | sudo tee -a /opt/n8n/.env > /dev/null
    fi
  done

  sudo python3 - <<PY
p="/opt/n8n/docker-compose.yml"
s=open(p).read()
a="      EXECUTIONS_DATA_MAX_AGE: \${EXECUTIONS_DATA_MAX_AGE}\n"
add=("      TRIAGE_API_URL: \${TRIAGE_API_URL}\n"
     "      TRIAGE_MODEL: \${TRIAGE_MODEL}\n"
     "      NODE_FUNCTION_ALLOW_BUILTIN: \${NODE_FUNCTION_ALLOW_BUILTIN}\n")
if "TRIAGE_API_URL" not in s and a in s: s=s.replace(a,a+add)
v="      - n8ndata:/home/node/.n8n\n"
vadd="      - /opt/gear-tickets/photos:/opt/gear-tickets/photos\n"
if "gear-tickets/photos" not in s and v in s: s=s.replace(v,v+vadd)
open(p,"w").write(s)
PY

  # n8n runs as uid 1000; nginx (uid 101) still reads via o+rx
  sudo chown -R 1000:1000 /opt/gear-tickets/photos
  sudo chmod -R 755 /opt/gear-tickets/photos
  cd /opt/n8n && sudo docker compose config -q && echo "  compose valid"
'
echo

# Credential SHELLS with fixed ids, so the workflows can be wired before Brian
# has pasted anything. He opens each in the UI and replaces the placeholder —
# no token ever goes through this script or a log.
echo "--- credential shells ---"
$SSH "$VM" '
  if sudo docker compose -f /opt/n8n/docker-compose.yml exec -T postgres \
       psql -U n8n -d n8n -tAc "SELECT 1 FROM credentials_entity WHERE id='"'"'GearTixTriageLLM'"'"';" | grep -q 1; then
      echo "  credential shells already exist"
  else
      cat > /tmp/gear-creds.json <<JSON
[
  {"id":"GearTixTriageLLM","name":"Triage LLM","type":"httpHeaderAuth",
   "data":{"name":"Authorization","value":"Bearer PASTE_GROQ_KEY_HERE"}},
  {"id":"GearTixMondayAPI","name":"Monday API","type":"httpHeaderAuth",
   "data":{"name":"Authorization","value":"PASTE_MONDAY_TOKEN_HERE"}}
]
JSON
      sudo docker cp /tmp/gear-creds.json n8n-n8n-1:/tmp/gear-creds.json
      sudo docker compose -f /opt/n8n/docker-compose.yml exec -T n8n \
        n8n import:credentials --input=/tmp/gear-creds.json 2>&1 | grep -i success
      rm -f /tmp/gear-creds.json
      sudo docker exec -u root n8n-n8n-1 rm -f /tmp/gear-creds.json
  fi
'
echo

# --- 5. workflows ----------------------------------------------------------
# import:workflow does NOT carry active state — it has to be published after,
# and n8n needs a restart before the webhook actually registers.
echo "--- workflows ---"
for f in 01_intake.json 02_nightly.json; do
    scp -q -o "ProxyJump tds" -i "$KEY" "$REPO/n8n/$f" "$VM:/tmp/$f"
    $SSH "$VM" "sudo docker cp /tmp/$f n8n-n8n-1:/tmp/$f && $N8N exec -T n8n n8n import:workflow --input=/tmp/$f 2>&1 | grep -i 'success\|error'"
done

$SSH "$VM" "
  $N8N exec -T n8n n8n publish:workflow --id=GearTixIntake001 2>&1 | grep -i publish
  $N8N restart n8n > /dev/null 2>&1
  echo '  waiting for n8n...'
  for i in \$(seq 1 40); do
    code=\$(curl -s -o /dev/null -w '%{http_code}' -H 'Host: tickets.tinydoorstudios.com' 'http://127.0.0.1:8088/form/gear-ticket' --max-time 5)
    [ \"\$code\" = '200' ] && { echo '  form is live'; break; }
    sleep 2
  done
"
echo

# --- 6. verify -------------------------------------------------------------
echo "--- verify ---"
$SSH "$VM" "
  echo 'tables:'
  $N8N exec -T postgres psql -U n8n -d tickets -tAc \"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1;\" | sed 's/^/    /'
  echo 'vhosts (all must answer):'
  for h in tinydoorstudios.com kb.tinydoorstudios.com n8n.tinydoorstudios.com tickets.tinydoorstudios.com; do
    printf '    %-32s %s\n' \"\$h\" \"\$(curl -s -o /dev/null -w '%{http_code}' -H \"Host: \$h\" http://127.0.0.1:8088/ --max-time 8)\"
  done
  echo 'form:'
  printf '    /form/gear-ticket                %s\n' \"\$(curl -s -o /dev/null -w '%{http_code}' -H 'Host: tickets.tinydoorstudios.com' http://127.0.0.1:8088/form/gear-ticket --max-time 8)\"
"
echo
echo "=== done ==="
echo
echo "STILL NEEDED — these want tokens only Brian has:"
echo "  The two Header Auth credentials already EXIST with placeholder values and"
echo "  are already wired into the nodes. Brian only pastes the secret:"
echo "     n8n UI -> Credentials -> 'Triage LLM'  -> value: Bearer <groq key>"
echo "     n8n UI -> Credentials -> 'Monday API'  -> value: <monday personal token>"
echo "  Set the Slack channel on 'Alert Brian' and 'Morning Digest'."
echo "  Publish 'Gear Tickets — Nightly Caretaker' once its creds are real:"
echo "     n8n publish:workflow --id=GearTixNightly01   (then restart n8n)"
echo
read -n 1 -s -r -p "Press any key to close..."
