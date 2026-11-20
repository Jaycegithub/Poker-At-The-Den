#!/usr/bin/env python3
"""
The Den Poker Lounge — static site build.

Renders Jinja2 templates in src/templates into dist/, reproducing the live
WordPress permalink structure exactly (e.g. /about-us/ -> dist/about-us/index.html).

    python3 build.py            # build into ./dist
    python3 build.py --serve    # build, then serve dist/ on http://localhost:8000

Requires: Python 3.9+, Jinja2.
"""
import http.server
import math
import json
import os
import re
import shutil
import socketserver
import sys
from datetime import date

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from markupsafe import Markup

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
SITE_URL = "https://pokerattheden.com"

# ---------------------------------------------------------------------------
# Business information — copied verbatim from the live site.
# ---------------------------------------------------------------------------
SITE = {
    "name": "The Den Poker Lounge",
    "url": SITE_URL,
    "phone": "+1 (214) 501-4909",
    "phone_href": "tel:+12145014909",
    "email": "jamiekempf@ymail.com",
    "hours": "Open 7 Days a Week",
    # Home page wording; the Contact page uses "6230 Dalrock Rd., Rowlett TX 75088" (see docs/AUDIT.md).
    "address_home": "6320 Dalrock Rd, Suite 100 Rowlett, TX",
    "address_contact": "6230 Dalrock Rd., Rowlett TX 75088",
    # Map query uses the address published by the Rowlett Area Chamber (matches the home page).
    "map_query": "6320 Dalrock Rd Suite 100, Rowlett, TX 75088",
    "instagram": "https://www.instagram.com/thedenpokerlounge",
    "facebook": "https://www.facebook.com/TheDenPokerLounge",
    "year": "2026",
}

# ---------------------------------------------------------------------------
# Navigation — identical labels, order, nesting and destinations to the live
# "Primary" menu. `None` = the live item is "#" (no destination yet).
# ---------------------------------------------------------------------------
NAV = [
    {"label": "Home", "href": "/"},
    {"label": "The Club", "children": [
        {"label": "About The Den", "href": "/about-us/"},
        {"label": "Our Team", "href": "/our-team/"},
        {"label": "Club Values", "href": "/club-values-atmosphere/"},
    ]},
    {"label": "Games", "children": [
        {"label": "Poker", "href": "/poker/", "children": [{"label": "Play Poker Cash", "href": "/play-poker-cash/"}]},
        {"label": "Chess", "href": "/chess/", "children": [{"label": "Play Chess", "href": "/play-chess/"}]},
        {"label": "Dominoes", "href": "/dominoes/", "children": [{"label": "Play Dominoes", "href": "/play-dominoes/"}]},
        {"label": "Spades", "href": "/spades/", "children": [{"label": "Play Spades", "href": "/play-spades/"}]},
    ]},
    {"label": "Poker", "children": [
        {"label": "Tournaments", "href": "/tournaments/", "children": [{"label": "ICM Calculator", "href": "/icm-calculator/"}]},
        {"label": "PokerAtlas", "href": None},
    ]},
    {"label": "Explore Rowlett", "href": "/explore-rowlett/", "children": [
        {"label": "Places To Eat", "href": "/places-to-eat/"},
        {"label": "Places To Stay", "href": "/places-to-stay/"},
        {"label": "Rowlett Community", "href": "/rowlett-community/"},
    ]},
    {"label": "Membership", "href": "/membership/", "children": [
        {"label": "Membership Options", "href": "/membership/"},
        {"label": "Why Join", "href": "/why-join/"},
        {"label": "Founders Membership Apply", "href": "/founders-membership-apply/"},
        {"label": "Join Now", "href": "/join-now/"},
    ]},
    {"label": "Resources", "children": [
        {"label": "FAQs", "href": "/faqs/"},
        {"label": "Club Rules", "href": "/house-rules-etiquette/"},
        {"label": "Contact Us", "href": "/contact-us/"},
        {"label": "Community Events", "href": "/community-events/"},
        {"label": "Networking", "href": "/networking/"},
        {"label": "Private Gatherings", "href": "/private-gatherings/"},
    ]},
]

# ---------------------------------------------------------------------------
# Pages: URL path -> template, breadcrumb section.
# ---------------------------------------------------------------------------
PAGES = {
    "/": ("home.html", None),
    "/about-us/": ("about-us.html", "The Club"),
    "/our-team/": ("our-team.html", "The Club"),
    "/club-values-atmosphere/": ("club-values-atmosphere.html", "The Club"),
    "/poker/": ("poker.html", "Games"),
    "/play-poker-cash/": ("play-poker-cash.html", "Games"),
    "/chess/": ("chess.html", "Games"),
    "/play-chess/": ("play-chess.html", "Games"),
    "/dominoes/": ("dominoes.html", "Games"),
    "/play-dominoes/": ("play-dominoes.html", "Games"),
    "/spades/": ("spades.html", "Games"),
    "/play-spades/": ("play-spades.html", "Games"),
    "/tournaments/": ("tournaments.html", "Poker"),
    "/icm-calculator/": ("icm-calculator.html", "Poker"),
    "/explore-rowlett/": ("explore-rowlett.html", "Explore Rowlett"),
    "/places-to-eat/": ("places-to-eat.html", "Explore Rowlett"),
    "/places-to-stay/": ("places-to-stay.html", "Explore Rowlett"),
    "/rowlett-community/": ("rowlett-community.html", "Explore Rowlett"),
    "/membership/": ("membership.html", "Membership"),
    "/why-join/": ("why-join.html", "Membership"),
    "/founders-membership-apply/": ("founders-membership-apply.html", "Membership"),
    "/join-now/": ("join-now.html", "Membership"),
    "/faqs/": ("faqs.html", "Resources"),
    "/house-rules-etiquette/": ("house-rules-etiquette.html", "Resources"),
    "/contact-us/": ("contact-us.html", "Resources"),
    "/community-events/": ("community-events.html", "Resources"),
    "/networking/": ("networking.html", "Resources"),
    "/private-gatherings/": ("private-gatherings.html", "Resources"),
    "/resources/": ("resources.html", None),
    "/behind-the-felt-a-day-in-the-life-of-an-ace-high-dealer/": ("post-behind-the-felt.html", None),
    "/what-to-expect-at-your-first-tournament/": ("post-first-tournament.html", None),
    "/mastering-the-mind-game-poker-psychology-101/": ("post-poker-psychology.html", None),
}

