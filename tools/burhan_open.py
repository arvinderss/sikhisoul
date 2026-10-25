# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""Burhanpuri saroop opening-spread illumination (pp.7-8), reconstructed as vector components."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from orn import *

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GOLD = '#CCA457'; GOLD_L = '#E3C47E'; GOLD_D = '#8E6A2B'; LAP = '#3D5A9A'; LAP_D = '#2A3F72'; LAP_L = '#7E95C8'
RED = '#C2343C'; PINK = '#D9607E'; ROSE = '#E796A8'; GREEN = '#6E8F4E'; INK = '#3A2A1C'; MAROON = '#9B2E46'

def sprinkle(x0, y0, x1, y1, n, seed, pal=(RED, PINK, RED, ROSE), r=(1.6, 3.2), clip=None):
    rnd = random.Random(seed); s = ''
    for _ in range(n):
        x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1); rr = rnd.uniform(*r); c = rnd.choice(pal)
        if rnd.random() < .45:
            s += g(x, y, rosette(5, rr * 1.6, rr * .7, c, rr * .4, GOLD_L))
        else:
            s += circle(x, y, rr * .7, c)
            s += g(x + rr, y - rr, leaf(rr * 2.4, rr * .8, GREEN), rot=rnd.uniform(0, 360))
    return s

def scrolls(x0, y0, x1, y1, step, col=GOLD_D, sw=.8, seed=1):
    """field of tight spiral scrolls (gold-on-gold arabesque)"""
    s = ''; rnd = random.Random(seed); y = y0 + step / 2; row = 0
    while y < y1:
        x = x0 + (step / 2 if row % 2 else 0) + step / 2
        while x < x1:
            r = step * .42; a0 = rnd.uniform(0, 6.28)
            d = f"M{f(x + r*math.cos(a0))} {f(y + r*math.sin(a0))}"
            for i in range(1, 24):
                a = a0 + i * .38; rr = r * (1 - i / 26)
                d += f" L{f(x + rr*math.cos(a))} {f(y + rr*math.sin(a))}"
            s += path(d, 'none', col, sw)
            x += step
        y += step * .86; row += 1
    return s

def quatrefoil(cx, cy, r, fill, stroke, inner=None):
    s = ''
    for a in (0, 90, 180, 270):
        ax, ay = math.cos(math.radians(a)) * r * .5, math.sin(math.radians(a)) * r * .5
        s += circle(cx + ax, cy + ay, r * .52, fill, stroke, .8)
    s += lozenge(cx, cy, r * 1.1, r * 1.1, fill)
    if inner: s += g(cx, cy, rosette(4, r * .55, r * .22, inner, r * .14, GOLD_L, rot0=45))
    return s

def lobed_lozenge(cx, cy, w, h, fill, stroke, sw=1.2):
    """ogival lozenge with cusped points (Mughal shamsa-like)."""
    hw, hh = w / 2, h / 2
    d = (f"M{f(cx)} {f(cy-hh)} C{f(cx+hw*.18)} {f(cy-hh*.72)} {f(cx+hw*.5)} {f(cy-hh*.55)} {f(cx+hw*.62)} {f(cy-hh*.38)} "
         f"C{f(cx+hw*.75)} {f(cy-hh*.3)} {f(cx+hw*.9)} {f(cy-hh*.2)} {f(cx+hw)} {f(cy)} "
         f"C{f(cx+hw*.9)} {f(cy+hh*.2)} {f(cx+hw*.75)} {f(cy+hh*.3)} {f(cx+hw*.62)} {f(cy+hh*.38)} "
         f"C{f(cx+hw*.5)} {f(cy+hh*.55)} {f(cx+hw*.18)} {f(cy+hh*.72)} {f(cx)} {f(cy+hh)} "
         f"C{f(cx-hw*.18)} {f(cy+hh*.72)} {f(cx-hw*.5)} {f(cy+hh*.55)} {f(cx-hw*.62)} {f(cy+hh*.38)} "
         f"C{f(cx-hw*.75)} {f(cy+hh*.3)} {f(cx-hw*.9)} {f(cy+hh*.2)} {f(cx-hw)} {f(cy)} "
         f"C{f(cx-hw*.9)} {f(cy-hh*.2)} {f(cx-hw*.75)} {f(cy-hh*.3)} {f(cx-hw*.62)} {f(cy-hh*.38)} "
         f"C{f(cx-hw*.5)} {f(cy-hh*.55)} {f(cx-hw*.18)} {f(cy-hh*.72)} {f(cx)} {f(cy-hh)}Z")
    return path(d, fill, stroke, sw)

