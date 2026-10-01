#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Kontrastdeck: Minimalpaare, die sich in genau einem Morphem unterscheiden.

Die Goethe-Beispielsaetze stellen nie zwei Formen gegenueber. Genau das
braucht man aber, um Nominalklassen und TAM-Marker zu begreifen: erst im
Paar wird sichtbar, welches Morphem die Bedeutung traegt.

Deutsche und englische Formen stehen ausgeschrieben in den Tabellen. Sie aus
einem Muster zu erzeugen ginge schief, weil das Deutsche Genus und Kasus
beugt und der englische Plural nicht immer auf -s endet.
"""
import csv
import adjektive as A
import glossen_en as GE
import konkordanz as K

FELDER = ['id', 'kontrasttyp', 'kontrasttyp_en', 'klasse', 'de_a', 'de_b',
          'en_a', 'en_b', 'sw_a', 'sw_b', 'gloss_a_mo', 'gloss_a_la',
          'gloss_a_la_en', 'gloss_b_mo', 'gloss_b_la', 'gloss_b_la_en',
          'unterschied', 'klassen', 'klassen_en', 'konkordanz',
          'konkordanz_en', 'hinweis', 'hinweis_en', 'tags']

# Sekela liest kein Deutsch; die Korrekturboegen brauchen jede Zeile englisch.
TYP_EN = {
    'Numerus': 'number', 'Konkordanz-Kaskade': 'agreement cascade',
    'Demonstrativ': 'demonstrative', 'Possessiv': 'possessive',
    'TAM': 'tense/aspect', 'Negation': 'negation',
    'Negation nach Zeit': 'negation by tense',
    'Numerus + TAM': 'number + tense',
}

HINWEIS_EN = {
    'Nasalpräfix n- vor z-': 'nasal prefix n- before z-',
    'kein Nasalpräfix vor k-': 'no nasal prefix before k-',
    'Nasalpräfix wird m- vor p-': 'nasal prefix becomes m- before p-',
    'Kl. 5 nimmt hier ji-, sonst Nullpräfix':
        'class 5 takes ji- here, zero prefix otherwise',
    'Kl. 5 hat Nullpräfix': 'class 5 has a zero prefix',
}


class Nomen:
    """Ein Nomen mit allem, was die Satzschablonen brauchen."""

    def __init__(self, sg, pl, ks, kp, label,
                 de_akk_sg, de_akk_pl, de_nom_sg, de_nom_pl, en_sg, en_pl):
        self.sg, self.pl, self.ks, self.kp, self.label = sg, pl, ks, kp, label
        self.de_akk_sg, self.de_akk_pl = de_akk_sg, de_akk_pl
        self.de_nom_sg, self.de_nom_pl = de_nom_sg, de_nom_pl
        self.en_sg, self.en_pl = en_sg, en_pl

    @property
    def en_bare_sg(self):
        """'a good book' -> 'book'"""
        return self.en_sg.split(' ')[-1]

    @property
    def en_bare_pl(self):
        return self.en_pl.split(' ')[-1]


# de_akk: "Ich habe <...>"  ·  de_nom: "<...> des Lehrers ist teuer"
NOMEN = [
    Nomen('mtoto', 'watoto', '1', '2', 'Kind',
          'ein gutes Kind', 'gute Kinder',
          'Dieses große Kind', 'Diese großen Kinder',
          'a good child', 'good children'),
    Nomen('mwalimu', 'walimu', '1', '2', 'Lehrer',
          'einen guten Lehrer', 'gute Lehrer',
          'Dieser große Lehrer', 'Diese großen Lehrer',
          'a good teacher', 'good teachers'),
    Nomen('mgeni', 'wageni', '1', '2', 'Gast',
          'einen guten Gast', 'gute Gäste',
          'Dieser große Gast', 'Diese großen Gäste',
          'a good guest', 'good guests'),
    Nomen('mti', 'miti', '3', '4', 'Baum',
          'einen guten Baum', 'gute Bäume',
          'Dieser große Baum', 'Diese großen Bäume',
          'a good tree', 'good trees'),
    Nomen('mkate', 'mikate', '3', '4', 'Brot',
          'ein gutes Brot', 'gute Brote',
          'Dieses große Brot', 'Diese großen Brote',
          'a good loaf', 'good loaves'),
    Nomen('mji', 'miji', '3', '4', 'Stadt',
          'eine gute Stadt', 'gute Städte',
          'Diese große Stadt', 'Diese großen Städte',
          'a good town', 'good towns'),
    Nomen('gari', 'magari', '5', '6', 'Auto',
          'ein gutes Auto', 'gute Autos',
          'Dieses große Auto', 'Diese großen Autos',
          'a good car', 'good cars'),
    Nomen('duka', 'maduka', '5', '6', 'Laden',
          'einen guten Laden', 'gute Läden',
          'Dieser große Laden', 'Diese großen Läden',
          'a good shop', 'good shops'),
    Nomen('jina', 'majina', '5', '6', 'Name',
          'einen guten Namen', 'gute Namen',
          'Dieser große Name', 'Diese großen Namen',
          'a good name', 'good names'),
    Nomen('kitabu', 'vitabu', '7', '8', 'Buch',
          'ein gutes Buch', 'gute Bücher',
          'Dieses große Buch', 'Diese großen Bücher',
          'a good book', 'good books'),
    Nomen('kiti', 'viti', '7', '8', 'Stuhl',
          'einen guten Stuhl', 'gute Stühle',
          'Dieser große Stuhl', 'Diese großen Stühle',
          'a good chair', 'good chairs'),
    Nomen('chumba', 'vyumba', '7', '8', 'Zimmer',
          'ein gutes Zimmer', 'gute Zimmer',
          'Dieses große Zimmer', 'Diese großen Zimmer',
          'a good room', 'good rooms'),
    Nomen('barua', 'barua', '9', '10', 'Brief',
          'einen guten Brief', 'gute Briefe',
          'Dieser große Brief', 'Diese großen Briefe',
          'a good letter', 'good letters'),
    Nomen('nyumba', 'nyumba', '9', '10', 'Haus',
          'ein gutes Haus', 'gute Häuser',
          'Dieses große Haus', 'Diese großen Häuser',
          'a good house', 'good houses'),
    Nomen('simu', 'simu', '9', '10', 'Telefon',
          'ein gutes Telefon', 'gute Telefone',
          'Dieses große Telefon', 'Diese großen Telefone',
          'a good telephone', 'good telephones'),
    Nomen('ufunguo', 'funguo', '11', '10', 'Schlüssel',
          'einen guten Schlüssel', 'gute Schlüssel',
          'Dieser große Schlüssel', 'Diese großen Schlüssel',
          'a good key', 'good keys'),
    Nomen('wimbo', 'nyimbo', '11', '10', 'Lied',
          'ein gutes Lied', 'gute Lieder',
          'Dieses große Lied', 'Diese großen Lieder',
          'a good song', 'good songs'),
    Nomen('ukuta', 'kuta', '11', '10', 'Wand',
          'eine gute Wand', 'gute Wände',
          'Diese große Wand', 'Diese großen Wände',
          'a good wall', 'good walls'),
]

# (Stamm, deutsch, Glosse des Objekts, Objekt, deutsches Objekt, engl. Objekt,
#  deutsches Partizip, englische ing-Form, englisches Partizip)
VERBEN = [
    ('som', 'lesen', 'ki-tabu', 'kitabu', 'das Buch', 'the book',
     'gelesen', 'reading', 'read'),
    ('nunu', 'kaufen', 'mi-kate', 'mikate', 'die Brote', 'the loaves',
     'gekauft', 'buying', 'bought'),
    ('andik', 'schreiben', 'barua', 'barua', 'den Brief', 'the letter',
     'geschrieben', 'writing', 'written'),
    ('on', 'sehen', 'ma-gari', 'magari', 'die Autos', 'the cars',
     'gesehen', 'seeing', 'seen'),
    ('pik', 'kochen', 'chakula', 'chakula', 'das Essen', 'the food',
     'gekocht', 'cooking', 'cooked'),
]

# TAM-Marker mit den deutschen und englischen Satzrahmen
TAM = {
    'na': ('PRÄS', lambda v, o, p: f'Ich {v.replace("en", "e")} gerade {o}.',
           lambda v, o, i, pp: f'I am {i} {o}.'),
    'li': ('PRÄT', lambda v, o, p: f'Ich {p.replace("ge", "").replace("t", "te")} {o} gestern.'
           if False else f'Gestern {v.replace("en", "te")} ich {o}.',
           lambda v, o, i, pp: f'I {pp} {o} yesterday.'),
    'me': ('PERF', lambda v, o, p: f'Ich habe {o} schon {p}.',
           lambda v, o, i, pp: f'I have already {pp} {o}.'),
    'ta': ('FUT', lambda v, o, p: f'Morgen werde ich {o} {v}.',
           lambda v, o, i, pp: f'I will {v if False else ""}{pp if False else ""}{o and ""}'),
}

PERSONEN = [('ni', 'si', '1SG', 'Ich', 'I', 'lese', 'read', 'read'),
            ('u', 'hu', '2SG', 'Du', 'You', 'liest', 'read', 'read'),
            ('a', 'ha', '3SG', 'Er', 'He', 'liest', 'reads', 'read'),
            ('tu', 'hatu', '1PL', 'Wir', 'We', 'lesen', 'read', 'read'),
            ('m', 'ham', '2PL', 'Ihr', 'You', 'lest', 'read', 'read'),
            ('wa', 'hawa', '3PL', 'Sie', 'They', 'lesen', 'read', 'read')]

POSSESSIV = [('angu', 'mein', 'my'), ('ako', 'dein', 'your'),
             ('ake', 'sein', 'his'), ('etu', 'unser', 'our')]


def tag(*teile):
    return ' '.join(t.replace(' ', '_') for t in teile if t)


def gen_morphem(gen):
    """cha -> ch-a, ya -> y-a"""
    return gen[:-1] + '-a'


def zeilen():
    out = []

    def add(**kw):
        out.append({'id': f'K{len(out) + 1:03d}', **kw})

    # --- 1. Numerus mit Adjektivkongruenz, zwei Adjektivstaemme -----------
    for stamm, dadj in (('zuri', 'gut'), ('dogo', 'klein')):
        for nn in NOMEN:
            a_sg, a_pl = A.form(stamm, nn.ks), A.form(stamm, nn.kp)
            m_sg, s_sg = A.segment(stamm, nn.ks)
            m_pl, s_pl = A.segment(stamm, nn.kp)
            hw = A.hinweis(stamm, nn.ks) or A.hinweis(stamm, nn.kp)
            de_a = nn.de_akk_sg if stamm == 'zuri' else \
                nn.de_akk_sg.replace('gute', 'kleine').replace('gutes', 'kleines')
            de_b = nn.de_akk_pl if stamm == 'zuri' else \
                nn.de_akk_pl.replace('gute', 'kleine')
            en_adj = 'good' if stamm == 'zuri' else 'small'
            en_a = nn.en_sg if stamm == 'zuri' else nn.en_sg.replace('good', 'small')
            en_b = nn.en_pl if stamm == 'zuri' else nn.en_pl.replace('good', 'small')
            # Bei Kl. 9/10 sind Nomen UND Adjektiv in beiden Numeri gleich.
            # Ein "Nina barua nzuri"-Paar waere zweimal derselbe Satz. Dort
            # muss das Demonstrativ den Numerus tragen -- genau der Punkt,
            # den diese Klasse lehrt.
            unsichtbar = nn.sg == nn.pl and a_sg == a_pl
            if unsichtbar:
                d_sg, d_pl = K.reihe(nn.ks)['dem_nah'], K.reihe(nn.kp)['dem_nah']
                felder = dict(
                    de_a=f'{nn.de_nom_sg.split()[0]} {nn.label} ist {dadj}.',
                    de_b=f'Diese {nn.de_akk_pl.split(" ", 1)[1]} sind {dadj}.',
                    en_a=f'This {nn.en_bare_sg} is {en_adj}.',
                    en_b=f'These {nn.en_bare_pl} are {en_adj}.',
                    sw_a=f'{nn.sg.capitalize()} {d_sg} ni {a_sg}.',
                    sw_b=f'{nn.pl.capitalize()} {d_pl} ni {a_pl}.',
                    gloss_a_mo=f'{nn.sg} {d_sg} ni {m_sg}',
                    gloss_a_la=f'KL{nn.ks}.{nn.label} KL{nn.ks}.DEM KOP '
                               f'KL{nn.ks}{s_sg}{dadj}',
                    gloss_b_mo=f'{nn.pl} {d_pl} ni {m_pl}',
                    gloss_b_la=f'KL{nn.kp}.{nn.label} KL{nn.kp}.DEM KOP '
                               f'KL{nn.kp}{s_pl}{dadj}',
                    unterschied=f'{d_sg}  →  {d_pl}')
            else:
                felder = dict(
                    de_a=f'Ich habe {de_a}.', de_b=f'Ich habe {de_b}.',
                    en_a=f'I have {en_a}.', en_b=f'I have {en_b}.',
                    sw_a=f'Nina {nn.sg} {a_sg}.', sw_b=f'Nina {nn.pl} {a_pl}.',
                    gloss_a_mo=f'ni-na {nn.sg} {m_sg}',
                    gloss_a_la=f'1SG-haben KL{nn.ks}.{nn.label} '
                               f'KL{nn.ks}{s_sg}{dadj}',
                    gloss_b_mo=f'ni-na {nn.pl} {m_pl}',
                    gloss_b_la=f'1SG-haben KL{nn.kp}.{nn.label} '
                               f'KL{nn.kp}{s_pl}{dadj}',
                    unterschied=f'{nn.sg} {a_sg}  →  {nn.pl} {a_pl}')
            add(kontrasttyp='Numerus', klasse=f'{nn.ks}/{nn.kp}', **felder,
                klassen=K.klassen_text(nn.ks, nn.kp, nn.sg, nn.pl),
                konkordanz=K.konkordanz_text(nn.ks) + ' · ' + K.konkordanz_text(nn.kp),
                hinweis=('Weder Nomen noch Adjektiv zeigen den Numerus — '
                         'nur das Demonstrativ tut es. Das ist die Eigenart '
                         'der Kl. 9/10.' if unsichtbar else
                         hw or (f'Adjektiv wechselt mit: {a_sg} → {a_pl}')),
                hinweis_en=('Neither the noun nor the adjective shows number — '
                            'only the demonstrative does. This is what makes '
                            'classes 9/10 special.' if unsichtbar else
                            HINWEIS_EN.get(hw, '') or
                            f'the adjective changes with it: {a_sg} → {a_pl}'),
                tags=tag('A1', 'SD1', 'kontrast', 'numerus',
                         f'kl{nn.ks}', f'kl{nn.kp}'))

    # --- 2. Konkordanz-Kaskade --------------------------------------------
    for nn in NOMEN:
        rs, rp = K.reihe(nn.ks), K.reihe(nn.kp)
        a_sg, a_pl = A.form('kubwa', nn.ks), A.form('kubwa', nn.kp)
        m_sg, s_sg = A.segment('kubwa', nn.ks)
        m_pl, s_pl = A.segment('kubwa', nn.kp)
        add(kontrasttyp='Konkordanz-Kaskade', klasse=f'{nn.ks}/{nn.kp}',
            de_a=f'{nn.de_nom_sg} des Lehrers',
            de_b=f'{nn.de_nom_pl} des Lehrers',
            en_a=f"this big {nn.en_bare_sg} of the teacher",
            en_b=f"these big {nn.en_bare_pl} of the teacher",
            sw_a=f'{nn.sg} {a_sg} {rs["dem_nah"]} {rs["gen"]} mwalimu',
            sw_b=f'{nn.pl} {a_pl} {rp["dem_nah"]} {rp["gen"]} mwalimu',
            gloss_a_mo=f'{nn.sg} {m_sg} {rs["dem_nah"]} {gen_morphem(rs["gen"])} mw-alimu',
            gloss_a_la=f'KL{nn.ks}.{nn.label} KL{nn.ks}{s_sg}groß KL{nn.ks}.DEM '
                       f'KL{nn.ks}-GEN KL1-Lehrer',
            gloss_b_mo=f'{nn.pl} {m_pl} {rp["dem_nah"]} {gen_morphem(rp["gen"])} mw-alimu',
            gloss_b_la=f'KL{nn.kp}.{nn.label} KL{nn.kp}{s_pl}groß KL{nn.kp}.DEM '
                       f'KL{nn.kp}-GEN KL1-Lehrer',
            unterschied=f'{a_sg} {rs["dem_nah"]} {rs["gen"]}  →  '
                        f'{a_pl} {rp["dem_nah"]} {rp["gen"]}',
            klassen=K.klassen_text(nn.ks, nn.kp, nn.sg, nn.pl),
            konkordanz=K.konkordanz_text(nn.ks) + ' · ' + K.konkordanz_text(nn.kp),
            hinweis='Adjektiv, Demonstrativ und Genitiv wechseln gemeinsam — '
                    'die Klasse steuert das ganze Satzgefüge',
            hinweis_en='adjective, demonstrative and genitive all change '
                       'together — the class governs the whole phrase',
            tags=tag('A1', 'SD1', 'kontrast', 'kaskade',
                     f'kl{nn.ks}', f'kl{nn.kp}'))

    # --- 3. Demonstrativ nah gegen fern -----------------------------------
    for nn in NOMEN:
        rs = K.reihe(nn.ks)
        add(kontrasttyp='Demonstrativ', klasse=nn.ks,
            de_a=f'{nn.de_nom_sg.split()[0].lower()} {nn.label} hier',
            de_b=({'Dieser': 'jener', 'Dieses': 'jenes',
                   'Diese': 'jene'}[nn.de_nom_sg.split()[0]]
                  + f' {nn.label} dort'),
            en_a=f'this {nn.en_bare_sg} here',
            en_b=f'that {nn.en_bare_sg} there',
            sw_a=f'{nn.sg} {rs["dem_nah"]}',
            sw_b=f'{nn.sg} {rs["dem_fern"]}',
            gloss_a_mo=f'{nn.sg} {rs["dem_nah"]}',
            gloss_a_la=f'KL{nn.ks}.{nn.label} KL{nn.ks}.DEM.nah',
            gloss_b_mo=f'{nn.sg} {rs["dem_fern"]}',
            gloss_b_la=f'KL{nn.ks}.{nn.label} KL{nn.ks}.DEM.fern',
            unterschied=f'{rs["dem_nah"]}  →  {rs["dem_fern"]}',
            klassen=K.klassen_text(nn.ks, nn.kp, nn.sg, nn.pl),
            konkordanz=K.konkordanz_text(nn.ks),
            hinweis='Nähe und Ferne haben je eine eigene Demonstrativreihe, '
                    'beide nach der Klasse gebildet',
            hinweis_en='near and far each have their own demonstrative series, '
                       'both formed from the class',
            tags=tag('A1', 'SD1', 'kontrast', 'demonstrativ', f'kl{nn.ks}'))

    # --- 4. Possessiv ueber die Klassen -----------------------------------
    for nn in NOMEN:
        rs, rp = K.reihe(nn.ks), K.reihe(nn.kp)
        # Kl. 1/2 hat in beiden Numeri w-: das waere kein Kontrast.
        if rs['poss'] == rp['poss']:
            continue
        p_sg = rs['poss'][:-1] + POSSESSIV[0][0]
        p_pl = rp['poss'][:-1] + POSSESSIV[0][0]
        add(kontrasttyp='Possessiv', klasse=f'{nn.ks}/{nn.kp}',
            de_a=f'mein {nn.label}',
            de_b=f'meine {nn.de_akk_pl.split(" ", 1)[1]}',
            en_a=f'my {nn.en_bare_sg}', en_b=f'my {nn.en_bare_pl}',
            sw_a=f'{nn.sg} {p_sg}', sw_b=f'{nn.pl} {p_pl}',
            gloss_a_mo=f'{nn.sg} {rs["poss"]}-angu'.replace('--', '-'),
            gloss_a_la=f'KL{nn.ks}.{nn.label} KL{nn.ks}-mein',
            gloss_b_mo=f'{nn.pl} {rp["poss"]}-angu'.replace('--', '-'),
            gloss_b_la=f'KL{nn.kp}.{nn.label} KL{nn.kp}-mein',
            unterschied=f'{p_sg}  →  {p_pl}',
            klassen=K.klassen_text(nn.ks, nn.kp, nn.sg, nn.pl),
            konkordanz=K.konkordanz_text(nn.ks) + ' · ' + K.konkordanz_text(nn.kp),
            hinweis='Der Possessivstamm -angu bleibt, nur das Konkordanz'
                    'präfix wechselt mit der Klasse',
            hinweis_en='the possessive stem -angu stays; only the agreement '
                       'prefix changes with the class',
            tags=tag('A1', 'SD1', 'kontrast', 'possessiv',
                     f'kl{nn.ks}', f'kl{nn.kp}'))

    # --- 5. TAM am selben Verb --------------------------------------------
    paare = (('na', 'me'), ('na', 'li'), ('na', 'ta'),
             ('li', 'me'), ('li', 'ta'), ('me', 'ta'))
    rahmen_de = {
        'na': lambda v, o: f'Ich {v} gerade {o}.',
        'li': lambda v, o: f'Gestern {v} ich {o}.',
        'me': lambda v, o: f'Ich habe {o} schon {{pp}}.',
        'ta': lambda v, o: f'Morgen {v} ich {o}.',
    }
    praes = {'som': 'lese', 'nunu': 'kaufe', 'andik': 'schreibe',
             'on': 'sehe', 'pik': 'koche'}
    praet = {'som': 'las', 'nunu': 'kaufte', 'andik': 'schrieb',
             'on': 'sah', 'pik': 'kochte'}
    OBJ_LA = {'ki-tabu': 'KL7-Buch', 'mi-kate': 'KL4-Brot',
              'barua': 'KL9.Brief', 'ma-gari': 'KL6-Auto',
              'chakula': 'KL7.Essen'}
    for stamm, dv, obj_mo, obj_sw, dobj, eobj, pp, ing, epp in VERBEN:
        obj_la = OBJ_LA[obj_mo]
        for t1, t2 in paare:
            def de(t):
                if t == 'na':
                    return f'Ich {praes[stamm]} gerade {dobj}.'
                if t == 'li':
                    return f'Gestern {praet[stamm]} ich {dobj}.'
                if t == 'me':
                    return f'Ich habe {dobj} schon {pp}.'
                return f'Morgen werde ich {dobj} {dv}.'

            def en(t):
                if t == 'na':
                    return f'I am {ing} {eobj} right now.'
                if t == 'li':
                    return f'I {epp} {eobj} yesterday.'
                if t == 'me':
                    return f'I have already {epp} {eobj}.'
                return f'I will {dv_en[stamm]} {eobj} tomorrow.'

            dv_en = {'som': 'read', 'nunu': 'buy', 'andik': 'write',
                     'on': 'see', 'pik': 'cook'}
            l1, l2 = {'na': 'PRÄS', 'li': 'PRÄT', 'me': 'PERF',
                      'ta': 'FUT'}[t1], {'na': 'PRÄS', 'li': 'PRÄT',
                                         'me': 'PERF', 'ta': 'FUT'}[t2]
            add(kontrasttyp='TAM', klasse='',
                de_a=de(t1), de_b=de(t2), en_a=en(t1), en_b=en(t2),
                sw_a=f'Ni{t1}{stamm}a {obj_sw}.',
                sw_b=f'Ni{t2}{stamm}a {obj_sw}.',
                gloss_a_mo=f'ni-{t1}-{stamm}-a {obj_mo}',
                gloss_a_la=f'1SG-{l1}-{dv}-IND {obj_la}',
                gloss_b_mo=f'ni-{t2}-{stamm}-a {obj_mo}',
                gloss_b_la=f'1SG-{l2}-{dv}-IND {obj_la}',
                unterschied=f'-{t1}-  →  -{t2}-',
                klassen='', konkordanz='',
                hinweis=f'Nur der TAM-Marker wechselt: -{t1}- {l1} gegen '
                        f'-{t2}- {l2}. Stamm und Endvokal bleiben.',
                hinweis_en=f'only the tense marker changes: -{t1}- against '
                           f'-{t2}-. Stem and final vowel stay the same.',
                tags=tag('A1', 'SD1', 'kontrast', 'tam', f'tam-{t1}', f'tam-{t2}'))

    # --- 6. Negation ueber die Personen -----------------------------------
    for pos, neg, person, dp, ep, dv, ev, _ in PERSONEN:
        add(kontrasttyp='Negation', klasse='7/8',
            de_a=f'{dp} {dv} das Buch.', de_b=f'{dp} {dv} das Buch nicht.',
            en_a=f'{ep} {ev} the book.',
            en_b=f'{ep} {"does" if person == "3SG" else "do"} not read the book.',
            sw_a=f'{pos.capitalize()}nasoma kitabu.',
            sw_b=f'{neg.capitalize()}somi kitabu.',
            gloss_a_mo=f'{pos}-na-som-a ki-tabu',
            gloss_a_la=f'{person}-PRÄS-lesen-IND KL7-Buch',
            gloss_b_mo=f'{neg}-som-i ki-tabu',
            gloss_b_la=f'{person}.NEG-lesen-NEG KL7-Buch',
            unterschied=f'{pos}-na-…-a  →  {neg}-…-i',
            klassen=K.klassen_text('7', '8', 'kitabu', 'vitabu'),
            konkordanz=K.konkordanz_text('7'),
            hinweis='Die Negation tauscht das Subjektpräfix, streicht den '
                    'TAM-Marker und ändert den Endvokal zu -i',
            hinweis_en='negation swaps the subject prefix, drops the tense '
                       'marker and changes the final vowel to -i',
            tags=tag('A1', 'SD1', 'kontrast', 'negation', f'p-{person}'))

    # --- 7. Negation durch die Zeiten -------------------------------------
    TAM_LABEL = {'na': 'PRÄS', 'li': 'PRÄT', 'me': 'PERF', 'ta': 'FUT'}
    for t, neg_mo, neg_la, dpos, dneg, epos, eneg in (
            ('na', 'si-som-i', '1SG.NEG-lesen-NEG',
             'Ich lese das Buch.', 'Ich lese das Buch nicht.',
             'I am reading the book.', 'I am not reading the book.'),
            ('li', 'si-ku-som-a', '1SG.NEG-PRÄT.NEG-lesen-IND',
             'Ich las das Buch.', 'Ich las das Buch nicht.',
             'I read the book.', 'I did not read the book.'),
            ('me', 'si-ja-som-a', '1SG.NEG-PERF.NEG-lesen-IND',
             'Ich habe das Buch gelesen.', 'Ich habe das Buch noch nicht gelesen.',
             'I have read the book.', 'I have not read the book yet.'),
            ('ta', 'si-ta-som-a', '1SG.NEG-FUT-lesen-IND',
             'Ich werde das Buch lesen.', 'Ich werde das Buch nicht lesen.',
             'I will read the book.', 'I will not read the book.')):
        add(kontrasttyp='Negation nach Zeit', klasse='7/8',
            de_a=dpos, de_b=dneg, en_a=epos, en_b=eneg,
            sw_a=f'Ni{t}soma kitabu.',
            sw_b=neg_mo.replace('-', '').capitalize() + ' kitabu.',
            gloss_a_mo=f'ni-{t}-som-a ki-tabu',
            gloss_a_la=f'1SG-{TAM_LABEL[t]}-lesen-IND KL7-Buch',
            gloss_b_mo=f'{neg_mo} ki-tabu',
            gloss_b_la=f'{neg_la} KL7-Buch',
            unterschied=f'ni-{t}-  →  {neg_mo.split("-som")[0]}-',
            klassen=K.klassen_text('7', '8', 'kitabu', 'vitabu'),
            konkordanz=K.konkordanz_text('7'),
            hinweis='Jede Zeit hat ihre eigene Negationsform — '
                    '-ku- für die Vergangenheit, -ja- für das Perfekt',
            hinweis_en='each tense has its own negative form — -ku- for the '
                       'past, -ja- for the perfect',
            tags=tag('A1', 'SD1', 'kontrast', 'negation', f'tam-{t}'))

    # --- 8. Das Ausgangsbeispiel: Numerus und TAM zugleich ----------------
    add(kontrasttyp='Numerus + TAM', klasse='7/8',
        de_a='Ich lese gerade das Buch.',
        de_b='Ich habe schon viele Bücher gelesen.',
        en_a='I am reading the book right now.',
        en_b='I have already read many books.',
        sw_a='Ninasoma kitabu.', sw_b='Nimesoma vitabu vingi.',
        gloss_a_mo='ni-na-som-a ki-tabu',
        gloss_a_la='1SG-PRÄS-lesen-IND KL7-Buch',
        gloss_b_mo='ni-me-som-a vi-tabu vi-ngi',
        gloss_b_la='1SG-PERF-lesen-IND KL8-Buch KL8-viele',
        unterschied='-na- ki-  →  -me- vi-',
        klassen=K.klassen_text('7', '8', 'kitabu', 'vitabu'),
        konkordanz=K.konkordanz_text('7') + ' · ' + K.konkordanz_text('8'),
        hinweis='Zwei Kontraste auf einmal: TAM -na- gegen -me- und '
                'Nominalklasse ki- gegen vi-',
        hinweis_en='two contrasts at once: tense -na- against -me- and noun '
                   'class ki- against vi-',
        tags=tag('A1', 'SD1', 'kontrast', 'numerus', 'tam', 'kl7', 'kl8'))
    return out


def main():
    rows = zeilen()
    glossar, fehlend = GE.lade_glossar(), set()
    for r in rows:
        r['kontrasttyp_en'] = TYP_EN.get(r['kontrasttyp'], r['kontrasttyp'])
        # Klassen- und Konkordanztexte englisch nachziehen: dieselben
        # Klassennummern, nur die Beschriftung wechselt.
        r['klassen_en'] = (r['klassen'].replace('Kl. ', 'class ')
                           .replace('kein Numeruswechsel', 'no number change')
                           .replace('Numerus nur an der Konkordanz',
                                    'number shows only in the agreement'))
        r['konkordanz_en'] = r['konkordanz'].replace('Kl.', 'class ')
        for q in ('a', 'b'):
            r[f'gloss_{q}_la_en'] = GE.uebersetze_zeile(
                r[f'gloss_{q}_la'], glossar, fehlend)
    if fehlend:
        print(f'WARNUNG: ohne englische Glosse: {", ".join(sorted(fehlend))}')
    with open('karten_kontrast.tsv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, FELDER, delimiter='\t', lineterminator='\n',
                           extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(f'karten_kontrast.tsv: {len(rows)} Minimalpaare')
    for t, n in sorted(Counter(r['kontrasttyp'] for r in rows).items()):
        print(f'  {t:24s} {n}')


if __name__ == '__main__':
    main()
