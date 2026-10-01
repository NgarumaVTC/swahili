#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Integritaetspruefung der Kartendateien.

Wichtigster Test: gloss_morpheme und gloss_labels muessen Wort fuer Wort und
Segment fuer Segment deckungsgleich sein (siehe GLOSSING.md). Eine Abweichung
ist ein harter Fehler, weil die Karte dann eine falsche Analyse zeigt.
"""
import csv, re, sys, unicodedata

PFLICHT = ('satz_sw', 'gloss_morpheme', 'gloss_labels')

# Stichprobe haeufiger deutscher Labelwoerter. Taucht eines in der englischen
# Zeile auf, ist die Uebersetzung dort durchgefallen.
DEUTSCHE_RESTE = {
    'haben', 'sein', 'mein', 'mit', 'bitte', 'gut', 'Buch', 'kommen', 'und',
    'gehen', 'lesen', 'Haus', 'Auto', 'Stunde', 'tun', 'Brief', 'Kind',
    'schreiben', 'wohnen', 'Arbeit', 'nehmen', 'sehen', 'PRÄS', 'PRÄT',
    'PERF', 'KONJ', 'KL1', 'KL7', 'KL9', 'nah', 'fern',
}
PFLICHT_KONTRAST = ('sw_a', 'sw_b', 'gloss_a_mo', 'gloss_b_mo')


def lade(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


def pruefe_paar(i, mo, la, melde):
    """Morphem- und Labelzeile muessen segmentweise deckungsgleich sein."""
    if not (mo and la):
        return
    wm, wl = mo.split(), la.split()
    if len(wm) != len(wl):
        melde(i, 'segmente',
              f'{len(wm)} Morphemwoerter vs. {len(wl)} Labelwoerter\n'
              f'        {mo}\n        {la}')
        return
    for a, b in zip(wm, wl):
        if a.count('-') != b.count('-'):
            melde(i, 'segmente',
                  f'{a!r} ({a.count("-") + 1} Segmente) vs. '
                  f'{b!r} ({b.count("-") + 1} Segmente)')
    if '-NEG' in la:
        for mw, lw in zip(wm, wl):
            if lw.endswith('-NEG') and not re.match(
                    r'(si|hu|ha|hatu|ham|hawa|hai|hau|hali|haya|haki|'
                    r'havi|hazi|haku|hapa|hamu)-', mw):
                melde(i, 'negation',
                      f'{mw!r} als {lw!r} glossiert, aber kein negatives '
                      f'Subjektpraefix im Wort')


def pruefe(pfad, lexikon=None):
    rows = lade(pfad)
    fehler = []

    def melde(i, art, text):
        fehler.append(f'{pfad}:{i + 2}  [{art}] {text}')

    for i, r in enumerate(rows):
        for f in (PFLICHT_KONTRAST if 'sw_a' in r else PFLICHT):
            if f in r and not (r[f] or '').strip():
                melde(i, 'leer', f'Feld {f} ist leer')

        # Kontrastkarten tragen zwei Glossenpaare statt eines
        paare = [(r.get('gloss_morpheme') or '', r.get('gloss_labels') or ''),
                 (r.get('gloss_morpheme') or '', r.get('gloss_labels_en') or '')]
        if 'gloss_a_mo' in r:
            paare = [(r.get('gloss_a_mo') or '', r.get('gloss_a_la') or ''),
                     (r.get('gloss_b_mo') or '', r.get('gloss_b_la') or ''),
                     (r.get('gloss_a_mo') or '', r.get('gloss_a_la_en') or ''),
                     (r.get('gloss_b_mo') or '', r.get('gloss_b_la_en') or '')]
        for mo, la in paare:
            pruefe_paar(i, mo, la, melde)

        mo, la = paare[0]
        if False:
            wm, wl = mo.split(), la.split()
            if len(wm) != len(wl):
                melde(i, 'segmente',
                      f'{len(wm)} Morphemwoerter vs. {len(wl)} Labelwoerter\n'
                      f'        {mo}\n        {la}')
            else:
                for a, b in zip(wm, wl):
                    if a.count('-') != b.count('-'):
                        melde(i, 'segmente',
                              f'{a!r} ({a.count("-") + 1} Segmente) vs. '
                              f'{b!r} ({b.count("-") + 1} Segmente)')

        # NEG am Endvokal setzt ein negatives Subjektpraefix voraus. Sonst ist
        # das -i meist der Stammauslaut eines arabischen Lehnverbs.
        if la and '-NEG' in la:
            for mw, lw in zip(mo.split(), la.split()):
                if lw.endswith('-NEG') and not re.match(
                        r'(si|hu|ha|hatu|ham|hawa|hai|hau|hali|haya|haki|'
                        r'havi|hazi|haku|hapa|hamu)-', mw):
                    melde(i, 'negation',
                          f'{mw!r} als {lw!r} glossiert, aber kein negatives '
                          f'Subjektpraefix im Wort')

        # Die Morphemzeile muss zum Satz passen: gleiche Wortzahl.
        sw = (r.get('satz_sw') or '')
        if sw and mo:
            n_sw = len(re.findall(r'[\w’\']+', sw))
            n_mo = len(mo.split())
            if abs(n_sw - n_mo) > max(2, n_sw // 3):
                melde(i, 'satzbezug',
                      f'Satz hat {n_sw} Woerter, Glosse {n_mo}')

        # Englische Labelzeile darf kein deutsches Restwort enthalten.
        for f in ('gloss_labels_en', 'gloss_a_la_en', 'gloss_b_la_en'):
            if not r.get(f):
                continue
            rest = [t for t in re.split(r'[-. /]', r[f])
                    if t and t in DEUTSCHE_RESTE]
            if rest:
                melde(i, 'sprache',
                      f'{f} enthaelt deutsche Woerter: {", ".join(sorted(set(rest)))}')

        for f, v in r.items():
            if v and ('\t' in v or '\n' in v):
                melde(i, 'tsv', f'Feld {f} enthaelt Tab oder Umbruch')
            if v and ('�' in v or any(
                    unicodedata.category(c) == 'Co' for c in v)):
                melde(i, 'zeichen', f'Feld {f} enthaelt Ersatzzeichen')

    if lexikon:
        lex = {r['sw_singular']: r for r in lade(lexikon)}
        for i, r in enumerate(rows):
            for wort in re.findall(r'[a-zA-Z’]+', r.get('satz_sw') or ''):
                e = lex.get(wort)
                kl = r.get('klassen') or ''
                if e and kl and f"Kl. {e['klasse_sg']}" not in kl:
                    melde(i, 'klasse',
                          f'{wort!r} ist laut Lexikon Kl. {e["klasse_sg"]}, '
                          f'Karte nennt: {kl!r}')

    print(f'{pfad}: {len(rows)} Zeilen, {len(fehler)} Beanstandungen')
    for f in fehler[:40]:
        print('  ' + f)
    if len(fehler) > 40:
        print(f'  ... und {len(fehler) - 40} weitere')
    return len(fehler)


if __name__ == '__main__':
    args = sys.argv[1:] or ['karten_haupt.tsv']
    lex = 'klassen_lexikon.tsv'
    import os
    n = sum(pruefe(a, lex if os.path.exists(lex) else None) for a in args)
    sys.exit(1 if n else 0)
