#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Drilldeck: Nominalklassen und Konkordanzen als System abfragen.

Richtungsunabhaengig, weil Swahili-intern. Vollstaendig aus
klassen_lexikon.tsv und der Konkordanztabelle erzeugt -- eine Korrektur im
Lexikon wirkt beim naechsten Lauf auf alle betroffenen Karten.
"""
import csv
import re
import adjektive as A
import konkordanz as K

FELDER = ['id', 'typ', 'typ_en', 'klasse', 'vorderseite', 'vorderseite_en',
          'rueckseite', 'rueckseite_en', 'erklaerung', 'erklaerung_en', 'tags']

# Sekela liest kein Deutsch: jede Karte traegt ihre englische Fassung mit.
TYP_EN = {
    'Klasse bestimmen': 'identify the class',
    'Plural bilden': 'form the plural',
    'Konkordanz': 'agreement form',
    'Adjektiv angleichen': 'make the adjective agree',
    'Lückensatz': 'fill the gaps',
}
TEIL_EN = {
    'Subjektpräfix': 'subject prefix', 'Objektpräfix': 'object prefix',
    'Adjektivpräfix': 'adjective prefix', 'Genitiv': 'genitive',
    'Demonstrativ nah': 'demonstrative (near)',
    'Demonstrativ fern': 'demonstrative (far)',
    'Possessivpräfix': 'possessive prefix', 'Relativinfix': 'relative infix',
}

# Nomen, an denen sich die Konkordanz sauber zeigen laesst: regelmaessig,
# haeufig, und mit eindeutigem Klassenpaar.
AUSWAHL_KLASSEN = ('1', '3', '5', '7', '9', '11')


def lade_lexikon():
    with open('klassen_lexikon.tsv', encoding='utf-8', newline='') as fh:
        return [r for r in csv.DictReader(fh, delimiter='\t')
                if r['sw_singular'] and r['sw_singular'] != '—'
                and r['klasse_sg'] in K.TABELLE
                and len(r['sw_singular'].split()) == 1]


def kurz(de):
    """'der Fuss, -ue, e' -> 'der Fuss'.

    Die deutsche Pluralangabe der Wortliste ist auf einer Klassenkarte
    Ballast -- gefragt ist die Swahili-Klasse, nicht der deutsche Plural.
    """
    return re.split(r',\s*[-\u2013]', de)[0].strip()


# Mehr als drei Bedeutungen sprengen die Kartenbreite, ohne beim Erkennen
# des Worts noch zu helfen.
MAX_BEDEUTUNGEN = 3


def bedeutung(woerter):
    return ', '.join(woerter[:MAX_BEDEUTUNGEN])


def gruppen(lex):
    """Ein Swahili-Wort, eine Karte -- mit allen seinen Bedeutungen.

    Das Lexikon ist nach dem deutschen Stichwort gebaut, darum steht kazi
    viermal darin (Arbeit, Beruf, Job, Aufgabe). Fuer den Drill zaehlt das
    Swahili-Wort; die deutschen und englischen Bedeutungen wandern
    zusammen auf dieselbe Karte, statt dass drei davon als Dublette
    wegfallen. Das Klassenpaar gehoert in den Schluessel: bibi ist als
    'Dame' Kl. 5/6 (mabibi), als 'Oma' Kl. 9/10 -- zwei echte Karten.
    """
    aus = {}
    for r in lex:
        g = aus.setdefault(
            (r['sw_singular'], r['klasse_sg'], r['klasse_pl']),
            {**r, 'de': [], 'en': []})
        for feld, liste in (('de_nomen', g['de']), ('en_nomen', g['en'])):
            w = kurz(r[feld]) if feld == 'de_nomen' else r[feld].strip()
            if w and w not in liste:
                liste.append(w)
    return list(aus.values())


HINWEIS_EN = {
    'Nasalpräfix n- vor z-': 'nasal prefix n- before z-',
    'kein Nasalpräfix vor k-': 'no nasal prefix before k-',
    'Nasalpräfix wird m- vor p-': 'nasal prefix becomes m- before p-',
    'Kl. 5 nimmt hier ji-, sonst Nullpräfix':
        'class 5 takes ji- here, zero prefix otherwise',
    'Kl. 5 hat Nullpräfix': 'class 5 has a zero prefix',
}


def zeilen():
    lex = gruppen(lade_lexikon())
    out = []

    def add(typ, klasse, vs, rs, erkl, *tags, vs_en='', erkl_en='', rs_en=''):
        out.append({'id': f'D{len(out) + 1:03d}', 'typ': typ,
                    'typ_en': TYP_EN.get(typ, typ), 'klasse': klasse,
                    'vorderseite': vs, 'vorderseite_en': vs_en,
                    'rueckseite': rs,
                    # Nur die Klassenantworten sind sprachgebunden; Swahili-
                    # Formen stehen in beiden Fassungen gleich.
                    'rueckseite_en': rs_en or rs.replace('Kl. ', 'class '),
                    'erklaerung': erkl,
                    'erklaerung_en': erkl_en,
                    'tags': ' '.join(('A1', 'SD1', 'drill') + tags)})

    # --- 1. Welche Klasse hat dieses Nomen? -------------------------------
    for r in lex:
        kl = r['klasse_sg']
        kong = r['kongruenz']
        rs = f'Kl. {kl}'
        if r['klasse_pl']:
            rs += f'/{r["klasse_pl"]}'
        erkl = K.klassen_text(kl, r['klasse_pl'], r['sw_singular'],
                              r['sw_plural'])
        if kong:
            erkl += (f'  —  Vorsicht: Form Kl. {kl}, aber Kongruenz '
                     f'Kl. {kong} (Person)')
        erkl_en = f'{r["sw_singular"]} is class {kl}'
        if r['klasse_pl']:
            erkl_en += f', plural {r["sw_plural"]} class {r["klasse_pl"]}'
        if kong:
            erkl_en += (f'  —  careful: form class {kl}, but agreement '
                        f'class {kong} (person)')
        add('Klasse bestimmen', kl,
            f'{r["sw_singular"]} ({bedeutung(r["de"])})  —  '
            f'welche Nominalklasse?', rs, erkl, 'klasse', f'kl{kl}',
            vs_en=f'{r["sw_singular"]} ({bedeutung(r["en"])})  —  '
                  f'which noun class?',
            erkl_en=erkl_en)

    # --- 2. Plural bilden -------------------------------------------------
    for r in lex:
        if not r['sw_plural'] or r['sw_plural'] == r['sw_singular']:
            continue
        add('Plural bilden', r['klasse_sg'],
            f'{r["sw_singular"]} ({bedeutung(r["de"])})  —  Plural?',
            r['sw_plural'],
            K.klassen_text(r['klasse_sg'], r['klasse_pl'],
                           r['sw_singular'], r['sw_plural']),
            'plural', f'kl{r["klasse_sg"]}',
            vs_en=f'{r["sw_singular"]} ({bedeutung(r["en"])})  —  plural?',
            erkl_en=f'class {r["klasse_sg"]}/{r["klasse_pl"]}: '
                    f'{r["sw_singular"]} → {r["sw_plural"]}')

    # --- 3. Konkordanzform zu einer Klasse --------------------------------
    teile = (('subj', 'Subjektpräfix'), ('obj', 'Objektpräfix'),
             ('adj', 'Adjektivpräfix'), ('gen', 'Genitiv'),
             ('dem_nah', 'Demonstrativ nah'), ('dem_fern', 'Demonstrativ fern'),
             ('poss', 'Possessivpräfix'), ('rel', 'Relativinfix'))
    for kl in K.TABELLE:
        reihe = K.reihe(kl)
        for feld, name in teile:
            feld_en = name
            add('Konkordanz', kl,
                f'Kl. {kl}  —  {name}?', reihe[feld],
                K.konkordanz_text(kl), 'konkordanz', f'kl{kl}',
                vs_en=f'class {kl}  —  {TEIL_EN[feld_en]}?',
                erkl_en=f'class {kl}: subject {reihe["subj"]} · '
                        f'adjective {reihe["adj"]} · genitive {reihe["gen"]} · '
                        f'demonstrative {reihe["dem_nah"]}/{reihe["dem_fern"]} · '
                        f'possessive {reihe["poss"]} · relative {reihe["rel"]}')

    # --- 4. Adjektiv an die Klasse anpassen -------------------------------
    for stamm in A.FORMEN:
        for kl in A.KLASSEN:
            f = A.form(stamm, kl)
            hw = A.hinweis(stamm, kl)
            erkl = f'Stamm -{stamm} ({A.DEUTSCH[stamm]}) + Kl. {kl} → {f}'
            if hw:
                erkl += f'  —  {hw}'
            erkl_en = (f'stem -{stamm} ({A.ENGLISCH[stamm]}) + '
                       f'class {kl} → {f}')
            if hw:
                erkl_en += f'  —  {HINWEIS_EN.get(hw, hw)}'
            add('Adjektiv angleichen', kl,
                f'-{stamm} ({A.DEUTSCH[stamm]}) + Kl. {kl}  —  '
                f'welche Form?', f, erkl, 'adjektiv', f'kl{kl}',
                vs_en=f'-{stamm} ({A.ENGLISCH[stamm]}) + class {kl}  —  '
                      f'which form?',
                erkl_en=erkl_en)

    # --- 5. Lueckensatz: die ganze Kette ----------------------------------
    # Die deutsche Fassung ausgeschrieben statt aus Artikel und Stichwort
    # zusammengesetzt: Genus und Plural treffen sonst nicht zu (das gute
    # Buch, die guten Buecher).
    ketten = [('kitabu', '7', 'das gute Buch', 'the good book'),
              ('vitabu', '8', 'die guten Bücher', 'the good books'),
              ('mti', '3', 'der gute Baum', 'the good tree'),
              ('miti', '4', 'die guten Bäume', 'the good trees'),
              ('gari', '5', 'das gute Auto', 'the good car'),
              ('magari', '6', 'die guten Autos', 'the good cars'),
              ('mtoto', '1', 'das gute Kind', 'the good child'),
              ('watoto', '2', 'die guten Kinder', 'the good children'),
              ('barua', '9', 'der gute Brief', 'the good letter'),
              ('nyumba', '9', 'das gute Haus', 'the good house')]
    for nomen, kl, de, en in ketten:
        r = K.reihe(kl)
        voll = f'{nomen} {A.form("zuri", kl)} {r["dem_nah"]} {r["gen"]} mwalimu'
        add('Lückensatz', kl,
            f'Ergänze die Konkordanz:  {nomen}  ___zuri  ___  ___a  mwalimu\n'
            f'({de} des Lehrers)',
            voll,
            f'Kl. {kl}: Adjektiv {A.form("zuri", kl)} · Demonstrativ '
            f'{r["dem_nah"]} · Genitiv {r["gen"]} — alle drei aus derselben '
            f'Konkordanzreihe', 'luecke', f'kl{kl}',
            vs_en=f'fill in the agreement:  {nomen}  ___zuri  ___  ___a  '
                  f'mwalimu  ({en} of the teacher)',
            erkl_en=f'class {kl}: adjective {A.form("zuri", kl)} · '
                    f'demonstrative {r["dem_nah"]} · genitive {r["gen"]} — '
                    f'all three from the same agreement series')
    return out


def main():
    rows = zeilen()
    # Das Lexikon enthaelt Synonympaare (daktari fuer Arzt und Doktor).
    # Fuer den Drill zaehlt die Swahili-Form, nicht das deutsche Stichwort.
    gesehen, eindeutig = set(), []
    for r in rows:
        schluessel = (r['typ'], r['vorderseite'])
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        eindeutig.append(r)
    doppelt = len(rows) - len(eindeutig)
    rows = [{**r, 'id': f'D{i + 1:03d}'} for i, r in enumerate(eindeutig)]
    if doppelt:
        print(f'{doppelt} Dubletten entfernt')
    with open('karten_drill.tsv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, FELDER, delimiter='\t', lineterminator='\n',
                           extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: (v or '').replace('\n', ' · ').replace('\t', ' ')
                        for k, v in r.items()})
    from collections import Counter
    print(f'karten_drill.tsv: {len(rows)} Karten')
    for t, n in sorted(Counter(r['typ'] for r in rows).items()):
        print(f'  {t:24s} {n}')


if __name__ == '__main__':
    main()
