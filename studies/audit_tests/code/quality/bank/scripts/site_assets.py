"""Project repository-card links into a self-contained Pages artifact.

Canonical Markdown is never changed. Only explicitly linked card resources and
active-authority publication assets are copied; historical attachments are not
recursively exposed merely because a JSON string mentions a research path.
"""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote,unquote,urlsplit,urlunsplit

MD_LINK=re.compile(r'(?<!\\)(?P<prefix>!?\[[^\]\n]*\]\()(?P<target><[^>]+>|[^\s)]+)(?P<suffix>[^)]*\))')
HTML_LINK=re.compile(r'(?P<prefix>\b(?:href|src)\s*=\s*[\"\'])(?P<target>[^\"\']+)(?P<suffix>[\"\'])',re.I)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(condition,message):
    if not condition:raise ValueError(message)

def is_external(value):
    parts=urlsplit(value)
    return bool(parts.scheme or parts.netloc) or value.startswith('#')

class Projector:
    def __init__(self,root):self.root=Path(root).resolve();self.assets={};self.generated={}
    def include(self,path):
        path=Path(path).resolve();need(path.is_relative_to(self.root),'Site target escapes bank')
        if path.is_dir():
            need(path.is_relative_to(self.root/'lean'),'Only explicit Lean evidence directories may be published as listings')
            links=[]
            for child in sorted(path.iterdir()):
                if child.name.startswith('.'):continue
                self.include(child)
                links.append('<li><a href="'+quote(child.name,safe='-._~')+('/index.html' if child.is_dir() else '')+'">'+html.escape(child.name)+'</a></li>')
            name=str(path.relative_to(self.root))+'/index.html'
            raw=('<!doctype html><meta charset="utf-8"><title>Lean evidence files</title><ul>'+''.join(links)+'</ul>').encode()
            self.generated[name]=raw;self.assets[name]={'sha256':sha(raw),'bytes':len(raw),'generated':True}
            return 'bank/'+quote(name,safe='/-._~')
        need(path.is_file(),'Missing linked site asset: '+str(path))
        name=str(path.relative_to(self.root));need(not name.startswith(('site/','.git/')),'Recursive/private site target refused')
        raw=path.read_bytes();self.assets[name]={'sha256':sha(raw),'bytes':len(raw)}
        return 'bank/'+quote(name,safe='/-._~')
    def url(self,value,base):
        if is_external(value):return value
        p=urlsplit(html.unescape(value));need(not p.path.startswith('/'),'Root-absolute link is not portable to a project site')
        target=(Path(base)/unquote(p.path)).resolve()
        return urlunsplit(('', '', self.include(target),p.query,p.fragment))
    def entry(self,entry,path):
        result=dict(entry)
        def replace(match):
            target=match['target']
            if target.isdecimal() and any(op in match['prefix'] for op in ('∘','⊕')):
                return '\\'+match.group(0) # Literal function evaluation, not a Markdown link.
            angle=target.startswith('<') and target.endswith('>')
            fixed=self.url(target[1:-1] if angle else target,Path(path).parent)
            return match['prefix']+('<'+fixed+'>' if angle else fixed)+match['suffix']
        result['body']=HTML_LINK.sub(replace,MD_LINK.sub(replace,entry['body']))
        result['formalized']=[self.url(value,self.root) for value in entry['formalized']]
        return result
    def active_authority(self,data):
        for key in ('ledger','manifest','previous_authority','correction_consensus_path'):
            if data.get(key):
                self.include(self.root/data[key])
        self.include(self.root/'active_review.json')
        for row in data['records'].values():
            self.include(self.root/row['archive_path'])
            if row['decision']!='retain':
                if row.get('withdrawal_dossier'):
                    self.include(self.root/row['withdrawal_dossier'])
                    self.include((self.root/row['withdrawal_dossier']).with_suffix('.json'))
                    for key,value in row.get('historical_artifacts',{}).items():
                        if key in {'certificate','dossier'}:self.include(self.root/value)
                    for item in row.get('public_supporting_evidence',[]):self.include(self.root/item['vendored_path'])
                continue
            for key in ('certificate','dossier'):self.include(self.root/row[key])
            self.include((self.root/row['dossier']).with_suffix('.json'))
            for item in row.get('evidence_files',[]):self.include(self.root/item['path'])
            for item in row.get('public_supporting_evidence',[]):self.include(self.root/item['vendored_path'])
        return self.assets
    def write(self,out):
        out=Path(out)
        for name,pin in self.assets.items():
            raw=self.generated[name] if name in self.generated else (self.root/name).read_bytes()
            need(sha(raw)==pin['sha256'],'Site source changed during build')
            path=out/'bank'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        (out/'SITE_ASSETS.json').write_text(json.dumps({'schema':'bugbank-site-assets/v1','files':self.assets},sort_keys=True,indent=2)+'\n')

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src') and value:self.links.append(value)

def local_target(out,parent,url):
    if is_external(url):return None
    p=urlsplit(html.unescape(url));need(not p.path.startswith('/'),'Site link escapes project subpath')
    target=(Path(parent)/unquote(p.path)).resolve();need(target.is_relative_to(Path(out).resolve()),'Site link escapes project artifact')
    need(target.is_file(),'Missing deployed target: '+str(target));return target

def validate(root,out,entries,expected_assets):
    root,out=Path(root),Path(out)
    need((out/'index.html').is_file(),'Corrected release requires site/index.html')
    manifest=json.loads((out/'SITE_ASSETS.json').read_text())
    need(manifest.get('files')==expected_assets,'Site asset inventory is stale')
    for name,pin in expected_assets.items():
        target=out/'bank'/name
        need(target.is_file() and sha(target.read_bytes())==pin['sha256'],'Missing or stale deployed asset: '+name)
    for entry in entries:
        for match in MD_LINK.finditer(entry['body']):local_target(out,out,match['target'].strip('<>'))
        for match in HTML_LINK.finditer(entry['body']):local_target(out,out,match['target'])
        for target in entry['formalized']:local_target(out,out,target)
    for name in expected_assets:
        if not name.endswith('.html'):continue
        path=out/'bank'/name;parser=Links();parser.feed(path.read_text())
        for target in parser.links:local_target(out,path.parent,target)
