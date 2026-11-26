import sys, os, contextlib, io
sys.path.insert(0, '/home/claude/sito-carloalbertogioja/tools/promo')
with contextlib.redirect_stdout(io.StringIO()):
    import rubriche as R
from rubriche import *
OUT = '.'; os.makedirs(OUT, exist_ok=True)
N = 5
def base(i, kicker):
    im, d = R.campionato_base()
    d.text((L, 240), kicker, font=K(30), fill=MINT)
    footer(d, CREAM, MINT, 'calcioallday.it/risultati')
    n = f'{i}/{N}'; d.text((880 - d.textlength(n, font=K(26)), H - 88), n, font=K(26), fill=MINT)
    return im, d
def fit(d, t, maxw, s=60):
    while d.textlength(t, font=T(s)) > maxw: s -= 2
    return T(s)
def row(d, y, h, t, a, hgt=120, s0=60):
    d.rounded_rectangle([L, y, W - L, y + hgt], radius=16, fill=GREEN)
    mw = (W - 2 * L - 60 - 170) / 2
    s = min(fit(d, h, mw, s0).size, fit(d, a, mw, s0).size); f = T(s)
    d.text((L + 30, y + (hgt - s) / 2 - 4), h, font=f, fill=CREAM)
    d.text((W - L - 30 - d.textlength(a, font=f), y + (hgt - s) / 2 - 4), a, font=f, fill=CREAM)
    ts = 52
    d.text((540 - d.textlength(t, font=T(ts)) / 2, y + (hgt - ts) / 2 - 4), t, font=T(ts), fill=MINT)
def para(d, y, txt, size=40, col=CREAM):
    for ln in wrap(d, txt, B(size), W - 2 * L):
        d.text((L, y), ln, font=B(size), fill=col); y += int(size * 1.45)
    return y

# 1 apertura
im, d = base(1, '13ª GIORNATA · DA VENERDÌ 27 A LUNEDÌ 30 NOVEMBRE')
for i, ln in enumerate(['SI COMINCIA', 'DAL PENZO.']): d.text((L, 300 + i * 124), ln, font=T(132), fill=CREAM)
y = para(d, 610, 'Dieci partite in quattro giorni, da venerdì sera a lunedì sera.')
d.text((L, y + 40), 'APRE LA GIORNATA', font=K(26), fill=MINT)
row(d, y + 80, 'VENEZIA', 'VEN 20:45', 'BOLOGNA')
d.text((L, y + 250), 'IL POSTICIPO DI DOMENICA', font=K(26), fill=MINT)
row(d, y + 290, 'COMO', 'DOM 20:45', 'JUVENTUS')
im.save(f'{OUT}/programma-1.jpg', quality=92)

# 2 la vetta
im, d = base(2, 'LA CLASSIFICA PRIMA DELLA GIORNATA')
d.text((L, 300), 'QUATTRO IN', font=T(132), fill=CREAM); d.text((L, 424), 'CINQUE PUNTI.', font=T(132), fill=CREAM)
y = 610
for nm, p, m in (('LAZIO', 32, 'In trasferta contro il Torino'), ('ROMA', 30, 'In casa contro il Monza'), ('INTER', 29, 'In casa contro il Genoa'), ('MILAN', 27, 'In trasferta contro il Cagliari')):
    d.rounded_rectangle([L, y, W - L, y + 112], radius=16, fill=CREAM)
    d.text((L + 30, y + 14), nm, font=T(56), fill=NAVY)
    d.text((L + 30, y + 74), m, font=K(25), fill=GREEN)
    pt = f'{p} PUNTI'; d.text((W - L - 30 - d.textlength(pt, font=T(52)), y + 30), pt, font=T(52), fill=NAVY)
    y += 128
im.save(f'{OUT}/programma-2.jpg', quality=92)

def day(i, kicker, title, ms, extra=None):
    im, d = base(i, kicker)
    y = 300
    for ln in wrap(d, title, T(120), W - 2 * L): d.text((L, y), ln, font=T(120), fill=CREAM); y += 116
    y += 50
    hgt, step = (140, 164) if len(ms) <= 3 else (120, 140)
    for h, t, a in ms: row(d, y, h, t, a, hgt); y += step
    if extra: para(d, y + 20, extra, 38)
    return im
day(3, 'SABATO 28 NOVEMBRE', 'LA CAPOLISTA VA A TORINO.', [('FROSINONE', '15:00', 'PARMA'), ('TORINO', '18:00', 'LAZIO'), ('INTER', '20:45', 'GENOA')]).save(f'{OUT}/programma-3.jpg', quality=92)
day(4, 'DOMENICA 29 NOVEMBRE', 'DOMENICA, QUATTRO PARTITE.', [('UDINESE', '12:30', 'FIORENTINA'), ('SASSUOLO', '15:00', 'NAPOLI'), ('ROMA', '18:00', 'MONZA'), ('COMO', '20:45', 'JUVENTUS')]).save(f'{OUT}/programma-4.jpg', quality=92)
day(5, 'LUNEDÌ 30 NOVEMBRE', 'IL MILAN CHIUDE IN SARDEGNA.', [('LECCE', '18:30', 'ATALANTA'), ('CAGLIARI', '20:45', 'MILAN')], 'Risultati, calendario completo e classifica aggiornata partita dopo partita su calcioallday.it.').save(f'{OUT}/programma-5.jpg', quality=92)
print('ok')