def stepped_cartouche(x0, y0, x1, y1, fill, stroke, sw=1.4):
    """long cartouche with cusped stepped ends (as in Burhanpuri p.7 panels)."""
    cy = (y0 + y1) / 2; h = y1 - y0; e = h * .9
    d = (f"M{f(x0+e)} {f(y0)} L{f(x1-e)} {f(y0)} "
         f"C{f(x1-e*.6)} {f(y0)} {f(x1-e*.7)} {f(y0-h*.12)} {f(x1-e*.45)} {f(y0-h*.12)} "
         f"C{f(x1-e*.15)} {f(y0-h*.12)} {f(x1-e*.2)} {f(cy-h*.2)} {f(x1)} {f(cy)} "
         f"C{f(x1-e*.2)} {f(cy+h*.2)} {f(x1-e*.15)} {f(y1+h*.12)} {f(x1-e*.45)} {f(y1+h*.12)} "
         f"C{f(x1-e*.7)} {f(y1+h*.12)} {f(x1-e*.6)} {f(y1)} {f(x1-e)} {f(y1)} "
         f"L{f(x0+e)} {f(y1)} "
         f"C{f(x0+e*.6)} {f(y1)} {f(x0+e*.7)} {f(y1+h*.12)} {f(x0+e*.45)} {f(y1+h*.12)} "
         f"C{f(x0+e*.15)} {f(y1+h*.12)} {f(x0+e*.2)} {f(cy+h*.2)} {f(x0)} {f(cy)} "
         f"C{f(x0+e*.2)} {f(cy-h*.2)} {f(x0+e*.15)} {f(y0-h*.12)} {f(x0+e*.45)} {f(y0-h*.12)} "
         f"C{f(x0+e*.7)} {f(y0-h*.12)} {f(x0+e*.6)} {f(y0)} {f(x0+e)} {f(y0)}Z")
    return path(d, fill, stroke, sw)

def save(name, w, h, body, title):
    open(f"{OUT}/{name}.svg", 'w').write(svg_doc(w, h, body, title=title))

# 1. horizontal cartouche panel
def panel_h(W=760, H=200, seed=3):
    s = rect(0, 0, W, H, GOLD) + scrolls(0, 0, W, H, 34, seed=seed) + sprinkle(0, 0, W, H, 40, seed)
    s += rect(14, 14, W - 28, H - 28, LAP, GOLD_L, 2)
    s += sprinkle(20, 20, W - 20, H - 20, 30, seed + 1, pal=(GOLD_L, ROSE, GOLD_L))
    s += stepped_cartouche(70, 44, W - 70, H - 44, GOLD, INK, 1.2)
    s += scrolls(80, 50, W - 80, H - 50, 28, seed=seed + 2) + sprinkle(90, 52, W - 90, H - 52, 46, seed + 3)
    s += lobed_lozenge(W / 2, H / 2, 150, 92, LAP, GOLD_L, 2) + sprinkle(W / 2 - 50, H / 2 - 26, W / 2 + 50, H / 2 + 26, 10, seed + 4, pal=(GOLD_L, ROSE))
    for x in (W * .2, W * .8):
        s += lozenge(x, H / 2, 54, 54, MAROON, GOLD_L, 1.2) + g(x, H / 2, rosette(8, 20, 6, PINK, 4, GOLD_L, RED, ROSE))
    return s
save('bur_cartouche_panel_h', 760, 200, panel_h(), 'Burhanpuri opening: horizontal lapis panel with stepped cartouche')

