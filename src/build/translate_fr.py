# -*- coding: utf-8 -*-
"""Φτιάχνει τις ΓΑΛΛΙΚΕΣ σελίδες, καθρεφτίζοντας τις αγγλικές.

Γιατί έτσι: οι αγγλικές σελίδες είναι ήδη εγκεκριμένες από τον Ιωάννη Ιδομενέως
(«Ναι είναι μια χαρά τα αγγλικά», 17 Αυγ 2026). Αντιγράφοντάς τες και αλλάζοντας
μόνο το κείμενο, η γαλλική έκδοση παίρνει δωρεάν όλες τις διορθώσεις που έγιναν
στην αγγλική — μενού, σύνδεσμοι, εικόνες, δομή.

Ροή: site-build/en/**  ->  site-build/fr/**
  1. αντιγραφή
  2. σύνδεσμοι  .../en/...  ->  .../fr/...
  3. κείμενο    αγγλικά -> γαλλικά, από το clone/translations-fr.json (τριάδες el/en/fr)
  4. lang="fr" και ετικέτες του διακόπτη γλώσσας
"""
import json, glob, os, re, shutil, hashlib, gzip, base64
import lxml.html as LH

ROOT = os.environ.get('FONODIA_ROOT', '/home/claude/fonodia')
OUT = ROOT + '/site-build'
# Ζεύγη «αποτύπωμα αγγλικού»: «γαλλικό». Το αποτύπωμα είναι τα 12 πρώτα ψηφία του
# sha1 του αγγλικού κειμένου με κανονικοποιημένα κενά — έτσι το αρχείο μένει μικρό
# και ταξιδεύει άνετα μέσα από τη γέφυρα. Τα πλήρη τρίγλωσσα κείμενα φυλάσσονται
# στα clone/translations-fr.json και clone/translations-fr-extra.json.
FR = ROOT + '/clone/fr.json'
FR_B64 = ROOT + '/clone/fr.b64'      # το ίδιο, συμπιεσμένο

# Το λεξικό είναι μεγάλο, οπότε δεν ταξιδεύει μέσα στο πακέτο της γέφυρας. Κάθεται
# στον ίδιο δημόσιο φάκελο του Drive, σε δύο κομμάτια, και κατεβαίνει μία φορά όταν
# χτίζεται η σελίδα μέσα στο GitHub. Τοπικά χρησιμοποιείται το clone/fr.json.
FR_PARTS = ('1wapYuAuyG7AKXkUDZHYerEGlEnFYQIbR', '1Ot5tlO2I5jda6tKwT38gYekuWaVlLkYg')


def fetch_b64():
    import subprocess
    out = []
    for fid in FR_PARTS:
        url = 'https://drive.usercontent.google.com/download?id=%s&export=download' % fid
        r = subprocess.run(['curl', '-fsSL', '--retry', '3', '-A', 'Mozilla/5.0', url],
                           capture_output=True)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError('den katevike to kommati ' + fid)
        out.append(r.stdout.decode('ascii').strip())
    data = ''.join(out)
    open(FR_B64, 'w').write(data)
    return data


def fp(s):
    return hashlib.sha1(' '.join(s.split()).encode('utf-8')).hexdigest()[:12]

TEXT_ATTRS = ('alt', 'title', 'placeholder', 'aria-label', 'value', 'content', 'data-pname',
              # τα λεκτικά του καταστήματος ταξιδεύουν μέσα σε data-* και τα διαβάζει η JavaScript
              'data-empty', 'data-req', 'data-ok', 'data-total', 'data-remove', 'data-checkout',
              'data-items', 'data-shiph', 'data-grand', 'data-ask', 'data-big', 'data-ww')

# Ονόματα γλωσσών: κάθε γλώσσα λέγεται στη δική της γραφή.
LANG_LABEL = {'el': 'Ελληνικά', 'en': 'English', 'fr': 'Français'}

