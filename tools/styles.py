# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""Border style definitions. Each returns dict(w, h, body, motif=(frag, w, h) optional)."""
import math
from orn import *

H = 80  # standard band tile height
GY0, GY1 = 9, 71  # gold ground extent
CY = 40

def frame(w, ground=P['gold'], outer=P['orange'], inner=P['pink_l'], dots=None, dotcol=None, dstep=6, extra=''):
    """ground band + symmetric rules. dots: 'out'|'in'|'both' adds dotted rule."""
    s = rect(0, 0, w, H, P['paper'])
    s += rect(0, GY0, w, GY1 - GY0, ground)
    for y in (GY0, GY1):
        s += hrule(y, w, 1.4, outer)
    s += hrule(GY0 - 4, w, .8, inner) + hrule(GY1 + 4, w, .8, inner)
    s += hrule(GY0 + 2.6, w, .7, inner) + hrule(GY1 - 2.6, w, .7, inner)
    if dots:
        c = dotcol or P['slate']
        if dots in ('out', 'both'):
            s += dotrule(GY0 - 6.5, w, dstep, 1.1, c) + dotrule(GY1 + 6.5, w, dstep, 1.1, c)
        if dots in ('in', 'both'):
            s += dotrule(GY0 + 5.5, w, dstep, 1.0, c) + dotrule(GY1 - 5.5, w, dstep, 1.0, c)
    return s + extra

def gold_texture(w):
    # faint burnishing strokes so flat gold reads as leaf
    s = ''
    for i, x in enumerate(range(3, int(w), 11)):
        s += path(f"M{x} {GY0+4} q2 {14 + (i%3)*4} -1 {GY1-GY0-8}", 'none', P['gold_l'], .6)
    return s

S = {}
def style(key, title, src):
    def deco(fn):
        S[key] = dict(fn=fn, title=title, src=src); return fn
    return deco

# ===================== A. Gold cartouche bands =====================
@style('bur_a01', 'Lobed cartouches, knotted', 'Burhanpuri p.9 (index)')
def _():
    w = 120
    s = frame(w, dots='out', dotcol=P['red'], dstep=5)
    s += cartouche(w/2, CY, 92, 46, P['gold'], P['orange'], 1.6, 'oval')
    s += cartouche(w/2, CY, 84, 38, 'none', P['pink_l'], .8, 'oval')
    for x in (0, w):
        s += bowtie(x, CY, 18, 50, P['orange'])
        s += lozenge(x, CY, 9, 20, P['blue'], P['white'], .6) + circle(x, CY, 2, P['yellow'])
        s += lozenge(x, GY0 + 5, 7, 8, P['blue']) + lozenge(x, GY1 - 5, 7, 8, P['blue'])
    return dict(w=w, h=H, body=s)

@style('bur_a02', 'Long panels, pearl knots', 'Burhanpuri p.50')
def _():
    w = 140
    s = frame(w, dots='both', dotcol=P['red'], dstep=5)
    s += cartouche(w/2, CY, 118, 44, P['gold'], P['orange'], 1.4, 'pointed')
    for x in (0, w):
        s += path(f"M{x-10} {GY0+3} L{x+10} {GY0+3} L{x+2} {CY} L{x+10} {GY1-3} L{x-10} {GY1-3} L{x-2} {CY}Z", P['yellow'], P['orange'], .8)
        s += circle(x, CY, 4.2, P['white'], P['slate_d'], .8) + circle(x, CY - 9, 2, P['blue']) + circle(x, CY + 9, 2, P['blue'])
    return dict(w=w, h=H, body=s)

@style('bur_a03', 'Panels with hourglass dividers', 'Burhanpuri p.54')
def _():
    w = 110
    s = frame(w, dots='both', dotcol=P['slate'], dstep=5)
    s += gold_texture(w)
    for x in (0, w):
        s += hourglass_bar(x, CY, 20, GY1 - GY0 - 6, P['gold_l'], P['pink'])
        s += path(f"M{x} {GY0+6} L{x} {GY1-6}", 'none', P['red'], .8) + circle(x, CY, 2.2, P['red'])
    return dict(w=w, h=H, body=s)

