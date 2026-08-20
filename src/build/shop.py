# -*- coding: utf-8 -*-
"""E-shop for the ΦΩΝΩΔΙΑ static clone: listing, product pages, cart."""
import os, re, json, html as H, urllib.parse as up
from lib import ROOT, CLONE, SITE, esc

WC_CART = SITE + '/en/cart/'
WC_CHECKOUT = SITE + '/en/checkout/'

# colour term -> swatch hex (Needleworks / Gildan-style names)
SWATCH = {
    'WHITE': '#ffffff', 'BLACK': '#141414', 'NAVY': '#1c2b45', 'MAROON': '#5c1a25',
    'BURGUNDY': '#6b1f2e', 'ROYAL': '#1f4fa8', 'SAPPHIRE': '#12507e', 'PURPLE': '#4b2a72',
    'IRIS': '#5a6fb5', 'JADE': '#00816d', 'FOREST GREEN': '#1f3d2b', 'LIGHT BLUE': '#a8c8e4',
    'CAROLINE BLUE': '#7fa9d6', 'CAROLINA BLUE': '#7fa9d6', 'AZALEA': '#f2a2bd',
    'DAISY': '#f6d64a', 'HELICONA': '#e0518a', 'HELICONIA': '#e0518a', 'RED': '#b8202c',
    'SPORT GREY': '#b6b6b6', 'GREY': '#8e8e8e', 'CHARCOAL': '#4a4d50', 'SAND': '#d9cbb3',
    'ORANGE': '#e8703a', 'PINK': '#efb0c8', 'GOLD': '#e0a92b', 'YELLOW': '#f2d33d',
    'SKY': '#8ec3e6', 'PISTACHIO': '#b9d3a3', 'TURQUOISE': '#2fb3b8', 'CHERRY RED': '#a3172a',
}
SIZE_ORDER = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

# Τιμές σε λεπτά — μπλουζάκια 18 €, φούτερ 28 € (εντολή Ιωάννη Ιδομενέως, 17 Αυγ 2026)
PRICE = {6525: 2800}
PRICE_DEFAULT = 1800

# Το WordPress κρατά μικρότερες εκδοχές κάθε φωτογραφίας. Το επίθεμα ανά προϊόν
# επαληθεύτηκε ένα-ένα από το srcset του Store API (17 Αυγ 2026) — τίποτα δεν μαντεύτηκε.
RESIZE = {6525: '-600x299', 6016: '-600x375', 5389: '-600x375', 5359: '-600x375',
          5880: '-600x450', 5313: '-600x450', 5292: '-600x450', 5415: '-600x450',
          6538: '-600x450'}

def small(url, pid):
    """Η ~600px εκδοχή της ίδιας φωτογραφίας — δεκάδες φορές ελαφρύτερη."""
    suf = RESIZE.get(int(pid)) if url else None
    if not suf:
        return url
    base, ext = os.path.splitext(url)
    return base + suf + ext

