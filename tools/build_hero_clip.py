# -*- coding: utf-8 -*-
"""Encode the hero clip from a supplied source.

The sprout clip had to be cut and cross-faded into a loop; see
build_hero_video.py, which is kept because that work is not reproducible from
here. This one is simpler: the supplied anatomy animation already returns to
its opening frame, measured at a mean difference of 3.4 out of 255 between the
first and last frames, so it loops on its own and needs no dissolve.

What it does need: the audio stripping, because the hero is silent and plays
without the visitor asking; two quality tiers, because the page serves phones
a lighter file; and a poster, because nothing is downloaded at all for a
visitor on Save-Data, on 2g, or who has asked for reduced motion.

The source is 462x294. That is close to right for a phone, where the hero box
is about 337 CSS px wide, and a little under what a desktop would like. It is
NOT upscaled: enlarging adds bytes without adding detail and looks worse than
letting the browser do it.

    python tools/build_hero_clip.py <source.mp4> <name>

e.g. python tools/build_hero_clip.py source-art/hero-anatomy-source.mp4 hero-anatomy
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Same tiers as the rest of the page: the phone file is cheaper, the desktop
# file is cleaner, and site.js picks between them.
DESKTOP_CRF = '26'
MOBILE_CRF = '32'
POSTER_W = 480


def run(args):
    subprocess.run(args, check=True)


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)

    src = Path(sys.argv[1])
    name = sys.argv[2]
    if not src.exists():
        raise SystemExit('missing %s' % src)

    video_dir = ROOT / 'assets' / 'video'
    img_dir = ROOT / 'assets' / 'img'
    video_dir.mkdir(parents=True, exist_ok=True)

    mp4 = video_dir / ('%s.mp4' % name)
    mp4_sm = video_dir / ('%s-480.mp4' % name)
    poster = img_dir / ('%s-poster.webp' % name)
    poster_sm = img_dir / ('%s-poster-480.webp' % name)

    common = [
        '-an',                                  # silent: it plays unasked
        '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
        '-preset', 'slow', '-g', '48', '-movflags', '+faststart',
    ]

    run(['ffmpeg', '-v', 'error', '-y', '-i', str(src)]
        + common + ['-crf', DESKTOP_CRF, str(mp4)])
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(src)]
        + common + ['-crf', MOBILE_CRF, str(mp4_sm)])

    tmp = ROOT / '_poster.png'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp4),
         '-vf', r'select=eq(n\,0)', '-vframes', '1', str(tmp)])

    im = Image.open(tmp).convert('RGB')
    im.save(poster, 'WEBP', quality=80, method=6)
    sm = im.resize((POSTER_W, round(im.height * POSTER_W / im.width)), Image.LANCZOS)
    sm.save(poster_sm, 'WEBP', quality=72, method=6)
    os.remove(tmp)

    print('source   %dx%d' % (im.width, im.height))
    for f in (mp4, mp4_sm, poster, poster_sm):
        print('%-40s %7d bytes' % (f.relative_to(ROOT).as_posix(), f.stat().st_size))


if __name__ == '__main__':
    main()