@style('bur_a04', 'Roundel & long cartouche', 'Burhanpuri p.100 / p.209')
def _():
    w = 170
    s = frame(w, dots='both', dotcol=P['slate'], dstep=5)
    s += cartouche(48, CY, 50, 50, P['gold_l'], P['pink'], 1.4, 'circle')
    s += cartouche(125, CY, 86, 48, P['gold'], P['pink'], 1.4, 'oval')
    for x in (0, 88, w):
        s += path(f"M{x-6} {GY0+3} L{x+6} {GY0+3} L{x} {CY-5}Z M{x-6} {GY1-3} L{x+6} {GY1-3} L{x} {CY+5}Z", P['green_d'])
        s += circle(x, CY, 1.8, P['red'])
    return dict(w=w, h=H, body=s)

@style('bur_a05', 'Pointed cartouches', 'Burhanpuri p.134 / p.161')
def _():
    w = 130
    s = frame(w, dots='both', dotcol=P['slate'], dstep=5)
    s += cartouche(w/2, CY, 120, 48, P['gold'], P['pink'], 1.3, 'pointed')
    for x in (0, w):
        s += path(f"M{x-5} {GY0+3} L{x+5} {GY0+3} L{x} {GY0+12}Z M{x-5} {GY1-3} L{x+5} {GY1-3} L{x} {GY1-12}Z", P['green_d'])
        s += circle(x, CY, 2, P['green_d'])
    return dict(w=w, h=H, body=s)

@style('bur_a06', 'Rounded panels, pink rules', 'Burhanpuri p.240')
def _():
    w = 120
    s = frame(w, dots='both', dotcol=P['slate'], dstep=5)
    s += rect(8, GY0 + 5, w - 16, GY1 - GY0 - 10, P['gold'], P['pink'], 1.3, rx=14)
    for x in (0, w):
        s += path(f"M{x-4} {GY0+3} L{x+4} {GY0+3} L{x} {CY}Z M{x-4} {GY1-3} L{x+4} {GY1-3} L{x} {CY}Z", P['green_d'])
    return dict(w=w, h=H, body=s)

@style('bur_a07', 'Gold with yellow bobbins', 'Burhanpuri p.261')
def _():
    w = 120
    s = frame(w, dots='both', dotcol=P['pink'], dstep=5)
    s += gold_texture(w)
    for x in (0, w):
        s += hourglass_bar(x, CY, 26, GY1 - GY0 - 8, P['yellow'], P['ochre'])
        s += path(f"M{x} {GY0+8} L{x} {GY1-8}", 'none', P['ochre'], .9)
    return dict(w=w, h=H, body=s)

@style('bur_a08', 'Lozenges with florets', 'Burhanpuri p.611')
def _():
    w = 64
    s = frame(w, dots='both', dotcol=P['red'], dstep=5)
    s += lozenge(w/2, CY, 30, 30, P['yellow'], P['ochre'], .8)
    s += g(w/2, CY, rosette(4, 9, 3.2, P['pink'], 2.2, P['green_d'], rot0=45))
    s += circle(0, CY, 1.6, P['red']) + circle(w, CY, 1.6, P['red'])
    return dict(w=w, h=H, body=s)

@style('bur_a09', 'Ring & oval chain, red knots', 'Burhanpuri p.629')
def _():
    w = 150
    s = frame(w, dots='both', dotcol=P['red'], dstep=5)
    s += cartouche(30, CY, 40, 40, 'none', P['orange'], 1.4, 'circle')
    s += cartouche(105, CY, 76, 40, 'none', P['orange'], 1.4, 'oval')
    for x in (0, 60, w):
        s += path(f"M{x} {GY0+3} L{x} {GY1-3}", 'none', P['blue'], 1.4)
        s += lozenge(x, CY, 8, 14, P['yellow'], P['orange'], .6)
    return dict(w=w, h=H, body=s)

