import sys, os, contextlib, io
sys.path.insert(0, '/home/claude/sito-carloalbertogioja/tools/promo')
with contextlib.redirect_stdout(io.StringIO()):
    import rubriche as R
from rubriche import *
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
N = 4
def base(i, kicker):
    im, d = R.coppe_base()
    d.text((L, 240), kicker, font=K(30), fill=NAVY)
    d.text((W - L - d.textlength(f'{i}/{N}', font=K(26)), H - 88), f'{i}/{N}', font=K(26), fill=NAVY)
    d.text((L, H - 90), 'calcioallday.it/champions-league', font=K(28), fill=CREAM)
    return im, d
def fit(d, t, maxw, s=54):
    while d.textlength(t, font=T(s)) > maxw: s -= 2
    return T(s)
def row(d, y, h, t, a, hgt=104):
    d.rounded_rectangle([L, y, W - L, y + hgt], radius=14, fill=NAVY)
    mw = (W - 2 * L - 60 - 170) / 2
    fh, fa = fit(d, h, mw), fit(d, a, mw); s = min(fh.size, fa.size); f = T(s)
    d.text((L + 30, y + (hgt - s) / 2 - 4), h, font=f, fill=CREAM)
    d.text((W - L - 30 - d.textlength(a, font=f), y + (hgt - s) / 2 - 4), a, font=f, fill=CREAM)
    d.text((540 - d.textlength(t, font=T(50)) / 2, y + (hgt - 50) / 2 - 4), t, font=T(50), fill=MINT)
KD = '5ª GIORNATA · MERCOLEDÌ 25 NOVEMBRE'
# 1 copertina
im, d = base(1, KD)
for i, ln in enumerate(['INTER IN CASA,', 'ROMA A PARIGI.']): d.text((L, 300 + i * 124), ln, font=T(132), fill=CREAM)
y = 600
for ln in wrap(d, 'Nove partite nella seconda serata della quinta giornata: due alle 18:45, sette alle 21:00.', B(40), W - 2 * L):
    d.text((L, y), ln, font=B(40), fill=CREAM); y += 58
y += 40
row(d, y, 'INTER', '21:00', 'STOCCARDA'); row(d, y + 120, 'PSG', '21:00', 'ROMA')
im.save(f'{OUT}/cl-1.jpg', quality=92)
# 2 le italiane, punti
im, d = base(2, 'LE ITALIANE · ORE 21:00 · PUNTI DOPO 4 GIORNATE')
d.text((L, 300), 'DUE SFIDE PESANTI.', font=T(120), fill=CREAM)
def card(y, a, pa, b, pb, note):
    d.rounded_rectangle([L, y, W - L, y + 270], radius=18, fill=CREAM)
    for x0, nm, p, al in ((L + 40, a, pa, 'l'), (W - L - 40, b, pb, 'r')):
        f = T(70); w = d.textlength(nm, font=f); xx = x0 if al == 'l' else x0 - w
        d.text((xx, y + 28), nm, font=f, fill=NAVY)
        pt = f'{p} PUNTI'; w2 = d.textlength(pt, font=T(46)); xx = x0 if al == 'l' else x0 - w2
        d.text((xx, y + 108), pt, font=T(46), fill=TERRA)
    d.text((540 - d.textlength('–', font=T(60)) / 2, y + 36), '–', font=T(60), fill=GREY)
    d.line([(L + 40, y + 176), (W - L - 40, y + 176)], fill=(23, 33, 43, 50), width=2)
    yy = y + 192
    for ln in wrap(d, note, K(27), W - 2 * L - 80): d.text((L + 40, yy), ln, font=K(27), fill=INK); yy += 36
card(460, 'INTER', 6, 'STOCCARDA', 7, "L'Inter arriva da due vittorie di fila, dopo i ko con Real Madrid e Bruges.")
card(760, 'PSG', 12, 'ROMA', 4, 'Il PSG ha vinto tutte e quattro le partite. La Roma arriva dal ko di Manchester.')
im.save(f'{OUT}/cl-2.jpg', quality=92)
# 3 programma 1
def prog(i, title, groups):
    im, d = base(i, KD)
    d.text((L, 300), title, font=T(120), fill=CREAM)
    y = 470
    for ora, ms in groups:
        for h, a in ms: row(d, y, h, ora, a, 100); y += 114
    return im, d
im, d = prog(3, 'IL PROGRAMMA.', [('18:45', [('SABAH', 'BARCELLONA'), ('SLAVIA PRAGA', 'VILLARREAL')]), ('21:00', [('ATLÉTICO MADRID', 'VIKING'), ('BRUGES', 'LIVERPOOL')])])
im.save(f'{OUT}/cl-3.jpg', quality=92)
im, d = prog(4, 'GLI ALTRI INCROCI.', [('21:00', [('LILLA', 'BAYERN'), ('SPORTING', 'MAN UNITED'), ('SHAKHTAR', 'FENERBAHÇE')])])
y = 470 + 3 * 114 + 40
for ln in wrap(d, 'Risultati e nuova classifica della fase campionato sul sito.', B(38), W - 2 * L):
    d.text((L, y), ln, font=B(38), fill=CREAM); y += 54
im.save(f'{OUT}/cl-4.jpg', quality=92)
