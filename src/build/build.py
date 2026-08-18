# -*- coding: utf-8 -*-
"""Build the static ΦΩΝΩΔΙΑ clone into /home/claude/fonodia/site-build."""
import sys, os, re, json, shutil, copy, urllib.parse as up
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import shop

os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT + '/assets', exist_ok=True)

# ====================================================================== ROUTES
# original URL path (unquoted, with trailing slash) -> local directory (relative to site root)
ROUTES = {}
def route(orig, local):
    ROUTES[up.unquote(orig).rstrip('/') + '/'] = local.strip('/')

route('/', '')
route('/en/homepage/', 'en')
route('/μέλη/', 'μέλη');                         route('/en/members/', 'en/members')
route('/events/', 'events');                     route('/en/performances/', 'en/performances')
route('/photo_album_category/concert/', 'gallery'); route('/gallery/', 'gallery'); route('/en/photos/', 'en/photos')
route('/performs-in-action/', 'performs-in-action'); route('/en/videos/', 'en/videos')
route('/about/', 'about');                       route('/en/a-few-words-about-the-ensemble/', 'en/a-few-words-about-the-ensemble')
route('/σχετικά-με-το-σύνολο/', 'σχετικά-με-το-σύνολο'); route('/en/about-the-ensemble/', 'en/about-the-ensemble')
route('/cf-83-cf-85-cf-83-cf-84-ce-b1-cf-84-ce-b9-ce-ba-ce-ad-cf-82-ce-b5-cf-80-ce-b9-cf-83-cf-84-ce-bf-ce-bb-ce-ad-cf-82/', 'είπαν-για-εμάς'); route('/en/testimonials/', 'en/testimonials')
route('/sponsor-us/', 'sponsor-us');             route('/en/support-our-projects/', 'en/support-our-projects')
route('/προϊόντα/', 'προϊόντα');                  route('/en/products/', 'en/products')
route('/merch/', 'merch');                       route('/en/store/', 'en/store')
route('/contact-2/', 'contact-2');               route('/en/contact/', 'en/contact')
route('/όροι-χρήσης/', 'όροι-χρήσης');            route('/en/terms-of-use/', 'en/terms-of-use')
route('/πολιτική-απορρήτου/', 'πολιτική-απορρήτου'); route('/en/5015-2/', 'en/privacy-policy')
route('/blog/', 'blog'); route('/en/blog/', 'en/blog')
route('/el/events/', 'events'); route('/el/about/', 'about'); route('/el/', '')
route('/cart/', 'cart'); route('/en/cart/', 'en/cart'); route('/en/checkout/', 'en/cart')

def local_href(from_dir, target, xlate=None):
    """Convert an absolute site URL (or route key) into a relative href from page at from_dir.
    xlate: optional {greek_local_dir: english_local_dir} so an English page keeps you in English."""
    if target is None:
        return '#'
    t = target
    if t.startswith(SITE):
        t = t[len(SITE):]
    if t.startswith('http'):
        return target                     # external
    if t.startswith('#') or t == '':
        return t or '#'
    key = up.unquote(t.split('#')[0].split('?')[0]).rstrip('/') + '/'
    if key not in ROUTES:
        return target                     # unknown → keep original (still works while WP lives)
    dest = ROUTES[key]
    if xlate:
        dest = xlate.get(dest, dest)
    return rel(from_dir, dest)

def rel(from_dir, dest_dir):
    from_parts = [p for p in from_dir.split('/') if p]
    up_ = '../' * len(from_parts)
    if dest_dir == '':
        return (up_ or './') + 'index.html'
    return up_ + dest_dir + '/index.html'

def dirprefix(from_dir):
    n = len([x for x in from_dir.split('/') if x])
    return '../' * n

def asset(from_dir, path):
    return dirprefix(from_dir) + path

