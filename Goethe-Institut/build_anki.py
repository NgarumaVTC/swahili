#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Karten-TSVs -> importfertige Anki-Dateien.

Primaer: anki_master.tsv mit allen Feldern. Ein Notiztyp mit vier
Kartenvorlagen erzeugt daraus die vier Richtungen; eine Korrektur wirkt
dann auf alle vier Karten derselben Notiz.

Zusaetzlich die vier flachen Zwei-Spalten-Decks fuer den Fall, dass ohne
eigenen Notiztyp importiert werden soll.
"""
import csv, html, os, sys

MASTER = ['Stichwort', 'Deutsch', 'Englisch', 'Swahili', 'Morpheme',
          'Labels', 'LabelsEN', 'Gloss', 'GlossEN', 'Klassen', 'KlassenEN',
          'Konkordanz', 'KonkordanzEN', 'Hinweis', 'HinweisEN', 'Quelle',
          'Tags']

RICHTUNGEN = (
    ('anki_sw_de.tsv', 'Swahili', 'Deutsch'),
    ('anki_sw_en.tsv', 'Swahili', 'Englisch'),
    ('anki_de_sw.tsv', 'Deutsch', 'Swahili'),
    ('anki_en_sw.tsv', 'Englisch', 'Swahili'),
)


def sauber(v):
    """Tabs und Umbrueche wuerden die TSV-Spalten zerreissen."""
    return ' '.join((v or '').split())


def glossen_html(mo, la):
    """Morphem- und Labelzeile als zweizeilige Tabelle, Segmente untereinander."""
    wm, wl = (mo or '').split(), (la or '').split()
    if not wm or len(wm) != len(wl):
        return ''
    zellen_mo = ''.join(f'<td>{html.escape(w)}</td>' for w in wm)
    zellen_la = ''.join(f'<td>{html.escape(w)}</td>' for w in wl)
    return (f'<table class=gloss><tr class=mo>{zellen_mo}</tr>'
            f'<tr class=la>{zellen_la}</tr></table>')


def schreib_tsv(pfad, zeilen):
    with open(pfad, 'w', encoding='utf-8', newline='\n') as fh:
        for z in zeilen:
            fh.write('\t'.join(z) + '\n')


def lade(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


def aus_haupt(r):
    return {
        'Stichwort': sauber(r['stichwort']),
        'Deutsch': sauber(r['satz_de']),
        'Englisch': sauber(r['satz_en']),
        'Swahili': sauber(r['satz_sw']),
        'Morpheme': sauber(r['gloss_morpheme']),
        'Labels': sauber(r['gloss_labels']),
        'LabelsEN': sauber(r['gloss_labels_en']),
        'Gloss': glossen_html(r['gloss_morpheme'], r['gloss_labels']),
        'GlossEN': glossen_html(r['gloss_morpheme'], r['gloss_labels_en']),
        'Klassen': sauber(r['klassen']),
        'KlassenEN': sauber(r['klassen_en']),
        'Konkordanz': sauber(r['konkordanz']),
        'KonkordanzEN': sauber(r['konkordanz_en']),
        'Hinweis': sauber(r['hinweis']),
        'HinweisEN': '',
        'Quelle': f"Wortliste S. {r['seite']}",
        'Tags': sauber(r['tags']),
    }


def aus_kontrast(r):
    """Ein Minimalpaar wird eine Notiz: beide Saetze stehen untereinander."""
    trenn = ' ⁄⁄ '
    return {
        'Stichwort': f"Kontrast: {sauber(r['kontrasttyp'])}",
        'Deutsch': sauber(r['de_a']) + trenn + sauber(r['de_b']),
        'Englisch': sauber(r['en_a']) + trenn + sauber(r['en_b']),
        'Swahili': sauber(r['sw_a']) + trenn + sauber(r['sw_b']),
        'Morpheme': sauber(r['gloss_a_mo']) + trenn + sauber(r['gloss_b_mo']),
        'Labels': sauber(r['gloss_a_la']) + trenn + sauber(r['gloss_b_la']),
        'LabelsEN': sauber(r['gloss_a_la_en']) + trenn + sauber(r['gloss_b_la_en']),
        'Gloss': (glossen_html(r['gloss_a_mo'], r['gloss_a_la'])
                  + glossen_html(r['gloss_b_mo'], r['gloss_b_la'])),
        'GlossEN': (glossen_html(r['gloss_a_mo'], r['gloss_a_la_en'])
                    + glossen_html(r['gloss_b_mo'], r['gloss_b_la_en'])),
        'Klassen': sauber(r['klassen']),
        'KlassenEN': sauber(r.get('klassen_en') or r['klassen']),
        'Konkordanz': sauber(r['konkordanz']),
        'KonkordanzEN': sauber(r.get('konkordanz_en') or r['konkordanz']),
        'Hinweis': sauber(r['unterschied']) + ' — ' + sauber(r['hinweis']),
        'HinweisEN': sauber(r['unterschied']) + ' — '
                     + sauber(r.get('hinweis_en') or ''),
        'Quelle': 'Kontrastdeck',
        'Tags': sauber(r['tags']),
    }


def aus_drill(r):
    return {
        'Stichwort': sauber(r['typ']),
        'Deutsch': sauber(r['vorderseite']),
        'Englisch': sauber(r['vorderseite_en'] or r['vorderseite']),
        'Swahili': sauber(r['rueckseite']),
        'Morpheme': '', 'Labels': '', 'LabelsEN': '',
        'Gloss': '', 'GlossEN': '',
        'Klassen': '', 'KlassenEN': '',
        'Konkordanz': sauber(r['erklaerung']),
        'KonkordanzEN': sauber(r.get('erklaerung_en') or r['erklaerung']),
        'Hinweis': '', 'HinweisEN': '', 'Quelle': 'Drilldeck',
        'Tags': sauber(r['tags']),
    }


def main():
    notizen = []
    for pfad, wandler in (('karten_haupt.tsv', aus_haupt),
                          ('karten_kontrast.tsv', aus_kontrast),
                          ('karten_drill.tsv', aus_drill)):
        if not os.path.exists(pfad):
            print(f'fehlt, wird uebersprungen: {pfad}')
            continue
        n = 0
        for r in lade(pfad):
            notizen.append(wandler(r))
            n += 1
        print(f'{pfad}: {n} Notizen')

    # Direkt schreiben statt ueber csv: die Felder enthalten "-Zeichen, die
    # jede Quoting-Mechanik verfaelschen wuerde. Tabs und Umbrueche sind
    # durch sauber() schon entfernt.
    schreib_tsv('anki_master.tsv', [MASTER] +
                [[n[f] for f in MASTER] for n in notizen])

    # Flache Decks: nur Satzkarten, der Drill ist richtungslos
    satz = [n for n in notizen if n['Quelle'] != 'Drilldeck']
    for pfad, vorn, hinten in RICHTUNGEN:
        zeilen = []
        for n in satz:
            if not (n[vorn] and n[hinten]):
                continue
            rueck = n[hinten]
            # Auf einer englischen Karte haben deutsche Labels nichts verloren.
            englisch = 'Englisch' in (vorn, hinten)
            g = n['GlossEN'] if englisch else n['Gloss']
            extra = [g] if g else []
            # Auf einer englischen Karte sollen auch Klassen- und
            # Konkordanzzeile englisch sein. Der Hinweis bleibt deutsch --
            # er ist Lernhilfe fuer den Besitzer, nicht Teil der Antwort.
            paare = ((('KlassenEN', 'klassen'), ('KonkordanzEN', 'konkordanz'))
                     if englisch else
                     (('Klassen', 'klassen'), ('Konkordanz', 'konkordanz')))
            hw = ('HinweisEN' if englisch and n['HinweisEN']
                  else 'Hinweis')
            for feld, css in paare + ((hw, 'hinweis'),):
                if n[feld]:
                    extra.append(f'<div class={css}>'
                                 f'{html.escape(n[feld])}</div>')
            if extra:
                rueck += '<hr>' + ''.join(extra)
            zeilen.append([n[vorn], rueck, n['Tags']])
        schreib_tsv(pfad, zeilen)
        print(f'{pfad}: {sum(1 for n in satz if n[vorn] and n[hinten])} Karten')

    zeilen = []
    for n in notizen:
        if n['Quelle'] != 'Drilldeck':
            continue
        rueck = n['Swahili']
        if n['Konkordanz']:
            rueck += f'<hr><div class=konkordanz>{html.escape(n["Konkordanz"])}</div>'
        zeilen.append([n['Deutsch'], rueck, n['Tags']])
    schreib_tsv('anki_drill.tsv', zeilen)
    print(f'anki_drill.tsv: {sum(1 for n in notizen if n["Quelle"] == "Drilldeck")} Karten')

    # TSV-Hygiene pruefen
    fehler = 0
    for pfad in ['anki_master.tsv', 'anki_drill.tsv'] + [p for p, _, _ in RICHTUNGEN]:
        with open(pfad, encoding='utf-8') as fh:
            spalten = {len(l.rstrip('\n').split('\t')) for l in fh}
        erwartet = {len(MASTER)} if pfad == 'anki_master.tsv' else {3}
        if spalten != erwartet:
            print(f'FEHLER {pfad}: Spaltenzahlen {spalten}, erwartet {erwartet}')
            fehler += 1
    print('TSV-Hygiene: ' + ('in Ordnung' if not fehler else f'{fehler} Datei(en) fehlerhaft'))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
