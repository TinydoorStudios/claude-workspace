#!/usr/bin/env python3
"""Upload Claude-folder binaries into Wiki.js as NATIVE assets (served by Wiki.js,
respecting user permissions). Files under a .../Wiki/assets/ dir go to asset paths
that match the imported page links; everything else goes under files/<mirrored path>.
After upload, builds a "Documents" index page linking every file.

  wiki_assets.py --test   # one file
  wiki_assets.py --all    # everything in scope + index page
"""
import os, re, json, sys, uuid, urllib.request, urllib.error

BASE = os.environ.get("KB_WIKI_BASE", "http://192.168.200.126:3000")
API  = BASE + "/graphql"
KEY  = os.environ.get("KB_WIKI_API_KEY", "").strip()
ROOT = os.path.expanduser("~/Documents/Claude")
if not KEY:
    print("ERROR: KB_WIKI_API_KEY not set"); sys.exit(1)
HDR = {"Authorization": "Bearer " + KEY}

INCLUDE_DIRS = ["audio", "KNOWLEDGE", "Code", "about-me", "Projects"]
EXCLUDE_PARTS = {".git","__pycache__","node_modules","site-packages","venv",".venv",
                 "dist-info","_ARCHIVE",".pytest_cache"}
EXCLUDE_NAME_RE = re.compile(r"(credential|secret|password)", re.I)
BIN_EXT = {".pdf",".xlsx",".xls",".docx",".doc",".ses",".png",".jpg",".jpeg",".svg",".pptx",".csv"}

def gql(q, v):
    data = json.dumps({"query": q, "variables": v}).encode()
    req = urllib.request.Request(API, data=data, headers={**HDR,"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

FOLDERS_Q = "query($p:Int!){assets{folders(parentFolderId:$p){id slug}}}"
CREATE_F = ("mutation($p:Int!,$s:String!,$n:String!){assets{createFolder("
            "parentFolderId:$p,slug:$s,name:$n){responseResult{succeeded}}}}")
LIST_Q = "query($p:Int!){assets{list(folderId:$p,kind:ALL){filename}}}"

_fcache = {}
def ensure_folder(slugs):
    parent = 0; key = ""
    for s in slugs:
        key += "/" + s
        if key in _fcache: parent = _fcache[key]; continue
        ex = gql(FOLDERS_Q, {"p": parent})["data"]["assets"]["folders"] or []
        m = next((f for f in ex if f["slug"] == s), None)
        if not m:
            gql(CREATE_F, {"p": parent, "s": s, "n": s})
            ex = gql(FOLDERS_Q, {"p": parent})["data"]["assets"]["folders"] or []
            m = next((f for f in ex if f["slug"] == s), None)
        if not m: raise RuntimeError("folder fail: " + key)
        parent = m["id"]; _fcache[key] = parent
    return parent

def list_files(fid):
    try:
        return {a["filename"] for a in (gql(LIST_Q, {"p": fid})["data"]["assets"]["list"] or [])}
    except Exception:
        return set()

def upload(fp, fid):
    b = "----wiki" + uuid.uuid4().hex
    fn = os.path.basename(fp)
    with open(fp, "rb") as f: fdata = f.read()
    head = (f'--{b}\r\nContent-Disposition: form-data; name="mediaUpload"\r\n\r\n'
            f'{json.dumps({"folderId": fid})}\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="mediaUpload"; filename="{fn}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n').encode()
    body = head + fdata + f'\r\n--{b}--\r\n'.encode()
    req = urllib.request.Request(BASE+"/u", data=body,
        headers={**HDR,"Content-Type":f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r: return r.status
    except urllib.error.HTTPError as e: return e.code

def slug(s):
    s = s.lower().strip(); s = re.sub(r"[^a-z0-9.]+","-",s)
    return re.sub(r"-+","-",s).strip("-")

def target(rel):
    low = rel.replace("\\","/").lower()
    if "/wiki/assets/" in low:
        sub = rel[low.index("/wiki/assets/")+len("/wiki/"):]   # assets/...
        folder = os.path.dirname(sub)
    else:
        folder = "files/" + os.path.dirname(rel)
    slugs = [slug(p) for p in folder.split("/") if slug(p)]
    return slugs

def collect():
    out = []
    for d in INCLUDE_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base): continue
        for dp, dn, fns in os.walk(base):
            dn[:] = [x for x in dn if x not in EXCLUDE_PARTS and not x.endswith(".egg-info")]
            for fn in fns:
                if os.path.splitext(fn)[1].lower() in BIN_EXT and not EXCLUDE_NAME_RE.search(fn):
                    out.append(os.path.join(dp, fn))
    return out

CREATE_PAGE = ("mutation($content:String!,$description:String!,$path:String!,$title:String!){"
 "pages{create(content:$content,description:$description,editor:\"markdown\",isPublished:true,"
 "isPrivate:false,locale:\"en\",path:$path,tags:[],title:$title){responseResult{succeeded errorCode message}}}}")

def main_all():
    files = sorted(collect())
    print(f"{len(files)} binaries to upload.\n")
    manifest = []  # (rel, url, ok)
    ok=skip=fail=0
    for fp in files:
        rel = os.path.relpath(fp, ROOT)
        slugs = target(rel)
        try:
            fid = ensure_folder(slugs)
            before = list_files(fid)
            if os.path.basename(fp) in before or slug(os.path.splitext(os.path.basename(fp))[0]) in {os.path.splitext(x)[0] for x in before}:
                # already there
                url = "/" + "/".join(slugs) + "/" + sorted(before)[0] if False else None
            code = upload(fp, fid)
            after = list_files(fid)
            new = after - before
            realname = (sorted(new)[0] if new else None)
            if realname is None:
                # maybe existed already; try to match
                cand = [x for x in after if slug(os.path.splitext(x)[0])==slug(os.path.splitext(os.path.basename(fp))[0])]
                realname = cand[0] if cand else os.path.basename(fp)
            url = "/" + "/".join(slugs + [realname])
            if code in (200,201):
                ok+=1; print(f"OK   {url}")
            elif not new:
                skip+=1; print(f"EXIST {url}")
            else:
                ok+=1; print(f"OK?  {url} (http {code})")
            manifest.append((rel, url))
        except Exception as e:
            fail+=1; print(f"FAIL {rel}: {e}")
    # build index page
    by_top = {}
    for rel, url in manifest:
        top = rel.split(os.sep)[0]
        by_top.setdefault(top, []).append((rel, url))
    lines = ["# Documents Library\n", "All uploaded files, grouped by area. Click to download.\n"]
    for top in sorted(by_top):
        lines.append(f"\n## {top}\n")
        for rel, url in sorted(by_top[top]):
            name = os.path.basename(rel)
            lines.append(f"- [{name}]({url}) — `{rel}`")
    content = "\n".join(lines)
    try:
        r = gql(CREATE_PAGE, {"content":content,"description":"Index of all uploaded files",
                              "path":"documents","title":"Documents Library"})
        rr = r["data"]["pages"]["create"]["responseResult"]
        print("\nindex page:", "OK /documents" if rr["succeeded"] else rr.get("message"))
    except Exception as e:
        print("\nindex page FAILED:", e)
    print(f"\nDone. uploaded={ok} existed={skip} failed={fail} total={len(files)}")

if __name__ == "__main__":
    if "--all" in sys.argv: main_all()
    else: print("pass --all")
