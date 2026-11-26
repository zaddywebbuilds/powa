# -*- coding: utf-8 -*-
"""Measuring aid: crop a region of a source image and overlay a pixel grid.

Used to read off the coordinates that fix_labels.py needs. Writes into the
scratch directory, never into the repo.
"""
import sys, os
from PIL import Image, ImageDraw
SCR = r"C:\Users\Johno\AppData\Local\Temp\claude\1b1e7f6bbd8b2c00\3ade23b7-ec85-41d8-ab3f-18d38702bf47\scratchpad"

def load(path):
    im = Image.open(path)
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, (255, 255, 255))
        bg.paste(im, mask=im.getchannel('A'))
        return bg
    return im.convert('RGB')

def grid(path, box, out, step=25, zoom=2):
    im = load(path)
    c = im.crop(box).resize(((box[2]-box[0])*zoom, (box[3]-box[1])*zoom), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for x in range(box[0] - box[0] % step, box[2], step):
        px = (x-box[0])*zoom
        if px < 0: continue
        d.line([(px,0),(px,c.height)], fill=(0,255,0))
        d.text((px+2,2), str(x), fill=(0,255,0))
    for y in range(box[1] - box[1] % step, box[3], step):
        py = (y-box[1])*zoom
        if py < 0: continue
        d.line([(0,py),(c.width,py)], fill=(255,0,255))
        d.text((2,py+2), str(y), fill=(255,0,255))
    p = os.path.join(SCR, out)
    c.save(p); print(p, c.size)