@style('bur_a10', 'Panels & bobbins, black-white chain', 'Burhanpuri p.647 / p.650')
def _():
    w = 110
    s = frame(w)
    for y in (GY0 - 6.5, GY1 + 6.5):
        s += hrule(y, w, 2.4, P['ink'])
        s += dotrule(y, w, 5, 1, P['white'])
    s += gold_texture(w)
    for x in (0, w):
        s += hourglass_bar(x, CY, 22, GY1 - GY0 - 6, P['gold_l'], P['orange'])
        s += path(f"M{x} {GY0+5} L{x} {GY1-5}", 'none', P['red'], 1) + circle(x, CY, 2.4, P['yellow'])
    return dict(w=w, h=H, body=s)

# ===================== B. Floral on gold =====================
def vine(w, a=10, col=None, sw=1.1, y=CY):
    col = col or P['green_d']
    return path(f"M0 {y} C{w/6} {y-a} {w/3} {y-a} {w/2} {y} S{5*w/6} {y+a} {w} {y}", 'none', col, sw)

@style('bur_b01', 'Five-petal roses in roundels', 'Burhanpuri p.290')
def _():
    w = 76
    s = frame(w, dots=None)
    s += circle(w/2, CY, 21, P['cream'], P['gold_d'], .8)
    s += g(w/2, CY, rose5(19, P['red'], center=P['green'], ring=P['red_d']))
    for x in (0, w):
        s += g(x, CY - 3, leaf(15, 5, P['green'], P['green_d']), rot=-55)
        s += g(x, CY + 3, leaf(15, 5, P['green'], P['green_d']), rot=-125)
        s += g(x, CY - 3, leaf(15, 5, P['green'], P['green_d']), rot=55)
        s += g(x, CY + 3, leaf(15, 5, P['green'], P['green_d']), rot=125)
    return dict(w=w, h=H, body=s, motif=(rose5(19, P['red'], center=P['green'], ring=P['red_d']), 40, 40))

@style('bur_b02', 'Lilac bells with leaf sprays', 'Burhanpuri p.295')
def _():
    w = 90
    s = frame(w)
    s += g(28, CY + 6, bell(28, P['lilac'], P['white'], P['lilac_d']), rot=-75)
    s += g(30, CY + 6, path(f"M0 0 Q-6 8 -16 10", 'none', P['green_d'], 1.2))
    s += g(66, CY + 18, curved_leaf(36, 6, .45, P['green'], P['green_d']), rot=10)
    s += g(70, CY + 18, curved_leaf(26, 5, -.3, P['green_l'], P['green_d']), rot=-30)
    return dict(w=w, h=H, body=s, motif=(bell(28, P['lilac'], P['white'], P['lilac_d']), 40, 40))

@style('bur_b03', 'Pink tulips on leafy stalks', 'Burhanpuri p.297 / p.559')
def _():
    w = 120
    s = frame(w)
    s += path(f"M14 {CY} L70 {CY}", 'none', P['green_d'], 1.4)
    s += g(36, CY, leaf(18, 5, P['green'], P['green_d']), rot=-55) + g(36, CY, leaf(18, 5, P['green'], P['green_d']), rot=-125)
    s += g(54, CY, leaf(14, 4.5, P['green'], P['green_d']), rot=-60) + g(54, CY, leaf(14, 4.5, P['green'], P['green_d']), rot=-120)
    s += g(70, CY, tulip(36, P['pink'], P['pink_l'], P['rose']), rot=90)
    return dict(w=w, h=H, body=s, motif=(tulip(36, P['pink'], P['pink_l'], P['rose']), 40, 40))

@style('bur_b04', 'Blue irises on undulating stem', 'Burhanpuri p.304 / p.312')
def _():
    w = 96
    s = frame(w)
    s += vine(w, 12, P['green_d'], 1.3)
    s += g(24, CY - 4, iris(26, P['blue'], P['blue_d'], P['white']), rot=-20)
    s += g(72, CY + 4, iris(26, P['blue'], P['blue_d'], P['white']), rot=200)
    s += g(48, CY, curved_leaf(30, 4.5, .35, P['green'], P['green_d']), rot=-60)
    s += g(48, CY, curved_leaf(30, 4.5, .35, P['green'], P['green_d']), rot=120)
    return dict(w=w, h=H, body=s, motif=(iris(26, P['blue'], P['blue_d'], P['white']), 40, 40))

