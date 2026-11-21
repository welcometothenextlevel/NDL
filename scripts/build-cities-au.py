"""Performance-marketing city pages for Australia: one per major city plus the
Australia hub. They target "marketing agency <city>", "Google Ads agency
<city>" and "lead generation <city>".

Run `python3 scripts/build-cities-au.py` after editing PAGES. Chrome (head,
header, footer) comes from websites.html; JSON-LD, reviews and the offer
blocks are filled by scripts/reviews.py, which this script runs at the end.
"""
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parent.parent
BASE = (ROOT / 'websites.html').read_text()
HEAD = BASE[:BASE.index('<main id="main">') + len('<main id="main">')]
FOOT = BASE[BASE.index('</main>'):]
NE = '<svg class="ico" viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M4 12 12 4M6 4h6v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

GUARANTEE = ('A volume of calls, quote requests or bookings guaranteed every month, '
             'set with you after the free audit, if your business is eligible.')

PAGES = [
    dict(slug='marketing-agency-melbourne', place='Melbourne', short='Melbourne', code='VIC',
         title='Marketing agency in Melbourne: guaranteed calls and quotes | Next Digital Level',
         desc='Performance marketing agency in Melbourne: Google Ads, local SEO and Meta. A guaranteed volume of calls and quote requests every month. Free audit.',
         h1='Marketing agency<br><em>in Melbourne.</em>',
         lead='From the CBD to the outer suburbs, Melbourne’s established businesses can’t rely on word of mouth alone. We bring you a steady flow of calls, quote requests and bookings, and we guarantee the volume every month for eligible businesses.',
         sectors=[('Construction and renovation', 'Builders, renovators, electricians and plumbers: quote requests from homeowners and businesses in the suburbs you actually service.'),
                  ('Health and allied health', 'Clinics, physios, dentists and specialists: patients who search for a practitioner nearby and book directly, without a booking platform in between.'),
                  ('Professional services', 'Accountants, lawyers, consultants: qualified enquiries from businesses and families, not tyre-kickers.')],
         local='Melbourne is a city of suburbs. People search “electrician Brunswick” or “dentist Glen Waverley”, not just “Melbourne”. We build your campaigns around the suburbs you service and track every call back to its source.',
         towns='the Melbourne CBD, Richmond, South Yarra, St Kilda, Brunswick, Footscray, Box Hill, Glen Waverley, Dandenong, Frankston, Werribee and Geelong',
         faq=[('Do you cover all of Melbourne?', 'Yes. We set your campaigns to the suburbs and the radius you actually service, from the inner city to the outer growth areas.'),
              ('Can my ads show only in the suburbs I service?', 'Yes. Ads can be limited to a list of suburbs or to a radius around your base, so you never pay for clicks from people you can’t serve.'),
              ('Do I need a new website?', 'Not necessarily. If your site already converts, we keep it; if not, we build the page and it’s included in the price.')]),
    dict(slug='marketing-agency-sydney', place='Sydney', short='Sydney', code='NSW',
         title='Marketing agency in Sydney: guaranteed calls and quotes | Next Digital Level',
         desc='Performance marketing agency in Sydney: Google Ads, local SEO and Meta. A guaranteed volume of calls, quotes and bookings every month. Free audit.',
         h1='Marketing agency<br><em>in Sydney.</em>',
         lead='Sydney is one of the most competitive online markets in the country, and every click costs more. We turn that budget into calls and enquiries you can count, and we guarantee the monthly volume for eligible businesses.',
         sectors=[('Trades and home services', 'Plumbers, electricians, builders, cleaners: quote requests from homeowners across the suburbs you cover.'),
                  ('Property and real estate', 'Sales, rentals, property management: qualified owners and investors, not idle browsers.'),
                  ('Health, beauty and wellbeing', 'Clinics, salons and studios: bookings straight into your diary.')],
         local='In Sydney, a campaign that targets the whole city wastes money. We concentrate your budget on the suburbs and the searches that actually turn into jobs, from the Northern Beaches to Western Sydney.',
         towns='the Sydney CBD, Parramatta, North Sydney, Chatswood, Bondi, the Northern Beaches, Liverpool, Penrith, Blacktown and Sutherland',
         faq=[('Is Google Ads more expensive in Sydney?', 'Competition is stronger than in most of Australia. That is why the free audit sets the right channel and the right budget before you commit.'),
              ('Can you target Western Sydney only?', 'Yes. Campaigns can be limited to specific suburbs or regions, so your budget goes where your clients are.'),
              ('Are the enquiries shared with other businesses?', 'No. Every enquiry comes from your own campaigns and reaches you alone. Nothing is resold.')]),
    dict(slug='marketing-agency-brisbane', place='Brisbane', short='Brisbane', code='QLD',
         title='Marketing agency in Brisbane: guaranteed calls and quotes | Next Digital Level',
         desc='Performance marketing agency in Brisbane: Google Ads, local SEO and Meta. A guaranteed volume of calls and quote requests every month. Free audit.',
         h1='Marketing agency<br><em>in Brisbane.</em>',
         lead='Brisbane is growing fast, and so is the competition for every local search. We bring Brisbane businesses a steady flow of calls, quote requests and bookings, with the volume guaranteed every month for eligible businesses.',
         sectors=[('Construction and trades', 'Builders, roofers, landscapers and renovators: quote requests from a city that keeps building.'),
                  ('Property', 'Developers, agents and property managers: qualified buyers, sellers and landlords.'),
                  ('Health and services', 'Clinics, practices and service businesses: appointments and bookings direct.')],
         local='From the inner suburbs to Logan, Ipswich and Moreton Bay, Brisbane clients search by suburb and by trade. We build campaigns around the areas you service and follow every enquiry back to its source.',
         towns='the Brisbane CBD, Fortitude Valley, South Brisbane, Chermside, Carindale, North Lakes, Springfield, Ipswich, Logan and Redcliffe',
         faq=[('Do you cover Logan, Ipswich and Moreton Bay?', 'Yes. We target the exact suburbs and regions you service, inside or outside the city.'),
              ('How soon do the first calls arrive?', 'Often in the first few days. Allow a few weeks for the campaign to settle; the monthly volume is guaranteed for eligible businesses.'),
              ('Do I need a new website?', 'Not necessarily. If your site already converts, we keep it; if not, we build the page and it’s included in the price.')]),
    dict(slug='marketing-agency-gold-coast', place='the Gold Coast', short='the Gold Coast', code='QLD',
         title='Marketing agency on the Gold Coast: guaranteed calls and bookings | Next Digital Level',
         desc='Performance marketing agency on the Gold Coast: Google Ads, local SEO and Meta. A guaranteed volume of calls, quotes and bookings every month. Free audit.',
         h1='Marketing agency<br><em>on the Gold Coast.</em>',
         lead='Locals, new residents and visitors: Gold Coast businesses serve all three, and each one searches differently. We bring you calls, quote requests and bookings all year round, with the monthly volume guaranteed for eligible businesses.',
         sectors=[('Hospitality and tourism', 'Restaurants, tours and accommodation: bookings from visitors who search on their phone, often the same day.'),
                  ('Construction and renovation', 'Builders, pool companies and renovators: quote requests from a fast-growing region.'),
                  ('Health and beauty', 'Clinics, salons and studios: appointments straight into your diary.')],
         local='The Gold Coast moves with the seasons and the school holidays. We adjust your campaigns to the calendar and to the suburbs you serve, from the northern growth corridor to the border.',
         towns='Surfers Paradise, Southport, Broadbeach, Robina, Burleigh Heads, Coolangatta, Helensvale, Coomera, Nerang and Tweed Heads',
         faq=[('Can campaigns follow the holiday seasons?', 'Yes. We raise or lower the effort with the season, so you get bookings when you can take them.'),
              ('Can you reach visitors as well as locals?', 'Yes. Depending on your business, we target people searching nearby, people planning a trip, or both, and track each separately.'),
              ('Are the enquiries exclusive?', 'Yes. They come from your own ads and pages and reach you alone.')]),
    dict(slug='marketing-agency-perth', place='Perth', short='Perth', code='WA',
         title='Marketing agency in Perth: guaranteed calls and quotes | Next Digital Level',
         desc='Performance marketing agency in Perth: Google Ads, local SEO and Meta. A guaranteed volume of calls and quote requests every month. Free audit.',
         h1='Marketing agency<br><em>in Perth.</em>',
         lead='Perth businesses work in a market of their own, spread across a huge metro area. We bring you a steady flow of calls, quote requests and bookings from the suburbs you service, with the volume guaranteed every month for eligible businesses.',
         sectors=[('Trades and home services', 'Solar, air conditioning, building and maintenance: quote requests from homeowners across the metro area.'),
                  ('Industrial and B2B', 'Suppliers and service companies: enquiries from businesses and project managers.'),
                  ('Health and services', 'Clinics and practices: patients who book directly.')],
         local='Perth stretches from Joondalup to Mandurah. We set your campaigns to the areas you can actually reach in a working day and track every call back to its source.',
         towns='the Perth CBD, Fremantle, Subiaco, Scarborough, Joondalup, Midland, Cannington, Armadale, Rockingham and Mandurah',
         faq=[('Do you work in WA time?', 'Yes. Campaigns, reports and calls are set to Perth time, and you can reach us 7 days a week.'),
              ('Can my ads cover only part of the metro area?', 'Yes. We limit them to the suburbs or the radius you service.'),
              ('Do I need a new website?', 'Not necessarily. If your site already converts, we keep it; if not, we build the page and it’s included in the price.')]),
    dict(slug='marketing-agency-adelaide', place='Adelaide', short='Adelaide', code='SA',
         title='Marketing agency in Adelaide: guaranteed calls and quotes | Next Digital Level',
         desc='Performance marketing agency in Adelaide: Google Ads, local SEO and Meta. A guaranteed volume of calls and quote requests every month. Free audit.',
         h1='Marketing agency<br><em>in Adelaide.</em>',
         lead='In Adelaide, reputation travels fast, but word of mouth alone doesn’t fill a diary. We bring established Adelaide businesses a steady flow of calls, quote requests and bookings, with the volume guaranteed every month for eligible businesses.',
         sectors=[('Construction and trades', 'Builders, renovators and tradies: quote requests from homeowners in the suburbs you cover.'),
                  ('Health and allied health', 'Clinics and practices: patients who book directly.'),
                  ('Hospitality and wine regions', 'Restaurants, venues and cellar doors: bookings from locals and visitors.')],
         local='From Glenelg to the Adelaide Hills, clients search by suburb and by need. We build your campaigns around the areas you service and follow every enquiry back to its source.',
         towns='the Adelaide CBD, North Adelaide, Glenelg, Norwood, Unley, Prospect, Mawson Lakes, Salisbury, Marion and Mount Barker',
         faq=[('Do you cover the Adelaide Hills and the wine regions?', 'Yes. We target the suburbs, towns and regions you service.'),
              ('How is the monthly volume set?', 'After the free audit, based on your trade, your area and your capacity, for eligible businesses.'),
              ('Can I stop at any time?', 'Yes. The service is monthly, with no lock-in contract.')]),
]
HUB = dict(slug='marketing-agency-australia', place='Australia', short='Australia', code='AU',
           title='Performance marketing agency in Australia | Next Digital Level',
           desc='Performance marketing agency in Australia: a guaranteed volume of calls, quotes and bookings every month. Melbourne, Sydney, Brisbane, Gold Coast, Perth, Adelaide.',
           h1='Performance marketing agency<br><em>in Australia.</em>',
           lead='Next Digital Level is a Swiss company. We help established Australian businesses grow with a steady flow of calls, quote requests and bookings, and we guarantee the volume every month for eligible businesses.',
           sectors=[('Construction and property', 'Builders, renovators, developers and property managers: qualified quote requests and listings.'),
                    ('Health, hospitality and services', 'Clinics, practices, venues and professional firms: appointments and bookings direct.'),
                    ('Industry and B2B', 'Suppliers, manufacturers and service companies: enquiries from businesses that buy.')],
           local='Every city has its own searches, suburbs and seasons. We build campaigns around the areas you actually service and track every call and every enquiry back to its source, from Perth to the Gold Coast.',
           towns='Melbourne, Sydney, Brisbane, the Gold Coast, Perth, Adelaide and regional Australia',
           faq=[('What exactly do you guarantee?', 'A fixed number of calls, quote requests or bookings every month. We set it with you after the free audit, based on your trade, your area and your capacity, for eligible businesses.'),
                ('What is a performance marketing agency?', 'An agency paid for measurable results rather than visibility: calls, enquiries and bookings. Every dollar spent is linked to the enquiries it produced.'),
                ('Which channels do you use?', 'Google Ads, local SEO and Google Maps, and Meta advertising. Each channel is a separate service; the audit picks the one that will pay off most.')])
