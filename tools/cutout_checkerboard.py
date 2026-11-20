import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, out, preview = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.int16)
mx, mn = a.max(axis=2), a.min(axis=2)
cand = ((mx - mn) <= 6) & (mn >= 214)
lab, n = ndimage.label(cand, structure=np.ones((3, 3)))
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
# enclosed regions that show the two-tone checker pattern are background too
v = mn
for i in range(1, n + 1):
    if i in border:
        continue
    m = lab == i
    cnt = m.sum()
    if cnt < 60:
        continue
    if cnt > 3000:
        bg |= m
        continue
    vals = v[m]
    dark = ((vals >= 224) & (vals <= 233)).mean()
    lite = (vals >= 250).mean()
    if dark > .2 and lite > .2 and dark + lite > .85:
        bg |= m
fg = ~bg
# drop tiny specks
lab2, n2 = ndimage.label(fg)
sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
keep = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s > 2000])
alpha = Image.fromarray((keep * 255).astype(np.uint8))
alpha = alpha.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
rgba = im.copy(); rgba.putalpha(alpha)
rgba = rgba.crop(alpha.getbbox())
rgba.save(out)
for name, col in (("dark", (12, 12, 12, 255)), ("white", (255, 255, 255, 255))):
    b = Image.new("RGBA", rgba.size, col); b.alpha_composite(rgba)
    b.convert("RGB").resize((rgba.width // 2, rgba.height // 2)).save(preview.replace(".jpg", f"-{name}.jpg"), quality=85)
print(rgba.size, "bg frac", bg.mean())
