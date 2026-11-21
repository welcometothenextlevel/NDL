"""Client reviews: the one place they live.

Every review block on the site sits between markers such as
`<!-- reviews:home -->` and `<!-- /reviews:home -->`; this script rewrites
what is inside them on every root page, builds /reviews, then runs offer.py
and structured_data.py. A new review only ever needs adding here.

    python3 scripts/reviews.py

Texts are copied word for word from the Google Business Profile. Reviews
written in French are shown in an English translation (`en`), labelled
"Translated from French". No Review or AggregateRating markup: Google does
not show stars for reviews a business publishes about itself.
"""
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parent.parent

# Update these two when the profile changes. RATED counts every rating,
# including ones left without a comment (which have no card below).
RATING, RATED = '5.0', 12
SEE_URL = 'https://search.google.com/local/reviews?placeid=ChIJDxHjKQyWSAkRY9ludK1MBZE'
WRITE_URL = 'https://search.google.com/local/writereview?placeid=ChIJDxHjKQyWSAkRY9ludK1MBZE'

# Newest first. `tags` decide which page blocks quote the review.
# `show=False` keeps a review counted in RATED but off the site.
REVIEWS = [
    dict(name='Troy Petersen', date='October 2026', lang='en', tags={'speed', 'design'},
         text=['Excellent service. fast and prompt and would highly recommend to anyone looking for a website']),
    dict(name='Ahmet Hoti', date='October 2026', lang='fr', tags={'marketing', 'results'},
         en=['Very satisfied with his work! He built my website and ran advertising for my emergency plumbing business. Thanks to him, I gained visibility and got new clients. Very professional, serious and efficient. I recommend him 100%!'],
         text=['Très satisfait de son travail ! Il m’a créé mon site internet et fait de la publicité pour mon entreprise de dépannage sanitaire. Grâce à lui, j’ai gagné en visibilité et obtenu de nouveaux clients. Très professionnel, sérieux et efficace, je recommande à 100 % !']),
    # Char's Beauty Room, Melbourne (first card in the portfolio).
    dict(name='Charmayne Grech', date='October 2026', lang='en', tags={'design'}, company='Char’s Beauty Room · Altona Meadows, VIC', slug='charmayne-grech',
         text=['Next digital level, has been absoulty amazing, from the start designed a new website 2 weeks turnaround. One of best desinged websites I’ve had. Very proffessional service. Highy recommend thank you']),
    dict(name='Vaciraya Pechlak', date='October 2026', lang='en', tags={'marketing'},
         text=['I’m very satisfied with their digital marketing services. The team is professional, easy to communicate with, and committed to providing quality service. A great choice for businesses looking to improve their online presence!']),
    dict(name='Mehdi Meharga', date='October 2026', lang='fr', tags={'marketing'},
         en=['Very satisfied, I recommend them. Website and marketing service, top notch.'],
         text=['Très satisfait je recommande, site internet + service marketing au top']),
    dict(name='Kaelyb Douglas', date='October 2026', lang='fr', tags={'suivi'},
         en=['I recommend them. Very professional people who really look after their clients.'],
         text=['Je recommande personnel très professionnel et au petit soin avec ses clients']),
    dict(name='Melik Karatas', date='October 2026', lang='fr', tags={'lausanne', 'suivi'},
         en=['Best web design agency in Lausanne. Impeccable follow-up, quick replies, nothing to fault!'],
         text=['Meilleure agence de création de site sur Lausanne, y’a un suivi impeccable, réponse rapide, rien à dire !']),
    dict(name='Omar Silva', date='October 2026', lang='fr', tags={'lausanne', 'results'},
         en=['I had another website before that cost me a fortune, didn’t display properly on phones, and in 4 years brought me 3 or 4 calls.', 'The Next Digital Level team built the site in less than a week, and after 3 weeks I already have clients coming from it.', 'They’re the best for website design in Lausanne.', 'Thank you Amin'],
         text=['J’avais un autre site avant que j’ai payé une fortune qui s’affichait pas bien sur téléphone et sur 4 ans j’ai eu 3-4 appels provenant du site.',
               'L’équipe de next digital level a fait le site en moins d’une semaine et après 3 semaines j’ai déjà des clients provenant du site.',
               'C’est les meilleures en terme de création de site internet à Lausanne.',
               'Merci Amin']),
    dict(name='Osman Konut', date='October 2026', lang='fr', tags={'speed'},
         en=['The speed and the quality of the work really impressed me. I truly recommend this service! Thank you so much for working with us!'],
         text=['La rapidité d’exécution et la qualité du travail m’ont vraiment agréablement surpris. Je recommande vraiment ce service! Merci beaucoup pour notre collaboration!!']),
    dict(name='Youssef Baraka', date='October 2026', lang='fr', tags={'lausanne', 'suivi', 'speed'},
         en=['The best web design agency in Lausanne!', 'They’re available Monday to Sunday and the site was done in 5 days! Huge thanks to the founder.'],
         text=['La meilleure agence de création de site internet a lausanne !',
               'Ils sont disponibles du lundi au dimanche et le site a été bouclé en 5 jours ! Grand merci au fondateur']),
    # Shown on the profile as the signed-in owner's own review, so it stays
    # off the site until confirmed to be an independent client's.
    dict(name='Bruce', date='October 2026', lang='fr', tags=set(), show=False,
         en=['Exceptional work, a tireless team that never sleeps! Every question or concern, they are there at any hour to answer and help. The best website builders in Lausanne. I can only recommend them, especially Amin the founder! I have known him since his beginnings and nothing fazes him, even the most technical sites! This is not my first project with them. True champions. Thanks a thousand times. Bruce C.'],
         text=['Travail exceptionnel, une équipe acharnée qui ne dort pas ! Chaque question préoccupation, ils sont là à toute heure pour répondre et aider. Les meilleurs créateurs de site internet de Lausanne, je ne peux que les recommander, spécialement Amin le fondateur ! Je le connais depuis ses débuts et rien ne lui fait froid aux yeux, même les sites les plus techniques ! J\'en suis pas à mon coup d\'essai avec eux. Vraiment des champions. Merci 1000 fois. Bruce C.']),
]
SHOWN = [r for r in REVIEWS if r.get('show', True)]

