"""Download the licensed stock photos used on the homepage (Pexels License: free for
commercial use, no attribution required) and build responsive WebP sizes.
Usage: python3 tools/stock_images.py <download_dir>
"""
import os, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "assets", "img")
DL = sys.argv[1]
os.makedirs(DL, exist_ok=True)

# name -> Pexels photo id
PHOTOS = {
    "stock-poker-hands": 1871508,      # hands, chips and cards at a poker table
    "stock-laughing-table": 7594399,   # two guests laughing at a gaming table
    "stock-chips-white": 7047194,      # chips and cards on a white surface
    "stock-lounge": 9890442,           # lounge interior with sofa and bar
    "stock-friends-cards": 8111370,    # friends playing cards around a table
    "stock-lounge-chair": 7195527,     # leather lounge chair
    "stock-chips-cards": 30090695,     # chip and cards on grey
    "stock-chess": 5234266,            # chess from above, hands moving pieces
    "stock-dominoes": 38977726,        # wooden dominoes on a table
    "stock-spades": 1679602,           # chips beside the jack of spades
    "stock-watch-party": 23495482,     # friends cheering at a game on TV
    "stock-social-table": 6962264,     # friends talking around a card table
    "stock-poker-night": 6963320,      # friends playing poker at a wooden table
    "stock-business": 4428041,         # colleagues talking over wine
}
WIDTHS = [480, 960, 1600]

for name, pid in PHOTOS.items():
    src = os.path.join(DL, f"{pid}.jpg")
    if not os.path.exists(src):
        url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=2000"
        subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0", "-o", src, url], check=True)
    im = Image.open(src).convert("RGB")
    for w in [x for x in WIDTHS if x < im.width] + [min(im.width, WIDTHS[-1])]:
        r = im if w >= im.width else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-{w}.webp"), "WEBP", quality=80, method=6)
    print(name, pid, im.size)
