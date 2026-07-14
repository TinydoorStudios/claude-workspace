#!/usr/bin/env python3
"""Create/replace the Wiki.js home page with a navigable landing page."""
import os, json, urllib.request, urllib.error, sys
BASE = os.environ.get("KB_WIKI_BASE", "http://192.168.200.126:3000")
API = BASE + "/graphql"
KEY = os.environ.get("KB_WIKI_API_KEY", "").strip()
if not KEY: print("ERROR: KB_WIKI_API_KEY not set"); sys.exit(1)
HDR = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
W = "/audio/live-sound-kb/wiki"   # KB page prefix

def gql(q, v):
    req = urllib.request.Request(API, data=json.dumps({"query": q, "variables": v}).encode(), headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

CONTENT = f"""# Live Sound KB

Working reference for live sound, multitrack, and post — venues, consoles, mic library, EQ and reverb starting points, show workflows, and every show file. Use the sections below or the search bar up top. File downloads open for anyone with a login.

## Start here

- [Documents Library](/documents) — every PDF, showfile, spreadsheet, and image, grouped by area (downloads)
- [All Shows](/audio/live-sound-kb/wiki/shows) — show pages with input lists, EQ, mic choices, and downloads
- [EQ Starting Points]({W}/eq-starting-points) · [Mic Library]({W}/mic-library) · [Reverb Reference]({W}/reverb-reference-memo)

---

## Venues

| Venue | |
|---|---|
| [Memorial Hall (Memo)]({W}/venue-memorial-hall) | 556-seat Beaux Arts hall · Q225 house · Jazz At The Memo |
| [Fountain Square (FSQ)]({W}/venue-fountain-square) | Outdoor plaza · Q225 FOH |
| [Washington Park (WP)]({W}/venue-washington-park) | Outdoor · Midas M32 |
| [Elm Street Plaza (ESP)]({W}/venue-elm-street-plaza) | Outdoor plaza |
| [Court Street Plaza (CSP)]({W}/venue-court-street-plaza) | Outdoor plaza |
| [Zeigler Park (ZP)]({W}/venue-zeigler-park) | Outdoor plaza |
| [Imagination Alley (IA)]({W}/venue-imagination-alley) | Outdoor |
| [Greaves Concert Hall (NKU)]({W}/venue-greaves-concert-hall) | 637-seat concert hall · two 9ft grands |

## Consoles

- [DiGiCo Quantum 225]({W}/console-digico-q225) — primary large-format desk
- [Behringer Wing]({W}/console-behringer-wing)
- [Yamaha CL3]({W}/console-yamaha-cl3)
- [Midas M32]({W}/console-midas-m32)

## Kit & Technique

- [Mic Library]({W}/mic-library) — full inventory, kit packages, pairings
- [DPA 4099 Clip-On]({W}/mic-dpa-4099) — extreme SPL, mounting, per-instrument EQ
- [EQ Starting Points]({W}/eq-starting-points) — by instrument and venue
- [Reverb Reference — Memo / Seventh Heaven Pro]({W}/reverb-reference-memo)

## Workflows

- [Show Document Workflow]({W}/show-document-workflow) — folders, input lists, stage plots, master PDFs
- [Show Processing Pipeline]({W}/show-processing-pipeline) — overview
- [Pipeline Spec — Memorial Hall]({W}/pipeline-spec-memo) · [Pipeline Spec — Fountain Square]({W}/pipeline-spec-fsq)
- [Input List Design Spec]({W}/input-list-design-spec)
- [Multitrack Recording (REAPER / Studio One)]({W}/multitrack-recording-workflow)
- [Post & Mastering (WaveLab 12)]({W}/post-and-mastering-workflow)

## Shows & Projects

- [All Shows]({W}/shows)
- [Active Projects]({W}/active-projects)
- [Open Questions]({W}/questions)

---

*Tip: anything that isn't a page lives in the [Documents Library](/documents) as a download. To add people, an admin can go to Administration → Users → New User.*
"""

def main():
    # delete an existing /home if present, then create fresh
    try:
        sp = gql("query($path:String!,$locale:String!){pages{singleByPath(path:$path,locale:$locale){id}}}",
                 {"path":"home","locale":"en"})
        pid = (sp.get("data",{}).get("pages",{}).get("singleByPath") or {}).get("id")
        if pid:
            gql("mutation($id:Int!){pages{delete(id:$id){responseResult{succeeded message}}}}", {"id":pid})
            print("removed old /home")
    except Exception as e:
        print("(no existing home / check skipped:", e, ")")
    CREATE = ("mutation($content:String!,$description:String!,$path:String!,$title:String!){"
      "pages{create(content:$content,description:$description,editor:\"markdown\",isPublished:true,"
      "isPrivate:false,locale:\"en\",path:$path,tags:[],title:$title){responseResult{succeeded errorCode message}}}}")
    r = gql(CREATE, {"content":CONTENT,"description":"Live Sound KB home","path":"home","title":"Live Sound KB"})
    rr = r["data"]["pages"]["create"]["responseResult"]
    print("home page:", "OK /home" if rr["succeeded"] else rr.get("message"))

if __name__ == "__main__":
    main()