T = {
    'el': dict(shop='Κατάστημα', cart='Καλάθι', size='Μέγεθος', color='Χρώμα',
               qty='Ποσότητα', add='Προσθήκη στο καλάθι', added='Προστέθηκε στο καλάθι',
               choose='Επιλέξτε μέγεθος και χρώμα', empty='Το καλάθι σας είναι άδειο.',
               total='Σύνολο', checkout='Ολοκλήρωση παραγγελίας', remove='Αφαίρεση',
               back='Συνέχεια αγορών', product='Προϊόν', price='Τιμή', view='Επιλογή',
               note='Η πληρωμή ολοκληρώνεται με ασφάλεια μέσω Viva — κάρτες, Apple Pay, Google Pay και IRIS.',
               ship='Η παραγωγή γίνεται κατά παραγγελία και η αποστολή γίνεται από τη Needleworks.',
               zoom='Πατήστε τη φωτογραφία για μεγέθυνση',
               cartline='Το καλάθι σας',
               order='Στοιχεία παραγγελίας', o_name='Ονοματεπώνυμο', o_email='Email',
               o_phone='Τηλέφωνο', o_addr='Διεύθυνση παράδοσης', o_city='Πόλη',
               o_zip='Ταχυδρομικός κώδικας', o_notes='Σημείωση (προαιρετικά)',
               o_send='Αποστολή παραγγελίας', o_req='Συμπληρώστε τα υποχρεωτικά πεδία.',
               o_empty='Το καλάθι σας είναι άδειο. Επιλέξτε πρώτα ένα προϊόν.',
               o_ok='Η παραγγελία ετοιμάστηκε. Ανοίγει το πρόγραμμα email σας για να την στείλετε.',
               o_intro='Συμπληρώστε τα στοιχεία σας. Θα λάβετε απάντηση με τον τρόπο πληρωμής '
                       'και τον χρόνο παράδοσης. Δεν χρεώνεστε τίποτα σε αυτό το βήμα.',
               o_cart='Η παραγγελία σας'),
    'en': dict(shop='Shop', cart='Cart', size='Size', color='Colour',
               qty='Quantity', add='Add to basket', added='Added to your basket',
               choose='Choose a size and a colour', empty='Your basket is currently empty.',
               total='Total', checkout='Proceed to checkout', remove='Remove',
               back='Continue shopping', product='Product', price='Price', view='Select options',
               note='Payment is completed securely through Viva — cards, Apple Pay, Google Pay and IRIS.',
               ship='Items are produced on demand and shipped by Needleworks.',
               zoom='Click the photo to enlarge',
               cartline='Your basket',
               order='Order details', o_name='Full name', o_email='Email',
               o_phone='Phone', o_addr='Delivery address', o_city='City',
               o_zip='Postcode', o_notes='Note (optional)',
               o_send='Send order', o_req='Please fill in the required fields.',
               o_empty='Your basket is empty. Please choose a product first.',
               o_ok='Your order is ready. Your email program is opening so you can send it.',
               o_intro='Fill in your details. You will receive a reply with the payment method '
                       'and the delivery time. Nothing is charged at this step.',
               o_cart='Your order'),
}

def money(minor, unit=2):
    return ('{:,.%df}' % unit).format(int(minor) / (10 ** unit)).replace(',', ' ').replace('.', ',') + ' €'

def clean(s):
    return H.unescape(s or '').replace('–', '–').strip()

def sort_sizes(terms):
    return sorted(terms, key=lambda t: SIZE_ORDER.index(t) if t in SIZE_ORDER else 99)

def slug_of(permalink):
    return up.unquote(permalink).rstrip('/').split('/')[-1]


def load():
    prods = json.load(open(CLONE + '/data-products-full.json', encoding='utf-8'))
    try:
        VAR = json.load(open(CLONE + '/data-variations.json', encoding='utf-8'))
    except Exception:
        VAR = {}
    out = []
    for p in prods:
        attrs = {a['name']: a['terms'] for a in (p.get('attributes') or [])}
        var_imgs = {k: v for k, v in VAR.get(str(p['id']), {}).items() if not k.startswith('_')}
        out.append(dict(
            id=p['id'], name=clean(p['name']), permalink=p['permalink'],
            slug=slug_of(p['permalink']),
            price=PRICE.get(p['id'], PRICE_DEFAULT), unit=p.get('currency_minor_unit') or 2,
            image=(p['images'] or [None])[0], images=p['images'],
            desc=p.get('description') or '', short=p.get('short_description') or '',
            cats=p.get('categories') or [],
            sizes=sort_sizes(attrs.get('Size') or []), colors=attrs.get('Color') or [],
            var_imgs=var_imgs,
        ))
    order = ['Phonodia in Tokyo – Kids', 'Phonodia in Tokyo – Gents', 'Phonodia in Tokyo – Ladies',
             'Φωνη – Hoodie – Unisex', 'The Great Journey in Tokyo – Gents',
             'The Great Journey in Tokyo – Ladies', 'Φωνη – Gents', 'Φωνη – Ladies', 'Φωνη – Kids']
    idx = {p['name']: p for p in out}
    return [idx[n] for n in order if n in idx] + [p for p in out if p['name'] not in order]


