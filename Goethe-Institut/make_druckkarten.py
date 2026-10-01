#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Lernkarten zum Ausschneiden, beidseitig bedruckt.

A4, 3 Spalten x 4 Zeilen, Karte 66 x 69 mm. Schrift Latin Modern -- Knuths
Computer Modern in der unicodefaehigen Fassung; das originale cmr10 koennte
weder das Nullpraefix Ø noch den Pluralpfeil →.

Der kritische Teil ist der Duplexdruck: beim Wenden ueber die lange Kante
muss die Rueckseite spaltenweise gespiegelt sein, sonst steht jede Antwort
hinter der falschen Frage. Darum --testblatt vor dem ersten echten Druck.
"""
import csv, os, subprocess, sys, tempfile

SPALTEN, ZEILEN = 3, 4
PRO_BLATT = SPALTEN * ZEILEN

PRAEAMBEL = r"""\documentclass[10pt]{article}
\usepackage{fontspec}
\usepackage[a4paper,left=6mm,right=6mm,top=10.5mm,bottom=10.5mm]{geometry}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{colortbl}
\setmainfont{Latin Modern Roman}
\setmonofont{Latin Modern Mono}
\pagestyle{empty}
\setlength{\parindent}{0pt}
% topskip schiebt die erste Box 10pt nach unten; das Raster
% fuellt die Seite exakt und rutschte dadurch auf die naechste.
\setlength{\topskip}{0pt}
\setlength{\parskip}{0pt}
\setlength{\tabcolsep}{0pt}
\setlength{\arrayrulewidth}{0.1pt}
\arrayrulecolor{black!30}
\renewcommand{\arraystretch}{1}
\newlength{\kartew}\newlength{\karteh}\newlength{\innenw}
\setlength{\kartew}{\dimexpr(\textwidth-4\arrayrulewidth)/3\relax}
% Etwas Spiel: Zeilen in einem tabular tragen ausser dem parbox
% noch Grundlinienabstand, sonst kippt das Raster auf die Folgeseite.
\setlength{\karteh}{\dimexpr(\textheight-5\arrayrulewidth-30pt)/4\relax}
\setlength{\innenw}{\dimexpr\kartew-6mm\relax}
\newcommand{\ecke}[1]{{\fontsize{6}{7}\selectfont\color{black!45}#1}}
\newcommand{\karte}[1]{%
  \parbox[t][\karteh][c]{\kartew}{\hfill
    \begin{minipage}{\innenw}#1\end{minipage}\hfill}}
\begin{document}
"""


def tex(s):
    """LaTeX-Sonderzeichen entschaerfen. xelatex vertraegt Unicode direkt."""
    if not s:
        return ''
    for a, b in (('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'),
                 ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'),
                 ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}')):
        s = s.replace(a, b)
    return s


def groesse(zeichen):
    """Schriftgrad nach Textmenge -- lange Saetze duerfen nicht ueberlaufen."""
    if zeichen < 45:
        return r'\fontsize{10}{12}\selectfont'
    if zeichen < 70:
        return r'\fontsize{9}{11}\selectfont'
    return r'\fontsize{8}{9.5}\selectfont'


def glossen_block(morpheme, labels, breite_zeichen=52, pt='5.5'):
    """Morphem- und Labelzeile als umbrechende Paartabelle.

    Labelwoerter werden bis zu 36 Zeichen lang; nebeneinander passen sie
    nicht auf 66 mm. Darum werden die Paare in Gruppen gebrochen, die je
    eine Zeile fuellen -- die Ausrichtung Morphem ueber Label bleibt.
    """
    mo, la = (morpheme or '').split(), (labels or '').split()
    if not mo or len(mo) != len(la):
        return ''
    gruppen, akt, breite = [], [], 0
    for m, l in zip(mo, la):
        w = max(len(m), len(l)) + 2
        if akt and breite + w > breite_zeichen:
            gruppen.append(akt); akt, breite = [], 0
        akt.append((m, l)); breite += w
    if akt:
        gruppen.append(akt)

    teile = []
    for g in gruppen:
        spalten = 'l' * len(g)
        oben = ' & '.join(f'{tex(m)}' for m, _ in g)
        unten = ' & '.join(f'{tex(l)}' for _, l in g)
        teile.append(
            r'\begin{tabular}{@{}' + spalten + r'@{}}' + '\n'
            + oben + r'\\' + '\n'
            + r'\color{black!55}' + unten + '\n'
            + r'\end{tabular}')
    return (r'{\ttfamily\fontsize{' + pt + r'}{' + str(float(pt) + 1.2)
            + r'}\selectfont\setlength{\tabcolsep}{2pt}'
            + r'\\[0.3ex]'.join(teile) + r'}')


def kuerzen(s, n):
    return s if len(s) <= n else s[:n - 1].rstrip(' ·,') + '…'


def vorderseite(k):
    satz = tex(k['satz_de'])
    stich = tex(k.get('stichwort') or '')
    quelle = tex(k.get('quelle') or '')
    kopf = r'\raggedleft\ecke{V}\par\vspace{1.5mm}'
    body = (r'\centering ' + groesse(len(k['satz_de'])) + ' ' + satz
            + r'\par\vspace{2.5mm}')
    if stich:
        body += (r'{\fontsize{7}{8}\selectfont\fbox{\strut ' + stich
                 + r'}}\par')
    fuss = (r'\vspace{2mm}{\fontsize{6}{7}\selectfont\color{black!45}'
            + quelle + r'}') if quelle else ''
    return kopf + body + fuss


def rueckseite(k):
    kopf = r'\raggedleft\ecke{R}\par\vspace{1.5mm}'
    body = (r'\centering ' + groesse(len(k['satz_sw'])) + ' '
            + tex(k['satz_sw']) + r'\par\vspace{1.5mm}')
    g = glossen_block(k.get('gloss_morpheme'), k.get('gloss_labels'))
    if g:
        body += g + r'\par\vspace{1.5mm}'
    kl = kuerzen(k.get('klassen') or '', 110)
    if kl:
        body += (r'{\fontsize{6}{7}\selectfont\color{black!60}' + tex(kl)
                 + r'\par}\vspace{1mm}')
    hw = k.get('hinweis') or ''
    if hw:
        body += (r'{\fontsize{6}{7.5}\selectfont\itshape\color{black!75}'
                 + tex(kuerzen(hw, 90)) + r'\par}')
    return kopf + body


def blatt(karten, seite_bauen, spiegeln):
    """Ein Blatt mit bis zu 12 Karten. Rueckseiten spaltenweise gespiegelt."""
    zeilen_tex = []
    for z in range(ZEILEN):
        zelle = []
        for s in range(SPALTEN):
            idx = z * SPALTEN + (SPALTEN - 1 - s if spiegeln else s)
            k = karten[idx] if idx < len(karten) else None
            zelle.append(r'\karte{' + (seite_bauen(k) if k else '') + '}')
        zeilen_tex.append(' & '.join(zelle))
    return (r'\noindent\begin{tabular}{|c|c|c|}\hline' + '\n'
            + (r'\\\hline' + '\n').join(zeilen_tex)
            + r'\\\hline' + '\n' + r'\end{tabular}')


def dokument(karten, titel=''):
    seiten = []
    for i in range(0, len(karten), PRO_BLATT):
        gruppe = karten[i:i + PRO_BLATT]
        seiten.append(blatt(gruppe, vorderseite, False))
        seiten.append(blatt(gruppe, rueckseite, True))
    return PRAEAMBEL + ('\n\\newpage\n'.join(seiten)) + '\n\\end{document}\n'


def uebersetzen(tex_quelle, ziel):
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, 'k.tex')
        open(p, 'w', encoding='utf-8').write(tex_quelle)
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', 'k.tex'],
                           cwd=t, capture_output=True, text=True)
        pdf = os.path.join(t, 'k.pdf')
        if not os.path.exists(pdf):
            log = os.path.join(t, 'k.log')
            fehler = [l for l in open(log, encoding='utf-8', errors='replace')
                      if l.startswith('!')][:8] if os.path.exists(log) else []
            sys.exit('xelatex fehlgeschlagen:\n' + ''.join(fehler)
                     + r.stdout[-1500:])
        warn = [l for l in open(os.path.join(t, 'k.log'), encoding='utf-8',
                                errors='replace')
                if 'Overfull \\hbox' in l or 'Missing character' in l]
        os.replace(pdf, ziel)
    return warn


def lade(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


def karten_haupt():
    return [{'satz_de': r['satz_de'], 'satz_sw': r['satz_sw'],
             'stichwort': r['stichwort'], 'quelle': f"A1 · S.{r['seite']}",
             'gloss_morpheme': r['gloss_morpheme'],
             'gloss_labels': r['gloss_labels'],
             'klassen': r['klassen'], 'hinweis': r['hinweis']}
            for r in lade('karten_haupt.tsv')]


def karten_kontrast():
    aus = []
    for r in lade('karten_kontrast.tsv'):
        aus.append({
            'satz_de': f"{r['de_a']}\\par\\vspace{{1mm}}{r['de_b']}",
            'satz_sw': f"{r['sw_a']}\\par\\vspace{{1mm}}{r['sw_b']}",
            'stichwort': r['kontrasttyp'], 'quelle': 'Kontrast',
            'gloss_morpheme': r['gloss_a_mo'], 'gloss_labels': r['gloss_a_la'],
            'klassen': r['unterschied'], 'hinweis': r['hinweis']})
    return aus


def karten_drill():
    return [{'satz_de': r['vorderseite'], 'satz_sw': r['rueckseite'],
             'stichwort': r['typ'], 'quelle': 'Drill',
             'gloss_morpheme': '', 'gloss_labels': '',
             'klassen': '', 'hinweis': r['erklaerung']}
            for r in lade('karten_drill.tsv')]


def testblatt():
    return [{'satz_de': r'\Huge ' + str(i + 1), 'satz_sw': r'\Huge ' + str(i + 1),
             'stichwort': 'Test', 'quelle': 'Ausrichtung',
             'gloss_morpheme': '', 'gloss_labels': '', 'klassen': '',
             'hinweis': 'Vorn und hinten muss dieselbe Zahl stehen.'}
            for i in range(PRO_BLATT)]


def main(argv):
    if '--testblatt' in argv:
        k, ziel = testblatt(), 'druck_testblatt.pdf'
    elif '--referenz' in argv:
        import konkordanz as K
        # Feldnamen tragen Unterstriche; als Spaltentitel muessen sie weg.
        titel = {'praefix': 'Präfix', 'subj': 'SUBJ', 'obj': 'OBJ',
                 'adj': 'ADJ', 'gen': 'GEN', 'dem_nah': 'DEM nah',
                 'dem_fern': 'DEM fern', 'poss': 'POSS', 'rel': 'REL'}
        kopf = ' & '.join(r'\textbf{' + tex(titel[f]) + '}' for f in K.FELDER)
        zeilen = [r'\textbf{Kl. ' + kl + r'} & ' + ' & '.join(
            tex(K.reihe(kl)[f]) for f in K.FELDER) + r'\\'
            for kl in K.TABELLE]
        inhalt = ' & '.join(r'\textbf{' + tex(I) + '}'
                            for I in ('Paar', 'Inhalt'))
        paare = [tex(p) + ' & ' + tex(t) + r'\\' for p, t in K.INHALT.items()]
        doc = (PRAEAMBEL.replace('left=6mm,right=6mm', 'left=12mm,right=12mm')
               + r'{\large\textbf{Konkordanzen der Nominalklassen}}'
               + r'\par\vspace{1mm}{\footnotesize\color{black!60}'
               + r'Referenzblatt zu den Lernkarten — die Reihe steht nicht auf '
               + r'jeder Karte, weil sie je Klasse immer dieselbe ist.}'
               + r'\par\vspace{4mm}'
               + r'{\small\setlength{\tabcolsep}{5pt}'
               + r'\begin{tabular}{l' + 'l' * len(K.FELDER) + r'}\hline' + '\n'
               + r'\textbf{} & ' + kopf + r'\\\hline' + '\n'
               + '\n'.join(zeilen) + r'\hline\end{tabular}}'
               + r'\par\vspace{8mm}'
               + r'{\large\textbf{Klassenpaare und typischer Inhalt}}'
               + r'\par\vspace{3mm}'
               + r'{\small\setlength{\tabcolsep}{5pt}'
               + r'\begin{tabular}{ll}\hline' + '\n' + inhalt + r'\\\hline' + '\n'
               + '\n'.join(paare) + r'\hline\end{tabular}}' + '\n'
               + r'\end{document}' + '\n')
        warn = uebersetzen(doc, 'druck_konkordanz.pdf')
        print(f'druck_konkordanz.pdf  ({len(warn)} Warnungen)')
        return 0
    else:
        decks = [a for a in argv if not a.startswith('-')] or ['haupt', 'kontrast']
        k = []
        for d in decks:
            k += {'haupt': karten_haupt, 'kontrast': karten_kontrast,
                  'drill': karten_drill}[d]()
        ziel = ('druck_drill.pdf' if decks == ['drill']
                else 'druck_satzkarten.pdf')
    warn = uebersetzen(dokument(k), ziel)
    blaetter = -(-len(k) // PRO_BLATT)
    print(f'{ziel}: {len(k)} Karten, {blaetter} Blätter '
          f'({blaetter * 2} Druckseiten duplex)')
    if warn:
        print(f'  {len(warn)} Satzwarnungen (Überlauf oder fehlende Glyphe)')
        for w in warn[:5]:
            print('   ', w.strip()[:110])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
