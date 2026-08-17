# -*- coding: utf-8 -*-
import json, html, re

U='https://phonodiavocalensemble.com'
mem=json.load(open('data-members.json'))
evs=json.load(open('data-events.json'))
vids=json.load(open('data-videos.json'))
albs=json.load(open('data-albums.json'))
pages={r['url']:r for r in json.load(open('harvest-pages.json'))}

def sec(url,heading=None,i=None):
    r=pages[url]
    if i is not None: return r['sections'][i]['text'] or ''
    for s in r['sections']:
        if s['heading']==heading: return s['text'] or ''
    return ''

FIX=[('με παιδιά 8 ετών έως ενήλικες 52 ετών','με παιδιά 10 ετών έως ενήλικες 54 ετών'),
     ('from 8-year-old children to adults up to 52 years old','from 10-year-old children to adults up to 54 years old'),
     ('children from 8 years old to adults up to 52 years old','children from 10 years old to adults up to 54 years old')]
def paras(t):
    t=t or ''
    for a,b in FIX: t=t.replace(a,b)
    return [p.strip() for p in t.split('||') if p.strip()]

ABOUT_EL=paras(sec(U+'/about/','Λίγα λόγια για το σύνολο'))[1:]
ABOUT_EN=paras(sec(U+'/en/a-few-words-about-the-ensemble/','The Tree of PHONODIA'))
BIO_EL=paras(sec(U+'/σχετικά-με-το-σύνολο/',None,0))[:3]
BIO_EN=paras(sec(U+'/en/about-the-ensemble/',None,0))[:3]
TES_EL=[('Άλκης Μπαλτάς',''),('Αντώνης Κοντογεωργίου',''),('Μίλτος Λογιάδης',''),('Μπάμπης Κανᾶς',''),('Νίκος Κυπουργός','')]
TES_EN=[(s['heading'],s['text']) for s in pages[U+'/en/testimonials/']['sections']]

TES_EL_TXT=json.load(open('testimonials-el.json'))

PROD=json.load(open('/home/claude/fonodia/site/products.json'))['products']
PORDER=['Phonodia in Tokyo – Kids','Phonodia in Tokyo – Gents','Phonodia in Tokyo – Ladies','Φωνη – Hoodie – Unisex','The Great Journey in Tokyo – Gents','The Great Journey in Tokyo – Ladies','Φωνη – Gents','Φωνη – Ladies','Φωνη – Kids']
pidx={p['name']:p for p in PROD}

e=html.escape
def T(el,en): return f'<span data-el="{e(el)}" data-en="{e(en)}">{e(el)}</span>'

NAV=[('#synolo','Το Σύνολο','The Ensemble'),('#ligalogia','Λίγα λόγια για το σύνολο','A few words'),
     ('#viografiko','Βιογραφικό','Biography'),('#eipan','Είπαν για εμάς','Testimonials'),
     ('#emfaniseis','Εμφανίσεις','Events'),('#meli','Μέλη','Members'),
     ('#fotografiko','Φωτογραφικό Υλικό','Photo Gallery'),('#video','Μαγνητοσκοπήσεις','Video'),
     ('#shop','Καλλιτεχνικά αναμνηστικά','Artistic Memorabilia'),('#stirikste','Στηρίξτε το έργο μας','Support us'),
     ('#epikoinonia','Επικοινωνία','Contact')]

def card(m):
    ph=m['photo'] or ''
    return f'''<figure class="m"><img loading="lazy" src="{e(ph)}" alt="{e(m['el'])}"><figcaption>{T(m['el'],m['en'])}</figcaption></figure>'''

def ev_html(v):
    meta=''.join(f'<li>{e(x)}</li>' for x in paras(v['meta']))
    body=''.join(f'<p>{e(x)}</p>' for x in paras(v['body']))
    tk=f'<a class="btn" href="{e(v["ticket"])}" target="_blank" rel="noopener">{T("Εισιτήρια","Tickets")}</a>' if v['ticket'] else ''
    img=f'<img loading="lazy" src="{e(v["poster"])}" alt="{e(v["title"])}">' if v['poster'] else ''
    return f'''<article class="ev">
<div class="ev-img">{img}</div>
<div class="ev-txt"><h3>{e(v['title'])}</h3>
<p class="dt">{e(v['date'] or '')}</p>
<p class="vn">{e(v['venue'] or '')}</p>
<ul class="meta">{meta}</ul>{body}{tk}</div></article>'''