@style('bur_b05', 'Violet flowers on scrolling vine', 'Burhanpuri p.320')
def _():
    w = 100
    s = frame(w)
    s += vine(w, 15, P['green_d'], 1.2)
    for x, y, r in ((25, CY - 10, -25), (75, CY + 10, 155)):
        s += g(x, y, lily(20, P['purple'], P['lilac'], P['violet']), rot=r)
    for x, y, r in ((50, CY, -40), (50, CY, 140), (8, CY - 6, 30), (92, CY + 6, 210)):
        s += g(x, y, curved_leaf(22, 4, .3, P['green'], P['green_d']), rot=r)
    return dict(w=w, h=H, body=s)

@style('bur_b06', 'Red tulip chain', 'Burhanpuri p.329')
def _():
    w = 70
    s = frame(w)
    s += path(f"M0 {CY} L{w} {CY}", 'none', P['green_d'], 1.2)
    s += g(30, CY + 2, tulip(26, P['red'], P['pink_l'], P['red_d']), rot=90)
    s += g(52, CY, leaf(14, 4.5, P['green'], P['green_d']), rot=-40) + g(52, CY, leaf(14, 4.5, P['green'], P['green_d']), rot=-140)
    s += g(6, CY, leaf(11, 4, P['green'], P['green_d']), rot=-50) + g(6, CY, leaf(11, 4, P['green'], P['green_d']), rot=-130)
    return dict(w=w, h=H, body=s)

@style('bur_b07', 'Kashmiri ogee lattice, yellow & blue', 'Burhanpuri p.337 / p.379')
def _():
    w = 72
    s = frame(w, ground=P['yellow'])
    s += path(f"M0 {GY0+2} C18 {GY0+2} 18 {GY1-2} 36 {GY1-2} C54 {GY1-2} 54 {GY0+2} 72 {GY0+2}", 'none', P['blue_d'], 3)
    s += path(f"M0 {GY1-2} C18 {GY1-2} 18 {GY0+2} 36 {GY0+2} C54 {GY0+2} 54 {GY1-2} 72 {GY1-2}", 'none', P['blue_d'], 3)
    s += path(f"M0 {GY0+2} C18 {GY0+2} 18 {GY1-2} 36 {GY1-2} C54 {GY1-2} 54 {GY0+2} 72 {GY0+2}", 'none', P['white'], .8)
    s += path(f"M0 {GY1-2} C18 {GY1-2} 18 {GY0+2} 36 {GY0+2} C54 {GY0+2} 54 {GY1-2} 72 {GY1-2}", 'none', P['white'], .8)
    for x in (0, 36, 72):
        s += g(x, CY, rose5(8, P['pink'], center=P['yellow']))
    s += g(18, CY, rosette(6, 9, 3, P['red'], 2.2, P['white'])) + g(54, CY, rosette(6, 9, 3, P['red'], 2.2, P['white']))
    s += lozenge(36, GY0 + 4, 8, 6, P['red']) + lozenge(36, GY1 - 4, 8, 6, P['red'])
    return dict(w=w, h=H, body=s)

@style('bur_b08', 'Blossoms on yellow ground', 'Burhanpuri p.341')
def _():
    w = 64
    s = frame(w, ground=P['yellow'])
    s += g(20, CY + 2, rosette(5, 11, 5, P['pink_l'], 3, P['magenta'], P['pink']))
    s += g(46, CY - 2, rosette(5, 10, 5, P['white'], 3, P['slate_d'], P['slate']))
    s += g(33, CY + 12, leaf(10, 4, P['green'], P['green_d']), rot=-100) + g(33, CY - 12, leaf(10, 4, P['green'], P['green_d']), rot=80)
    return dict(w=w, h=H, body=s)

