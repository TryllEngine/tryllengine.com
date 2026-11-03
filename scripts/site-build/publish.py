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
    print(f'dist/: {len(keep)} files, {size / 1e6:.1f} MB; left out {len(paths) - len(keep)} '
          f'(scripts, notes, sources)')


if __name__ == '__main__':
    main()
