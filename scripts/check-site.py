"""Dependency-free checks for nextdigitalevel.com (static, GitHub Pages).

    python3 scripts/check-site.py

The site is one English page for Australia (index.html) plus redirect stubs
that keep the old French URLs landing on the home page, the unlisted
owner/ statement and the 404 page.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re

ROOT = Path(__file__).resolve().parent.parent
WA = '/61488894068'
OLD_NUMBERS = r'61425887683|61488896075|488 896 075|41762632817|76 263 28 17'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.h1, self.lang = path, set(), [], 0, None
        self.jsonld, self.buffer = False, ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if a.get('id'):
            assert a['id'] not in self.ids, f'{self.path}: duplicate id {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'img': assert 'alt' in a, f'{self.path}: image without alt'
        for key in ('href', 'src', 'srcset'):
            if a.get(key):
                self.links += [u.strip().split(' ')[0] for u in a[key].split(',')] if key == 'srcset' else [a[key]]
        if tag == 'script' and a.get('type') == 'application/ld+json': self.jsonld, self.buffer = True, ''

    def handle_data(self, data):
        if self.jsonld: self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.jsonld: json.loads(self.buffer); self.jsonld = False


pages = {}
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts or 'notes' in path.parts: continue
    text = path.read_text(); page = Page(path.relative_to(ROOT)); page.feed(text)
    stub = 'http-equiv="refresh"' in text
    assert page.lang == ('en' if path.parent.name == 'owner' else 'en-AU'), f'{path}: wrong language'
    # owner/ is the visa ownership statement: it keeps the Swiss details on purpose.
    if path.parent.name != 'owner': assert not re.search(OLD_NUMBERS, text), f'{path}: old phone number'
    assert '—' not in text or stub or path.parent.name == 'owner', f'{path}: em dash in copy'
    if stub:
        assert 'url=/"' in text and 'noindex' in text, f'{path}: redirect stub must point at / and be noindex'
    elif path.name != '404.html' and path.parent.name != 'owner':
        assert page.h1 == 1, f'{path}: expected one h1'
        for token in ('rel="canonical"', 'property="og:title"', 'name="description"'):
            assert token in text, f'{path}: missing {token}'
    pages[path.resolve()] = page

for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if page.path.parent.name != 'owner':
            if url.scheme == 'tel': assert link == 'tel:+61488894068', f'{page.path}: wrong phone {link}'
            if url.netloc == 'wa.me': assert url.path == WA, f'{page.path}: wrong WhatsApp number {link}'
        if url.scheme or url.netloc or link.startswith('#') and not url.path:
            if url.fragment and not url.path and not url.scheme: assert unquote(url.fragment) in page.ids, f'{page.path}: missing #{url.fragment}'
            continue
        target = (ROOT / url.path.lstrip('/')) if url.path.startswith('/') else (path.parent / url.path)
        target = target.resolve()
        if target.is_dir(): target /= 'index.html'
        assert target.exists(), f'{page.path}: missing {link}'
        if url.fragment and target in pages: assert unquote(url.fragment) in pages[target].ids, f'{page.path}: missing {link}'

home = (ROOT / 'index.html').read_text()
for token in ('$499', 'wa.me/61488894068', 'Built before you pay', 'Rated 5 stars on Google'):
    assert token in home, f'home page lost: {token}'
assert not re.search(r'AggregateRating|"Review"', home), 'no rating or review markup'
print(f'PASS: {len(pages)} HTML pages; links, ids, language, phone numbers, redirects.')
