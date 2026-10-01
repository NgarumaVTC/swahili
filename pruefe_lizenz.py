#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Prueft, ob die Ausnahmeliste in LICENSE.md noch stimmt.

Eine handgepflegte Liste driftet, sobald eine neue Datei entsteht. Darum
wird sie hier gegen die Wirklichkeit gehalten: Referenz sind die deutschen
Beispielsaetze aus wortliste_de.tsv, also das, was woertlich vom
Goethe-Institut uebernommen wurde. Jede Datei, die davon etwas enthaelt,
muss in LICENSE.md stehen -- und jede dort genannte Datei muss wirklich
etwas enthalten.
"""
import csv, os, re, sys

PROJEKT = 'Goethe-Institut'
QUELLE = os.path.join(PROJEKT, 'wortliste_de.tsv')
LIZENZ = 'LICENSE.md'
MINDESTLAENGE = 20          # kurze Fragmente sind keine Uebernahme
UEBERSPRINGEN = {'.git', '__pycache__', '.DS_Store'}
# Die Quelle selbst und das PDF sind per Definition ausgenommen.
# Wortgruppenliste: woertliche Extraktion wie wortliste_de.tsv, aber ihre
# Eintraege sind zu kurz, um per Satzvergleich erkannt zu werden.
IMMER = {os.path.join(PROJEKT, 'A1_SD1_Wortliste_02.pdf'), QUELLE,
         os.path.join(PROJEKT, 'wortgruppen_de.tsv')}


# Alltagsfloskeln. Sie stehen zwar in der Wortliste, aber niemand haelt
# Rechte an "Mit freundlichen Gruessen" -- taucht so etwas in einem Brief
# dieses Repositorys auf, ist das keine Uebernahme, sondern deutsche Sprache.
FLOSKELN = {
    'Mit freundlichen Grüßen', 'Sehr geehrte Damen und Herren!',
    'Auf Wiedersehen!', 'Auf Wiedersehen.', 'Guten Morgen!', 'Guten Appetit!',
    'Vielen Dank!', 'Herzlichen Dank!', 'Danke sehr!', 'Herzlich willkommen!',
    'Herzlichen Glückwunsch!', 'Alles Gute!', 'Viel Glück!', 'Wie bitte?',
    'Ein gutes neues Jahr!', 'Zahlen, bitte!', 'Moment mal bitte!',
    'Einen Moment bitte.', 'Liebe Susanne, lieber Hans,',
}


def goethe_saetze():
    with open(QUELLE, encoding='utf-8', newline='') as fh:
        saetze = {r['satz_de'] for r in csv.DictReader(fh, delimiter='\t')}
    return {s for s in saetze if len(s) >= MINDESTLAENGE and s not in FLOSKELN}


def dateien():
    for wurzel, verz, namen in os.walk('.'):
        verz[:] = [v for v in verz if v not in UEBERSPRINGEN]
        for n in namen:
            if n in UEBERSPRINGEN:
                continue
            p = os.path.relpath(os.path.join(wurzel, n), '.')
            yield p


def enthaelt_goethe(pfad, saetze):
    """Auch PDFs: deren Text wird mit dem Projektwerkzeug gelesen."""
    if pfad in IMMER:
        return True
    if pfad.lower().endswith('.pdf'):
        sys.path.insert(0, PROJEKT)
        try:
            import pdftext
            d, objs = pdftext.load(pfad)
            text = ''.join(
                ''.join(t for *_, t in pdftext.seitentext(objs, n))
                for n in pdftext.seitenbaum(objs))
        except Exception:
            return False
        # Im PDF-Text fehlen Leerzeichen zwischen Textstuecken; darum
        # beide Seiten entleeren und dann vergleichen.
        kompakt = re.sub(r'\s+', '', text)
        return any(re.sub(r'\s+', '', s) in kompakt for s in saetze)
    try:
        inhalt = open(pfad, encoding='utf-8', errors='replace').read()
    except OSError:
        return False
    return any(s in inhalt for s in saetze)


def deklariert():
    """Dateinamen aus dem Ausnahmeabschnitt von LICENSE.md."""
    if not os.path.exists(LIZENZ):
        sys.exit(f'{LIZENZ} fehlt')
    text = open(LIZENZ, encoding='utf-8').read()
    m = re.search(r'<!-- AUSNAHMEN -->(.*?)<!-- /AUSNAHMEN -->', text, re.S)
    if not m:
        sys.exit(f'{LIZENZ}: Markierung <!-- AUSNAHMEN --> fehlt')
    return set(re.findall(r'`([^`]+)`', m.group(1)))


def main():
    saetze = goethe_saetze()
    tatsaechlich = {p for p in dateien() if enthaelt_goethe(p, saetze)}
    erklaert = deklariert()

    fehlt = sorted(tatsaechlich - erklaert)
    ueberzaehlig = sorted(erklaert - tatsaechlich)

    print(f'Referenzsätze: {len(saetze)}')
    print(f'Dateien mit Goethe-Text: {len(tatsaechlich)}')
    print(f'In {LIZENZ} deklariert: {len(erklaert)}')
    if fehlt:
        print(f'\nFEHLT in {LIZENZ} (enthält Goethe-Text):')
        for p in fehlt:
            print(f'  {p}')
    if ueberzaehlig:
        print(f'\nÜBERZÄHLIG in {LIZENZ} (enthält keinen Goethe-Text):')
        for p in ueberzaehlig:
            print(f'  {p}')
    if not (fehlt or ueberzaehlig):
        print('\nAusnahmeliste deckt sich genau mit dem Befund.')
    return 1 if (fehlt or ueberzaehlig) else 0


if __name__ == '__main__':
    sys.exit(main())
