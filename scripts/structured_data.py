"""Single owner of the site's JSON-LD. Run after any page generator:

    python3 scripts/structured_data.py          # rewrite every page
    python3 scripts/structured_data.py --check  # report only, change nothing

Rules it enforces on every root page:
  * exactly one business entity, @id https://nextdigitalevel.com/#business,
    identical on every page so @id references resolve on the page itself;
  * no street address in it (owner's instruction, 2026-10-01; locality only);
  * every other node points at the business by @id only;
  * FAQPage is rebuilt from the FAQ the visitor can actually read, so the
    questions and answers match the visible text word for word;
  * every /marketing-agency-* page has a Service with the page's city
    (or Australia) as areaServed;
  * every indexable page except the homepage has a BreadcrumbList.
"""
from pathlib import Path
import html, json, re, sys

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://nextdigitalevel.com'
BUSINESS_ID = SITE + '/#business'
CITIES = [('Melbourne', 'Victoria'), ('Sydney', 'New South Wales'), ('Brisbane', 'Queensland'),
          ('Gold Coast', 'Queensland'), ('Perth', 'Western Australia'), ('Adelaide', 'South Australia')]

BUSINESS = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": BUSINESS_ID,
    "name": "Next Digital Level",
    "alternateName": "NDL",
    "url": SITE + "/",
    "logo": SITE + "/assets/logo-mark-512.png",
    "image": SITE + "/assets/social-preview.png",
    "description": ("Performance marketing agency for Australian businesses. Next Digital Level guarantees "
                    "eligible businesses a fixed monthly volume of calls, quote requests or bookings, "
                    "through Google Ads, local SEO and Meta advertising. Free audit, no lock-in contract."),
    "slogan": "Calls, quotes, bookings. For you alone.",
    "knowsAbout": ["Performance marketing", "Lead generation", "Google Ads", "Meta advertising",
                   "Local SEO", "SEO", "Web design", "Client acquisition"],
    "founder": {"@type": "Person", "name": "Amin Hamdi", "jobTitle": "Founder", "nationality": {"@type": "Country", "name": "Switzerland"}},
    "telephone": "+61 488 894 068",
    "email": "contact@nextdigitalevel.com",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "West Melbourne",
        "postalCode": "3003",
        "addressRegion": "VIC",
        "addressCountry": "AU",
    },
    "areaServed": [{"@type": "Country", "name": "Australia"}] + [{"@type": "City", "name": c} for c, _ in CITIES],
    "sameAs": [
        "https://www.instagram.com/nextdigitalevel/",
        "https://www.facebook.com/profile.php?id=61591099700363",
        "https://www.google.com/maps/place/?q=place_id:ChIJDxHjKQyWSAkRY9ludK1MBZE",
    ],
    "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "00:00", "closes": "23:59",
    },
    "knowsLanguage": ["en", "fr"],
    "contactPoint": {"@type": "ContactPoint", "telephone": "+61 488 894 068",
                     "contactType": "customer service", "availableLanguage": ["English", "French"]},
}

def city(name, state):
    return {"@type": "City", "name": name,
            "containedInPlace": {"@type": "AdministrativeArea", "name": state}}

# Performance-marketing city pages (scripts/build-cities-au.py)
PLACES = {'marketing-agency-australia': ('Australia', {"@type": "Country", "name": "Australia"}, 'Performance marketing')}
for _c, _s in CITIES:
    PLACES['marketing-agency-' + _c.lower().replace(' ', '-')] = (_c, city(_c, _s), 'Performance marketing')

# Breadcrumb names: the same labels the footer uses.
CRUMB_NAMES = {
    'websites': 'The offer',
    'advertising': 'Our channels',
    'book': 'Free audit',
    'reviews': 'Client reviews',
    'privacy': 'Privacy policy',
    'tradie-websites': 'Tradies & service businesses',
    'beauty-salon-websites': 'Salons & clinics',
    'ndis-provider-websites': 'NDIS experience in Australia',
    'web-design-melbourne': 'Our Australian experience',
    'website-cost-australia': 'Planning your project',
}
NO_CRUMB = {'index', '404'}

