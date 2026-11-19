"""Generate The Den's original SVG illustrations into src/assets/img/art/.

Usage: python3 tools/make_art.py

Every illustration shares one palette (black felt, metallic gold, ivory cards,
muted card-red) and is built from simple geometry so it stays crisp and light.
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "assets", "img", "art")
os.makedirs(OUT, exist_ok=True)

INK, FELT, FELT2 = "#0d0d0c", "#151513", "#1e1c18"
GOLD, GOLD_L, GOLD_D = "#c6a15b", "#ecd193", "#8e6f37"
IVORY, IVORY_D, RED = "#f7f3ea", "#e3dccd", "#a3313a"
SERIF = "Georgia, 'Times New Roman', serif"

SUITS = {
    "spade": "M7.18.94a1 1 0 0 1 1.64 0C10.6 3.4 15 6.6 15 9.8 15 11.9 13.4 13.3 11.6 13.3c-1 0-1.9-.4-2.5-1.1.2 1.3.7 2.2 1.4 2.8H5.5c.7-.6 1.2-1.5 1.4-2.8-.6.7-1.5 1.1-2.5 1.1C2.6 13.3 1 11.9 1 9.8c0-3.2 4.4-6.4 6.18-8.86Z",
    "heart": "M8 14.5S1 10.3 1 5.7C1 3.6 2.6 2 4.6 2c1.4 0 2.6.8 3.4 2 .8-1.2 2-2 3.4-2C13.4 2 15 3.6 15 5.7c0 4.6-7 8.8-7 8.8Z",
    "diamond": "M8 .8 13.6 8 8 15.2 2.4 8Z",
    "club": "M8 1.1a3.2 3.2 0 0 1 3.05 4.18A3.2 3.2 0 1 1 9.3 11.4l.9 3.8H5.8l.9-3.8a3.2 3.2 0 1 1-1.75-6.12A3.2 3.2 0 0 1 8 1.1Z",
}


def defs():
    syms = "".join(f'<symbol id="{k}" viewBox="0 0 16 16"><path d="{v}"/></symbol>' for k, v in SUITS.items())
    return f"""<defs>{syms}
