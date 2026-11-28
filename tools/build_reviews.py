# -*- coding: utf-8 -*-
"""Prepare the review photographs carried over from the old sales page.

The originals at /powa are 768x768 JPEGs: a photograph of a man holding the
bottle, with a white caption card composited over the bottom third carrying
the stars, the name and the quote.

Baked-in text is the wrong way to ship a review. It cannot reflow, so on a
360px phone it is either unreadably small or needs pinch-zoom; a screen reader
gets nothing; and search engines see an image. So the caption is cropped off
here and the words are rendered by the page instead, from reviews.items in
config.js, in the site's own type. Same content, same photograph, readable.

The crop line is found rather than guessed: the caption card is near white
across almost its full width, which no part of these photographs is.

    python tools/build_reviews.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'source-art' / 'reviews'
OUT = ROOT / 'assets' / 'img'

# Displayed about 300px wide in a card, so 360 covers a phone and 720 a
# desktop at 2x. Same quality tiers as the rest of the page.
WIDTHS = ((360, 72), (720, 78))

NEAR_WHITE = 228      # a pixel this bright on every channel is card, not photo
ROW_SHARE = 0.80      # ... and a row this full of them is the card
RUN = 14              # ... sustained for this many rows, so a bright sky
                      #     or a white shirt cannot be mistaken for it


def card_top(im: Image.Image) -> int:
    """First row of the composited caption card, searching the lower half."""
    px = im.convert('RGB').load()
    w, h = im.size
    step = max(1, w // 160)          # sampling is plenty at this size
    run = 0

    for y in range(h // 2, h):
        light = 0
        total = 0
        for x in range(0, w, step):
            r, g, b = px[x, y]
            total += 1
            if r >= NEAR_WHITE and g >= NEAR_WHITE and b >= NEAR_WHITE:
                light += 1
        if total and light / total >= ROW_SHARE:
            run += 1
            if run >= RUN:
                return y - RUN + 1
        else:
            run = 0

    return h          # no card found: keep the whole frame


def main() -> None:
    files = sorted(SRC.glob('*.jpeg'))
    if not files:
        raise SystemExit('no source images in %s' % SRC)

    for i, path in enumerate(files, start=1):
        im = Image.open(path)
        top = card_top(im)

        # A few pixels back from the detected edge, to clear the card's
        # rounded corner and its drop shadow.
        cut = max(1, top - 10)
        photo = im.crop((0, 0, im.width, cut))

        for width, quality in WIDTHS:
            height = max(1, round(photo.height * width / photo.width))
            name = 'review-%d-%d.webp' % (i, width)
            photo.resize((width, height), Image.LANCZOS).save(
                OUT / name, 'WEBP', quality=quality, method=6)

        kb = (OUT / ('review-%d-360.webp' % i)).stat().st_size / 1024
        print('%-18s card starts at y=%-4d photo %dx%d  (%.0f KB at 360w)'
              % (path.name, top, photo.width, photo.height, kb))

    print('')
    print('aspect ratio for the CSS: %.3f' % (photo.width / photo.height))


if __name__ == '__main__':
    main()
