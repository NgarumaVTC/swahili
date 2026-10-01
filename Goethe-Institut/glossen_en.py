#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Glossen-Labels Deutsch -> Englisch, segmenterhaltend.

Sekela liest kein Deutsch, und auf einer englischen Karte haben deutsche
Labels ohnehin nichts verloren. Uebersetzt wird Segment fuer Segment, die
Struktur der Zeile bleibt exakt erhalten:

    1SG-PRÄS-lesen-IND   ->   1SG-PRS-read-IND

Nicht abgedeckte Tokens werden gemeldet, nicht stillschweigend durchgereicht
-- sonst entstehen halbdeutsche Glossen, die niemandem auffallen.
"""
import csv, re, sys

# Grammatische Marker: geschlossene Menge, darum hier statt in der Tabelle.
GRAM = {
    'PRÄS': 'PRS', 'PRÄT': 'PST', 'PERF': 'PRF', 'FUT': 'FUT',
    'IND': 'IND', 'KONJ': 'SBJV', 'NEG': 'NEG', 'IMP': 'IMP',
    'APPL': 'APPL', 'PASS': 'PASS', 'KAUS': 'CAUS', 'STAT': 'STAT',
    'REZ': 'RECP', 'REFL': 'REFL', 'HAB': 'HAB', 'IRR': 'IRR',
    'KONSEK': 'CONSEC', 'KOP': 'COP', 'LOK': 'LOC', 'GEN': 'GEN',
    'DEM': 'DEM', 'REL': 'REL', 'ALLG': 'GNRL',
    'nah': 'prox', 'fern': 'dist',
    '1SG': '1SG', '2SG': '2SG', '3SG': '3SG',
    '1PL': '1PL', '2PL': '2PL', '3PL': '3PL',
    'PL': 'PL', 'SG': 'SG',
}

# KL7 -> CL7, OBJ7 -> OBJ7, REL9 -> REL9
KLASSE = re.compile(r'^KL(\d+)$')
OBJEKT = re.compile(r'^OBJ(\d+(?:SG|PL)?)$')
RELATIV = re.compile(r'^REL(\d*)$')


def lade_glossar(pfad='glossar_en.tsv'):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return {r['de']: r['en'] for r in csv.DictReader(fh, delimiter='\t')}


def uebersetze_token(t, glossar, fehlend):
    if t in GRAM:
        return GRAM[t]
    m = KLASSE.match(t)
    if m:
        return f'CL{m.group(1)}'
    m = OBJEKT.match(t)
    if m:
        return f'OBJ{m.group(1)}'
    m = RELATIV.match(t)
    if m:
        return f'REL{m.group(1)}'
    if t in glossar:
        return glossar[t]
    fehlend.add(t)
    return t


def uebersetze_zeile(zeile, glossar, fehlend):
    """Erhaelt Woerter, Bindestriche und Punkte exakt."""
    woerter = []
    for wort in (zeile or '').split():
        teile = []
        for seg in wort.split('-'):
            # Punkt-Komposita zuerst als Ganzes nachschlagen: "möglich.sein"
            # soll "be.possible" werden, nicht "possible.be".
            if seg in glossar:
                teile.append(glossar[seg])
                continue
            punkte = []
            for p in seg.split('.'):
                # Zusammengesetzte Klassenlabels wie KL9/KL1 (Form- gegen
                # Kongruenzklasse) segmentweise uebersetzen.
                punkte.append('/'.join(
                    uebersetze_token(q, glossar, fehlend)
                    for q in p.split('/')))
            teile.append('.'.join(punkte))
        woerter.append('-'.join(teile))
    return ' '.join(woerter)


def pruefe():
    glossar = lade_glossar()
    fehlend = set()
    n = 0
    for pfad, felder in (('karten_haupt.tsv', ['gloss_labels']),
                         ('karten_kontrast.tsv', ['gloss_a_la', 'gloss_b_la'])):
        with open(pfad, encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                for f in felder:
                    de = r.get(f) or ''
                    en = uebersetze_zeile(de, glossar, fehlend)
                    # Struktur muss identisch bleiben
                    if ([len(w.split('-')) for w in de.split()]
                            != [len(w.split('-')) for w in en.split()]):
                        print(f'STRUKTUR {pfad} {r["id"]}: {de!r} -> {en!r}')
                        n += 1
    print(f'Glossar: {len(glossar)} Eintraege')
    if fehlend:
        print(f'NICHT ABGEDECKT ({len(fehlend)}):')
        for t in sorted(fehlend):
            print(f'  {t}')
    else:
        print('Alle Label-Tokens abgedeckt.')
    return len(fehlend) + n


if __name__ == '__main__':
    if '--pruefe' in sys.argv:
        sys.exit(1 if pruefe() else 0)
    g = lade_glossar()
    f = set()
    for zeile in sys.argv[1:]:
        print(uebersetze_zeile(zeile, g, f))
    if f:
        print('fehlend:', ' '.join(sorted(f)), file=sys.stderr)
