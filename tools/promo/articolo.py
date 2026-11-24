"""Post «L'articolo» (rubrica articoli) dall'articolo del giorno del sito.
Uso: python3 articolo.py <repo_sito> <slug|latest> <cartella_uscita>
Produce articolo-1..3.jpg (1080x1350) e post.json con i testi per rete.
Grafica: fondo crema, titoli Source Serif, doppio filetto da testata, retino
terracotta in basso a destra. Testi presi solo dall'articolo pubblicato.
"""
import json, os, random, sys, datetime
from PIL import Image, ImageDraw, ImageFont
H0 = os.path.dirname(os.path.abspath(__file__))
F = lambda n, s: ImageFont.truetype(os.path.join(H0, n), s)
T = lambda s: F('barlow-condensed-800.ttf', s)
B = lambda s: F('inter-400.ttf', s)
K = lambda s: F('inter-600.ttf', s)
S = lambda s: F('serif-700.ttf', s)
NAVY = (20, 38, 56); CREAM = (247, 242, 232); TERRA = (174, 81, 69); INK = (23, 33, 43); GREY = (89, 103, 117)
W, H, L = 1080, 1350, 90
MESI = 'gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'.split()
GIORNI = 'lunedì martedì mercoledì giovedì venerdì sabato domenica'.split()

repo, slug, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
src = open(f'{repo}/src/data/editorial/launchArticles.ts').read()
arts = json.loads(src[src.index('= [') + 2: src.rindex(']') + 1])
art = max(arts, key=lambda a: a['publishedAt']) if slug == 'latest' else next(a for a in arts if a['slug'] == slug)
dt = datetime.datetime.fromisoformat(art['publishedAt'])
when = f"{GIORNI[dt.weekday()]} {dt.day} {MESI[dt.month - 1]}".upper()
heads = [b['text'] for b in art['body'] if b['type'] == 'h2'][:4]
LOGO = Image.open(os.path.join(H0, 'logo-navy.png'))

def wrap(d, text, font, maxw):
    res, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: res.append(cur); cur = w
    return res + [cur]

def base(n, tot=3):
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im, 'RGBA')
    for gy in range(22):
        for gx in range(22):
            x, y = W - 30 - gx * 24, H - 140 - gy * 24
            r = max(0, 9 - (gx + gy) * 0.32)
            if r > .6: d.ellipse([x - r, y - r, x + r, y + r], fill=(174, 81, 69, 40))
    lg = LOGO.resize((280, int(280 * LOGO.height / LOGO.width)), Image.LANCZOS); im.paste(lg, (L, 92), lg)
    f = K(26); t = "L'ARTICOLO"; tw = d.textlength(t, font=f)
    d.rounded_rectangle([W - L - tw - 36, 96, W - L, 146], radius=25, fill=NAVY); d.text((W - L - tw - 18, 105), t, font=f, fill=CREAM)
    d.line([(L, 196), (W - L, 196)], fill=INK, width=4); d.line([(L, 206), (W - L, 206)], fill=INK, width=1)
    d.line([(L, H - 112), (W - L, H - 112)], fill=INK + (70,), width=2); d.rectangle([L, H - 113, L + 60, H - 110], fill=TERRA)
    d.text((L, H - 90), 'calcioallday.it/news', font=K(28), fill=INK)
    s = f'{n}/{tot}'; d.text((W - L - d.textlength(s, font=K(26)), H - 88), s, font=K(26), fill=TERRA)
    return im, d

def texture(d, y0, y1):
    rnd = random.Random(7)
    if y1 - y0 < 80: return
    for x0, x1 in [(L, 330), (380, 640), (670, 990)]:
        y = y0
        while y < y1:
            ln = x1 - x0 if rnd.random() > .15 else int((x1 - x0) * rnd.uniform(.4, .8))
            d.rectangle([x0, y, x0 + ln, y + 7], fill=(23, 33, 43, 14)); y += 22
            if rnd.random() < .07: y += 26
    for x in (355, 655): d.line([(x, y0), (x, y1)], fill=(23, 33, 43, 18), width=2)

