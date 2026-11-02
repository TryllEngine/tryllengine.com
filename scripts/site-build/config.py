"""Everything the design export doesn't know: SEO copy, link targets, forms.

Edit this file, then run  py -3 scripts/site-build/build.py
"""

SITE = 'https://tryllengine.com'
GTM_ID = 'GTM-K8MPGKVX'            # contains GA4 G-V0BH3P7R63 + form/download events
OG_IMAGE = '/assets/images/og-image.png'

# Forms — the same endpoints the old site used, so submissions keep landing
# in the same Formspree inbox and MailerLite group.
FORMS = {'contact': 'https://formspree.io/f/movlaywd'}
MAILERLITE_ACCOUNT = '2274886'
MAILERLITE_FORM = '185451758358627764'   # "blog" signup form

DISCORD = 'https://discord.gg/DTKycjPpzs'
YOUTUBE = 'https://www.youtube.com/@Tryll_Engine'
LINKEDIN = 'https://www.linkedin.com/company/tryllengine/'
DOCS = 'https://docs.tryllengine.com/'
DOCS_V = 'https://docs.tryllengine.com/v0.9/'   # bump with each docs release

# Until the plugin and the demo game can be downloaded, every download and
# "Get Tryll Engine" button says "Coming soon" and leads to the newsletter
# signup, and the demo's store buttons are hidden. On launch day: fill in the
# TODO download links below and set this to True. preview.py always builds
# with downloads on, as designed.
DOWNLOADS_LIVE = False
COMING_SOON = {
    'nav': 'Coming soon',                  # nav and mobile-menu button
    'cta': 'Coming soon · Get notified',   # big buttons
    'href': '/blog#subscribe',
}

# "How to build" video lists (homepage and /download), keyed by the list's
# heading in the design: the YouTube playlist behind "Watch on YouTube", then
# one (video id, length, title) per card. The build saves each thumbnail to
# assets/images/videos/ the first time it sees a video.
VIDEO_LISTS = {
    'Dev talks': ('PLKAJH9fZXZys', [
        ('e4djfzmjy3w', '7:32', 'Guardrails, VRAM optimization and voice control'),
        ('_yAfJ3A2lNk', '7:26', 'Tryll and the Murder Mystery demo'),
        ('6r85hTAEybQ', '4:18', 'Miloš Petković on the Murder Mystery demo'),
    ]),
    'Tutorials': ('PLZqr8WpRovB4', [
        ('CCOVxDNkvpc', '9:20', 'Make an NPC answer from game facts and lore'),
        ('aPr5C8NP30o', '6:36', 'Create NPCs that react to player behavior'),
        ('6kWWgV-6BZo', '4:43', 'Build a voice AI character'),
        ('gQlC57ahfpc', '9:02', 'Create a safe AI agent with guardrails and testing'),
    ]),
}

# Team preview (preview.py): GitHub Pages project site, no analytics, noindex.
# Only the password's SHA-256 is stored; change it with  preview.py --password NEW
PREVIEW = {
    'repo': 'TryllEngine/site-preview',
    'base': '/site-preview',
    'password_sha256': '6d22b8a2d2f6d1a4a70df5975665aa970eab7a9c9c53b0d7baa8ff258ae97439',
}

TODO = 'TODO:'   # prefix: link stays href="#" with data-todo, build prints it

# Placeholder links in the design (href="#"), keyed by link text, or by
# aria-label for icon-only links. A list means "nth occurrence on the page".
COMMON_LINKS = {
    'Docs': DOCS,
    'Discord': DISCORD,
    'Join Discord': DISCORD,
    'Discord Never build alone. Join us on Discord': DISCORD,
    'YouTube': YOUTUBE,
    'LinkedIn': LINKEDIN,
    'Watch on YouTube': YOUTUBE,   # homepage hero; the video lists use VIDEO_LISTS
    'Documentation API reference and guides, on docs.tryllengine.com': DOCS,
}

PAGE_LINKS = {
    'index': {
        'See it in a scene': DOCS_V + 'use-cases/talking-npc.html',
        'Hear it in a scene': DOCS_V + 'how-to/add-voice-to-an-agent.html',
        'How agents follow your rules': DOCS_V + 'how-to/use-canned-responses-and-guardrails.html',
        'Browse examples': DOCS_V + 'use-cases/index.html',
    },
    'download': {
        'Install guide': [DOCS_V + 'getting-started/first-inference-unity.html',
                          DOCS_V + 'getting-started/first-inference-unreal.html'],
        'Download for Unity 6+': TODO + 'Unity plugin download URL',
        'Download for UE 5.7+': TODO + 'Unreal plugin download URL',
        'Share of players · Steam Hardware Survey, 07/2026': 'https://store.steampowered.com/hwsurvey/',
    },
    'demo': {
        'Direct download': TODO + 'Tryll Colony direct download URL',
        'Steam': TODO + 'Tryll Colony Steam page',
        'Itch.io': TODO + 'Tryll Colony itch.io page',
    },
    'about': {
        'Alexander Stojanovic on LinkedIn': 'https://www.linkedin.com/in/stojanovic/',
        'Pierre Moisan on LinkedIn': 'https://www.linkedin.com/in/pierre-moisan-2431272/',
        'Gennadii Potapov on LinkedIn': 'https://www.linkedin.com/in/gennadiipotapov/',
        'Lidia Kozlova on LinkedIn': 'https://www.linkedin.com/in/lidia-kozlova-gamedev/',
        'Andrei Morozov on LinkedIn': 'https://www.linkedin.com/in/andreymorozov8/',
        'Miloš Petković on LinkedIn': 'https://www.linkedin.com/in/milos-petkovic-109a2098/',
        'Nikolay Andreev on LinkedIn': 'https://www.linkedin.com/in/nikolay-andreev-008802178/',
        'Dasha on LinkedIn': 'https://www.linkedin.com/in/daria-trush-265a31369/',
    },
    # Replaced by real controls in build.py (subscribe form, pagination).
    'blog': {k: None for k in ('Get updates', 'Previous', 'Next', '1', '2', '3')},
}


