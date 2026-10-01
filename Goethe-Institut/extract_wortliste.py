#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""A1_SD1_Wortliste_02.pdf -> wortliste_de.tsv

Layout der Wortlistenseiten (9-27): zwei Spalten, x~144 Stichwort,
x~236 Beispielsatz. Jedes Beispiel steht auf einer eigenen Zeile; eine Zeile
mit leerem Stichwort ist entweder ein weiteres Beispiel zum Vorgaenger oder
die Fortsetzung eines umgebrochenen Satzes.
"""
import re, sys, unicodedata
import pdftext

X_HEAD, X_SENT = 100, 230   # Satzspalte beginnt in 831 von 852 Zeilen exakt bei x=237
Y_HEADER = 760        # Marginalie INVENTARE liegt auf jeder Seite bei y~781,5
ROW_TOL = 4          # Zeilenabstand ist 13 pt, 4 pt Toleranz ist sicher
WORTLISTE = range(9, 28)


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def rows_of_page(items, pg):
    """-> [(stichwort, satz, ist_untereintrag)] in Lesereihenfolge."""
    buckets = {}
    for y, x, seq, t in items:
        if t.strip() in ('VS_02_280312', f'Seite {pg}'):
            continue
        if x < X_HEAD:                   # Kapitelkopf "Alphabetische Wortliste"
            continue
        if y > Y_HEADER:                 # Marginalie INVENTARE
            continue
        buckets.setdefault(round(y / ROW_TOL) * ROW_TOL, []).append((x, seq, t))

    out = []
    for key in sorted(buckets, reverse=True):
        g = buckets[key]
        # Bei x-Gleichstand ist die Dokumentreihenfolge die Lesereihenfolge.
        head = ''.join(t for _, _, t in sorted(
            (e for e in g if e[0] < X_SENT), key=lambda e: e[1]))
        sent = ''.join(t for _, _, t in sorted(
            (e for e in g if e[0] >= X_SENT), key=lambda e: e[1]))
        sub = head.startswith('  ') or head.startswith('  ')
        out.append((norm(head), norm(sent), sub))
    return out


def is_complete(s):
    """Gilt der Satz als abgeschlossen?"""
    s = s.rstrip()
    if s.endswith(('.', '!', '?', '…')):
        return True
    # Eine auf ")" endende Zeile ist vollstaendig. Ohne diese Regel wuerde ein
    # geklammerter Zusatz am Seitenende mit dem ersten Eintrag der Folgeseite
    # verschmolzen.
    if s.endswith(')'):
        return True
    # Zeilen, die mit "z. B." beginnen, sind Beispielreihen und damit
    # vollstaendig, obwohl kein Satzzeichen folgt.
    return s.startswith(('z. B.', 'z.B.'))


def is_wrap(prev, cur):
    """Ist cur die Fortsetzung des umgebrochenen Satzes prev?

    Entscheidend ist allein, ob prev mitten im Satz abbricht. Die
    Grossschreibung von cur taugt nicht als Kriterium: Fortsetzungen wie
    "Deutsch." oder "Rhein." beginnen gross.
    """
    return bool(prev and cur) and not is_complete(prev)


def joins_hyphenated(prev_head, prev_sent, cur_head, cur_sent):
    """Setzt cur_head ein am Zeilenende getrenntes Stichwort fort?

    Selbstpruefend: nur wenn das zusammengesetzte Wort im Beispielsatz
    wirklich vorkommt. Das trennt "der Anruf-"/"beantworter" von
    Stammformen wie "lieb-", auf die zufaellig "lieben" folgt.
    """
    if not prev_head.endswith('-') or not cur_head:
        return False
    if is_complete(prev_sent):
        return False
    stem = prev_head[:-1].split()[-1]
    joined = stem + cur_head.split()[0].rstrip(',')
    return joined.lower() in (prev_sent + ' ' + cur_sent).lower()


def main():
    P = pdftext.pages()
    missing = [p for p in WORTLISTE if p not in P]
    if missing:
        sys.exit(f'Seiten fehlen: {missing}')

    recs = []            # (seite, buchstabe, stichwort, untereintrag, satz)
    letter = ''
    carry = ''           # ueber zwei Zeilen gesetztes Stichwort
    for pg in WORTLISTE:
        for head, sent, sub in rows_of_page(P[pg], pg):
            if head and not sent and len(head) == 1 and head.isalpha():
                letter = head.upper()          # Abschnittsbuchstabe
                continue
            if not head and not sent:
                continue
            # Stichwortzeile ohne Beispiel, die auf "-" oder "/" endet, laeuft
            # in die naechste Zeile weiter: "die Ehefrau, -en/" + "der Ehemann".
            if head and not sent and head.endswith(('-', '/')):
                carry = head[:-1] if head.endswith('-') else head
                continue
            if carry:
                head, carry = carry + head, ''
                sub = False
            if head:
                if recs and joins_hyphenated(recs[-1][2], recs[-1][4], head, sent):
                    p = recs[-1]
                    p[2] = norm(p[2][:-1] + head)
                    p[4] = norm(p[4] + ' ' + sent) if p[4] else sent
                    continue
                recs.append([pg, letter, head, sub, sent])
            elif recs:
                if is_wrap(recs[-1][4], sent):
                    recs[-1][4] = norm(recs[-1][4] + ' ' + sent)
                else:
                    p = recs[-1]
                    recs.append([pg, letter, p[2], p[3], sent])

    # Unvollstaendig gebliebene Saetze melden statt stillschweigend ausliefern.
    odd = [r for r in recs if r[4] and not is_complete(r[4])
           and not r[4].rstrip().endswith((':', ','))]

    with open('wortliste_de.tsv', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('id\tseite\tbuchstabe\tstichwort\tuntereintrag\tsatz_de\n')
        kid = 0
        for pg, let, head, sub, sent in recs:
            if not sent:
                continue
            kid += 1
            fh.write(f'{kid}\t{pg}\t{let}\t{head}\t{int(sub)}\t{sent}\n')

    n = sum(1 for r in recs if r[4])
    heads = {r[2] for r in recs}
    print(f'Karten:       {n}')
    print(f'Stichwoerter: {len(heads)}')
    print(f'Seiten:       {min(WORTLISTE)}-{max(WORTLISTE)}')
    if odd:
        print(f'\nWARNUNG: {len(odd)} Saetze ohne Schlusszeichen:')
        for r in odd[:15]:
            print(f'  S.{r[0]} {r[2]!r} -> {r[4]!r}')
    bad = [c for r in recs for c in r[4] if unicodedata.category(c) == 'Co' or c == '�']
    if bad:
        print(f'\nWARNUNG: {len(bad)} nicht dekodierte Zeichen')


if __name__ == '__main__':
    main()