# 2. vertical cartouche panel
def panel_v():
    W, H = 200, 620
    inner = panel_h(H, W, seed=11)
    return f'<g transform="translate({W} 0) rotate(90)">{inner}</g>'
save('bur_cartouche_panel_v', 200, 620, panel_v(), 'Burhanpuri opening: vertical lapis panel with stepped cartouche')

# 3. mandorla (shamsa) panel in cusped niche
def mandorla():
    W, H = 360, 640
    s = rect(0, 0, W, H, GOLD) + scrolls(0, 0, W, H, 30, seed=21) + sprinkle(0, 0, W, H, 40, 22)
    # cusped niche: arch top & bottom
    m = 18
    niche = (f"M{m} 150 C{m} 110 {m+30} 96 {m+56} 96 C{m+56} 60 {W/2-40} 40 {W/2} {m} "
             f"C{W/2+40} 40 {W-m-56} 60 {W-m-56} 96 C{W-m-30} 96 {W-m} 110 {W-m} 150 "
             f"L{W-m} {H-150} C{W-m} {H-110} {W-m-30} {H-96} {W-m-56} {H-96} C{W-m-56} {H-60} {W/2+40} {H-40} {W/2} {H-m} "
             f"C{W/2-40} {H-40} {m+56} {H-60} {m+56} {H-96} C{m+30} {H-96} {m} {H-110} {m} {H-150}Z")
    s += path(niche, LAP, GOLD_L, 2.4)
    s += sprinkle(30, 40, W - 30, H - 40, 60, 23, pal=(GOLD_L, ROSE, '#9FB2DA'), r=(1.2, 2.6))
    s += lobed_lozenge(W / 2, H / 2, 230, 300, GOLD, GOLD_L, 2.4)
    s += scrolls(W / 2 - 100, H / 2 - 130, W / 2 + 100, H / 2 + 130, 26, seed=24) + sprinkle(W / 2 - 90, H / 2 - 110, W / 2 + 90, H / 2 + 110, 40, 25)
    for y in (H * .16, H * .84):
        s += quatrefoil(W / 2, y, 44, GOLD, GOLD_L, RED)
    return s, W, H
b, W, H = mandorla(); save('bur_mandorla_panel', W, H, b, 'Burhanpuri opening: lobed mandorla in cusped lapis niche')

# 4. ogee arcade headpiece (p.8 top)
def arcade():
    W, H = 760, 240
    s = rect(0, 0, W, H, GOLD) + scrolls(0, 0, W, H, 30, seed=31) + sprinkle(0, 0, W, H, 90, 32)
    # lapis zigzag band with domes
    n = 3; span = W / n
    top = ''
    for i in range(n):
        x0 = i * span; xm = x0 + span / 2
        top += (f"M{f(x0)} 20 L{f(x0+span*.18)} 60 Q{f(xm-span*.18)} 18 {f(xm)} 8 Q{f(xm+span*.18)} 18 {f(x0+span*.82)} 60 L{f(x0+span)} 20 Z ")
    s += path(f"M0 0 L{W} 0 L{W} 20 L0 20Z", LAP)
    s += path(top, LAP, GOLD_L, 1.4)
    # domes (gold onion arches)
    for i in range(n):
        x0 = i * span; xm = x0 + span / 2
        dome = (f"M{f(x0+span*.08)} {H} L{f(x0+span*.08)} 120 C{f(x0+span*.08)} 80 {f(xm-span*.25)} 70 {f(xm-span*.12)} 54 "
                f"C{f(xm-span*.05)} 44 {f(xm-4)} 40 {f(xm)} 22 C{f(xm+4)} 40 {f(xm+span*.05)} 44 {f(xm+span*.12)} 54 "
                f"C{f(xm+span*.25)} 70 {f(x0+span*.92)} 80 {f(x0+span*.92)} 120 L{f(x0+span*.92)} {H}")
        s += path(dome, 'none', MAROON, 2.2)
        s += circle(xm, 16, 6, GOLD_L, INK, .8)
    # central inverted lapis cusp (between arches)
    for i in range(1, n):
        x = i * span
        s += path(f"M{f(x-56)} {H} C{f(x-40)} {H-50} {f(x-16)} {H-70} {f(x)} {H-110} C{f(x+16)} {H-70} {f(x+40)} {H-50} {f(x+56)} {H}Z", LAP, GOLD_L, 1.4)
    s += path(f"M{W/2-90} {H} C{W/2-60} {H-50} {W/2-20} {H-60} {W/2} {H-100} C{W/2+20} {H-60} {W/2+60} {H-50} {W/2+90} {H}Z", LAP, GOLD_L, 1.4)
    s += sprinkle(W / 2 - 60, H - 70, W / 2 + 60, H - 10, 10, 33, pal=(GOLD_L, ROSE))
    return s, W, H
