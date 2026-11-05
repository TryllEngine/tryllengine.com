"""Step 2 of the site build: render the Claude Design export to static HTML.

Run this whenever a new design export arrives:

    py -3 scripts/site-build/bake.py "C:/path/to/design-export"
    py -3 scripts/site-build/build.py

An export of some pages only (the designer's "parts") bakes just those, and the
other pages keep their last bake:

    py -3 scripts/site-build/bake.py "C:/path/to/design-export" index 404

It annotates the export (annotate.py), serves it on 127.0.0.1, lets headless
Chrome or Edge run the design runtime once per page, and saves the rendered
DOM to scripts/site-build/baked/. The export's files that those pages use
(images, scripts like three.js) go to assets/site/.
"""
import functools
import http.server
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import annotate  # noqa: E402

PAGES = ['index', 'features', 'download', 'demo', 'about', 'blog', 'blog-post', 'privacy', '404']
BROWSERS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium',
]


def main(src, pages=PAGES):
    unknown = [p for p in pages if p not in PAGES]
    if unknown:
        raise SystemExit(f'not design pages: {", ".join(unknown)} (pages: {", ".join(PAGES)})')
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        raise SystemExit('Chrome or Edge not found; add its path to BROWSERS in bake.py')
    work = tempfile.mkdtemp(prefix='tryll-bake-')
    annotate.main(src, work)

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=work))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    out = os.path.join(HERE, 'baked')
    os.makedirs(out, exist_ok=True)
    profile = os.path.join(work, '_profile')
    used = set()
    for page in pages:
        dom = subprocess.run(
            [browser, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={profile}',
             '--window-size=1440,900', '--virtual-time-budget=5000', '--dump-dom',
             f'http://127.0.0.1:{port}/{page}.html'],
            capture_output=True, timeout=120).stdout.decode('utf-8')
        if 'id="dc-root"' not in dom:
            raise SystemExit(f'{page}: design runtime did not render')
        with open(os.path.join(out, page + '.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(dom)
        shutil.copy2(os.path.join(work, page + '.loops.json'), os.path.join(out, page + '.loops.json'))
        with open(os.path.join(out, page + '.loops.json'), encoding='utf-8') as f:
            used.update(re.findall(r'assets/([0-9a-f]{32}\.\w+)', dom + f.read()))
        print(f'baked {page} ({len(dom) // 1024} KB)')
    server.shutdown()

    # Only the files the baked pages use: a parts export carries the whole project's.
    assets = os.path.join(ROOT, 'assets', 'site')
    os.makedirs(assets, exist_ok=True)
    for name in os.listdir(os.path.join(src, 'assets')):
        if name in used:
            shutil.copy2(os.path.join(src, 'assets', name), os.path.join(assets, name))
    shutil.rmtree(work, ignore_errors=True)
    print('done; now run build.py')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2:] or PAGES)
