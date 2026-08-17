# -*- coding: utf-8 -*-
"""Shared helpers for building the ΦΩΝΩΔΙΑ static clone from the saved Firefox DOMs + harvest data."""
import re, json, glob, os, html, urllib.parse as up
import lxml.html as LH
from lxml import etree

ROOT = os.environ.get('FONODIA_ROOT', '/home/claude/fonodia')
SAVED = ROOT + '/saved'
CLONE = ROOT + '/clone'
SITE = 'https://phonodiavocalensemble.com'
OUT = ROOT + '/site-build'

# ---------------------------------------------------------------- image inventory
_inv = None
def inventory():
    """basename (unquoted) -> absolute original URL for every wp-content/uploads asset we know."""
    global _inv
    if _inv is not None:
        return _inv
    urls = set()
    pat = re.compile(r'https?://(?:phonodiavocalensemble\.com|phonodia\.com)/wp-content/uploads/[^\s"\'<>)\\]+')
    files = glob.glob(CLONE + '/*.json') + glob.glob(ROOT + '/site/*.json') + glob.glob(ROOT + '/site/*.md') + glob.glob(SAVED + '/*.htm')
    for f in files:
        try:
            t = open(f, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        for u in pat.findall(t):
            u = u.replace('phonodia.com/', 'phonodiavocalensemble.com/') if '//phonodia.com/' in u else u
            u = u.rstrip('.,;')
            urls.add(u)
    inv = {}
    for u in urls:
        b = up.unquote(u.rsplit('/', 1)[-1])
        inv.setdefault(b, u)
        # also register size-stripped variant so any size can be resolved to the *original*
    _inv = inv
    return inv

def resolve_local(ref):
    """Turn a Firefox '<page>_files/NAME_XXXX.ext' reference back into the original absolute URL."""
    m = re.search(r'_files/(.+)$', ref)
    if not m:
        return None
    name = up.unquote(m.group(1))
    name = re.sub(r'_[A-Za-z0-9]{4}(?=\.[A-Za-z0-9]+$)', '', name)   # strip Firefox suffix
    inv = inventory()
    if name in inv:
        return inv[name]
    # try size-stripped original
    base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', name)
    if base in inv:
        return inv[base]
    # try any inventory key that startswith base stem
    stem = os.path.splitext(base)[0]
    for k, v in inv.items():
        if k.startswith(stem):
            return v
    return None

# ---------------------------------------------------------------- html cleaning
def strip_junk(root):
    """Remove scripts/styles/links/noscripts from a parsed tree."""
    for el in root.xpath('//script|//style|//link|//noscript|//meta'):
        el.getparent().remove(el)
    for c in root.xpath('//comment()'):
        c.getparent().remove(c)

def fix_refs(root, page_dir_depth=0):
    """Rewrite _files references, phonodia.com→ensemble, drop inline computed styles that break static layout."""
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in ('src', 'href', 'data-bgimage', 'data-href', 'poster', 'data-src'):
            v = el.get(attr)
            if v and '_files/' in v:
                nv = resolve_local(v)
                if nv:
                    el.set(attr, nv)
                else:
                    # facebook emoji pngs etc → drop the image, keep alt
                    if el.tag == 'img':
                        alt = el.get('alt') or ''
                        el.tag = 'span'
                        el.text = alt
                        for a in list(el.attrib):
                            del el.attrib[a]
                    else:
                        el.set(attr, '#')
        ss = el.get('srcset')
        if ss:
            parts = []
            for p in ss.split(','):
                p = p.strip()
                if not p:
                    continue
                bits = p.split()
                u = bits[0]
                if '_files/' in u:
                    u = resolve_local(u) or ''
                if u:
                    parts.append(' '.join([u] + bits[1:]))
            if parts:
                el.set('srcset', ', '.join(parts))
            else:
                del el.attrib['srcset']
        st = el.get('style')
        if st:
            # background-image url pointing to _files
            def _bg(m):
                u = m.group(1).strip('\'"')
                if '_files/' in u:
                    u = resolve_local(u) or u
                return "url('%s')" % u
            st = re.sub(r'url\(([^)]+)\)', _bg, st)
            # remove JS-computed geometry (but keep author-set sizes on images/figures)
            if el.tag in ('img', 'figure'):
                st = re.sub(r'(?:^|;)\s*(left|top|opacity|position|overflow)\s*:[^;]+', '', st)
            else:
                st = re.sub(r'(?:^|;)\s*(width|max-width|left|top|height|min-height|opacity|margin-bottom|position|display|overflow|box-sizing)\s*:[^;]+', '', st)
            st = st.strip(' ;')
            if st:
                el.set('style', st)
            else:
                del el.attrib['style']
        for attr in list(el.attrib):
            v = el.get(attr)
            if v and 'phonodia.com/' in v and 'phonodiavocalensemble' not in v:
                el.set(attr, v.replace('https://phonodia.com/', SITE + '/').replace('http://phonodia.com/', SITE + '/'))

def tostr(el):
    return LH.tostring(el, encoding='unicode', method='html')

def parse(path):
    return LH.parse(path).getroot()

def load_json(p):
    return json.load(open(p, encoding='utf-8'))

def esc(s):
    return html.escape(s or '', quote=True)
