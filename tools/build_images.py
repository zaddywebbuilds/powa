# -*- coding: utf-8 -*-
"""Rebuild the served WebP variants for the retouched bottle artwork.

Sizes come from assets/img/_manifest.json so the <img width/height> and the
srcset widths already in the HTML stay correct. Transparent art is trimmed to
its alpha bounding box first, the same way the originals were.
"""
import json, os, sys
from PIL import Image

MAN = 'assets/img/_manifest.json'
FIXED = 'source-art/fixed'
Q = 82

def main(names):
    man = json.load(open(MAN))
    for name in names:
        info = man[name]
        im = Image.open(os.path.join(FIXED, name + '.png'))
        if im.mode == 'RGBA':
            im = im.crop(im.getchannel('A').getbbox())
        out_dir = 'assets/img' if info['dir'] == 'img' else 'assets/img/reserve'
        for v in info['variants']:
            r = im.resize((v['w'], v['h']), Image.LANCZOS)
            p = os.path.join(out_dir, v['file'])
            r.save(p, 'WEBP', quality=Q, method=6)
            print('%-26s %5dx%-5d %7d bytes' % (v['file'], v['w'], v['h'], os.path.getsize(p)))

if __name__ == '__main__':
    main(sys.argv[1:] or ['hero-dark', 'hero-dark-alt', 'product-hero',
                          'product-usage', 'bundle-one', 'bundle-two', 'bundle-three'])
