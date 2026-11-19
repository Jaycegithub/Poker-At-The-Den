"""Builds responsive image derivatives from the original site uploads.
Usage: python3 tools_images.py <originals_dir> <out_dir>
"""
import os, sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
WIDTHS = [480, 960, 1600]
SKIP = {"The-Den-Poker-Lounge-3-2.webp"}  # byte-identical duplicate of 3-1

for f in sorted(os.listdir(src)):
    if not f.endswith(".webp") or f in SKIP or "Logo" in f:
        continue
    im = Image.open(os.path.join(src, f)).convert("RGB")
    base = f[:-5]
    for w in [x for x in WIDTHS if x < im.width] + [min(im.width, WIDTHS[-1])]:
        r = im if w >= im.width else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(out, f"{base}-{w}.webp"), "WEBP", quality=78, method=6)

# Logo: original (dark lettering, for light backgrounds) + light variant for dark backgrounds.
logo = Image.open(os.path.join(src, "The-Den-Poker-Lounge-Logo.webp")).convert("RGBA")
px = logo.load()
light = logo.copy(); lp = light.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = px[x, y]
        if a and max(r, g, b) - min(r, g, b) < 40 and max(r, g, b) < 120:
            lp[x, y] = (245, 243, 239, a)  # warm white #F5F3EF
for img, name in ((logo, "logo-dark"), (light, "logo-light")):
    for w in (360, 720):
        img.resize((w, round(img.height * w / img.width)), Image.LANCZOS).save(
            os.path.join(out, f"{name}-{w}.webp"), "WEBP", quality=90, method=6)
# Social share image
og = Image.open(os.path.join(src, "The-Den-Poker-Lounge-Image-8.webp")).convert("RGB")
og.resize((1200, round(og.height * 1200 / og.width))).save(os.path.join(out, "og-default.jpg"), quality=82)