NE = '<svg class="ico" viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M4 12 12 4M6 4h6v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
STARS = '<span class="rv-stars" role="img" aria-label="5 stars out of 5">' + '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.8l2.5 5.3 5.8.7-4.3 4 1.1 5.7L10 14.7l-5.1 2.8 1.1-5.7-4.3-4 5.8-.7z"/></svg>' * 5 + '</span>'
G = ('<svg class="rv-g" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
     '<path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5a5.6 5.6 0 0 1-2.4 3.6v3h3.9c2.3-2.1 3.5-5.2 3.5-8.8z"/>'
     '<path fill="#34A853" d="M12 24c3.2 0 6-1.1 7.9-2.9l-3.9-3c-1.1.7-2.4 1.2-4 1.2-3.1 0-5.7-2.1-6.7-4.9h-4v3.1A12 12 0 0 0 12 24z"/>'
     '<path fill="#FBBC05" d="M5.3 14.4a7.2 7.2 0 0 1 0-4.7V6.6h-4a12 12 0 0 0 0 10.8z"/>'
     '<path fill="#EA4335" d="M12 4.8c1.8 0 3.3.6 4.6 1.8l3.4-3.4A12 12 0 0 0 1.3 6.6l4 3.1C6.3 6.9 8.9 4.8 12 4.8z"/></svg>')
EXT = ' target="_blank" rel="noopener noreferrer"'


