#!/usr/bin/env python3
"""
publish.py — push site/pages.json + figures/ + downloads/ into the DiGiCo Wiki.js instance.
Runs ON the wiki container (CT 101) so the API key never leaves the server:
    API_KEY=… WIKI=http://127.0.0.1:3002 python3 publish.py <site_dir> [--no-assets] [--search] [--nav]
Idempotent: pages are created or updated by path, assets skipped if the filename already exists.
"""
import os, sys, json, glob, urllib.request, uuid, mimetypes, time
WIKI = os.environ.get('WIKI', 'http://127.0.0.1:3002'); KEY = os.environ['API_KEY']
H = {'Authorization': 'Bearer ' + KEY}
def gql(q, v=None):
    req = urllib.request.Request(WIKI + '/graphql', data=json.dumps({'query': q, 'variables': v or {}}).encode(), headers={**H, 'Content-Type': 'application/json'})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code} on query {q[:120]}… body: {e.read()[:600]}')
    if r.get('errors'): raise SystemExit('GraphQL error: ' + json.dumps(r['errors'])[:500])
    return r['data']
def upload(folder_id, fp):
    boundary = uuid.uuid4().hex; name = os.path.basename(fp)
    ctype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    body = b''
    body += f'--{boundary}\r\nContent-Disposition: form-data; name="mediaUpload"\r\n\r\n{json.dumps({"folderId": folder_id})}\r\n'.encode()
    body += f'--{boundary}\r\nContent-Disposition: form-data; name="mediaUpload"; filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode() + open(fp, 'rb').read() + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()
    req = urllib.request.Request(WIKI + '/u', data=body, headers={**H, 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    try:
        return urllib.request.urlopen(req, timeout=300).status
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code} uploading {name}: {e.read()[:400]}')
def ensure_folder(slug):
    fl = gql('{assets{folders(parentFolderId:0){id name slug}}}')['assets']['folders']
    for f in fl:
        if f['slug'] == slug: return f['id']
    gql('mutation($s:String!,$n:String){assets{createFolder(parentFolderId:0,slug:$s,name:$n){responseResult{succeeded message}}}}', {'s': slug, 'n': slug})
    return ensure_folder(slug)
def sync_assets(local_dir, slug):
    if not os.path.isdir(local_dir): return
    fid = ensure_folder(slug)
    have = {a['filename'] for a in gql('query($f:Int!){assets{list(folderId:$f,kind:ALL){id filename}}}', {'f': fid})['assets']['list']}
    files = sorted(glob.glob(os.path.join(local_dir, '*')))
    n = 0
    for fp in files:
        if os.path.basename(fp) in have: continue
        upload(fid, fp); n += 1
        if n % 50 == 0: print(f'  uploaded {n}…', flush=True)
    print(f'assets /{slug}: {len(files)} local, {n} uploaded, {len(have)} already there')
    if '--prune-assets' in sys.argv:
        local = {os.path.basename(f) for f in files}
        for a in gql('query($f:Int!){assets{list(folderId:$f,kind:ALL){id filename}}}', {'f': fid})['assets']['list']:
            if a['filename'] not in local:
                gql('mutation($id:Int!){assets{deleteAsset(id:$id){responseResult{succeeded message}}}}', {'id': a['id']}); print('  deleted asset', a['filename'])
def main():
    site = sys.argv[1]; flags = sys.argv[2:]
    if '--search' in flags:
        r = gql('mutation{site{updateConfig(title:"DiGiCo Q225 Wiki",description:"How to do anything on the Quantum 225, its DMI cards and racks — staff reference",featurePageComments:false,featurePageRatings:false,featurePersonalWikis:false,authAutoLogin:false,authEnforce2FA:false,authHideLocal:false,authLoginBgUrl:"",authJwtAudience:"urn:wiki.js",authJwtExpiration:"30m",authJwtRenewablePeriod:"14d",editFab:true,editMenuBar:false,editMenuBtn:false,editMenuExternalBtn:false,editMenuExternalName:"",editMenuExternalIcon:"",editMenuExternalUrl:"",securityOpenRedirect:true,securityIframe:true,securityReferrerPolicy:true,securityTrustProxy:true,securitySRI:true,securityHSTS:false,securityHSTSDuration:0,securityCSP:false,securityCSPDirectives:"",host:"https://digico.tinydoorstudios.com",company:"Tiny Door Studios / 3CDC",contentLicense:"",footerOverride:"",logoUrl:"https://static.requarks.io/logo/wikijs-butterfly.svg",pageExtensions:"md, html, txt",uploadScanSVG:true,uploadForceDownload:true,uploadMaxFileSize:52428800,uploadMaxFiles:20){responseResult{succeeded message}}}}')
        print('site config:', r['site']['updateConfig']['responseResult'])
    if '--no-assets' not in flags:
        sync_assets(os.path.join(site, 'figures'), 'figures')
        sync_assets(os.path.join(site, 'downloads'), 'downloads')
    pages = json.load(open(os.path.join(site, 'pages.json')))
    existing = {p['path']: p['id'] for p in gql('{pages{list(limit:10000){id path}}}')['pages']['list']}
    created = updated = 0
    for p in pages:
        v = dict(content=p['content'], description=p['description'][:255], title=p['title'][:255], tags=p['tags'], path=p['path'])
        if p['path'] in existing:
            r = gql('mutation($id:Int!,$content:String,$description:String,$title:String,$tags:[String],$path:String){pages{update(id:$id,content:$content,description:$description,title:$title,tags:$tags,isPublished:true,isPrivate:false,locale:"en",editor:"markdown",path:$path){responseResult{succeeded message}}}}', {**v, 'id': existing[p['path']]})
            rr = r['pages']['update']['responseResult']; updated += 1
        else:
            r = gql('mutation($content:String!,$description:String!,$title:String!,$tags:[String]!,$path:String!){pages{create(content:$content,description:$description,editor:"markdown",isPublished:true,isPrivate:false,locale:"en",path:$path,tags:$tags,title:$title){responseResult{succeeded message}}}}', v)
            rr = r['pages']['create']['responseResult']; created += 1
        if not rr['succeeded']: print('  FAIL', p['path'], rr['message'])
    print(f'pages: {created} created, {updated} updated')
    if '--prune' in flags:
        want = {p['path'] for p in pages}
        for path, pid in existing.items():
            if path not in want:
                gql('mutation($id:Int!){pages{delete(id:$id){responseResult{succeeded message}}}}', {'id': pid}); print('  deleted', path)
    if '--nav' in flags:
        nav = json.load(open(os.path.join(site, 'nav.json')))
        items = [dict(id=str(uuid.uuid4()), kind='link', label='Home', icon='mdi-home', targetType='home', target='/', visibilityMode='all', visibilityGroups=[])]
        for label, icon, links in nav:
            items.append(dict(id=str(uuid.uuid4()), kind='divider', label='', icon='', targetType='', target='', visibilityMode='all', visibilityGroups=[]))
            items.append(dict(id=str(uuid.uuid4()), kind='header', label=label, icon=icon, targetType='', target='', visibilityMode='all', visibilityGroups=[]))
            for t, tgt in links:
                items.append(dict(id=str(uuid.uuid4()), kind='link', label=t[:60], icon=icon, targetType='page', target=tgt, visibilityMode='all', visibilityGroups=[]))
        gql('mutation($t:[NavigationTreeInput]!){navigation{updateTree(tree:$t){responseResult{succeeded message}}}}', {'t': [dict(locale='en', items=items)]})
        gql('mutation{navigation{updateConfig(mode:STATIC){responseResult{succeeded message}}}}')
        print(f'nav: {len(items)} items')
    if '--search' in flags:
        r = gql('mutation{search{updateSearchEngines(engines:[{isEnabled:true,key:"postgres",config:[{key:"dictLanguage",value:"{\\"v\\":\\"english\\"}"}]},{isEnabled:false,key:"db",config:[]}]){responseResult{succeeded message}}}}')
        print('search engine:', r['search']['updateSearchEngines']['responseResult'])
        time.sleep(3)
        r = gql('mutation{search{rebuildIndex{responseResult{succeeded message}}}}'); print('rebuild:', r['search']['rebuildIndex']['responseResult'])
main()