def vid_html(v):
    meta=''.join(f'<li>{e(x)}</li>' for x in paras(v['meta']))
    body=''.join(f'<p>{e(x)}</p>' for x in paras(v['body']))
    return f'''<article class="vd"><div class="yt"><iframe loading="lazy" src="https://www.youtube.com/embed/{e(v['yt'])}" title="{e(v['title'])}" allowfullscreen></iframe></div>
<h3>{e(v['title'])}</h3><p class="dt">{e(v['date'] or '')}</p><p class="vn">{e(v['venue'] or '')}</p><ul class="meta">{meta}</ul>{body}</article>'''

def alb_html(a):
    ims=''.join(f'<a href="{e(i)}" target="_blank" rel="noopener"><img loading="lazy" src="{e(i)}" alt="{e(a["title"])}"></a>' for i in a['images'])
    return f'<section class="alb"><h3>{e(a["title"])}</h3><div class="grid-g">{ims}</div></section>'

def prod_html(n):
    p=pidx[n]
    price='{:,.2f}'.format(int(p['price'])/100).replace('.',',')+' €'
    return f'''<a class="pr" href="{e(p['permalink'])}" target="_blank" rel="noopener">
<img loading="lazy" src="{e(p['images'][0])}" alt="{e(p['name'])}">
<span class="pn">{e(p['name'])}</span><span class="pp">{price}</span></a>'''

CSS = """
:root{--ink:#12100f;--bg:#ffffff;--soft:#f6f3ee;--line:#e2dbd0;--gold:#b08d4f;--mut:#6d655c}
*{box-sizing:border-box}
body{margin:0;font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:var(--bg)}
img{max-width:100%;display:block}
a{color:inherit}
header{position:sticky;top:0;z-index:60;background:rgba(18,16,15,.96);backdrop-filter:blur(10px);color:#fff}
.bar{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:10px 18px}
.bar img{height:38px;width:auto;filter:invert(1) brightness(2)}
nav{margin-left:auto;display:flex;flex-wrap:wrap;gap:2px}
nav a{padding:7px 10px;font-size:13px;text-decoration:none;opacity:.88;border-radius:6px}
nav a:hover{background:rgba(255,255,255,.12);opacity:1}
.lang{margin-left:8px;display:flex;border:1px solid rgba(255,255,255,.35);border-radius:20px;overflow:hidden}
.lang button{background:none;border:0;color:#fff;padding:6px 12px;font:600 12px/1 inherit;cursor:pointer}
.lang button.on{background:var(--gold)}
.burger{display:none;margin-left:auto;background:none;border:1px solid rgba(255,255,255,.4);color:#fff;border-radius:8px;padding:8px 12px;font-size:16px;cursor:pointer}
.hero{position:relative;min-height:74vh;display:grid;place-items:center;text-align:center;color:#fff;overflow:hidden}
.hero img.bgimg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.42)}
.hero .in{position:relative;padding:60px 20px}
.hero h1{font-size:clamp(32px,6vw,62px);margin:0 0 8px;font-weight:600;letter-spacing:.01em}
.hero p{font-size:clamp(14px,2vw,19px);letter-spacing:.22em;text-transform:uppercase;margin:0;opacity:.9}
section.s{max-width:1180px;margin:0 auto;padding:64px 20px;border-top:1px solid var(--line)}
section.s:first-of-type{border-top:0}
h2{font-size:clamp(24px,3.4vw,36px);font-weight:600;margin:0 0 26px}
h3{font-size:20px;margin:0 0 6px;font-weight:600}
p{margin:0 0 14px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:start}
.ev{display:grid;grid-template-columns:240px 1fr;gap:26px;padding:26px 0;border-bottom:1px solid var(--line)}
.ev:last-child{border-bottom:0}
.ev-img img{border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.14)}
.dt{color:var(--gold);font-weight:600;margin:0 0 2px}
.vn{color:var(--mut);margin:0 0 10px}
ul.meta{list-style:none;padding:0;margin:0 0 12px;color:var(--mut);font-size:14px}
ul.meta li{padding:1px 0}
.btn{display:inline-block;margin-top:8px;padding:10px 20px;background:var(--ink);color:#fff;text-decoration:none;border-radius:24px;font-size:14px}
.grid-m{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:20px}
figure.m{margin:0;text-align:center}
figure.m img{aspect-ratio:1/1;object-fit:cover;border-radius:50%;width:100%;background:var(--soft)}
figure.m figcaption{margin-top:9px;font-size:14px}
.lead{display:flex;gap:24px;align-items:center;margin-bottom:34px;flex-wrap:wrap}
.lead img{width:130px;height:130px;object-fit:cover;border-radius:50%}
.grid-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.grid-g img{aspect-ratio:3/2;object-fit:cover;border-radius:8px}
.alb{margin-bottom:36px}
.grid-v{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:32px}
.yt{position:relative;padding-top:56.25%;margin-bottom:12px}
.yt iframe{position:absolute;inset:0;width:100%;height:100%;border:0;border-radius:10px}
.grid-p{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:22px}
.pr{text-decoration:none;text-align:center;display:block}
.pr img{background:var(--soft);border-radius:10px;aspect-ratio:1/1;object-fit:contain;padding:8px}
.pn{display:block;margin-top:9px;font-size:14px}
.pp{display:block;color:var(--gold);font-weight:600;font-size:14px}
blockquote{margin:0 0 30px;padding:22px 26px;background:var(--soft);border-left:3px solid var(--gold);border-radius:0 10px 10px 0}
blockquote h3{color:var(--gold)}
footer{background:var(--ink);color:#e9e3da;margin-top:20px}
.fin{max-width:1180px;margin:0 auto;padding:52px 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:32px;font-size:14px}
.fin img.pay{height:26px;width:auto;display:inline-block;margin:4px 6px 0 0;filter:none}
footer a{color:#e9e3da}
.copy{border-top:1px solid rgba(255,255,255,.14);padding:16px 20px;text-align:center;font-size:12.5px;opacity:.72}
@media(max-width:860px){
 nav{display:none;width:100%;flex-direction:column;background:rgba(18,16,15,.99);padding:6px 0}
 nav.open{display:flex}
 .burger{display:block}
 .bar{flex-wrap:wrap}
 .two{grid-template-columns:1fr}
 .ev{grid-template-columns:1fr}
 .ev-img img{max-width:260px;margin:0 auto}
}
"""

