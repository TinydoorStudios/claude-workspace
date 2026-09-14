"""Wiki.js GraphQL access — read every page of a wiki, and write the teachings-inbox page.

Two wikis: the DiGiCo wiki (all pages) and the Live Sound KB (an allowlist of slugs).
Both are Wiki.js 2.x behind the same GraphQL shape publish.py already uses.
"""
import json
import httpx


class Wiki:
    def __init__(self, base_url: str, api_key: str, public_url: str):
        self.base = base_url.rstrip('/')
        self.public = public_url.rstrip('/')
        self.h = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}

    def gql(self, query: str, variables: dict | None = None) -> dict:
        r = httpx.post(self.base + '/graphql', headers=self.h,
                       content=json.dumps({'query': query, 'variables': variables or {}}), timeout=120)
        r.raise_for_status()
        d = r.json()
        if d.get('errors'):
            raise RuntimeError('GraphQL: ' + json.dumps(d['errors'])[:400])
        return d['data']

    def list_pages(self) -> list[dict]:
        return self.gql('{pages{list(limit:10000){id path title updatedAt isPublished}}}')['pages']['list']

    def get_page(self, page_id: int) -> dict:
        return self.gql('query($id:Int!){pages{single(id:$id){id path title description content tags{tag}}}}',
                        {'id': page_id})['pages']['single']

    def page_url(self, path: str) -> str:
        return f'{self.public}/{path}'

    def upsert_page(self, path: str, title: str, description: str, content: str, tags: list[str]) -> str:
        existing = {p['path']: p['id'] for p in self.list_pages()}
        v = dict(content=content, description=description[:255], title=title[:255], tags=tags, path=path)
        if path in existing:
            r = self.gql('mutation($id:Int!,$content:String,$description:String,$title:String,$tags:[String]){'
                         'pages{update(id:$id,content:$content,description:$description,editor:"markdown",'
                         'isPublished:true,isPrivate:false,locale:"en",tags:$tags,title:$title)'
                         '{responseResult{succeeded message}}}}', {'id': existing[path], **v})
            rr = r['pages']['update']['responseResult']
        else:
            r = self.gql('mutation($content:String!,$description:String!,$title:String!,$tags:[String]!,$path:String!){'
                         'pages{create(content:$content,description:$description,editor:"markdown",isPublished:true,'
                         'isPrivate:false,locale:"en",path:$path,tags:$tags,title:$title)'
                         '{responseResult{succeeded message}}}}', v)
            rr = r['pages']['create']['responseResult']
        if not rr['succeeded']:
            raise RuntimeError(f'wiki write failed for {path}: {rr["message"]}')
        return self.page_url(path)
