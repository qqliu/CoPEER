#!/usr/bin/env python3
"""Static checks of the website in docs/: HTML parses; every local href/src/url() target exists with docs/ as the
deployment root; every fragment link points at an existing id; no link escapes docs/; scripts pass `node --check`;
no email addresses in the site's own text files. Usage: check_site.py [docs_dir]
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

docs = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'docs').resolve()
errors, warnings = [], []
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(edu|com|org|net|io)\b')


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.stack, self.title = set(), [], [], None
        self.has_lang = self.has_viewport = self.has_charset = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: errors.append('duplicate id #%s at line %d' % (a['id'], self.getpos()[0]))
            self.ids.add(a['id'])
        if tag == 'html' and a.get('lang'): self.has_lang = True
        if tag == 'meta' and a.get('name') == 'viewport': self.has_viewport = True
        if tag == 'meta' and 'charset' in a: self.has_charset = True
        for k in ('href', 'src', 'data', 'poster'):
            if k in a and a[k]: self.links.append((tag, k, a[k], self.getpos()[0]))
        if tag == 'img' and not a.get('alt') and a.get('alt') != '': warnings.append('img without alt at line %d' % self.getpos()[0])
        if tag == 'a' and a.get('target') == '_blank' and 'noopener' not in (a.get('rel') or ''): warnings.append('target=_blank without rel=noopener at line %d' % self.getpos()[0])
    def handle_data(self, d):
        pass


pages = sorted(docs.rglob('*.html'))
ids_by_page = {}
parsed = {}
for page in pages:
    p = P(); text = page.read_text(encoding='utf-8')
    try:
        p.feed(text)
    except Exception as e:  # pragma: no cover
        errors.append('%s: HTML parse error %s' % (page.name, e))
    parsed[page] = p
    ids_by_page[page] = p.ids
    if not p.has_lang: errors.append('%s: <html> without lang' % page.relative_to(docs))
    if not p.has_viewport: errors.append('%s: no viewport meta' % page.relative_to(docs))
    if not p.has_charset: errors.append('%s: no charset meta' % page.relative_to(docs))
    if '<title>' not in text: errors.append('%s: no <title>' % page.relative_to(docs))
    if EMAIL.search(text): errors.append('%s: email address in page text' % page.relative_to(docs))

for page, p in parsed.items():
    for tag, k, url, line in p.links:
        u = urlparse(url)
        if u.scheme in ('http', 'https', 'mailto', 'data', 'javascript'):
            if u.scheme == 'mailto': errors.append('%s:%d mailto link' % (page.relative_to(docs), line))
            continue
        if url.startswith('#'):
            if url != '#' and url[1:] not in p.ids: errors.append('%s:%d fragment #%s not found' % (page.relative_to(docs), line, url[1:]))
            continue
        path = unquote(u.path)
        if path.startswith('/'):
            errors.append('%s:%d absolute path %s (breaks subpath deployment)' % (page.relative_to(docs), line, url)); continue
        target = (page.parent / path).resolve() if path else page
        try:
            target.relative_to(docs)
        except ValueError:
            errors.append('%s:%d link escapes docs/: %s' % (page.relative_to(docs), line, url)); continue
        if not target.exists(): errors.append('%s:%d missing target %s' % (page.relative_to(docs), line, url)); continue
        if u.fragment and target.suffix == '.html' and target in ids_by_page and u.fragment not in ids_by_page[target]:
            errors.append('%s:%d fragment %s not in %s' % (page.relative_to(docs), line, u.fragment, target.relative_to(docs)))

for css in sorted(docs.rglob('*.css')):
    txt = css.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', txt):
        ref = m.group(1)
        if ref.startswith(('data:', 'http', '#')): continue
        t = (css.parent / unquote(urlparse(ref).path)).resolve()
        if not t.exists():
            # KaTeX lists woff and ttf fallbacks that are intentionally not shipped
            if css.name == 'katex.min.css' and (ref.endswith('.woff') or ref.endswith('.ttf')): continue
            errors.append('%s: missing url() target %s' % (css.relative_to(docs), ref))

js_files = [p for p in docs.rglob('*.js') if 'katex' not in p.parts]
for js in js_files:
    r = subprocess.run(['node', '--check', str(js)], capture_output=True, text=True)
    if r.returncode != 0: errors.append('%s: node --check failed: %s' % (js.relative_to(docs), r.stderr.strip().splitlines()[-1] if r.stderr else ''))
    if 'tests' in js.parts or 'data' in js.parts: continue
    if EMAIL.search(js.read_text(encoding='utf-8', errors='replace')): errors.append('%s: email address in script' % js.relative_to(docs))

print('pages: %d, scripts checked: %d, errors: %d, warnings: %d' % (len(pages), len(js_files), len(errors), len(warnings)))
for e in errors: print('ERROR', e)
for w in warnings[:20]: print('WARN ', w)
sys.exit(1 if errors else 0)