ALL = [HUB] + PAGES


def chrome(pg):
    head = HEAD
    head = re.sub(r'<title>.*?</title>', '<title>' + html.escape(pg['title']) + '</title>', head)
    short = html.escape(pg['title'].split(' | ')[0], quote=True)
    desc = html.escape(pg['desc'], quote=True)
    for pat, val in [(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">'),
                     (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://nextdigitalevel.com/{pg["slug"]}">'),
                     (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{short}">'),
                     (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">'),
                     (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="https://nextdigitalevel.com/{pg["slug"]}">'),
                     (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{short}">'),
                     (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{desc}">')]:
        head = re.sub(pat, val, head)
    return head


def page(pg):
    hub = pg is HUB
    cards = ''.join('<article class="card card--spot" data-spot><span class="card__num">%02d</span><h3 class="t-display-sm">%s</h3><p class="t-body">%s</p></article>' % (i + 1, t, b) for i, (t, b) in enumerate(pg['sectors']))
    faq = ''.join('<details class="faq-detail"><summary>%s<span aria-hidden="true">+</span></summary><p class="t-body">%s</p></details>' % (q, a) for q, a in pg['faq'])
    label = lambda o: o['place'][0].upper() + o['place'][1:]
    if hub:
        others = ''.join(f'<a href="/{o["slug"]}" data-cursor="view"><span><small>{o["code"]}</small>{label(o)}</span><span aria-hidden="true">{NE}</span></a>' for o in PAGES)
        others_title = 'Your city.'
    else:
        others = ''.join(f'<a href="/{o["slug"]}" data-cursor="view"><span><small>{o["code"]}</small>{label(o)}</span><span aria-hidden="true">{NE}</span></a>' for o in PAGES if o is not pg)
        others += f'<a href="/{HUB["slug"]}" data-cursor="view"><span><small>AU</small>All of Australia</span><span aria-hidden="true">{NE}</span></a>'
        others_title = 'Elsewhere in Australia.'
    main = f'''
<section class="hero inner-hero agency-hero">
<div class="hero__aura" aria-hidden="true"></div>
<div class="container hero__inner">
<span class="eyebrow">/ Performance marketing agency · {label(pg)}</span><h1 class="t-display-xl hero__title">{pg['h1']}</h1><p class="t-body-lg hero__lead">{pg['lead']}</p>
<div class="hero__actions">
<a class="btn btn--primary btn--lg" href="/book">Request my free audit{NE}</a><a class="btn btn--ghost btn--lg" href="tel:+61488894068">Call +61 488 894 068{NE}</a>
</div>
<p class="hero__note">Swiss company · no middleman · guaranteed monthly volume · no lock-in contract</p>
</div>
</section>
<section class="section">
<div class="container">
<div class="included">
<div class="included__copy reveal">
<span class="eyebrow">/ Our guarantee</span>
<h2 class="t-display-lg" data-split="words">A volume of enquiries<br><em>guaranteed, every month.</em></h2>
<p class="t-body-lg">{GUARANTEE}</p>
<a class="btn btn--ghost btn--lg" href="/websites">See the full offer{NE}</a>
</div>
<ul class="included__list included__list--simple stagger">
<li><i></i><b>Guaranteed monthly volume</b><span>Calls, quote requests or bookings</span></li>
<li><i></i><b>Exclusive enquiries</b><span>They reach you alone, never resold</span></li>
<li><i></i><b>The right channel</b><span>Chosen by the free audit for your trade</span></li>
<li><i></i><b>Ad budget included</b><span>On Google Ads and Meta, in the monthly price</span></li>
<li><i></i><b>Monthly report</b><span>Every call linked to its source</span></li>
<li><i></i><b>No lock-in contract</b><span>Cancel any month</span></li>
</ul>
</div>
</div>
</section>
<section class="section section--soft">
<div class="container">
<div class="sec-head reveal">
<span class="eyebrow">/ Who we work with in {pg['short']}</span><h2 class="t-display-lg" data-split="words">Established businesses<br>in {pg['place']}.</h2>
<p class="t-body">We work with businesses in {pg['towns']}.</p>
</div>
<div class="grid grid--3 stagger">{cards}</div>
</div>
</section>
<section class="section">
<div class="container">
<div class="included">
<div class="included__copy reveal">
<span class="eyebrow">/ Local demand</span>
<h2 class="t-display-lg" data-split="words">Where your clients<br><em>are searching.</em></h2>
<p class="t-body-lg">{pg['local']}</p>
</div>
<div class="sector-links reveal">
<a href="/google-ads" data-cursor="view"><span><small>01</small>Google Ads</span><span aria-hidden="true">{NE}</span></a>
<a href="/local-seo" data-cursor="view"><span><small>02</small>Local SEO and Google Maps</span><span aria-hidden="true">{NE}</span></a>
<a href="/meta-ads" data-cursor="view"><span><small>03</small>Meta advertising</span><span aria-hidden="true">{NE}</span></a>
<a href="/websites" data-cursor="view"><span><small>Site</small>Your website, included</span><span aria-hidden="true">{NE}</span></a>
</div>
</div>
</div>
</section>
<section class="section section--soft">
<div class="container">
<div class="faq-layout">
<div class="sec-head reveal">
<span class="eyebrow">/ Your questions</span><h2 class="t-display-lg" data-split="words">Frequently asked questions<br>in {pg['short']}.</h2>
<p class="t-body faq-aside">Another question? The assistant at the bottom of the page answers straight away, or message us on WhatsApp.</p>
</div>
<div class="faq reveal">{faq}</div>
</div>
</div>
</section>
<!-- reviews:all --><!-- /reviews:all -->
<section class="section">
<div class="container">
<div class="sec-head reveal">
<span class="eyebrow">/ Australia</span><h2 class="t-display-lg" data-split="words">{others_title}</h2>
</div>
<div class="sector-links reveal">{others}</div>
</div>
</section>
<section class="cta-band" data-dots-region>
<canvas class="dot-canvas dot-canvas--dark" data-dots data-dots-theme="dark" aria-hidden="true"></canvas>
<div class="container cta-band__inner reveal">
<span class="eyebrow">/ Shall we start?</span><h2 class="t-display-lg" data-split="words">Calls in {pg['short']}.<br><em>Let’s start with the audit.</em></h2><p class="t-body-lg">Tell us about your business. We start with a free audit of your market, with no lock-in contract.</p>
<div class="hero__actions">
<a class="btn btn--gold btn--lg" href="/book">Request my free audit{NE}</a><a class="btn btn--onpanel btn--lg" href="https://wa.me/61488894068">Chat on WhatsApp{NE}</a>
</div>
</div>
</section>
'''
    return chrome(pg) + main + FOOT


for pg in ALL:
    (ROOT / (pg['slug'] + '.html')).write_text(page(pg))
    print('wrote', pg['slug'])

import subprocess as _sp, sys as _sys
_sp.run([_sys.executable, str(ROOT / 'scripts' / 'reviews.py')], check=True)