def button(d, text):
    f = T(50); w = d.textlength(text, font=f)
    d.rounded_rectangle([L, H - 260, L + w + 68, H - 170], radius=12, fill=NAVY); d.text((L + 34, H - 244), text, font=f, fill=CREAM)

# 1 copertina
im, d = base(1)
d.text((L, 236), f"{art['category'].upper()} · {when}", font=K(28), fill=TERRA)
size = 92
while True:
    lines = wrap(d, art['title'], S(size), W - 2 * L)
    if len(lines) <= 5 or size <= 64: break
    size -= 4
y = 300
for ln in lines: d.text((L, y), ln, font=S(size), fill=INK); y += int(size * 1.13)
y += 30; d.line([(L, y), (L + 120, y)], fill=TERRA, width=6); y += 40
for ln in wrap(d, art['summary'], B(40), W - 2 * L): d.text((L, y), ln, font=B(40), fill=GREY); y += 58
texture(d, y + 40, H - 300); button(d, 'LEGGI TUTTO SUL SITO')
im.save(f'{out}/articolo-1.jpg', quality=92)

# 2 i capitoli dell'articolo
im, d = base(2)
d.text((L, 236), "NELL'ARTICOLO", font=K(28), fill=TERRA)
y = 300
for i, h in enumerate(heads):
    d.text((L, y - 6), str(i + 1), font=S(110), fill=TERRA)
    yy = y
    for ln in wrap(d, h, S(56), W - 2 * L - 110): d.text((L + 110, yy), ln, font=S(56), fill=INK); yy += 66
    y = max(y + 130, yy + 40)
    if i < len(heads) - 1: d.line([(L, y - 24), (W - L, y - 24)], fill=(23, 33, 43, 40), width=2)
texture(d, y + 20, H - 300); button(d, 'CONTINUA SUL SITO')
im.save(f'{out}/articolo-2.jpg', quality=92)

# 3 invito
im, d = base(3)
d.text((L, 236), 'OGNI MATTINA ALLE 7', font=K(28), fill=TERRA)
y = 300
for ln in ['Un articolo', 'nuovo ogni giorno', 'su calcioallday.it']:
    d.text((L, y), ln, font=S(96), fill=INK); y += 112
y += 30; d.line([(L, y), (L + 120, y)], fill=TERRA, width=6); y += 40
for ln in wrap(d, "Risultati, pagelle, classifiche e l'articolo di oggi, tutto sul sito. Iscriviti alla newsletter del venerdì per non perderne uno.", B(40), W - 2 * L):
    d.text((L, y), ln, font=B(40), fill=GREY); y += 58
texture(d, y + 40, H - 300); button(d, 'CALCIOALLDAY.IT')
im.save(f'{out}/articolo-3.jpg', quality=92)

import re
first = next(b['text'] for b in art['body'] if b['type'] == 'p')
sents = re.split(r'(?<=[.!?])\s+', first); lead = ''
for x in sents:
    if len(lead) + len(x) > 230 and lead: break
    lead = (lead + ' ' + x).strip()
utm = lambda src, med: f"https://www.calcioallday.it/news/{art['slug']}?utm_source={src}&utm_medium={med}&utm_campaign=articolo-{dt:%Y%m%d}"
tags = '#SerieA #CalcioAllDay'
json.dump(dict(
    slug=art['slug'], title=art['title'],
    tiktok=dict(title=art['title'][:90], text=f"{lead} Articolo completo su calcioallday.it {tags}"),
    instagram=f"{art['title']}\n\n{lead}\n\nL'articolo completo su calcioallday.it (link in bio).\n\n{tags}",
    facebook=f"{art['title']}\n\n{lead}\n\nLeggi l'articolo: {utm('facebook', 'post')}\n\n{tags}",
    links=dict(facebook=utm('facebook', 'post'))), open(f'{out}/post.json', 'w'), ensure_ascii=False, indent=1)
print('ok', art['slug'])