# ====================================================================== CSS
def build_css():
    order = ['bundle-002.css', 'bundle-004-woo-mobile.css', 'bundle-003-woo.css',
             'fonts-garamond.css', 'bundle-main.css', 'fonts-roboto.css']
    css = ''
    for f in order:
        c = open(SAVED + '/' + f, encoding='utf-8', errors='replace').read()
        if f == 'bundle-004-woo-mobile.css':
            c = '@media only screen and (max-width:768px){' + c + '}'
        css += '\n/* ==== %s ==== */\n' % f + c
    # inline theme styles from the saved pages (colours, vc custom css, wp custom css)
    seen = set(); extra = ''
    for f in ['home.htm', 'members.htm', 'pnoi.htm', 'video.htm', 'concert-gallery.htm', 'contact.htm']:
        h = open(SAVED + '/' + f, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<style([^>]*)>(.*?)</style>', h, re.S):
            a, b = m.group(1), m.group(2)
            if 'jetpack-boost-critical' in a or 'nfd-wonder' in a or 'wp-block' in a or 'global-styles' in a or 'core-block' in a or 'wp-emoji' in a or 'wp-img-auto' in a or 'classic-theme' in a or 'woocommerce-inline' in a or 'woo-variation' in a:
                continue
            key = b.strip()
            if key in seen or not key:
                continue
            seen.add(key)
            extra += '\n/* inline %s %s */\n' % (f, a.strip()[:40]) + b
    css += '\n/* ==== inline theme styles ==== */\n' + extra
    # asset paths
    css = css.replace('/wp-content/themes/slide/assets/font-awesome-5.0.8/css/../webfonts/', 'webfonts/')
    css = re.sub(r'url\((["\']?)/wp-content/', lambda m: 'url(%s%s/wp-content/' % (m.group(1), SITE), css)
    # our overrides – things WordPress/theme JS did at runtime
    css += r'''
/* ==== static-site overrides (replacing theme JS behaviour) ==== */
nav.classic_menu_left ul.menu>li{position:relative}
nav.classic_menu_left ul.sub-menu{display:none;margin-top:0!important;top:100%;left:0;min-width:220px;z-index:50}
nav.classic_menu_left ul.sub-menu:before{content:"";position:absolute;left:0;right:0;top:-14px;height:14px}
nav.classic_menu_left li.menu-item-has-children:hover>ul.sub-menu{display:block}
nav.classic_menu_left ul.sub-menu li{display:block;float:none;white-space:nowrap}
#lc_page_header ul.sub-menu li a{color:#050505!important}
#lc_swp_content h1,#lc_swp_content h2,#lc_swp_content h3,#lc_swp_content h4,#lc_swp_content h5,#heading_area h1,#heading_area h2,#lc_swp_content .artist_title,#lc_swp_content .video_title,#lc_swp_content .lc_share_item_text,#lc_swp_content a.lc_share_item,#lc_swp_content .lc_event_entry,#lc_swp_content .swp_vc_column_title,#lc_swp_content .gallery_item_details h2{color:#181b31}
#lc_swp_content .vc_row.white_on_black h1,#lc_swp_content .vc_row.white_on_black h2,#lc_swp_content .vc_row.white_on_black h3,#lc_swp_content .vc_gitem-zone h3,#lc_swp_content .vc_gitem-zone div,#hero h1,#hero p{color:#fff}
.canvas_image{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;background-size:cover;background-position:center}
.canvas_overlay{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0}
#lc_swp_wrapper{position:relative;z-index:1;background:transparent}
body{background-color:transparent!important}
html{background:#f9f9f9}
#footer_sidebars{position:relative;overflow:hidden}
#footer_sidebars .footer_widget_overlay{position:absolute;inset:0;z-index:0}
#footer_sidebars_inner{position:relative;z-index:1}
#heading_area{position:relative}
#heading_area>.lc_swp_overlay{position:absolute;inset:0;z-index:0}
#heading_area .heading_content_container{position:relative;z-index:1}
#heading_area.white_on_black h1,#heading_area.white_on_black h2{color:#fff}
#lc_swp_content .page_text_white,#lc_swp_content .page_text_white p,#lc_swp_content .page_text_white strong{color:#fff}
/* επικοινωνία: το email να διαβάζεται πάνω στη φωτογραφία */
.has_canvas_image .contact_address_entry,.has_canvas_image .contact_address_data,.has_canvas_image .before_contact_entry{color:#fff!important;font-weight:600;text-shadow:0 1px 8px rgba(0,0,0,.85),0 0 2px rgba(0,0,0,.9)}
.lc_button a{color:inherit}
.eventlist_day,.eventlist_month,.event_list_title,.event_buy_btn.lc_js_link{color:#181b31}
.event_list_entry.event_venue,.event_list_entry.event_time{overflow:visible;line-height:1.4;height:auto}
.event_list_location{white-space:normal}
.single_event_list .event_list_entry{height:auto;min-height:60px}
.evnt_list_title_loc,.event_list_title{white-space:normal;line-height:1.3}
.event_list_entry.event_title_img{width:36%!important}
#lc_swp_content .lc_button{color:#181b31;border-color:#181b31}
#lc_swp_content .lc_button:hover,#lc_swp_content .lc_button.lc_button_fill{color:#fff}
.photo_gallery_overlay{opacity:0;transition:opacity .3s}.photo_gallery_item:hover .photo_gallery_overlay{opacity:.75}
.gallery_item_details{position:absolute;left:0;right:0;bottom:20px;text-align:center;z-index:2}

#lc_swp_wrapper{opacity:1!important}
.single_artist_item,.single_video_item,.photo_gallery_item{opacity:1!important}
.single_artist_item{margin-bottom:98px}
.artist_img_container{aspect-ratio:1/1;height:auto!important}
.video_image_container{aspect-ratio:16/9;height:auto!important}
.lc_swp_background_image{background-position:center center;background-repeat:no-repeat;background-size:cover}
.lc_swp_overlay{position:absolute}
.vc_row[data-vc-full-width]{position:relative;overflow:hidden;width:100vw;left:50%;margin-left:-50vw!important;margin-right:0!important;padding-left:0;padding-right:0}
.vc_row[data-vc-full-width][data-vc-stretch-content] > .vc_column_container{padding-left:0;padding-right:0}
.vc_row.vc_row-flex{display:flex;flex-wrap:wrap}
.vc_row.vc_row-flex>.vc_column_container{display:flex}
.vc_row.vc_row-flex>.vc_column_container>.vc_column-inner{display:flex;flex-direction:column;flex-grow:1;flex-basis:100%}
.vc_row.vc_row-o-content-middle>.vc_column_container>.vc_column-inner{justify-content:center}
.vc_row.vc_row-o-content-top>.vc_column_container>.vc_column-inner{justify-content:flex-start}
.vc_grid .vc_pageable-slide-wrapper{position:relative;height:auto!important;display:flex!important;flex-wrap:wrap;align-items:flex-start}
.vc_grid .vc_grid-item{position:relative!important;left:auto!important;top:auto!important;float:left;padding-left:15px;padding-right:15px;margin-bottom:30px}
.vc_grid .vc_grid-item.vc_visible-item{visibility:visible;opacity:1}
.vc_gitem-zone-a.vc-gitem-zone-height-mode-auto:before{content:"";display:block;padding-top:133%}
.vc_gitem-zone-a{background-size:cover;background-position:center;position:relative}
.vc_gitem-zone-a img.vc_gitem-zone-img{display:none}
.vc_gitem-zone-a .vc_gitem-zone-mini{position:absolute;inset:0}
.vc_gitem-zone-b .vc_gitem-zone-mini{position:relative}
.vc_gitem-zone-b .vc_gitem-col{padding:14px 15px}
@media(min-width:768px){.vc_grid .vc_grid-item.vc_col-sm-4{width:33.3333%!important}.vc_grid .vc_grid-item.vc_col-sm-6{width:50%!important}.vc_grid .vc_grid-item.vc_col-sm-2{width:16.6666%!important}}
.wpb_animate_when_almost_visible{opacity:1!important;filter:none!important;animation:none!important}
.vc_gitem-zone-b{position:absolute;inset:0;opacity:0;transition:opacity .35s ease;display:flex;align-items:center;background:rgba(0,0,0,.35)}
.vc_gitem-animated-block:hover .vc_gitem-zone-b{opacity:1}
.vc_gitem-zone-b .vc_gitem-zone-mini{position:relative;width:100%}
.vc_gitem-zone-b .vc_gitem_row{width:100%;margin:0}
.vc_gitem_row.vc_gitem-row-position-middle{display:flex}
.vc_gitem-zone-a .vc_gitem-zone-a .vc_gitem-zone-mini{position:absolute;inset:0}
.vc_gitem-zone-b .vc_gitem-zone-mini{position:relative}
.vc_gitem-zone-b .vc_gitem-col{padding:14px 15px}
@media(min-width:768px){.vc_grid .vc_grid-item.vc_col-sm-4{width:33.3333%!important}.vc_grid .vc_grid-item.vc_col-sm-6{width:50%!important}.vc_grid .vc_grid-item.vc_col-sm-2{width:16.6666%!important}}
.wpb_animate_when_almost_visible{opacity:1!important;filter:none!important;animation:none!important}
.vc_gitem-animated-block{position:relative}
.vc_gitem-zone .vc-zone-link{position:absolute;inset:0;z-index:2}
#hero{min-height:80vh;display:flex;align-items:center;background:#111}
#hero .hero-title h1{font-size:50px;line-height:1.2;color:#fff;margin:0 0 5px}
#hero .wpb_column{width:100%}
#hero .hero-title{max-width:640px}
#hero .hero-title p{color:#fff;font-size:18px;letter-spacing:.05em}
#hero .swp_video_btn_scd{margin-top:35px}
#hero video.hero-video{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:0}
#hero .wpb_wrapper,#hero .vc_column-inner{position:relative;z-index:1}
#hero .vc_column_container{width:100%}
.header_inner.lc_wide_menu.transparent{background-color:transparent!important}
header#lc_page_header.cust_page_menu_style .header_inner.lc_wide_menu{background-color:rgba(0,0,0,0)!important}
header#lc_page_header.cust_page_menu_style ul.menu>li>a,header#lc_page_header.cust_page_menu_style .classic_header_icon,header#lc_page_header.cust_page_menu_style .classic_header_icon a{color:#fff!important}
header#lc_page_header.cust_page_menu_style .global_logo{display:none}
header#lc_page_header.cust_page_menu_style .cust_page_logo{display:inline-block}
header#lc_page_header:not(.cust_page_menu_style) .cust_page_logo{display:none}
header#lc_page_header.sticky_enabled{position:fixed;top:0;background:#fff;box-shadow:0 1px 8px rgba(0,0,0,.08)}
header#lc_page_header.sticky_enabled .header_inner.lc_wide_menu{background-color:#fff!important;height:70px}
header#lc_page_header.sticky_enabled ul.menu>li>a,header#lc_page_header.sticky_enabled .classic_header_icon,header#lc_page_header.sticky_enabled .classic_header_icon a{color:#000!important}
header#lc_page_header.sticky_enabled .global_logo{display:inline-block!important}
header#lc_page_header.sticky_enabled .cust_page_logo{display:none!important}
#logo img{max-height:70px;width:auto}
.mobile_navigation_container.open{display:block}
.mobile_navigation ul.sub-menu{display:block}
.mobile_navigation ul li a{display:block}
.mobile_navigation ul li.menu-item-has-children>ul.sub-menu{padding-left:20px}
.hero-video-poster{position:absolute;inset:0;background:#0d0d0d}
.hero-body-hidden{display:none}
.swp_video_modal{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;display:none;align-items:center;justify-content:center}
.swp_video_modal.open{display:flex}
.swp_video_modal iframe{width:min(90vw,1100px);aspect-ratio:16/9;border:0}
.swp_video_modal .close{position:absolute;top:20px;right:30px;color:#fff;font-size:34px;cursor:pointer;line-height:1}
.evt_body_html div[dir="auto"]{margin:0 0 4px}
.evt_body_html .html-span,.evt_body_html span[class*="x1"]{display:inline}
.evt_body_html img{max-width:100%;height:auto}
.event_right img{max-width:100%;height:auto}
.event_left,.event_right{float:left}
.swp_gallery_item_thumbnail{width:100%;height:auto;display:block}
.photo_gallery_item{overflow:hidden}
.artist_bio_wrap{max-width:900px;margin:0 auto}
.artist_single_img{max-width:420px;margin:0 auto 30px}
.artist_single_img img{width:100%;height:auto;display:block}
.blog_list_item{margin-bottom:60px}
.blog_list_item img{max-width:100%;height:auto}
.woocommerce ul.products li.product img{width:100%;height:auto}
.wc-block-grid__product-image img{width:100%;height:auto}
.products_grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:30px}
.products_grid a{text-decoration:none;color:inherit;text-align:center}
.products_grid img{width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;background:#f6f6f6}
.products_grid .pn{display:block;margin-top:10px}
.products_grid .pp{display:block;font-weight:600;color:#ff9568}
.products_grid .lc_button{margin-top:6px}
.testimonial_block{margin-bottom:50px}
.testimonial_block h3{margin-bottom:10px}
.support_iban{background:#f5f5f5;padding:20px 26px;border-left:3px solid #ff9568;margin:20px 0}
.lc_content_full.page_text{padding-top:20px;padding-bottom:80px}
.about_two{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start}
.about_two h3{font-weight:400;font-size:26px;margin:0 0 30px}
.about_two img{width:100%;height:auto;display:block}
@media(max-width:900px){.about_two{grid-template-columns:1fr;gap:20px}}
.tes_name{margin:34px 0 8px}.tes_name strong{color:#181b31}
#heading_area.events_heading{background:#f1f1e0}
.blog_grid{display:grid;grid-template-columns:1fr 1fr;gap:60px 80px;max-width:900px;margin:0 auto}
@media(max-width:800px){.blog_grid{grid-template-columns:1fr}}
.blog_date{color:#ff9568;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 10px}
.blog_list_item h3{font-size:22px;line-height:1.3;margin:0 0 14px}
.blog_more{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#181b31}
.blog_more i{margin-left:6px;font-size:10px}
@media (max-width:1199px){header#lc_page_header .header_inner.lc_mobile_menu{display:block!important;background:#fff}
 header#lc_page_header.cust_page_menu_style .header_inner.lc_mobile_menu{background:#fff}
 .single_artist_item{width:48%}.single_artist_item.has_right_padding{margin-right:4%}.single_artist_item:nth-child(2n){margin-right:0}
 .event_left,.event_right{width:100%!important;float:none}
}
@media (max-width:767px){.vc_grid .vc_grid-item{width:100%!important}}
@media (max-width:768px){#hero{min-height:70vh}#hero .hero-title h1{font-size:34px}.events .swp_slide_btn_container{text-align:left;margin:10px 0 20px}.events .swp_slide_btn_container a{color:#181b31!important;border:1px solid #181b31;padding:8px 14px;display:inline-block}.single_video_item{width:100%!important;margin-right:0!important}.photo_gallery_item{width:100%!important;margin-right:0!important;margin-bottom:20px}
 .single_event_list .event_list_entry{float:none;display:block;height:auto;width:100%!important;margin-bottom:8px}}
'''
    css += '\n' + shop.CSS
    css = drop_wp_assets(css)
    open(OUT + '/assets/site.css', 'w', encoding='utf-8').write(css)
    print('css bytes', len(css))


def drop_wp_assets(css):
    """Βγάζει από το φύλλο στυλ ό,τι ζητούσε ακόμα αρχεία από το WordPress.
    Είναι γραμματοσειρές εικονιδίων και εικονίδια παλαιών προσθέτων που καμία
    σελίδα μας δεν χρησιμοποιεί — έτσι η σελίδα μένει καθαρή και ανεξάρτητη."""
    before = css.count('phonodiavocalensemble.com/wp-content')
    # 1) ολόκληρα τα @font-face που δείχνουν στο WordPress
    out, i = [], 0
    for m in re.finditer(r'@font-face\s*\{[^}]*\}', css):
        if 'phonodiavocalensemble.com/wp-content' in m.group(0):
            out.append(css[i:m.start()])
            i = m.end()
    out.append(css[i:])
    css = ''.join(out)
    # 2) όσες μεμονωμένες url(...) απέμειναν
    css = re.sub(r'url\(\s*[\'"]?https://phonodiavocalensemble\.com/wp-content[^)]*\)',
                 'none', css)
    print('drop_wp_assets: %d αναφορές WordPress -> %d'
          % (before, css.count('phonodiavocalensemble.com/wp-content')))
    return css

# ====================================================================== JS
JS = r'''
(function(){
  var hdr=document.getElementById('lc_page_header');
  var isCust=hdr&&hdr.classList.contains('cust_page_menu_style');
  function onScroll(){ if(!hdr) return; if(window.scrollY>120){hdr.classList.add('sticky_enabled');} else {hdr.classList.remove('sticky_enabled');} }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  // mobile menu
  var burger=document.querySelector('.hmb_menu'); var mnav=document.querySelector('.mobile_navigation_container');
  if(burger&&mnav){burger.addEventListener('click',function(){mnav.classList.toggle('open');});}
  // js links
  document.querySelectorAll('.lc_js_link[data-href]').forEach(function(el){
    el.addEventListener('click',function(e){var h=el.getAttribute('data-href'); if(!h||h=='#') return; if(el.getAttribute('data-target')=='_blank'){window.open(h,'_blank');} else {window.location.href=h;}});
  });
  // hero video popup
  document.querySelectorAll('.video_play_btn_scd[data-vid]').forEach(function(btn){
    btn.style.cursor='pointer'; var wrap=btn.closest('.swp_video_btn_scd')||btn; wrap.style.cursor='pointer';
    wrap.addEventListener('click',function(){
      var id=btn.getAttribute('data-vid');
      if(location.protocol==='file:'){ window.open('https://www.youtube.com/watch?v='+id,'_blank'); return; }
      var m=document.getElementById('swp_video_modal');
      if(!m){m=document.createElement('div');m.id='swp_video_modal';m.className='swp_video_modal';m.innerHTML='<span class="close">&times;</span><iframe allow="autoplay; fullscreen" allowfullscreen></iframe>';document.body.appendChild(m);
        m.querySelector('.close').addEventListener('click',function(){m.classList.remove('open');m.querySelector('iframe').src='';});
        m.addEventListener('click',function(e){if(e.target===m){m.classList.remove('open');m.querySelector('iframe').src='';}});}
      m.querySelector('iframe').src='https://www.youtube.com/embed/'+id+'?autoplay=1&rel=0';
      m.classList.add('open');
    });
  });
  // gallery lightbox (simple)
  document.querySelectorAll('a[data-lightbox]').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();
      var m=document.getElementById('swp_img_modal');
      if(!m){m=document.createElement('div');m.id='swp_img_modal';m.className='swp_video_modal';m.innerHTML='<span class="close">&times;</span><img style="max-width:92vw;max-height:90vh;object-fit:contain">';document.body.appendChild(m);
        m.querySelector('.close').addEventListener('click',function(){m.classList.remove('open');});
        m.addEventListener('click',function(e){if(e.target===m){m.classList.remove('open');}});}
      m.querySelector('img').src=a.getAttribute('href'); m.classList.add('open');
    });
  });
  // hero video autoplay
  var v=document.querySelector('#hero video.hero-video'); if(v){v.muted=true;v.play&&v.play().catch(function(){});}
})();
'''
open(OUT + '/assets/site.js', 'w', encoding='utf-8').write(JS + shop.JS)

# ====================================================================== SHELLS
home_doc = parse(SAVED + '/home.htm')
inner_doc = parse(SAVED + '/pnoi.htm')

def prep(el):
    el = copy.deepcopy(el)
    strip_junk(el)
    fix_refs(el)
    return el

HEADER_HOME = prep(home_doc.get_element_by_id('lc_page_header'))
HEADER_INNER = prep(inner_doc.get_element_by_id('lc_page_header'))
FOOTER_EL = prep(home_doc.get_element_by_id('footer_sidebars'))
COPY_EL = prep(home_doc.xpath('//div[contains(@class,"lc_copy_area")]')[0])

# remove the tiny data-uri submenu arrow imgs? keep (theme). Remove inline colour styles on menu links (theme JS added them)
for hd in (HEADER_HOME, HEADER_INNER):
    for ul in hd.xpath('.//ul[contains(@class,"swp_show_submenu")]'):
        ul.set('class', 'sub-menu')
    for a in hd.xpath('.//a[@style]'):
        del a.attrib['style']
    for d in hd.xpath('.//*[@style]'):
        del d.attrib['style']

# Το e-shop υπάρχει στη ζωντανή σελίδα αλλά λείπει από το μενού της — μπαίνει εδώ,
# με τη δική της ονομασία «Καλλιτεχνικά αναμνηστικά», πριν από την Επικοινωνία.
SHOP_LABEL = 'Κατάστημα'
for hd in (HEADER_HOME, HEADER_INNER):
    for ul in hd.xpath('.//ul[contains(@class,"menu")]'):
        if ul.getparent() is not None and 'sub-menu' in (ul.get('class') or ''):
            continue
        if ul.xpath('./li[contains(@class,"lang-item")]'):
            if ul.xpath('./li/a[normalize-space(text())="%s"]' % SHOP_LABEL):
                continue
            lang_li = ul.xpath('./li[contains(@class,"lang-item")]')[0]
            li = etree.Element('li')
            li.set('class', 'menu-item menu-item-type-post_type menu-item-object-page menu-item-shop')
            a = etree.SubElement(li, 'a')
            a.set('href', SITE + '/προϊόντα/')
            a.text = SHOP_LABEL
            lang_li.addprevious(li)

# 17 Αυγ 2026: το Blog κρύβεται από το μενού (οι σελίδες παραμένουν έτοιμες)
HIDE_MENU = {'Blog'}
for hd in (HEADER_HOME, HEADER_INNER):
    for li in hd.xpath('.//ul[contains(@class,"menu")]/li'):
        if (li.xpath('normalize-space(./a)') or '') in HIDE_MENU:
            li.getparent().remove(li)

# EN menu translation table: EL label -> (EN label, EN href)
EN_MENU = {
    'Το Σύνολο': ('The Ensemble', SITE + '/en/about-the-ensemble/'),
    'Λίγα λόγια για το σύνολο': ('A few words about the ensemble', SITE + '/en/a-few-words-about-the-ensemble/'),
    'Βιογραφικό': ('Biography', SITE + '/en/about-the-ensemble/'),
    'Είπαν για εμάς': ('Testimonials', SITE + '/en/testimonials/'),
    'Εμφανίσεις': ('Performances', SITE + '/en/performances/'),
    'Μέλη': ('Members', SITE + '/en/members/'),
    'Blog': ('Blog', SITE + '/en/blog/'),
    'Media': ('Media', '#'),
    'Φωτογραφικό Υλικό': ('Photos', SITE + '/en/photos/'),
    'Μαγνητοσκοπήσεις': ('Videos', SITE + '/en/videos/'),
    'Κατάστημα': ('Shop', SITE + '/en/products/'),
    'Επικοινωνία': ('Contact', SITE + '/en/contact/'),
    'English': ('Ελληνικά', SITE + '/'),
}
FOOTER_EN = {
    'Η Φωνωδία λειτουργεί υπό το Κέντρο Φωνητικής Τέχνης Κρήτης στο Ηράκλειο της Κρήτης – μιας Αστικής Μη-Κερδοσκοπικής Εταιρίας που στόχο έχει την ανάδειξη της μουσικής τέχνης στο νησί, μέσα από τη φωνητική και το χορωδιακό τραγούδι.':
    'Phonodia (Fónodia) operates under the Cretan Center of Vocal Arts in Herakleion, Crete – an Urban Non-Profit Organization with the aim of promoting the art of music through vocal performance and choral works.',
}

def localise(el, from_dir, lang, alt_url=None):
    """Rewrite hrefs to local relative paths; translate menu when lang=='en'."""
    # language switcher (Polylang item): swap flag + target
    for li in el.xpath('.//li[contains(@class,"lang-item")]'):
        for a in li.xpath('.//a'):
            if lang == 'en':
                a.set('href', alt_url or rel(from_dir, ''))
                a.set('lang', 'el'); a.set('hreflang', 'el')
                a.set('title', 'Ελληνικά')
                for img in a.xpath('.//img'):
                    img.set('src', FLAG_EL); img.set('alt', 'Ελληνικά')
            else:
                a.set('href', alt_url or rel(from_dir, 'en'))
                a.set('title', 'English')
            a.set('data-langswitch', '1')
    for a in el.xpath('.//a[contains(@class,"cart-contents")]'):
        a.set('href', SITE + ('/en/cart/' if lang == 'en' else '/cart/'))
    for a in el.xpath('.//a[@href]'):
        if a.get('data-langswitch'):
            del a.attrib['data-langswitch']
            continue
        h = a.get('href')
        if lang == 'en':
            label = (a.text_content() or '').strip()
            if label in EN_MENU:
                en_label, en_href = EN_MENU[label]
                # replace text but keep child imgs (flag)
                if a.text and a.text.strip():
                    a.text = en_label
                else:
                    for t in a.itertext():
                        pass
                    # text may be in tail of an img
                    for ch in a:
                        if ch.tail and ch.tail.strip():
                            ch.tail = en_label
                h = en_href
                if h == '#':
                    a.set('href', '#'); continue
        a.set('href', local_href(from_dir, h))
    for d in el.xpath('.//*[@data-href]'):
        d.set('data-href', local_href(from_dir, d.get('data-href')))
    if lang == 'en':
        for a in el.xpath('.//a[contains(@class,"logo")]|.//*[contains(@id,"logo")]//a'):
            a.set('href', rel(from_dir, 'en'))
    if lang == 'en':
        for p in el.xpath('.//p|.//div|.//span|.//h2|.//a'):
            if p.text and p.text.strip() in FOOTER_EN:
                p.text = FOOTER_EN[p.text.strip()]
        for a in el.xpath('.//a'):
            t = (a.text or '').strip()
            if t == 'Επικοινωνία - Contact': a.text = 'Contact'
            if t == 'Όροι Χρήσης - Terms of Use': a.text = 'Terms of Use'
            if t == 'Πολιτική Απορρήτου - Privacy Policy': a.text = 'Privacy Policy'
            if t == 'Επικοινωνία': a.text = 'Contact'
    return el

FLAG_EL = open(os.path.dirname(__file__) + '/flag_el.txt').read().strip()

HEAD_TPL = '''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="{site}/wp-content/uploads/2025/04/cropped-CleanShot-2025-04-25-at-16.55.17@2x-32x32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{site}/wp-content/uploads/2025/04/cropped-CleanShot-2025-04-25-at-16.55.17@2x-180x180.png">
<link rel="stylesheet" href="{css}">
{alt}
</head>
<body class="{bodyclass}">
<div id="lc_swp_wrapper">
'''
TAIL_TPL = '''
</div>
<script src="{js}"></script>
</body>
</html>
'''

def write_page(local_dir, title, content_html, lang='el', home=False, bodyclass='', heading_html='', alt_url=None, canvas_img=None):
    d = OUT + '/' + local_dir if local_dir else OUT
    os.makedirs(d, exist_ok=True)
    # a relative folder link opens a directory listing when browsing from disk → point at the file
    if alt_url and '://' not in alt_url and alt_url.endswith('/'):
        alt_url += 'index.html'
    hdr = copy.deepcopy(HEADER_HOME if home else HEADER_INNER)
    hdr = localise(hdr, local_dir, lang, alt_url)
    ftr = localise(copy.deepcopy(FOOTER_EL), local_dir, lang)
    cp = localise(copy.deepcopy(COPY_EL), local_dir, lang)
    bc = ('home ' if home else '') + 'wp-theme-slide theme-slide woocommerce-js wpb-js-composer js-comp-ver-8.3 vc_responsive custom-background ' + bodyclass
    alt = ''
    if alt_url:
        alt = '<link rel="alternate" hreflang="%s" href="%s">' % ('en' if lang == 'el' else 'el', alt_url)
    page = HEAD_TPL.format(lang=lang, title=esc(title), site=SITE, css=asset(local_dir, 'assets/site.css'), alt=alt, bodyclass=bc)
    canvas = ''
    if canvas_img:
        # percent-encode non-ASCII filenames so url() stays valid everywhere
        _sch, _rest = canvas_img.split('://', 1)
        _host, _path = _rest.split('/', 1)
        canvas_img = _sch + '://' + _host + '/' + up.quote(_path)
        bc += ' has_canvas_image'
        canvas = '<div class="canvas_image lc_swp_background_image" style="background-image:url(\'%s\')"></div><div class="canvas_overlay lc_swp_bg_color" style="background-color:rgba(0,0,0,0)"></div>' % canvas_img
        page = page.replace('class="%s"' % (bc.replace(' has_canvas_image','')), 'class="%s"' % bc)
    else:
        canvas = '<div class="canvas_overlay lc_swp_bg_color" style="background-color:#ffffff"></div>'
    page += tostr(hdr) + '\n' + heading_html + '\n<div id="lc_swp_content">\n' + content_html + '\n</div>\n' + tostr(ftr) + tostr(cp)
    page += TAIL_TPL.format(js=asset(local_dir, 'assets/site.js')).replace('</div>\n<script', '</div>\n' + canvas + '\n<script', 1)
    open(d + '/index.html', 'w', encoding='utf-8').write(page)
    return d + '/index.html'

def heading_area(title, subtitle=None, cls='settings_default'):
    sub = ('<div class="heading_area_subtitle title_centered swp_page_title"><h2 class="title_centered swp_page_title">%s</h2></div>' % esc(subtitle)) if subtitle else ''
    return ('''<div id="heading_area" class="%s">''' % cls) + '''
<div class="heading_content_container lc_swp_boxed title_centered swp_page_title">
<div class="heading_titles_container">%s
<div class="heading_area_title title_centered swp_page_title"><h1 class="title_centered swp_page_title"> %s </h1></div>
</div></div></div>''' % (sub, esc(title))

def content_of(doc):
    c = prep(doc.get_element_by_id('lc_swp_content'))
    inner = ''.join(tostr(ch) if isinstance(ch.tag, str) else '' for ch in c)
    return (c.text or '') + inner

def heading_of(doc):
    try:
        h = doc.get_element_by_id('heading_area')
    except KeyError:
        return ''
    return tostr(prep(h))

# Ελληνικός τοπικός φάκελος -> αγγλικός δίδυμός του. Όσο μένεις στα αγγλικά, μένεις στα αγγλικά.
# Αγγλικοί τίτλοι, εγκεκριμένοι από τον Ιωάννη 16 Αυγ 2026
ALBUM_EN = {
    'Οι σπόροι της Σμύρνης': 'The Seeds of Smyrna',
    'Λιλιπούπολη': 'Lilipoupoli',
    'Η συνέλευση των ζώων': 'The Assembly of the Animals',
    'Άγιος Τίτος': 'Agios Titos',
    'Η νέα γη': 'The New Earth',
}
POST_EN = {
    'Η ΦΩΝΩΔΙΑ ταξιδεύει στην Ιαπωνία!': 'PHONODIA travels to Japan!',
}
POST_EN_THEATRO = '“At the Theatre”: Recital and Solo Concert by the PHONODIA Vocal Ensemble at the Hellenic Mediterranean University'

EN_XLATE = {
    'performs-in-action': 'en/videos',
    'gallery': 'en/photos',
    'blog': 'en/blog',
    'blog/στο-θέατρο': 'en/blog/στο-θέατρο',
    'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία': 'en/blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία',
}

def relink(html_str, from_dir, xlate=None):
    """Rewrite absolute site links inside an HTML string to local relative ones where routed."""
    frag = LH.fragment_fromstring('<div>' + html_str + '</div>')
    for a in frag.xpath('.//a[@href]'):
        a.set('href', local_href(from_dir, a.get('href'), xlate))
    for d in frag.xpath('.//*[@data-href]'):
        d.set('data-href', local_href(from_dir, d.get('data-href'), xlate))
    out = (frag.text or '') + ''.join(tostr(ch) for ch in frag)
    return out

# ====================================================================== DATA
events = load_json(CLONE + '/data-events.json')
videos = load_json(CLONE + '/data-videos.json')
albums = load_json(CLONE + '/data-albums.json')
members = load_json(CLONE + '/data-members.json')
pages = {r['url']: r for r in load_json(CLONE + '/harvest-pages.json')}
tes_el = load_json(CLONE + '/testimonials-el.json')
harvest_events = {r['url']: r for r in load_json(CLONE + '/harvest-events.json')
                 if (r.get('title') or '').strip() != 'Dummy Album Format'}

# 17 Αυγ 2026 — νέα συναυλία που έδωσε ο Ιωάννης Ιδομενέως.
# 18 Αυγ 2026 — μπήκε η κανονική αφίσα των Αρχανών, εγκεκριμένη από τον Ιωάννη Ιδομενέως.
AFISA_ARXANES = '/img/afisa-pnoi-arxanes-2026.webp'
AFISA_SHA1 = '9e96f2546dc60edb6da69ac3ff8d7c276965fc41'
# τα τέσσερα κομμάτια της αφίσας, όπως ανέβηκαν στον φάκελο της γέφυρας στο Drive
AFISA_DRIVE = (('1jLAoGzWCq1EvBUUa-X2vu4pkj7xiCf8a', 'ad6fc09a5d1c'),
               ('1v7Mo_osSatVQSVHIRDZOQrseo4qy-r3Z', '3cc07e0762c7'),
               ('1LyO0LCpZDlRHkGwi-PpARctlLYHbSMVC', 'a13cab0b6124'),
               ('1qYFwCKqftjmmB9wdZDWFrda5F-q-rupT', 'e258a4016ee2'))
NEW_EVENT_URL = SITE + '/js_events/πνοή-αρχάνες-2026/'
NEW_EVENT = {'title': 'Πνοή', 'date': 'October 24, 2026',
             'venue': 'Συνεδριακό Κέντρο «Δίας», Αρχάνες', 'meta': '8:30 pm || Διοργάνωση: Περιφέρεια Κρήτης',
             'body': 'Χορωδιακή Συναυλία Φωνητικού Συνόλου ΦΩΝΩΔΙΑ «ΠΝΟΗ» || Ώρα έναρξης 20:30',
             'poster': AFISA_ARXANES,
             'ticket': None, 'url': NEW_EVENT_URL}
events.insert(0, NEW_EVENT)
harvest_events[NEW_EVENT_URL] = {'url': NEW_EVENT_URL, 'type': 'event', 'title': 'Πνοή', 'links': []}
route('/js_events/πνοή-αρχάνες-2026/', 'js_events/πνοή-αρχάνες-2026')

# κάθε σελίδα συναυλίας αποκτά αγγλικό δίδυμο (en/js_events/...) ώστε από το αγγλικό
# μενού να μένουμε σε αγγλικό περιβάλλον
for _u, _r in harvest_events.items():
    if _r['type'] == 'event':
        _p = up.unquote(_u).replace(SITE, '').strip('/')
        EN_XLATE[_p] = 'en/' + _p
        route('/en/' + _p + '/', 'en/' + _p)
# Άδειες καρτέλες που είχαν μείνει στο WordPress από παλιά. Ο Ιωάννης Ιδομενέως
# ζήτησε να μη φτάσουν ποτέ στη νέα σελίδα (18 Αυγ 2026).
SKOUPIDIA = {'Σιμος', 'Σίμος', 'Dummy Album Format'}

el_artists = []
for f in ('harvest-artists-1.json', 'harvest-artists-2.json', 'harvest-artists-3.json'):
    el_artists += [r for r in load_json(CLONE + '/' + f)
                   if (r.get('title') or '').strip() not in SKOUPIDIA]
en_artists = load_json(CLONE + '/harvest-artists-en.json')
products = load_json(ROOT + '/site/products.json')['products']

FIX = [('με παιδιά 8 ετών έως ενήλικες 52 ετών', 'με παιδιά 10 ετών έως ενήλικες 54 ετών'),
       ('from 8-year-old children to adults up to 52 years old', 'from 10-year-old children to adults up to 54 years old'),
       ('children from 8 years old to adults up to 52 years old', 'children from 10 years old to adults up to 54 years old')]
def fixtxt(t):
    for a, b in FIX:
        t = (t or '').replace(a, b)
    return t
def paras(t):
    return [p.strip() for p in fixtxt(t).split('||') if p.strip()]
def sec(url, heading=None, i=None):
    r = pages[url]
    if i is not None:
        return r['sections'][i]['text'] or ''
    for s in r['sections']:
        if s['heading'] == heading:
            return s['text'] or ''
    return ''

# slug helpers: register CPT routes
def slug_of(url):
    return up.unquote(url).rstrip('/').split('/')[-1]
for u in harvest_events:
    p = up.unquote(u).replace(SITE, '')
    typ = p.strip('/').split('/')[0]
    route(p, p.strip('/'))
for r in el_artists:
    p = up.unquote(r['url']).replace(SITE, ''); route(p, p.strip('/'))
for r in en_artists:
    p = up.unquote(r['url']).replace(SITE, ''); route(p, p.strip('/'))
route('/στο-θέατρο-ρεσιτάλ-και-σολιστική-συ/', 'blog/στο-θέατρο')
route('/η-φωνωδια-ταξιδεύει-στην-ιαπωνία/', 'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία')

def add_hero_video(hero):
    """Insert the background video inside a clipped wrapper, with geometry inlined so no
    stylesheet difference between browsers can let it escape the hero."""
    hero.set('style', 'position:relative;overflow:hidden;background:#111')
    media = etree.Element('div')
    media.set('class', 'hero-media')
    media.set('style', 'position:absolute;top:0;left:0;width:100%;height:100%;overflow:hidden;z-index:0;pointer-events:none')
    vid = etree.SubElement(media, 'video')
    vid.set('class', 'hero-video')
    vid.set('autoplay', 'autoplay'); vid.set('muted', 'muted'); vid.set('loop', 'loop')
    vid.set('playsinline', 'playsinline'); vid.set('preload', 'auto')
    vid.set('style', 'width:100%;height:100%;object-fit:cover;display:block')
    vid.set('src', SITE + '/wp-content/uploads/2026/04/bannerlite.mp4')
    hero.insert(0, media)


# ====================================================================== 1. HOME (EL)
def build_home():
    c = prep(home_doc.get_element_by_id('lc_swp_content'))
    # hero: remove saved <video> and the raw_code block; add our video
    hero = c.get_element_by_id('hero')
    for v in hero.xpath('.//video'):
        v.getparent().remove(v)
    for raw in hero.xpath('.//div[contains(@class,"wpb_raw_html")]'):
        raw.getparent().remove(raw)
    add_hero_video(hero)
    # vc grid: drop inline positioning already stripped by fix_refs; remove nested style/link junk (done)
    html_ = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    html_ = relink(html_, '')
    write_page('', 'Φωνωδία – Μεικτό Φωνητικό Σύνολο', html_, 'el', home=True, bodyclass='page page-template-template-visual-composer', alt_url='en/')

# ====================================================================== 1b. HOME (EN) – same layout, EN texts
def build_home_en():
    c = prep(home_doc.get_element_by_id('lc_swp_content'))
    hero = c.get_element_by_id('hero')
    for v in hero.xpath('.//video'): v.getparent().remove(v)
    for raw in hero.xpath('.//div[contains(@class,"wpb_raw_html")]'): raw.getparent().remove(raw)
    add_hero_video(hero)
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    en = pages[SITE + '/en/homepage/']
    about_en = paras(sec(SITE + '/en/homepage/', None, 1))
    repl = [
        ('Φωνητικό σύνολο Φωνωδία', 'Phonodia Vocal Ensemble'),
        ('Κέντρο Φωνητικής Τέχνης Κρήτης</span></p>', 'Cretan Center for Vocal Arts</span></p>'),
        ('Παρακολουθήστε το βίντεο', "Don't miss the full video!"),
        ('Εμφανίσεις</span></h2>', 'Performances</span></h2>'),
        ('ΟΛΕΣ ΟΙ ΕΜΦΑΝΙΣΕΙΣ', 'ALL PERFORMANCES'),
        ('Λιγά λόγια για το σύνολο', 'A few words about the ensemble'),
        ('Διαβάστε περισσότερα', 'Read more'),
        (SITE + '/el/events/', SITE + '/en/performances/'),
        (SITE + '/about/', SITE + '/en/a-few-words-about-the-ensemble/'),
        (SITE + '/el/about/', SITE + '/en/a-few-words-about-the-ensemble/'),
    ]
    for a, b in repl:
        h = h.replace(a, b)
    # replace the two Greek about paragraphs with EN ones
    el_about = paras(sec(SITE + '/', 'Λιγά λόγια για το σύνολο'))
    frag = LH.fragment_fromstring('<div>' + h + '</div>')
    ps = [p for p in frag.xpath('.//p') if p.text_content().strip().startswith('Όταν ξεκινήσαμε') or p.text_content().strip().startswith('Σήμερα, κοιτάζοντας')]
    for p, t in zip(ps, about_en):
        for ch in list(p): p.remove(ch)
        p.text = t
    # AMKE heading + text
    for el in frag.xpath('.//*'):
        if el.text and 'Η\n Φωνωδία λειτουργεί' in el.text or (el.text and el.text.strip().startswith('Η Φωνωδία λειτουργεί')):
            el.text = FOOTER_EN[list(FOOTER_EN)[0]]
    for el in frag.xpath('.//*[text()]'):
        if el.text and re.sub(r'\s+', ' ', el.text).strip().startswith('Η Φωνωδία λειτουργεί'):
            el.text = FOOTER_EN[list(FOOTER_EN)[0]]
    h = (frag.text or '') + ''.join(tostr(ch) for ch in frag)
    h = relink(h, 'en', EN_XLATE)
    write_page('en', 'Phonodia Vocal Ensemble', h, 'en', home=True, bodyclass='page page-template-template-visual-composer', alt_url='../')

# ====================================================================== 2. MEMBERS
def artist_item(name, url, photo, from_dir, last=False):
    return '''<div class="single_artist_item %s artists_4_on_row">
<div class="artist_img_container lc_swp_background_image" data-bgimage="%s" style="background-image: url('%s');">
<div class="album_overlay artist_overlay lc_swp_overlay transition3 lc_js_link" data-href="%s" data-target="_self"></div>
<div class="artist_item_socials"></div></div>
<a href="%s"><h3 class="artist_title album_heading transition4"> %s </h3></a>
<div class="artist_nickname">  </div></div>''' % ('' if last else 'has_right_padding', esc(photo or ''), esc(photo or ''), local_href(from_dir, url), local_href(from_dir, url), esc(name))

def build_members():
    # Use the real saved DOM (exact structure), only removing the hidden test block ("Σιμος") and relinking.
    c = prep(parse(SAVED + '/members.htm').get_element_by_id('lc_swp_content'))
    for bird in c.xpath('.//div[@id="bird-tab"]'):
        bird.getparent().remove(bird)
    for rawjs in c.xpath('.//div[contains(@class,"wpb_raw_js")]'):
        rawjs.getparent().remove(rawjs)
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    h = relink(h, 'μέλη')
    write_page('μέλη', 'Μέλη - Φωνωδία', h, 'el', bodyclass='page', alt_url='../en/members/')
    # EN members: same DOM, English names + EN links, section headings from EN page
    c = prep(parse(SAVED + '/members.htm').get_element_by_id('lc_swp_content'))
    for bird in c.xpath('.//div[@id="bird-tab"]'): bird.getparent().remove(bird)
    for rawjs in c.xpath('.//div[contains(@class,"wpb_raw_js")]'): rawjs.getparent().remove(rawjs)
    name_map = {}
    for grp in ('members', 'kids', 'partners'):
        for m in members[grp]:
            name_map[m['el']] = (m['en'], m['url_en'])
    name_map[members['director']['el']] = (members['director']['en'], members['director']['url_en'])
    for h3 in c.xpath('.//h3[contains(@class,"artist_title")]'):
        nm = h3.text_content().strip()
        if nm in name_map:
            en, url = name_map[nm]
            h3.text = ' %s ' % en
            a = h3.getparent()
            if a.tag == 'a' and url: a.set('href', url)
            item = a.getparent()
            for ov in item.xpath('.//*[@data-href]'):
                if url: ov.set('data-href', url)
    # headings
    txt_map = {'Καλλιτεχνικός διευθυντής': 'Artistic Director', 'Καλλιτεχνικός Διευθυντής': 'Artistic Director & Conductor', 'Μέλη': 'Members',
               'Παιδικά – Εφηβικά Τμήματα': 'Junior & Youth Division', 'Συνεργάτες': 'Collaborators',
               'Υπεύθυνη Έργου & Οπτικής Ταυτότητας': 'Project Manager & Visual Identity Coordinator'}
    for el in c.xpath('.//*'):
        if el.text and el.text.strip() in txt_map:
            el.text = txt_map[el.text.strip()]
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    h = relink(h, 'en/members')
    write_page('en/members', 'Members - Φωνωδία', h, 'en', bodyclass='page', alt_url='../../μέλη/')

# ====================================================================== 3. ARTIST SINGLE PAGES
def build_artists():
    def one(r, lang):
        p = up.unquote(r['url']).replace(SITE, '').strip('/')
        photo = None
        for i in r.get('images') or []:
            k = i.split('/uploads/')[-1]
            if any(x in k for x in ('Φωνωδία-mavro', 'Φωνωδία-aspro', '2025/11/', 'cropped-CleanShot')): continue
            photo = re.sub(r'-\d+x\d+(?=\.\w+$)', '', i); break
        body = r.get('body') or ''
        boiler = 'Η Φωνωδία λειτουργεί' in body or 'Phonodia (Fónodia) operates' in body
        body_html = '' if (not body or boiler) else ''.join('<p>%s</p>' % esc(x) for x in paras(body))
        role = r.get('role') or ''
        if role in ('dokimi', 'dokimi-en'): role = ''
        img = '<div class="artist_single_img"><img src="%s" alt="%s"></div>' % (esc(photo), esc(r['title'])) if photo else ''
        content = '<div class="lc_content_full lc_swp_boxed lc_basic_content_padding page_text"><div class="artist_bio_wrap">%s%s</div></div>' % (img, body_html)
        back = SITE + ('/en/members/' if lang == 'en' else '/μέλη/')
        content += '<div class="lc_swp_boxed" style="padding-bottom:60px"><div class="lc_button"><a href="%s">%s</a></div></div>' % (local_href(p, back), 'Members' if lang == 'en' else 'Μέλη')
        write_page(p, r['title'] + ' - Φωνωδία', content, lang, bodyclass='single single-js_artist', heading_html=heading_area(r['title'], role or None))
    for r in el_artists:
        if r['title'].strip() in ('Σιμος',): continue
        one(r, 'el')
    for r in en_artists:
        if r['title'].strip() in ('Simos',): continue
        one(r, 'en')

# ====================================================================== 4. EVENTS
MONTHS_EN = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
MONTH_NAMES = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
def parse_date(s):
    m = re.search(r'([A-Z][a-z]+) (\d{1,2}), (\d{4})', s or '')
    if not m: return None
    return (int(m.group(3)), MONTH_NAMES[m.group(1)], int(m.group(2)))
def parse_end(s):
    ms = re.findall(r'([A-Z][a-z]+) (\d{1,2}), (\d{4})', s or '')
    if len(ms) > 1:
        return int(ms[1][1])
    return None

def build_events():
    # single events: reuse the Πνοή DOM as template
    tpl = prep(inner_doc.get_element_by_id('lc_swp_content'))
    ev_by_title = {}
    for u, r in harvest_events.items():
        if r['type'] == 'event' and u != NEW_EVENT_URL: ev_by_title[r['title']] = (u, r)
    listing = []
    for e in events:
        u, r = (e['url'], harvest_events[e['url']]) if e.get('url') else ev_by_title[e['title']]
        p = up.unquote(u).replace(SITE, '').strip('/')
        c = copy.deepcopy(tpl)
        # date/time/venue/location entries
        entries = c.xpath('.//div[@class="event_short_details"]/div[contains(@class,"lc_event_entry")]')
        # entries[0]=date, [1]=time, [2]=location(itemprop), [3]=venue pin, then display_none name
        date_txt = (e['date'] or '').split('||')[0].strip()
        meta = paras(e['meta'])
        time_txt = meta[0] if meta and re.match(r'^\d{1,2}:\d{2}\s*[ap]m$', meta[0]) else ''
        rest_meta = meta[1:] if time_txt else meta
        venue = e['venue'] or ''
        vparts = [x.strip() for x in re.split(r'\s*[|,]\s*', venue, maxsplit=1)] if venue else ['']
        loc, pin = (vparts[0], vparts[1] if len(vparts) > 1 else '')
        def set_entry(div, icon_class, text):
            for ch in list(div): div.remove(ch)
            i = etree.SubElement(div, 'i'); i.set('class', icon_class); i.set('aria-hidden', 'true'); i.tail = ' ' + text + ' '
            div.text = ''
        set_entry(entries[0], 'far fa-calendar-alt', date_txt)
        entries[0].set('content', '')
        if time_txt: set_entry(entries[1], 'far fa-clock', time_txt)
        else: entries[1].getparent().remove(entries[1])
        set_entry(entries[2], 'fas fa-map-marker-alt', loc)
        if pin: set_entry(entries[3], 'fas fa-map-pin', pin)
        else: entries[3].getparent().remove(entries[3])
        for dn in c.xpath('.//div[contains(@class,"display_none") and @itemprop="name"]'):
            dn.text = e['title']
        for a in c.xpath('.//a[@itemprop="url"]'): a.set('href', local_href(p, u))
        # buttons
        scp = c.xpath('.//div[@class="small_content_padding"]')[0]
        btnwrap = scp.xpath('./div[contains(@class,"lc_event_entry")]')[0]
        for ch in list(btnwrap): btnwrap.remove(ch)
        links = [l for l in (r.get('links') or []) if not any(x in l for x in ('twitter.com/intent', 'facebook.com/sharer', 'pinterest.com/pin', 'youtube.com/embed', 'instagram.com/phonodia', 'youtube.com/channel'))]
        # 17 Αυγ 2026: κανένα κουμπί «Εισιτήρια» — οι συναυλίες έχουν τελειώσει
        for l in links:
            if l == e.get('ticket'): continue
            if 'facebook.com/photo' in l or 'fb.me' in l or 'facebook.com/events' in l:
                b = etree.SubElement(btnwrap, 'div'); b.set('class', 'lc_button'); a = etree.SubElement(b, 'a'); a.set('href', l); a.set('target', '_blank'); a.text = 'Facebook Event'
        # description
        desc = c.xpath('.//div[@itemprop="description"]')[0]
        for ch in list(desc): desc.remove(ch)
        desc.text = ''
        body_html = ''.join('<p>%s</p>' % esc(x) for x in paras(e['body']))
        if rest_meta:
            body_html += ''.join('<p>%s</p>' % esc(x) for x in rest_meta)
        # embedded youtube for Requiem
        yt = [l for l in (r.get('links') or []) if 'youtube.com/embed' in l]
        if yt:
            m = re.search(r'embed/(?:watch\?v=)?([A-Za-z0-9_-]{6,})', yt[0])
            if m: body_html += '<div class="yt_embed" style="position:relative;padding-top:56.25%%;margin-top:20px"><iframe style="position:absolute;inset:0;width:100%%;height:100%%;border:0" src="https://www.youtube.com/embed/%s" allowfullscreen></iframe></div>' % m.group(1)
        desc.append(LH.fragment_fromstring('<div class="evt_body_html">' + body_html + '</div>'))
        # sharing links
        for a in c.xpath('.//div[contains(@class,"lc_sharing_icons")]//a'):
            h = a.get('href')
            h = re.sub(r'url=[^&]+', 'url=' + up.quote(u, safe=''), h)
            if 'pinterest' in h and e.get('poster'):
                h = re.sub(r'media=.*$', 'media=' + e['poster'], h)
            a.set('href', h)
        # poster
        er = c.xpath('.//div[@class="event_right"]')[0]
        for ch in list(er): er.remove(ch)
        if e.get('poster'):
            img = etree.SubElement(er, 'img'); img.set('src', e['poster']); img.set('alt', e['title']); img.set('loading', 'lazy'); img.set('class', 'attachment-large size-large wp-post-image'); img.set('itemprop', 'image')
        h0 = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
        write_page(p, e['title'] + ' - Φωνωδία', relink(h0, p), 'el', bodyclass='single single-js_events', heading_html=heading_area(e['title']), alt_url='../../en/' + p + '/')
        write_page('en/' + p, e['title'] + ' - Φωνωδία', relink(h0, 'en/' + p, EN_XLATE), 'en', bodyclass='single single-js_events', heading_html=heading_area(e['title']), alt_url='../../../' + p + '/')
        listing.append((e, u, loc, pin, time_txt))
    # events archive (EL + EN) – theme's events_list markup
    def archive(local_dir, lang):
        items = ''
        for e, u, loc, pin, time_txt in listing:
            d = parse_date(e['date']); end = parse_end(e['date'])
            day = '%02d' % d[2] + ('-%02d' % end if end else '')
            mon = MONTHS_EN[d[1]].lower()
            thumb = re.sub(r'\.(\w+)$', r'-300x300.\1', e['poster']) if e.get('poster') else ''
            # use original size (300 variant may not exist for all) → use poster itself
            thumb = e.get('poster') or ''
            buy = ''
            items += '''<li class="single_event_list clearfix"><a href="%s">
<div class="event_list_entry event_date"><div class="text_center event_list_date_container"><div class="eventlist_day">%s</div><div class="eventlist_month">%s</div><div class="eventlist_year">%d</div></div></div>
<div class="event_list_entry event_title_img clearfix">%s<div class="evnt_list_title_loc"><div class="event_list_title">%s</div><div class="event_list_location"> %s </div></div></div>
<div class="event_list_entry event_venue"><i class="fas fa-map-marker-alt" aria-hidden="true"></i> %s</div>
<div class="event_list_entry event_time"><i class="far fa-clock" aria-hidden="true"></i> %s</div>
<div class="event_list_entry event_buy">%s</div></a></li>''' % (local_href(local_dir, u, EN_XLATE if lang == 'en' else None), day, mon, d[0],
                ('<div class="event_img"><img src="%s" alt="%s"></div>' % (esc(thumb), esc(e['title']))) if thumb else '',
                esc(e['title']), esc(e['venue'] or ''), esc(pin), esc(time_txt), buy)
        content = '<div class="lc_content_full lc_swp_boxed"><ul class="events_list">%s</ul></div>' % items
        title = 'Εμφανίσεις - Φωνωδία' if lang == 'el' else 'Events'
        hd = heading_area('Εμφανίσεις' if lang == 'el' else 'Events').replace('id="heading_area" class="settings_default"', 'id="heading_area" class="settings_default events_heading"')
        write_page(local_dir, title, content, lang, bodyclass='page page-template-template-events-all', heading_html=hd, alt_url=('../en/performances/' if lang == 'el' else '../../events/'))
    archive('events', 'el'); archive('en/performances', 'en')

# ====================================================================== 5. VIDEOS
def build_videos():
    doc = parse(SAVED + '/video.htm')
    c = prep(doc.get_element_by_id('lc_swp_content'))
    # video items link to single_video pages we don't have; make them open YouTube in modal instead
    vids_by_title = {v['title']: v for v in videos}
    for item in c.xpath('.//div[contains(@class,"single_video_item")]'):
        t = ''.join(item.xpath('.//h3//text()') or item.xpath('.//div[contains(@class,"video_title")]//text()')).strip()
        v = None
        for k, vv in vids_by_title.items():
            if k[:25] in t or t[:25] in k: v = vv; break
        if not v:
            for k, vv in vids_by_title.items():
                kk = re.sub(r'\W+', '', k)[:18]; tt = re.sub(r'\W+', '', t)[:18]
                if kk and (kk in re.sub(r'\W+', '', t) or tt in re.sub(r'\W+', '', k)): v = vv; break
        if v and v.get('yt'):
            for el in item.xpath('.//*[@data-href]'):
                el.set('data-href', '#'); el.set('data-vid', v['yt']); el.set('class', (el.get('class') or '') + ' video_play_btn_scd')
            for a in item.xpath('.//a[@href]'):
                a.set('href', 'https://www.youtube.com/watch?v=' + v['yt']); a.set('target', '_blank')
    for nav in c.xpath('.//div[contains(@class,"video_post_nav")]'):
        nav.getparent().remove(nav)
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    raw = h
    hd = heading_of(doc).replace('>Video Gallery<', '>Video Gallery<').replace('> Video <', '> Μαγνητοσκοπήσεις <')
    write_page('performs-in-action', 'Μαγνητοσκοπήσεις - Φωνωδία', relink(raw, 'performs-in-action'), 'el',
               bodyclass='page page-template-template-videos', heading_html=hd, alt_url='../en/videos/')
    # EN δίδυμη: ίδια βίντεο, ίδιοι ελληνικοί τίτλοι έργων, αγγλικό μενού και αγγλική επικεφαλίδα
    hd_en = hd.replace('> Μαγνητοσκοπήσεις <', '> Videos <')
    write_page('en/videos', 'Videos - Φωνωδία', relink(raw, 'en/videos', EN_XLATE), 'en',
               bodyclass='page page-template-template-videos', heading_html=hd_en, alt_url='../../performs-in-action/')

# ====================================================================== 6. GALLERY + ALBUMS
def build_gallery():
    doc = parse(SAVED + '/concert-gallery.htm')
    c = prep(doc.get_element_by_id('lc_swp_content'))
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    write_page('gallery', 'Φωτογραφικό Υλικό - Φωνωδία', relink(h, 'gallery'), 'el', bodyclass='archive tax-photo_album_category', heading_html=heading_of(doc), alt_url='../en/photos/')
    # album pages (EL + EN δίδυμες) — οι τίτλοι των άλμπουμ μένουν αυτολεξεί όπως στο WordPress
    album_dirs = {}
    for a in albums:
        u = [k for k, r in harvest_events.items() if r['type'] == 'album' and r['title'] == a['title']][0]
        p = up.unquote(u).replace(SITE, '').strip('/')
        album_dirs[p] = 'en/' + p
    EN_XLATE.update(album_dirs)
    # EN copy of the listing: same DOM, title "Photo Gallery", links stay in English
    hd = heading_of(doc).replace('Φωτογραφικό Υλικό', 'Photo Gallery')
    h_en = relink(h, 'en/photos', EN_XLATE)
    for gr, en_ in ALBUM_EN.items():
        h_en = h_en.replace(gr, en_)
    write_page('en/photos', 'Photo Gallery - Φωνωδία', h_en, 'en', bodyclass='archive tax-photo_album_category', heading_html=hd, alt_url='../../gallery/')
    for a in albums:
        u = [k for k, r in harvest_events.items() if r['type'] == 'album' and r['title'] == a['title']][0]
        p = up.unquote(u).replace(SITE, '').strip('/')
        grid = ''
        for i, img in enumerate(a['images']):
            grid += '<div class="photo_gallery_item %s"><a href="%s" data-lightbox="album"><img loading="lazy" class="swp_gallery_item_thumbnail" src="%s" alt="%s"></a></div>' % ('has_right_padding' if (i % 3) != 2 else '', esc(img), esc(img), esc(a['title']))
        grid_html = '<div class="lc_content_full photo_gallery_container lc_swp_boxed"><div class="photo_gallery_row clearfix">%s</div></div>' % grid
        pen = 'en/' + p
        back_el = '<div class="lc_swp_boxed" style="padding-bottom:60px"><div class="lc_button"><a href="%s">Φωτογραφικό Υλικό</a></div></div>' % rel(p, 'gallery')
        back_en = '<div class="lc_swp_boxed" style="padding-bottom:60px"><div class="lc_button"><a href="%s">Photo Gallery</a></div></div>' % rel(pen, 'en/photos')
        write_page(p, a['title'] + ' - Φωνωδία', grid_html + back_el, 'el', bodyclass='single single-js_photo_albums',
                   heading_html=heading_area(a['title'], 'Concert'), alt_url=rel(p, pen))
        ten = ALBUM_EN.get(a['title'], a['title'])
        write_page(pen, ten + ' - Φωνωδία', grid_html + back_en, 'en', bodyclass='single single-js_photo_albums',
                   heading_html=heading_area(ten, 'Concert'), alt_url=rel(pen, p))

# ====================================================================== 7. CONTACT
CONSENT_EL = 'Συμφωνώ να χρησιμοποιηθούν τα στοιχεία μου για την επικοινωνία μας.'
CONSENT_EN = 'I agree that my details may be used for our communication.'

def build_contact():
    doc = parse(SAVED + '/contact.htm')
    c = prep(doc.get_element_by_id('lc_swp_content'))
    # contact form: keep markup, point to formsubmit-less mailto (static) – form posts nowhere; convert to mailto link + note
    for f in c.xpath('.//form'):
        f.set('action', 'mailto:contact@phonodia.com'); f.set('method', 'post'); f.set('enctype', 'text/plain')
    h = (c.text or '') + ''.join(tostr(ch) for ch in c if isinstance(ch.tag, str))
    CANV = SITE + '/wp-content/uploads/2025/05/IMG_3091-AM-scaled.jpg'
    # EL — ο τίτλος που ζήτησε ο Ιωάννης (διαφορά #11)
    el_ = h.replace('Ελάτε σε επικοινωνία', 'Επικοινωνήστε μαζί μας')
    el_ = el_.replace('Συμφωνείτε στην επεξεργασία των προσωπικών σας δεδομένων', CONSENT_EL)
    write_page('contact-2', 'Επικοινωνία - Φωνωδία', relink(el_, 'contact-2'), 'el', bodyclass='page page-template-template-visual-composer-header', heading_html=heading_of(doc), alt_url='../en/contact/', canvas_img=CANV)
    # EN — οι αποδόσεις είναι αυτολεξεί από τη ζωντανή αγγλική σελίδα /en/contact/
    en = h
    for a, b in [('Ελάτε σε επικοινωνία', 'Feel free to contact us'),
                 ('Ακολουθήστε μας στα social ή στείλτε μας email.', 'Follow us on social media or send us an email'),
                 ('Στείλτε μας ένα μήνυμα', 'Send us a message'),
                 ('Συμφωνείτε στην επεξεργασία των προσωπικών σας δεδομένων', CONSENT_EN),
                 # η διεύθυνση στη γραφή που χρησιμοποιεί ήδη το υποσέλιδο της ίδιας της σελίδας
                 ('Ιερολοχιτών 3, 71305, Ηράκλειο Κρήτης', 'Ieroloxiton 3, 71305, Herakleion, Crete'),
                 ('Νέο μήνυμα από την ιστοσελίδα', 'New message from the website'),
                 ('Αποστολή', 'Send')]:
        en = en.replace(a, b)
    write_page('en/contact', 'Contact - Φωνωδία', relink(en, 'en/contact'), 'en', bodyclass='page page-template-template-visual-composer-header', heading_html=heading_of(doc).replace('Επικοινωνία', 'Contact'), alt_url='../../contact-2/', canvas_img=CANV)

# ====================================================================== 8. TEXT PAGES
def text_page(local_dir, title, blocks, lang, alt=None, bodyclass='page', heading_title=None,
              canvas_img=None, white_text=False):
    """blocks: list of (heading or None, [paragraph strings]) → theme text page."""
    inner = ''
    for hd, ps in blocks:
        if hd: inner += '<p class="tes_name"><strong>%s</strong></p>' % esc(hd)
        inner += ''.join('<p>%s</p>' % esc(x) for x in ps)
    cls = 'lc_content_full lc_swp_boxed lc_basic_content_padding page_text'
    if white_text:
        cls += ' page_text_white'
    content = '<div class="%s">%s</div>' % (cls, inner)
    head = heading_area(heading_title or title, cls='white_on_black' if white_text else 'settings_default')
    write_page(local_dir, title, content, lang, bodyclass=bodyclass, heading_html=head, alt_url=alt, canvas_img=canvas_img)

def build_text_pages():
    U = SITE
    # Λίγα λόγια (with tree image)
    tree = U + '/wp-content/uploads/2025/05/ΤΟ-ΔΕΝΤΡΟ-ΜΑΣ-e1746545945362.jpg'
    def about(local_dir, title, cap, ps, lang, alt):
        content = '<div class="lc_content_full lc_swp_boxed lc_basic_content_padding page_text"><div class="about_two"><div class="about_left"><h3>%s</h3><img src="%s" alt="%s"></div><div class="about_right">%s</div></div></div>' % (esc(cap), esc(tree), esc(cap), ''.join('<p>%s</p>' % esc(x) for x in ps))
        write_page(local_dir, title, content, lang, bodyclass='page', heading_html=heading_area(title), alt_url=alt)
    about('about', 'Λίγα λόγια για το σύνολο', 'Το δένδρο της ΦΩΝΩΔΙΑΣ', [x.replace('δέντρο', 'δένδρο').replace('δέντρα', 'δένδρα') for x in paras(sec(U + '/about/', 'Λίγα λόγια για το σύνολο'))[1:]], 'el', '../en/a-few-words-about-the-ensemble/')
    about('en/a-few-words-about-the-ensemble', 'A few words about the ensemble', 'The Tree of PHONODIA', paras(sec(U + '/en/a-few-words-about-the-ensemble/', 'The Tree of PHONODIA')), 'en', '../../about/')
    # Βιογραφικό — φωτογραφία φόντου + λευκά γράμματα, όπως στο πραγματικό DOM
    CANV_BIO = U + '/wp-content/uploads/2025/06/ΦΩΝΩΔΙΑ-e1750335264323.jpg'
    text_page('σχετικά-με-το-σύνολο', 'Βιογραφικό', [(None, paras(sec(U + '/σχετικά-με-το-σύνολο/', None, 0))[:3])], 'el', '../en/about-the-ensemble/', canvas_img=CANV_BIO, white_text=True)
    text_page('en/about-the-ensemble', 'Biography', [(None, paras(sec(U + '/en/about-the-ensemble/', None, 0))[:3])], 'en', '../../σχετικά-με-το-σύνολο/', canvas_img=CANV_BIO, white_text=True)
    # Είπαν για εμάς — φωτογραφία φόντου από το πραγματικό DOM (data-bgimage)
    CANV_TES = U + '/wp-content/uploads/2025/05/IMG_5993-scaled.jpg'
    blocks = [(t['name'], t['paras']) for t in tes_el]
    text_page('είπαν-για-εμάς', 'Είπαν για εμάς', blocks, 'el', '../en/testimonials/', canvas_img=CANV_TES)
    en_t = [(s['heading'], paras(s['text'])) for s in pages[U + '/en/testimonials/']['sections']]
    text_page('en/testimonials', 'Testimonials', en_t, 'en', '../../είπαν-για-εμάς/', canvas_img=CANV_TES)
    # Στηρίξτε
    r = pages[U + '/sponsor-us/']
    blocks = [(s['heading'] if s['heading'] != 'NONE' else None, paras(s['text'])) for s in r['sections'] if s['text']]
    # add donation details (from EN page, factual)
    text_page('sponsor-us', 'Στηρίξτε το έργο μας', blocks, 'el', '../en/support-our-projects/')
    r = pages[U + '/en/support-our-projects/']
    blocks = [(s['heading'] if s['heading'] != 'NONE' else None, paras(s['text'])) for s in r['sections'] if s['text']]
    text_page('en/support-our-projects', 'Support our Projects', blocks, 'en', '../../sponsor-us/')
    # Όροι / Απόρρητο
    # Στοιχεία επιχείρησης — από τη Βεβαίωση Δραστηριοτήτων της ΑΑΔΕ (26/05/2025)
    # που έστειλε ο Ιωάννης Ιδομενέως. Τίποτα εδώ δεν είναι εικασία.
    LEGAL_EL = ('Στοιχεία επιχείρησης', [
        'Επωνυμία: ΚΕΝΤΡΟ ΦΩΝΗΤΙΚΗΣ ΤΕΧΝΗΣ ΚΡΗΤΗΣ Α.Μ.Κ.Ε. — Διακριτικός τίτλος: ΦΩΝΩΔΙΑ',
        'Νομική μορφή: Αστική Μη Κερδοσκοπική Εταιρεία. Καταστατικό επικυρωμένο από το '
        'Πρωτοδικείο Ηρακλείου, αριθμός 1, 29 Ιανουαρίου 2025.',
        'Έδρα: Ιερολοχιτών 3, 71305 Ηράκλειο Κρήτης',
        'ΑΦΜ: 996445420 — ΔΟΥ Ηρακλείου',
        'Ηλεκτρονικό ταχυδρομείο: contact@phonodia.com',
        # ΦΠΑ: ΑΦΑΙΡΕΘΗΚΕ 17 Αυγ 2026. Η βεβαίωση ΑΑΔΕ (26/05/2025) έγραφε «απαλλασσόμενων
        # μικρών επιχειρήσεων», όμως ο Ιωάννης Ιδομενέως διευκρίνισε ότι τα έσοδα από
        # εισιτήρια ξεπερνούν το όριο. Καμία αναφορά σε ΦΠΑ μέχρι να απαντήσει ο λογιστής.
        'Για καταγγελίες μπορείτε να απευθυνθείτε στη Γενική Γραμματεία Εμπορίου '
        '(kataggelies.mindev.gov.gr, γραμμή καταναλωτή 1520) ή στον Συνήγορο του Καταναλωτή '
        '(synigoroskatanaloti.gr).',
    ])
    LEGAL_EN = ('Company details', [
        'Name: CRETAN CENTER OF VOCAL ARTS (Non-Profit Organization) — Trading as: PHONODIA',
        'Legal form: Urban Non-Profit Company. Articles of association certified by the '
        'Court of First Instance of Herakleion, no. 1, 29 January 2025.',
        'Registered address: Ieroloxiton 3, 71305 Herakleion, Crete, Greece',
        'Tax ID (ΑΦΜ): 996445420 — Tax Office of Herakleion',
        'Email: contact@phonodia.com',
        'Complaints may be addressed to the General Secretariat of Commerce '
        '(kataggelies.mindev.gov.gr, consumer line 1520) or to the Greek Consumer Ombudsman '
        '(synigoroskatanaloti.gr).',
    ])
    for src, loc, ttl, lang, alt in [('/όροι-χρήσης/', 'όροι-χρήσης', 'Όροι Χρήσης', 'el', '../en/terms-of-use/'), ('/en/terms-of-use/', 'en/terms-of-use', 'Terms of Use', 'en', '../../όροι-χρήσης/'),
                                     ('/πολιτική-απορρήτου/', 'πολιτική-απορρήτου', 'Πολιτική Απορρήτου', 'el', '../en/privacy-policy/'), ('/en/5015-2/', 'en/privacy-policy', 'Privacy Policy', 'en', '../../πολιτική-απορρήτου/')]:
        r = pages[U + src]
        blocks = [(s['heading'] if s['heading'] not in ('NONE', None) and 'Κέντρο Φωνητικής' not in s['heading'] else None, paras(s['text'])) for s in r['sections'] if s['text'] and 'Η Φωνωδία λειτουργεί' not in (s['text'] or '')[:30] and 'Phonodia (Fónodia) operates' not in (s['text'] or '')[:40]]
        if 'όροι' in loc or 'terms' in loc:
            blocks.append(LEGAL_EL if lang == 'el' else LEGAL_EN)
        text_page(loc, ttl, blocks, lang, alt)

# ====================================================================== 9. PRODUCTS / E-SHOP
def build_products():
    prods = shop.load()
    # register routes for every product + the cart pages
    for p in prods:
        route('/product/%s/' % p['slug'], 'product/%s' % p['slug'])
        route('/en/product/%s/' % p['slug'], 'en/product/%s' % p['slug'])
    route('/cart/', 'cart'); route('/en/cart/', 'en/cart')
    route('/παραγγελία/', 'παραγγελία'); route('/en/order/', 'en/order')
    route('/checkout/', 'παραγγελία'); route('/en/checkout/', 'en/order')

    def build_for(lang, shop_dirs, cart_dir):
        t = shop.T[lang]
        for p in prods:
            d = ('en/product/' if lang == 'en' else 'product/') + p['slug']
            html_ = shop.product_page(p, lang,
                                      local_href(d, SITE + ('/en/cart/' if lang == 'en' else '/cart/')),
                                      local_href(d, SITE + ('/en/products/' if lang == 'en' else '/προϊόντα/')))
            write_page(d, p['name'] + ' - Φωνωδία', html_, lang,
                       bodyclass='single single-product woocommerce woocommerce-page',
                       heading_html=heading_area(p['name'], t['shop']))
        # καλάθι + σελίδα παραγγελίας (το ταμείο μένει πια μέσα στη σελίδα μας)
        order_dir = 'en/order' if lang == 'en' else 'παραγγελία'
        shop_url = SITE + ('/en/products/' if lang == 'en' else '/προϊόντα/')
        write_page(cart_dir, t['cart'] + ' - Φωνωδία',
                   shop.cart_page(lang, local_href(cart_dir, shop_url),
                                  local_href(cart_dir, SITE + ('/en/order/' if lang == 'en' else '/παραγγελία/'))),
                   lang, bodyclass='woocommerce woocommerce-cart', heading_html=heading_area(t['cart']))
        write_page(order_dir, t['order'] + ' - Φωνωδία',
                   shop.order_page(lang, local_href(order_dir, shop_url)),
                   lang, bodyclass='woocommerce', heading_html=heading_area(t['order']))
        # listing pages
        for dirname, intro in shop_dirs:
            hrefs = {p['slug']: local_href(dirname, SITE + ('/en/product/' if lang == 'en' else '/product/') + p['slug'] + '/') for p in prods}
            write_page(dirname, t['shop'] + ' - Φωνωδία', shop.listing(prods, lang, hrefs, intro), lang,
                       bodyclass='woocommerce woocommerce-page', heading_html=heading_area(t['shop']),
                       alt_url=None)

    STORE_INTRO_EN = ("By supporting Phonodia's non-profit vocal ensemble, your purchase directly contributes to the "
                      "preservation and international promotion of Greek choral artistry. Each item helps sustain our "
                      "artistic vision and enables performances that connect voices, cultures, and generations.")
    build_for('el', [('προϊόντα', ''), ('merch', '')], 'cart')
    build_for('en', [('en/products', ''), ('en/store', STORE_INTRO_EN)], 'en/cart')

# ====================================================================== 10. BLOG
def build_blog():
    posts = load_json(ROOT + '/site/posts.json')['posts']
    p1 = posts[0]
    p1_html = p1['content']['rendered']
    p1_html = re.sub(r'\s(width|height)="\d+"', '', p1_html)
    p1_html = re.sub(r'https://phonodiavocalensemble\.com/wp-content/uploads/[^"\' ]+-\d+x\d+(\.\w+)', lambda m: m.group(0), p1_html)
    p2 = {'title': 'Η ΦΩΝΩΔΙΑ ταξιδεύει στην Ιαπωνία!', 'date': 'April 30, 2025', 'img': SITE + '/wp-content/uploads/2025/04/FB_IMG_1745959107568-1-1024x1024.jpg',
          'body': ['Είμαστε στην ευχάριστη θέση να σας ανακοινώσουμε επίσημα την συμμετοχή μας στον 7ο Διεθνή Διαγωνισμό Χορωδιών που θα πραγματοποιηθεί τον Ιούλιο του 2025 στο Τόκιο!', 'Θα τραγουδήσουμε ανάμεσα σε κορυφαία φωνητικά σύνολα από όλον τον κόσμο!', 'Αν επιθυμείτε να στηρίξετε το ταξίδι μας, δείτε εδώ τους διαθέσιμους τρόπους στήριξης ή επικοινωνήστε μαζί μας!', 'Μείνετε συντονισμένοι για τα καλύτερα, που έρχονται σύντομα!']}
    # single posts — τα κείμενα μένουν αυτολεξεί ελληνικά· αλλάζει μόνο το μενού γύρω τους
    t1 = p1['title']['rendered']
    b1_body = '<div class="lc_content_full lc_swp_boxed lc_basic_content_padding page_text"><p class="dt" style="color:#ff9568">April 30, 2025</p>%s</div>'
    b2 = '<div class="lc_content_full lc_swp_boxed lc_basic_content_padding page_text"><p class="dt" style="color:#ff9568">%s</p><div class="artist_single_img" style="max-width:640px;margin:0 auto 30px"><img src="%s" alt=""></div>%s</div>' % (p2['date'], esc(p2['img']), ''.join('<p>%s</p>' % esc(x) for x in p2['body']))
    for lang, pre in (('el', ''), ('en', 'en/')):
        d1, d2 = pre + 'blog/στο-θέατρο', pre + 'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία'
        o1 = ('en/' if lang == 'el' else '') + 'blog/στο-θέατρο'
        o2 = ('en/' if lang == 'el' else '') + 'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία'
        o1 = o1 if lang == 'el' else 'blog/στο-θέατρο'
        o2 = o2 if lang == 'el' else 'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία'
        h1 = POST_EN_THEATRO if lang == 'en' else t1
        h2 = POST_EN.get(p2['title'], p2['title']) if lang == 'en' else p2['title']
        write_page(d1, h1, b1_body % relink(p1_html, d1, EN_XLATE if lang == 'en' else None), lang,
                   bodyclass='single single-post', heading_html=heading_area(h1), alt_url=rel(d1, o1))
        write_page(d2, h2, b2, lang, bodyclass='single single-post',
                   heading_html=heading_area(h2), alt_url=rel(d2, o2))
    # listing (EL + EN)
    entries = [(t1, 'blog/στο-θέατρο', 'Το Φωνητικό Σύνολο ΦΩΝΩΔΙΑ ετοιμάζεται να σας υποδεχτεί σε μια ξεχωριστή μουσική βραδιά! Με ένα πρόγραμμα που περιλαμβάνει ρεσιτάλ…'),
               (p2['title'], 'blog/η-φωνωδια-ταξιδεύει-στην-ιαπωνία', 'Είμαστε στην ευχάριστη θέση να σας ανακοινώσουμε επίσημα την συμμετοχή μας στον 7ο Διεθνή Διαγωνισμό Χορωδιών που θα…')]
    for lang, d, pre in (('el', 'blog', ''), ('en', 'en/blog', 'en/')):
        items = ''
        for t, href, excerpt in entries:
            if lang == 'en':
                t = POST_EN_THEATRO if href.endswith('στο-θέατρο') else POST_EN.get(t, t)
            hh = rel(d, pre + href)
            items += '<div class="blog_list_item"><p class="blog_date">April 30, 2025</p><a href="%s"><h3>%s</h3></a><p>%s</p><a class="blog_more" href="%s">Read more <i class="fas fa-arrow-right" aria-hidden="true"></i></a></div>' % (hh, esc(t), esc(excerpt), hh)
        write_page(d, 'Blog - Φωνωδία', '<div class="lc_content_full lc_swp_boxed lc_basic_content_padding page_text"><div class="blog_grid">%s</div></div>' % items,
                   lang, bodyclass='page page-template-template-blog', heading_html=heading_area('Blog'),
                   alt_url=rel(d, 'en/blog' if lang == 'el' else 'blog'))

# ====================================================================== RUN
def afisa_from_drive():
    """Κατεβάζει τα κομμάτια της αφίσας και τα ξανακολλάει σε εικόνα.

    Κάθε κομμάτι έχει το δικό του αποτύπωμα, ώστε αν κάτι φτάσει αλλοιωμένο να ξέρουμε
    ποιο ακριβώς φταίει και να μη γράψουμε ποτέ χαλασμένη εικόνα.
    """
    import base64, hashlib, subprocess
    chunks = []
    for n, (fid, want) in enumerate(AFISA_DRIVE, 1):
        url = 'https://drive.usercontent.google.com/download?id=%s&export=download' % fid
        out = '/tmp/afisa-%d.b64' % n
        try:
            subprocess.run(['curl', '-fsSL', '-A', 'Mozilla/5.0', '-o', out, url],
                           check=True, timeout=120)
        except Exception as e:
            print('afisa: το κομμάτι %d δεν κατέβηκε (%s)' % (n, e))
            return None
        txt = ''.join(open(out, encoding='utf-8', errors='replace').read().split())
        got = hashlib.sha1(txt.encode()).hexdigest()[:12]
        if got != want:
            print('afisa: το κομμάτι %d ήρθε αλλοιωμένο (%s αντί %s, %d χαρακτήρες)'
                  % (n, got, want, len(txt)))
            return None
        chunks.append(txt)
    try:
        data = base64.b64decode(''.join(chunks))
    except Exception as e:
        print('afisa: τα κομμάτια δεν έδεσαν (%s)' % e)
        return None
    if hashlib.sha1(data).hexdigest() != AFISA_SHA1:
        print('afisa: η τελική εικόνα δεν ταιριάζει με το αποτύπωμα')
        return None
    print('afisa: κατέβηκε ολόκληρη από το Drive, %d bytes' % len(data))
    return data


def emit_afisa():
    """Η αφίσα των Αρχανών.

    Η γέφυρα γράφει μόνο κείμενο, οπότε η εικόνα ταξιδεύει μία και μόνη φορά: σε
    κομμάτια από τον φάκελο της γέφυρας στο Drive. Μόλις φτάσει, μένει μέσα στο
    αποθετήριο και δεν ξαναχρειάζεται δίκτυο.
    """
    import hashlib
    repo = os.path.dirname(ROOT.rstrip('/'))
    keep = CLONE + AFISA_ARXANES[AFISA_ARXANES.rindex('/'):]

    def good(path):
        if not os.path.exists(path):
            return None
        b = open(path, 'rb').read()
        return b if hashlib.sha1(b).hexdigest() == AFISA_SHA1 else None

    data = good(keep) or good(repo + AFISA_ARXANES) or afisa_from_drive()
    if data is None:
        print('emit_afisa: η αφίσα λείπει — η σελίδα χτίζεται χωρίς αυτήν')
        return
    open(keep, 'wb').write(data)
    os.makedirs(OUT + '/img', exist_ok=True)
    open(OUT + AFISA_ARXANES, 'wb').write(data)
    print('emit_afisa: %d bytes -> %s' % (len(data), AFISA_ARXANES))


def apply_local_images():
    """Δείχνει κάθε φωτογραφία στο τοπικό /img/... αντί στο WordPress.
    Ο χάρτης φτιάχτηκε από το tools/localise.py που έτρεξε στο GitHub (17 Αυγ 2026)."""
    mf = CLONE + '/img-manifest.json'
    if not os.path.exists(mf):
        print('apply_local_images: λείπει ο χάρτης — οι εικόνες μένουν στο WordPress')
        return
    man = json.load(open(mf, encoding='utf-8'))
    pairs = []
    for key, dest in man.items():
        pairs.append((key, '/' + dest))
        q = up.quote(key, safe=':/')
        if q != key:
            pairs.append((q, '/' + dest))
    n = 0
    for root, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith(('.html', '.css', '.js')):
                continue
            path = os.path.join(root, f)
            txt = old = open(path, encoding='utf-8').read()
            if 'phonodiavocalensemble.com/wp-content/uploads' not in txt:
                continue
            for a, b in pairs:
                txt = txt.replace(a, b)
            if txt != old:
                open(path, 'w', encoding='utf-8').write(txt)
                n += 1
    print('apply_local_images: %d αρχεία, %d τοπικές εικόνες' % (n, len(man)))



# ---------------------------------------------------------------- ορθογραφία
# Λάθη που εντόπισε ο Ιωάννης Ιδομενέως στο ίδιο το WordPress. Τα διορθώνουμε εδώ,
# ώστε τα αρχεία της συγκομιδής να μένουν αυτούσια και η κάθε αλλαγή να φαίνεται.
TYPOS = [
    ('Δημοτικο Ωδείο', 'Δημοτικό Ωδείο'),
    ('Tόκιο', 'Τόκιο'),                      # λατινικό T -> ελληνικό Τ
    ('της Φωνωδία ', 'της Φωνωδίας '),
    ('κεράσιες', 'κερασιές'),
    ('Φωνη \u2013', 'Φωνή \u2013'),           # όνομα προϊόντος: έλειπε ο τόνος
    ('Ο ιστότοπος phonodia.com', 'Ο ιστότοπος phonodiavocalensemble.com'),
    ('ΑΦΜ EL996445420', 'ΑΦΜ 996445420'),    # το EL είναι μορφή VIES· η ΑΜΚΕ είναι σε απαλλαγή
    ('ΑΦΜ: EL996445420', 'ΑΦΜ: 996445420'),
]


def fix_typos():
    """Περνά τις διορθώσεις μόνο σε ορατό κείμενο — ποτέ σε διευθύνσεις ή αρχεία."""
    import glob as _g
    hits = files = 0
    for path in _g.glob(OUT + '/**/index.html', recursive=True):
        r = LH.parse(path).getroot()
        n = 0
        for el in r.iter():
            if not isinstance(el.tag, str) or el.tag in ('script', 'style'):
                continue
            for attr in ('alt', 'title', 'content', 'data-pname'):
                v = el.get(attr)
                if v:
                    for a_, b_ in TYPOS:
                        if a_ in v:
                            v = v.replace(a_, b_); el.set(attr, v); n += 1
            for name in ('text', 'tail'):
                v = getattr(el, name)
                if v:
                    for a_, b_ in TYPOS:
                        if a_ in v:
                            v = v.replace(a_, b_); setattr(el, name, v); n += 1
        if n:
            open(path, 'w', encoding='utf-8').write(
                '<!DOCTYPE html>\n' + LH.tostring(r, encoding='unicode', method='html'))
            files += 1; hits += n
    print('fix_typos: %d διορθώσεις σε %d σελίδες' % (hits, files))



if __name__ == '__main__':
    shutil.copy(SAVED + '/../site-build/assets/webfonts/fa-solid-900.woff2', OUT + '/assets/webfonts/fa-solid-900.woff2') if False else None
    build_css()
    build_home(); build_home_en()
    build_members(); build_artists()
    build_events(); build_videos(); build_gallery(); build_contact()
    build_products(); build_text_pages(); build_blog()
    # εργαλείο αυτονομίας + λίστα αρχείων που δεν δημοσιεύονται
    os.makedirs(OUT + '/tools', exist_ok=True)
    shutil.copy(os.path.dirname(os.path.abspath(__file__)) + '/localise.py', OUT + '/tools/localise.py')
    open(OUT + '/.assetsignore', 'w', encoding='utf-8').write(
        '.git\n.git/**\n.github\n.github/**\ntools\ntools/**\nsrc\nsrc/**\n'
        'wrangler.jsonc\n.assetsignore\n*.zip\nimg/manifest.json\n.bridge-version\n')
    # το εργαστήριο ταξιδεύει μαζί, για να μπορεί το GitHub να ξαναχτίζει μόνο του
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(here)
    for sub in ('build', 'clone', 'saved', 'site'):
        dst = OUT + '/src/' + sub
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(base + '/' + sub, dst,
                        ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '*.bak'))
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('files written:', n)
    fix_typos()                   # ορθογραφικές διορθώσεις που ζήτησε ο Ιωάννης Ιδομενέως
    import translate_en           # εγκεκριμένες αγγλικές αποδόσεις (16 Αυγ 2026)
    translate_en.main()
    import translate_fr           # γαλλικά: καθρέφτης των εγκεκριμένων αγγλικών (17 Αυγ 2026)
    translate_fr.main()
    emit_afisa()                   # η αφίσα των Αρχανών, 18 Αυγ 2026
    apply_local_images()           # οι φωτογραφίες ζουν πλέον μέσα στη σελίδα