# ------------------------------------------------------------------ markup
def card(p, lang, href):
    t = T[lang]
    return '''<li class="product">
<a class="woocommerce-LoopProduct-link" href="%s">
<span class="prod_thumb"><img loading="lazy" decoding="async" width="600" height="450" src="%s" alt="%s"></span>
<h2 class="woocommerce-loop-product__title">%s</h2>
<span class="price"><span class="woocommerce-Price-amount amount">%s</span></span>
</a>
<a href="%s" class="button">%s</a>
</li>''' % (href, esc(small(p['image'], p['id'])), esc(p['name']), esc(p['name']), money(p['price'], p['unit']), href, t['view'])


def listing(products, lang, hrefs, intro=''):
    t = T[lang]
    items = ''.join(card(p, lang, hrefs[p['slug']]) for p in products)
    lead = '<p class="shop_intro">%s</p>' % esc(intro) if intro else ''
    return '''<div class="lc_content_full lc_swp_boxed lc_basic_content_padding woocommerce">%s
<ul class="products columns-3">%s</ul>
<p class="shop_note">%s<br>%s</p></div>''' % (lead, items, esc(t['note']), esc(t['ship']))


def product_page(p, lang, cart_href, shop_href):
    t = T[lang]
    sizes = ''.join('<button type="button" class="opt size_opt" data-v="%s">%s</button>' % (esc(s), esc(s)) for s in p['sizes'])
    cols = ''
    for c in p['colors']:
        hexv = SWATCH.get(c.upper())
        sw = ('<i style="background:%s"></i>' % hexv) if hexv else ''
        vfull = p.get('var_imgs', {}).get(c.upper()) or p.get('var_imgs', {}).get(c)
        vimg = small(vfull, p['id']) if vfull else vfull
        cols += '<button type="button" class="opt color_opt%s" data-v="%s" data-img="%s" data-full="%s" title="%s">%s<span>%s</span></button>' % (
            ' has_sw' if hexv else '', esc(c), esc(vimg or ''), esc(vfull or ''), esc(c), sw, esc(c.title()))
    desc = p['desc'] or p['short'] or ''
    desc = re.sub(r'\sdata-(start|end)="[^"]*"', '', desc)
    return '''<div class="lc_content_full lc_swp_boxed lc_basic_content_padding woocommerce single_product"
 data-pid="%s" data-pname="%s" data-pprice="%s" data-pimg="%s" data-purl="%s">
<div class="prod_wrap">
  <div class="prod_images">
    <a id="prod_zoom" href="%s" data-lightbox="product" title="%s"><img id="prod_main_img" src="%s" alt="%s"></a>
    <span class="zoom_hint">%s</span>
  </div>
  <div class="prod_summary">
    <p class="prod_top_back"><a href="%s">%s</a></p>
    <h1 class="product_title">%s</h1>
    <p class="price"><span class="woocommerce-Price-amount amount">%s</span></p>
    <div class="opt_group"><span class="opt_label">%s</span><div class="opts" id="sizes">%s</div></div>
    <div class="opt_group"><span class="opt_label">%s <b class="opt_pick" id="color_pick"></b></span><div class="opts" id="colors">%s</div></div>
    <div class="opt_group qty_group"><span class="opt_label">%s</span>
      <div class="qty_box"><button type="button" class="qminus">−</button><input type="text" id="qty" value="1" inputmode="numeric"><button type="button" class="qplus">+</button></div>
    </div>
    <button type="button" id="add_to_cart" class="lc_button lc_button_fill">%s</button>
    <p class="add_msg" id="add_msg"></p>
    <div class="prod_desc">%s</div>
    <p class="shop_note">%s<br>%s</p>
    <p class="prod_back"><a href="%s">%s</a> &nbsp;·&nbsp; <a href="%s">%s</a></p>
  </div>
</div></div>''' % (p['id'], esc(p['name']), p['price'], esc(small(p['image'], p['id'])), esc(p['permalink']),
                   esc(p['image']), esc(t['zoom']), esc(small(p['image'], p['id'])), esc(p['name']), esc(t['zoom']),
                   shop_href, esc('\u2190 ') + t['shop'], esc(p['name']), money(p['price'], p['unit']),
                   t['size'], sizes, t['color'], cols, t['qty'], t['add'], desc,
                   esc(t['note']), esc(t['ship']), shop_href, t['back'], cart_href, t['cart'])