def placeholder_link(page, key, n):
    links = PAGE_LINKS.get(page, {})
    url = links[key] if key in links else COMMON_LINKS.get(key, KeyError)
    if url is KeyError:
        print(f'WARN {page}: no target for placeholder link "{key}"')
        return None
    if isinstance(url, list):
        url = url[min(n, len(url)) - 1]
    return url


# One entry per design page. "out" is the file written in the repo root;
# "path" is the canonical URL (GitHub Pages serves /features from features.html).
PAGES = {
    'index': {
        'out': 'index.html', 'path': '/', 'priority': '1.0',
        'title': 'Tryll Engine — On-Device AI for Game Characters',
        'description': 'On-device AI middleware for Unity, Unreal Engine 5 and custom engines. NPCs that '
                       "understand, remember and act, on the player's GPU. No servers, no token fees.",
    },
    'features': {
        'out': 'features.html', 'path': '/features', 'priority': '0.9',
        'title': 'Features for Developers — Tryll Engine',
        'description': 'What Tryll Engine gives game developers: basic and advanced NPCs, editor tools '
                       'like the Dialog Tester and Agent Log, and control over performance and memory.',
    },
    'download': {
        'out': 'download.html', 'path': '/download', 'priority': '0.9',
        'title': 'Get Tryll Engine for Unity and Unreal Engine',
        'description': 'Download the Tryll plugin for Unity 6+ or Unreal Engine 5.7+. Free until '
                       'your game earns $500k. System requirements, install guides and tutorials.',
        'description_soon': 'The Tryll plugin for Unity 6+ and Unreal Engine 5.7+ is coming soon. Free '
                            'until your game earns $500k. System requirements, install guides and tutorials.',
    },
    'demo': {
        'out': 'demo.html', 'path': '/demo', 'priority': '0.8',
        'title': 'Tryll Colony — Demo Game Built with Tryll Engine',
        'description': 'Play Tryll Colony, a short demo where you talk your way through a scene and '
                       'watch AI characters react in real time, fully on your own PC.',
        'description_soon': 'Tryll Colony, a demo game built with Tryll Engine, is coming soon: talk your '
                            'way through a scene and watch AI characters react in real time, on your own PC.',
    },
    'about': {
        'out': 'about.html', 'path': '/about', 'priority': '0.7',
        'title': 'About Tryll Engine — The Team Behind On-Device Game AI',
        'description': 'Meet the founders and team building Tryll Engine: game developers from '
                       'Playrix, esports and AAA art production, backed by Early Game Ventures and '
                       'Epic MegaGrants.',
    },
    'blog': {
        'out': 'blog.html', 'path': '/blog', 'priority': '0.8',
        'title': 'Tryll Engine Blog — On-Device AI for Games',
        'description': 'Engineering deep-dives, product updates and event news from the Tryll '
                       'Engine team: on-device AI for games, intelligent NPCs and local LLMs.',
    },
    'privacy': {
        'out': 'privacy-policy.html', 'path': '/privacy-policy', 'priority': '0.3',
        'title': 'Privacy Policy — Tryll Engine',
        'description': 'How Tryll Engine, Inc. handles personal data of visitors to tryllengine.com: '
                       'contact forms, the newsletter, cookies and analytics, and your rights under GDPR.',
    },
}

# Old-design pages kept at their URLs until they are redesigned.
LEGACY_PAGES = [
    ('/tryll-assistant', '2025-12-01', '0.7'),
    ('/boscotryll', '2025-07-22', '0.5'),
]

# Retired URLs. GitHub Pages can't send real redirects, so the build writes a
# small noindex page per entry that forwards instantly and tells Google where
# it moved.
REDIRECTS = {
    '/closed-beta': '/download',   # closed beta ended
}

SOFTWARE_LD = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    'name': 'Tryll Engine',
    'applicationCategory': 'DeveloperApplication',
    'operatingSystem': 'Windows 10, Windows 11',
    'description': 'On-device AI middleware for game engines: NPCs that understand natural '
                   "language, remember and act, running locally on the player's GPU.",
    'url': SITE + '/',
    'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD',
               'description': 'Free until a shipped game passes $500k USD gross revenue, then a 1% royalty.'},
}