# Λεκτικά του καταστήματος και του μενού. Δεν υπάρχουν στη συγκομιδή, γιατί τα
# γράψαμε εμείς — άρα τα αποδίδω εδώ, ρητά και ελέγξιμα.
UI = {
    # κατάστημα — τρόπος παράδοσης (19 Αυγ 2026)
    'Delivery method': 'Mode de livraison',
    'Where it is going': 'Destination',
    'Greece': 'Grèce',
    'Europe': 'Europe',
    'Rest of the world': 'Reste du monde',
    'To a BOX NOW locker': 'Dans un casier BOX NOW',
    'Collect it whenever you like, from the locker that suits you.':
        'Retirez-le quand vous voulez, dans le casier qui vous arrange.',
    'To my address': 'À mon adresse',
    'Courier delivery, on working days and hours.':
        'Livraison par coursier, aux jours et heures ouvrables.',
    'Which locker suits you?': 'Quel casier vous arrange ?',
    'Find your locker': 'Trouvez votre casier',
    'Shipping': 'Frais de port',
    'For orders above 15 items please write to us and we will arrange it together.':
        'Pour les commandes de plus de 15 articles, écrivez-nous et nous organiserons cela ensemble.',
    'For destinations outside Europe please write to us and we will tell you the exact cost.':
        'Pour les destinations hors d\'Europe, écrivez-nous et nous vous indiquerons le coût exact.',
    'on request': 'sur demande',
    'Grand total': 'Total à payer',
    'Items': 'Articles',
    'Garments are printed to order by the NeedleWorks shop and reach their destination within 15 days at the latest.':
        'Les vêtements sont imprimés à la commande par la boutique NeedleWorks et arrivent à destination en 15 jours au maximum.',
    # μενού
    'The Ensemble': "L'Ensemble",
    'A few words about the ensemble': "Quelques mots sur l'ensemble",
    'Biography': 'Biographie',
    'Testimonials': 'Ils ont dit de nous',
    'Performances': 'Concerts',
    'Members': 'Les membres',
    'Media': 'Média',
    'Photos': 'Photos',
    'Videos': 'Vidéos',
    'Contact': 'Contact',
    'Shop': 'Boutique',
    'Blog': 'Blog',
    'Events': 'Concerts',
    'Photo Gallery': 'Galerie photo',
    'Video Gallery': 'Galerie vidéo',
    'Support our Projects': 'Soutenez nos projets',
    'Terms of Use': "Conditions d'utilisation",
    'Privacy Policy': 'Politique de confidentialité',
    'Read more': 'En savoir plus',
    'ALL PERFORMANCES': 'TOUS LES CONCERTS',
    "Don't miss the full video!": 'Ne manquez pas la vidéo complète !',
    'Company details': "Coordonnées de l'organisme",
    'Phonodia Vocal Ensemble': 'Phonodia — Ensemble vocal',
    'Order details': 'Détails de la commande',
    # κατάστημα
    'Cart': 'Panier', 'Size': 'Taille', 'Colour': 'Couleur', 'Quantity': 'Quantité',
    'Add to basket': 'Ajouter au panier', 'Added to your basket': 'Ajouté à votre panier',
    'Choose a size and a colour': 'Choisissez une taille et une couleur',
    'Your basket is currently empty.': 'Votre panier est vide.',
    'Total': 'Total', 'Proceed to checkout': 'Passer la commande', 'Remove': 'Retirer',
    'Continue shopping': 'Poursuivre vos achats', 'Product': 'Produit', 'Price': 'Prix',
    'Select options': 'Choisir', 'Click the photo to enlarge': 'Cliquez sur la photo pour agrandir',
    'Your basket': 'Votre panier',
    'Payment is completed securely through Viva — cards, Apple Pay, Google Pay and IRIS.':
        'Le paiement est effectué en toute sécurité via Viva — cartes, Apple Pay, Google Pay et IRIS.',
    'Items are produced on demand and shipped by Needleworks.':
        'Les articles sont fabriqués à la commande et expédiés par Needleworks.',
    # σελίδα παραγγελίας
    'Order details': 'Détails de la commande', 'Full name': 'Nom et prénom',
    'Email': 'E-mail', 'Phone': 'Téléphone', 'Delivery address': 'Adresse de livraison',
    'City': 'Ville', 'Postcode': 'Code postal', 'Note (optional)': 'Remarque (facultatif)',
    'Send order': 'Envoyer la commande',
    'Please fill in the required fields.': 'Veuillez remplir les champs obligatoires.',
    'Your basket is empty. Please choose a product first.':
        "Votre panier est vide. Choisissez d'abord un article.",
    'Your order is ready. Your email program is opening so you can send it.':
        "Votre commande est prête. Votre logiciel de messagerie s'ouvre pour l'envoyer.",
    'Your order': 'Votre commande', 'New order': 'Nouvelle commande',
    'Fill in your details. You will receive a reply with the payment method and the delivery '
    'time. Nothing is charged at this step.':
        'Renseignez vos coordonnées. Vous recevrez une réponse avec le mode de paiement et le '
        'délai de livraison. Rien ne vous est débité à cette étape.',
    # φόρμα επικοινωνίας
    'Feel free to contact us': 'Écrivez-nous',
    'Follow us on social media or send us an email': 'Suivez-nous sur les réseaux ou écrivez-nous',
    'Send us a message': 'Envoyez-nous un message',
    'I agree that my details may be used for our communication.':
        'J’accepte que mes coordonnées soient utilisées pour notre correspondance.',
    'Please enter your name': 'Veuillez saisir votre nom',
    'Please enter a correct email address': 'Veuillez saisir une adresse e-mail valide',
    'Please enter a message': 'Veuillez saisir un message',
    'Send': 'Envoyer',
    'Your message was sent successfully. Thanks!': 'Votre message a bien été envoyé. Merci !',
    'Cannot send mail, an error occurred while delivering this message. Please try again later.':
        "Envoi impossible : une erreur est survenue. Veuillez réessayer plus tard.",
}


