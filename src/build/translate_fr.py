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

TEXT_ATTRS = ('alt', 'title', 'placeholder', 'aria-label', 'value', 'content', 'data-pname')

# Ονόματα γλωσσών: κάθε γλώσσα λέγεται στη δική της γραφή.
LANG_LABEL = {'el': 'Ελληνικά', 'en': 'English', 'fr': 'Français'}

# Λεκτικά του καταστήματος και του μενού. Δεν υπάρχουν στη συγκομιδή, γιατί τα
# γράψαμε εμείς — άρα τα αποδίδω εδώ, ρητά και ελέγξιμα.
UI = {
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


def add_switch(lang_dir, label, target):
    """Προσθέτει έναν σύνδεσμο γλώσσας δίπλα στον υπάρχοντα διακόπτη."""
    pat = OUT + ('/**/index.html' if not lang_dir else '/' + lang_dir + '/**/index.html')
    for path in glob.glob(pat, recursive=True):
        rel = os.path.relpath(path, OUT)
        if lang_dir == '' and (rel.startswith('en/') or rel.startswith('fr/')):
            continue
        depth = rel.count('/')
        href = '../' * depth + target
        r = LH.parse(path).getroot()
        changed = False
        for ul in r.xpath('//ul[contains(@class,"menu")]'):
            if ul.xpath('./li[contains(@class,"lang-extra")]'):
                continue
            items = ul.xpath('./li[contains(@class,"lang-item")]')
            if not items:
                continue
            li = LH.fragment_fromstring(
                '<li class="menu-item lang-extra"><a href="%s">%s</a></li>' % (href, label))
            items[-1].addnext(li)
            changed = True
        if changed:
            open(path, 'w', encoding='utf-8').write(
                '<!DOCTYPE html>\n' + LH.tostring(r, encoding='unicode', method='html'))


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
    # ο σύνδεσμος «Français» στα ελληνικά και στα αγγλικά, «English» στα γαλλικά
    add_switch('', 'Français', 'fr/index.html')
    add_switch('en', 'Français', 'fr/index.html')
    add_switch('fr', 'English', 'en/index.html')


if __name__ == '__main__':
    main()