b, W, H = arcade(); save('bur_ogee_arcade_headpiece', W, H, b, 'Burhanpuri opening: ogee arcade headpiece')

# 5. star & cartouche band
def starband():
    W, H = 760, 110
    s = rect(0, 0, W, H, LAP) + sprinkle(0, 0, W, H, 30, 41, pal=(GOLD_L, ROSE))
    def star8(cx, cy, r):
        pts = []
        for i in range(16):
            a = math.radians(i * 22.5 - 90); rr = r if i % 2 == 0 else r * .72
            pts.append(f"{f(cx + rr*math.cos(a))} {f(cy + rr*math.sin(a))}")
        return path("M" + " L".join(pts) + "Z", GOLD, GOLD_L, 1.4)
    for x in (55, W - 55):
        s += star8(x, H / 2, 46) + sprinkle(x - 26, H / 2 - 26, x + 26, H / 2 + 26, 6, int(x))
    s += stepped_cartouche(130, 22, W - 130, H - 22, GOLD, GOLD_L, 1.4)
    s += sprinkle(150, 26, W - 150, H - 26, 40, 42)
    for x in (W * .33, W * .67):
        s += star8(x, H / 2, 30)
    return s, W, H
b, W, H = starband(); save('bur_star_cartouche_band', W, H, b, 'Burhanpuri opening: 8-point stars and stepped cartouche band')

# 6. diamond lattice panel
def lattice():
    W, H = 760, 300
    s = rect(0, 0, W, H, GOLD) + scrolls(0, 0, W, H, 30, seed=51) + sprinkle(0, 0, W, H, 140, 52)
    step = W / 4
    for k in range(-2, 7):
        x = k * step
        s += path(f"M{f(x)} 0 L{f(x+step*1.6)} {H}", 'none', MAROON, 9) + path(f"M{f(x)} 0 L{f(x+step*1.6)} {H}", 'none', ROSE, 1)
        s += path(f"M{f(x+step*1.6)} 0 L{f(x)} {H}", 'none', MAROON, 9) + path(f"M{f(x+step*1.6)} 0 L{f(x)} {H}", 'none', ROSE, 1)
    s += rect(0, 0, 70, H, LAP, GOLD_L, 1.4) + rect(W - 70, 0, 70, H, LAP, GOLD_L, 1.4)
    for x in (35, W - 35):
        s += f'<g transform="translate({x+22} 30) rotate(90)">' + stepped_cartouche(0, 0, H - 60, 44, GOLD, GOLD_L, 1) + '</g>'
        s += quatrefoil(x, H / 2, 26, GOLD, GOLD_L, RED)
    return f'<defs><clipPath id="lc"><rect width="{W}" height="{H}"/></clipPath></defs><g clip-path="url(#lc)">{s}</g>', W, H
b, W, H = lattice(); save('bur_diamond_lattice_panel', W, H, b, 'Burhanpuri opening: crimson diamond lattice on gold')

