"""Genera le grafiche dei post AllYouCanWedding (1080x1350 JPEG) da una specifica JSON.

Uso:  python3 tools/render.py spec.json OUT_DIR
Spec: {"post": "p04", "slides": [ {...}, ... ]}

Tipi di slide (tutti i campi testo sono facoltativi tranne "title"):
  cover    foto a tutto schermo + eyebrow + title          campi: image, eyebrow, title
  photo    foto in alto, testo sotto su avorio             campi: image, focus ("center", "top", "50% 30%"...), eyebrow, title, text
  text     fondo prugna, solo testo                        campi: eyebrow, title, text
  list     fondo avorio, elenco puntato numerato           campi: eyebrow, title, items[]
  question fondo prugna, domanda grande e opzioni          campi: eyebrow, title, options[]
  cta      fondo avorio, chiusura con contatto             campi: eyebrow, title, text, cta, contact

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
"""


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


def slide_html(s, i, n, workdir):
    t = s.get("type", "text")
    foot = '<div class="mark">allyoucan.wedding</div>'
    if n > 1:
        foot += '<div class="pg">%s</div>' % ("Scorri →" if i == 1 and t == "cover" else "%d / %d" % (i, n))
    eye = '<div class="eye">%s</div>' % e(s.get("eyebrow")) if s.get("eyebrow") else ""
    text = "<p>%s</p>" % e(s.get("text")) if s.get("text") else ""
    if t == "cover":
        return '<div class="s cover" style="background-image:url(\'%s\')"><div class="txt">%s<h1>%s</h1></div>%s</div>' % (
            img_url(s.get("image"), workdir), eye, e(s["title"]), foot)
    if t == "photo":
        return ('<div class="s photo"><div class="img" style="background-image:url(\'%s\');background-position:%s"></div>'
                '<div class="txt">%s<h2>%s</h2><div class="rule"></div>%s</div>%s</div>') % (
            img_url(s.get("image"), workdir), s.get("focus", "center"), eye, e(s["title"]), text, foot)
    if t == "list":
        items = "".join("<div>%s</div>" % e(x) for x in s.get("items", []))
        return '<div class="s list"><div class="txt">%s<h2>%s</h2><div class="items">%s</div></div>%s</div>' % (eye, e(s["title"]), items, foot)
    if t == "question":
        opts = "".join("<div>%s</div>" % e(x) for x in s.get("options", []))
        return '<div class="s dark q"><div class="txt">%s<h2>%s</h2><div class="opts">%s</div></div>%s</div>' % (eye, e(s["title"]), opts, foot)
    if t == "cta":
        return ('<div class="s cta"><div class="txt">%s<h2>%s</h2>%s<div class="ctab"><strong>%s</strong><span>%s</span></div></div>%s</div>') % (
            eye, e(s["title"]), text, e(s.get("cta", "Un solo referente per ogni servizio.")),
            e(s.get("contact", "Scriveteci in privato · allyoucan.wedding")), foot)
    return '<div class="s dark"><div class="txt">%s<h2>%s</h2><div class="rule"></div>%s</div>%s</div>' % (eye, e(s["title"]), text, foot)


def main(spec_path, out_dir):
    ensure_fonts()
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    slides = spec["slides"]
    body = "".join('<div id="s%d">%s</div>' % (i, slide_html(s, i, len(slides), out_dir)) for i, s in enumerate(slides, 1))
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
