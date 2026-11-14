"""Genera le grafiche dei post AllYouCanWedding (1080x1350 JPEG) da una specifica JSON.

Uso:  python3 tools/render.py spec.json OUT_DIR
Spec: {"post": "p04", "slides": [ {...}, ... ]}

Tipi di slide (tutti i campi testo sono facoltativi tranne "title"):
  cover    foto a tutto schermo + eyebrow + title          campi: image, eyebrow, title
  photo    foto in alto, testo sotto su avorio             campi: image, focus ("center", "top", "50% 30%"...), img_height (px, default 690), eyebrow, title, text
  text     fondo prugna, solo testo                        campi: eyebrow, title, text
  list     fondo avorio, elenco puntato numerato           campi: eyebrow, title, items[]
  question fondo prugna, domanda grande e opzioni          campi: eyebrow, title, options[]
  cta      fondo avorio, chiusura con contatto             campi: eyebrow, title, text, cta, contact

Arricchimenti (facoltativi, non cambiano le slide esistenti):
  "deco": true (sulla spec o sulla singola slide) aggiunge cornice sottile, rametto botanico e, sul fondo
           prugna, una luce morbida; sulle cta anche le fedi intrecciate.
  "image" su list/cta/question/text: fascia fotografica in alto (campi: image, focus, band_height, default 430).
  "images": [a, b] su cover: due foto affiancate (es. chiesa | giardino).
  "theme": "natale" (sulla spec o sulla slide, insieme a deco) sostituisce i rametti con palline appese,
           stelline e fiocchi di neve dorati e una cornice doppia oro: per i post delle feste.

"image" è un percorso locale o un URL https. Le slide di un carosello ricevono la numerazione "n / N";
la cover di un carosello mostra "Scorri →".
"""
import html, json, os, sys, urllib.request
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
FONT_URLS = {
    "Playfair.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "Figtree.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/figtree/Figtree%5Bwght%5D.ttf",
}

