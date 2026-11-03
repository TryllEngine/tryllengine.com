"""Copy the files the live site serves into dist/, which Cloudflare Pages publishes.

    py -3 scripts/site-build/publish.py      (Cloudflare's build command: python3 scripts/site-build/publish.py)

Cloudflare Pages publishes its build output directory as it is. When that was the repo root,
anyone could download the build scripts, CLAUDE.md, the skills and the blog's Markdown from
tryllengine.com. This copies every file git tracks except those into dist/. The pages
themselves are built locally by build.py and committed, so nothing is built here.
"""
import os
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'dist')
# Not part of the site: tooling, notes, the blog's sources (build.py turns them into
# blog/posts/) and files only other hosts read. Markdown files are notes wherever they are.
SKIP_DIRS = ('scripts/', '.claude/', '.github/', 'blog/content/', 'references/')
SKIP_FILES = {'blog/posts.json', '.gitignore', '.htaccess', '.nojekyll', 'CNAME'}
# Cloudflare Pages keeps serving a removed file for up to a week to anyone who requested it
# before ("asset preservation"), unless a redirect matches first. So every path left out
# here, and these that were taken off the site before, go to the home page via _redirects.
RETIRED = ['/preview/*']


def published(path):
    return not (path.startswith(SKIP_DIRS) or path in SKIP_FILES or path.endswith('.md'))


def tracked():
    """Paths git tracks, with forward slashes; every file on disk when git isn't there."""
    try:
        out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout
        return [p for p in out.decode('utf-8').split('\0') if p]
    except (OSError, subprocess.CalledProcessError):
        paths = []
        for top, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in ('.git', 'dist')]
            paths += [os.path.relpath(os.path.join(top, f), ROOT).replace(os.sep, '/') for f in files]
        return paths


def redirects(left_out):
    """_redirects lines that send the paths left out of dist/ to the home page."""
    dirs = sorted({d for p in left_out for d in SKIP_DIRS if p.startswith(d)})
    files = sorted(p for p in left_out if not p.startswith(SKIP_DIRS))
    return [f'/{d}* / 302' for d in dirs] + [f'{r} / 302' for r in RETIRED] + [f'/{p} / 302' for p in files]


def main():
    paths = tracked()
    keep = [p for p in paths if published(p) and os.path.isfile(os.path.join(ROOT, p))]
    shutil.rmtree(OUT, ignore_errors=True)
    size = 0
    for p in keep:
        dst = os.path.join(OUT, p)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, p), dst)
        size += os.path.getsize(dst)
    rules = redirects([p for p in paths if not published(p)])
    with open(os.path.join(OUT, '_redirects'), 'a', encoding='utf-8') as f:   # after any _redirects of the site's own
        f.write('\n'.join(rules) + '\n')
    print(f'dist/: {len(keep)} files, {size / 1e6:.1f} MB; left out {len(paths) - len(keep)} '
          f'(scripts, notes, sources), redirected by {len(rules)} rules')


if __name__ == '__main__':
    main()
