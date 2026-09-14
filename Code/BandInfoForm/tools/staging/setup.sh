#!/usr/bin/env bash
# Build the staging clone on the VM. Idempotent — tears down a previous one first.
set -euo pipefail
T=$HOME/advtest
LIVE=/opt/band-advance
# SRC = where the code under test comes from: the live install (default) or a
# repo checkout rsynced to the VM (app/ + tools/ layout, flattened below so
# it matches the live layout every tool assumes).
SRC=${1:-$LIVE}
"$(dirname "$0")/teardown.sh" >/dev/null 2>&1 || true
mkdir -p "$T/Dropbox" "$T/code"

echo "1/5 database clone -> advance_test"
sudo docker exec advance-db psql -U advance -d advance -qc "DROP DATABASE IF EXISTS advance_test;" 2>/dev/null || true
sudo docker exec advance-db psql -U advance -d advance -qc "CREATE DATABASE advance_test OWNER advance;"
sudo docker exec advance-db sh -c "pg_dump -U advance advance | psql -U advance -q advance_test" >/dev/null
LIVE_URL=$(grep -m1 '^ADVANCE_DB_URL=' "$LIVE/advance.env" | cut -d= -f2-)
TEST_URL="${LIVE_URL%/advance}/advance_test"

echo "2/5 Dropbox copy (Nyquist + current/next month venue folders)"
rsync -a --exclude '.dropbox*' "$HOME/Dropbox/Nyquist/" "$T/Dropbox/Nyquist/"
for v in "3CDC Fountain Square" "3CDC Washington Park" "3CDC Court Street" "3CDC Elm Street Plaza" "3CDC Ziegler Park" "3CDC Imagination Alley" "3CDC Memorial Hall"; do
  mkdir -p "$T/Dropbox/$v"
  for m in $(date +%m.%Y) $(date -d '+1 month' +%m.%Y); do
    for d in "$HOME/Dropbox/$v/"$m*; do [ -d "$d" ] && rsync -a "$d/" "$T/Dropbox/$v/$(basename "$d")/"; done
  done
done

echo "3/5 code copy + env (from $SRC)"
if [ -f "$SRC/app/app.py" ]; then
  # repo layout -> flat live layout
  rsync -a --exclude '__pycache__' --exclude 'data' "$SRC/app/" "$T/code/"
  rsync -a --exclude '__pycache__' --exclude drafts --exclude filled --exclude followups --exclude _package "$SRC/tools/" "$T/code/tools/"
  rsync -a "$SRC/ops/" "$T/code/ops/"; rsync -a "$SRC/db/" "$T/code/db/"
else
  rsync -a --exclude venv --exclude '__pycache__' --exclude 'data' "$SRC/" "$T/code/"
fi
mkdir -p "$T/code/data/uploads"; rsync -a "$LIVE/data/uploads/" "$T/code/data/uploads/"
sed "s#__FILLED_BY_SETUP__#$TEST_URL#" "$T/code/tools/staging/advtest.env.template" > "$T/advtest.env"
# schema migrations against the clone too
for m in "$T/code"/db/migrations/*.sql; do sudo docker exec -i advance-db psql -U advance -d advance_test -v ON_ERROR_STOP=1 -q < "$m"; done

echo "4/5 mail stub :8199"
set -a; . "$T/advtest.env"; set +a
rm -f "$T/mail.jsonl"
nohup "$LIVE/venv/bin/python" "$T/code/tools/staging/mailstub.py" --port 8199 --log "$T/mail.jsonl" > "$T/mailstub.log" 2>&1 &
echo $! > "$T/mailstub.pid"

echo "5/5 app :8198"
cd "$T/code"
nohup "$LIVE/venv/bin/gunicorn" --worker-class gthread -w 2 --threads 4 --timeout 120 -b 127.0.0.1:8198 app:app > "$T/gunicorn.log" 2>&1 &
echo $! > "$T/gunicorn.pid"
sleep 2
curl -s http://127.0.0.1:8198/healthz; echo
echo "staging ready: env $T/advtest.env, mail log $T/mail.jsonl"