@style('bur_b09', 'Pink rosettes on vine with leaves', 'Burhanpuri p.345')
def _():
    w = 64
    s = frame(w)
    s += vine(w, 8, P['green_d'], 1)
    s += g(w/2, CY, circle(0, 0, 15, P['pink_l']) + star5(14, P['pink'], P['magenta'], P['green_d']))
    for x in (0, w):
        for r in (-60, -120, 60, 120):
            s += g(x, CY, leaf(13, 4.5, P['green'], P['green_d']), rot=r)
    return dict(w=w, h=H, body=s, motif=(circle(0, 0, 15, P['pink_l']) + star5(14, P['pink'], P['magenta'], P['green_d']), 34, 34))

@style('bur_b10', 'Blue florets in ogival frames', 'Burhanpuri p.355')
def _():
    w = 60
    s = frame(w)
    s += path(f"M0 {GY0+3} Q15 {CY} 0 {GY1-3} M{w} {GY0+3} Q{w-15} {CY} {w} {GY1-3}", 'none', P['red'], 1)
    s += g(w/2, CY, rose5(12, P['slate'], center=P['red'], dots=P['white']))
    s += g(w/2 - 13, CY, leaf(8, 3, P['green'], None), rot=-90) + g(w/2 + 13, CY, leaf(8, 3, P['green'], None), rot=90)
    s += circle(0, CY, 2.4, P['white'])
    return dict(w=w, h=H, body=s)

@style('bur_b11', 'Red poppies, sparse sprigs', 'Burhanpuri p.360')
def _():
    w = 120
    s = frame(w)
    s += path(f"M30 {CY+4} L60 {CY+2}", 'none', P['green_d'], 1.3)
    s += g(40, CY + 4, leaf(18, 6, P['green'], P['green_d']), rot=-30) + g(40, CY + 4, leaf(16, 6, P['green'], P['green_d']), rot=-150)
    s += g(62, CY + 2, poppy_side(26, P['red'], P['red_d'], P['green']), rot=80)
    return dict(w=w, h=H, body=s, motif=(poppy_side(26, P['red'], P['red_d'], P['green']), 40, 40))

@style('bur_b12', 'Gold-on-gold arabesque', 'Burhanpuri p.369')
def _():
    w = 90
    s = frame(w, ground=P['gold_l'])
    for k in (0, 1):
        x0 = k * 45
        s += path(f"M{x0} {CY} C{x0+10} {CY-22} {x0+30} {CY-22} {x0+22} {CY-4} C{x0+18} {CY+6} {x0+8} {CY} {x0+14} {CY-8}", 'none', P['gold_d'], 1.4)
        s += path(f"M{x0+22} {CY-4} C{x0+30} {CY+16} {x0+42} {CY+18} {x0+45} {CY}", 'none', P['gold_d'], 1.4)
        s += g(x0 + 33, CY + 10, leaf(9, 3.5, P['gold_d']), rot=40) + g(x0 + 8, CY - 12, leaf(9, 3.5, P['gold_d']), rot=-50)
    return dict(w=w, h=H, body=s)

@style('bur_b13', 'Red roundels & acanthus curls', 'Burhanpuri p.384')
def _():
    w = 64
    s = frame(w)
    s += circle(18, CY, 13, P['red'], P['red_d'], .8)
    for dx, dy in ((-4, -4), (4, -4), (-4, 4), (4, 4)):
        s += circle(18 + dx, CY + dy, 2.1, P['white'])
    s += g(48, CY, cscroll(11, P['green'], P['green_d']))
    return dict(w=w, h=H, body=s)

@style('bur_b14', 'Tulip at tip of sweeping leaf', 'Burhanpuri p.395 / p.407 / p.450')
def _():
    w = 110
    s = frame(w)
    s += path(f"M20 {CY+8} C40 {CY-6} 60 {CY-6} 76 {CY-2}", 'none', P['green_d'], 1.2)
    s += path(f"M20 {CY+8} C34 {CY-14} 58 {CY-16} 74 {CY-6} C56 {CY-8} 38 {CY-2} 20 {CY+8}Z", P['green'], P['green_d'], .7)
    s += path(f"M24 {CY+9} C40 {CY+12} 58 {CY+8} 70 {CY+2} C54 {CY+2} 38 {CY+4} 24 {CY+9}Z", P['green_l'], P['green_d'], .6)
    s += g(78, CY - 2, tulip(24, P['red'], P['pink_l'], P['red_d']), rot=80)
    s += circle(76, CY - 2, 2.2, P['white'])
    return dict(w=w, h=H, body=s)

