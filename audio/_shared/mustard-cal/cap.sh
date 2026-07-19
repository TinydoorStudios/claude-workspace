#!/bin/sh
SP="$(dirname "$0")"
screencapture -x "$SP/cur.png"
sips -Z 1728 "$SP/cur.png" --out "$SP/cur_s.png" >/dev/null 2>&1