JS = """
function setLang(l){
 document.querySelectorAll('[data-el]').forEach(function(n){n.textContent=n.getAttribute('data-'+l)});
 document.querySelectorAll('[data-elhtml]').forEach(function(n){n.innerHTML=n.getAttribute('data-'+l+'html')});
 document.documentElement.lang=(l==='el'?'el':'en');
 document.querySelectorAll('.lang button').forEach(function(b){b.classList.toggle('on',b.dataset.l===l)});
 try{localStorage&&0}catch(e){}
}
document.querySelectorAll('.lang button').forEach(function(b){b.onclick=function(){setLang(b.dataset.l)}});
document.querySelector('.burger').onclick=function(){document.querySelector('nav').classList.toggle('open')};
document.querySelectorAll('nav a').forEach(function(a){a.onclick=function(){document.querySelector('nav').classList.remove('open')}});
"""

def bl(el_paras,en_paras):
    """bilingual paragraph block"""
    elh=''.join('<p>'+e(p)+'</p>' for p in el_paras)
    enh=''.join('<p>'+e(p)+'</p>' for p in en_paras)
    return f'<div data-elhtml="{e(elh)}" data-enhtml="{e(enh)}">{elh}</div>'

nav_html=''.join(f'<a href="{h}">{T(a,b)}</a>' for h,a,b in NAV)

tes_html=''
for i,(nm,_) in enumerate(TES_EL):
    el_txt=TES_EL_TXT[i]['text']; en_nm,en_txt=TES_EN[i]
    elh=''.join('<p>'+e(p)+'</p>' for p in el_txt.split('\n\n') if p.strip())
    enh=''.join('<p>'+e(p)+'</p>' for p in en_txt.split('||') if p.strip())
    tes_html+=f'<blockquote><h3>{T(nm,en_nm)}</h3><div data-elhtml="{e(elh)}" data-enhtml="{e(enh)}">{elh}</div></blockquote>'