CSS = """
@font-face{font-family:Disp;src:url(FONTS/Playfair.ttf)}
@font-face{font-family:Fig;src:url(FONTS/Figtree.ttf)}
:root{--plum:#5E3450;--ivory:#F6F2EC;--ink:#2A2228;--sage:#7E8C76;--rose:#E7C9D8}
*{box-sizing:border-box;margin:0}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Fig,sans-serif;color:var(--ink);background:var(--ivory)}
.eye{font-weight:600;font-size:26px;letter-spacing:.22em;text-transform:uppercase}
h1,h2{font-family:Disp,Georgia,serif;font-weight:600;line-height:1.08;letter-spacing:-.015em}
.mark{position:absolute;left:80px;bottom:64px;font-size:26px;letter-spacing:.08em}
.pg{position:absolute;right:80px;bottom:64px;font-size:26px;letter-spacing:.1em;opacity:.7}
.rule{width:120px;height:3px;background:var(--sage)}
.cover{background-size:cover;background-position:center}
.cover::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,10,18,0) 35%,rgba(20,10,18,.55) 62%,rgba(20,10,18,.88) 100%)}
.cover .txt{position:absolute;left:80px;right:80px;bottom:150px;z-index:2;color:#fff;display:grid;gap:28px}
.cover h1{font-size:104px}.cover .eye{color:var(--rose)}.cover .mark,.cover .pg{color:#fff;z-index:2}
.photo .img{height:690px;background-size:cover}
.photo .txt{padding:70px 80px 0;display:grid;gap:26px}
.photo .eye,.list .eye,.cta .eye{color:var(--plum)}
.photo h2{font-size:96px;color:var(--plum)}
.photo p{font-size:44px;line-height:1.3;max-width:900px}
.dark{background:var(--plum);color:var(--ivory)}
.dark .txt{position:absolute;left:80px;right:80px;top:240px;display:grid;gap:40px}
.dark .eye{color:var(--rose)}.dark .rule{background:var(--rose)}
.dark h2{font-size:140px;color:var(--ivory)}
.dark p{font-size:50px;line-height:1.3;max-width:880px}
.dark.q h2{font-size:110px}
.opts{display:grid;gap:22px;margin-top:10px}
.opts div{border:3px solid var(--rose);border-radius:60px;padding:24px 40px;font-size:46px;font-weight:600}
.list .txt,.cta .txt{position:absolute;left:80px;right:80px;top:180px;display:grid;gap:36px}
.list h2,.cta h2{font-size:120px;color:var(--plum)}
.items{display:grid;gap:30px;margin-top:10px;counter-reset:n}
.items div{display:grid;grid-template-columns:80px 1fr;gap:20px;font-size:46px;line-height:1.25;align-items:start}
.items div::before{counter-increment:n;content:counter(n);font-family:Disp,serif;font-weight:600;font-size:58px;color:var(--sage);line-height:1}
.cta p{font-size:48px;line-height:1.3}
.ctab{margin-top:30px;border-top:2px solid var(--sage);padding-top:44px;display:grid;gap:14px}
.ctab strong{font-weight:600;font-size:52px;line-height:1.2}
.ctab span{font-size:40px;font-weight:600;color:var(--plum)}
.cover.split{background:#1a0f17}
.cover.split .halves{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.cover.split .halves div{background-size:cover;background-position:center}
.frame{position:absolute;inset:36px;border:2px solid rgba(126,140,118,.45);border-radius:6px;pointer-events:none;z-index:3}
.dark .frame{border-color:rgba(231,201,216,.35)}
.dark.deco{background:radial-gradient(circle at 85% 12%,rgba(231,201,216,.18),rgba(231,201,216,0) 45%),radial-gradient(circle at 10% 95%,rgba(126,140,118,.22),rgba(126,140,118,0) 50%),var(--plum)}
.list.deco,.cta.deco{background:radial-gradient(circle at 90% 8%,rgba(231,201,216,.55),rgba(231,201,216,0) 40%),radial-gradient(circle at 5% 100%,rgba(126,140,118,.18),rgba(126,140,118,0) 45%),var(--ivory)}
.sprig{position:absolute;right:46px;top:46px;width:300px;height:300px;z-index:1;pointer-events:none}
.sprig.bl{right:auto;top:auto;left:30px;bottom:110px;transform:rotate(180deg);width:240px;height:240px}
.rings{position:absolute;right:90px;bottom:150px;width:240px;z-index:1;opacity:.9}
.band{position:absolute;left:0;right:0;top:0;background-size:cover}
.xm .frame{border:2px solid rgba(201,169,110,.75);inset:30px}
.xm .frame::after{content:"";position:absolute;inset:10px;border:1px solid rgba(201,169,110,.45);border-radius:4px}
.xm.dark.deco{background:radial-gradient(circle at 80% 10%,rgba(201,169,110,.28),rgba(201,169,110,0) 42%),radial-gradient(circle at 12% 92%,rgba(231,201,216,.18),rgba(231,201,216,0) 48%),var(--plum)}
.xm.list.deco,.xm.cta.deco{background:radial-gradient(circle at 88% 8%,rgba(201,169,110,.30),rgba(201,169,110,0) 40%),radial-gradient(circle at 6% 100%,rgba(231,201,216,.45),rgba(231,201,216,0) 45%),var(--ivory)}
.baubles{position:absolute;right:50px;top:40px;width:300px;height:330px;z-index:1;pointer-events:none}
.flakes{position:absolute;inset:0;z-index:1;pointer-events:none}
.band::after{content:"";position:absolute;left:0;right:0;bottom:0;height:90px;background:linear-gradient(180deg,rgba(246,242,236,0),var(--ivory))}
.dark .band::after{background:linear-gradient(180deg,rgba(94,52,80,0),var(--plum))}
.hasband h2{font-size:96px!important}
.hasband .items{gap:22px}.hasband .items div{font-size:42px}
"""

