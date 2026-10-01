#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Wortgruppenliste (S. 6-8) -> wortgruppen_de.tsv

Anders als die alphabetische Liste ist das hier ein mehrspaltiges Raster mit
je Abschnitt wechselnden Spaltenpositionen. Die Spalten werden darum nicht
ueber feste x-Zonen, sondern ueber Luecken im Zeilenverlauf getrennt.
"""
import re
import pdftext

SEITEN = (6, 7, 8)
Y_HEADER = 760
GAP = 7.0           # Luecke, ab der eine neue Rasterzelle beginnt

UEBERSCHRIFTEN = {
    'Wortgruppenliste', 'Zahlen', 'Datum', 'Uhrzeit',
    'Zeitmaße, Zeitangaben', 'Woche/Wochentage', 'Tag/Tageszeiten',
    'Monat/Monatsnamen', 'Jahr/Jahreszeiten', 'Währungen',
    'Maße und Gewichte', 'Länder/Ländernamen/Nationalitäten',
    'Angabe der eigenen Herkunft oder Nationalität', 'Farben',
    'Himmelsrichtungen',
}


def cells(items, pg):
    """-> [(y, [zelle, ...])] in Lesereihenfolge."""
    rows = {}
    for y, x, seq, t in items:
        if t.strip() in ('VS_02_280312', f'Seite {pg}') or y > Y_HEADER:
            continue
        rows.setdefault(round(y / 4) * 4, []).append((x, seq, t))

    out = []
    for key in sorted(rows, reverse=True):
        g = sorted(rows[key], key=lambda e: e[1])
        cur, parts, end = [], [], None
        for x, seq, t in g:
            if end is not None and x - end > GAP:
                parts.append(''.join(cur)); cur = []
            cur.append(t)
            end = x + 4.2 * len(t)        # grobe Breitenschaetzung je Glyphe
        if cur:
            parts.append(''.join(cur))
        parts = [re.sub(r'\s+', ' ', p).strip() for p in parts]
        parts = [p for p in parts if p]
        # "ein Meter" / "=" / "1 m" wieder zu einer Gleichung zusammenziehen
        merged = []
        for p in parts:
            if p == '=' and merged:
                merged[-1] += ' ='
            elif merged and merged[-1].endswith('='):
                merged[-1] += ' ' + p
            else:
                merged.append(p)
        parts = merged
        if parts:
            out.append((key, parts))
    return out


def main():
    P = pdftext.pages()
    recs = []
    gruppe = ''
    for pg in SEITEN:
        for _y, parts in cells(P[pg], pg):
            if len(parts) == 1 and parts[0] in UEBERSCHRIFTEN:
                if parts[0] != 'Wortgruppenliste':
                    gruppe = parts[0]
                continue
            for p in parts:
                if p in UEBERSCHRIFTEN:
                    gruppe = p
                    continue
                recs.append((pg, gruppe, p))

    with open('wortgruppen_de.tsv', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('seite\tgruppe\teintrag\n')
        for pg, gr, p in recs:
            fh.write(f'{pg}\t{gr}\t{p}\n')

    print(f'Eintraege: {len(recs)}')
    from collections import Counter
    for gr, n in Counter(g for _, g, _ in recs).items():
        print(f'  {gr or "(ohne Gruppe)"}: {n}')


if __name__ == '__main__':
    main()
