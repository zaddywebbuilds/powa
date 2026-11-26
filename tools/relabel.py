# -*- coding: utf-8 -*-
"""
Repaint the garbled text on the Knack Extra bottle artwork.

The supplied AI art prints nonsense on the bullet band of every bottle
("Casual In Sexuit Penfarinione", "Stemm Mattural Blrength", and a legible
"Makes Erection Strong" claim). This rebuilds that band from the clean label
rows above and below it, then prints three lines that are true and that are
backed by assets/js/config.js:

    Herbal food supplement          <- product.category, verified
    For adult men, 18 and over      <- product.warnings[0], verified
    Not a medicine. Read the label. <- legal.disclaimer

It does not touch "KNACK EXTRA CAPSULES", "100% HERBAL PRODUCT" or
"30 CAPSULES". Those are legible already; the pack size is still unverified
and is tracked in LAUNCH-CHECKLIST.md.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = 'source-art'
FONT = r'C:\Windows\Fonts\ARIALNB.TTF'

LINES = ["Herbal food supplement",
         "For adult men, 18 and over",
         "Not a medicine. Read the label."]


def load(path):
    im = Image.open(os.path.join(SRC, path))
    alpha = im.getchannel('A') if im.mode == 'RGBA' else None
    return im.convert('RGB'), alpha


def detect(arr, x0, x1, seed, lmin, smax, gap, win):
    """Per-column top/bottom of the cream band, walking out from `seed`.

    `win` bounds the search so a column that misses the dark panel (the thin
    cream margin at the label edge) cannot run away up the bottle."""
    L = arr.mean(2)
    sat = arr.max(2) - arr.min(2)
    cream = (L > lmin) & (sat < smax)
    ymin, ymax = win
    tops, bots = [], []
    for x in range(x0, x1 + 1):
        col = cream[:, x]
        t = seed
        miss = 0
        y = seed
        while y > ymin:
            y -= 1
            if col[y]:
                t = y; miss = 0
            else:
                miss += 1
                if miss > gap: break
        b = seed
        miss = 0
        y = seed
        while y < ymax:
            y += 1
            if col[y]:
                b = y; miss = 0
            else:
                miss += 1
                if miss > gap: break
        tops.append(t); bots.append(b)
    return np.array(tops), np.array(bots)


def fit(a, deg=2):
    """Robust polynomial through a detected edge.

    The band edge is a smooth curve on a cylinder, so fitting it removes the
    column-to-column wobble that the detector picks up where the old text ran
    close to the boundary. Wobble would make the new text bounce.
    """
    x = np.arange(len(a), dtype=float)
    y = a.astype(float)
    keep = np.ones(len(a), bool)
    for _ in range(3):
        c = np.polyfit(x[keep], y[keep], deg)
        r = y - np.polyval(c, x)
        s = max(np.std(r[keep]), 0.5)
        keep = np.abs(r) < 2.0 * s
        if keep.sum() < deg + 2:
            break
    return np.polyval(np.polyfit(x[keep], y[keep], deg), x)


def build_strip(w, h, lines, checks, supers=3, color=(38, 36, 34)):
    """Flat artwork for the band: optional gold ticks plus the three lines."""
    W, H = w * supers, h * supers
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rows = len(lines)
    lh = H / rows
    left = W * 0.035
    tick_w = lh * 0.62 if checks else 0.0
    gap = lh * 0.22 if checks else 0.0
    tx = left + tick_w + gap
    avail = W - tx - W * 0.03

    cap = int(lh * 0.70)
    size = 6
    while size < cap:
        f = ImageFont.truetype(FONT, size + 1)
        if max(d.textlength(s, font=f) for s in lines) > avail * 0.97:
            break
        size += 1
    f = ImageFont.truetype(FONT, size)

    for i, s in enumerate(lines):
        cy = lh * (i + 0.5)
        if checks:
            s_ = tick_w
            ox, oy = left, cy - s_ / 2
            d.line([(ox + .16 * s_, oy + .50 * s_), (ox + .40 * s_, oy + .76 * s_),
                    (ox + .90 * s_, oy + .14 * s_)],
                   fill=(176, 126, 36, 255), width=max(2, int(s_ * .17)), joint='curve')
        d.text((tx, cy), s, font=f, fill=color + (255,), anchor='lm')

    return img.resize((w, h), Image.LANCZOS)


def _hblur(a, w):
    pad = w // 2
    p = np.pad(a, ((0, 0), (pad + 1, pad), (0, 0)), mode='edge')
    c = np.cumsum(p, axis=1)
    return (c[:, w:] - c[:, :-w]) / float(w)


def smear(arr, box, w=41, thr=10.0, feather=10):
    """Wipe lettering out of a region without softening the region itself.

    Used on the shrink-wrap cap and on the mirrored reflection, where the art
    prints nonsense. The replacement is the same pixels blurred along the
    horizontal axis only, so the cap ridges and the bottle edge stay sharp and
    only the letterforms dissolve into the band they sit on.
    """
    x0, y0, x1, y1 = box
    reg = arr[y0:y1, x0:x1]
    bg = _hblur(reg, w)
    d = np.abs(reg.mean(2) - bg.mean(2))
    m = np.clip((d - thr) / max(thr, 1.0), 0, 1)
    m = _hblur(m[:, :, None], 5)[:, :, 0]
    h, ww = m.shape
    fy = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / float(feather), 0, 1)
    fx = np.clip(np.minimum(np.arange(ww), ww - 1 - np.arange(ww)) / float(feather), 0, 1)
    m = m * fy[:, None] * fx[None, :]
    reg[:] = reg * (1 - m[:, :, None]) + bg * m[:, :, None]


def bar(arr, box, pct=80.0, text='', color=(20, 20, 20), frac=0.62,
        track=0.0, noise=1.2, font=None):
    """Reprint one horizontal bar of a badge.

    The bar is rebuilt from its own pixels: for each row, the pct-th
    percentile across the bar is the colour of the bar without the lettering
    on it (high percentile for dark text on gold, low for white text on navy).
    The new text is then set on the rebuilt bar.
    """
    x0, y0, x1, y1 = box
    reg = arr[y0:y1, x0:x1]
    prof = np.percentile(reg, pct, axis=1)                      # (rows, 3)
    rng = np.random.default_rng(11)
    reg[:] = prof[:, None, :] + rng.normal(0, noise, reg.shape)
    if not text:
        return
    w, h = x1 - x0, y1 - y0
    sup = 3
    layer = Image.new('RGBA', (w * sup, h * sup), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = int(h * sup * frac)
    f = ImageFont.truetype(font or FONT, size)
    sp = int(size * track)
    while size > 6:
        wd = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
        if wd <= w * sup * 0.92:
            break
        size -= 2
        f = ImageFont.truetype(font or FONT, size)
        sp = int(size * track)
    wd = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
    x = (w * sup - wd) / 2.0
    for c in text:
        d.text((x, h * sup / 2.0), c, font=f, fill=tuple(color) + (255,), anchor='lm')
        x += d.textlength(c, font=f) + sp
    small = np.asarray(layer.resize((w, h), Image.LANCZOS)).astype(float) / 255.0
    a = small[:, :, 3:4]
    reg[:] = np.clip(reg * (1 - a) + small[:, :, :3] * 255.0 * a, 0, 255)


def deblue(arr, strength=1.0, knee=26.0, cast=(0.95, 1.02, 0.93)):
    """Pull a blue cast out of an image and leave a near-neutral dark.

    The badge art is navy, which is not a colour this site uses anywhere.
    Only pixels that are actually blue are touched, so the gold keeps its
    warmth and the lighting stays where the artist put it.
    """
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    m = np.clip((b - np.maximum(r, g)) / float(knee), 0, 1) * strength
    lum = 0.34 * r + 0.52 * g + 0.14 * b
    for i, k in enumerate(cast):
        arr[:, :, i] = arr[:, :, i] * (1 - m) + lum * k * m


def soften(arr, box, radius=6.0, feather=14):
    """Blur a region behind a feathered edge.

    Only used on the mirrored reflection under the bottle, where the art
    repeats the nonsense upside down. A reflection reading softer than the
    object above it is what a reflection does anyway.
    """
    from PIL import ImageFilter
    x0, y0, x1, y1 = box
    reg = arr[y0:y1, x0:x1]
    b = np.asarray(Image.fromarray(np.clip(reg, 0, 255).astype('uint8'))
                   .filter(ImageFilter.GaussianBlur(radius))).astype(float)
    h, w = y1 - y0, x1 - x0
    H, W = arr.shape[0], arr.shape[1]
    # An edge that sits on the image border needs no feather: there is nothing
    # beyond it to blend into, and feathering there leaves a readable sliver.
    def ramp(n, lo, hi):
        a = np.arange(n, dtype=float)
        u = np.full(n, 1e9) if not lo else a
        v = np.full(n, 1e9) if not hi else (n - 1 - a)
        return np.clip(np.minimum(u, v) / float(feather), 0, 1)
    fy = ramp(h, y0 > 0, y1 < H)
    fx = ramp(w, x0 > 0, x1 < W)
    m = (fy[:, None] * fx[None, :])[:, :, None]
    reg[:] = reg * (1 - m) + b * m


def paint(arr, x0, tops, bots, strip, pad, noise=1.4, rng=None):
    """Rebuild the band from its clean edge rows, then lay the strip over it."""
    sa = np.asarray(strip).astype(float) / 255.0
    Hs = sa.shape[0]
    rng = rng or np.random.default_rng(7)
    for i in range(len(tops)):
        x = x0 + i
        t, b = int(round(tops[i])), int(round(bots[i]))
        a, z = t + pad, b - pad
        if z - a < 6: continue
        up = arr[max(t + 1, a - 2):a + 1, x].mean(0)
        dn = arr[z:min(b, z + 3), x].mean(0)
        n = z - a + 1
        w = np.linspace(0, 1, n)[:, None]
        base = up[None, :] * (1 - w) + dn[None, :] * w
        base += rng.normal(0, noise, base.shape)

        idx = np.linspace(0, Hs - 1, n)
        i0 = np.floor(idx).astype(int)
        i1 = np.minimum(i0 + 1, Hs - 1)
        fw = (idx - i0)[:, None]
        col = sa[i0, i] * (1 - fw) + sa[i1, i] * fw
        al = col[:, 3:4]
        arr[a:z + 1, x] = np.clip(base * (1 - al) + col[:, :3] * 255.0 * al, 0, 255)


def run(spec, debug=None):
    im, alpha = load(spec['src'])
    arr = np.asarray(im).astype(float)
    for band in spec['bands']:
        x0, x1 = band['x']
        tops, bots = detect(arr, x0, x1, band['seed'],
                            band.get('lmin', 150), band.get('smax', 72),
                            band.get('gap', 20), band['win'])
        tops, bots = fit(tops, band.get('deg', 2)), fit(bots, band.get('deg', 2))
        h = int(round((bots - tops).mean()))
        pad = band.get('pad', 3)
        strip = build_strip(x1 - x0 + 1, max(h - 2 * pad, 8),
                            band.get('lines', LINES), band.get('checks', True),
                            color=band.get('color', (38, 36, 34)))
        paint(arr, x0, tops, bots, strip, pad, band.get('noise', 1.4))
        if debug is not None:
            debug.append((x0, tops, bots))
    if 'deblue' in spec:
        deblue(arr, **spec['deblue'])
    for b in spec.get('bars', []):
        bar(arr, b['box'], b.get('pct', 80.0), b.get('text', ''),
            b.get('color', (20, 20, 20)), b.get('frac', 0.62),
            b.get('track', 0.0), b.get('noise', 1.2), b.get('font'))
    for bl in spec.get('blur', []):
        soften(arr, bl['box'], bl.get('radius', 6.0), bl.get('feather', 14))
    for sm in spec.get('smear', []):
        smear(arr, sm['box'], sm.get('w', 41), sm.get('thr', 10.0), sm.get('feather', 10))
    out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGB')
    if alpha is not None:
        out = out.convert('RGBA'); out.putalpha(alpha)
    return out