def sprig(color, cls="sprig"):
    import math
    leaves = []
    # stelo curvo da (270,20) a (40,280) con foglie alternate
    pts = [(270 - 230 * t, 20 + 260 * t - 70 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
    d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
    for k in range(1, 10):
        x, y = pts[k]
        x0, y0 = pts[k - 1]
        ang = math.degrees(math.atan2(y - y0, x - x0))
        for side in ((1,) if k == 9 else (1, -1)):
            a = ang + side * 55
            sz = 30 - k * 1.6
            cx, cy = x + math.cos(math.radians(a)) * sz, y + math.sin(math.radians(a)) * sz
            leaves.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" transform="rotate(%.1f %.1f %.1f)"/>' % (cx, cy, sz, sz * 0.42, a, cx, cy))
    berries = "".join('<circle cx="%.1f" cy="%.1f" r="7"/>' % (pts[k][0] + 18, pts[k][1] - 26) for k in (2, 5))
    return ('<svg class="%s" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">'
            '<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
            '<g fill="none" stroke="%s" stroke-width="2.6">%s</g><g fill="%s" opacity=".55">%s</g></svg>') % (cls, d, color, color, "".join(leaves), color, berries)

def xmas_svg(dark, kind=""):
    gold = "#C9A96E"
    ball2 = "#E7C9D8" if dark else "#5E3450"
    def ball(x, length, r, col):
        return ('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
                '<rect x="%d" y="%d" width="16" height="12" rx="2" fill="%s"/>'
                '<circle cx="%d" cy="%d" r="%d" fill="%s"/>'
                '<path d="M%d %d q%d -%d %d 0" stroke="#fff" stroke-opacity=".35" stroke-width="3" fill="none"/>') % (
            x, x, length, gold, x - 8, length, gold, x, length + 12 + r, r, col, x - r * 0.55, length + 12 + r * 0.7, r * 0.3, r * 0.3, r * 0.6)
    star = ('<svg class="baubles" viewBox="0 0 300 330" fill="none" stroke="%s" stroke-linecap="round">'
            '<path d="M230 40 L234 78 L272 82 L234 86 L230 124 L226 86 L188 82 L226 78Z" fill="%s" fill-opacity=".9" stroke-width="1.5"/>'
            '<line x1="230" y1="20" x2="230" y2="144" stroke-width="1.2" opacity=".6"/><line x1="168" y1="82" x2="292" y2="82" stroke-width="1.2" opacity=".6"/>'
            '<line x1="196" y1="48" x2="264" y2="116" stroke-width="1" opacity=".45"/><line x1="264" y1="48" x2="196" y2="116" stroke-width="1" opacity=".45"/>'
            '<circle cx="230" cy="82" r="58" stroke-width="1" opacity=".35"/></svg>') % (gold, gold)
    baub = star + ("" if kind == "question" else sprig(gold, "sprig bl"))
    import random
    rnd = random.Random(7)
    pts = [(1024, 600), (1024, 880), (880, 1236), (480, 1244), (660, 1228), (1024, 1120)]
    if kind == "question":
        pts = [q for q in pts if q[1] < 1150] + [(1024, 360)]
    fl = []
    for k, (x, y) in enumerate(pts):
        sz = rnd.choice([12, 15, 18])
        op = rnd.choice([.45, .6, .75])
        if k % 2:
            fl.append('<g transform="translate(%d %d)" stroke="%s" stroke-width="2.4" stroke-linecap="round" opacity="%.2f">'
                      '<line x1="-%d" y1="0" x2="%d" y2="0"/><line x1="0" y1="-%d" x2="0" y2="%d"/>'
                      '<line x1="-%d" y1="-%d" x2="%d" y2="%d"/><line x1="-%d" y1="%d" x2="%d" y2="-%d"/></g>' % (
                          x, y, gold, op, sz, sz, sz, sz, sz * .7, sz * .7, sz * .7, sz * .7, sz * .7, sz * .7, sz * .7, sz * .7))
        else:
            fl.append('<path transform="translate(%d %d) scale(%.2f)" d="M0 -20 L5 -5 L20 0 L5 5 L0 20 L-5 5 L-20 0 L-5 -5Z" fill="%s" opacity="%.2f"/>' % (x, y, sz / 22, gold, op))
    return baub + '<svg class="flakes" viewBox="0 0 1080 1350">%s</svg>' % "".join(fl)


RINGS = ('<svg class="rings" viewBox="0 0 200 130" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-width="5">'
         '<circle cx="72" cy="72" r="48" stroke="#7E8C76"/><circle cx="128" cy="72" r="48" stroke="#5E3450"/>'
         '<path d="M118 14 l10 -10 l10 10 l-10 10z" fill="#E7C9D8" stroke="#5E3450" stroke-width="3"/></svg>')



def ensure_fonts():
    os.makedirs(FONTS, exist_ok=True)
    for name, url in FONT_URLS.items():
        p = os.path.join(FONTS, name)
        if not os.path.exists(p):
            urllib.request.urlretrieve(url, p)


def e(s):
    return html.escape(s or "")


def img_url(src, workdir):
    if not src:
        return ""
    if src.startswith("http"):
        local = os.path.join(workdir, "_img_" + str(abs(hash(src))) + ".jpg")
        if not os.path.exists(local):
            urllib.request.urlretrieve(src, local)
        src = local
    return "file://" + os.path.abspath(src)


deco_all_theme = [None]


def slide_html(s, i, n, workdir, deco_all=False):
    h = _slide_html(s, i, n, workdir)
    t = s.get("type", "text")
    deco = s.get("deco", deco_all) and t not in ("cover", "photo")
    if s.get("image") and t in ("list", "cta", "question", "text"):
        bh = int(s.get("band_height", 430))
        band = '<div class="band" style="height:%dpx;background-image:url(\'%s\');background-position:%s"></div>' % (bh, img_url(s["image"], workdir), s.get("focus", "center"))
        h = h.replace('<div class="txt">', band + '<div class="txt" style="top:%dpx">' % (bh + 50), 1)
        h = h.replace('class="s ', 'class="s hasband ', 1)
    if deco:
        dark = t in ("text", "question")
        extra = '<div class="frame"></div>'
        col = "#E7C9D8" if dark else "#7E8C76"
        if t == "cta":
            extra += sprig(col, "sprig bl") + RINGS
        elif not s.get("image"):
            extra += sprig(col)
            if t not in ("question",):
                extra += sprig(col, "sprig bl")
        if s.get("theme", deco_all_theme[0]) == "natale":
            extra = '<div class="frame"></div>' + xmas_svg(dark, t) + (RINGS if t == "cta" else "")
            h = h.replace('class="s ', 'class="s xm ', 1)
        h = h.replace('class="s ', 'class="s deco ', 1)
        h = h[:-6] + extra + "</div>"
    return h


def _slide_html(s, i, n, workdir):
    t = s.get("type", "text")
    foot = '<div class="mark">allyoucan.wedding</div>'
    if n > 1:
        foot += '<div class="pg">%s</div>' % ("Scorri →" if i == 1 and t == "cover" else "%d / %d" % (i, n))
    eye = '<div class="eye">%s</div>' % e(s.get("eyebrow")) if s.get("eyebrow") else ""
    text = "<p>%s</p>" % e(s.get("text")) if s.get("text") else ""
    if t == "cover" and s.get("images"):
        halves = "".join('<div style="background-image:url(\'%s\')"></div>' % img_url(x, workdir) for x in s["images"])
        return '<div class="s cover split"><div class="halves">%s</div><div class="txt">%s<h1>%s</h1></div>%s</div>' % (halves, eye, e(s["title"]), foot)
    if t == "cover":
        return '<div class="s cover" style="background-image:url(\'%s\')"><div class="txt">%s<h1>%s</h1></div>%s</div>' % (
            img_url(s.get("image"), workdir), eye, e(s["title"]), foot)
    if t == "photo":
        rule = '<div class="rule"></div>' if text else ""
        return ('<div class="s photo"><div class="img" style="background-image:url(\'%s\');background-position:%s;height:%dpx"></div>'
                '<div class="txt">%s<h2>%s</h2>%s%s</div>%s</div>') % (
            img_url(s.get("image"), workdir), s.get("focus", "center"), int(s.get("img_height", 690)), eye, e(s["title"]), rule, text, foot)
    if t == "list":
        items = "".join("<div>%s</div>" % e(x) for x in s.get("items", []))
        return '<div class="s list"><div class="txt">%s<h2>%s</h2><div class="items">%s</div></div>%s</div>' % (eye, e(s["title"]), items, foot)
    if t == "question":
        opts = "".join("<div>%s</div>" % e(x) for x in s.get("options", []))
        return '<div class="s dark q"><div class="txt">%s<h2>%s</h2><div class="opts">%s</div></div>%s</div>' % (eye, e(s["title"]), opts, foot)
    if t == "cta":
        return ('<div class="s cta"><div class="txt">%s<h2>%s</h2>%s<div class="ctab"><strong>%s</strong><span>%s</span></div></div>%s</div>') % (
            eye, e(s["title"]), text, e(s.get("cta", "Un solo referente per ogni servizio.")),
            e(s.get("contact", "Scriveteci a info@allyoucan.wedding")), foot)
    return '<div class="s dark"><div class="txt">%s<h2>%s</h2><div class="rule"></div>%s</div>%s</div>' % (eye, e(s["title"]), text, foot)


def main(spec_path, out_dir):
    ensure_fonts()
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    slides = spec["slides"]
    deco_all_theme[0] = spec.get("theme")
    body = "".join('<div id="s%d">%s</div>' % (i, slide_html(s, i, len(slides), out_dir, spec.get("deco", False))) for i, s in enumerate(slides, 1))
    page = os.path.join(out_dir, "_render.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write('<!doctype html><meta charset="utf-8"><style>%s</style>%s' % (CSS.replace("FONTS", "file://" + FONTS), body))
    from PIL import Image
    outs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + os.path.abspath(page))
        pg.wait_for_timeout(700)
        for i in range(1, len(slides) + 1):
            png = os.path.join(out_dir, "_s%d.png" % i)
            pg.locator("#s%d > .s" % i).screenshot(path=png)
            name = "%s_slide%d.jpg" % (spec["post"], i) if len(slides) > 1 else "%s.jpg" % spec["post"]
            jpg = os.path.join(out_dir, name)
            Image.open(png).convert("RGB").save(jpg, quality=80, optimize=True)
            os.remove(png)
            outs.append(jpg)
        b.close()
    os.remove(page)
    print("\n".join(outs))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
