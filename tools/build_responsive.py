# -*- coding: utf-8 -*-
"""Build a responsive image ladder sized from how the page actually renders.

98% of the traffic is mobile, much of it on a weak network, and the old two
step ladder was costing a fortune there. A 375px phone at device pixel ratio 2
downloaded 1,490 KB of images, because:

  * the small variants stopped at 604-716px, below what a DPR 2 phone asks
    for, so the browser skipped straight to the 1100-1672px originals;
  * the `sizes` attributes were hand-written guesses in vw, several of which
    overstated the slot badly enough to push the choice up a tier anyway;
  * the three package thumbnails are 94px wide on a phone and were loading the
    full 760px bundle art, about 250 KB for three postage stamps.

SLOTS below is measured, not guessed: each row is the rendered CSS width of
that image at five viewport widths, read out of the live page with
getBoundingClientRect.

WHY <picture> AND NOT JUST srcset
---------------------------------
srcset multiplies `sizes` by the device's own pixel ratio, and there is no way
to tell it to stop at 1.6. On a DPR 3 phone an honest `sizes` fetches three
device pixels per CSS pixel, which is most of the weight on this page and is
invisible at arm's length. So the phone and tablet bands are served as
<source media> entries, which name one exact file and ignore DPR entirely, and
only the desktop bands keep a DPR-aware srcset. Deterministic beats clever
when the connection is the constraint.

    python tools/build_responsive.py            # build and rewrite index.html
    python tools/build_responsive.py --dry-run  # print the plan, touch nothing

Re-measure if the layout changes materially; the snippet is in README.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / 'assets' / 'img'
FIXED = ROOT / 'source-art' / 'fixed'
MANIFEST = IMG / '_manifest.json'
INDEX = ROOT / 'index.html'

# Viewport widths the slots were measured at.
BREAKPOINTS = [360, 600, 768, 1120, 1440]

# Media bands, as (max-width or None, index into the measurement row).
BANDS = [(420, 0), (680, 1), (900, 2), (1200, 3), (None, 4)]

# The top of each band, so a slot measured at 360 is scaled to what it becomes
# at 420 before anything is decided from it.
BAND_TOP = [420, 680, 900, 1200, 1440]

# Bands at or below this are served one exact file through <source media>.
MOBILE_BAND_MAX = 900

# Device pixels per CSS pixel. Phones get 1.4; desktop, 2% of the traffic and
# usually on a better connection, gets 2. Because each band is sized for the
# TOP of its range and then snapped up to a ladder step, a 360px phone ends up
# nearer 1.7 in practice, which is the number that actually matters.
DPR_MOBILE = 1.4
DPR_DESKTOP = 2.0

LADDER = [160, 200, 260, 320, 400, 480, 560, 680, 820, 1000, 1200, 1440, 1672]

# Rendered CSS width of each image at BREAKPOINTS.
SLOTS = {
    'bundle-one':        [94, 94, 94, 268, 316],
    'bundle-two':        [94, 94, 94, 268, 316],
    'bundle-three':      [94, 94, 94, 268, 316],
    'confident-man':     [324, 552, 692, 508, 657],
    'discreet-delivery': [324, 552, 692, 508, 657],
    'doorstep-handover': [322, 550, 338, 326, 374],
    'happy-couple':      [322, 550, 338, 326, 374],
    'hero-dark':         [244, 472, 612, 279, 331],
    'hero-dark-alt':     [322, 550, 690, 463, 531],
    'mature-man':        [322, 550, 221, 326, 374],
    'package-podium':    [244, 472, 612, 333, 393],
    'product-hero':      [324, 552, 692, 508, 657],
    'product-usage':     [322, 550, 338, 326, 374],
    'researching-man':   [242, 188, 258, 221, 265],
    'returns-badge':     [244, 472, 612, 317, 375],
    'supportive-couple': [322, 550, 221, 326, 374],
    'thoughtful-man':    [242, 188, 258, 221, 265],
    'trusted-friends':   [322, 550, 221, 326, 374],
}


def quality_for(width: int) -> int:
    """Smaller variants are shown smaller, so they take more compression."""
    if width <= 480:
        return 70
    if width <= 820:
        return 74
    if width <= 1100:
        return 80
    return 82


def band_slot(name: str, i: int) -> int:
    measured = SLOTS[name][i]
    scaled = measured * (BAND_TOP[i] / BREAKPOINTS[i])
    return int(round(max(measured, scaled) * 1.04))


def snap(need: int, src_w: int) -> int:
    for step in LADDER:
        if step >= need:
            return min(step, src_w)
    return src_w


def plan(name: str, src_w: int, src_h: int) -> dict:
    mobile = []          # [(max_width, variant_width)]
    desktop_w = []       # widths for the img's own srcset
    desktop_sizes = []

    for (max_w, i) in BANDS:
        slot = band_slot(name, i)
        if max_w is not None and max_w <= MOBILE_BAND_MAX:
            mobile.append((max_w, snap(int(round(slot * DPR_MOBILE)), src_w)))
        else:
            desktop_w.append(snap(int(round(slot * DPR_DESKTOP)), src_w))
            desktop_sizes.append(
                '%dpx' % slot if max_w is None
                else '(max-width:%dpx) %dpx' % (max_w, slot))

    # Consecutive bands that land on the same file collapse into one source.
    collapsed = []
    for max_w, w in mobile:
        if collapsed and collapsed[-1][1] == w:
            collapsed[-1] = (max_w, w)
        else:
            collapsed.append((max_w, w))

    widths = sorted(set([w for _, w in collapsed] + desktop_w))
    heights = {w: max(1, int(round(w * src_h / src_w))) for w in widths}

    return {
        'mobile': collapsed,
        'desktop_widths': sorted(set(desktop_w)),
        'desktop_sizes': ', '.join(desktop_sizes),
        'widths': widths,
        'heights': heights,
        'src_w': src_w,
    }


def variant_file(name: str, w: int, src_w: int) -> str:
    return '%s.webp' % name if w == src_w else '%s-%d.webp' % (name, w)


def source_image(name: str, man: dict) -> Image.Image:
    """The retouched art where it exists, else the largest WebP.

    Downscaling a WebP is lossy on lossy, but every variant it feeds is
    smaller than it is, and the resample hides more than it adds.
    """
    png = FIXED / (name + '.png')
    if png.exists():
        im = Image.open(png)
        if im.mode == 'RGBA':
            im = im.crop(im.getchannel('A').getbbox())
        return im.convert('RGB')

    # The lifestyle photographs have no PNG behind them, so the unsuffixed
    # WebP is the only full resolution copy that exists. It is kept on disk
    # whether or not the page still links to it; see prune().
    original = IMG / (name + '.webp')
    if original.exists():
        return Image.open(original).convert('RGB')

    biggest = max(man[name]['variants'], key=lambda v: v['w'])
    return Image.open(IMG / biggest['file']).convert('RGB')


def build(dry: bool) -> dict:
    man = json.loads(MANIFEST.read_text(encoding='utf-8'))
    plans = {}
    made = 0

    for name in sorted(SLOTS):
        info = man[name]
        src_w = max(v['w'] for v in info['variants'])
        src_h = [v['h'] for v in info['variants'] if v['w'] == src_w][0]

        p = plan(name, src_w, src_h)
        wanted = {}
        im = None

        for w in p['widths']:
            fname = variant_file(name, w, src_w)
            path = IMG / fname
            wanted[w] = fname
            if path.exists() and w == src_w:
                continue
            if dry:
                continue
            if im is None:
                im = source_image(name, man)
            im.resize((w, p['heights'][w]), Image.LANCZOS).save(
                path, 'WEBP', quality=quality_for(w), method=6)
            made += 1

        # Never delete the unsuffixed original. For most of these images it is
        # the only full resolution copy in the repository, and every smaller
        # variant is resampled from it.
        keep = set(wanted.values()) | {name + '.webp'}
        for v in info['variants']:
            if v['file'] not in keep:
                stale = IMG / v['file']
                if stale.exists() and not dry:
                    stale.unlink()

        info['variants'] = [
            {'file': wanted[w], 'w': w, 'h': p['heights'][w]} for w in p['widths']
        ]
        p['files'] = wanted
        plans[name] = p

        print('%-19s mobile %-28s desktop %s'
              % (name,
                 ', '.join('<=%s:%s' % (mw, w) for mw, w in p['mobile']),
                 p['desktop_widths']))

    # The package thumbnails are built in JavaScript, so their <picture> is
    # written out by hand in site.js. This keeps the two honest about each
    # other: if the ladder moves, the build stops and says what to change.
    bundle = plans['bundle-one']
    expected = {'mobile': [(680, 160), (900, 200)], 'widths': [160, 200, 680]}
    actual = {'mobile': bundle['mobile'], 'widths': bundle['widths']}
    assert actual == expected, (
        'package thumbnail ladder moved.' + chr(10)
        + '  expected %s' % expected + chr(10)
        + '  got      %s' % actual + chr(10)
        + '  update renderPackages() and updateSummary() in assets/js/site.js')

    if not dry:
        MANIFEST.write_text(json.dumps(man, indent=1), encoding='utf-8')
    print('')
    print('variants written: %d' % made)
    return plans


# ------------------------------------------------------------ the markup ---

BLOCK = re.compile(
    r'<picture>[ \r\n]*(?:<source[^>]*>[ \r\n]*)*<img\b[^>]*>[ \r\n]*</picture>'
    r'|<img\b[^>]*>',
    re.I)


def rewrite_html(plans: dict, dry: bool) -> int:
    html = INDEX.read_text(encoding='utf-8')
    changed = 0

    def fix(m):
        nonlocal changed
        block = m.group(0)
        tag = re.search(r'<img\b[^>]*>', block, re.I).group(0)

        # The order summary thumbnail is 54px and site.js swaps it as the
        # package changes, so it keeps a single small file of its own.
        if 'id="sum-img"' in tag:
            out = re.sub(r'\ssrc="[^"]*"',
                         ' src="assets/img/bundle-one-160.webp"', tag)
            if out != block:
                changed += 1
            return out

        src = re.search(r'src="assets/img/([A-Za-z0-9\-]+?)(?:-\d+)?\.webp"', tag)
        if not src or src.group(1) not in plans:
            return block
        name = src.group(1)
        p = plans[name]

        top = p['widths'][-1]
        new_tag = re.sub(r'\ssrc="[^"]*"',
                         ' src="assets/img/%s"' % p['files'][top], tag)

        desktop_srcset = ', '.join(
            'assets/img/%s %dw' % (p['files'][w], w) for w in p['desktop_widths'])

        for attr, value in (('srcset', desktop_srcset), ('sizes', p['desktop_sizes'])):
            if re.search(r'\s%s="' % attr, new_tag):
                new_tag = re.sub(r'\s%s="[^"]*"' % attr,
                                 ' %s="%s"' % (attr, value), new_tag)
            else:
                new_tag = new_tag.replace(' src="',
                                          ' %s="%s" src="' % (attr, value), 1)

        new_tag = re.sub(r'\swidth="\d+"', ' width="%d"' % top, new_tag)
        new_tag = re.sub(r'\sheight="\d+"',
                         ' height="%d"' % p['heights'][top], new_tag)

        sources = ''.join(
            '<source media="(max-width:%dpx)" srcset="assets/img/%s">'
            % (mw, p['files'][w]) for mw, w in p['mobile'])

        out = '<picture>%s%s</picture>' % (sources, new_tag)
        if out != block:
            changed += 1
        return out

    new = BLOCK.sub(fix, html)
    if not dry and new != html:
        INDEX.write_text(new, encoding='utf-8')
    print('image blocks rewritten: %d' % changed)
    return changed


def main() -> None:
    dry = '--dry-run' in sys.argv
    plans = build(dry)
    rewrite_html(plans, dry)


if __name__ == '__main__':
    main()
