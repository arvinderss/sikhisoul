# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""Bhanno MS opening-folio illumination (PDL, 1700s), reconstructed as vector."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from orn import *

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GOLD = '#C9A24E'; GOLD_L = '#DDBF73'; GOLD_D = '#8F6E2C'; LAP = '#2E3F6E'; LAP_L = '#4D6197'
RED = '#A8352B'; ROSE = '#B9506A'; BLUEF = '#7C93C9'; INK = '#2B2420'; BRN = '#6E3A26'; PAPER = '#E7D7B4'

def floret(x, y, r, col):
    return circle(x, y, r, col) + circle(x, y, r * .45, '#E9D9A6')

def spiral(cx, cy, r, col=GOLD_D, sw=.7):
    d = f"M{f(cx)} {f(cy)}"
    for i in range(1, 40):
        a = i * .32; rr = r * i / 40
        d += f" L{f(cx + rr*math.cos(a))} {f(cy + rr*math.sin(a))}"
    return path(d, 'none', col, sw)

# ---------- K: kangura scalloped band (period 100) ----------
def kangura_tile():
    w, h = 100, 120
    s = ''
    # rays (finials pointing outward/up)
    for x, ln in ((0, 34), (50, 44), (25, 24), (75, 24)):
        base = 58 if x in (0,) else (30 if x == 50 else 48)
        top = base - ln
        s += path(f"M{x} {base} L{x} {top}", 'none', INK, .9)
        s += path(f"M{x-3} {top+7} L{x} {top} L{x+3} {top+7}", 'none', INK, .8)
        s += path(f"M{x-2.5} {base-8} Q{x} {base-12} {x+2.5} {base-8}", 'none', INK, .6)
    # scallop edge (ogee peaks at 50, valleys at 0/100)
    edge = "M0 62 C6 52 30 44 50 30 C70 44 94 52 100 62"
    s += path(edge + f" L100 {h} L0 {h}Z", GOLD)
    s += path(edge, 'none', INK, 1.4)
    s += path("M0 67 C6 57 30 49 50 35 C70 49 94 57 100 67", 'none', RED, 1)
    # gold field ornament: spirals + florets
    for cx, cy in ((25, 86), (75, 86), (50, 104)):
        s += spiral(cx, cy, 13)
    # lapis pendant at valleys (hanging) and lapis arch under peak (rising from bottom)
    for x in (0, 100):
        s += path(f"M{x-14} 64 C{x-8} 66 {x-4} 70 {x} 82 C{x+4} 70 {x+8} 66 {x+14} 64 L{x} 62Z", LAP, '#E6D9B8', .6)
        s += floret(x, 70, 2.4, RED)
    s += path(f"M36 118 C40 106 46 98 50 92 C54 98 60 106 64 118Z", LAP, '#E6D9B8', .6)
    s += floret(50, 108, 2.4, ROSE) + floret(44, 115, 1.6, RED) + floret(56, 115, 1.6, RED)
    for x, y, c in ((22, 76, RED), (32, 96, BLUEF), (68, 96, ROSE), (80, 74, BLUEF), (12, 104, RED), (88, 104, ROSE), (50, 50, RED)):
        s += floret(x, y, 2.6, c)
    s += hrule(117, w, 2, BRN)
    return w, h, s

# ---------- C: cartouche band (period 110) ----------
def cartouche_tile():
    w, h = 110, 56
    s = rect(0, 0, w, h, LAP)
    s += rect(14, 6, 82, 44, GOLD, '#F1E6C8', 1.2, rx=22)
    s += spiral(40, 28, 13) + spiral(70, 28, 13)
    s += floret(42, 28, 3.2, RED) + floret(68, 28, 3.2, BLUEF) + floret(55, 16, 2, ROSE) + floret(55, 40, 2, RED)
    # bowtie gold accents in lapis
    for x in (0, w):
        s += floret(x, 14, 2.2, '#E3A07F') + floret(x, 42, 2.2, '#E3A07F') + floret(x, 28, 2.6, GOLD_L)
    s += hrule(.8, w, 1.6, BRN) + hrule(h - .8, w, 1.6, BRN)
    return w, h, s