def card(r, anchor=False):
    paras = r.get('en') or r['text']
    body = ''.join('<p>%s</p>' % html.escape(p, quote=False) for p in paras)
    note = ' · Translated from French' if r.get('en') else ''
    # /reviews gives a card an id when something links to it (the portfolio does).
    ident = f' id="{r["slug"]}"' if anchor and r.get('slug') else ''
    return (f'<figure class="rv-card"{ident}>'
            f'<div class="rv-card__top">{STARS}{G}</div>'
            f'<blockquote class="rv-card__text">{body}</blockquote>'
            f'<figcaption><span class="rv-avatar" aria-hidden="true">{html.escape(r["name"][0])}</span>'
            f'<span class="rv-who"><b>{html.escape(r["name"])}</b>'
            + (f'<span class="rv-co">{html.escape(r["company"])}</span>' if r.get('company') else '')
            + f'<small>Google review · {r["date"]}{note}</small></span></figcaption>'
            '</figure>')


def score(cls=''):
    return (f'<a class="rv-score {cls}" href="/reviews">{STARS}<b>{RATING}</b>'
            f'<span>{RATED} Google reviews</span></a>')


def buttons(all_link=True):
    out = '<div class="rv-actions">'
    if all_link:
        out += f'<a class="btn btn--primary" href="/reviews">Read all our reviews{NE}</a>'
    out += f'<a class="btn btn--ghost" href="{SEE_URL}"{EXT}>See our reviews on Google{NE}</a>'
    out += f'<a class="btn btn--ghost" href="{WRITE_URL}"{EXT}>Leave a review{NE}</a>'
    return out + '</div>'


PREV = '<svg class="ico" viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M13 8H3M7 4 3 8l4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
NEXT = '<svg class="ico" viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def rail(items, label='Client reviews'):
    return (f'<div class="rv-viewport" data-reviews-rail tabindex="0" aria-label="{label}"><div class="rv-rail">'
            + ''.join(card(r) for r in items) + '</div></div>'
            f'<div class="rv-controls"><button class="rbtn" type="button" data-rv-prev aria-label="Previous review">{PREV}</button>'
            f'<button class="rbtn" type="button" data-rv-next aria-label="Next review">{NEXT}</button>'
            '<span class="work__hint">Scroll through the reviews</span></div>')


def section(eyebrow, title, sub, items, soft=False, all_link=True, sid=''):
    return (f'<section class="section reviews{" section--soft" if soft else ""}"{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}>\n'
            '<div class="container">\n'
            '<div class="reviews__head">\n'
            f'<div class="sec-head reveal"><span class="eyebrow">{eyebrow}</span><h2 class="t-display-lg" data-split="words">{title}</h2><p class="t-body">{sub}</p></div>\n'
            f'<div class="rv-summary reveal"><b class="rv-summary__n">{RATING}</b>{STARS}<span>{RATED} reviews on Google</span></div>\n'
            '</div>\n'
            f'{rail(items)}\n'
            f'{buttons(all_link)}\n'
            '</div>\n'
            '</section>')


def pick(*tags):
    return [r for r in SHOWN if r['tags'] & set(tags)] if tags else SHOWN