HERO=U+'/wp-content/uploads/2020/06/20171218_Christmas_Concert_Bach-64.jpg'
TREE=U+'/wp-content/uploads/2025/05/ΤΟ-ΔΕΝΤΡΟ-ΜΑΣ-e1746545945362.jpg'
LOGO=U+'/wp-content/uploads/2025/04/Φωνωδία-aspro.png'
PAY=[U+'/wp-content/uploads/2025/11/274751750325e062f8530373699503fbbfa16b58.png',
     U+'/wp-content/uploads/2025/11/d51f7a234af740dcf1ad7dc9619e18c065a31cf7.png',
     U+'/wp-content/uploads/2025/11/e0b4cdc54800b9d7abcb9c012990662978eb39d4.png',
     U+'/wp-content/uploads/2025/11/c7b56c359755790e7604b830a8a7390d172dc900.png',
     U+'/wp-content/uploads/2025/11/IRIS-online-payments-logo-4283025463.jpg']
AMKE_EL='Η Φωνωδία λειτουργεί υπό το Κέντρο Φωνητικής Τέχνης Κρήτης στο Ηράκλειο της Κρήτης – μιας Αστικής Μη-Κερδοσκοπικής Εταιρίας που στόχο έχει την ανάδειξη της μουσικής τέχνης στο νησί, μέσα από τη φωνητική και το χορωδιακό τραγούδι.'
AMKE_EN='Phonodia (Fónodia) operates under the Cretan Center of Vocal Arts in Herakleion, Crete – an Urban Non-Profit Organization with the aim of promoting the art of music through vocal performance and choral works.'

SUP_EL=paras(sec(U+'/sponsor-us/',None,0))+paras(sec(U+'/sponsor-us/','Η στήριξή σας σημαίνει τα πάντα για εμάς!'))
SUP_EN=paras(sec(U+'/en/support-our-projects/',None,0))

