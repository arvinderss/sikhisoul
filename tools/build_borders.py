# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
from orn import svg_doc, f, P
from styles import S, H
import cairosvg
from PIL import Image, ImageDraw

OUT = sys.argv[1]; NATIVE = sys.argv[2]
for d in ('tiles', 'strips', 'motifs', '_png'):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)
index = []
for key, st in S.items():
    r = st['fn']()
    w, h, body = r['w'], r['h'], r['body']
    tile = svg_doc(w, h, f'<g clip-path="url(#c)">{body}</g>', defs=f'<clipPath id="c"><rect width="{f(w)}" height="{f(h)}"/></clipPath>', title=st['title'])
    open(f"{OUT}/tiles/{key}.svg", 'w').write(tile)
    n = max(3, int(round(560 / w)))
    W = w * n
    strip = svg_doc(W, h, f'<rect width="{f(W)}" height="{f(h)}" fill="url(#t)"/>',
                    defs=f'<pattern id="t" width="{f(w)}" height="{f(h)}" patternUnits="userSpaceOnUse">{body}</pattern>', title=st['title'])
    open(f"{OUT}/strips/{key}.svg", 'w').write(strip)
    m = None
    if r.get('motif'):
        frag, mw, mh = r['motif']
        mo = svg_doc(mw, mh, f'<g transform="translate({f(mw/2)} {f(mh*0.55 if mh<60 else mh*0.98)})">{frag}</g>', title=st['title'] + ' (motif)')
        open(f"{OUT}/motifs/{key}_motif.svg", 'w').write(mo); m = f"motifs/{key}_motif.svg"
    cairosvg.svg2png(bytestring=strip.encode(), write_to=f"{OUT}/_png/{key}.png", output_width=int(W * 1.5))
    index.append(dict(key=key, title=st['title'], source=st['src'], tile=f"tiles/{key}.svg", strip=f"strips/{key}.svg", motif=m, w=w, h=h))
json.dump(index, open(f"{OUT}/index.json", 'w'), indent=1)

# comparison sheets: reference crop (left) vs vector strip (right)
rows = []
for it in index:
    pg = int(re.search(r'p\.(\d+)', it['source']).group(1))
    im = Image.open(f"{NATIVE}/p-{pg:03d}.jpg").convert('RGB'); w, h = im.size
    ref = im.crop((int(w*.5), 0, int(w*.97), int(h*.17))); ref = ref.resize((int(ref.width*1.4), int(ref.height*1.4)))
    vec = Image.open(f"{OUT}/_png/{it['key']}.png").convert('RGB'); vec.thumbnail((620, 200))
    row = Image.new('RGB', (ref.width + 640, max(ref.height, vec.height) + 4), 'white')
    row.paste(ref, (0, 0)); row.paste(vec, (ref.width + 12, 4))
    ImageDraw.Draw(row).text((ref.width + 14, row.height - 14), it['key'] + ' ' + it['title'], fill='black')
    rows.append(row)
for si in range(0, len(rows), 6):
    ch = rows[si:si+6]; W = max(r.width for r in ch); Ht = sum(r.height + 6 for r in ch)
    sh = Image.new('RGB', (W, Ht), (220, 220, 220)); y = 0
    for r_ in ch: sh.paste(r_, (0, y)); y += r_.height + 6
    sh.save(f"{OUT}/_png/compare_{si//6+1:02d}.jpg", quality=85)
print(len(index), 'styles')
