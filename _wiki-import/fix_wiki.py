#!/usr/bin/env python3
"""Fix the rebuilt wiki:
 1) Repair internal cross-links (root /slug -> /audio/live-sound-kb/wiki/slug).
 2) Rebuild the Shows page listing EVERY show + all paperwork with download links.
"""
import os, re, json, urllib.request, sys
BASE = os.environ.get("KB_WIKI_BASE", "http://192.168.200.126:3000")
API = BASE + "/graphql"
KEY = os.environ.get("KB_WIKI_API_KEY", "").strip()
if not KEY: print("ERROR: KB_WIKI_API_KEY not set"); sys.exit(1)
HDR = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
KBP = "/audio/live-sound-kb/wiki/"

def gql(q, v=None):
    req = urllib.request.Request(API, data=json.dumps({"query": q, "variables": v or {}}).encode(), headers=HDR)
    with urllib.request.urlopen(req, timeout=40) as r: return json.loads(r.read())

# ---------- asset tree ----------
def asset_tree():
    """return dict: folderPath -> list of filenames"""
    out = {}
    def walk(fid, path):
        files = gql("query($p:Int!){assets{list(folderId:$p,kind:ALL){filename}}}", {"p": fid})
        fl = [a["filename"] for a in (files["data"]["assets"]["list"] or [])]
        if fl: out[path] = fl
        subs = gql("query($p:Int!){assets{folders(parentFolderId:$p){id slug}}}", {"p": fid})
        for f in (subs["data"]["assets"]["folders"] or []):
            walk(f["id"], (path + "/" + f["slug"]).lstrip("/"))
    walk(0, "")
    return out

def label(fn):
    base = os.path.splitext(fn)[0]; ext = os.path.splitext(fn)[1].lstrip(".").upper()
    base = re.sub(r"[-_]+", " ", base).strip().title()
    return f"{base} ({ext})"

# ---------- build shows page ----------
SHOWS_2025 = {  # 2025-shows folder grouped by filename prefix
    "atomic-wiseguys": "Atomic Wiseguys",
    "chicago-tribute": "Chicago Tribute",
    "donna-the-buffalo": "Donna The Buffalo",
    "on-a-winters-night": "On A Winter's Night",
    "pop-goes-emo": "Pop Goes Emo",
    "talk-low-festival": "Talk Low Festival",
}

def build_shows(tree):
    venues = {"Memorial Hall": [], "Fountain Square": []}
    # date-prefixed show folders under files/audio/<venue>/<date-...> and assets/shows/<date-...>
    for path, files in tree.items():
        m = re.search(r"/([0-9]{4}-[0-9]{2}-[0-9]{2})[-_]?(.*)$", "/" + path)
        if not m: continue
        date, rest = m.group(1), m.group(2)
        title = re.sub(r"[-_]+", " ", rest).strip().title() or "Show"
        ven = "Memorial Hall" if "memorial-hall" in path else ("Fountain Square" if "fountain-square" in path or path.startswith("assets/shows") else "Other")
        links = [f"  - [{label(f)}](/{path}/{f})" for f in sorted(files)]
        venues.setdefault(ven, []).append((date, f"### {date} — {title}\n" + "\n".join(links)))
    # 2025-shows archive grouped by prefix
    arch = tree.get("files/audio/memorial-hall/2025-shows", [])
    if arch:
        groups = {}
        for f in arch:
            key = next((k for k in SHOWS_2025 if f.lower().startswith(k)), None)
            name = SHOWS_2025.get(key, "Other")
            groups.setdefault(name, []).append(f)
        for name in sorted(groups):
            links = [f"  - [{label(f)}](/files/audio/memorial-hall/2025-shows/{f})" for f in sorted(groups[name])]
            venues["Memorial Hall"].append(("2025", f"### {name} (2025)\n" + "\n".join(links)))

    out = ["# Shows\n", "Every show and all the paperwork we've built — input lists, channel processing, showfiles, packets. Click any item to download.\n"]
    for ven in ["Memorial Hall", "Fountain Square", "Other"]:
        items = venues.get(ven) or []
        if not items: continue
        out.append(f"\n## {ven}\n")
        for _, block in sorted(items, key=lambda x: x[0], reverse=True):
            out.append(block + "\n")
    return "\n".join(out)

def update_page_by_path(path, title, content):
    sp = gql("query($p:String!,$l:String!){pages{singleByPath(path:$p,locale:$l){id description editor isPublished isPrivate locale path title}}}",
             {"p": path, "l": "en"})
    pg = sp["data"]["pages"]["singleByPath"]
    UP = ("mutation($id:Int!,$content:String!,$description:String!,$editor:String!,$isPublished:Boolean!,"
      "$isPrivate:Boolean!,$locale:String!,$path:String!,$tags:[String]!,$title:String!){pages{update("
      "id:$id,content:$content,description:$description,editor:$editor,isPublished:$isPublished,"
      "isPrivate:$isPrivate,locale:$locale,path:$path,tags:$tags,title:$title){responseResult{succeeded message}}}}")
    r = gql(UP, {"id": pg["id"], "content": content, "description": pg["description"] or title,
                 "editor": pg["editor"] or "markdown", "isPublished": True, "isPrivate": False,
                 "locale": "en", "path": pg["path"], "tags": [], "title": title})
    return r["data"]["pages"]["update"]["responseResult"]

# ---------- link fix ----------
def fix_links():
    pages = gql("query{pages{list(orderBy:PATH){id path}}}")["data"]["pages"]["list"]
    kb_slugs = {p["path"].split("/")[-1] for p in pages if p["path"].startswith("audio/live-sound-kb/wiki/")}
    pat = re.compile(r"\]\(/([a-z0-9][a-z0-9\-]*)(#[^)]*)?\)")
    changed = 0
    for p in pages:
        single = gql("query($id:Int!){pages{single(id:$id){id content description editor isPublished isPrivate locale path title}}}",
                     {"id": p["id"]})["data"]["pages"]["single"]
        content = single["content"]
        def rep(m):
            slug, anchor = m.group(1), m.group(2) or ""
            if slug in kb_slugs:
                return f"](" + KBP + slug + anchor + ")"
            return m.group(0)
        new = pat.sub(rep, content)
        if new != content:
            UP = ("mutation($id:Int!,$content:String!,$description:String!,$editor:String!,$isPublished:Boolean!,"
              "$isPrivate:Boolean!,$locale:String!,$path:String!,$tags:[String]!,$title:String!){pages{update("
              "id:$id,content:$content,description:$description,editor:$editor,isPublished:$isPublished,"
              "isPrivate:$isPrivate,locale:$locale,path:$path,tags:$tags,title:$title){responseResult{succeeded}}}}")
            gql(UP, {"id": single["id"], "content": new, "description": single["description"] or single["title"],
                     "editor": single["editor"] or "markdown", "isPublished": True, "isPrivate": False,
                     "locale": "en", "path": single["path"], "tags": [], "title": single["title"]})
            changed += 1; print("relinked:", single["path"])
    print(f"links fixed in {changed} pages")

if __name__ == "__main__":
    print("== fixing cross-links ==")
    fix_links()
    print("\n== rebuilding Shows page ==")
    tree = asset_tree()
    content = build_shows(tree)
    rr = update_page_by_path("audio/live-sound-kb/wiki/shows", "Shows", content)
    print("shows page:", "OK" if rr["succeeded"] else rr.get("message"))
