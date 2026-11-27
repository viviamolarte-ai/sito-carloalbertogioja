import sys, os, contextlib, io
sys.path.insert(0, '/home/claude/sito-carloalbertogioja/tools/promo')
_cwd = os.getcwd(); os.chdir('/tmp')
with contextlib.redirect_stdout(io.StringIO()):
    import rubriche as R
os.chdir(_cwd)
from rubriche import *
N = 4
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
    d.text((540 - d.textlength(t, font=T(52)) / 2, y + (hgt - 52) / 2 - 4), t, font=T(52), fill=MINT)
def para(d, y, txt, size=40, col=CREAM):
    for ln in wrap(d, txt, B(size), W - 2 * L):
        d.text((L, y), ln, font=B(size), fill=col); y += int(size * 1.45)
    return y
def title(d, txt, y=300, s=120):
    for ln in wrap(d, txt, T(s), W - 2 * L): d.text((L, y), ln, font=T(s), fill=CREAM); y += int(s * .97)
    return y
def stat(d, y, big, small):
    d.rounded_rectangle([L, y, W - L, y + 132], radius=16, fill=CREAM)
    d.text((L + 30, y + 24), big, font=fit(d, big, 250, 80), fill=NAVY)
    x = L + 300
    ls = wrap(d, small, K(28), W - L - 30 - x)
    yy = y + 66 - len(ls) * 19
    for ln in ls: d.text((x, yy), ln, font=K(28), fill=GREEN); yy += 38
    return y + 154

# 1 apertura
im, d = base(1, 'SERIE A · SABATO 28 NOVEMBRE')
y = title(d, 'LAZIO E INTER IN CAMPO NELLO STESSO GIORNO.', s=100)
y = para(d, y + 40, 'Tre partite della 13ª giornata, dal primo pomeriggio alla sera.')
y += 55
for h, t, a in (('FROSINONE', '15:00', 'PARMA'), ('TORINO', '18:00', 'LAZIO'), ('INTER', '20:45', 'GENOA')):
    row(d, y, h, t, a, 132); y += 154
im.save('anteprima-1.jpg', quality=92)

def match(i, ora, stadio, h, a, tit, stats, chiusa=None):
    im, d = base(i, f'ORE {ora} · {stadio}')
    row(d, 300, h, 'OGGI', a, 128)
    y = title(d, tit, 490, 88)
    y += 45
    for b, s in stats: y = stat(d, y, b, s)
    if chiusa: para(d, y + 6, chiusa, 34)
    return im
match(2, '15:00', 'STADIO BENITO STIRPE', 'FROSINONE', 'PARMA',
      'ALLO STIRPE IL FROSINONE HA PERSO UNA VOLTA SOLA.',
      [('5 SU 6', 'Le vittorie del Frosinone in casa in questo campionato'),
       ('4 KO', 'Il Parma in cinque trasferte: quattro sconfitte e una vittoria'),
       ('8 GOL', 'Antonio Raimondo, il capocannoniere del Frosinone')]).save('anteprima-2.jpg', quality=92)
match(3, '18:00', 'STADIO OLIMPICO DI TORINO', 'TORINO', 'LAZIO',
      'LA LAZIO DI GATTUSO NON HA ANCORA PERSO.',
      [('10 V · 2 N', 'Il campionato della capolista: 32 punti in 12 giornate'),
       ('1 SU 5', 'Le vittorie del Torino nelle ultime cinque giornate'),
       ('6 + 4', 'Gol e assist di Tijjani Noslin in campionato')]).save('anteprima-3.jpg', quality=92)
match(4, '20:45', 'STADIO GIUSEPPE MEAZZA', 'INTER', 'GENOA',
      'A SAN SIRO L’INTER HA SEMPRE VINTO.',
      [('6 SU 6', 'Le vittorie dell’Inter in casa: nessun’altra squadra ha fatto percorso netto'),
       ('4 SU 5', 'Le vittorie del Genoa di De Rossi nelle ultime cinque'),
       ('6 GOL', 'Milutin Osmajić, il miglior marcatore del Genoa')],
      'Risultati e classifica aggiornati sul sito.').save('anteprima-4.jpg', quality=92)
print('ok')