def cart_page(lang, shop_href, order_href):
    t = T[lang]
    return '''<div class="lc_content_full lc_swp_boxed lc_basic_content_padding woocommerce cart_page"
 data-empty="%s" data-total="%s" data-remove="%s" data-checkout="%s" data-wc="%s">
<div id="cart_body"></div>
<p class="shop_note">%s<br>%s</p>
<p class="prod_back"><a href="%s">%s</a></p></div>''' % (
        esc(t['empty']), esc(t['total']), esc(t['remove']), esc(t['checkout']), esc(order_href),
        esc(t['note']), esc(t['ship']), shop_href, t['back'])



# Παραλήπτες της παραγγελίας. Ο Ιωάννης Ιδομενέως και η Needleworks που ετοιμάζει
# την αποστολή. Όσο δεν υπάρχει υπηρεσία αποστολής email, η φόρμα ανοίγει το
# πρόγραμμα αλληλογραφίας του πελάτη με το μήνυμα έτοιμο.
ORDER_TO = 'contact@phonodia.com'
ORDER_CC = 'office@needleworks.gr'   # το ζήτησε ο Μιχάλης, 19 Αυγ 2026 (δουλεύει και το info)
ORDER_ENDPOINT = ''          # όταν στηθεί υπηρεσία, μπαίνει εδώ η διεύθυνσή της


def order_page(lang, shop_href):
    t = T[lang]
    f = lambda i, lab, typ, req: (
        '<p class="of_row"><label for="%s">%s%s</label>'
        '<input id="%s" type="%s"%s></p>' % (i, esc(lab), ' *' if req else '', i, typ,
                                             ' required' if req else ''))
    fields = (f('of_name', t['o_name'], 'text', True) +
              f('of_email', t['o_email'], 'email', True) +
              f('of_phone', t['o_phone'], 'tel', True) +
              f('of_addr', t['o_addr'], 'text', True) +
              f('of_city', t['o_city'], 'text', True) +
              f('of_zip', t['o_zip'], 'text', True) +
              '<p class="of_row"><label for="of_notes">%s</label>'
              '<textarea id="of_notes" rows="3"></textarea></p>' % esc(t['o_notes']))
    return '''<div class="lc_content_full lc_swp_boxed lc_basic_content_padding order_page"
 data-to="%s" data-cc="%s" data-endpoint="%s" data-empty="%s" data-req="%s" data-ok="%s"
 data-total="%s" data-subject="%s">
<p class="shop_intro">%s</p>
<h3 class="of_h">%s</h3>
<div id="order_cart"></div>
<h3 class="of_h">%s</h3>
<form class="order_form" id="order_form" novalidate>%s
<button type="submit" id="of_send" class="lc_button lc_button_fill">%s</button>
<p class="add_msg" id="of_msg"></p></form>
<p class="shop_note">%s<br>%s</p>
<p class="prod_back"><a href="%s">%s</a></p></div>''' % (
        ORDER_TO, ORDER_CC, ORDER_ENDPOINT, esc(t['o_empty']), esc(t['o_req']), esc(t['o_ok']),
        esc(t['total']), esc('Νέα παραγγελία' if lang == 'el' else 'New order'),
        esc(t['o_intro']), esc(t['o_cart']), esc(t['order']), fields, esc(t['o_send']),
        esc(t['note']), esc(t['ship']), shop_href, t['back'])

