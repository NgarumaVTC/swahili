#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Konkordanztabelle der Nominalklassen — eine Quelle fuer alles.

Die Tabelle ist die Maschinenfassung von GLOSSING.md. Weil die Konkordanzen
hier und nur hier stehen, koennen sie in 850 Karten nicht auseinanderdriften;
das Lexikon speichert pro Substantiv lediglich die Klassennummer.
"""

# Kl.: (Nominalpraefix, SUBJ, OBJ, ADJ, GEN, DEM nah, DEM fern, POSS, REL)
TABELLE = {
    '1':  ('m-/mw-', 'a-',  '-m-',  'm-/mw-', 'wa',  'huyu', 'yule', 'w-',  '-ye'),
    '2':  ('wa-',    'wa-', '-wa-', 'wa-',    'wa',  'hawa', 'wale', 'w-',  '-o'),
    '3':  ('m-/mw-', 'u-',  '-u-',  'm-/mw-', 'wa',  'huu',  'ule',  'w-',  '-o'),
    '4':  ('mi-',    'i-',  '-i-',  'mi-',    'ya',  'hii',  'ile',  'y-',  '-yo'),
    '5':  ('ji-/Ø',  'li-', '-li-', 'ji-/Ø',  'la',  'hili', 'lile', 'l-',  '-lo'),
    '6':  ('ma-',    'ya-', '-ya-', 'ma-',    'ya',  'haya', 'yale', 'y-',  '-yo'),
    '7':  ('ki-',    'ki-', '-ki-', 'ki-',    'cha', 'hiki', 'kile', 'ch-', '-cho'),
    '8':  ('vi-',    'vi-', '-vi-', 'vi-',    'vya', 'hivi', 'vile', 'vy-', '-vyo'),
    '9':  ('Ø/n-',   'i-',  '-i-',  'Ø/n-',   'ya',  'hii',  'ile',  'y-',  '-yo'),
    '10': ('Ø/n-',   'zi-', '-zi-', 'Ø/n-',   'za',  'hizi', 'zile', 'z-',  '-zo'),
    '11': ('u-',     'u-',  '-u-',  'm-/mw-', 'wa',  'huu',  'ule',  'w-',  '-o'),
    '14': ('u-',     'u-',  '-u-',  'm-/mw-', 'wa',  'huu',  'ule',  'w-',  '-o'),
    '15': ('ku-',    'ku-', '-ku-', 'ku-',    'kwa', 'huku', 'kule', 'kw-', '-ko'),
    '16': ('pa-',    'pa-', '-pa-', 'pa-',    'pa',  'hapa', 'pale', 'p-',  '-po'),
    '17': ('ku-',    'ku-', '-ku-', 'ku-',    'kwa', 'huku', 'kule', 'kw-', '-ko'),
    '18': ('mu-/m-', 'mu-', '-mu-', 'mu-',    'mwa', 'humu', 'mule', 'mw-', '-mo'),
}

FELDER = ('praefix', 'subj', 'obj', 'adj', 'gen', 'dem_nah', 'dem_fern',
          'poss', 'rel')

INHALT = {
    '1/2':  'Personen',
    '3/4':  'Pflanzen, Koerperteile, Dinge',
    '5/6':  'Paarige Dinge, Fruechte, Augmentativa',
    '7/8':  'Dinge, Werkzeuge, Sprachen, Diminutiva',
    '9/10': 'Tiere und Lehnwoerter; Singular = Plural',
    '11/10': 'Lange, duenne Dinge',
    '14':   'Abstrakta, kein Plural',
    '15':   'Verbalnomen',
}


def reihe(kl):
    """Kl. -> dict der Konkordanzen."""
    return dict(zip(FELDER, TABELLE[str(kl)]))


def konkordanz_text(kl):
    """Kompakte Konkordanzzeile fuer das Kartenfeld `konkordanz`."""
    r = reihe(kl)
    return (f"Kl.{kl}: SUBJ {r['subj']} · ADJ {r['adj']} · GEN {r['gen']} · "
            f"DEM {r['dem_nah']}/{r['dem_fern']} · POSS {r['poss']} · "
            f"REL {r['rel']}")


def klassen_text(sg, pl, sw_sg, sw_pl):
    """Kompakte Klassenzeile fuer das Kartenfeld `klassen`."""
    if not pl or pl == sg:
        return f"{sw_sg} Kl. {sg} ({reihe(sg)['praefix']}), kein Numeruswechsel"
    a, b = reihe(sg)['praefix'], reihe(pl)['praefix']
    # Die Praefixe enthalten selbst "/", darum " › " als Paartrenner.
    pfx = a if a == b else f"{a} › {b}"
    hinweis = '' if sw_pl != sw_sg else '  — Numerus nur an der Konkordanz'
    return f"{sw_sg} Kl. {sg}/{pl} ({pfx}) → {sw_pl}{hinweis}"


def konkordanz_text_en(kl):
    """Englische Fassung fuer die EN-Decks und Sekelas Boegen."""
    r = reihe(kl)
    return (f"class {kl}: SUBJ {r['subj']} · ADJ {r['adj']} · GEN {r['gen']} · "
            f"DEM {r['dem_nah']}/{r['dem_fern']} · POSS {r['poss']} · "
            f"REL {r['rel']}")


def klassen_text_en(sg, pl, sw_sg, sw_pl):
    if not sg:
        return ''
    if not pl or pl == sg:
        return f"{sw_sg} class {sg} ({reihe(sg)['praefix']}), no number change"
    a, b = reihe(sg)['praefix'], reihe(pl)['praefix']
    pfx = a if a == b else f'{a} › {b}'
    hinweis = '' if sw_pl != sw_sg else '  — number shows only in the agreement'
    return f'{sw_sg} class {sg}/{pl} ({pfx}) → {sw_pl}{hinweis}'


if __name__ == '__main__':
    for kl in TABELLE:
        print(konkordanz_text(kl))
