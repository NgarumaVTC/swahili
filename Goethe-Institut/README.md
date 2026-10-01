# Swahili-Lernkarten auf Basis der Goethe-A1-Wortliste

Lernziel ist **Swahili**. Die offizielle Goethe-Wortliste zum *Zertifikat A1 /
Start Deutsch 1* (`A1_SD1_Wortliste_02.pdf`) dient nur als Gerüst: sie
garantiert, dass der Kartensatz den Alltagswortschatz abdeckt, statt dass
Vokabeln willkürlich ausgewählt werden.

Gelernt wird in vier Richtungen, mit sichtbarer Morphologie auf jeder
Rückseite: Morphem-für-Morphem-Glossierung, Nominalklasse mit Plural,
Konkordanzreihe und ein Hinweis auf die jeweilige Swahili-Eigenheit.

## Herkunft der deutschen Sätze

Die 850 deutschen Beispielsätze sind **wörtlich** der Goethe-Wortliste
entnommen, © Goethe-Institut e. V. und telc GmbH. Eine Erlaubnis dafür wurde
nicht eingeholt. Einzelheiten und das Angebot an den Rechteinhaber:
[`../HERKUNFT.md`](../HERKUNFT.md). Lizenz des eigenen Teils und Liste der
ausgenommenen Dateien: [`../LICENSE.md`](../LICENSE.md).

## Umfang

| Deck | Notizen | Karten |
|---|---:|---:|
| Hauptkarten aus den 850 Goethe-Beispielsätzen | 850 | 3.400 |
| Kontrastdeck: Minimalpaare | 128 | 512 |
| Drilldeck: Klassen und Konkordanzen | 544 | 544 |
| **Summe** | **1.522** | **4.456** |

Einstieg → `ANKI_SETUP.md`.

## Was hier drinsteht und warum

Die Goethe-Sätze stellen **nie** zwei Formen gegenüber. Für Nominalklassen und
TAM-Marker braucht man aber genau das: erst im Paar wird sichtbar, welches
Morphem die Bedeutung trägt. Darum das **Kontrastdeck** — 128 Paare, die sich
in genau einem Morphem unterscheiden:

```
Ninasoma kitabu.          Nimesoma vitabu vingi.
ni-na-som-a  ki-tabu      ni-me-som-a  vi-tabu  vi-ngi
1SG-PRÄS-lesen-IND KL7    1SG-PERF-lesen-IND KL8 KL8-viele
                     Δ    -na- ki-  →  -me- vi-
```

Der didaktisch wichtigste Fall sind die Klassen 9/10: dort zeigen **weder
Nomen noch Adjektiv** den Numerus (*barua nzuri* ist Singular wie Plural).
Nur die Konkordanz tut es — *barua hii* gegen *barua hizi*. Für diese Klassen
baut der Generator die Karten eigens so, dass der Unterschied am Demonstrativ
hängt.

Ebenso kennzeichnet das Lexikon 20 Personenwörter, deren **Form** und
**Kongruenz** auseinanderfallen. *rafiki* ist formal Kl. 9/10, verhält sich
aber wie Kl. 1/2: *rafiki yangu* (Kl. 9), aber *rafiki anakuja* (Kl. 1).

Das **Drilldeck** fragt die Klassen Swahili-intern ab, nennt aber immer die
Bedeutung mit: *mguu (das Bein, der Fuß) — welche Nominalklasse?* Eine Klasse
zu einem Wort zu lernen, das man nicht kennt, ist Unsinn. Da das Lexikon nach
dem deutschen Stichwort gebaut ist, stehen Synonyme dabei auf **einer** Karte
— *kazi (der Beruf, der Job, die Arbeit)* — statt dass drei von ihnen als
Dublette wegfallen.

## Dateien

### Quellen und Referenz

| Datei | Inhalt |
|---|---|
| `A1_SD1_Wortliste_02.pdf` | Goethe-Wortliste, 29 Seiten |
| `GLOSSING.md` | Glossierungskonvention, Konkordanztabelle Kl. 1–18 |
| `klassen_lexikon.tsv` | 330 Substantive: Swahili, Klassenpaar, Kongruenz |
| `konkordanz.py` | Konkordanztabelle als Maschinenfassung |
| `adjektive.py` | Adjektivformen je Klasse samt Segmentierung |

### Pipeline

