"""Post 7 CalcioAllDay - chiusura della giornata. Uso: python3 make.py spec.json
spec: {cover_kicker, cover_title[], results:[[casa,gol,gol,trasferta]], stories:[{kicker,title[],body}],
       table:[[pos,squadra,punti]], table_note, cta_title[], cta_body, box:[titolo,testo], tag}"""
import json,sys
from PIL import Image, ImageDraw, ImageFont
NAVY=(20,38,56); MINT=(69,213,165); CREAM=(247,242,232); GREEN=(36,75,61)
T=lambda s: ImageFont.truetype(__import__('os').path.join(__import__('os').path.dirname(__file__),'barlow-condensed-800.ttf'),s)
B=lambda s: ImageFont.truetype(__import__('os').path.join(__import__('os').path.dirname(__file__),'inter-400.ttf'),s)
K=lambda s: ImageFont.truetype(__import__('os').path.join(__import__('os').path.dirname(__file__),'inter-600.ttf'),s)
W,H=1080,1350; L=90
sp=json.load(open(sys.argv[1])); N=3+len(sp['stories'])
RH=sp.get("row_h",150); RF=sp.get("row_font",64); RS=sp.get("row_score",80)
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def base(n):
    im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im,'RGBA')
    # linee del campo, appena visibili
    c=(69,213,165,28)
    d.ellipse([W-330,H-640,W+330,H+20],outline=c,width=4)
    d.line([(W-330,0),(W-330,H)],fill=c,width=4)
    d.rectangle([W-150,H-760,W+10,H-100],outline=c,width=4)
    d.line([(L,H-112),(W-L,H-112)],fill=(69,213,165,90),width=2); d.rectangle([L,H-113,L+60,H-110],fill=MINT)
    d.text((L,H-90),"@calcioallday",font=K(26),fill=CREAM)
    s=f"{n}/{N}"; d.text((W-L-d.textlength(s,font=K(26)),H-90),s,font=K(26),fill=MINT)
    d.rectangle([L,110,L+60,115],fill=MINT)
    return im,d
def head(d,kicker,title,y=138,size=132,step=124):
    if kicker: d.text((L,y),kicker,font=K(30),fill=MINT); y+=58
    for ln in title: d.text((L,y),ln,font=T(size),fill=CREAM); y+=step
    return y
n=1
im,d=base(n); y=head(d,sp['cover_kicker'],sp['cover_title'],size=118,step=110)+40
for k,(h,gh,ga,a) in enumerate(sp['results']):
    top=(k==sp.get('highlight',-1))
    bg,tx,sc_c=(MINT,NAVY,NAVY) if top else (GREEN,CREAM,MINT)
    d.rounded_rectangle([L,y,W-L,y+RH],radius=16,fill=bg)
    f=T(RF); sc=f"{gh}–{ga}"
    d.text((L+34,y+(RH-RF)/2-4),h.upper(),font=f,fill=tx)
    tw=d.textlength(a.upper(),font=f); d.text((W-L-34-tw,y+(RH-RF)/2-4),a.upper(),font=f,fill=tx)
    sw=d.textlength(sc,font=T(RS)); d.text(((W-sw)/2,y+(RH-RS)/2-6),sc,font=T(RS),fill=sc_c)
    y+=RH+16
im.save(f"slide-{n}.jpg",quality=92)
for i,st in enumerate(sp['stories']):
    n+=1; im,d=base(n); f=T(330); sc=st.get('score','')
    if i%2==1 and sc:
        # risultato in alto, titolo e testo sotto
        d.text((L,138),st['kicker'],font=K(30),fill=MINT)
        d.text((L-8,170),sc,font=f,fill=MINT)
        d.text((L,520),st.get('teams','').upper(),font=K(30),fill=CREAM)
        y=head(d,None,st['title'],y=600)+40
        for ln in wrap(d,st['body'],B(38),W-2*L): d.text((L,y),ln,font=B(38),fill=CREAM); y+=54
    else:
        y=head(d,st['kicker'],st['title'])+44
        for ln in wrap(d,st['body'],B(38),W-2*L): d.text((L,y),ln,font=B(38),fill=CREAM); y+=54
        if sc:
            d.text((L-8,H-560),sc,font=f,fill=MINT)
            d.text((L,H-205),st.get('teams','').upper(),font=K(30),fill=CREAM)
    im.save(f"slide-{n}.jpg",quality=92)
n+=1; im,d=base(n); y=head(d,"CLASSIFICA",["CINQUE SQUADRE","IN SEI PUNTI."],size=118,step=110)+30
for i,(p,sq,pt) in enumerate(sp['table']):
    if i%2==0: d.rectangle([L,y-12,W-L,y+84],fill=(36,75,61,150))
    d.text((L+24,y),str(p),font=T(56),fill=MINT); d.text((L+110,y),sq.upper(),font=T(56),fill=CREAM)
    s=str(pt); d.text((W-L-24-d.textlength(s,font=T(56)),y),s,font=T(56),fill=CREAM); y+=104
if sp.get('table_note'):
    y+=20
    for ln in wrap(d,sp['table_note'],B(32),W-2*L): d.text((L,y),ln,font=B(32),fill=CREAM); y+=46
im.save(f"slide-{n}.jpg",quality=92)
n+=1; im,d=base(n); y=head(d,None,sp['cta_title'])+44
for ln in wrap(d,sp['cta_body'],B(38),W-2*L): d.text((L,y),ln,font=B(38),fill=CREAM); y+=54
y+=30; d.rectangle([L,y,W-L,y+150],fill=MINT)
d.text((L+30,y+28),sp['box'][0],font=K(40),fill=NAVY); d.text((L+30,y+84),sp['box'][1],font=B(34),fill=NAVY)
if sp.get('cta_big'): d.text((L-8,y+150-70),sp['cta_big'],font=T(330),fill=MINT)
im.save(f"slide-{n}.jpg",quality=92)
print("ok",n,"slide")