LD = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>\n?', re.S)
INLINE = re.compile(r'</?(?:a|b|strong|em|i|span|small|abbr|code)\b[^>]*>', re.I)
BLOCK = re.compile(r'<br\s*/?>|</?(?:p|div|li|ul|ol|h[1-6])\b[^>]*>', re.I)


def visible_text(fragment):
    """The text a reader sees: inline tags vanish, block tags become a space,
    entities are decoded (a non-breaking space stays one), and only the
    formatting whitespace of the source is collapsed."""
    t = BLOCK.sub(' ', INLINE.sub('', fragment))
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    return re.sub(r'[ \t\r\n]+', ' ', t).strip()


def visible_faq(page):
    out = []
    for m in re.finditer(r'<details class="faq-detail">(.*?)</details>', page, re.S):
        body = m.group(1)
        sm = re.search(r'<summary>(.*?)</summary>(.*)', body, re.S)
        if not sm:
            continue
        q = re.sub(r'<span aria-hidden="true">.*?</span>', '', sm.group(1), flags=re.S)
        out.append((visible_text(q), visible_text(sm.group(2))))
    return out


def render(obj):
    return '<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(obj, ensure_ascii=False, indent=1)


def process(path, check=False):
    page = path.read_text()
    slug = path.stem
    blocks, issues = [], []
    for m in LD.finditer(page):
        try:
            blocks.append((m.group(0), json.loads(m.group(1))))
        except ValueError:
            issues.append('invalid JSON-LD left untouched')
            blocks.append((m.group(0), None))

    kept = []
    for raw, d in blocks:
        if d is None:
            kept.append(raw); continue
        t = d.get('@type')
        if t == 'ProfessionalService':
            continue                                  # replaced by the canonical entity
        if t in ('FAQPage',):
            continue                                  # rebuilt from the visible FAQ
        if t == 'Service' and slug in PLACES:
            continue                                  # rebuilt from PLACES
        if t == 'BreadcrumbList':
            continue                                  # rebuilt below, in English
        if t == 'Service':
            d['provider'] = {"@id": BUSINESS_ID}
        if t == 'WebSite':
            d['publisher'] = {"@id": BUSINESS_ID}
        kept.append(render(d))

    new = [render(BUSINESS)]
    if slug in PLACES:
        label, area = PLACES[slug][:2]
        stype = PLACES[slug][2] if len(PLACES[slug]) > 2 else "Web design"
        new.append(render({"@context": "https://schema.org", "@type": "Service",
                           "serviceType": stype,
                           "name": stype + " in " + label,
                           "provider": {"@id": BUSINESS_ID},
                           "areaServed": area,
                           "url": "%s/%s" % (SITE, slug)}))
    faq = visible_faq(page)
    if faq:
        new.append(render({"@context": "https://schema.org", "@type": "FAQPage",
                           "mainEntity": [{"@type": "Question", "name": q,
                                           "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}))
    if slug not in NO_CRUMB:
        name = CRUMB_NAMES.get(slug) or html.unescape(re.search(r'<title>(.*?)</title>', page).group(1)).split(' | ')[0].split(' · ')[0]
        new.append(render({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": "%s/%s" % (SITE, slug)}]}))

    # Rebuild: drop every old JSON-LD block, put the full set back where the first one was.
    first = LD.search(page)
    stripped = LD.sub('', page)
    at = first.start() if first else stripped.index('</head>')
    out = stripped[:at] + ''.join(new + kept) + stripped[at:]
    out = out.replace(SITE + '/#organization', BUSINESS_ID)
    if not check and out != page:
        path.write_text(out)
    return out != page, faq, issues


def main():
    check = '--check' in sys.argv
    changed = []
    for path in sorted(ROOT.glob('*.html')):
        if 'http-equiv="refresh"' in path.read_text():
            continue                                  # redirect stubs to the English pages
        did, faq, issues = process(path, check)
        if did:
            changed.append(path.name)
        for i in issues:
            print('!', path.name, i)
    print(('would change' if check else 'changed'), len(changed), 'pages')
    return changed


if __name__ == '__main__':
    main()
