#!/usr/bin/env python3
"""Draw the app icons: a timer ring split like a 25-minute slot (15 green, 5 yellow, 5 red) on blue.

Run from the repository root: python3 tools/icons.py  (needs Pillow)
Writes icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png and icon.svg.
"""
from PIL import Image, ImageDraw

BLUE, GREEN, YELLOW, RED, WHITE = '#1F5FA8', '#1D7646', '#F4C430', '#B4233A', '#F6F7F3'
SEGMENTS = [(0, 216, GREEN), (216, 288, YELLOW), (288, 360, RED)]  # degrees clockwise from 12 o'clock
GAP = 4  # degrees of blue between segments


def draw(size, full_bleed, ring_r, ring_w):
    """ring_r and ring_w are fractions of the icon size (radius to the stroke centre, stroke width)."""
    k = 4  # supersample, then shrink for smooth edges
    S = size * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if full_bleed:
        d.rectangle([0, 0, S, S], fill=BLUE)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(0.22 * S), fill=BLUE)
    c, r, w = S / 2, ring_r * S, ring_w * S
    box = [c - r - w / 2, c - r - w / 2, c + r + w / 2, c + r + w / 2]
    for a, b, col in SEGMENTS:
        d.arc(box, start=a - 90 + GAP / 2, end=b - 90 - GAP / 2, fill=col, width=int(w))
    # a clock hand at 12 and its hub
    hw = 0.045 * S
    d.rounded_rectangle([c - hw / 2, c - 0.17 * S, c + hw / 2, c], radius=int(hw / 2), fill=WHITE)
    d.ellipse([c - 0.05 * S, c - 0.05 * S, c + 0.05 * S, c + 0.05 * S], fill=WHITE)
    return im.resize((size, size), Image.LANCZOS)


def svg(ring_r=0.27, ring_w=0.09):
    """The same drawing as a scalable favicon, on a 100-unit canvas."""
    r, w = ring_r * 100, ring_w * 100
    arcs = ''.join(
        f'<circle cx="50" cy="50" r="{r:g}" fill="none" stroke="{col}" stroke-width="{w:g}" pathLength="360" '
        f'stroke-dasharray="{b - a - GAP:g} 360" stroke-dashoffset="{-(a + GAP / 2):g}" transform="rotate(-90 50 50)"/>'
        for a, b, col in SEGMENTS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<rect width="100" height="100" rx="22" fill="{BLUE}"/>{arcs}'
            f'<rect x="47.75" y="33" width="4.5" height="17" rx="2.25" fill="{WHITE}"/>'
            f'<circle cx="50" cy="50" r="5" fill="{WHITE}"/></svg>\n')


if __name__ == '__main__':
    draw(192, False, 0.27, 0.09).save('icon-192.png')
    draw(512, False, 0.27, 0.09).save('icon-512.png')
    # maskable: full-bleed, drawing inside the central safe circle (radius 40% of the size)
    draw(512, True, 0.24, 0.08).save('icon-maskable-512.png')
    # iOS rounds the corners itself and wants no transparency
    draw(180, True, 0.27, 0.09).convert('RGB').save('apple-touch-icon.png')
    open('icon.svg', 'w').write(svg())
    print('icons written')