def load_map():
    """αγγλικό -> γαλλικό."""
    if os.path.exists(FR):
        m = dict(json.load(open(FR, encoding='utf-8')))
    else:
        data = open(FR_B64).read() if os.path.exists(FR_B64) else fetch_b64()
        m = json.loads(gzip.decompress(base64.b64decode(data)).decode('utf-8'))
    for en, fr in UI.items():                 # τα δικά μας υπερισχύουν
        m[fp(en)] = fr
    return m


def relink(el):
    """κάθε σύνδεσμος που δείχνει στα αγγλικά, δείχνει τώρα στα γαλλικά."""
    for attr in ('href', 'data-href', 'src'):
        for node in el.xpath('.//*[@%s]' % attr):
            v = node.get(attr)
            if not v or v.startswith(('http', '//', 'mailto:', '#', '/img/')):
                continue
            nv = re.sub(r'(^|/)en/', r'\1fr/', v)
            if nv != v:
                node.set(attr, nv)


def apply_to(path, m):
    r = LH.parse(path).getroot()
    relink(r)
    r.set('lang', 'fr')
    hits = 0

    def sub(s):
        if not s or not s.strip():
            return s, False
        norm = ' '.join(s.split())
        out = m.get(fp(norm))
        if out is None and norm.endswith(' *'):         # υποχρεωτικά πεδία φόρμας
            base = m.get(fp(norm[:-2].strip()))
            if base:
                out = base + ' *'
        if out is None:
            return s, False
        # κρατάμε τα κενά γύρω-γύρω, γιατί το θέμα βασίζεται σε αυτά
        pre = s[:len(s) - len(s.lstrip())]
        post = s[len(s.rstrip()):]
        return pre + out + post, True

    # ο τίτλος της σελίδας είναι «Κάτι - Phonodia»· μεταφράζεται κομμάτι-κομμάτι
    for tt in r.xpath('//title'):
        if tt.text:
            parts = [p.strip() for p in tt.text.split(' - ')]
            new = ' - '.join(m.get(fp(x), x) for x in parts)
            if new != tt.text:
                tt.text = new; hits += 1

    for el in r.iter():
        if el.tag == 'title':
            continue
        if not isinstance(el.tag, str) or el.tag in ('script', 'style'):
            continue
        for attr in TEXT_ATTRS:
            v = el.get(attr)
            if v:
                nv, ch = sub(v)
                if ch:
                    el.set(attr, nv); hits += 1
        for name in ('text', 'tail'):
            v = getattr(el, name)
            if v:
                nv, ch = sub(v)
                if ch:
                    setattr(el, name, nv); hits += 1

    # ο διακόπτης γλώσσας: από τα γαλλικά δείχνουμε στα ελληνικά
    for a in r.xpath('//li[contains(@class,"lang-item")]//a'):
        a.set('title', LANG_LABEL['el'])
        for img in a.xpath('.//img'):
            img.set('alt', LANG_LABEL['el'])

    open(path, 'w', encoding='utf-8').write(
        '<!DOCTYPE html>\n' + LH.tostring(r, encoding='unicode', method='html'))
    return hits


FLAG_SVG = {
    'el': ('<svg viewBox="0 0 27 18" class="lc_flag"><rect width="27" height="18" fill="#0d5eaf"/>'
           '<g fill="#fff"><rect y="2" width="27" height="2"/><rect y="6" width="27" height="2"/>'
           '<rect y="10" width="27" height="2"/><rect y="14" width="27" height="2"/></g>'
           '<rect width="10" height="10" fill="#0d5eaf"/>'
           '<g fill="#fff"><rect x="4" width="2" height="10"/><rect y="4" width="10" height="2"/></g></svg>'),
    'en': ('<svg viewBox="0 0 27 18" class="lc_flag"><rect width="27" height="18" fill="#012169"/>'
           '<path d="M0,0 27,18 M27,0 0,18" stroke="#fff" stroke-width="3.6"/>'
           '<path d="M0,0 27,18 M27,0 0,18" stroke="#C8102E" stroke-width="2.2"/>'
           '<path d="M13.5,0 V18 M0,9 H27" stroke="#fff" stroke-width="6"/>'
           '<path d="M13.5,0 V18 M0,9 H27" stroke="#C8102E" stroke-width="3.6"/></svg>'),
    'fr': ('<svg viewBox="0 0 27 18" class="lc_flag"><rect width="9" height="18" fill="#002395"/>'
           '<rect x="9" width="9" height="18" fill="#fff"/>'
           '<rect x="18" width="9" height="18" fill="#ED2939"/></svg>'),
}