@style('bur_b15', 'Pink buds with leaf pairs', 'Burhanpuri p.415 / p.465')
def _():
    w = 96
    s = frame(w)
    s += path(f"M26 {CY} L52 {CY}", 'none', P['green_d'], 1.2)
    s += g(34, CY, leaf(14, 5, P['green'], P['green_d']), rot=-40) + g(34, CY, leaf(14, 5, P['green'], P['green_d']), rot=-140)
    s += g(54, CY, lotus_bud(20, 9, P['lilac'], P['purple'], P['pink_l']), rot=90)
    s += circle(52, CY, 2, P['rose'])
    return dict(w=w, h=H, body=s)

@style('bur_b16', 'Pomegranate buds with pearls', 'Burhanpuri p.420')
def _():
    w = 64
    s = frame(w)
    s += vine(w, 6, P['green_d'], 1)
    s += g(w/2, CY, pomegranate(11, P['red'], P['white'], P['green']), rot=90)
    s += g(8, CY, leaf(12, 4, P['green'], P['green_d']), rot=-45) + g(8, CY, leaf(12, 4, P['green'], P['green_d']), rot=-135)
    return dict(w=w, h=H, body=s, motif=(pomegranate(11, P['red'], P['white'], P['green']), 30, 34))

@style('bur_b17', 'Large lily sprays', 'Burhanpuri p.431')
def _():
    w = 130
    s = frame(w)
    s += path(f"M14 {CY+8} C40 {CY+4} 60 {CY} 80 {CY-2}", 'none', P['green_d'], 1.4)
    s += g(84, CY - 2, lily(30, P['red'], P['pink_l'], P['red_d']), rot=80)
    s += g(70, CY + 2, lily(22, P['lilac'], P['white'], P['lilac_d']), rot=100)
    s += g(30, CY + 6, curved_leaf(22, 6, .3, P['green'], P['green_d']), rot=-30) + g(44, CY + 4, curved_leaf(20, 6, -.3, P['green'], P['green_d']), rot=-150)
    return dict(w=w, h=H, body=s)

@style('bur_b18', 'Grape clusters & vine leaves', 'Burhanpuri p.440 / p.527')
def _():
    w = 74
    s = frame(w)
    s += vine(w, 8, P['red_d'], .8)
    s += g(22, CY - 10, grapes(3.6, P['lilac'], P['white']), rot=-90)
    s += g(56, CY, rosette(5, 12, 6, P['green'], 2, P['green_d'], P['green_d']))
    return dict(w=w, h=H, body=s, motif=(grapes(3.6, P['lilac'], P['white']), 26, 26))

@style('bur_b19', 'Red rosettes in leaf lozenges', 'Burhanpuri p.455')
def _():
    w = 96
    s = frame(w)
    s += path(f"M14 {CY} C30 {CY-14} 66 {CY-14} 82 {CY} C66 {CY+14} 30 {CY+14} 14 {CY}Z", P['green'], P['green_d'], .8)
    s += g(48, CY, rosette(6, 11, 5, P['red'], 3.2, P['white'], P['red_d']))
    s += g(30, CY, rosette(5, 6, 3, P['pink'], 1.5, P['yellow']))
    return dict(w=w, h=H, body=s)

