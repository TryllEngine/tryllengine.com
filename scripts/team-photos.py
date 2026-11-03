"""Normalise the team photos so every face is the same size on the page.

Two shapes are used on /about, and both were inconsistent before this script:

* **Founder cutouts** (the party cards) are transparent PNGs. The card renders
  them `height:178px; width:auto`, anchored `bottom:0`, so what decides how big
  a head looks is face-height / image-height — not the source resolution. Each
  cutout is cropped from the bottom until that ratio matches `CUTOUT_FACE`; the
  hair is already at the top edge in every source, so the torso is the only
  free dimension. The full width is kept, because trimming it would cut
  shoulders. The matte is eroded by a pixel first: background removal leaves a
  light rim, and that rim is the "white halo" you see against the card.
* **Square headshots** (Advisors and Team) are cropped so the face box is
  `SQUARE_FACE` of the side and the eye line sits `SQUARE_EYE` down, then
  resized to one size. That is what makes a row of them read as a set.

Faces are found with OpenCV's YuNet, which also returns the eyes.

    py -3 scripts/team-photos.py <source-dir> [--only sasha-glotov]

Source files are named after the person's slug (`vladimir-beliaev.jpg`); the
extension does not matter. A source that is already a cutout (transparent PNG)
is used as is, anything else is passed through rembg first. Outputs go to
assets/images/team/ and are wired up by TEAM_PHOTOS in config.py.

Needs: pip install opencv-python-headless rembg pillow
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, 'assets', 'images', 'team')
MODEL = os.path.join(HERE, 'yunet.onnx')

# Cutouts: the tightest source sets the target, so nobody needs padding.
CUTOUT_FACE = 0.543
CUTOUT_MAX_H = 600       # the card renders these at 178 px; more is dead weight
FEATHER = 1              # px of alpha erosion, to cut the cutout's light rim
# Squares: face box width as a fraction of the side, and the eye line's depth.
SQUARE_FACE = 0.34
SQUARE_FACE_MAX = 0.46   # tightest fallback when a face sits near an edge
SQUARE_EYE = 0.40
SQUARE_SIZE = 800

CUTOUTS = ['sasha-glotov', 'vladimir-beliaev', 'alex-riabov', 'maksim-makevich']


def detector(w, h):
    import cv2
    if not os.path.isfile(MODEL):
        sys.exit(f'YuNet model missing: {MODEL}\n'
                 'Download face_detection_yunet_2023mar.onnx from opencv/opencv_zoo '
                 '(Git LFS: use the media.githubusercontent.com URL) and put it there.')
    d = cv2.FaceDetectorYN.create(MODEL, '', (w, h), 0.5, 0.3, 5000)
    d.setInputSize((w, h))
    return d


def find_face(pil_rgb):
    """Largest face as (x, y, w, h, eye_x, eye_y), or None."""
    import cv2, numpy as np
    img = cv2.cvtColor(np.array(pil_rgb), cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    _, faces = detector(w, h).detect(img)
    if faces is None or len(faces) == 0:
        return None
    f = max(faces, key=lambda f: f[2] * f[3])
    return (float(f[0]), float(f[1]), float(f[2]), float(f[3]),
            (float(f[4]) + float(f[6])) / 2, (float(f[5]) + float(f[7])) / 2)


def make_cutout(src, dst):
    from PIL import Image, ImageFilter
    im = Image.open(src)
    if im.mode in ('RGBA', 'LA') and im.getchannel('A').getextrema()[0] == 0:
        rgba = im.convert('RGBA')                      # already cut out
    else:
        from rembg import remove, new_session
        rgb = im.convert('RGB')
        if rgb.height < 1000:                          # a thin source makes a soft matte
            rgb = rgb.resize((rgb.width * 3, rgb.height * 3), Image.LANCZOS)
        rgba = remove(rgb, session=new_session('u2net')).convert('RGBA')

    if FEATHER:
        r, g, b, a = rgba.split()
        a = a.filter(ImageFilter.MinFilter(2 * FEATHER + 1))
        rgba = Image.merge('RGBA', (r, g, b, a))

    flat = Image.new('RGBA', rgba.size, (128, 128, 128, 255))
    flat.alpha_composite(rgba)
    face = find_face(flat.convert('RGB'))
    if face is None:
        print(f'WARN {os.path.basename(src)}: no face found, left uncropped')
        rgba.save(dst)
        return
    height = min(face[3] / CUTOUT_FACE, float(rgba.height))
    out = rgba.crop((0, 0, rgba.width, round(height)))
    if out.height > CUTOUT_MAX_H:
        out = out.resize((round(out.width * CUTOUT_MAX_H / out.height), CUTOUT_MAX_H),
                         Image.LANCZOS)
    out.save(dst)


def make_square(src, dst):
    from PIL import Image
    im = Image.open(src).convert('RGB')
    w, h = im.size
    face = find_face(im)
    if face is None:
        print(f'WARN {os.path.basename(src)}: no face found, centre crop')
        side = min(w, h)
        left, top = (w - side) / 2, (h - side) / 2
    else:
        fx, fy, fw, fh, ex, ey = face
        # The shared face size comes first, but a face near an edge cannot be
        # centred at that size. A head a little larger reads far better than a
        # correctly sized one shoved against the frame, so tighten the crop
        # until it can be centred, up to SQUARE_FACE_MAX.
        frac = SQUARE_FACE
        while True:
            side = min(fw / frac, float(min(w, h)))
            left = min(max(ex - side / 2, 0.0), w - side)
            top = min(max(ey - side * SQUARE_EYE, 0.0), h - side)
            off = abs(left - (ex - side / 2)) / side
            if off <= 0.02 or frac >= SQUARE_FACE_MAX:
                break
            frac = min(frac + 0.01, SQUARE_FACE_MAX)
        if off > 0.02:
            print(f'NOTE {os.path.basename(src)}: the face is {off:.0%} off centre even at '
                  f'the tightest crop — the source has too little room beside it')
        elif frac > SQUARE_FACE:
            print(f'NOTE {os.path.basename(src)}: cropped tighter (face {frac:.2f} of the '
                  f'side, not {SQUARE_FACE:.2f}) so it could be centred')
    im.crop((round(left), round(top), round(left + side), round(top + side))) \
      .resize((SQUARE_SIZE, SQUARE_SIZE), Image.LANCZOS) \
      .save(dst, quality=92, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source_dir', help='folder of sources named <person-slug>.<ext>')
    ap.add_argument('--only', help='one slug, instead of everything in the folder')
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    sources = sorted(glob.glob(os.path.join(args.source_dir, '*')))
    if args.only:
        sources = [p for p in sources
                   if os.path.splitext(os.path.basename(p))[0] == args.only]
        if not sources:
            sys.exit(f'no source named {args.only} in {args.source_dir}')

    for src in sources:
        slug = os.path.splitext(os.path.basename(src))[0]
        if slug in CUTOUTS:
            dst = os.path.join(OUT_DIR, slug + '.png')
            make_cutout(src, dst)
        else:
            dst = os.path.join(OUT_DIR, slug + '.jpg')
            make_square(src, dst)
        print(f'{slug:24s} -> assets/images/team/{os.path.basename(dst)}')


if __name__ == '__main__':
    main()