doc=f'''<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Φωνητικό σύνολο Φωνωδία</title>
<style>{CSS}</style>
</head>
<body>
<header>
<div class="bar">
<img src="{LOGO}" alt="Φωνωδία">
<button class="burger" aria-label="menu">☰</button>
<nav>{nav_html}</nav>
<div class="lang"><button data-l="el" class="on">EL</button><button data-l="en">EN</button></div>
</div>
</header>

<div class="hero" id="synolo">
<img class="bgimg" src="{HERO}" alt="">
<div class="in">
<h1>{T('Φωνητικό σύνολο Φωνωδία','Phonodia Vocal Ensemble')}</h1>
<p>{T('Κέντρο Φωνητικής Τέχνης Κρήτης','Cretan Center for Vocal Arts')}</p>
</div>
</div>

<section class="s" id="ligalogia">
<h2>{T('Λίγα λόγια για το σύνολο','A few words about the ensemble')}</h2>
<div class="two">
<div><img src="{TREE}" alt="Το δέντρο της ΦΩΝΩΔΙΑΣ" style="border-radius:12px">
<p style="text-align:center;margin-top:10px;color:var(--mut)">{T('Το δέντρο της ΦΩΝΩΔΙΑΣ','The Tree of PHONODIA')}</p></div>
<div>{bl(ABOUT_EL,ABOUT_EN)}</div>
</div>
</section>

<section class="s" id="viografiko">
<h2>{T('Βιογραφικό','Biography')}</h2>
{bl(BIO_EL,BIO_EN)}
</section>

<section class="s" id="eipan">
<h2>{T('Είπαν για εμάς','Testimonials')}</h2>
{tes_html}
</section>

<section class="s" id="emfaniseis">
<h2>{T('Εμφανίσεις','Events')}</h2>
{''.join(ev_html(v) for v in evs)}
</section>

<section class="s" id="meli">
<h2>{T('Μέλη','Members')}</h2>
<div class="lead"><img src="{e(mem['director']['photo'])}" alt="Ιωάννης Ιδομενέως">
<div><h3>{T('Ιωάννης Ιδομενέως','Ioannis Idomeneos')}</h3><p style="color:var(--mut)">{T('Καλλιτεχνικός διευθυντής','Artistic Director')}</p></div></div>
<h3 style="margin:26px 0 16px">{T('Μέλη','Members')}</h3>
<div class="grid-m">{''.join(card(m) for m in mem['members'])}</div>
<h3 style="margin:40px 0 16px">{T('Παιδικά – Εφηβικά Τμήματα','Junior & Youth Division')}</h3>
<div class="grid-m">{''.join(card(m) for m in mem['kids'])}</div>
<h3 style="margin:40px 0 16px">{T('Συνεργάτες','Collaborators')}</h3>
<div class="grid-m">{''.join(card(m) for m in mem['partners'])}</div>
<p style="text-align:center;color:var(--mut);font-size:14px;margin-top:10px">{T('Υπεύθυνη Έργου & Οπτικής Ταυτότητας','Project Manager & Visual Identity Coordinator')}</p>
</section>

<section class="s" id="fotografiko">
<h2>{T('Φωτογραφικό Υλικό','Photo Gallery')}</h2>
{''.join(alb_html(a) for a in albs)}
</section>

<section class="s" id="video">
<h2>{T('Μαγνητοσκοπήσεις','Video')}</h2>
<div class="grid-v">{''.join(vid_html(v) for v in vids)}</div>
</section>

<section class="s" id="shop">
<h2>{T('Καλλιτεχνικά αναμνηστικά','Artistic Memorabilia')}</h2>
<div class="grid-p">{''.join(prod_html(n) for n in PORDER)}</div>
</section>

<section class="s" id="stirikste">
<h2>{T('Στηρίξτε το έργο μας','Support our Projects')}</h2>
{bl(SUP_EL,SUP_EN)}
</section>

<section class="s" id="epikoinonia">
<h2>{T('Επικοινωνία','Contact')}</h2>
<p>{T('Ελάτε σε επικοινωνία','Feel free to contact us')}</p>
<p>Ιερολοχιτών 3, 71305, Ηράκλειο Κρήτης</p>
<p>Email: <a href="mailto:contact@phonodia.com">contact@phonodia.com</a></p>
<p>{T('Ακολουθήστε μας στα social ή στείλτε μας email.','Follow us on social media or send us an email')}</p>
<p><a href="https://www.instagram.com/phonodia_vocal_ensemble" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.youtube.com/channel/UCEKFE5EBTg78MRV2zHX7fZQ" target="_blank" rel="noopener">YouTube</a></p>
</section>

<footer>
<div class="fin">
<div><img src="{LOGO}" alt="Φωνωδία" style="height:44px;margin-bottom:12px">
<p>{T(AMKE_EL,AMKE_EN)}</p></div>
<div><p><strong>Κέντρο Φωνητικής Τέχνης Κρήτης</strong><br>Αστική Μη-Κερδοσκοπική Εταιρία<br>Ιερολοχιτών 3, 71305, Ελλάδα<br>ΑΦΜ: EL996445420</p>
<p><strong>Cretan Center of Vocal Arts</strong><br>Urban Non-Profit Organization<br>Ieroloxiton 3, 71305, Greece<br>VAT: EL996445420</p></div>
<div><p>We accept all major card networks, Apple Pay, Google Pay or IRIS Payments</p>
<p>{''.join(f'<img class="pay" src="{p}" alt="">' for p in PAY)}</p>
<p><a href="{U}/όροι-χρήσης/" target="_blank" rel="noopener">{T('Όροι Χρήσης','Terms of Use')}</a> · <a href="{U}/πολιτική-απορρήτου/" target="_blank" rel="noopener">{T('Πολιτική Απορρήτου','Privacy Policy')}</a></p></div>
</div>
<div class="copy">© Κέντρο Φωνητικής Τέχνης Κρήτης — Φωνητικό σύνολο ΦΩΝΩΔΙΑ</div>
</footer>
<script>{JS}</script>
</body></html>'''

open('/home/claude/fonodia/clone/fonodia-klonos.html','w',encoding='utf-8').write(doc)
print('bytes',len(doc.encode()))