@style('bur_b20', 'Red roses on wavy vine', 'Burhanpuri p.471')
def _():
    w = 70
    s = frame(w)
    s += path(f"M0 {CY+10} C15 {CY+10} 20 {CY-14} 35 {CY-14} S55 {CY+10} 70 {CY+10}", 'none', P['green_d'], 1)
    s += path(f"M0 {CY-10} C15 {CY-10} 20 {CY+14} 35 {CY+14} S55 {CY-10} 70 {CY-10}", 'none', P['green_d'], 1)
    s += g(35, CY, rose5(14, P['red'], center=P['white'], ring=P['red_d'], dots=P['pink_l']))
    for x, y, r in ((10, CY + 8, -40), (10, CY - 8, -140), (60, CY + 8, 40), (60, CY - 8, 140)):
        s += g(x, y, leaf(10, 4, P['green'], P['green_d']), rot=r)
    return dict(w=w, h=H, body=s)

@style('bur_b21', 'Star flowers & leaves', 'Burhanpuri p.480')
def _():
    w = 74
    s = frame(w)
    s += g(26, CY, star5(14, P['red'], P['red_d'], P['white']))
    s += g(54, CY + 10, curved_leaf(24, 5, .3, P['green'], P['green_d']), rot=20)
    s += g(58, CY + 10, curved_leaf(18, 4, -.3, P['green_l'], P['green_d']), rot=-15)
    return dict(w=w, h=H, body=s)

@style('bur_b22', 'Pink flowers in vine roundels', 'Burhanpuri p.488 / p.504 / p.510')
def _():
    w = 70
    s = frame(w)
    s += circle(35, CY, 20, 'none', P['green_d'], .9)
    s += path(f"M0 {CY} C8 {CY-16} 14 {CY-20} 18 {CY-12} M70 {CY} C62 {CY+16} 56 {CY+20} 52 {CY+12}", 'none', P['green_d'], .9)
    s += path(f"M0 {CY} C8 {CY+16} 14 {CY+20} 18 {CY+12} M70 {CY} C62 {CY-16} 56 {CY-20} 52 {CY-12}", 'none', P['green_d'], .9)
    s += g(35, CY, pansy(12, P['pink_l'], P['red'], P['yellow']))
    for x, y, r in ((4, CY - 12, 20), (4, CY + 12, 160), (66, CY - 12, -20), (66, CY + 12, 200)):
        s += g(x, y, leaf(10, 4, P['green'], P['green_d']), rot=r)
    return dict(w=w, h=H, body=s, motif=(pansy(12, P['pink_l'], P['red'], P['yellow']), 34, 34))

@style('bur_b23', 'Almond buds with pointed sepals', 'Burhanpuri p.496')
def _():
    w = 100
    s = frame(w)
    s += path(f"M0 {CY} L{w} {CY}", 'none', P['green_d'], 1)
    s += g(28, CY, almond_bud(40, 13, P['rose'], P['red_d'], P['green']))
    return dict(w=w, h=H, body=s)

@style('bur_b24', 'Purple lilies with leaves', 'Burhanpuri p.520')
def _():
    w = 84
    s = frame(w)
    s += g(30, CY + 10, lily(26, P['lilac'], P['white'], P['purple']), rot=-70)
    s += g(60, CY + 14, curved_leaf(30, 6, .3, P['green'], P['green_d']), rot=-10)
    s += g(64, CY - 14, curved_leaf(22, 5, -.3, P['green'], P['green_d']), rot=190)
    return dict(w=w, h=H, body=s)

@style('bur_b25', 'Blue & white blossoms on vine', 'Burhanpuri p.535')
def _():
    w = 76
    s = frame(w)
    s += vine(w, 10, P['green_d'], 1)
    s += g(24, CY - 2, pansy(12, P['blue'], P['white'], P['yellow']))
    s += g(56, CY + 4, leaf(16, 5, P['green'], P['green_d']), rot=-30) + g(56, CY + 4, leaf(14, 5, P['green'], P['green_d']), rot=40)
    return dict(w=w, h=H, body=s)

@style('bur_b26', 'Rosettes & acanthus, blue hearts', 'Burhanpuri p.545')
def _():
    w = 72
    s = frame(w)
    s += path(f"M0 {CY+12} C12 {CY+12} 18 {CY-10} 36 {CY-12} S60 {CY+12} 72 {CY+12}", 'none', P['green_d'], .8)
    s += g(20, CY, rosette(6, 11, 5, P['red'], 3.5, P['slate'], P['red_d']))
    s += g(52, CY - 2, cscroll(11, P['green'], P['green_d']), rot=180)
    return dict(w=w, h=H, body=s)