CSS = r'''
/* ---------------- e-shop ---------------- */
.woocommerce ul.products{list-style:none;margin:30px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:40px 30px}
.woocommerce ul.products li.product{width:auto!important;float:none!important;margin:0!important;text-align:center}
.woocommerce ul.products li.product a{text-decoration:none;color:inherit;display:block}
.prod_thumb{display:block;background:#f4f2ef;border-radius:4px;overflow:hidden}
.prod_thumb img{width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;padding:12px;transition:transform .4s ease}
.woocommerce ul.products li.product:hover .prod_thumb img{transform:scale(1.04)}
.woocommerce ul.products li.product h2.woocommerce-loop-product__title{font-size:16px!important;font-weight:400;margin:14px 0 4px;padding:0;color:#181b31}
.woocommerce ul.products li.product .price{color:#ff9568;font-size:16px;font-weight:600;display:block}
.woocommerce ul.products li.product a.button{display:inline-block;margin-top:10px;padding:9px 20px;border:1px solid #181b31;border-radius:2px;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;background:none;color:#181b31}
.woocommerce ul.products li.product a.button:hover{background:#ff9568;border-color:#ff9568;color:#fff}
.shop_intro{max-width:760px;margin:0 auto 10px;text-align:center}
.shop_note{font-size:13px;line-height:1.6;color:#8a8a94;margin-top:34px}
.prod_wrap{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
.prod_images{background:#f4f2ef;border-radius:4px;position:sticky;top:110px}
.prod_images img{width:100%;height:auto;display:block;padding:24px;max-height:70vh;object-fit:contain}
.opt_pick{color:#181b31;font-weight:600;letter-spacing:.6px}
.prod_images a#prod_zoom{display:block;cursor:zoom-in}
.zoom_hint{display:block;text-align:center;font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:#8a8a94;padding:0 0 14px}
.prod_top_back{margin:0 0 14px;font-size:13px;letter-spacing:1.2px;text-transform:uppercase}
.prod_top_back a{color:#8a8a94}
.prod_top_back a:hover{color:#ff9568}
.prod_desc{margin-top:34px;padding-top:26px;border-top:1px solid #eae7e2}
.prod_summary h1.product_title{font-size:32px;margin:0 0 8px;color:#181b31}
.prod_summary .price{color:#ff9568;font-size:24px;font-weight:600;margin:0 0 18px}
.prod_desc p{margin:0 0 10px}
.opt_group{margin-bottom:22px}
.opt_label{display:block;font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:#8a8a94;margin-bottom:9px}
.opts{display:flex;flex-wrap:wrap;gap:8px}
button.opt{cursor:pointer;font:inherit;font-size:13px;background:#fff;border:1px solid #d8d5d0;color:#181b31;padding:8px 14px;border-radius:2px;line-height:1;display:inline-flex;align-items:center;gap:7px}
button.opt:hover{border-color:#181b31}
button.opt.sel{border-color:#ff9568;background:#ff9568;color:#fff}
button.opt.has_sw{padding:6px 12px 6px 6px}
button.opt i{width:20px;height:20px;border-radius:50%;display:inline-block;border:1px solid rgba(0,0,0,.18)}
.qty_box{display:inline-flex;border:1px solid #d8d5d0;border-radius:2px;overflow:hidden}
.qty_box button{cursor:pointer;font:inherit;font-size:17px;width:38px;height:38px;background:#fff;border:0;color:#181b31}
.qty_box button:hover{background:#f4f2ef}
.qty_box input{width:46px;text-align:center;border:0;border-left:1px solid #d8d5d0;border-right:1px solid #d8d5d0;font:inherit;font-size:15px}
#add_to_cart{display:inline-block;cursor:pointer;font:inherit;font-size:12px;letter-spacing:1.8px;text-transform:uppercase;padding:14px 34px;border:1px solid #ff9568;background:#ff9568;color:#fff;border-radius:2px}
#add_to_cart:hover{background:#181b31;border-color:#181b31}
#add_to_cart[disabled]{opacity:.45;cursor:not-allowed}
.add_msg{min-height:22px;margin:12px 0 0;font-size:14px;color:#ff9568}
.prod_back{margin-top:30px;font-size:14px}
.prod_back a{color:#8a8a94;border-bottom:1px solid #d8d5d0}
.prod_back a:hover{color:#ff9568}
.of_h{font-size:20px;margin:34px 0 6px;color:#181b31}
.order_form{max-width:560px}
.of_row{margin:0 0 14px}
.of_row label{display:block;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#8a8a94;margin-bottom:6px}
.of_row input,.of_row textarea{width:100%;font:inherit;font-size:15px;padding:11px 13px;border:1px solid #d8d5d0;border-radius:2px;background:#fff;color:#181b31}
.of_row input:focus,.of_row textarea:focus{outline:none;border-color:#ff9568}
.of_row input.bad,.of_row textarea.bad{border-color:#d9534f;background:#fff7f7}
#of_send{display:inline-block;cursor:pointer;font:inherit;font-size:12px;letter-spacing:1.8px;text-transform:uppercase;padding:14px 34px;border:1px solid #ff9568;background:#ff9568;color:#fff;border-radius:2px}
#of_send:hover{background:#181b31;border-color:#181b31}
table.cart_table{width:100%;border-collapse:collapse;margin:20px 0 26px}
table.cart_table th{text-align:left;font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:#8a8a94;font-weight:400;padding:0 0 12px;border-bottom:1px solid #e6e3de}
table.cart_table td{padding:18px 0;border-bottom:1px solid #f0ede8;vertical-align:middle}
table.cart_table td.ct_img{width:92px}
table.cart_table td.ct_img img{width:76px;height:76px;object-fit:contain;background:#f4f2ef;border-radius:3px;padding:6px}
.ct_name{color:#181b31;display:block;margin-bottom:3px}
.ct_var{font-size:13px;color:#8a8a94}
td.ct_price,td.ct_sum{white-space:nowrap;text-align:right}
td.ct_sum{color:#ff9568;font-weight:600}
.ct_rm{cursor:pointer;border:0;background:none;color:#b9b5ae;font-size:20px;line-height:1;padding:0 0 0 14px}
.ct_rm:hover{color:#b8202c}
.cart_total{display:flex;justify-content:flex-end;align-items:baseline;gap:22px;font-size:20px;margin-bottom:24px}
.cart_total b{color:#ff9568;font-size:26px}
.cart_actions{text-align:right}
a.checkout_btn{display:inline-block;padding:15px 40px;background:#ff9568;color:#fff;border-radius:2px;font-size:12px;letter-spacing:1.8px;text-transform:uppercase}
a.checkout_btn:hover{background:#181b31}
.cart_empty{padding:40px 0;color:#8a8a94}
.cart-contents-count{font-size:11px}
/* footer payment logos + small print */
.lc_footer_sidebar .wp-block-group.is-layout-flex{display:flex;flex-wrap:wrap;align-items:center;gap:14px}
.lc_footer_sidebar .wp-block-image{margin:0}
.lc_footer_sidebar .wp-block-image img{max-width:52px;height:auto;display:block}
#footer_sidebar3 p.wp-block-paragraph{font-size:12px;line-height:1.6;color:#8a8a94}
#footer_sidebar3 #block-13 p.wp-block-paragraph{font-size:13px}
@media (max-width:900px){.prod_wrap{grid-template-columns:1fr;gap:28px}}
@media (max-width:600px){table.cart_table td.ct_img{width:66px}table.cart_table td.ct_img img{width:56px;height:56px}
 .prod_summary h1.product_title{font-size:24px}}
'''

