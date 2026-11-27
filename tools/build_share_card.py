# -*- coding: utf-8 -*-
"""Build the link preview image.

Every image the page serves is WebP, which is right for the page and wrong for
a shared link: WhatsApp does not render a WebP og:image at all, and several
other clients are unreliable with it. So the share card is a JPEG, and it is
the only JPEG in the project.

1200x630 is the size Facebook, WhatsApp, LinkedIn, Slack and X all accept as a
large preview card. Anything smaller than 600x315 is shown as a small
thumbnail instead, and WhatsApp drops images over about 600 KB.

The picture is the bottle on its dark background, cropped from the retouched
artwork. No text is composited on top: the label already carries the brand
name, and a share card is exactly the place where an unevidenced line would
travel furthest.

    python tools/build_share_card.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_PNG = ROOT / 'source-art' / 'fixed' / 'hero-dark.png'
SRC_WEBP = ROOT / 'assets' / 'img' / 'hero-dark.webp'
OUT = ROOT / 'assets' / 'img' / 'share-card.jpg'

WIDTH, HEIGHT = 1200, 630
QUALITY = 82


def source() -> Image.Image:
    if SRC_PNG.exists():
        im = Image.open(SRC_PNG)
        if im.mode == 'RGBA':
            im = im.crop(im.getchannel('A').getbbox())
        return im.convert('RGB')
    return Image.open(SRC_WEBP).convert('RGB')


def main() -> None:
    im = source()
    target = WIDTH / HEIGHT

    # Centre crop to the card's aspect ratio, then scale. The artwork is
    # 1.78:1 and the card is 1.90:1, so this trims a little off the top and
    # bottom rather than squeezing the bottle.
    if im.width / im.height > target:
        w = int(round(im.height * target))
        box = ((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height)
    else:
        h = int(round(im.width / target))
        box = (0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h)

    card = im.crop(box).resize((WIDTH, HEIGHT), Image.LANCZOS)
    card.save(OUT, 'JPEG', quality=QUALITY, optimize=True, progressive=True)

    print('%s  %dx%d  %.0f KB' % (OUT.name, WIDTH, HEIGHT, OUT.stat().st_size / 1024))


if __name__ == '__main__':
    main()