BLOCKS = {
    'score': lambda: score(),
    'home': lambda: section('/ Client reviews', 'What our clients<br><em>say.</em>',
                            'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick(), sid='client-reviews'),
    'websites': lambda: section('/ Client reviews', 'They weren’t getting many enquiries.<br><em>Here is what they say.</em>',
                                'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick(), soft=True),
    'lausanne': lambda: section('/ Reviews', 'They trusted us<br><em>with their business.</em>',
                                'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick('lausanne', 'speed')),
    'marketing': lambda: section('/ Client reviews', 'Website and marketing,<br><em>on the same side.</em>',
                                 'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick('marketing', 'results')),
    'all': lambda: section('/ Client reviews', 'What our clients<br><em>say.</em>',
                           'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick()),
    'book': lambda: section('/ Client reviews', 'They started<br><em>exactly where you are.</em>',
                            'The audit, the page, then the enquiries. Here is what they say about it on Google.', pick()),
    'suivi': lambda: section('/ Client reviews', 'Available,<br><em>and it shows.</em>',
                             'Reviews left on our Google Business Profile. Those written in French are shown in English.', pick('suivi', 'speed')),
}


def reviews_page():
    base = (ROOT / 'websites.html').read_text()
    head = base[:base.index('<main id="main">') + len('<main id="main">')]
    foot = base[base.index('</main>'):]
    title = 'Client reviews | Next Digital Level'
    desc = f'Rated {RATING} out of 5 on Google: what our clients say about their website and marketing. Read the reviews or leave your own.'
    head = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head)
    for pat, val in [(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc, quote=True)}">'),
                     (r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://nextdigitalevel.com/reviews">'),
                     (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Client reviews">'),
                     (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc, quote=True)}">'),
                     (r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://nextdigitalevel.com/reviews">'),
                     (r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="Client reviews">'),
                     (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">')]:
        head = re.sub(pat, val, head)
    grid = ''.join(card(r, anchor=True) for r in SHOWN)
    main = f'''
<section class="hero inner-hero rv-hero">
<div class="hero__aura" aria-hidden="true"></div>
<div class="container hero__inner">
<span class="eyebrow">/ Client reviews</span><h1 class="t-display-xl hero__title">Our clients<br><em>say it better than we do.</em></h1>
<p class="t-body-lg hero__lead">Many mention Amin, the founder: he is the one who answers you, with no middleman, from the first message to launch day.</p>
<p class="t-body hero__lead">Every review below was left by a client on our Google Business Profile. Reviews written in French are shown in English translation; you can read every original on Google.</p>
<div class="rv-hero__score"><b class="rv-summary__n">{RATING}</b><div>{STARS}<span>{RATED} reviews on Google</span></div></div>
{buttons(all_link=False)}
</div>
</section>
<section class="section">
<div class="container">
<div class="rv-grid stagger">{grid}</div>
<p class="rv-note">Ratings left without a comment count towards the average but are not shown here.</p>
</div>
</section>
<section class="section section--soft">
<div class="container rv-ask reveal">
<span class="eyebrow">/ Are you a client?</span>
<h2 class="t-display-lg" data-split="words">Your review counts<br><em>more than our advertising.</em></h2>
<p class="t-body-lg">A few lines help another business choose with confidence. It takes a minute, and we read every one.</p>
<a class="btn btn--primary btn--lg" href="{WRITE_URL}"{EXT}>Leave a review on Google{NE}</a>
</div>
</section>
<section class="cta-band" data-dots-region>
<canvas class="dot-canvas dot-canvas--dark" data-dots data-dots-theme="dark" aria-hidden="true"></canvas>
<div class="container cta-band__inner reveal">
<span class="eyebrow">/ Shall we start?</span><h2 class="t-display-lg" data-split="words">Your business, the next review.<br><em>Let’s start with the audit.</em></h2><p class="t-body-lg">Tell us about your business. We start with a free audit of your market, with no lock-in contract.</p>
<div class="hero__actions">
<a class="btn btn--gold btn--lg" href="/book">Request my free audit{NE}</a><a class="btn btn--onpanel btn--lg" href="https://wa.me/61488894068">Chat on WhatsApp{NE}</a>
</div>
</div>
</section>
'''
    (ROOT / 'reviews.html').write_text(head + main + foot)


MARK = re.compile(r'<!-- reviews:(\w+) -->.*?<!-- /reviews:\1 -->', re.S)


def inject():
    for f in sorted(ROOT.glob('*.html')):
        src = f.read_text()
        out = MARK.sub(lambda m: f'<!-- reviews:{m[1]} -->{BLOCKS[m[1]]()}<!-- /reviews:{m[1]} -->', src)
        if out != src:
            f.write_text(out)


if __name__ == '__main__':
    reviews_page()
    inject()
    sys_path = str(ROOT / 'scripts')
    import sys as _sys
    if sys_path not in _sys.path: _sys.path.insert(0, sys_path)
    import offer
    offer.run()
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'structured_data.py')], check=True)
