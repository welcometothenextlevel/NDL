"""The offer: client acquisition, priced after the free audit. The one place it lives.

Fills `<!-- offer:full -->` (who it is for, platforms vs us, price card) and
`<!-- offer:note -->` (one line, booking page) on every root page.
Run by scripts/reviews.py, so every page generator picks it up.
No public price: the free audit sets it.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

NE = '<svg class="ico" viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M4 12 12 4M6 4h6v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
TICK = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" aria-hidden="true"><path d="M3 8.5l3 3 7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

INCLUDED = [
    'Guaranteed monthly volume',
    'Free audit: the best channel for you',
    'Google Ads, local SEO or Meta',
    'Ad budget included (Google Ads, Meta)',
    'A website or page that converts, included',
    'Calls, quotes and bookings tracked',
    'A clear report every month',
    'One contact, 7 days a week',
]


def full():
    items = ''.join(f'<li>{TICK}<span>{t}</span></li>' for t in INCLUDED)
    return f'''<section class="section offer-sec" id="offer">
<div class="container">
<div class="offer">
<div class="offer__copy reveal">
<span class="eyebrow">/ The offer</span>
<h2 class="t-display-lg" data-split="words">Enquiries, not clicks.<br><em>And yours alone.</em></h2>
<p class="t-body-lg">You live on word of mouth, your calls come in waves, or you have already paid for “leads” that went nowhere. We set up the channel that brings you steady calls and enquiries, and we run it every month.</p>
<div class="vs">
<div class="vs__col"><span class="vs__who">Lead platforms</span><b>Shared enquiries</b><b>12-month contracts</b><span class="vs__extra">The same enquiry sold to several competitors</span></div>
<div class="vs__col vs__col--us"><span class="vs__who">Next Digital Level</span><b>Exclusive calls</b><b>No lock-in contract</b><span class="vs__extra">Every call comes from your campaigns, for you alone</span></div>
</div>
<p class="t-body">Each channel is a separate service. It all starts with a free audit: we study your trade, your area and your competitors, then tell you which channel will pay off most.</p>
</div>
<div class="price-card reveal">
<div class="price-card__top"><span class="eyebrow">One channel · per month</span><span class="price-card__tag">No lock-in contract</span></div>
<div class="price price--text"><b>Tailored</b><span>set in the free audit</span></div>
<p class="price__sub">The channel chosen in the audit, run for you. Cancel any month.</p>
<ul class="price__list">{items}</ul>
<p class="price__zero"><b>Exclusive calls and enquiries</b> <i aria-hidden="true">·</i> <b>No lock-in</b></p>
<a class="btn btn--gold btn--lg" href="/book">Request my free audit{NE}</a>
</div>
</div>
<p class="offer__fine">The price and the guaranteed monthly volume depend on the channel, your trade and your area: the free audit sets them before you commit, for eligible businesses.</p>
</div>
</section>'''


def note():
    return ('<p class="offer-note-line"><b>Free audit</b>, then a price set for your trade and your area. '
            'Each channel is a separate service. No lock-in contract.</p>')


BLOCKS = {'full': full, 'note': note, 'promo': lambda: ''}
MARK = re.compile(r'<!-- offer:(\w+) -->.*?<!-- /offer:\1 -->', re.S)


def run():
    for f in sorted(ROOT.glob('*.html')):
        src = f.read_text()
        out = MARK.sub(lambda m: f'<!-- offer:{m[1]} -->{BLOCKS[m[1]]()}<!-- /offer:{m[1]} -->', src)
        if out != src:
            f.write_text(out)


if __name__ == '__main__':
    run()