# 7. outer gold scroll border tile (circle-scroll vine)
def scrollborder():
    w, h = 90, 70
    s = rect(0, 0, w, h, GOLD)
    s += path(f"M0 35 C15 5 45 5 45 35 C45 65 75 65 90 35", 'none', GOLD_D, 1.4)
    s += path(f"M45 35 C40 22 28 20 24 30 C21 38 30 42 33 36", 'none', GOLD_D, 1)
    s += path(f"M45 35 C50 48 62 50 66 40 C69 32 60 28 57 34", 'none', GOLD_D, 1)
    s += g(28, 32, rosette(6, 6, 2.6, RED, 1.6, GOLD_L)) + g(62, 38, rosette(6, 6, 2.6, PINK, 1.6, GOLD_L))
    for x, y, r in ((12, 18, 30), (80, 52, 210), (45, 12, 100), (45, 58, -80)):
        s += g(x, y, leaf(8, 3, GREEN), rot=r)
    s += hrule(1, w, 2, MAROON) + hrule(h - 1, w, 2, MAROON)
    return s, w, h
b, w, h = scrollborder()
save('bur_scroll_border_tile', w, h, b, 'Burhanpuri opening: outer gold scroll-vine border (tile)')
open(f"{OUT}/bur_scroll_border_strip.svg", 'w').write(svg_doc(w * 7, h, f'<rect width="{w*7}" height="{h}" fill="url(#t)"/>', defs=f'<pattern id="t" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{b}</pattern>', title='Burhanpuri opening: outer gold scroll-vine border'))

# 8. cloud-band heading cartouche (p.33 style) with placeholder
def cloudhead():
    W, H = 420, 130
    s = rect(0, 0, W, H, GOLD_L) + sprinkle(0, 0, W, H, 80, 61, pal=(RED, PINK, LAP_L, GREEN), r=(1.4, 2.6))
    cloud = ("M120 64 C116 46 138 38 152 48 C158 30 186 30 192 46 C200 34 222 36 224 52 C238 44 258 54 250 68 "
             "C262 74 254 92 238 88 C232 102 208 100 204 88 C194 100 170 98 168 86 C152 96 132 88 138 76 C122 78 114 70 120 64Z")
    s += path(cloud, '#F4EAD2', GOLD_D, 1.4)
    s += path("M30 100 C60 86 90 108 120 96 M300 100 C330 86 360 108 390 96", 'none', GOLD_D, 1)
    s += rect(0, H - 22, W, 22, '#F4EAD2', MAROON, 1)
    s += f'<text x="{W/2-12}" y="74" text-anchor="middle" font-family="serif" font-size="15" fill="#6B4A2A">[ HEADING ]</text>'
    return s, W, H
b, W, H = cloudhead(); save('bur_cloud_heading', W, H, b, 'Burhanpuri: cloud-band heading cartouche on sprinkled gold (placeholder)')

# 9. baluster column pair (p.8 right)
def baluster():
    W, H = 140, 420
    s = rect(0, 0, W, H, LAP)
    for cx in (38, 102):
        col = (f"M{cx-10} {H-20} L{cx+10} {H-20} L{cx+8} {H-60} C{cx+22} {H-90} {cx+22} {H-140} {cx+8} {H-170} "
               f"L{cx+5} 120 C{cx+18} 100 {cx+14} 70 {cx+4} 56 L{cx+8} 30 L{cx-8} 30 L{cx-4} 56 "
               f"C{cx-14} 70 {cx-18} 100 {cx-5} 120 L{cx-8} {H-170} C{cx-22} {H-140} {cx-22} {H-90} {cx-8} {H-60}Z")
        s += path(col, GOLD, GOLD_L, 1.4)
        s += path(f"M{cx} 40 L{cx} {H-30}", 'none', MAROON, 1.4)
        s += lozenge(cx, H - 115, 14, 30, RED) + lozenge(cx, 88, 10, 22, RED)
        s += rect(cx - 18, 18, 36, 12, GOLD, GOLD_L, 1) + rect(cx - 18, H - 22, 36, 12, GOLD, GOLD_L, 1)
    return s, W, H
b, W, H = baluster(); save('bur_baluster_columns', W, H, b, 'Burhanpuri opening: paired baluster columns')
print('ok')
