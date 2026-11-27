# -*- coding: utf-8 -*-
"""Build the hero clip from the supplied source video.

The source runs 10 seconds. Only the first 4.5 are usable:

  0.0 - 4.6s   a seed germinating in soil, then its roots in cross-section
  4.7 - 10.0s  gold 3D lettering rotating around the sprout, reading
               "ALL FROM NA...", "NATURAL ROO..." and similar

Two reasons that tail is cut rather than shipped:

  1. The lettering is garbled, the same defect that had to be repainted off
     every bottle (see tools/relabel.py). It cannot be repainted across 130
     frames of moving, rotating 3D type.
  2. Read as intended it says the product is all from natural roots. That is
     a composition claim, and product.ingredients is unverified in config.js.
     reserve-ingredients.webp is held off the site for exactly this reason.

What is left makes no claim: soil and a seedling, which is consistent with
product.category ("Herbal food supplement for adult men"), the one thing about
the composition that is verified.

The clip is then closed into a seamless loop. The last 0.8s is dissolved into
the first 0.8s and that blend is moved to the end, so the final frame and the
first frame are the same moment and the loop has no visible cut.

Run:  python tools/build_hero_video.py
Needs ffmpeg on PATH.
"""
import os, subprocess, sys
from PIL import Image

SRC = 'source-art/hero-sprout-source.mp4'
MP4 = 'assets/video/hero-sprout.mp4'
POSTER = 'assets/img/hero-sprout-poster.webp'

CUT = 4.5    # last clean second before the lettering fades in (it starts 4.71)
FADE = 0.8   # length of the dissolve that closes the loop

FILTER = (
    "[0:v]trim=0:{cut},setpts=PTS-STARTPTS,split=3[s0][s1][s2];"
    "[s0]trim={tail}:{cut},setpts=PTS-STARTPTS[tail];"
    "[s1]trim=0:{fade},setpts=PTS-STARTPTS[head];"
    "[s2]trim={fade}:{tail},setpts=PTS-STARTPTS[mid];"
    "[tail][head]xfade=transition=fade:duration={fade}:offset=0[mix];"
    "[mid][mix]concat=n=2:v=1:a=0[v]"
).format(cut=CUT, fade=FADE, tail=round(CUT - FADE, 3))


def run(args):
    subprocess.run(args, check=True)


if __name__ == '__main__':
    if not os.path.exists(SRC):
        sys.exit('missing ' + SRC)
    os.makedirs('assets/video', exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', '-i', SRC,
         '-filter_complex', FILTER, '-map', '[v]',
         '-an',                               # silent: it autoplays
         '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
         '-crf', '25', '-preset', 'slow', '-g', '48',
         '-movflags', '+faststart', MP4])
    run(['ffmpeg', '-v', 'error', '-y', '-i', MP4,
         '-vf', r'select=eq(n\,0)', '-vframes', '1', 'poster.png'])
    Image.open('poster.png').save(POSTER, 'WEBP', quality=80, method=6)
    os.remove('poster.png')
    print('%s  %d bytes' % (MP4, os.path.getsize(MP4)))
    print('%s  %d bytes' % (POSTER, os.path.getsize(POSTER)))
