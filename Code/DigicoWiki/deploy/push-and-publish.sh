#!/usr/bin/env bash
# Build site/, ship content + figures + publisher to CT 101, publish there (API key stays on the CT).
#   deploy/push-and-publish.sh [--no-assets] [--nav] [--search]
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/build_site.py
rm -rf site/figures site/downloads; cp -r figures site/figures; [ -d downloads ] && cp -r downloads site/downloads || true
cp tools/publish.py site/publish.py
tar -C site -czf /tmp/digico-site.tgz .
scp -q /tmp/digico-site.tgz tds:/tmp/digico-site.tgz
ssh tds 'pct push 101 /tmp/digico-site.tgz /root/digico-site.tgz && rm /tmp/digico-site.tgz && pct exec 101 -- bash -c "rm -rf /root/digico-site && mkdir -p /root/digico-site && tar -C /root/digico-site -xzf /root/digico-site.tgz && rm /root/digico-site.tgz && source /root/.digico-apikey && cd /root/digico-site && API_KEY=\$API_KEY python3 publish.py /root/digico-site '"$*"'"'
