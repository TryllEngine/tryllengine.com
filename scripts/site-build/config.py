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
    'Watch on YouTube': YOUTUBE,
    'Privacy Policy': '/privacy-policy',
    'Documentation API reference and guides, on docs.tryllengine.com': DOCS,
    # "How to build" video lists: titles in the design are placeholders.
    '24:10 Running a 7B model next to your game': TODO + 'real dev talk video URL',
    '18:32 Memory that survives saves': TODO + 'real dev talk video URL',
    '21:47 Designing guardrails for NPCs': TODO + 'real dev talk video URL',
    '6:12 Install Tryll in Unity': TODO + 'real tutorial video URL',
    '11:40 Your first talking NPC': TODO + 'real tutorial video URL',
    '9:05 Connect lore to a character': TODO + 'real tutorial video URL',
    '7:28 Test it in the Dialog Tester': TODO + 'real tutorial video URL',
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
    },
    'demo': {
        'out': 'demo.html', 'path': '/demo', 'priority': '0.8',
        'title': 'Tryll Colony — Demo Game Built with Tryll Engine',
        'description': 'Play Tryll Colony, a short demo where you talk your way through a scene and '
                       'watch AI characters react in real time, fully on your own PC.',
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
}

# Old-design pages kept at their URLs until they are redesigned.
LEGACY_PAGES = [
    ('/tryll-assistant', '2025-12-01', '0.7'),
    ('/boscotryll', '2025-07-22', '0.5'),
    ('/privacy-policy', '2025-07-18', '0.3'),
]

# Retired URLs. GitHub Pages can't send real redirects, so the build writes a
# small page per entry that forwards instantly and tells Google where it moved.
REDIRECTS = {
    '/closed-beta': '/download',   # closed beta ended; the engine is free to download
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
