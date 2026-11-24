"""Stili delle rubriche CalcioAllDay (bozza da approvare).
Ogni rubrica ha fondo, segno grafico ed etichetta propri:
  campionato  navy, menta, barre del logo (lo stile attuale)
  fantacalcio verde stadio, schede color crema, griglia da «listone»
  articolo    crema, titoli in Source Serif, filetti da giornale
  coppe       terracotta, fascia a righe da sciarpa
Uso: python3 rubriche.py  -> mock/rubrica-*.jpg e mock/rubriche.jpg
"""
import os
from PIL import Image, ImageDraw, ImageFont
H0 = os.path.dirname(os.path.abspath(__file__))
F = lambda n, s: ImageFont.truetype(os.path.join(H0, n), s)
T = lambda s: F('barlow-condensed-800.ttf', s)
B = lambda s: F('inter-400.ttf', s)
K = lambda s: F('inter-600.ttf', s)
S = lambda s: F('serif-700.ttf', s)
NAVY = (20, 38, 56); MINT = (69, 213, 165); CREAM = (247, 242, 232); GREEN = (36, 75, 61); TERRA = (174, 81, 69); INK = (23, 33, 43); GREY = (89, 103, 117)
W, H, L = 1080, 1350, 90
LOGO = {'cream': Image.open(os.path.join(H0, 'logo-cream.png')), 'navy': Image.open(os.path.join(H0, 'logo-navy.png'))}
os.makedirs('mock', exist_ok=True)

def wrap(d, text, font, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

def logo(im, which, x=L, y=92, w=280):
    lg = LOGO[which]; lg = lg.resize((w, int(w * lg.height / lg.width)), Image.LANCZOS); im.paste(lg, (x, y), lg)

def tag(d, text, x, y, bg, fg):
    f = K(26); w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 36, y + 50], radius=25, fill=bg); d.text((x + 18, y + 9), text, font=f, fill=fg)

def footer(d, ink, accent, url='calcioallday.it', n=None):
    d.line([(L, H - 112), (W - L, H - 112)], fill=ink + (70,), width=2)
    d.rectangle([L, H - 113, L + 60, H - 110], fill=accent)
    d.text((L, H - 90), url, font=K(28), fill=ink)
    if n: d.text((W - L - d.textlength(n, font=K(26)), H - 88), n, font=K(26), fill=accent)

# ---------- CAMPIONATO (attuale) ----------
def campionato_base():
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im, 'RGBA'); k = .32
    c = (247, 242, 232, 28)
    d.rectangle([-40, 150, W + 40, H + 40], outline=c, width=3)
    d.line([(-40, 760), (W + 40, 760)], fill=c, width=3)
    d.ellipse([540 - 190, 760 - 190, 540 + 190, 760 + 190], outline=c, width=3)
    d.ellipse([540 - 7, 760 - 7, 540 + 7, 760 + 7], fill=c)
    d.rectangle([540 - 330, H - 230, 540 + 330, H + 40], outline=c, width=3)
    d.arc([540 - 190, H - 230 - 120, 540 + 190, H - 230 + 120], 180, 360, fill=c, width=3)
    for x, w, col in ((930, 8, (69, 213, 165, 90)), (968, 34, (69, 213, 165, 235)), (1016, 34, (247, 242, 232, 215))):
        d.polygon([(x, H), (x + w, H), (x + w + k * 520, H - 520), (x + k * 520, H - 520)], fill=col)
    logo(im, 'cream'); tag(d, 'SERIE A', W - L - 150, 96, MINT, NAVY)
    return im, d
im, d = campionato_base()
d.text((L, 240), '13ª GIORNATA · VENERDÌ 27 NOVEMBRE', font=K(30), fill=MINT)
for i, ln in enumerate(['SI RIPARTE', 'DA VENEZIA.']): d.text((L, 300 + i * 124), ln, font=T(132), fill=CREAM)
y = 600
for h, t, a in (('VENEZIA', '20:45', 'BOLOGNA'), ('COMO', 'DOM 20:45', 'JUVENTUS'), ('ROMA', 'DOM', 'MONZA')):
    d.rounded_rectangle([L, y, W - L, y + 120], radius=16, fill=GREEN)
    d.text((L + 30, y + 30), h, font=T(60), fill=CREAM); d.text((W - L - 30 - d.textlength(a, font=T(60)), y + 30), a, font=T(60), fill=CREAM)
    d.text((540 - d.textlength(t, font=T(52)) / 2, y + 34), t, font=T(52), fill=MINT); y += 140
