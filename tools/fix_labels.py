# -*- coding: utf-8 -*-
"""Rebuild the bullet band on every bottle in the artwork. See relabel.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relabel as R
from PIL import Image

OUT = 'source-art/fixed'

SPECS = {
 'hero-dark': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_09_47 PM-1.png',
   'bands': [{'x': (972, 1334), 'seed': 655, 'win': (600, 712), 'pad': 4}]},

 'hero-dark-alt': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_22 PM-10.png',
   'bands': [{'x': (225, 560), 'seed': 620, 'win': (575, 675), 'pad': 4}],
   'blur': [{'box': (178, 858, 636, 941), 'radius': 7.0, 'feather': 18}]},

 'product-hero': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_22 PM-1.png',
   'bands': [{'x': (312, 812), 'seed': 940, 'win': (865, 1020), 'pad': 5}]},

 'product-usage': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_29 PM-5.png',
   'bands': [{'x': (288, 592), 'seed': 845, 'win': (795, 892), 'pad': 4,
              'checks': False, 'lmin': 140, 'smax': 80}],
   'smear': [{'box': (274, 278, 616, 466), 'w': 65, 'thr': 5.0, 'feather': 16}]},

 'bundle-one': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_09_56 PM-6.png',
   'bands': [{'x': (345, 900), 'seed': 930, 'win': (855, 1010), 'pad': 5}]},

 'bundle-two': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_09_58 PM-7.png',
   'bands': [{'x': (166, 656), 'seed': 905, 'win': (845, 975), 'pad': 4},
             {'x': (690, 1082), 'seed': 895, 'win': (820, 965), 'pad': 4,
              'checks': False}]},

 'bundle-three': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_19 PM-8.png',
   'bands': [{'x': (392, 862), 'seed': 880, 'win': (805, 960), 'pad': 4},
             {'x': (66, 378), 'seed': 830, 'win': (778, 892), 'pad': 3},
             {'x': (884, 1168), 'seed': 830, 'win': (778, 892), 'pad': 3}]},
 'returns-badge': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_31 PM-6.png',
   'bands': [{'x': (106, 458), 'seed': 905, 'win': (855, 968), 'pad': 4,
              'checks': False}],
   # The art prints "100% MONEY BACK GUARANTEED", which the seller has no
   # written conditions behind. The 14 day window in config.js is the one
   # returns fact that is verified, so that is what the badge now says.
   'deblue': {'strength': 1.0, 'knee': 26.0},
   'bars': [{'box': (503, 583, 809, 646), 'pct': 18.0, 'text': 'RETURNS',
             'color': (248, 245, 238), 'frac': 0.58, 'track': 0.10},
            {'box': (499, 648, 812, 727), 'pct': 72.0, 'text': '14 DAYS',
             'color': (16, 24, 48), 'frac': 0.78},
            {'box': (503, 729, 809, 788), 'pct': 18.0, 'text': 'FROM DELIVERY',
             'color': (236, 232, 224), 'frac': 0.44, 'track': 0.16}],
   'blur': [{'box': (96, 1146, 486, 1268), 'radius': 6.0, 'feather': 18}]},

 # Six bottles, all carrying the same nonsense. Each band is rebuilt and
 # reset in fine print, the same three lines as every other bottle.
 'package-podium': {
   'src': 'ChatGPT Image Nov 26, 2026, 05_10_33 PM-7.png',
   'bands': [{'x': (84, 258), 'seed': 798, 'win': (768, 830), 'pad': 2, 'checks': False},
             {'x': (399, 572), 'seed': 798, 'win': (768, 830), 'pad': 2, 'checks': False},
             {'x': (568, 682), 'seed': 792, 'win': (768, 820), 'pad': 2, 'checks': False, 'deg': 1},
             {'x': (750, 842), 'seed': 796, 'win': (775, 821), 'pad': 2, 'checks': False, 'deg': 1},
             {'x': (841, 1032), 'seed': 798, 'win': (770, 830), 'pad': 2, 'checks': False},
             ],
   # A sliver of a sixth bottle sits in shadow behind the fifth. Too little of
   # its band is visible to reset cleanly, so it is thrown out of focus, which
   # is where a bottle that far back would be anyway.
   'blur': [{'box': (1024, 762, 1118, 832), 'radius': 4.0, 'feather': 10}]},
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:] or list(SPECS)
    for name in only:
        spec = SPECS[name]
        dbg = []
        im = R.run(spec, dbg)
        im.save(os.path.join(OUT, name + '.png'))
        for i, (x0, t, b) in enumerate(dbg):
            print('%-14s band %d  x %d..%d  top %.0f..%.0f  bot %.0f..%.0f  h %.0f'
                  % (name, i, x0, x0 + len(t) - 1, t[0], t[-1], b[0], b[-1], (b - t).mean()))
