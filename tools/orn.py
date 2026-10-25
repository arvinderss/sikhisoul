# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""Ornament primitives for manuscript border tiles. All motif fns return SVG
fragment strings drawn around (0,0); place with g(x, y, frag, rot, scale)."""
import math

# ---- palette (sampled from Burhanpuri / Bhanno scans, cleaned) ----
P = dict(
    gold='#CFAE68', gold_l='#E2C88E', gold_d='#A9853F', gold_line='#8C6A2A',
    paper='#F1E8D3', cream='#F6EEDB', white='#FFFDF6',
    red='#D8392F', red_d='#A8241F', orange='#E0683A', vermilion='#D2542C',
    pink='#E77A98', pink_l='#F4B8C8', rose='#C9356A', magenta='#B5307A',
    lilac='#A79BDA', lilac_d='#7768B8', purple='#7E5BB5', violet='#5D4597',
    blue='#6F86CF', blue_d='#3F55A4', lapis='#2F4A8F', slate='#8FA6BE', slate_d='#5E7891',
    green='#5E9150', green_d='#3D6B36', green_l='#93BC6C', teal='#4E8C7A',
    yellow='#E7B93C', ochre='#C98F2B', ink='#2A2018', brown='#6B4A2A',
)

def f(n):
    return f"{n:.2f}".rstrip('0').rstrip('.')

def g(x, y, frag, rot=0, sc=1, sx=None, sy=None):
    t = f"translate({f(x)} {f(y)})"
    if rot: t += f" rotate({f(rot)})"
    if sx is not None or sy is not None:
        t += f" scale({f(sx if sx is not None else sc)} {f(sy if sy is not None else sc)})"
    elif sc != 1: t += f" scale({f(sc)})"
    return f'<g transform="{t}">{frag}</g>'

def path(d, fill='none', stroke=None, sw=1, extra=''):
    s = f'<path d="{d}" fill="{fill}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{f(sw)}" stroke-linecap="round" stroke-linejoin="round"'
    return s + extra + '/>'

def circle(cx, cy, r, fill, stroke=None, sw=1):
    s = f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{f(sw)}"'
    return s + '/>'

def ellipse(cx, cy, rx, ry, fill, stroke=None, sw=1, rot=0):
    s = f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{f(sw)}"'
    if rot: s += f' transform="rotate({f(rot)} {f(cx)} {f(cy)})"'
    return s + '/>'

def rect(x, y, w, h, fill, stroke=None, sw=1, rx=0):
    s = f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{fill}"'
    if rx: s += f' rx="{f(rx)}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{f(sw)}"'
    return s + '/>'

# ---------------- petals & leaves (pointing up, base at origin) ----------------
def petal_d(l, w):
    return (f"M0 0 C{f(w)} {f(-l*.25)} {f(w*.75)} {f(-l)} 0 {f(-l)} "
            f"C{f(-w*.75)} {f(-l)} {f(-w)} {f(-l*.25)} 0 0Z")

def petal(l, w, fill, stroke=None, sw=.8):
    return path(petal_d(l, w), fill, stroke, sw)

def leaf(l, w, fill, rib=None, sw=.8, stroke=None):
    d = f"M0 0 Q{f(w)} {f(-l*.45)} 0 {f(-l)} Q{f(-w)} {f(-l*.45)} 0 0Z"
    s = path(d, fill, stroke, sw)
    if rib: s += path(f"M0 {f(-l*.05)} Q{f(w*.15)} {f(-l*.5)} 0 {f(-l*.92)}", 'none', rib, sw)
    return s

def curved_leaf(l, w, bend, fill, rib=None, sw=.8):
    """leaf whose tip swings sideways by `bend` (fraction of l)."""
    tx = l * bend
    d = (f"M0 0 C{f(w*1.1)} {f(-l*.3)} {f(tx+w*.6)} {f(-l*.75)} {f(tx)} {f(-l)} "
         f"C{f(tx-w*.4)} {f(-l*.7)} {f(-w*.9)} {f(-l*.35)} 0 0Z")
    s = path(d, fill)
    if rib: s += path(f"M0 0 C{f(w*.2)} {f(-l*.35)} {f(tx*.7)} {f(-l*.7)} {f(tx)} {f(-l)}", 'none', rib, sw)
    return s

def serrated_leaf(l, w, fill, rib, n=6):
    pts = []
    for i in range(n + 1):
        t = i / n; y = -l * t; half = w * math.sin(math.pi * t) ** .8
        pts.append((half, y))
    right = " ".join(f"L{f(x + (2 if i % 2 else 0))} {f(y - (2 if i % 2 else 0))}" for i, (x, y) in enumerate(pts))
    left = " ".join(f"L{f(-x - (2 if i % 2 else 0))} {f(y - (2 if i % 2 else 0))}" for i, (x, y) in reversed(list(enumerate(pts))))
    d = "M0 0 " + right + " " + left + " Z"
    s = path(d, fill)
    s += path(f"M0 0 L0 {f(-l*.95)}", 'none', rib, 1)
    for i in range(1, n):
        y = -l * i / n
        s += path(f"M0 {f(y)} L{f(w*.5)} {f(y - l*.08)} M0 {f(y)} L{f(-w*.5)} {f(y - l*.08)}", 'none', rib, .7)
    return s

# ---------------- flowers ----------------
def rosette(n, r, pw, fill, center, ccol, stroke=None, inner=None, rot0=0):
    s = ''
    for i in range(n):
        s += g(0, 0, petal(r, pw, fill, stroke), rot=rot0 + 360 * i / n)
    if inner:
        for i in range(n):
            s += g(0, 0, petal(r * .55, pw * .45, inner), rot=rot0 + 360 * i / n)
    s += circle(0, 0, center, ccol)
    return s

def rose5(r, fill, center='#F6E7A0', ring=None, dots=None):
    """five round petals (garden-rose style)."""
    s = ''
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        s += circle(r * .52 * math.cos(a), r * .52 * math.sin(a), r * .5, fill)
    if ring: s += circle(0, 0, r * .42, ring)
    s += circle(0, 0, r * .26, center)
    if dots:
        for i in range(5):
            a = math.radians(-90 + 72 * i)
            s += circle(r * .62 * math.cos(a), r * .62 * math.sin(a), r * .07, dots)
    return s

def star5(r, fill, line, center):
    s = ''
    for i in range(5):
        s += g(0, 0, path(f"M0 0 C{f(r*.45)} {f(-r*.35)} {f(r*.35)} {f(-r*.9)} 0 {f(-r)} C{f(-r*.35)} {f(-r*.9)} {f(-r*.45)} {f(-r*.35)} 0 0Z", fill, line, .6), rot=72 * i)
        s += g(0, 0, path(f"M0 {f(-r*.2)} L0 {f(-r*.7)}", 'none', line, .7), rot=72 * i)
    s += circle(0, 0, r * .16, center)
    return s

def tulip(h, fill, light=None, line=None):
    w = h * .48
    d = (f"M{f(-w)} {f(-h*.3)} C{f(-w*1.05)} {f(-h*.75)} {f(-w*.7)} {f(-h*.95)} {f(-w*.55)} {f(-h*1.02)} "
         f"L{f(-w*.25)} {f(-h*.68)} L0 {f(-h*1.08)} L{f(w*.25)} {f(-h*.68)} L{f(w*.55)} {f(-h*1.02)} "
         f"C{f(w*.7)} {f(-h*.95)} {f(w*1.05)} {f(-h*.75)} {f(w)} {f(-h*.3)} "
         f"C{f(w*.8)} {f(h*.02)} {f(-w*.8)} {f(h*.02)} {f(-w)} {f(-h*.3)}Z")
    s = path(d, fill, line, .7)
    if light:
        s += path(f"M{f(-w*.3)} {f(-h*.1)} Q{f(-w*.35)} {f(-h*.5)} {f(-w*.25)} {f(-h*.68)} M{f(w*.3)} {f(-h*.1)} Q{f(w*.35)} {f(-h*.5)} {f(w*.25)} {f(-h*.68)}", 'none', light, 1.1)
    return s

def lily(h, fill, light, line=None):
    """flared six-petal lily / bell seen from side."""
    s = ''
    for a, sc in ((-38, .9), (38, .9), (-14, 1), (14, 1), (0, 1.05)):
        s += g(0, 0, petal(h * sc, h * .2, fill, line, .6), rot=a)
    for a in (-14, 14, 0):
        s += g(0, 0, path(f"M0 {f(-h*.15)} L0 {f(-h*.8)}", 'none', light, 1), rot=a)
    return s

def bell(h, fill, light, line=None):
    w = h * .55
    d = (f"M0 0 C{f(w*.5)} 0 {f(w*.55)} {f(-h*.45)} {f(w*.6)} {f(-h*.75)} "
         f"L{f(w*.95)} {f(-h*.95)} L{f(w*.35)} {f(-h*.88)} L0 {f(-h*1.05)} L{f(-w*.35)} {f(-h*.88)} L{f(-w*.95)} {f(-h*.95)} "
         f"L{f(-w*.6)} {f(-h*.75)} C{f(-w*.55)} {f(-h*.45)} {f(-w*.5)} 0 0 0Z")
    return path(d, fill, line, .7) + path(f"M0 {f(-h*.1)} L0 {f(-h*.85)} M{f(-w*.25)} {f(-h*.1)} L{f(-w*.35)} {f(-h*.8)} M{f(w*.25)} {f(-h*.1)} L{f(w*.35)} {f(-h*.8)}", 'none', light, .9)

def iris(h, fill, dark, light):
    s = ''
    s += g(0, 0, petal(h * .95, h * .2, fill), rot=0)                 # standard
    s += g(0, -h*.25, petal(h * .7, h * .22, fill), rot=-118)          # falls
    s += g(0, -h*.25, petal(h * .7, h * .22, fill), rot=118)
    s += g(0, 0, petal(h * .75, h * .16, dark), rot=-28)
    s += g(0, 0, petal(h * .75, h * .16, dark), rot=28)
    s += path(f"M0 {f(-h*.15)} L0 {f(-h*.75)}", 'none', light, 1)
    return s

def poppy_side(h, fill, dark, sepal):
    """flower seen from side, cup with frilled top (Burhanpuri 361/600)."""
    w = h * .7
    d = (f"M{f(-w*.55)} {f(-h*.15)} C{f(-w*.9)} {f(-h*.55)} {f(-w*1.0)} {f(-h*.85)} {f(-w*.85)} {f(-h*1.0)} "
         f"L{f(-w*.55)} {f(-h*.8)} L{f(-w*.35)} {f(-h*1.05)} L{f(-w*.12)} {f(-h*.82)} L{f(w*.12)} {f(-h*1.08)} "
         f"L{f(w*.35)} {f(-h*.82)} L{f(w*.6)} {f(-h*1.04)} L{f(w*.72)} {f(-h*.8)} L{f(w*.95)} {f(-h*.95)} "
         f"C{f(w*.95)} {f(-h*.6)} {f(w*.8)} {f(-h*.3)} {f(w*.55)} {f(-h*.15)} C{f(w*.3)} {f(h*.02)} {f(-w*.3)} {f(h*.02)} {f(-w*.55)} {f(-h*.15)}Z")
    s = path(d, fill)
    for x in (-.4, -.15, .1, .35, .6):
        s += path(f"M{f(w*x*.6)} {f(-h*.12)} L{f(w*x)} {f(-h*.8)}", 'none', dark, .9)
    s += path(f"M{f(-w*.45)} {f(-h*.05)} Q0 {f(h*.12)} {f(w*.45)} {f(-h*.05)} L0 {f(h*.12)}Z", sepal)
    return s

def lotus_fan(h, fill, dark):
    s = ''
    for a in (-60, -40, -20, 0, 20, 40, 60):
        s += g(0, 0, petal(h * (1 - abs(a) / 220), h * .17, fill, dark, .5), rot=a)
    return s

def lotus_bud(l, w, fill, dark, light):
    d = f"M0 0 C{f(w)} {f(-w*.2)} {f(w*.9)} {f(-l*.75)} 0 {f(-l)} C{f(-w*.9)} {f(-l*.75)} {f(-w)} {f(-w*.2)} 0 0Z"
    s = path(d, fill)
    s += path(f"M0 {f(-l*.08)} C{f(w*.45)} {f(-l*.3)} {f(w*.4)} {f(-l*.7)} 0 {f(-l*.97)} M0 {f(-l*.08)} C{f(-w*.45)} {f(-l*.3)} {f(-w*.4)} {f(-l*.7)} 0 {f(-l*.97)}", 'none', dark, .9)
    s += path(f"M{f(-w*.3)} {f(-l*.2)} C{f(-w*.5)} {f(-l*.45)} {f(-w*.35)} {f(-l*.75)} {f(-w*.1)} {f(-l*.9)}", 'none', light, 1.2)
    return s

def almond_bud(l, w, fill, dark, sepal):
    s = g(0, 0, path(f"M0 0 L{f(-l*.25)} {f(-w*.55)} L{f(-l*.12)} 0 L{f(-l*.25)} {f(w*.55)}Z", sepal))
    s += g(0, 0, path(f"M{f(l*.1)} 0 L{f(l*1.25)} {f(-w*.3)} L{f(l*1.1)} 0 L{f(l*1.25)} {f(w*.3)}Z", sepal))
    s += path(f"M0 0 C{f(l*.25)} {f(-w)} {f(l*.75)} {f(-w)} {f(l)} 0 C{f(l*.75)} {f(w)} {f(l*.25)} {f(w)} 0 0Z", fill)
    s += path(f"M{f(l*.1)} 0 L{f(l*.9)} 0", 'none', dark, .8)
    return s

def pomegranate(r, fill, pearl, sepal):
    s = path(f"M0 {f(-r)} C{f(r*1.1)} {f(-r)} {f(r*1.2)} {f(r*.6)} 0 {f(r*.95)} C{f(-r*1.2)} {f(r*.6)} {f(-r*1.1)} {f(-r)} 0 {f(-r)}Z", fill)
    s += path(f"M{f(-r*.45)} {f(-r*.85)} L{f(-r*.25)} {f(-r*1.35)} L0 {f(-r*.95)} L{f(r*.25)} {f(-r*1.35)} L{f(r*.45)} {f(-r*.85)}Z", sepal)
    s += circle(r * .55, -r * .65, r * .32, pearl, '#9AA6AE', .5)
    return s

def grapes(r, fill, light, n_rows=4):
    s = ''
    y = 0
    for row in range(n_rows):
        k = n_rows - row
        for i in range(k):
            x = (i - (k - 1) / 2) * r * 1.7
            s += circle(x, -y, r, fill, light, .5) + circle(x - r * .3, -y - r * .3, r * .3, light)
        y += r * 1.5
    return s

def pinecone(l, w, fill, line, cap):
    s = path(f"M0 0 C{f(w)} 0 {f(w)} {f(-l*.75)} 0 {f(-l)} C{f(-w)} {f(-l*.75)} {f(-w)} 0 0 0Z", fill)
    for i in range(1, 5):
        y = -l * i / 5
        s += path(f"M{f(-w*.8)} {f(y+3)} L0 {f(y-3)} L{f(w*.8)} {f(y+3)}", 'none', line, .8)
    s += path(f"M{f(-w*.6)} 0 L0 {f(l*.18)} L{f(w*.6)} 0Z", cap)
    return s

def pansy(r, top, side, center):
    s = ''
    s += g(0, 0, path(f"M0 0 C{f(-r)} {f(-r*.2)} {f(-r*1.1)} {f(-r*1.1)} {f(-r*.2)} {f(-r*.95)} C{f(r*.1)} {f(-r*.9)} {f(r*.15)} {f(-r*.4)} 0 0Z", top))
    s += g(0, 0, path(f"M0 0 C{f(r)} {f(-r*.2)} {f(r*1.1)} {f(-r*1.1)} {f(r*.2)} {f(-r*.95)} C{f(-r*.1)} {f(-r*.9)} {f(-r*.15)} {f(-r*.4)} 0 0Z", top))
    s += path(f"M0 0 C{f(-r*.9)} {f(r*.1)} {f(-r*1.3)} {f(-r*.35)} {f(-r*1.35)} {f(-r*.05)} C{f(-r*1.2)} {f(r*.5)} {f(-r*.4)} {f(r*.45)} 0 0Z", side)
    s += path(f"M0 0 C{f(r*.9)} {f(r*.1)} {f(r*1.3)} {f(-r*.35)} {f(r*1.35)} {f(-r*.05)} C{f(r*1.2)} {f(r*.5)} {f(r*.4)} {f(r*.45)} 0 0Z", side)
    s += path(f"M0 0 C{f(-r*.6)} {f(r*.4)} {f(-r*.4)} {f(r*1)} 0 {f(r*.95)} C{f(r*.4)} {f(r*1)} {f(r*.6)} {f(r*.4)} 0 0Z", top)
    s += circle(0, 0, r * .18, center)
    s += path(f"M0 0 L{f(-r*.35)} {f(-r*.5)} M0 0 L{f(r*.35)} {f(-r*.5)} M0 0 L0 {f(r*.5)}", 'none', '#3A2A3A', .7)
    return s

def cscroll(r, fill, line):
    """acanthus-like curled leaf (Burhanpuri 385/546)."""
    d = (f"M{f(-r)} 0 C{f(-r)} {f(-r*1.1)} {f(r*.9)} {f(-r*1.2)} {f(r)} {f(-r*.1)} "
         f"C{f(r)} {f(r*.6)} {f(r*.2)} {f(r*.75)} {f(-r*.1)} {f(r*.35)} C{f(r*.15)} {f(r*.45)} {f(r*.55)} {f(r*.2)} {f(r*.45)} {f(-r*.2)} "
         f"C{f(r*.2)} {f(-r*.7)} {f(-r*.6)} {f(-r*.5)} {f(-r*.55)} {f(r*.1)} C{f(-r*.5)} {f(r*.6)} {f(-r*.2)} {f(r*.8)} 0 {f(r*.95)} C{f(-r*.7)} {f(r*.9)} {f(-r)} {f(r*.4)} {f(-r)} 0Z")
    return path(d, fill, line, .7)

# ---------------- band furniture ----------------
def hrule(y, w, th, col):
    return rect(0, y - th / 2, w, th, col)

def dotrule(y, w, step, r, col, x0=None):
    x0 = step / 2 if x0 is None else x0
    s = ''
    x = x0
    while x < w:
        s += circle(x, y, r, col); x += step
    return s

def cartouche(x, y, w, h, fill, stroke, sw=1.2, kind='oval'):
    if kind == 'oval':
        return rect(x - w / 2, y - h / 2, w, h, fill, stroke, sw, rx=h / 2)
    if kind == 'pointed':
        return path(f"M{f(x-w/2)} {f(y)} C{f(x-w/2+h*.35)} {f(y-h/2)} {f(x-w/4)} {f(y-h/2)} {f(x)} {f(y-h/2)} "
                    f"C{f(x+w/4)} {f(y-h/2)} {f(x+w/2-h*.35)} {f(y-h/2)} {f(x+w/2)} {f(y)} "
                    f"C{f(x+w/2-h*.35)} {f(y+h/2)} {f(x+w/4)} {f(y+h/2)} {f(x)} {f(y+h/2)} "
                    f"C{f(x-w/4)} {f(y+h/2)} {f(x-w/2+h*.35)} {f(y+h/2)} {f(x-w/2)} {f(y)}Z", fill, stroke, sw)
    if kind == 'circle':
        return circle(x, y, h / 2, fill, stroke, sw)

def bowtie(x, y, w, h, fill, stroke=None, sw=.8):
    return path(f"M{f(x-w/2)} {f(y-h/2)} L{f(x+w/2)} {f(y-h/2)} L{f(x+w*.08)} {f(y)} L{f(x+w/2)} {f(y+h/2)} "
                f"L{f(x-w/2)} {f(y+h/2)} L{f(x-w*.08)} {f(y)}Z", fill, stroke, sw)

def hourglass_bar(x, y, w, h, fill, stroke):
    return path(f"M{f(x-w/2)} {f(y-h/2)} L{f(x+w/2)} {f(y-h/2)} C{f(x+w*.15)} {f(y-h*.2)} {f(x+w*.15)} {f(y+h*.2)} {f(x+w/2)} {f(y+h/2)} "
                f"L{f(x-w/2)} {f(y+h/2)} C{f(x-w*.15)} {f(y+h*.2)} {f(x-w*.15)} {f(y-h*.2)} {f(x-w/2)} {f(y-h/2)}Z", fill, stroke, .9)

def lozenge(x, y, w, h, fill, stroke=None, sw=.8):
    return path(f"M{f(x)} {f(y-h/2)} L{f(x+w/2)} {f(y)} L{f(x)} {f(y+h/2)} L{f(x-w/2)} {f(y)}Z", fill, stroke, sw)

def svg_doc(w, h, body, defs='', title=''):
    title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = f'<title>{title}</title>' if title else ''
    d = f'<defs>{defs}</defs>' if defs else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" height="{f(h)}">'
            f'{t}{d}{body}</svg>')
