"""Genera fuochi d'artificio realistici (PNG trasparenti) per il tema capodanno."""
import numpy as np, math, random, sys
from PIL import Image, ImageFilter

def burst(size, seed, cols, n=150, light=False):
    rnd = random.Random(seed)
    S = size
    acc = np.zeros((S, S, 3), np.float32)
    cx = cy = S / 2
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        sp = rnd.uniform(.55, 1.0) * S * .40
        col = np.array(rnd.choice(cols), np.float32) / 255
        steps = 70
        for i in range(steps):
            t = i / steps
            r = sp * (1 - (1 - t) ** 2.2)
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r + (t ** 2) * S * .10   # gravita
            inten = (t ** 1.5) * (1 - t) ** .6 * 2.2         # scia che si accende verso la punta
            xi, yi = int(x), int(y)
            if 1 <= xi < S - 1 and 1 <= yi < S - 1:
                acc[yi, xi] += col * inten
                acc[yi, xi + 1] += col * inten * .4
        # scintilla finale
        x = cx + math.cos(a) * sp; y = cy + math.sin(a) * sp + S * .10
        xi, yi = int(x), int(y)
        if 2 <= xi < S - 2 and 2 <= yi < S - 2:
            acc[yi - 1:yi + 2, xi - 1:xi + 2] += col * 1.6
    # bagliore centrale tenue
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot(xx - cx, yy - cy) / (S * .5)
    glow = np.clip(1 - d, 0, 1) ** 3 * .10
    acc += glow[..., None] * np.array(cols[0], np.float32) / 255
    sharp = acc
    img = Image.fromarray(np.clip(sharp * 255, 0, 255).astype(np.uint8))
    blur = np.asarray(img.filter(ImageFilter.GaussianBlur(S / 120)), np.float32) / 255
    blur2 = np.asarray(img.filter(ImageFilter.GaussianBlur(S / 40)), np.float32) / 255
    tot = sharp + blur * 1.8 + blur2 * 2.5
    a = np.clip(tot.max(axis=2) * (1.6 if light else 1.3), 0, 1)
    rgb = np.where(a[..., None] > 0, tot / np.maximum(tot.max(axis=2, keepdims=True), 1e-4), 0)
    if light:
        rgb = rgb * .62
    out = np.dstack([np.clip(rgb, 0, 1), a])
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")

if __name__ == "__main__":
    out = sys.argv[1]
    gold = [(232, 200, 140), (214, 178, 110), (250, 228, 180)]
    rose = [(240, 200, 220), (226, 170, 200)]
    # per fondo prugna (chiari) e per fondo avorio (piu scuri)
    burst(700, 1, gold + gold + rose).save(out + "/fw_big_dark.png")
    burst(400, 2, rose + gold).save(out + "/fw_small_dark.png")
    goldD = [(176, 136, 70), (160, 120, 60), (196, 156, 90)]
    roseD = [(150, 80, 120), (120, 60, 100)]
    burst(700, 1, goldD + goldD + roseD, light=True).save(out + "/fw_big_light.png")
    burst(400, 2, roseD + goldD, light=True).save(out + "/fw_small_light.png")
