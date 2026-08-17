# -*- coding: utf-8 -*-
"""Κάνει την ιστοσελίδα ΑΥΤΟΝΟΜΗ.

Κατεβάζει κάθε φωτογραφία και το βίντεο από το WordPress, τα βάζει μέσα στη σελίδα
(φάκελος img/), τα σμικρύνει όπου χρειάζεται, και αλλάζει όλες τις αναφορές ώστε
να μη ζητά τίποτα από το phonodiavocalensemble.com.

Τρέχει μέσα στο GitHub (εκεί υπάρχει δίκτυο). Τοπικά τρέχει με --dry για έλεγχο.
"""
import os, re, sys, glob, json, hashlib, subprocess
import urllib.parse as up

WP = 'https://phonodiavocalensemble.com/wp-content/uploads/'
PAT = re.compile(r'https://phonodiavocalensemble\.com/wp-content/uploads/[^\s"\'\)<>\\]+')
OUT = 'img'
MANIFEST = OUT + '/manifest.json'
MAXW = 1600          # καμία φωτογραφία πλατύτερη από αυτό
JPEG_Q = 82
DRY = '--dry' in sys.argv


def targets():
    out = []
    for pat in ('**/*.html', 'assets/*.css', 'assets/*.js'):
        for p in glob.glob(pat, recursive=True):
            if p.startswith(('_out/', 'node_modules/', OUT + '/')):
                continue
            out.append(p)
    return sorted(set(out))


def collect(files):
    """{κανονικοποιημένο url -> [παραλλαγές όπως εμφανίζονται στα αρχεία]}"""
    seen = {}
    for f in files:
        txt = open(f, encoding='utf-8').read()
        for raw in PAT.findall(txt):
            raw = raw.rstrip('.,;')
            key = up.unquote(raw)
            seen.setdefault(key, set()).add(raw)
    return {k: sorted(v) for k, v in seen.items()}


def local_of(key):
    ext = os.path.splitext(up.urlparse(key).path)[1].lower() or '.jpg'
    if ext == '.jpeg':
        ext = '.jpg'
    return '%s/%s%s' % (OUT, hashlib.sha1(key.encode('utf-8')).hexdigest()[:12], ext)


def fetch(key, dest):
    url = up.quote(key, safe=':/?&=%')
    for attempt in range(3):
        r = subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '120',
                            '-A', 'Mozilla/5.0 (phonodia-localiser)', '-o', dest, url])
        if r.returncode == 0 and os.path.getsize(dest) > 0:
            return True
        print('   ξανά (%d) %s' % (attempt + 1, key))
    return False


def shrink_image(path):
    try:
        from PIL import Image
    except Exception:
        return
    try:
        im = Image.open(path)
    except Exception:
        return
    w, h = im.size
    changed = False
    if w > MAXW:
        im = im.resize((MAXW, max(1, round(h * MAXW / w))), Image.LANCZOS)
        changed = True
    if path.endswith('.jpg') and (changed or os.path.getsize(path) > 300_000):
        im.convert('RGB').save(path, 'JPEG', quality=JPEG_Q, optimize=True, progressive=True)
    elif changed:
        im.save(path)


def shrink_video(path):
    tmp = path + '.tmp.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path,
                        '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-crf', '30',
                        '-preset', 'slow', '-an', '-movflags', '+faststart', tmp])
    if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
        os.replace(tmp, path)


def main():
    files = targets()
    found = collect(files)
    print('αρχεία σελίδας: %d · διαφορετικά αρχεία WordPress: %d' % (len(files), len(found)))
    if DRY:
        for k in sorted(found)[:5]:
            print('  ', local_of(k), '<-', k)
        print('(δοκιμή· δεν κατέβηκε τίποτα)')

    os.makedirs(OUT, exist_ok=True)
    man = {}
    if os.path.exists(MANIFEST):
        man = json.load(open(MANIFEST, encoding='utf-8'))

    ok, fail = 0, []
    for key in sorted(found):
        dest = local_of(key)
        if os.path.exists(dest) and man.get(key) == dest:
            ok += 1
            continue
        if DRY:
            continue
        if not fetch(key, dest):
            fail.append(key)
            if os.path.exists(dest):
                os.remove(dest)
            continue
        if dest.endswith('.mp4'):
            shrink_video(dest)
        else:
            shrink_image(dest)
        man[key] = dest
        ok += 1
        print('  ✓ %s  (%d KB)' % (dest, os.path.getsize(dest) // 1024))

    if not DRY:
        json.dump(man, open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- αλλαγή αναφορών
    rewrites = 0
    for f in files:
        txt = old = open(f, encoding='utf-8').read()
        for key, variants in found.items():
            if key in fail:
                continue
            dest = man.get(key) or local_of(key)
            if DRY and not os.path.exists(dest):
                pass
            for v in variants:
                txt = txt.replace(v, '/' + dest)
        if txt != old:
            rewrites += 1
            if not DRY:
                open(f, 'w', encoding='utf-8').write(txt)
    print('κατέβηκαν/υπήρχαν: %d · απέτυχαν: %d · σελίδες που άλλαξαν: %d'
          % (ok, len(fail), rewrites))
    for k in fail:
        print('  ΑΠΕΤΥΧΕ', k)


if __name__ == '__main__':
    main()