JS = r'''
(function(){
  var KEY='fonodia_cart_v1', mem=[];
  function read(){ try{ var s=localStorage.getItem(KEY); return s?JSON.parse(s):[]; }catch(e){ return mem; } }
  function write(v){ mem=v; try{ localStorage.setItem(KEY,JSON.stringify(v)); }catch(e){} badge(); }
  function count(){ return read().reduce(function(n,i){return n+i.q;},0); }
  function money(c){ return (c/100).toFixed(2).replace('.',',')+' €'; }
  function badge(){ document.querySelectorAll('.cart-contents-count').forEach(function(el){ el.textContent=count(); }); }
  badge();

  // ---- product page
  var pp=document.querySelector('.single_product');
  if(pp){
    var sel={size:null,color:null};
    function pick(group,btn){ pp.querySelectorAll('#'+group+' .opt').forEach(function(b){b.classList.remove('sel');});
      btn.classList.add('sel'); sel[group==='sizes'?'size':'color']=btn.getAttribute('data-v');
      if(group==='colors'){ var lbl=pp.querySelector('#color_pick');
        if(lbl) lbl.textContent=btn.getAttribute('data-v');
        var vi=btn.getAttribute('data-img'), im=pp.querySelector('#prod_main_img');
        if(vi&&im){ im.src=vi; pp.dataset.pimg=vi; }
        var vf=btn.getAttribute('data-full'), zl=pp.querySelector('#prod_zoom');
        if(vf&&zl){ zl.setAttribute('href',vf); } }
      check(); }
    pp.querySelectorAll('#sizes .opt').forEach(function(b){ b.onclick=function(){pick('sizes',b);}; });
    pp.querySelectorAll('#colors .opt').forEach(function(b){ b.onclick=function(){pick('colors',b);}; });
    var one=pp.querySelectorAll('#colors .opt'); if(one.length===1) pick('colors',one[0]);
    var qty=pp.querySelector('#qty'), btnA=pp.querySelector('#add_to_cart'), msg=pp.querySelector('#add_msg');
    pp.querySelector('.qminus').onclick=function(){ qty.value=Math.max(1,(parseInt(qty.value)||1)-1); };
    pp.querySelector('.qplus').onclick=function(){ qty.value=Math.min(99,(parseInt(qty.value)||1)+1); };
    function need(){ return (pp.querySelectorAll('#sizes .opt').length&&!sel.size) || (pp.querySelectorAll('#colors .opt').length&&!sel.color); }
    function check(){ btnA.disabled=need(); }
    check();
    btnA.onclick=function(){
      if(need()) return;
      var it={id:pp.dataset.pid, name:pp.dataset.pname, price:parseInt(pp.dataset.pprice),
              img:pp.dataset.pimg, url:pp.dataset.purl, size:sel.size, color:sel.color,
              q:Math.max(1,parseInt(qty.value)||1)};
      var c=read(), k=c.find(function(x){return x.id===it.id&&x.size===it.size&&x.color===it.color;});
      if(k) k.q+=it.q; else c.push(it);
      write(c);
      msg.textContent=btnA.getAttribute('data-added')||msg.getAttribute('data-added')||'';
      msg.textContent=pp.getAttribute('data-added')||'✓';
      msg.textContent='✓ '+(document.body.lang==='en'?'Added to your basket':'Προστέθηκε στο καλάθι');
    };
  }

  // ---- order page
  var op=document.querySelector('.order_page');
  if(op){
    var oc=op.querySelector('#order_cart'), c=read(), total=0;
    if(!c.length){ oc.innerHTML='<p class="cart_empty">'+op.dataset.empty+'</p>'; }
    else{
      var rows='';
      c.forEach(function(it){
        var sum=it.price*it.q; total+=sum;
        var v=[it.size,it.color].filter(Boolean).join(' \u00b7 ');
        rows+='<tr><td class="ct_img"><img src="'+it.img+'" alt=""></td>'+
          '<td><span class="ct_name">'+it.name+'</span><span class="ct_var">'+v+'</span></td>'+
          '<td class="ct_price">'+money(it.price)+' \u00d7 '+it.q+'</td>'+
          '<td class="ct_sum">'+money(sum)+'</td></tr>';
      });
      oc.innerHTML='<table class="cart_table"><tbody>'+rows+'</tbody></table>'+
        '<div class="cart_total"><span>'+op.dataset.total+'</span><b>'+money(total)+'</b></div>';
    }
    var form=op.querySelector('#order_form'), omsg=op.querySelector('#of_msg');
    form.onsubmit=function(e){
      e.preventDefault();
      var cart=read();
      if(!cart.length){ omsg.textContent=op.dataset.empty; return; }
      var ids=['of_name','of_email','of_phone','of_addr','of_city','of_zip'], vals={}, ok=true;
      ids.forEach(function(id){
        var el=op.querySelector('#'+id), v=(el.value||'').trim();
        if(!v){ el.classList.add('bad'); ok=false; } else { el.classList.remove('bad'); }
        vals[id]=v;
      });
      if(!ok){ omsg.textContent=op.dataset.req; return; }
      vals.of_notes=(op.querySelector('#of_notes').value||'').trim();
      var lines=[], tot=0;
      cart.forEach(function(it){
        var sum=it.price*it.q; tot+=sum;
        lines.push('- '+it.name+' | '+[it.size,it.color].filter(Boolean).join(' / ')+
                   ' | x'+it.q+' | '+money(sum));
      });
      var body=[op.dataset.subject,'',lines.join('\n'),'',
        op.dataset.total+': '+money(tot),'',
        '---','',
        vals.of_name,vals.of_email,vals.of_phone,
        vals.of_addr+', '+vals.of_city+' '+vals.of_zip,
        vals.of_notes?('','',vals.of_notes):''].join('\n');
      var ep=op.dataset.endpoint;
      if(ep){
        var fd=new FormData();
        fd.append('subject',op.dataset.subject); fd.append('message',body);
        fd.append('email',vals.of_email); fd.append('name',vals.of_name);
        fetch(ep,{method:'POST',body:fd}).then(function(){ omsg.textContent=op.dataset.ok; });
        return;
      }
      var href='mailto:'+op.dataset.to+'?cc='+op.dataset.cc+
               '&subject='+encodeURIComponent(op.dataset.subject)+
               '&body='+encodeURIComponent(body);
      omsg.textContent=op.dataset.ok;
      window.location.href=href;
    };
  }

  // ---- cart page
  var cp=document.querySelector('.cart_page');
  if(cp){
    function render(){
      var c=read(), box=cp.querySelector('#cart_body');
      if(!c.length){ box.innerHTML='<p class="cart_empty">'+cp.dataset.empty+'</p>'; return; }
      var rows='', total=0;
      c.forEach(function(it,i){
        var sum=it.price*it.q; total+=sum;
        var v=[it.size,it.color].filter(Boolean).join(' · ');
        rows+='<tr><td class="ct_img"><img src="'+it.img+'" alt=""></td>'+
          '<td><span class="ct_name">'+it.name+'</span><span class="ct_var">'+v+'</span></td>'+
          '<td class="ct_price">'+money(it.price)+' × '+it.q+'</td>'+
          '<td class="ct_sum">'+money(sum)+'<button class="ct_rm" data-i="'+i+'" title="'+cp.dataset.remove+'">×</button></td></tr>';
      });
      box.innerHTML='<table class="cart_table"><tbody>'+rows+'</tbody></table>'+
        '<div class="cart_total"><span>'+cp.dataset.total+'</span><b>'+money(total)+'</b></div>'+
        '<div class="cart_actions"><a class="checkout_btn" href="'+cp.dataset.wc+'">'+cp.dataset.checkout+'</a></div>';
      box.querySelectorAll('.ct_rm').forEach(function(b){ b.onclick=function(){ var c=read(); c.splice(parseInt(b.dataset.i),1); write(c); render(); }; });
    }
    render();
  }
})();
'''
