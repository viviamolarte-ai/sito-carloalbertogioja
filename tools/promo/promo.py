"""Grafiche dell'ufficio promozione CalcioAllDay, generate dai dati del sito.

Uso: python3 promo.py <repo_sito> <giornata> <cartella_uscita>
  repo_sito = cartella sito/ del repo viviamolarte-ai/calcioallday

Produce:
  top11-1..5.jpg        carosello «Top 11 della giornata» (1080x1350)
  squadra-<slug>.jpg    una pagella per squadra (1080x1350), solo 3 voti
  tiktok-1..4.jpg       fotogrammi 1080x1920 «migliore e peggiore»
  tiktok.mp4            video di ~14 secondi dai fotogrammi
  dati.json             chi è stato scelto e perché (per i testi e i controlli)

Regole: solo dati del sito (pagelle e eventi già verificati), al massimo 3-4 voti
per grafica, nessuno stemma né foto, titoli fattuali con i nomi dei giocatori.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY = (20, 38, 56); MINT = (69, 213, 165); CREAM = (247, 242, 232); GREEN = (36, 75, 61); TERRA = (174, 81, 69)
F = lambda n, s: ImageFont.truetype(os.path.join(HERE, n), s)
T = lambda s: F('barlow-condensed-800.ttf', s)
B = lambda s: F('inter-400.ttf', s)
K = lambda s: F('inter-600.ttf', s)
L = 90

repo, rnd, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
os.makedirs(out, exist_ok=True)
sa = json.load(open(f'{repo}/src/data/real/serie-a.json'))
pag = json.load(open(f'{repo}/src/data/editorial/pagelle/giornata-{rnd}.json'))
ev_path = f'{repo}/scripts/eventi/input/giornata-{rnd}.json'
ev = {m['matchId']: m for m in json.load(open(ev_path))['matches']} if os.path.exists(ev_path) else {}
P = {p['id']: p for p in sa['players']}; TM = {t['id']: t for t in sa['teams']}; MT = {m['id']: m for m in sa['matches']}
NICE = {'Como 1907': 'Como', 'Venezia FC': 'Venezia'}
tname = lambda tid: NICE.get(TM[tid]['name'], TM[tid]['name'])
vfmt = lambda v: (f'{v:.1f}'.replace('.', ',')).replace(',0', '')
surname = lambda n: n if ' ' not in n else n.split(' ', 1)[1] if len(n.split()) == 2 else n.split()[-1]

PARTICLES = {'de', 'da', 'di', 'van', 'von', 'dos', 'del', 'della', 'dal', 'le', 'la', 'ter', 'den'}
def last(n):
    parts = n.split()
    if len(parts) == 1:
        return n
    if len(parts) == 2 and len(n) <= 10:
        return n
    out = [parts[-1]]
    i = len(parts) - 2
    while i > 0 and parts[i].lower() in PARTICLES:
        out.insert(0, parts[i]); i -= 1
    return ' '.join(out)
def key_sur(n):
    return n.split()[-1]

# ---------- dati: un record per calciatore votato ----------
rows = []
for m in pag['matches']:
    mm = MT[m['matchId']]; e = ev.get(m['matchId'], {})
    for side, tid, oid in (('home', mm['homeId'], mm['awayId']), ('away', mm['awayId'], mm['homeId'])):
        tag = 'H' if side == 'home' else 'A'
        for x in m[side]:
            if x['vote'] is None:
                continue
            sur = key_sur(x['name'])
            mine = lambda k: [g for g in e.get('goals', []) if g['team'] == tag and g['name'] and sur.lower() in g['name'].lower()]
            goals = [g for g in mine(0) if not g.get('og')]
            ogs = [g for g in e.get('goals', []) if g.get('og') and g['team'] == tag and sur.lower() in (g['name'] or '').lower()]
            assists = [g for g in e.get('goals', []) if g['team'] == tag and g.get('assist') not in (None, 'none') and sur.lower() in str(g.get('assist')).lower()]
            reds = [r for r in e.get('red', []) if r.get('team') == tag and sur.lower() in r.get('name', '').lower()]
            rows.append(dict(
                name=x['name'], short=last(x['name']), vote=x['vote'], bench=x['bench'],
                role=P.get(x.get('playerId'), {}).get('role'), team=tname(tid), teamId=tid, opp=tname(oid),
                home=side == 'home', match=mm, goals=len(goals), pens=sum(1 for g in goals if g.get('pen')),
                assists=len(assists), og=len(ogs), red=len(reds)))

def score_line(r):
    mm = r['match']; s = mm['score']
    return f"{tname(mm['homeId'])}–{tname(mm['awayId'])} {s['home']}-{s['away']}"

FEM = {'Lazio', 'Roma', 'Juventus', 'Fiorentina', 'Cremonese', 'Salernitana', 'Sampdoria', 'Reggiana', 'Spal'}
VOW = {'Inter', 'Atalanta', 'Udinese', 'Empoli', 'Hellas Verona'}
def contro(team):
    if team in VOW: return f"contro l'{team}"
    return f"contro la {team}" if team in FEM else f"contro il {team}"

def fact(r, short=False):
    bits = []
    if r['goals']:
        g = r['goals']; p = r['pens']
        bits.append({1: 'un gol', 2: 'doppietta', 3: 'tripletta', 4: 'quattro gol', 5: 'cinque gol'}.get(g, f'{g} gol') + (f' ({p} su rigore)' if p else ''))
    if r['assists']:
        bits.append('un assist' if r['assists'] == 1 else f"{r['assists']} assist")
    if r['og']:
        bits.append('un autogol')
    if r['red']:
        bits.append('un\'espulsione')
    if r['bench']:
        bits.append('entrato dalla panchina')
    head = (bits[0][0].upper() + bits[0][1:] + (', ' + ', '.join(bits[1:]) if len(bits) > 1 else '')) if bits else 'Il voto più alto della sua squadra'
    return f"{head} {contro(r['opp'])}." if short else f"{head} in {score_line(r)}."

best_key = lambda r: (-r['vote'], -(r['goals'] - r['pens']), -r['goals'], -r['assists'], r['bench'], r['name'])

# ---------- Top 11: modulo con la somma di voti più alta ----------
def pick(role, n, used):
    c = sorted([r for r in rows if r['role'] == role and r['name'] not in used], key=best_key)
    return c[:n]
best = None
for mod in ((3, 4, 3), (4, 3, 3), (3, 5, 2), (4, 4, 2), (4, 2, 3)):
    used = set(); xi = {'P': pick('P', 1, used)}
    for role, n in zip('DCA', mod):
        xi[role] = pick(role, n, used)
    if any(len(xi[k]) < n for k, n in zip('PDCA', (1,) + mod)):
        continue
    tot = sum(r['vote'] for v in xi.values() for r in v)
    if best is None or tot > best[0] + 1e-9:
        best = (tot, mod, xi)
_, MOD, XI = best
xi_all = [r for k in 'PDCA' for r in XI[k]]
stars = sorted(xi_all, key=best_key)[:3]

# migliore e peggiore (a parità di voto il peggiore è chi ha un autogol o un'espulsione)
top1 = sorted(rows, key=best_key)[0]
worst = sorted(rows, key=lambda r: (r['vote'], -(r['og'] + r['red']), r['bench'], r['name']))[0]
worst_ties = sum(1 for r in rows if r['vote'] == worst['vote']) - 1

# ---------- disegno ----------
LOGO_C = Image.open(os.path.join(HERE, 'logo-cream.png'))

def canvas(h=1350, n=None, total=None, url='calcioallday.it/pagelle'):
    im = Image.new('RGB', (1080, h), NAVY); d = ImageDraw.Draw(im, 'RGBA')
    # barre del logo in basso a destra (stesso segno delle copertine del sito)
    k = 0.32
    for x, w, col in ((930, 8, (69, 213, 165, 90)), (968, 34, (69, 213, 165, 235)), (1016, 34, (247, 242, 232, 215))):
        y0 = h - 520
        d.polygon([(x, h), (x + w, h), (x + w + k * 520, y0), (x + k * 520, y0)], fill=col)
    lg = LOGO_C.resize((300, int(300 * LOGO_C.height / LOGO_C.width)), Image.LANCZOS)
    im.paste(lg, (L, 92), lg)
    d.line([(L, h - 112), (860, h - 112)], fill=(69, 213, 165, 90), width=2)
    d.rectangle([L, h - 113, L + 60, h - 110], fill=MINT)
    d.text((L, h - 90), url, font=K(28), fill=CREAM)
    if n:
        s = f'{n}/{total}'; d.text((840 - d.textlength(s, font=K(26)), h - 88), s, font=K(26), fill=MINT)
    return im, d

def wrap(d, text, font, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

def title(d, kicker, lines, y=210, size=124, step=116, maxw=900):
    d.text((L, y), kicker, font=K(30), fill=MINT); y += 56
    for ln in lines:
        f = T(size)
        while d.textlength(ln, font=f) > maxw and f.size > 60:
            f = T(f.size - 4)
        d.text((L, y), ln, font=f, fill=CREAM); y += step
    return y

ORD = f'{rnd}ª'

# Top 11 – copertina con il campo
im, d = canvas(n=1, total=5)
y = title(d, f'SERIE A · {ORD} GIORNATA', ['LA TOP 11', 'CALCIOALLDAY'], size=112, step=102)
top, bot = y + 26, 1180
d.rounded_rectangle([L, top, 990, bot], radius=22, fill=GREEN)
lc = (247, 242, 232, 60)
d.rounded_rectangle([L + 24, top + 24, 966, bot - 24], radius=10, outline=lc, width=3)
mid = (top + bot) // 2
d.line([(L + 24, mid), (966, mid)], fill=lc, width=3); d.ellipse([540 - 70, mid - 70, 540 + 70, mid + 70], outline=lc, width=3)
d.rectangle([540 - 150, bot - 24 - 90, 540 + 150, bot - 24], outline=lc, width=3)
lines = [XI['A'], XI['C'], XI['D'], XI['P']]
ys = [top + 70 + i * (bot - top - 140) / 3 for i in range(4)]
for row, yy in zip(lines, ys):
    n = len(row)
    for i, r in enumerate(sorted(row, key=lambda r: r['name'])):
        cx = L + 24 + (i + 0.5) * (966 - L - 24) / n
        nm = r['short'].upper(); f = T(46)
        while d.textlength(nm, font=f) > (876 / n) - 10 and f.size > 28: f = T(f.size - 2)
        w = d.textlength(nm, font=f); d.text((cx - w / 2, yy - 30), nm, font=f, fill=CREAM)
        tm = r['team'].upper(); w = d.textlength(tm, font=K(20)); d.text((cx - w / 2, yy + 22), tm, font=K(20), fill=MINT)
im.save(f'{out}/top11-1.jpg', quality=92)

def score_card(d, r, y):
    mm = r['match']; sc = mm['score']
    txt = f"{tname(mm['homeId']).upper()}  {sc['home']}–{sc['away']}  {tname(mm['awayId']).upper()}"
    f = T(64)
    while d.textlength(txt, font=f) > 860: f = T(f.size - 2)
    d.rounded_rectangle([L, y, 990, y + 100], radius=16, fill=GREEN)
    d.text((540 - d.textlength(txt, font=f) / 2, y + 12 + (64 - f.size) / 2), txt, font=f, fill=CREAM)

for i, r in enumerate(stars):
    im, d = canvas(n=i + 2, total=5)
    y = title(d, f"{r['team'].upper()} · TOP 11 {ORD} GIORNATA", [r['name'].upper()], size=120)
    d.text((L - 12, y - 10), vfmt(r['vote']), font=T(560), fill=MINT)
    yy = y + 600
    for ln in wrap(d, fact(r, short=True), B(42), 860):
        d.text((L, yy), ln, font=B(42), fill=CREAM); yy += 58
    score_card(d, r, 1070)
    im.save(f'{out}/top11-{i + 2}.jpg', quality=92)

im, d = canvas(n=5, total=5)
y = title(d, f'PAGELLE {ORD} GIORNATA', ['TUTTE LE PAGELLE', 'SU CALCIOALLDAY.IT'], size=112, step=104)
d.text((L, y + 24), 'Voti di tutti i calciatori, partita per partita:', font=B(38), fill=CREAM)
y += 100
ms = sorted({r['match']['id']: r['match'] for r in rows}.values(), key=lambda m: m['kickoff'])
for m in ms:
    sc = m['score']; hh, aa = tname(m['homeId']).upper(), tname(m['awayId']).upper()
    d.text((L, y), hh, font=T(46), fill=CREAM)
    mid = f"{sc['home']}–{sc['away']}"; d.text((470 - d.textlength(mid, font=T(46)) / 2, y), mid, font=T(46), fill=MINT)
    d.text((560, y), aa, font=T(46), fill=CREAM)
    y += 58
im.save(f'{out}/top11-5.jpg', quality=92)

# Pagella per squadra (3 voti)
cards = []
for tid in sorted({r['teamId'] for r in rows}, key=lambda t: TM[t]['slug']):
    tr = sorted([r for r in rows if r['teamId'] == tid], key=best_key)[:3]
    mm = tr[0]['match']; s = mm['score']
    im, d = canvas(url=f"calcioallday.it/pagelle")
    y = title(d, f'PAGELLE · {ORD} GIORNATA', [tname(tid).upper()], size=150, step=140) + 40
    h, a = tname(mm['homeId']).upper(), tname(mm['awayId']).upper()
    sc = f"{h}  {s['home']}–{s['away']}  {a}"
    f = T(64)
    while d.textlength(sc, font=f) > 900: f = T(f.size - 2)
    d.rounded_rectangle([L, y + 10, 990, y + 110], radius=16, fill=GREEN)
    d.text((540 - d.textlength(sc, font=f) / 2, y + 22), sc, font=f, fill=CREAM)
    y += 170
    d.text((L, y), 'I MIGLIORI SECONDO CALCIOALLDAY', font=K(28), fill=MINT); y += 60
    for r in tr:
        d.line([(L, y), (990, y)], fill=(247, 242, 232, 50), width=2)
        nm = r['name'].upper(); f = T(66)
        while d.textlength(nm, font=f) > 690: f = T(f.size - 2)
        d.text((L, y + 26), nm, font=f, fill=CREAM)
        v = vfmt(r['vote']); d.text((990 - d.textlength(v, font=T(96)), y + 6), v, font=T(96), fill=MINT)
        y += 128
    d.line([(L, y), (990, y)], fill=(247, 242, 232, 50), width=2)
    for ln in wrap(d, f"Tutti i voti di {tname(tid)} e delle altre 19 squadre sul sito.", B(38), 800):
        d.text((L, y + 34), ln, font=B(38), fill=CREAM); y += 52
    slug = TM[tid]['slug']
    im.save(f'{out}/squadra-{slug}.jpg', quality=92)
    cards.append(dict(team=tname(tid), slug=slug, anchor=f"pagelle-{TM[mm['homeId']]['slug']}-{TM[mm['awayId']]['slug']}",
                      votes=[(r['name'], r['vote']) for r in tr]))

# TikTok: migliore e peggiore
fr = []
im, d = canvas(h=1920, url='calcioallday.it/pagelle')
yy = title(d, f'SERIE A · {ORD} GIORNATA · VOTI CALCIOALLDAY', ['MIGLIORE', 'E PEGGIORE', 'DELLA GIORNATA'], y=520, size=170, step=160)
d.text((L, yy + 40), f"{last(top1['name']).upper()} E {last(worst['name']).upper()}", font=T(96), fill=MINT)
fr.append(im)
for lab, r, col in (('IL MIGLIORE', top1, MINT), ('IL PEGGIORE', worst, TERRA)):
    im, d = canvas(h=1920, url='calcioallday.it/pagelle')
    y = title(d, f"{lab} · {r['team'].upper()}", [r['name'].upper()], y=420, size=150)
    d.text((L - 10, y + 20), vfmt(r['vote']), font=T(560), fill=col)
    yy = y + 640
    tx = fact(r, True) if r is top1 else (fact(r, True) if (r['og'] or r['red']) else f"Il voto più basso {contro(r['opp'])}.")
    if r is worst and worst_ties:
        tx += f" Stesso voto per altri {worst_ties}." if worst_ties > 1 else ' Stesso voto per un altro calciatore.'
    for ln in wrap(d, tx, B(48), 860):
        d.text((L, yy), ln, font=B(48), fill=CREAM); yy += 66
    score_card(d, r, yy + 40)
    fr.append(im)
im, d = canvas(h=1920, url='calcioallday.it/pagelle')
yy = title(d, 'PAGELLE CALCIOALLDAY', ['LA PAGELLA', 'COMPLETA', 'È SUL SITO'], y=520, size=170, step=160)
d.text((L, yy + 40), 'calcioallday.it/pagelle', font=T(96), fill=MINT)
d.text((L, yy + 170), 'I voti di tutti i calciatori, partita per partita.', font=B(46), fill=CREAM)
fr.append(im)
for i, im in enumerate(fr):
    im.save(f'{out}/tiktok-{i + 1}.jpg', quality=92)
durs = [2.8, 4.2, 4.2, 3.2]
inputs = sum([['-loop', '1', '-t', str(t), '-i', f'{out}/tiktok-{i + 1}.jpg'] for i, t in enumerate(durs)], [])
fl, prev, off = [], '0:v', 0.0
for i in range(1, 4):
    off += durs[i - 1] - 0.4
    fl.append(f'[{prev}][{i}:v]xfade=transition=slideleft:duration=0.4:offset={off:.2f}[v{i}]'); prev = f'v{i}'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fl), '-map', f'[{prev}]',
                '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{out}/tiktok.mp4'], check=True)

json.dump(dict(round=rnd, module='-'.join(map(str, MOD)),
               top11=[dict(name=r['name'], team=r['team'], role=r['role'], vote=r['vote']) for r in xi_all],
               stars=[dict(name=r['name'], team=r['team'], vote=r['vote'], fact=fact(r)) for r in stars],
               best=dict(name=top1['name'], team=top1['team'], vote=top1['vote'], fact=fact(top1)),
               worst=dict(name=worst['name'], team=worst['team'], vote=worst['vote'], ties=worst_ties, fact=fact(worst)),
               cards=cards), open(f'{out}/dati.json', 'w'), ensure_ascii=False, indent=1)
print('ok', out)