def tile_svg(name, fn, title):
    w, h, s = fn()
    open(f"{OUT}/{name}.svg", 'w').write(svg_doc(w, h, s, title=title))
    W = w * 5
    open(f"{OUT}/{name}_strip.svg", 'w').write(svg_doc(W, h, f'<rect width="{W}" height="{h}" fill="url(#t)"/>', defs=f'<pattern id="t" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{s}</pattern>', title=title))
    return w, h, s

kw, kh, ks = tile_svg('bha_kangura_band', kangura_tile, 'Bhanno MS: kangura scalloped band with rays')
cw, ch, cs = tile_svg('bha_cartouche_band', cartouche_tile, 'Bhanno MS: oval cartouche band on lapis')

# ---------- full opening-page frame ----------
PW, PH = 800, 980
defs = (f'<pattern id="K" width="{kw}" height="{kh}" patternUnits="userSpaceOnUse">{ks}</pattern>'
        f'<pattern id="C" width="{cw}" height="{ch}" patternUnits="userSpaceOnUse">{cs}</pattern>')
b = rect(0, 0, PW, PH, PAPER)
# outer kangura band: four sides drawn as rotated groups of pattern-filled rects
L = 60; T = 60  # band outer origin
bandW = PW - 2 * L; bandH = PH - 2 * T
def band(x, y, length, rot):
    return f'<g transform="translate({x} {y}) rotate({rot})"><rect x="0" y="0" width="{length}" height="{kh}" fill="url(#K)"/></g>'
b += band(L, T - 20, bandW, 0)
b += band(PW - L + 20, T, bandH, 90)
b += band(PW - L, PH - T + 20, bandW, 180)
b += band(L - 20, PH - T, bandH, 270)
# corner blocks covering band overlaps
for cx, cy in ((L + 40, T + 40), (PW - L - 40, T + 40), (L + 40, PH - T - 40), (PW - L - 40, PH - T - 40)):
    b += rect(cx - 60, cy - 60, 120, 120, GOLD, INK, 1.2) + rect(cx - 54, cy - 54, 108, 108, 'none', RED, .8)
    b += lozenge(cx, cy, 70, 70, LAP, '#E6D9B8', .8) + lozenge(cx, cy, 34, 34, GOLD, '#E6D9B8', .6) + floret(cx, cy, 5, RED)
    for dx, dy in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        b += spiral(cx + dx, cy + dy, 12) + floret(cx + dx * .7, cy + dy * .7, 2.4, ROSE)
# rules
inner_x0, inner_y0 = L + 106, T + 106
iw, ih = PW - 2 * inner_x0, PH - 2 * inner_y0
for k, (col, sw) in enumerate(((BRN, 2), (RED, 1), (GOLD_D, 1))):
    o = k * 4
    b += rect(inner_x0 + o, inner_y0 + o, iw - 2 * o, ih - 2 * o, 'none', col, sw)
# cartouche frame band
cx0, cy0 = inner_x0 + 16, inner_y0 + 16; cwid, chgt = iw - 32, ih - 32
def cband(x, y, length, rot):
    return f'<g transform="translate({x} {y}) rotate({rot})"><rect x="0" y="0" width="{length}" height="{ch}" fill="url(#C)"/></g>'
b += cband(cx0, cy0, cwid, 0) + cband(cx0 + cwid, cy0 + ch, chgt - 2 * ch, 90) + cband(cx0 + cwid, cy0 + chgt, cwid, 180) + cband(cx0, cy0 + chgt - ch, chgt - 2 * ch, 270)
# text block
tx0, ty0 = cx0 + ch + 14, cy0 + ch + 14; tw, th = cwid - 2 * ch - 28, chgt - 2 * ch - 28
b += rect(tx0 - 6, ty0 - 6, tw + 12, th + 12, 'none', RED, 1.2) + rect(tx0, ty0, tw, th, '#EFE3C4')
n = 15
for i in range(n):
    y = ty0 + 22 + i * (th - 34) / (n - 1)
    ww = tw - 40 if i < n - 1 else (tw - 40) * .6
    b += rect(tx0 + 20, y, ww, 6, '#B9A57C' if i else RED, rx=2)
open(f"{OUT}/bha_opening_frame_full.svg", 'w').write(svg_doc(PW, PH, b, defs=defs, title='Bhanno MS opening folio frame (reconstruction)'))
print('ok')