| Datei | Zweck |
|---|---|
| `pdftext.py` | Textextraktion aus dem PDF, nur Standardbibliothek |
| `extract_wortliste.py` | PDF S. 9–27 → `wortliste_de.tsv` (850 Sätze) |
| `extract_wortgruppen.py` | PDF S. 6–8 → `wortgruppen_de.tsv` (145 Einträge) |
| `batch_haupt_*.tsv` | Übersetzungen, eine Datei pro PDF-Seite |
| `build_karten.py` | Batches + Lexikon → `karten_haupt.tsv` |
| `generate_kontrast.py` | → `karten_kontrast.tsv` |
| `generate_drill.py` | → `karten_drill.tsv` |
| `build_anki.py` | → `anki_*.tsv` |
| `glossar_en.tsv` · `glossen_en.py` | englische Glossen, segmenterhaltend |
| `make_druckkarten.py` | → `druck_*.pdf`, 12 Karten pro A4-Blatt |
| `make_korrekturbogen.py` | → `korrektur_kurz.pdf`, `korrektur_lang.pdf` |
| `check_karten.py` | Integritätsprüfung |
| `install_anki.py` | `anki_*.tsv` → laufende Anki-Sammlung per AnkiConnect |

### Ergebnis

`Swahili-A1-SD1-Deutsch.apkg` — fertiges Deck zum Importieren, deutsche
Richtungen, 1.522 Notizen / 2.500 Karten. Sonst:

`anki_master.tsv` (ein Notiztyp, vier Richtungen) · `anki_sw_de.tsv` ·
`anki_sw_en.tsv` · `anki_de_sw.tsv` · `anki_en_sw.tsv` · `anki_drill.tsv`

Zum Drucken: `druck_satzkarten.pdf` (82 Blätter) · `druck_drill.pdf`
(46 Blätter) · `druck_konkordanz.pdf` · `druck_testblatt.pdf` — siehe
`DRUCKEN.md`.

Zum Gegenlesen: `korrektur_kurz.pdf` (33 Seiten) und `korrektur_lang.pdf`
(108 Seiten), durchgehend englisch und Swahili — siehe `KORREKTUR.md`.

## Neu bauen

```sh
python3 extract_wortliste.py      # PDF → Deutsch
python3 extract_wortgruppen.py
python3 build_karten.py           # + Übersetzungen → Hauptkarten
python3 generate_kontrast.py
python3 generate_drill.py
python3 check_karten.py karten_haupt.tsv karten_kontrast.tsv
python3 build_anki.py
```

Alles läuft mit der Python-Standardbibliothek. Kein `poppler`, kein `pypdf`,
kein `genanki`.

## Zur Technik der PDF-Extraktion

Drei Dinge, an denen ein naiver Ansatz scheitert und die hier gelöst sind:

1. **`Td`/`TD`-Offsets sind Textraum-Einheiten**, skaliert durch die
   Fontmatrix. Unskaliert addiert ergeben sie zufällig plausible, aber falsche
   Positionen.
2. **Ein Teil des Textes liegt in einem Identity-H-Subsetfont** als
   Hex-CIDs. Ohne Auswertung der ToUnicode-CMap fehlen ganze Einträge —
   zum Beispiel *abfahren* mitsamt Beispielsatz.
3. **Glyphenvorschübe müssen aus `/Widths` und `/W` berechnet werden.** Sonst
   bleibt x innerhalb einer Zeile auf dem Wert der letzten Positionierung
   stehen, und 38 Zeilen, die ohne `Td` von der Stichwort- in die Satzspalte
   laufen, sind nicht mehr trennbar.

## Korrekturen

Klassenzuordnungen entstehen **nur** in `klassen_lexikon.tsv`. Eine Korrektur
dort wirkt nach erneutem Lauf auf alle betroffenen Karten in allen drei Decks.
Das ist der Hebel mit dem besten Verhältnis von Aufwand zu Wirkung.

`check_karten.py` prüft:

- Morphem- und Labelzeile segmentweise deckungsgleich (harter Fehler)
- Negation nur mit negativem Subjektpräfix
- Klassenangaben konsistent mit dem Lexikon, Homonyme ausgenommen
- keine Tabs, Umbrüche oder Ersatzzeichen in Feldern

## Einschränkung

Die ~1.000 Swahili-Sätze samt Morphemanalyse sind maschinell erzeugt und
nicht gegen eine Quelle verifiziert. Bei Klassen 9/10, bei Lehnwörtern, bei
abweichender Personenkongruenz und bei idiomatischer Formulierung ist eine
Fehlerquote anzunehmen.

Vor dem ernsthaften Lernen sollte jemand mit L1-Swahili mindestens
`klassen_lexikon.tsv` durchsehen — 330 Zeilen, in etwa einer Stunde machbar.
Daraus folgt alles andere.
