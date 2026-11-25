import sys, os, contextlib, io
sys.path.insert(0, '/home/claude/sito-carloalbertogioja/tools/promo')
with contextlib.redirect_stdout(io.StringIO()):
    import rubriche as R
from rubriche import *
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
N = 5
def base(i, kicker):
    _tag = R.tag
    def eltag(d, text, x, y, bg, fg):
        t = 'EUROPA LEAGUE'; _tag(d, t, W - L - d.textlength(t, font=K(26)) - 36, y, bg, fg)
    R.tag = eltag
    try: im, d = R.coppe_base()
    finally: R.tag = _tag
    d.text((L, 240), kicker, font=K(30), fill=NAVY)
    d.text((W - L - d.textlength(f'{i}/{N}', font=K(26)), H - 88), f'{i}/{N}', font=K(26), fill=NAVY)
    d.text((L, H - 90), 'calcioallday.it/europa-league', font=K(28), fill=CREAM)
    return im, d
def fit(d, t, maxw, s=54):
    while d.textlength(t, font=T(s)) > maxw: s -= 2
    return T(s)
def row(d, y, h, t, a, hgt=104, s0=54):
    d.rounded_rectangle([L, y, W - L, y + hgt], radius=14, fill=NAVY)
    mw = (W - 2 * L - 60 - 170) / 2
    fh, fa = fit(d, h, mw, s0), fit(d, a, mw, s0); s = min(fh.size, fa.size); f = T(s)
    d.text((L + 30, y + (hgt - s) / 2 - 4), h, font=f, fill=CREAM)
    d.text((W - L - 30 - d.textlength(a, font=f), y + (hgt - s) / 2 - 4), a, font=f, fill=CREAM)
    ts = min(50, s0 - 4)
    d.text((540 - d.textlength(t, font=T(ts)) / 2, y + (hgt - ts) / 2 - 4), t, font=T(ts), fill=MINT)
KD = '5ª GIORNATA · GIOVEDÌ 26 NOVEMBRE'
im, d = base(1, KD)
for i, ln in enumerate(['MILAN AL PIREO,', 'JUVE IN CASA.']): d.text((L, 300 + i * 124), ln, font=T(132), fill=CREAM)
y = 600
for ln in wrap(d, 'Diciotto partite nella quinta giornata della fase campionato: otto alle 18:45, dieci alle 21:00.', B(40), W - 2 * L):
    d.text((L, y), ln, font=B(40), fill=CREAM); y += 58
y += 40
row(d, y, 'OLYMPIAKOS', '18:45', 'MILAN'); row(d, y + 120, 'JUVENTUS', '21:00', 'OMONIA')
im.save(f'{OUT}/el-1.jpg', quality=92)
im, d = base(2, 'LE ITALIANE · PUNTI DOPO 4 GIORNATE')
d.text((L, 300), 'MOMENTI OPPOSTI.', font=T(120), fill=CREAM)
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
card(460, 'OLYMPIAKOS', 10, 'MILAN', 3, "Il Milan è 29°, fuori dalle prime 24: ha vinto solo a Salisburgo. L'Olympiakos non ha mai perso.")
card(760, 'JUVENTUS', 10, 'OMONIA', 6, 'La Juventus è imbattuta: tre vittorie e il 2-2 con il Rennes.')
im.save(f'{OUT}/el-2.jpg', quality=92)
def prog(i, title, groups, hgt=86, step=98, y=470):
    im, d = base(i, KD)
    d.text((L, 300), title, font=T(120), fill=CREAM)
    for ora, ms in groups:
        for h, a in ms: row(d, y, h, ora, a, hgt, 48); y += step
    return im, d, y
im, d, _ = prog(3, 'ALLE 18:45.', [('18:45', [('SALISBURGO', 'ARARAT-ARMENIA'), ('UNION SG', 'LECH POZNAN'), ('PLZEN', 'BENFICA'), ('MARSIGLIA', 'LEVSKI SOFIA'), ('DINAMO ZAGABRIA', 'LEVERKUSEN'), ('CELTA VIGO', 'BOURNEMOUTH'), ('BEŞIKTAŞ', 'HAPOEL BEER SHEVA')])], hgt=72, step=82, y=462)
im.save(f'{OUT}/el-3.jpg', quality=92)
im, d, _ = prog(4, 'ALLE 21:00.', [('21:00', [('TORREENSE', 'CELTIC'), ('SUNDERLAND', 'JAGIELLONIA'), ('SPARTA PRAGA', 'AZ ALKMAAR'), ('OFI CRETA', 'ANDERLECHT'), ('NEC NIMEGA', 'RENNES')])])
im.save(f'{OUT}/el-4.jpg', quality=92)
im, d, y = prog(5, 'GLI ALTRI INCROCI.', [('21:00', [('LIONE', 'LILLESTRØM'), ('HOFFENHEIM', 'STURM GRAZ'), ('FERENCVÁROS', 'CELJE'), ('CRYSTAL PALACE', 'REAL SOCIEDAD')])])
y += 30
for ln in wrap(d, 'Risultati e classifica della fase campionato sul sito, partita per partita.', B(38), W - 2 * L):
    d.text((L, y), ln, font=B(38), fill=CREAM); y += 54
im.save(f'{OUT}/el-5.jpg', quality=92)
