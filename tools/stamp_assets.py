# -*- coding: utf-8 -*-
"""Stamp the CSS and JS links in the static pages with a content hash.

GitHub Pages serves assets with a cache lifetime of its own, and the HTML is
revalidated far more often than the files it points at. That used to be
harmless. It is not any more: the hero video has no `src` in the markup, so a
visitor holding a stale site.js now gets new HTML, no video source, and no
video. The package thumbnails quietly fall back to the full size art for the
same reason.

Appending ?v=<hash of the file> makes the URL change whenever the file does,
so a stale copy can never be paired with fresh HTML. Running it twice is
harmless; the old stamp is replaced, not appended to.

    python tools/stamp_assets.py

The WordPress build does not need this: inc/assets.php versions every
enqueue with the file's own modification time.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = ['index.html', 'policies.html', 'thank-you.html']
ASSETS = ['assets/css/site.css', 'assets/js/site.js', 'assets/js/config.js']


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def main() -> None:
    stamps = {}
    for rel in ASSETS:
        p = ROOT / rel
        if p.exists():
            stamps[rel] = digest(p)

    for page in PAGES:
        path = ROOT / page
        if not path.exists():
            continue
        html = path.read_text(encoding='utf-8')
        before = html

        for rel, h in stamps.items():
            # Matches the bare path and any stamp already on it.
            pattern = re.compile(re.escape(rel) + r'(\?v=[0-9a-f]+)?')
            html = pattern.sub(rel + '?v=' + h, html)

        if html != before:
            path.write_text(html, encoding='utf-8')
            print('%-16s stamped' % page)
        else:
            print('%-16s unchanged' % page)

    for rel, h in stamps.items():
        print('  %-22s %s' % (rel, h))


if __name__ == '__main__':
    main()
