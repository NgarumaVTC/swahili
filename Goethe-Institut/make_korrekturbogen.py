#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Korrekturboegen zum Gegenlesen durch eine Swahili-Muttersprachlerin.

Durchgehend Englisch und Swahili -- kein Wort Deutsch, auch nicht in
Kopfzeilen oder Spaltentiteln. Die Leserin spricht kein Deutsch, und ein
Bogen, den sie nur zur Haelfte lesen kann, taugt nichts.

Zwei Faszungen:
  korrektur_kurz.pdf   Anleitung + Lexikon + Minimalpaare + Konkordanztabelle
  korrektur_lang.pdf   zusaetzlich alle 850 Beispielsaetze
"""
import csv, os, subprocess, sys, tempfile
import konkordanz as K

# K.INHALT ist deutsch; fuer diesen Bogen die englische Fassung.
INHALT_EN = {
    '1/2': 'people', '3/4': 'plants, body parts, things',
    '5/6': 'paired things, fruit, augmentatives',
    '7/8': 'things, tools, languages, diminutives',
    '9/10': 'animals and loanwords; singular = plural',
    '11/10': 'long, thin things', '14': 'abstracts, no plural',
    '15': 'verbal nouns',
}

PRAEAMBEL = r"""\documentclass[10pt]{article}
\usepackage{fontspec}
\usepackage[a4paper,landscape,left=12mm,right=12mm,top=14mm,bottom=14mm]{geometry}
\usepackage{longtable}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{colortbl}
\setmainfont{Latin Modern Roman}
\setmonofont{Latin Modern Mono}
\setlength{\parindent}{0pt}
\setlength{\LTpre}{0pt}\setlength{\LTpost}{6mm}
\renewcommand{\arraystretch}{1.15}
\arrayrulecolor{black!35}
\newcommand{\korr}{\makebox[0pt][l]{\color{black!15}\rule{48mm}{0.4pt}}}
\newcommand{\sw}[1]{\textbf{#1}}
\newcommand{\gl}[1]{{\ttfamily\scriptsize\color{black!65}#1}}
\newcommand{\abschnitt}[2]{\vspace{4mm}{\large\textbf{#1}}\par
  {\footnotesize\color{black!60}#2}\par\vspace{2mm}}
\begin{document}
"""


def tex(s):
    if not s:
        return ''
    for a, b in (('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'),
                 ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'),
                 ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}')):
        s = s.replace(a, b)
    return s


def lade(p):
    with open(p, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


ANLEITUNG = r"""
{\LARGE\textbf{Swahili flashcards --- please check}}\par\vspace{4mm}

{\large Asante sana for reading through this.}\par\vspace{3mm}

\begin{minipage}{0.56\textwidth}
These cards teach Swahili to a German speaker. The Swahili sentences, the
morpheme analysis and the noun-class entries were all produced
\textbf{by a machine} and have never been checked by anyone who speaks the
language. That is what this sheet is for.

\vspace{3mm}
\textbf{What to look at, in order of importance:}

\vspace{2mm}
\textbf{1. The noun classes (Part A).} Is the Swahili word right for the
English meaning? Is the plural right? Is the class pair right? This matters
most: every card in the whole set is built from these entries, so one
correction here fixes many cards at once.

\vspace{2mm}
\textbf{2. The contrast pairs (Part B).} Each pair should differ in exactly
one thing. Does the Swahili show that difference correctly?

\vspace{2mm}
\textbf{3. The sentences (Part C).} Is the Swahili correct and natural?
Does it mean what the English says? Standard Swahili, Tanzanian usage ---
not Sheng.
\end{minipage}\hfill
\begin{minipage}{0.40\textwidth}
\colorbox{black!5}{\begin{minipage}{0.95\textwidth}\vspace{2mm}
\textbf{How to mark it}\par\vspace{2mm}
If a line is correct, leave it alone --- no tick needed.\par\vspace{2mm}
If it is wrong, cross it out and write the correction in the empty column
on the right.\par\vspace{2mm}
If you are unsure, put a question mark. That is useful too.\par\vspace{2mm}
If a sentence is grammatically possible but nobody would say it that way,
please say so --- that is exactly the kind of mistake a machine makes.
\vspace{2mm}\end{minipage}}

\vspace{4mm}
\textbf{Abbreviations in the morpheme lines}\par\vspace{1mm}
{\footnotesize
\begin{tabular}{@{}ll@{}}
\texttt{CL7} & noun class 7\\
\texttt{1SG, 2PL} & person and number\\
\texttt{PRS, PST, PRF, FUT} & tense\\
\texttt{NEG} & negative\\
\texttt{APPL, PASS, CAUS, RECP} & verb extensions\\
\texttt{GEN, DEM, POSS, REL} & agreement forms\\
\texttt{COP} & copula \textit{ni}\\
\end{tabular}}
\end{minipage}

\vspace{5mm}
{\footnotesize\color{black!60}Everything here is for private language
learning. Nothing is sold.}
\newpage
"""


def teil_a():
    """Nominalklassen-Lexikon, nach Klassenpaar gruppiert."""
    rows = [r for r in lade('klassen_lexikon.tsv') if r['sw_singular'] != '—']
    abw = [r for r in rows if r['kongruenz']]
    rest = [r for r in rows if not r['kongruenz']]

    def paar(r):
        return r['klasse_sg'] + (f"/{r['klasse_pl']}" if r['klasse_pl'] else '')

    def tabelle(gruppe, titel, gruppieren=True):
        kopf = (r'\begin{longtable}{@{}p{28mm}p{28mm}p{14mm}p{40mm}p{46mm}p{50mm}@{}}'
                + '\n' + r'\hline' + '\n'
                + r'\textbf{Swahili} & \textbf{Plural} & \textbf{Class} & '
                + r'\textbf{English} & \textbf{Note} & '
                + r'\textbf{Correction}\\\hline' + '\n' + r'\endhead' + '\n')
        # Nach Klassenpaar sortieren: zusammengehoerende Entscheidungen stehen
        # dann beieinander und lassen sich am Stueck pruefen.
        if gruppieren:
            gruppe = sorted(gruppe, key=lambda r: (
                int(r['klasse_sg'] or 99), int(r['klasse_pl'] or 0),
                r['sw_singular']))
        zeilen, letztes = [], None
        for r in gruppe:
            if gruppieren and paar(r) != letztes:
                letztes = paar(r)
                inhalt = INHALT_EN.get(letztes, '')
                zeilen.append(
                    r'\multicolumn{6}{@{}l}{\cellcolor{black!6}\textbf{class '
                    + tex(letztes) + '}'
                    + (r'\quad{\footnotesize\color{black!60}' + tex(inhalt)
                       + '}' if inhalt else '') + r'}\\')
            zeilen.append(
                r'\sw{' + tex(r['sw_singular']) + '} & '
                + tex(r['sw_plural'] or '—') + ' & ' + tex(paar(r)) + ' & '
                + tex(r['en_nomen']) + ' & '
                + r'{\footnotesize\color{black!60}' + tex(r['notiz_en']) + '} & '
                + r'\korr \\')
        return (titel + r'{\small' + kopf + '\n'.join(zeilen)
                + '\n' + r'\hline\end{longtable}}')

    a = tabelle(rest, r'\abschnitt{Part A --- nouns and their classes}'
                r'{Grouped by class pair. Is the Swahili word right, is the '
                r'plural right, is the class right?}')
    b = tabelle(abw, r'\abschnitt{Part A2 --- people: form and agreement differ}'
                r'{These nouns look like one class but agree like another --- '
                r'\textit{rafiki yangu} (class 9) but \textit{rafiki anakuja} '
                r'(class 1). Most likely place for mistakes.}',
                gruppieren=False)
    return a + '\n\\newpage\n' + b


def teil_b():
    rows = lade('karten_kontrast.tsv')
    kopf = (r'\begin{longtable}{@{}p{52mm}p{58mm}p{58mm}p{52mm}@{}}' + '\n'
            + r'\hline' + '\n'
            + r'\textbf{English} & \textbf{Swahili} & '
            + r'\textbf{Morphemes} & \textbf{Correction}\\\hline' + '\n'
            + r'\endhead' + '\n')
    zeilen = []
    for r in rows:
        zeilen.append(
            tex(r['en_a']) + r'\newline ' + tex(r['en_b']) + ' & '
            + r'\sw{' + tex(r['sw_a']) + r'}\newline \sw{' + tex(r['sw_b']) + '} & '
            + r'\gl{' + tex(r['gloss_a_mo']) + r'}\newline \gl{'
            + tex(r['gloss_a_la_en']) + r'}\newline \gl{' + tex(r['gloss_b_mo'])
            + r'}\newline \gl{' + tex(r['gloss_b_la_en']) + '} & '
            + r'\korr \\')
    tab = (r'\abschnitt{Part B --- contrast pairs}'
           r'{Each pair should differ in exactly one morpheme. '
           r'Does the Swahili show it?}'
           + kopf + '\n'.join(zeilen) + '\n' + r'\hline\end{longtable}')

    kk = (r'\abschnitt{Part B2 --- the agreement table}'
          r'{This table drives every card in the set. If a cell is wrong, '
          r'many cards are wrong.}'
          + r'\begin{longtable}{@{}l' + 'l' * len(K.FELDER) + r'p{40mm}@{}}' + '\n'
          + r'\hline' + '\n' + r'\textbf{Class} & '
          + ' & '.join(r'\textbf{' + tex(t) + '}' for t in
                       ('Prefix', 'SUBJ', 'OBJ', 'ADJ', 'GEN', 'DEM near',
                        'DEM far', 'POSS', 'REL'))
          + r' & \textbf{Correction}\\\hline' + '\n' + r'\endhead' + '\n'
          + '\n'.join(
              tex(kl) + ' & '
              + ' & '.join(r'\sw{' + tex(K.reihe(kl)[f]) + '}' for f in K.FELDER)
              + r' & \korr \\' for kl in K.TABELLE)
          + '\n' + r'\hline\end{longtable}')
    return tab + '\n\\newpage\n' + kk


def teil_c():
    rows = lade('karten_haupt.tsv')
    kopf = (r'\begin{longtable}{@{}p{62mm}p{62mm}p{62mm}p{44mm}@{}}' + '\n'
            + r'\hline' + '\n'
            + r'\textbf{English} & \textbf{Swahili} & '
            + r'\textbf{Morphemes} & \textbf{Correction}\\\hline' + '\n'
            + r'\endhead' + '\n')
    zeilen, letzter = [], None
    for r in rows:
        if r['buchstabe'] != letzter:
            letzter = r['buchstabe']
            zeilen.append(r'\multicolumn{4}{@{}l}{\textbf{\large '
                          + tex(letzter) + r'}}\\')
        zeilen.append(
            tex(r['satz_en']) + ' & ' + r'\sw{' + tex(r['satz_sw']) + '} & '
            + r'\gl{' + tex(r['gloss_morpheme']) + r'}\newline \gl{'
            + tex(r['gloss_labels_en']) + '} & ' + r'\korr \\')
    return (r'\abschnitt{Part C --- all 850 example sentences}'
            r'{Grouped by the letter of the German word list. '
            r'Is the Swahili correct, natural, and does it match the English?}'
            + kopf + '\n'.join(zeilen) + '\n' + r'\hline\end{longtable}')


def uebersetzen(quelle, ziel):
    with tempfile.TemporaryDirectory() as t:
        open(os.path.join(t, 'k.tex'), 'w', encoding='utf-8').write(quelle)
        for _ in range(2):          # longtable braucht zwei Laeufe
            r = subprocess.run(['xelatex', '-interaction=nonstopmode', 'k.tex'],
                               cwd=t, capture_output=True, text=True)
        pdf = os.path.join(t, 'k.pdf')
        if not os.path.exists(pdf):
            log = os.path.join(t, 'k.log')
            f = [l for l in open(log, encoding='utf-8', errors='replace')
                 if l.startswith('!')][:8] if os.path.exists(log) else []
            sys.exit('xelatex fehlgeschlagen:\n' + ''.join(f) + r.stdout[-1200:])
        warn = [l for l in open(os.path.join(t, 'k.log'), encoding='utf-8',
                                errors='replace') if 'Overfull \\hbox' in l]
        os.replace(pdf, ziel)
    return warn


def main():
    a, b, c = teil_a(), teil_b(), teil_c()
    for ziel, teile in (('korrektur_kurz.pdf', [a, b]),
                        ('korrektur_lang.pdf', [a, b, c])):
        doc = PRAEAMBEL + ANLEITUNG + '\n\\newpage\n'.join(teile) \
            + '\n' + r'\end{document}' + '\n'
        warn = uebersetzen(doc, ziel)
        print(f'{ziel}  ({len(warn)} Satzwarnungen)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