IMG_DIR = os.path.join(SRC, "assets", "img")

# Nine seats around an oval poker table (dealer position at the top is left open).
SEATS = [(round(50 + 50 * math.cos(math.radians(-54 + 36 * i)), 2),
          round(50 + 50 * math.sin(math.radians(-54 + 36 * i)), 2)) for i in range(9)]


def _widths(name):
    pat = re.compile(re.escape(name) + r"-(\d+)\.webp$")
    return sorted(int(m.group(1)) for f in os.listdir(IMG_DIR) if (m := pat.match(f)))


def img(name, alt="", sizes="100vw", cls="", eager=False, width=None, height=None):
    """Responsive <img> with srcset built from the generated derivatives."""
    ws = _widths(name)
    if not ws:
        raise SystemExit(f"Missing image derivatives for {name}")
    srcset = ", ".join(f"/assets/img/{name}-{w}.webp {w}w" for w in ws)
    default = next((w for w in ws if w >= 960), ws[-1])
    from PIL import Image  # dimensions for CLS-free layout
    with Image.open(os.path.join(IMG_DIR, f"{name}-{ws[-1]}.webp")) as im:
        w, h = im.size
    attrs = [
        f'src="/assets/img/{name}-{default}.webp"', f'srcset="{srcset}"', f'sizes="{sizes}"',
        f'width="{width or w}"', f'height="{height or h}"', f'alt="{Markup.escape(alt)}"',
        'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"', 'decoding="async"',
    ]
    if cls:
        attrs.append(f'class="{cls}"')
    return Markup("<img " + " ".join(attrs) + ">")


def art(name, alt="", cls="", eager=False):
    """An original SVG illustration from assets/img/art/."""
    path = os.path.join(IMG_DIR, "art", name + ".svg")
    head = open(path, encoding="utf-8").read(400)
    w, h = re.search(r'viewBox="0 0 (\d+) (\d+)"', head).groups()
    return Markup(f'<img src="/assets/img/art/{name}.svg" width="{w}" height="{h}" alt="{Markup.escape(alt)}"'
                  + (' loading="eager"' if eager else ' loading="lazy"') + ' decoding="async"' + (f' class="{cls}"' if cls else "") + ">")


def mascot():
    """Path of Ali, the club's bear mascot, once the original artwork is added
    as src/assets/img/ali.webp or ali.png (transparent background); else None."""
    for ext in ("webp", "png"):
        if os.path.exists(os.path.join(IMG_DIR, "ali." + ext)):
            return "/assets/img/ali." + ext
    return None


def icon(name, cls=""):
    fill = name.startswith("suit-")
    c = "icon" + (" icon--fill" if fill else "") + (f" {cls}" if cls else "")
    return Markup(f'<svg class="{c}" aria-hidden="true" focusable="false"><use href="#i-{name}"></use></svg>')


def widget(name):
    with open(os.path.join(SRC, "widgets", name + ".html"), encoding="utf-8") as fh:
        return Markup(fh.read())


def build():
    seo = json.load(open(os.path.join(SRC, "data", "seo.json"), encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(os.path.join(SRC, "templates")),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    env.globals.update(site=SITE, nav=NAV, seats=SEATS, img=img, art=art, mascot=mascot(), icon=icon, widget=widget, site_url=SITE_URL,
                       build_date=date.today().isoformat())

    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(DIST, "assets"))

    for path, (tpl, section) in PAGES.items():
        meta = seo[path]
        try:
            template = env.get_template("pages/" + tpl)
        except TemplateNotFound:
            print(f"  SKIP {path} (missing template {tpl})")
            continue
        html = template.render(
            path=path, section=section, meta=meta, canonical=SITE_URL + path,
        )
        out = os.path.join(DIST, path.strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  built {path}")

    # 404 + robots + sitemap
    if os.path.exists(os.path.join(SRC, "templates", "pages", "404.html")):
      with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(env.get_template("pages/404.html").render(
            path="/404/", section=None, canonical=SITE_URL + "/",
            meta={"title": "Page Not Found - The Den Poker Lounge", "description": "", "robots": "noindex, follow", "og_type": "website"}))
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for path in PAGES:
            lm = (seo[path].get("modified") or "")[:10]
            fh.write(f"  <url><loc>{SITE_URL}{path}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>\n")
        fh.write("</urlset>\n")
    with open(os.path.join(DIST, "robots.txt"), "w") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {DIST}")


def serve(port=8000):
    os.chdir(DIST)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    with socketserver.TCPServer(("", port), H) as httpd:
        print(f"Serving http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
