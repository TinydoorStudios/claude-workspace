#!/usr/bin/env python3
"""Import Claude-folder text docs into the fresh Wiki.js as pages (GraphQL).
Pass 1: markdown + text. Binary downloads handled in a second pass.
Runs ON THE MAC (needs LAN access to the Wiki.js API). Reads KB_WIKI_API_KEY from env.
Idempotent: existing pages are skipped.
"""
import os, re, json, sys, urllib.request

API = os.environ.get("KB_WIKI_API_URL", "http://192.168.200.126:3000/graphql")
KEY = os.environ.get("KB_WIKI_API_KEY", "").strip()
ROOT = os.path.expanduser("~/Documents/Claude")

if not KEY:
    print("ERROR: KB_WIKI_API_KEY not set"); sys.exit(1)

# ---- what to include / exclude ----
INCLUDE_DIRS = ["audio", "KNOWLEDGE", "Code", "about-me", "Projects"]
INCLUDE_ROOT_FILES = True            # root-level .md too (minus secrets)
EXCLUDE_DIR_PARTS = {".git", "__pycache__", "node_modules", "site-packages",
                     "venv", ".venv", "dist-info", "_ARCHIVE", "Kims Stuff",
                     ".pytest_cache", "egg-info"}
EXCLUDE_NAMES = {"TDS_Credentials_CheatSheet.md"}
EXCLUDE_NAME_RE = re.compile(r"(credential|secret|\.pat|password)", re.I)
TEXT_EXT = {".md", ".txt"}

def slug(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "x"

def wiki_path(rel):
    rel = os.path.splitext(rel)[0]
    parts = [slug(p) for p in rel.split(os.sep) if p and slug(p)]
    # collapse a trailing 'wiki' duplicate noise but keep structure
    return "/".join(parts)

def title_of(path, body):
    m = re.search(r'^title:\s*"?(.+?)"?\s*$', body[:1500], re.M)
    if m: return m.group(1).strip()
    m = re.search(r'^#\s+(.+)$', body, re.M)
    if m: return m.group(1).strip()
    base = os.path.splitext(os.path.basename(path))[0]
    return base.replace("-", " ").replace("_", " ").strip().title()

def gql(query, variables):
    data = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

CREATE = """mutation($content:String!,$description:String!,$path:String!,$title:String!,$tags:[String]!){
 pages{create(content:$content,description:$description,editor:"markdown",isPublished:true,
 isPrivate:false,locale:"en",path:$path,tags:$tags,title:$title){
 responseResult{succeeded errorCode message} page{id path}}}}"""

def collect():
    files = []
    # root-level docs
    if INCLUDE_ROOT_FILES:
        for f in os.listdir(ROOT):
            p = os.path.join(ROOT, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() in TEXT_EXT \
               and f not in EXCLUDE_NAMES and not EXCLUDE_NAME_RE.search(f):
                files.append(p)
    for d in INCLUDE_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base): continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in EXCLUDE_DIR_PARTS
                           and not x.endswith(".egg-info")]
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in TEXT_EXT \
                   and fn not in EXCLUDE_NAMES and not EXCLUDE_NAME_RE.search(fn):
                    files.append(os.path.join(dirpath, fn))
    return files

def main():
    files = collect()
    print(f"Found {len(files)} text docs to import.\n")
    ok = skip = fail = 0
    for p in sorted(files):
        rel = os.path.relpath(p, ROOT)
        try:
            body = open(p, encoding="utf-8", errors="replace").read()
        except Exception as e:
            print(f"READ-FAIL {rel}: {e}"); fail += 1; continue
        if p.lower().endswith(".txt"):
            body = "```\n" + body + "\n```"
        path = wiki_path(rel)
        title = title_of(p, body)
        desc = (re.search(r'^description:\s*"?(.+?)"?\s*$', body[:1500], re.M) or [None])
        desc = desc.group(1).strip() if hasattr(desc, "group") else title
        try:
            r = gql(CREATE, {"content": body, "description": desc[:255],
                             "path": path, "title": title[:255], "tags": []})
            rr = r["data"]["pages"]["create"]["responseResult"]
            if rr["succeeded"]:
                ok += 1; print(f"OK    /{path}")
            elif rr.get("errorCode") in (6002, 6, 'PageDuplicateCreate') or "exists" in (rr.get("message","").lower()):
                skip += 1; print(f"EXIST /{path}")
            else:
                fail += 1; print(f"FAIL  /{path}: {rr.get('message')}")
        except Exception as e:
            fail += 1; print(f"ERROR /{path}: {e}")
    print(f"\nDone. created={ok} existed={skip} failed={fail}  total={len(files)}")

if __name__ == "__main__":
    main()