footer(d, CREAM, MINT, 'calcioallday.it', '1/5'); im.save('mock/rubrica-campionato.jpg', quality=92)

# ---------- FANTACALCIO ----------
def fanta_base():
    im = Image.new('RGB', (W, H), GREEN); d = ImageDraw.Draw(im, 'RGBA')
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(247, 242, 232, 14), width=1)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(247, 242, 232, 14), width=1)
    d.rectangle([0, 0, 22, H], fill=MINT)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for txt, x, y, sz in (('+3', 700, 150, 420), ('+1', 40, 930, 300), ('+3', 760, 1000, 260)):
        ld.text((x, y), txt, font=T(sz), fill=(0, 0, 0, 0), stroke_width=3, stroke_fill=(247, 242, 232, 40))
    im.paste(lay, (0, 0), lay); d = ImageDraw.Draw(im, 'RGBA')
    logo(im, 'cream'); tag(d, 'FANTACALCIO', W - L - 232, 96, MINT, NAVY)
    return im, d
im, d = fanta_base()
d.text((L, 240), 'BONUS DELLA 12ª GIORNATA · DIFESA', font=K(30), fill=MINT)
for i, ln in enumerate(['I DIFENSORI', 'CHE HANNO', 'PORTATO BONUS']): d.text((L, 300 + i * 112), ln, font=T(120), fill=CREAM)
y = 680
for nm, sq, b in (('JACOBO RAMÓN', 'Como', 'GOL'), ('JUAN CABAL', 'Juventus', 'GOL'), ('YAN COUTO', 'Como', '2 ASSIST')):
    d.rounded_rectangle([L, y, W - L, y + 128], radius=18, fill=CREAM)
    d.text((L + 30, y + 18), nm, font=T(58), fill=NAVY); d.text((L + 30, y + 84), sq, font=K(26), fill=GREEN)
    d.rounded_rectangle([W - L - 220, y + 30, W - L - 30, y + 98], radius=34, fill=NAVY)
    d.text((W - L - 125 - d.textlength(b, font=T(44)) / 2, y + 38), b, font=T(44), fill=MINT); y += 148
footer(d, CREAM, MINT, 'calcioallday.it/fantacalcio', '1/4'); im.save('mock/rubrica-fantacalcio.jpg', quality=92)

# ---------- ARTICOLO ----------
def art_texture(d, y0, y1):
    import random; rnd = random.Random(7)
    if y1 - y0 < 80: return
    for x0, x1 in [(L, 330), (380, 640), (670, 990)]:
        y = y0
        while y < y1:
            ln = x1 - x0 if rnd.random() > .15 else int((x1 - x0) * rnd.uniform(.4, .8))
            d.rectangle([x0, y, x0 + ln, y + 7], fill=(23, 33, 43, 14)); y += 22
            if rnd.random() < .07: y += 26
    for x in (355, 655): d.line([(x, y0), (x, y1)], fill=(23, 33, 43, 18), width=2)

def art_base():
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im, 'RGBA')
    # retino tipografico in basso a destra, che sfuma verso il centro
    for gy in range(0, 22):
        for gx in range(0, 22):
            x, y = W - 30 - gx * 24, H - 140 - gy * 24
            r = max(0, 9 - (gx + gy) * 0.32)
            if r > .6: d.ellipse([x - r, y - r, x + r, y + r], fill=(174, 81, 69, 40))
    logo(im, 'navy'); tag(d, "L'ARTICOLO", W - L - 190, 96, NAVY, CREAM)
    d.line([(L, 196), (W - L, 196)], fill=INK, width=4); d.line([(L, 206), (W - L, 206)], fill=INK, width=1)
    return im, d
