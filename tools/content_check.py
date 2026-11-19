"""Verify every text string from the live page appears in the rebuilt page.
Usage: python3 tools/content_check.py <live.html> <built.html>
Compares the live page's main Elementor content + footer (case/quote/whitespace-insensitive)."""
import re, sys
from bs4 import BeautifulSoup

def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", t).strip().lower()

live = BeautifulSoup(open(sys.argv[1], encoding="utf-8").read(), "html.parser")
built = BeautifulSoup(open(sys.argv[2], encoding="utf-8").read(), "html.parser")
for t in built(["script", "style", "svg"]): t.decompose()
built_text = norm(built.get_text(" "))
regions = [e for e in live.find_all(attrs={"data-elementor-type": True}) if e["data-elementor-type"] in ("wp-page", "wp-post", "footer")]
missing, total = [], 0
for region in regions:
    for t in region(["script", "style", "svg", "form"]): t.decompose()
    for s in region.stripped_strings:
        n = norm(s)
        if len(n) < 2: continue
        total += 1
        if n not in built_text:
            missing.append(s)
print(f"{total - len(missing)}/{total} live text strings found")
for s in missing: print("  MISSING:", s)
