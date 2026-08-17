# -*- coding: utf-8 -*-
"""Post-build pass: put the approved English wording into the pages under site-build/en/.

Runs on the built DOM (never on raw HTML) so that:
  * only text nodes and human-facing attributes change,
  * image paths such as .../uploads/2025/04/Φωνωδία-mavro.png stay untouched,
  * entities like &amp; keep working.

Decisions taken by Ιωάννης Ιδομενέως, 16 Αυγ 2026:
  1 Ελληνόγραμμα -> Ellinogramma      2 Πνοή -> Breath
  3 «Φωνη» on the garments stays Greek (it is the print itself)
  4 member names in Latin letters      5 venue names translated
  6 copyright line -> Cretan Center of Vocal Arts
  7 the language switcher keeps saying «Ελληνικά»
"""
import json, glob, os, re, unicodedata
import lxml.html as LH

ROOT = os.environ.get('FONODIA_ROOT', '/home/claude/fonodia')
OUT = ROOT + '/site-build'
TRANS = ROOT + '/clone/translations-en.json'

# decision 7 — a language names itself in its own script
KEEP_GREEK = {'Ελληνικά'}

TEXT_ATTRS = ('alt', 'title', 'placeholder', 'aria-label', 'value', 'content')


def load_map():
    m = {}
    for e in json.load(open(TRANS, encoding='utf-8')):
        g, en = e['greek'], e['english']
        if g.strip() in KEEP_GREEK or not en or en == g:
            continue
        m[g] = en
        m[' '.join(g.split())] = en          # whitespace-normalised key as a fallback
    return m


# decision 4 — Greek member names in Latin letters on the English pages.
# The Latin form is taken from the artist page slug the site itself already uses,
# so nothing here is invented.
def name_map():
    d = json.load(open(ROOT + '/clone/names-en.json', encoding='utf-8'))
    return {g: l for g, l in d.items() if not g.startswith('_')}


def apply_to(path, m, nm):
    r = LH.parse(path).getroot()
    hits = 0

    def sub(s):
        if not s:
            return s, False
        raw = unicodedata.normalize('NFC', s)   # some names arrive with decomposed accents
        key = raw if raw in m else ' '.join(raw.split())
        out = m.get(key, raw)
        out = out.replace(' - Φωνωδία', ' - Phonodia')
        # names always run afterwards too, because a translated phrase can still
        # carry a Greek name inside it ("Μυρτώ Κονιδάκη & Νίκη Παπαγγελή: Voice")
        for g, l in nm.items():
            if g and g in out:
                out = out.replace(g, l)
        return out, out != s

    for el in r.iter():
        if not isinstance(el.tag, str) or el.tag in ('script', 'style'):
            continue
        for attr in TEXT_ATTRS:
            v = el.get(attr)
            if v and re.search(r'[Α-Ωα-ωΆ-ώ]', v):
                nv, ch = sub(v)
                if ch:
                    el.set(attr, nv); hits += 1
        for holder, getter, setter in ((el, 'text', 'text'), (el, 'tail', 'tail')):
            v = getattr(holder, getter)
            if v and re.search(r'[Α-Ωα-ωΆ-ώ]', v):
                nv, ch = sub(v)
                if ch:
                    setattr(holder, setter, nv); hits += 1

    if hits:
        open(path, 'w', encoding='utf-8').write(
            '<!DOCTYPE html>\n' + LH.tostring(r, encoding='unicode', method='html'))
    return hits


def main():
    m = load_map()
    nm = name_map()
    total = files = 0
    for p in sorted(glob.glob(OUT + '/en/**/index.html', recursive=True)):
        n = apply_to(p, m, nm)
        if n:
            files += 1; total += n
    print('translate_en: %d replacements in %d pages (%d phrases, %d names)'
          % (total, files, len(set(m.values())), len(nm)))


if __name__ == '__main__':
    main()
