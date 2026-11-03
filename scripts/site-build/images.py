"""Lighter pictures: a WebP copy of each picture the pages show, where that changes nothing you can see.

    py -3 scripts/site-build/images.py        (needs Pillow:  py -3 -m pip install pillow)

For every JPEG and PNG in assets/ that the built pages show, this tries WebP at
falling quality and keeps the smallest copy that still matches the original
(SSIM >= 0.99 on brightness; a picture with transparency is checked over white
and over the site's navy), if it is at least a fifth smaller. The copy is saved
next to the original as <name>.webp, and build.py makes the pages load it
(config.WEBP). The original stays: link previews (og:image) and structured
data use it, and old links to it keep working.

Pictures that can't get smaller that way (the grainy blog covers, JPEGs that are
tight already) are left as they are. images.json records each verdict with the
original's SHA-1, so a later run only tries new or changed pictures, and
build.py ignores a copy whose original has changed since. Run it after adding
pictures (a blog post, a design export): it builds the site first, to see which
pictures the pages show, and again at the end, so the pages load the copies.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RECORD = os.path.join(HERE, 'images.json')
TARGET = 0.99           # SSIM the copy must keep
MIN_GAIN = 0.2          # ...and at least this much smaller
MIN_SAVED = 10 * 1024   # ...and at least this many bytes
BACKGROUNDS = ((255, 255, 255), (22, 29, 41))   # transparent pictures sit on white or navy (#161D29)

# Root-relative pictures as the pages write them (build.py's RASTER_URL, plus their .webp).
PICTURE = re.compile(r'''(?<=["'(;])/assets/(?!favicon/)[^"'?#()\s\\&]+\.(?:jpe?g|png|webp)(?=[?"')\\&\s])''')


def sha1(path):
    with open(path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def shown_pictures():
    """assets/ paths of the JPEGs and PNGs the built pages and their logic load."""
    pages = []
    for d, _, names in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT).replace('\\', '/')
        if rel.startswith(('.git', 'scripts', '.claude', 'node_modules')):
            continue
        pages += [os.path.join(d, n) for n in names if n.endswith('.html')]
    pages += [os.path.join(ROOT, 'assets', 'js', 'pages', n)
              for n in os.listdir(os.path.join(ROOT, 'assets', 'js', 'pages')) if n.endswith('.js')]
    found = set()
    for p in pages:
        with open(p, encoding='utf-8') as f:
            for u in PICTURE.findall(f.read()):
                path = u.lstrip('/')
                if path.endswith('.webp'):   # already swapped by build.py: find its original
                    stem = path[:-5]
                    path = next((stem + e for e in ('.jpg', '.jpeg', '.png') if os.path.isfile(os.path.join(ROOT, stem + e))), '')
                if path and os.path.isfile(os.path.join(ROOT, path)):
                    found.add(path)
    return sorted(found)


def ssim(a, b, k=8):
    """Mean SSIM of two brightness arrays over k x k blocks."""
    import numpy as np
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    a = a[:h, :w].reshape(h // k, k, w // k, k)
    b = b[:h, :w].reshape(h // k, k, w // k, k)
    ma, mb = a.mean((1, 3)), b.mean((1, 3))
    va, vb = a.var((1, 3)), b.var((1, 3))
    cov = ((a - ma[:, None, :, None]) * (b - mb[:, None, :, None])).mean((1, 3))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    return float((((2 * ma * mb + c1) * (2 * cov + c2)) / ((ma ** 2 + mb ** 2 + c1) * (va + vb + c2))).mean())


def views(im, alpha):
    """What a visitor sees of a picture, as brightness: over each background if it has transparency."""
    import numpy as np
    from PIL import Image
    if not alpha:
        return [np.asarray(im.convert('L'))]
    out = []
    for bg in BACKGROUNDS:
        base = Image.new('RGBA', im.size, bg + (255,))
        base.alpha_composite(im.convert('RGBA'))
        out.append(np.asarray(base.convert('L')))
    return out


def best_webp(path):
    """(quality, bytes) of the smallest WebP that keeps TARGET, or None."""
    from PIL import Image, ImageOps
    im = Image.open(path)
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im)   # a photo stored rotated: the copy carries no orientation tag
    alpha = im.mode in ('RGBA', 'LA', 'PA') or (im.mode == 'P' and 'transparency' in im.info)
    im = im.convert('RGBA' if alpha else 'RGB')
    ref = views(im, alpha)
    lo, hi, found = 60, 96, None
    while lo <= hi:
        q = (lo + hi) // 2
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=q, method=6, **({'icc_profile': icc} if icc else {}))
        dec = Image.open(io.BytesIO(buf.getvalue()))
        dec.load()
        if min(ssim(r, d) for r, d in zip(ref, views(dec, alpha))) >= TARGET:
            found, hi = (q, buf.getvalue()), q - 1
        else:
            lo = q + 1
    return found


def job(path):
    src = os.path.join(ROOT, path)
    size = os.path.getsize(src)
    found = best_webp(src)
    if found and len(found[1]) <= size * (1 - MIN_GAIN) and size - len(found[1]) >= MIN_SAVED:
        return path, found[0], found[1]
    return path, None, None


def main():
    try:
        import numpy  # noqa: F401
        import PIL  # noqa: F401
    except ImportError:
        raise SystemExit('needs Pillow and numpy:  py -3 -m pip install pillow numpy')
    build = [sys.executable, os.path.join(HERE, 'build.py')] + sys.argv[1:]
    subprocess.run(build, check=True, capture_output=True)   # the pages as they are now
    record = {}
    if os.path.exists(RECORD):
        with open(RECORD, encoding='utf-8') as f:
            record = json.load(f)
    shown = shown_pictures()
    stems = {}
    for p in shown:
        stems.setdefault(os.path.splitext(p)[0], []).append(p)
    todo = []
    for p in shown:
        if len(stems[os.path.splitext(p)[0]]) > 1:
            print(f'skipped {p}: another picture has the same name, so their .webp would clash')
            continue
        r = record.get(p)
        webp = os.path.splitext(p)[0] + '.webp'
        if r and r['sha1'] == sha1(os.path.join(ROOT, p)) and (not r['webp'] or os.path.isfile(os.path.join(ROOT, webp))):
            continue
        todo.append(p)
    print(f'{len(shown)} pictures on the pages, {len(todo)} to try')
    saved = 0
    with ProcessPoolExecutor() as pool:
        for path, q, data in pool.map(job, todo):
            src = os.path.join(ROOT, path)
            webp = os.path.splitext(path)[0] + '.webp'
            size = os.path.getsize(src)
            if data:
                with open(os.path.join(ROOT, webp), 'wb') as f:
                    f.write(data)
                saved += size - len(data)
                print(f'{size // 1024:6} KB -> {len(data) // 1024:5} KB  webp q{q}  {path}')
            else:
                if os.path.isfile(os.path.join(ROOT, webp)):
                    os.remove(os.path.join(ROOT, webp))
                print(f'{size // 1024:6} KB    kept            {path}')
            record[path] = {'sha1': sha1(src), 'webp': webp if data else None, 'quality': q}
    # Forget pictures the pages no longer show, and their copies.
    for path in [p for p in record if p not in shown]:
        webp = record.pop(path).get('webp')
        if webp and os.path.isfile(os.path.join(ROOT, webp)):
            os.remove(os.path.join(ROOT, webp))
            print(f'removed {webp}: the pages no longer show {path}')
    with open(RECORD, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(sorted(record.items())), f, indent=1)
        f.write('\n')
    print(f'saved {saved // 1024} KB' if todo else 'nothing new', '- building the site:', flush=True)
    subprocess.run(build, check=True)


if __name__ == '__main__':
    sys.exit(main())