FLAG_CSS = """
/* --- διακόπτης γλώσσας: τρεις σημαίες (απόφαση Ιωάννη Ιδομενέως, 18 Αυγ 2026) --- */
li.lc_langs{display:flex!important;align-items:center;gap:11px}
li.lc_langs a{display:block!important;line-height:0;padding:0!important;opacity:.5;
  transition:opacity .2s ease;border:0!important}
li.lc_langs a:hover{opacity:1}
li.lc_langs a.on{opacity:1;box-shadow:0 0 0 2px #ff9568;border-radius:1px}
svg.lc_flag{display:block;width:25px;height:16px;border-radius:1px}
@media (max-width:1024px){li.lc_langs{gap:14px}svg.lc_flag{width:28px;height:18px}}
"""


def _targets(rel_path, el_href):
    """Πού πάει η κάθε γλώσσα από τη σελίδα rel_path (π.χ. 'en/testimonials/index.html')."""
    parts = rel_path.split('/')
    depth = len(parts) - 1
    up = '../' * depth
    if parts[0] == 'en':
        base = '/'.join(parts[1:])
        return {'el': el_href, 'en': None, 'fr': up + 'fr/' + base}
    if parts[0] == 'fr':
        base = '/'.join(parts[1:])
        return {'el': el_href, 'en': up + 'en/' + base, 'fr': None}
    # ελληνική σελίδα: το el_href δείχνει ήδη στην αγγλική
    fr = re.sub(r'(^|/)en/', r'\1fr/', el_href) if el_href else None
    return {'el': None, 'en': el_href, 'fr': fr}


def lang_switcher():
    """Αντικαθιστά τον διακόπτη γλώσσας με τρεις σημαίες, σε κάθε σελίδα."""
    names = {'el': 'Ελληνικά', 'en': 'English', 'fr': 'Français'}
    order = ('el', 'en', 'fr')
    done = 0
    for path in glob.glob(OUT + '/**/index.html', recursive=True):
        rel = os.path.relpath(path, OUT)
        cur = 'en' if rel.startswith('en/') else ('fr' if rel.startswith('fr/') else 'el')
        r = LH.parse(path).getroot()
        changed = False
        for ul in r.xpath('//ul[contains(@class,"menu")]'):
            items = ul.xpath('./li[contains(@class,"lang-item")]')
            if not items:
                continue
            el_href = None
            for a in items[0].xpath('.//a[@href]'):
                el_href = a.get('href'); break
            tg = _targets(rel, el_href)
            html = '<li class="menu-item lc_langs">'
            for lg in order:
                href = '#' if lg == cur else (tg.get(lg) or '#')
                html += '<a href="%s" title="%s" hreflang="%s"%s>%s</a>' % (
                    href, names[lg], lg, ' class="on"' if lg == cur else '', FLAG_SVG[lg])
            html += '</li>'
            items[0].addprevious(LH.fragment_fromstring(html))
            for li in items:
                li.getparent().remove(li)
            for li in ul.xpath('./li[contains(@class,"lang-extra")]'):
                li.getparent().remove(li)
            changed = True
        if changed:
            open(path, 'w', encoding='utf-8').write(
                '<!DOCTYPE html>\n' + LH.tostring(r, encoding='unicode', method='html'))
            done += 1
    css = OUT + '/assets/site.css'
    if os.path.exists(css) and 'li.lc_langs' not in open(css, encoding='utf-8').read():
        open(css, 'a', encoding='utf-8').write(FLAG_CSS)
    print('lang_switcher: τρεις σημαίες σε %d σελίδες' % done)


def main():
    src, dst = OUT + '/en', OUT + '/fr'
    if not os.path.isdir(src):
        print('translate_fr: λείπουν οι αγγλικές σελίδες'); return
    try:
        m = load_map()
    except Exception as e:
        # Αν για οποιονδήποτε λόγο δεν βρεθεί το λεξικό, η υπόλοιπη σελίδα μένει
        # ανέπαφη. Καλύτερα χωρίς γαλλικά παρά χαλασμένο χτίσιμο.
        print('translate_fr: ΠΑΡΑΛΕΙΠΕΤΑΙ —', e); return
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    total = files = 0
    for p in sorted(glob.glob(dst + '/**/index.html', recursive=True)):
        n = apply_to(p, m)
        if n:
            files += 1; total += n
    print('translate_fr: %d αντικαταστάσεις σε %d σελίδες (%d αποδόσεις)'
          % (total, files, len(set(m.values()))))
    lang_switcher()      # τρεις σημαίες παντού


if __name__ == '__main__':
    main()