<radialGradient id="felt" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="{FELT2}"/><stop offset="1" stop-color="{INK}"/></radialGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>
<linearGradient id="ivory" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffdf8"/><stop offset="1" stop-color="{IVORY}"/></linearGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{GOLD}" stop-opacity=".38"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/></filter>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1" fill="{GOLD}" opacity=".16"/></pattern>
</defs>"""


def suit(name, x, y, size, fill):
    return f'<use href="#{name}" x="{x - size / 2:.1f}" y="{y - size / 2:.1f}" width="{size}" height="{size}" fill="{fill}"/>'


def card(cx, cy, w, h, rank, s, angle=0, pivot=None, big=True):
    """An ivory playing card centred on (cx, cy)."""
    col = RED if s in ("heart", "diamond") else INK
    x, y = cx - w / 2, cy - h / 2
    rot = f' transform="rotate({angle} {pivot[0]} {pivot[1]})"' if pivot else (f' transform="rotate({angle} {cx} {cy})"' if angle else "")
    fs = w * 0.17
    g = [f'<g{rot} filter="url(#shadow)">',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w * .08}" fill="url(#ivory)" stroke="{IVORY_D}" stroke-width="1.5"/>',
         f'<rect x="{x + w * .07}" y="{y + h * .05}" width="{w * .86}" height="{h * .9}" rx="{w * .05}" fill="none" stroke="{GOLD}" stroke-opacity=".45" stroke-width="1"/>',
         f'<text x="{x + w * .14}" y="{y + h * .16}" font-family="{SERIF}" font-weight="700" font-size="{fs:.1f}" fill="{col}" text-anchor="middle">{rank}</text>',
         suit(s, x + w * .14, y + h * .24, w * .11, col),
         f'<g transform="rotate(180 {cx} {cy})"><text x="{x + w * .14}" y="{y + h * .16}" font-family="{SERIF}" font-weight="700" font-size="{fs:.1f}" fill="{col}" text-anchor="middle">{rank}</text>{suit(s, x + w * .14, y + h * .24, w * .11, col)}</g>']
    if big:
        g.append(suit(s, cx, cy, w * .42, col))
    g.append("</g>")
    return "".join(g)


def chip_stack(cx, base_y, n, face, edge, rx=34, ry=11, step=7):
    out = [f'<g filter="url(#shadow)">']
    for i in range(n):
        y = base_y - i * step
        out.append(f'<ellipse cx="{cx}" cy="{y + 3}" rx="{rx}" ry="{ry}" fill="{edge}"/>')
        out.append(f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="{face}"/>')
        out.append(f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" stroke="{edge}" stroke-width="5" stroke-dasharray="7 9"/>')
    top = base_y - (n - 1) * step
    out.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx * .55}" ry="{ry * .55}" fill="none" stroke="{edge}" stroke-opacity=".6" stroke-width="1.2"/>')
    out.append("</g>")
    return "".join(out)


def frame(w, h, inset=18):
    return (f'<rect x="{inset}" y="{inset}" width="{w - 2 * inset}" height="{h - 2 * inset}" rx="14" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width="1.5"/>'
            f'<rect x="{inset + 8}" y="{inset + 8}" width="{w - 2 * inset - 16}" height="{h - 2 * inset - 16}" rx="10" fill="none" stroke="{GOLD}" stroke-opacity=".2" stroke-width="1"/>')


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<title>{title}</title>{defs()}{body}</svg>')


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    print(name, len(content), "bytes")


# 1. A fanned royal hand with chip stacks (hero card, 5:7)
W, H = 500, 700
b = [f'<rect width="{W}" height="{H}" fill="url(#felt)"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
     f'<ellipse cx="250" cy="300" rx="230" ry="200" fill="url(#glow)"/>', frame(W, H)]
for (rank, s), a in zip([("A", "spade"), ("K", "heart"), ("Q", "diamond"), ("J", "club")], [-19, -6.5, 6.5, 19]):
    b.append(card(250, 300, 140, 198, rank, s, angle=a, pivot=(250, 720)))
b.append(chip_stack(150, 590, 6, "#1b1b1b", GOLD))
b.append(chip_stack(250, 610, 9, GOLD, INK, rx=38, ry=12))
b.append(chip_stack(350, 592, 5, IVORY, INK))
b.append(f'<text x="250" y="660" font-family="{SERIF}" font-size="15" letter-spacing="6" fill="{GOLD}" text-anchor="middle" opacity=".85">THE DEN · ROWLETT</text>')
write("art-hand.svg", svg(W, H, "".join(b), "A fanned royal hand of cards above stacks of poker chips"))

# 2. Your seat — top-down table under a lamp, one gold reserved chair (3:4)
W, H = 600, 800
cx, cy, rx, ry = 300, 380, 160, 230
b = [f'<rect width="{W}" height="{H}" fill="{INK}"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
     f'<ellipse cx="{cx}" cy="{cy}" rx="300" ry="380" fill="url(#glow)"/>']
# chairs
n = 8
for i in range(n):
    ang = math.radians(90 + i * 360 / n)
    x = cx + (rx + 58) * math.cos(ang)
    y = cy + (ry + 56) * math.sin(ang)
    rot = math.degrees(ang) + 90
    yours = i == 0
    fill = "url(#gold)" if yours else "#34312b"
    stroke = GOLD_L if yours else "#6b5a3a"
    b.append(f'<g transform="rotate({rot:.1f} {x:.1f} {y:.1f})" filter="url(#shadow)">'
             f'<rect x="{x - 34:.1f}" y="{y - 26:.1f}" width="68" height="52" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
             f'<rect x="{x - 28:.1f}" y="{y + 8:.1f}" width="56" height="14" rx="7" fill="#000" fill-opacity=".25"/></g>')
    if yours:
        b.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="70" ry="60" fill="url(#glow)"/>')
# table
b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 22}" ry="{ry + 22}" fill="#2a2016" stroke="{GOLD}" stroke-width="2.5" filter="url(#shadow)"/>')
b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#felt)" stroke="{GOLD_D}" stroke-width="1.5"/>')
b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 34}" ry="{ry - 40}" fill="none" stroke="{GOLD}" stroke-opacity=".4" stroke-width="1.2" stroke-dasharray="6 8"/>')
# community cards
for i, (r, s) in enumerate([("A", "spade"), ("K", "heart"), ("Q", "diamond"), ("J", "club"), ("10", "spade")]):
    b.append(card(cx - 108 + i * 54, cy - 30, 46, 66, r, s, big=False))
b.append(chip_stack(cx - 40, cy + 90, 5, GOLD, INK, rx=24, ry=8, step=5))
b.append(chip_stack(cx + 30, cy + 96, 3, IVORY, INK, rx=24, ry=8, step=5))
# reserved plaque at the gold seat
py = cy + ry + 56 + 50
b.append(f'<rect x="{cx - 70}" y="{py}" width="140" height="34" rx="17" fill="{INK}" stroke="{GOLD}" stroke-width="1.5"/>')
b.append(f'<text x="{cx}" y="{py + 22}" font-family="{SERIF}" font-size="14" letter-spacing="4" fill="{GOLD_L}" text-anchor="middle">RESERVED</text>')
# lamp
b.append(f'<path d="M{cx - 70} 70 L{cx + 70} 70 L{cx + 40} 20 L{cx - 40} 20 Z" fill="url(#gold)"/>')
b.append(f'<line x1="{cx}" y1="0" x2="{cx}" y2="20" stroke="{GOLD_D}" stroke-width="2"/>')
b.append(f'<path d="M{cx - 70} 70 L{cx - 230} 300 L{cx + 230} 300 L{cx + 70} 70 Z" fill="url(#glow)" opacity=".5"/>')
write("art-seat.svg", svg(W, H, "".join(b), "A poker table seen from above with one gold seat reserved"))

# 3. Chess — pieces standing on the board edge (6:5)
W, H = 600, 500
b = [f'<rect width="{W}" height="{H}" fill="url(#felt)"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
     f'<ellipse cx="300" cy="230" rx="260" ry="190" fill="url(#glow)"/>']
# board strip in slight perspective: two rows of squares
for row, (y, hh) in enumerate([(372, 46), (418, 62)]):
    nsq = 8
    for i in range(nsq):
        top_w = 560 / nsq if row else 480 / nsq
        bot_w = 600 / nsq if row else 560 / nsq
        x0t = (W - top_w * nsq) / 2 + i * top_w
        x0b = (W - bot_w * nsq) / 2 + i * bot_w
        dark = (i + row) % 2 == 0
        col = "#26231d" if dark else "#e9e2d2"
        b.append(f'<path d="M{x0t:.1f} {y} L{x0t + top_w:.1f} {y} L{x0b + bot_w:.1f} {y + hh} L{x0b:.1f} {y + hh} Z" fill="{col}"/>')
b.append(f'<path d="M60 372 L540 372 L600 480 L0 480 Z" fill="none" stroke="{GOLD}" stroke-width="2"/>')


def base(x, w, y):
    return (f'<rect x="{x - w / 2}" y="{y - 16}" width="{w}" height="16" rx="5"/>'
            f'<rect x="{x - w / 2 + 8}" y="{y - 26}" width="{w - 16}" height="12" rx="5"/>')


def piece(kind, x, y, fill, stroke):
    g = [f'<g fill="{fill}" stroke="{stroke}" stroke-width="1.5" filter="url(#shadow)">']
    if kind == "pawn":
        g += [base(x, 76, y), f'<path d="M{x - 22} {y - 26} C{x - 18} {y - 70} {x - 10} {y - 86} {x - 10} {y - 96} L{x + 10} {y - 96} C{x + 10} {y - 86} {x + 18} {y - 70} {x + 22} {y - 26} Z"/>',
              f'<ellipse cx="{x}" cy="{y - 98}" rx="22" ry="6"/>', f'<circle cx="{x}" cy="{y - 122}" r="22"/>']
    elif kind == "rook":
        g += [base(x, 92, y), f'<path d="M{x - 28} {y - 26} L{x - 22} {y - 130} L{x + 22} {y - 130} L{x + 28} {y - 26} Z"/>',
              f'<path d="M{x - 34} {y - 130} L{x + 34} {y - 130} L{x + 34} {y - 170} L{x + 20} {y - 170} L{x + 20} {y - 156} L{x + 7} {y - 156} L{x + 7} {y - 170} L{x - 7} {y - 170} L{x - 7} {y - 156} L{x - 20} {y - 156} L{x - 20} {y - 170} L{x - 34} {y - 170} Z"/>']
    elif kind == "king":
        g += [base(x, 100, y), f'<path d="M{x - 30} {y - 26} C{x - 24} {y - 110} {x - 18} {y - 160} {x - 30} {y - 196} L{x + 30} {y - 196} C{x + 18} {y - 160} {x + 24} {y - 110} {x + 30} {y - 26} Z"/>',
              f'<ellipse cx="{x}" cy="{y - 196}" rx="38" ry="9"/>', f'<path d="M{x - 26} {y - 204} C{x - 26} {y - 240} {x + 26} {y - 240} {x + 26} {y - 204} Z"/>',
              f'<rect x="{x - 5}" y="{y - 280}" width="10" height="46" rx="2"/>', f'<rect x="{x - 18}" y="{y - 266}" width="36" height="10" rx="2"/>']
    elif kind == "knight":
        g += [base(x, 92, y), f'<path d="M{x - 30} {y - 26} C{x - 32} {y - 70} {x - 6} {y - 92} {x - 14} {y - 120} L{x - 44} {y - 104} C{x - 56} {y - 112} {x - 52} {y - 128} {x - 40} {y - 140} C{x - 22} {y - 160} {x - 12} {y - 186} {x + 6} {y - 196} L{x + 10} {y - 212} L{x + 20} {y - 192} C{x + 44} {y - 176} {x + 52} {y - 120} {x + 32} {y - 26} Z"/>',
              f'<circle cx="{x - 8}" cy="{y - 158}" r="4" fill="{stroke}" stroke="none"/>']
    g.append("</g>")
    return "".join(g)


b.append(piece("rook", 120, 400, IVORY, IVORY_D))
b.append(piece("king", 248, 402, "url(#gold)", GOLD_D))
b.append(piece("knight", 372, 402, "#1c1b18", GOLD))
b.append(piece("pawn", 486, 400, "url(#gold)", GOLD_D))
write("art-chess.svg", svg(W, H, "".join(b), "Chess pieces — a rook, king, knight and pawn — standing on the edge of a board"))

# 4. Dominoes — a chain with a double laid crosswise (6:5)
W, H = 600, 500
PIPS = {0: [], 1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}


def domino(cx, cy, a, bb, horizontal=True, angle=0):
    L, S = 120, 60
    w, h = (L, S) if horizontal else (S, L)
    g = [f'<g transform="rotate({angle} {cx} {cy})" filter="url(#shadow)">',
         f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="9" fill="url(#ivory)" stroke="{IVORY_D}" stroke-width="1.5"/>']
    if horizontal:
        g.append(f'<line x1="{cx}" y1="{cy - h / 2 + 8}" x2="{cx}" y2="{cy + h / 2 - 8}" stroke="{GOLD_D}" stroke-width="2"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{GOLD}"/>')
        halves = [(cx - L / 4, cy, a), (cx + L / 4, cy, bb)]
    else:
        g.append(f'<line x1="{cx - w / 2 + 8}" y1="{cy}" x2="{cx + w / 2 - 8}" y2="{cy}" stroke="{GOLD_D}" stroke-width="2"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{GOLD}"/>')
        halves = [(cx, cy - L / 4, a), (cx, cy + L / 4, bb)]
    for hx, hy, v in halves:
        for px, py in PIPS[v]:
            g.append(f'<circle cx="{hx + px * 14}" cy="{hy + py * 14}" r="5.2" fill="{INK}"/>')
    g.append("</g>")
    return "".join(g)


b = [f'<rect width="{W}" height="{H}" fill="url(#felt)"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
     f'<ellipse cx="300" cy="250" rx="260" ry="200" fill="url(#glow)"/>']
# chain: 5|3 — 3|6 — [6|6 double crosswise] — 6|2 ; plus a branch 6|1 going down from the double
b.append(domino(110, 210, 5, 3))
b.append(domino(232, 210, 3, 6))
b.append(domino(323, 210, 6, 6, horizontal=False))
b.append(domino(414, 210, 6, 2))
b.append(domino(323, 334, 6, 1, horizontal=False))
# boneyard tiles face down
for x, y, ang in [(120, 380, -14), (190, 404, 8), (470, 360, 18), (520, 410, -6)]:
    b.append(f'<g transform="rotate({ang} {x} {y})" filter="url(#shadow)"><rect x="{x - 30}" y="{y - 60}" width="60" height="120" rx="9" fill="#1d1b17" stroke="{GOLD}" stroke-opacity=".6"/>'
             f'{suit("spade", x, y, 18, GOLD)}</g>')
write("art-dominoes.svg", svg(W, H, "".join(b), "A dominoes layout with the double six laid crosswise and face-down tiles in the boneyard"))

# 5. Spades — a hand of spades with a bid marker (6:5)
W, H = 600, 500
b = [f'<rect width="{W}" height="{H}" fill="url(#felt)"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
     f'<ellipse cx="300" cy="230" rx="260" ry="200" fill="url(#glow)"/>']
for (rank, a) in zip(["10", "J", "Q", "K", "A"], [-24, -12, 0, 12, 24]):
    b.append(card(300, 230, 136, 192, rank, "spade", angle=a, pivot=(300, 560), big=True))
# bid marker
b.append(f'<g filter="url(#shadow)"><circle cx="510" cy="420" r="50" fill="{INK}" stroke="url(#gold)" stroke-width="6"/>'
         f'<circle cx="510" cy="420" r="38" fill="none" stroke="{GOLD}" stroke-opacity=".6" stroke-dasharray="5 6"/>'
         f'<text x="510" y="414" font-family="{SERIF}" font-size="13" letter-spacing="3" fill="{GOLD_L}" text-anchor="middle">BID</text>'
         f'<text x="510" y="442" font-family="{SERIF}" font-weight="700" font-size="26" fill="{IVORY}" text-anchor="middle">4</text></g>')
b.append(chip_stack(130, 430, 4, GOLD, INK, rx=30, ry=10, step=6))
write("art-spades.svg", svg(W, H, "".join(b), "A fanned hand of spades from ten to ace beside a bid marker"))
