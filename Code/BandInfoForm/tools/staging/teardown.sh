#!/usr/bin/env bash
# Remove the staging clone: app, stub, test DB, copied files.
T=$HOME/advtest
for p in gunicorn mailstub; do
  [ -f "$T/$p.pid" ] && kill "$(cat "$T/$p.pid")" 2>/dev/null; rm -f "$T/$p.pid"
done
pkill -f "advtest/code/tools/staging/mailstub.py" 2>/dev/null || true
pkill -f "127.0.0.1:8198" 2>/dev/null || true
for p in $(ss -ltnp 2>/dev/null | grep -E ":8199 |:8198 " | grep -oE "pid=[0-9]+" | cut -d= -f2 | sort -u); do kill "$p" 2>/dev/null || true; done
# 2026-09-21 sweep (TEST-6): the app spawns tools with start_new_session, so they outlive gunicorn
# and hold advance_test open. Kill only python whose cwd is under $T; live runs sit in /opt/band-advance.
T_REAL=$(readlink -f "$T" 2>/dev/null || echo "$T")
killed=""
for p in $(pgrep -u "$(id -u)" -f 'python' 2>/dev/null); do
  c=$(readlink "/proc/$p/cwd" 2>/dev/null) || continue
  case "$c" in "$T_REAL"/*|"$T"/*) kill "$p" 2>/dev/null && killed="$killed $p";; esac
done
for i in 1 2 3 4 5; do
  alive=""; for p in $killed; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ -z "$alive" ] && break; sleep 1
done
sudo docker exec advance-db psql -U advance -d advance -qc "DROP DATABASE IF EXISTS advance_test WITH (FORCE);" 2>/dev/null || true
rm -rf "$T"
echo "staging removed"
