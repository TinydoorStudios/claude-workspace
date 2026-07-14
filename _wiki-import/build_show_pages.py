#!/usr/bin/env python3
"""Restructure Shows: index page = clickable show titles; one sub-page per show
holding that show's downloadable files."""
import os, re, json, urllib.request, sys
BASE = os.environ.get("KB_WIKI_BASE", "http://192.168.200.126:3000")
API = BASE + "/graphql"
KEY = os.environ.get("KB_WIKI_API_KEY", "").strip()
if not KEY: print("ERROR: KB_WIKI_API_KEY not set"); sys.exit(1)
HDR = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
SHOWS_ROOT = "audio/live-sound-kb/wiki/shows"

def gql(q, v=None):
    req = urllib.request.Request(API, data=json.dumps({"query": q, "variables": v or {}}).encode(), headers=HDR)
    with urllib.request.urlopen(req, timeout=40) as r: return json.loads(r.read())

def asset_tree():
    out = {}
    def walk(fid, path):
        fl = [a["filename"] for a in (gql("query($p:Int!){assets{list(folderId:$p,kind:ALL){filename}}}",{"p":fid})["data"]["assets"]["list"] or [])]
        if fl: out[path] = fl
        for f in (gql("query($p:Int!){assets{folders(parentFolderId:$p){id slug}}}",{"p":fid})["data"]["assets"]["folders"] or []):
            walk(f["id"], (path+"/"+f["slug"]).lstrip("/"))
    walk(0, ""); return out

def slug(s):
    s=s.lower().strip(); s=re.sub(r"[^a-z0-9]+","-",s); return re.sub(r"-+","-",s).strip("-")
def clean(s):
    return re.sub(r"[-_]+"," ",s).strip().title()
def label(fn):
    base=os.path.splitext(fn)[0]; ext=os.path.splitext(fn)[1].lstrip(".").upper()
    return f"{clean(base)} ({ext})"
def venue_of(path):
    if "memorial-hall" in path: return "Memorial Hall"
    if "fountain-square" in path or path.startswith("assets/shows"): return "Fountain Square"
    return "Other"

SHOWS_2025 = {"atomic-wiseguys":"Atomic Wiseguys","chicago-tribute":"Chicago Tribute",
 "donna-the-buffalo":"Donna The Buffalo","on-a-winters-night":"On A Winter's Night",
 "pop-goes-emo":"Pop Goes Emo","talk-low-festival":"Talk Low Festival"}

def assemble():
    tree = asset_tree(); shows={}
    for path, files in tree.items():
        if "/2025-shows" in path: continue
        m = re.search(r"(?:^|/)([0-9]{4}-[0-9]{2}-[0-9]{2})[-_]?(.*)$", path)
        if not m or "/" not in path: continue
        date=m.group(1); title=clean(m.group(2)) or "Show"; ven=venue_of(path)
        key=(ven, slug(title))
        s=shows.setdefault(key,{"venue":ven,"date":date,"title":title,"files":{}})
        for f in files: s["files"][label(f)]=f"/{path}/{f}"
    for f in tree.get("files/audio/memorial-hall/2025-shows",[]):
        k=next((k for k in SHOWS_2025 if slug(f).startswith(k)),None); name=SHOWS_2025.get(k,"Other")
        key=("Memorial Hall", slug(name)+"-2025")
        s=shows.setdefault(key,{"venue":"Memorial Hall","date":"2025","title":name,"files":{}})
        s["files"][label(f)]=f"/files/audio/memorial-hall/2025-shows/{f}"
    return shows

def upsert(path, title, content):
    sp=gql("query($p:String!,$l:String!){pages{singleByPath(path:$p,locale:$l){id}}}",{"p":path,"l":"en"})
    pid=(sp.get("data",{}).get("pages",{}).get("singleByPath") or {}).get("id")
    if pid:
        UP=("mutation($id:Int!,$content:String!,$description:String!,$editor:String!,$isPublished:Boolean!,$isPrivate:Boolean!,$locale:String!,$path:String!,$tags:[String]!,$title:String!){pages{update(id:$id,content:$content,description:$description,editor:$editor,isPublished:$isPublished,isPrivate:$isPrivate,locale:$locale,path:$path,tags:$tags,title:$title){responseResult{succeeded message}}}}")
        return gql(UP,{"id":pid,"content":content,"description":title,"editor":"markdown","isPublished":True,"isPrivate":False,"locale":"en","path":path,"tags":[],"title":title})["data"]["pages"]["update"]["responseResult"]
    CR=("mutation($content:String!,$description:String!,$path:String!,$title:String!){pages{create(content:$content,description:$description,editor:\"markdown\",isPublished:true,isPrivate:false,locale:\"en\",path:$path,tags:[],title:$title){responseResult{succeeded message}}}}")
    return gql(CR,{"content":content,"description":title,"path":path,"title":title})["data"]["pages"]["create"]["responseResult"]

def purge_show_subpages():
    pages=gql("query{pages{list(orderBy:PATH){id path}}}")["data"]["pages"]["list"]
    for p in pages:
        if p["path"].startswith(SHOWS_ROOT+"/"):
            gql("mutation($id:Int!){pages{delete(id:$id){responseResult{succeeded}}}}",{"id":p["id"]})
            print("removed old", p["path"])

def main():
    purge_show_subpages()
    shows=assemble()
    # per-show pages
    by_venue={}
    for (ven,_), s in shows.items():
        spath=f"{SHOWS_ROOT}/{slug(ven)}/{(s['date']+'-'+slug(s['title'])) if s['date']!='2025' else slug(s['title'])+'-2025'}"
        lines=[f"# {s['title']}", "", f"**{s['venue']}** · {s['date']}", "", "## Files", ""]
        for lab in sorted(s["files"]): lines.append(f"- [{lab}]({s['files'][lab]})")
        lines += ["", "---", "[← All Shows](/audio/live-sound-kb/wiki/shows)"]
        rr=upsert(spath, s["title"], "\n".join(lines))
        print(("OK   " if rr["succeeded"] else "FAIL ")+ "/"+spath + ("" if rr["succeeded"] else " "+str(rr.get("message"))))
        by_venue.setdefault(s["venue"],[]).append((s["date"], s["title"], "/"+spath))
    # index
    idx=["# Shows","","Pick a show to see its input list, channel processing, showfiles, and packets.",""]
    for ven in ["Memorial Hall","Fountain Square","Other"]:
        items=by_venue.get(ven)
        if not items: continue
        idx.append(f"\n## {ven}\n")
        for date,title,url in sorted(items,key=lambda x:x[0],reverse=True):
            idx.append(f"- [{title}]({url}) — {date}")
    rr=upsert("audio/live-sound-kb/wiki/shows","Shows","\n".join(idx))
    print(("OK   " if rr["succeeded"] else "FAIL ")+"shows index")

if __name__=="__main__": main()
