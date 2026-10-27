"""Team preview of the current branch: no analytics, noindex, password screen.

    py -3 scripts/site-build/preview.py --publish            # rebuild + push to the preview site
    py -3 scripts/site-build/preview.py --password NEW ...   # use a different password

The preview is a copy of the built site that:
  - drops Google Tag Manager and the cookie banner (no analytics),
  - marks every page noindex, nofollow,
  - asks for a team password before showing anything (a screen, not real
    security: the site source is public on GitHub anyway),
  - rewrites root links for the GitHub Pages project path (/site-preview/).

Forms are left working, so the preview is also the place to test the real
Formspree and MailerLite submissions.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import config as C  # noqa: E402

SKIP_DIRS = ('scripts/', '.claude/', '.github/', 'preview/', 'references/', 'blog/content/')
SKIP_FILES = {'CNAME', '.htaccess', '.gitignore', '.nojekyll', 'sitemap.xml', 'robots.txt', 'llms.txt'}

GATE = """<meta name="robots" content="noindex, nofollow">
<script>
/* Team preview password screen. Keeps casual visitors out; not real security. */
(function () {
  var H = '%s', K = 'tryll-preview', d = document.documentElement;
  try { if (localStorage.getItem(K) === H) return; } catch (e) {}
  d.style.visibility = 'hidden';
  function show() {
    var o = document.createElement('div');
    o.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;' +
      'background:#161D29;visibility:visible;font-family:"Space Grotesk",system-ui,sans-serif';
    o.innerHTML = '<form style="background:#fff;border-radius:16px;padding:32px;width:min(360px,88vw);display:flex;flex-direction:column;gap:14px">' +
      '<b style="font-size:24px;font-weight:500;color:#181716">Tryll site preview</b>' +
      '<span style="color:rgba(24,23,22,.72);font-size:16px">Enter the team password to continue.</span>' +
      '<input type="password" aria-label="Password" style="height:48px;border-radius:8px;border:1px solid rgba(24,23,22,.2);padding:0 14px;font:inherit;font-size:16px">' +
      '<button style="height:48px;border:0;border-radius:8px;background:#232E41;color:#fff;font:inherit;font-size:16px;cursor:pointer">Open preview</button>' +
      '<small style="color:#B42318;min-height:1.2em;font-size:14px"></small></form>';
    document.body.appendChild(o);
    var f = o.firstChild, i = f.querySelector('input');
    i.focus();
    f.onsubmit = function (e) {
      e.preventDefault();
      crypto.subtle.digest('SHA-256', new TextEncoder().encode(i.value)).then(function (b) {
        var h = Array.from(new Uint8Array(b)).map(function (x) { return x.toString(16).padStart(2, '0'); }).join('');
        if (h !== H) { f.querySelector('small').textContent = 'Wrong password'; i.select(); return; }
        try { localStorage.setItem(K, H); } catch (e2) {}
        o.remove();
        d.style.visibility = '';
      });
    };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show); else show();
})();
</script>"""


def site_files():
    out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.split('\n')
    for f in out:
        if f and not f.startswith(SKIP_DIRS) and f not in SKIP_FILES and not f.endswith('.md') \
                and os.path.exists(os.path.join(ROOT, f)):
            yield f


def rebase_html(s, base):
    s = re.sub(r'((?:href|src|action|poster)=["\'])/(?!/)', r'\1' + base + '/', s)
    s = re.sub(r'(url\((?:["\']|&quot;)?)/(?!/)', r'\1' + base + '/', s)
    s = s.replace('\\"/assets/', '\\"' + base + '/assets/')          # loop templates (JSON)
    s = re.sub(r'(content="0; url=)/', r'\1' + base + '/', s)          # redirect pages
    s = s.replace('location.replace("/', 'location.replace("' + base + '/')
    return s


def strip_analytics(s):
    s = re.sub(r'<!-- Google Tag Manager -->\s*', '', s)
    s = re.sub(r'<!-- End Google Tag Manager -->\s*', '', s)
    s = re.sub(r'<!-- Google Tag Manager \(noscript\) -->\s*|<!-- End Google Tag Manager \(noscript\) -->\s*', '', s)
    s = re.sub(r'<script>\s*\(function\(w,d,s,l,i\).*?</script>\s*', '', s, flags=re.S)
    s = re.sub(r'<noscript><iframe src="https://www\.googletagmanager\.com/ns\.html.*?</noscript>\s*', '', s, flags=re.S)
    s = re.sub(r'<script src="/assets/js/cookie-consent\.js"></script>\s*', '', s)
    return s


def build_preview(out, base, pw_hash):
    if os.path.exists(out):
        for name in os.listdir(out):
            if name != '.git':
                p = os.path.join(out, name)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    count = 0
    for f in site_files():
        src, dst = os.path.join(ROOT, f), os.path.join(out, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if f.endswith('.html'):
            s = open(src, encoding='utf-8').read()
            s = strip_analytics(s)
            assert 'googletagmanager' not in s, f
            s = re.sub(r'<meta name="robots"[^>]*>\s*', '', s)
            s = re.sub(r'<head>', '<head>\n' + GATE % pw_hash, s, count=1)
            s = rebase_html(s, base)
            open(dst, 'w', encoding='utf-8', newline='\n').write(s)
        elif f.startswith('assets/js/pages/'):
            s = open(src, encoding='utf-8').read()
            s = re.sub(r'(["\'])/assets/', r'\1' + base + '/assets/', s)
            open(dst, 'w', encoding='utf-8', newline='\n').write(s)
        else:
            shutil.copy2(src, dst)
        count += 1
    open(os.path.join(out, '.nojekyll'), 'w').close()
    return count


def git(args, cwd):
    return subprocess.run(['git'] + args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def publish(out, repo):
    url = f'https://github.com/{repo}.git'
    exists = subprocess.run(['gh', 'repo', 'view', repo], capture_output=True).returncode == 0
    if not exists:
        owner, name = repo.split('/')
        subprocess.run(['gh', 'repo', 'create', repo, '--public',
                        '--description', 'Team preview of the tryllengine.com redesign (noindex, no analytics)',
                        '--homepage', f'https://{owner.lower()}.github.io/{name}/'], check=True)
    if not os.path.exists(os.path.join(out, '.git')):
        git(['init', '-b', 'main'], out)
        git(['remote', 'add', 'origin', url], out)
    for key in ('user.name', 'user.email'):
        val = subprocess.run(['git', 'config', key], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if val:
            git(['config', key, val], out)
    branch = git(['rev-parse', '--abbrev-ref', 'HEAD'], ROOT)
    sha = git(['rev-parse', '--short', 'HEAD'], ROOT)
    git(['add', '-A'], out)
    git(['commit', '--allow-empty', '-m', f'Preview of {branch} @ {sha}'], out)
    git(['push', '-f', 'origin', 'main'], out)
    if not exists:
        subprocess.run(['gh', 'api', '-X', 'POST', f'repos/{repo}/pages',
                        '-f', 'source[branch]=main', '-f', 'source[path]=/'], check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--publish', action='store_true', help=f'push to {C.PREVIEW["repo"]}')
    ap.add_argument('--password', help='use this password instead of the one in config.py')
    ap.add_argument('--out', default=os.path.join(tempfile.gettempdir(), 'tryll-site-preview'))
    a = ap.parse_args()

    pw_hash = hashlib.sha256(a.password.encode()).hexdigest() if a.password else C.PREVIEW['password_sha256']
    if a.password:
        print(f'password hash (put in config.PREVIEW to keep it): {pw_hash}')
    subprocess.run([sys.executable, os.path.join(HERE, 'build.py')], check=True)
    n = build_preview(a.out, C.PREVIEW['base'], pw_hash)
    print(f'preview: {n} files in {a.out}')
    if a.publish:
        publish(a.out, C.PREVIEW['repo'])
        owner, name = C.PREVIEW['repo'].split('/')
        print(f'published: https://{owner.lower()}.github.io/{name}/ (Pages can take a minute to update)')


if __name__ == '__main__':
    main()
