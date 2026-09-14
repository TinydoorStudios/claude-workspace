#!/usr/bin/env bash
# Remove the staging clone: app, stub, test DB, copied files.
T=$HOME/advtest
for p in gunicorn mailstub; do
  [ -f "$T/$p.pid" ] && kill "$(cat "$T/$p.pid")" 2>/dev/null; rm -f "$T/$p.pid"
done
pkill -f "advtest/code/tools/staging/mailstub.py" 2>/dev/null || true
pkill -f "127.0.0.1:8198" 2>/dev/null || true
sudo docker exec advance-db psql -U advance -d advance -qc "DROP DATABASE IF EXISTS advance_test;" 2>/dev/null || true
rm -rf "$T"
echo "staging removed"
