"""Everything the design export doesn't know: SEO copy, link targets, forms.

Edit this file, then run  py -3 scripts/site-build/build.py
"""

SITE = 'https://tryllengine.com'
GTM_ID = 'GTM-K8MPGKVX'            # contains GA4 G-V0BH3P7R63 + form/download events
OG_IMAGE = '/assets/images/og-image.png'

# Forms — the same endpoints the old site used, so submissions keep landing
# in the same Formspree inbox and MailerLite group.
FORMS = {'contact': 'https://formspree.io/f/movlaywd'}
# Contact form -> HubSpot once HUBSPOT['form'] is set: each message becomes a contact in
# the CRM (EU1 account) with its "message", and HubSpot sends the notification email.
# Without a form it falls back to Formspree. "form" is the form's ID in HubSpot (Marketing > Forms).
HUBSPOT = {'api': 'https://api-eu1.hsforms.com', 'portal': '147726156',
           'form': 'eefbc03c-966e-4e77-9d6b-ae89c11b84e1'}
# Accepted contact messages also go to the team's Slack channel through a Cloudflare
# Worker (scripts/lead-alerts): its URL, e.g. https://tryll-lead-alerts.<account>.workers.dev.
# Empty = off.
LEAD_ALERTS = 'https://tryll-lead-alerts.sasha-glotov.workers.dev'
MAILERLITE_ACCOUNT = '2274886'
MAILERLITE_FORM = '185451758358627764'   # "blog" signup form

DISCORD = 'https://discord.gg/DTKycjPpzs'
YOUTUBE = 'https://www.youtube.com/@Tryll_Engine'
LINKEDIN = 'https://www.linkedin.com/company/tryllengine/'
DOCS = 'https://docs.tryllengine.com/'
# Deep links into the docs follow "latest", which the docs site moves to each new release,
# so they never need a version bump. The docs home stays DOCS ("latest/" alone has no page).
DOCS_V = DOCS + 'latest/'

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

# Wording changed since the design export, swapped in on every design page:
# (text in the design, text on the site). Drop an entry once the design has it.
COPY = [
    ('$500k', '$200k'),   # pricing threshold
    ('that allows integrate in-game AI', 'that lets you integrate in-game AI'),   # hero typo
]
if HUBSPOT['form']:   # the privacy policy names the contact form's processor
    COPY += [
        ('<b>Formspree</b> (contact form processing) - Formspree, Inc., USA.',
         '<b>HubSpot</b> (contact forms and customer records) - HubSpot, Inc., USA; '
         'our account is hosted in the EU.'),
        ('Last updated May 27, 2026', 'Last updated November 2, 2026'),
        ('Effective May 27, 2026', 'Effective November 2, 2026'),
    ]
if LEAD_ALERTS:   # ...and where contact messages are passed on to
    COPY.append(('our account is hosted in the EU.</li>',
                 'our account is hosted in the EU.</li>'
                 '<li><b>Slack</b> (team notifications about contact form messages) - Slack Technologies, LLC, USA.</li>'
                 '<li><b>Cloudflare</b> (passes contact form messages on to our team chat) - Cloudflare, Inc., USA.</li>'))

