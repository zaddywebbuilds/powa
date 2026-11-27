# -*- coding: utf-8 -*-
"""Make the delivery photograph usable by taking the card payment out of it.

The art showed a rider holding out a POS terminal while the customer offered a
bank card. `payment.cardOnDelivery` is false in config.js, so the picture was
making a claim the seller cannot keep, and it sat unused in assets/img/reserve/.

Painting the terminal and the card out was tried first and abandoned. The
background behind them is not flat: a warm door frame, a bright door gap and
the customer's own silhouette all run through it, and rebuilding ~200x150px of
that by cloning left vertical streaks across the doorway. Reconstructing the
rider's hand afterwards was worse. Nothing here can invent what was behind an
object, so the frame is moved instead of the pixels.

The frame now starts to the right of the terminal. What is left is the
customer at his own door holding the parcel: no terminal, no card, no payment
of any kind shown, and nothing in the picture that has to be true.

Run:  python tools/fix_delivery.py
"""
import os
from PIL import Image

SRC = 'source-art/ChatGPT Image Nov 26, 2026, 05_10_20 PM-9.png'
OUT = 'source-art/fixed/doorstep-handover.png'

# x0 clears the right tip of the terminal, which reaches x=558.
# y keeps his face and the parcel, and loses empty ceiling and floor.
CROP = (566, 96, 1122, 1250)

# Modest upscale: the crop is 556px wide, and the card it sits in asks for
# more than that on a 2x screen. 1.4x on this art stays clean.
SCALE = 1.4

if __name__ == '__main__':
    im = Image.open(SRC).convert('RGB').crop(CROP)
    w, h = int(im.width * SCALE), int(im.height * SCALE)
    im = im.resize((w, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT)
    print('%s  %dx%d' % (OUT, w, h))