im, d = art_base()
d.text((L, 236), 'CRONACA · MARTEDÌ 24 NOVEMBRE', font=K(28), fill=TERRA)
y = 300
for ln in wrap(d, 'Doppio Varela, il Monza esce dalla zona rossa: Fiorentina ko 3-0', S(92), W - 2 * L):
    d.text((L, y), ln, font=S(92), fill=INK); y += 104
y += 30
d.line([(L, y), (L + 120, y)], fill=TERRA, width=6); y += 40
for ln in wrap(d, 'Rigore e colpo di tacco di Varela, poi Robinson: il Monza interrompe una serie di quattro sconfitte, aggancia il Lecce e inguaia la Fiorentina.', B(40), W - 2 * L):
    d.text((L, y), ln, font=B(40), fill=GREY); y += 58
art_texture(d, y + 40, H - 300)
d.rounded_rectangle([L, H - 260, L + 480, H - 170], radius=12, fill=NAVY)
d.text((L + 34, H - 244), 'LEGGI TUTTO SUL SITO', font=T(50), fill=CREAM)
footer(d, INK, TERRA, 'calcioallday.it/news', '1/3'); im.save('mock/rubrica-articolo.jpg', quality=92)

# ---------- COPPE ----------
def coppe_base():
    im = Image.new('RGB', (W, H), TERRA)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    import math
    for ox, oy, base in ((W + 60, -60, 200), (-60, -60, 340)):
        for i in range(7):
            a = math.radians(base + i * 6); b = math.radians(base + i * 6 + 2.2)
            Lr = 2600
            ld.polygon([(ox, oy), (ox + Lr * math.cos(a), oy - Lr * math.sin(a)), (ox + Lr * math.cos(b), oy - Lr * math.sin(b))], fill=(247, 242, 232, 22))
    for r in (40, 70):
        ld.ellipse([W - 60 - r, -60 - r, W - 60 + r, -60 + r], fill=(247, 242, 232, 30))
    im.paste(lay, (0, 0), lay); d = ImageDraw.Draw(im, 'RGBA')
    y0 = H - 130
    for i, col in enumerate([NAVY, CREAM, NAVY, CREAM, NAVY]):
        d.rectangle([0, y0 - 150 + i * 30, W, y0 - 150 + (i + 1) * 30], fill=col)
    d.rectangle([0, y0, W, H], fill=TERRA)
    logo(im, 'cream'); tag(d, 'CHAMPIONS LEAGUE', W - L - 300, 96, NAVY, CREAM)
    return im, d
im, d = coppe_base()
d.text((L, 240), '5ª GIORNATA · MARTEDÌ 24 NOVEMBRE', font=K(30), fill=NAVY)
for i, ln in enumerate(['STASERA', 'IN EUROPA.']): d.text((L, 300 + i * 124), ln, font=T(132), fill=CREAM)
y = 600
for h, t, a in (('REAL MADRID', '21:00', 'PSV'), ('MAN CITY', '21:00', 'NAPOLI'), ('ARSENAL', '21:00', 'DORTMUND'), ('COMO', '21:00', 'AEK')):
    d.rounded_rectangle([L, y, W - L, y + 104], radius=14, fill=NAVY)
    d.text((L + 30, y + 24), h, font=T(54), fill=CREAM); d.text((W - L - 30 - d.textlength(a, font=T(54)), y + 24), a, font=T(54), fill=CREAM)
    d.text((540 - d.textlength(t, font=T(50)) / 2, y + 26), t, font=T(50), fill=MINT); y += 108
d.text((L, H - 90), 'calcioallday.it/champions-league', font=K(28), fill=CREAM)
im.save('mock/rubrica-coppe.jpg', quality=92)

# foglio riassuntivo
names = ['campionato', 'fantacalcio', 'articolo', 'coppe']
s = Image.new('RGB', (4 * 380 + 50, 520), (235, 235, 235)); dd = ImageDraw.Draw(s)
for i, n in enumerate(names):
    s.paste(Image.open(f'mock/rubrica-{n}.jpg').resize((360, 450)), (10 + i * 380, 50))
    dd.text((10 + i * 380, 12), n.upper(), font=K(24), fill=INK)
s.save('mock/rubriche.jpg', quality=90)
print('ok')