# Media logos on the homepage link to their articles, keyed by the logo's alt
# text (or its text, for a text-only logo) in the design.
MEDIA_LINKS = {
    'mobidictum': 'https://mobidictum.com/tryll-engine-valued-6m-opens-closed-alpha/',
    'Tech in Asia': 'https://www.techinasia.com/news/us-ai-gaming-startup-tryll-valued-at-6m-launches-alpha',
    'tech.eu': 'https://tech.eu/2026/06/17/tryll-launches-ai-gaming-engine-alpha-and-secures-600k-pre-seed-funding/',
    'unite.ai': 'https://www.unite.ai/tryll-engine-raises-600k-pre-seed-at-6m-valuation-to-bring-on-device-ai-'
                'characters-and-conversations-to-games/',
    'startup-rise': 'https://startuprise.co.uk/tryll-raises-600k-in-pre-seed-round-led-by-early-game-ventures/',
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

# Homepage use-case cards whose picture replaces the design's, keyed by the card's
# heading: (image, description for screen readers). Images are 16:10, 1152x720.
CARD_PICTURES = {
    'Real Talk': ('/assets/images/real-talk.jpg',
                  'A player talks to a settler by voice; the conversation appears on screen'),
    'Dynamic worlds': ('/assets/images/dynamic-worlds.jpg', 'A colony village seen from above'),
    'New genres': ('/assets/images/new-genres.jpg',
                   'A twenty-sided die opening up with light inside, joined to other dice by threads'),
}

# /demo (Tryll Colony): the gallery in order, as (image in assets/images/demo/, which also
# has a -thumb copy; description for screen readers), and "About this game" in Markdown.
DEMO_SHOTS = [
    ('tavern-talk', 'A settler outside the Black Bear tavern says: I tended the sheep and the cows all morning.'),
    ('settler-stats', 'Greta Lark’s stats: skills, needs and mood'),
    ('village-night', 'The village at night, lit by lanterns and windows'),
    ('village-day', 'The village from above: cottages, the tavern, market stalls and fields'),
    ('work-schedule', 'The work schedule: sleep, work and rest hours for each settler'),
    ('trade-talk', 'Trading with the seed merchant and haggling with her in plain words'),
]
DEMO_ABOUT = 'demo-about.md'   # in scripts/site-build/
DEMO_DROP_TAGS = ['Simulation']   # design tags left out ("Colony sim" says it)
# /demo system requirements, in order: (row, minimum, recommended), or (row, value) when
# both are the same, which then shows once across both columns.
DEMO_REQUIREMENTS = [
    ('OS', 'Windows 11 64-bit'),
    ('Processor', 'Intel Core i5-10400 / AMD Ryzen 5 3600', 'AMD Ryzen 5 7500F / Intel Core i5-12400'),
    ('Memory', '16 GB RAM'),
    ('Graphics', 'NVIDIA GeForce RTX 4060 / AMD Radeon RX 7600 (8 GB VRAM)',
     'NVIDIA GeForce RTX 4070 / AMD Radeon RX 7700 XT (12 GB VRAM)'),
    ('DirectX', 'Version 12'),
    ('Storage', '8 GB available space'),
]

# "What clients are saying" on the homepage: one card per quote, in order ('role', 'site'
# and 'linkedin' may be empty: no link then). 'picture' is a 16:9 image shown whole
# (1152x648, assets/images/clients/); without one, the card keeps the design's picture in
# its place. An empty list leaves the section's heading and carousel out; "Media about
# us" below it stays.
CLIENT_QUOTES = [
    {'studio': 'Studios iLLOGIKA', 'site': 'https://www.illogika.com/en',
     'name': 'Hervé Lange', 'linkedin': 'https://www.linkedin.com/in/herv%C3%A9-lange-782b361/',
     'role': 'Sr. Technical Director',
     'picture': ('/assets/images/clients/illogika.jpg', 'Studios iLLOGIKA logo'),
     'quote': 'Language models represent the next major leap for interactive experiences. With Tryll '
              'Engine, I finally found technology that actually works for game developers, backed by an '
              'outstanding team whose support has been invaluable in navigating this new world.'},
    {'studio': 'GunGrounds', 'site': 'https://gungrounds.com/',
     'name': 'Kristian Macanga', 'linkedin': 'https://www.linkedin.com/in/krismacanga/', 'role': '',
     'picture': ('/assets/images/clients/gungrounds.jpg',
                 'A scene from a GunGrounds murder mystery: questioning LUCE, the intelligence '
                 'that operates Barbeta Lighthouse'),
     'quote': 'Tryll Engine allows us to bring a new level of interactivity to storytelling without '
              'sacrificing creative control. Our writers carefully craft the narrative, characters, and '
              'dialogue content, while Tryll understands players’ questions and intentions, allowing '
              'characters to respond naturally while staying true to the story, their personalities, and '
              'the knowledge defined by our writers. It’s technology that empowers our writers rather '
              'than replaces them, giving us the freedom to create experiences that traditional dialogue '
              'systems simply couldn’t deliver.'},
    {'studio': 'Meant Well Games', 'site': '', 'name': 'Sergey Plyaka', 'linkedin': '', 'role': '',
     'picture': ('/assets/images/clients/voice-heist.jpg',
                 'Voice Heist mockup: the player’s robot points at an opened door and says '
                 '“It’s open now, Boss. I used my head!”'),
     'quote': 'While developing Voice Heist, a game where players control a robot using natural voice '
              'commands, one of my biggest challenges was making speech recognition and intent '
              'understanding work together to create a seamless gameplay experience. Tryll helped me '
              'experiment with different AI models, quickly identify issues, compare what worked best, '
              'and iterate faster, allowing me to focus on making the robot feel responsive and alive.'},
]

# The hero's badges and the footer's "Epic MegaGrants recipient" link out (build.py
# badge_links): the grant's blog post; EGV's logo to their site, its text to the news.
EPIC_MEGAGRANT = '/blog/posts/epic-megagrant-from-unreal-engine/'
EGV_SITE = 'https://earlygame.vc/'
EGV_NEWS = MEDIA_LINKS['tech.eu']

# "Faster than speech" on /features ends with a row to compare with: people talk at
# about 150 words a minute, and at ~1.3 tokens a word that is ~3 tokens a second.
# (number, label, sentence added to the footnote)
SPEECH_ROW = ('~3', 'tok/s · People talking', 'People talk at about 150 words a minute.')

# Clips cut from the trailer by clips.py (needs ffmpeg), then placed by build.py:
#   py -3 scripts/site-build/clips.py "C:/path/to/trailer.mp4"
# A shot is (start s, end s, ffmpeg crop "w:h:x:y" in the 1920x1080 trailer); x can
# be an expression of t, seconds into the shot, to pan. "poster": seconds into the clip.
TRAILER_URL = ''   # hero "Watch on YouTube": empty leaves it out; set to the trailer's own link once it's up
CLIPS = {
    # Hero: three tavern close-ups (1:21.8-1:30.1), each reframed so the face clears the headline.
    'hero': {'size': (1152, 720), 'small': (640, 400), 'crf': 27, 'poster': 0, 'shots': [
        (81.84, 85.80, '1344:840:0:120'),
        (85.88, 88.48, '1344:840:330:120'),
        (88.56, 90.12, '1344:840:367:120'),
    ]},
    # Smart NPCs, "Before": "Nice weather, huh?" in the storm, then a boulder knocks his
    # head aside and the frame freezes (0:13.8-0:17.4); the crop follows his head left.
    'npc-before': {'size': (576, 720), 'crf': 28, 'audio': True, 'poster': 1.0,
                   'label': 'Before: an NPC in a storm says "Nice weather, huh?" and a boulder hits his head',
                   'shots': [
        (13.76, 17.40, "694:868:'if(lt(t,2),573,max(0,573-573*(t-2)/0.16))':106"),
    ]},
    # Smart NPCs, "With Tryll": he points everyone to the tavern (0:51.7-0:54.1);
    # the crop follows him to the right while he points, then back.
    'npc-after': {'size': (576, 720), 'crf': 28, 'audio': True, 'poster': 1.2,
                  'label': 'With Tryll: an NPC in the storm points the way to the tavern', 'shots': [
        (51.72, 54.12, "592:740:'if(lt(t,1.65),734+150*(1-cos(PI*t/1.65)),1034-170*(1-cos(PI*min((t-1.65)/0.75,1))))':150"),
    ]},
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
    'Watch on YouTube': TRAILER_URL or None,   # homepage hero; the video lists use VIDEO_LISTS
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
                       'your game earns $200k. System requirements, install guides and tutorials.',
        'description_soon': 'The Tryll plugin for Unity 6+ and Unreal Engine 5.7+ is coming soon. Free '
                            'until your game earns $200k. System requirements, install guides and tutorials.',
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
               'description': 'Free until a shipped game passes $200k USD gross revenue, then a 1% royalty.'},
}