@style('bur_b27', 'Alternating pink rosettes & red florets', 'Burhanpuri p.552 / p.556')
def _():
    w = 100
    s = frame(w)
    s += path(f"M0 {CY} C12 {CY-16} 38 {CY-16} 50 {CY} S88 {CY+16} 100 {CY}", 'none', P['green_d'], .9)
    s += g(25, CY - 2, rosette(8, 11, 4.5, P['pink'], 3, P['magenta'], P['rose'], P['pink_l']))
    s += g(75, CY + 2, rose5(8, P['red'], center=P['white']))
    s += g(50, CY, leaf(11, 4, P['green'], P['green_d']), rot=-30) + g(50, CY, leaf(11, 4, P['green'], P['green_d']), rot=30) + g(50, CY, leaf(11, 4, P['green'], P['green_d']), rot=180)
    s += g(0, CY, leaf(11, 4, P['green'], P['green_d']), rot=150) + g(100, CY, leaf(11, 4, P['green'], P['green_d']), rot=-150)
    return dict(w=w, h=H, body=s)

@style('bur_b28', 'Pinecones with red flowers', 'Burhanpuri p.567')
def _():
    w = 70
    s = frame(w)
    s += g(24, CY + 4, pinecone(22, 9, P['lilac'], P['white'], P['red']), rot=-90)
    s += g(50, CY, star5(7, P['red'], P['red_d'], P['white']))
    s += g(58, CY + 6, leaf(14, 4, P['green'], P['green_d']), rot=30) + g(58, CY - 6, leaf(14, 4, P['green'], P['green_d']), rot=150)
    return dict(w=w, h=H, body=s)

@style('bur_b29', 'Serrated feather leaves', 'Burhanpuri p.575')
def _():
    w = 110
    s = frame(w)
    s += g(20, CY + 6, serrated_leaf(70, 12, P['green'], P['green_d'], 8), rot=80)
    return dict(w=w, h=H, body=s, motif=(serrated_leaf(70, 12, P['green'], P['green_d'], 8), 30, 76))

@style('bur_b30', 'Lotus buds with leaf diamonds', 'Burhanpuri p.585')
def _():
    w = 110
    s = frame(w)
    s += g(18, CY, lotus_bud(52, 13, P['magenta'], P['violet'], P['pink_l']), rot=90)
    s += lozenge(90, CY, 18, 26, P['green'], P['green_d'], .8) + path(f"M90 {CY-12} L90 {CY+12}", 'none', P['green_d'], .8)
    return dict(w=w, h=H, body=s, motif=(lotus_bud(52, 13, P['magenta'], P['violet'], P['pink_l']), 30, 56))

@style('bur_b31', 'Red tulips on running vine', 'Burhanpuri p.592')
def _():
    w = 80
    s = frame(w)
    s += vine(w, 12, P['green_d'], 1)
    s += g(26, CY - 4, tulip(18, P['red'], P['white'], P['red_d']), rot=60)
    s += g(54, CY + 4, curved_leaf(18, 5, .3, P['green'], P['green_d']), rot=-130) + g(56, CY + 2, curved_leaf(16, 5, -.3, P['green'], P['green_d']), rot=50)
    return dict(w=w, h=H, body=s)

@style('bur_b32', 'Lotus fans with leaf pairs', 'Burhanpuri p.599')
def _():
    w = 120
    s = frame(w)
    s += path(f"M30 {CY} L72 {CY}", 'none', P['green_d'], 1.2)
    s += g(40, CY, leaf(26, 7, P['green_d'], P['green']), rot=-40) + g(40, CY, leaf(26, 7, P['green_d'], P['green']), rot=-140)
    s += g(78, CY, lotus_fan(24, P['rose'], P['red_d']), rot=90)
    return dict(w=w, h=H, body=s, motif=(lotus_fan(24, P['rose'], P['red_d']), 40, 40))
