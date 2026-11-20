"""Turn dist/index.html into a self-contained, clearly labelled design preview.

Usage: python3 tools/make_preview.py <out_dir>

- assets are copied next to the page and referenced relatively
- links to other pages point at the current live site (inner pages are not redesigned yet)
- the Google Maps iframe is replaced by a static location card (preview hosts block iframes)
- forms run in preview mode (no submission) and a "Design preview" label is added
"""
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
LIVE = "https://pokerattheden.com"

out = sys.argv[1]
if os.path.isdir(out):
    shutil.rmtree(out)
os.makedirs(out)

html = open(os.path.join(DIST, "index.html"), encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

# Static map card instead of the iframe
for iframe in soup.select(".map iframe"):
    card = BeautifulSoup(
        '<div class="map-static"><div class="map-static__grid"></div>'
        '<span class="map-static__pin"><svg class="icon" aria-hidden="true"><use href="#i-pin"></use></svg></span></div>',
        "html.parser")
    iframe.replace_with(card)

# Internal links -> live site
for a in soup.find_all("a", href=True):
    h = a["href"]
    if h.startswith("/") and not h.startswith("//"):
        a["href"] = LIVE + h
        a["target"] = "_blank"
        a["rel"] = "noopener"

for s in soup.find_all("script", type="application/ld+json"):
    s.decompose()

head = soup.head
body = soup.body
keep_head = []
for el in head.find_all(recursive=False):
    if el.name == "title":
        keep_head.append(str(el))
    elif el.name == "link" and el.get("rel") and ("stylesheet" in el["rel"] or "preconnect" in el["rel"] or "preload" in el["rel"]):
        keep_head.append(str(el))

extra = """
<meta name="robots" content="noindex">
<style>
  .site-header { top: env(safe-area-inset-top, 0px); }
  .map-static { position: relative; width: 100%; height: 100%; min-height: 280px; overflow: hidden;
    background: radial-gradient(circle at 55% 45%, rgba(176,138,62,.18), transparent 40%), #f3f0e9; }
  .map-static__grid { position: absolute; inset: -20%; transform: rotate(-24deg);
    background-image: linear-gradient(rgba(18,18,18,.08) 2px, transparent 2px), linear-gradient(90deg, rgba(18,18,18,.05) 1px, transparent 1px);
    background-size: 120px 90px, 70px 70px; }
  .map-static__grid::after { content: ""; position: absolute; left: 0; right: 0; top: 48%; height: 10px; background: rgba(176,138,62,.35); }
  .map-static__pin { position: absolute; left: 58%; top: 42%; transform: translate(-50%, -100%); width: 46px; height: 46px; border-radius: 50%;
    display: grid; place-items: center; background: #c6a15b; color: #0b0b0b; box-shadow: 0 0 0 10px rgba(198,161,91,.18), 0 10px 30px rgba(0,0,0,.6); }
  .map-static__pin .icon { width: 22px; height: 22px; }
  .preview-pill { position: fixed; z-index: 150; left: 50%; transform: translateX(-50%);
    bottom: calc(16px + env(safe-area-inset-bottom, 0px)); display: flex; align-items: center; gap: .6rem;
    padding: .55rem 1rem; border-radius: 999px; background: rgba(11,11,11,.92); border: 1px solid rgba(198,161,91,.5);
    color: #f5f3ef; font: 600 .72rem/1.3 "Manrope", system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase;
    box-shadow: 0 10px 30px rgba(0,0,0,.6); flex-wrap: wrap; justify-content: center; max-width: calc(100% - 32px); }
  .preview-pill .pp-label { color: #a5a5a5; }
  .preview-pill button { font: inherit; letter-spacing: inherit; text-transform: inherit; color: #f5f3ef; background: transparent; border: 1px solid rgba(198,161,91,.45); border-radius: 999px; padding: .4rem .75rem; cursor: pointer; }
  .preview-pill button[aria-pressed="true"] { background: #c6a15b; color: #0b0b0b; border-color: #c6a15b; }
  .preview-pill button:focus-visible { outline: 2px solid #ecd193; outline-offset: 2px; }
  .preview-pill b { color: #c6a15b; font-weight: 700; }
  @media (max-width: 700px) { .preview-pill { bottom: calc(84px + env(safe-area-inset-bottom, 0px)); font-size: .6rem; gap: .4rem; padding: .5rem .7rem; border-radius: 16px; } .preview-pill .pp-label { display: none; } }
</style>
<script>window.DEN_PREVIEW = true;</script>
"""
pill = ('<div class="preview-pill" role="group" aria-label="Design preview: choose a hero option" data-hero-switch>'
        '<b>Design preview</b><span class="pp-label">Hero option</span>'
        '<button type="button" value="a" aria-pressed="true">A · Cards</button>'
        '<button type="button" value="b" aria-pressed="false">B · Arch</button>'
        '<button type="button" value="c" aria-pressed="false">C · Flop</button></div>')

body_html = body.decode_contents()
page = "\n".join(keep_head) + extra + body_html + pill
page = page.replace('"/assets/', '"assets/').replace(" /assets/", " assets/").replace(",/assets/", ",assets/")
page = page.replace('href="https://pokerattheden.com/assets/', 'href="assets/')
page = page.replace("<title>Home - The Den Poker Lounge</title>", "<title>The Den Redesign</title>", 1)
page = page.encode("ascii", "xmlcharrefreplace").decode("ascii")
with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(page)

# Copy every asset the page references
refs = set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:webp|png|jpg|svg|css|js)', page))
refs |= {"assets/img/spade.svg", "assets/img/check.svg"}
for r in sorted(refs):
    src = os.path.join(DIST, r)
    dst = os.path.join(out, r)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
print(len(refs), "assets copied")
for r in sorted(refs):
    print(r)
