# Glossierungskonvention

Verbindliche Referenz für alle Kartendateien. Labels sind deutsch, die
Segmentierung folgt den Leipzig Glossing Rules.

Jede Karte trägt zwei Zeilen, die **segmentweise übereinanderstehen**:

```
ni-na-som-a         ki-tabu   cha
1SG-PRÄS-lesen-IND  KL7-Buch  KL7-GEN
```

Regel: `gloss_morpheme` und `gloss_labels` haben zeilenweise **gleich viele
bindestrichgetrennte Segmente pro Wort und gleich viele Wörter**. Das ist
maschinell prüfbar und der wichtigste Integritätstest des ganzen Kartensatzes.

## Verbalstruktur

```
SUBJ - TAM - (OBJ) - WURZEL - (ABLEITUNG) - ENDVOKAL
ni   - na  -        - som    -             - a
```

### Subjektpräfixe

| | Singular | Plural |
|---|---|---|
| 1. Person | `ni-` 1SG | `tu-` 1PL |
| 2. Person | `u-` 2SG | `m-` 2PL |
| 3. Person (Kl. 1/2) | `a-` 3SG | `wa-` 3PL |

Bei Nicht-Personen steht die Klasse statt der Person: `KL5`, `KL7`, `KL9` …
Also `ki-na-…` = `KL7-PRÄS-…`, nicht `3SG-PRÄS-…`.

### TAM-Marker

| Morphem | Label | Bedeutung |
|---|---|---|
| `-na-` | `PRÄS` | Präsens / Verlaufsform |
| `-a-` | `PRÄS.ALLG` | allgemeines Präsens (*nasoma*) |
| `-li-` | `PRÄT` | Vergangenheit |
| `-me-` | `PERF` | Perfekt, Resultat liegt vor |
| `-ta-` | `FUT` | Futur |
| `hu-` | `HAB` | Gewohnheit — **ohne** Subjektpräfix |
| `-ki-` | `KOND` | wenn/falls |
| `-nge-` | `IRR` | würde (Gegenwart) |
| `-ngali-` | `IRR.VERG` | hätte (Vergangenheit) |
| `-ka-` | `KONSEK` | und dann |
| — | `KONJ` | Konjunktiv: kein TAM, Endvokal `-e` |

### Negation

Negation ist mehrteilig und wird **an jedem beteiligten Morphem** glossiert.

| Form | Segmentierung | Labels |
|---|---|---|
| *sisomi* | `si-som-i` | `1SG.NEG-lesen-NEG` |
| *hasomi* | `ha-som-i` | `3SG.NEG-lesen-NEG` |
| *hatusomi* | `hatu-som-i` | `1PL.NEG-lesen-NEG` |
| *sikusoma* | `si-ku-som-a` | `1SG.NEG-PRÄT.NEG-lesen-IND` |
| *sijasoma* | `si-ja-som-a` | `1SG.NEG-PERF.NEG-lesen-IND` |
| *sitasoma* | `si-ta-som-a` | `1SG.NEG-FUT-lesen-IND` |

Negative Subjektpräfixe: `si-` 1SG · `hu-` 2SG · `ha-` 3SG · `hatu-` 1PL ·
`ham-` 2PL · `hawa-` 3PL. Im Präsens wechselt zusätzlich der Endvokal von
`-a` zu `-i` — der häufigste Fehler überhaupt, darum eigenes Label `NEG`.

### Objektpräfixe

`OBJ` plus Person oder Klasse: `OBJ1SG`, `OBJ2SG`, `OBJ3SG`, `OBJ7` …
*ninakisoma* → `ni-na-ki-som-a` / `1SG-PRÄS-OBJ7-lesen-IND`

### Ableitungen

| Morphem | Label | Wirkung |
|---|---|---|
| `-i-` / `-e-` | `APPL` | Applikativ: für/zu jemanden |
| `-w-` | `PASS` | Passiv |
| `-sh-` / `-z-` | `KAUS` | Kausativ: veranlassen |
| `-k-` | `STAT` | Stativ: Zustand |
| `-an-` | `REZ` | reziprok: einander |

### Endvokal

`IND` für `-a` (Indikativ), `KONJ` für `-e` (Konjunktiv, Imperativ Plural),
`NEG` für `-i` im negativen Präsens.

Arabische Lehnverben enden nicht auf `-a` und werden **nicht** segmentiert:
*kusamehe*, *kujibu*, *kufikiri*. Glosse: `jibu` / `antworten`.

## Nomen

`KLn-Stamm`, also `ki-tabu` / `KL7-Buch`. Bei Nullpräfix (Kl. 9/10) steht
kein Segment, sondern nur `KL9-Tasche` für *mfuko*… — Gegenbeispiel: *barua*
ist Kl. 9 ohne sichtbares Präfix, Glosse `barua` / `KL9.Brief`. Punkt statt
Bindestrich, wenn das Morphem nicht abtrennbar ist.

## Einsilbige Verbstämme behalten ku-

Bei *kwenda*, *kuja*, *kula*, *kunywa*, *kuwa* bleibt das `ku-` in finiten
Formen erhalten. Dort ist es **kein** Verbalnomen der Kl. 15 und wird nicht
eigens glossiert, sondern als Teil des Stammes geschrieben:

| Form | `gloss_morpheme` | `gloss_labels` |
|---|---|---|
| *linakwenda* | `li-na-kwend-a` | `KL5-PRÄS-gehen-IND` |
| *tutakuwa* | `tu-ta-kuw-a` | `1PL-FUT-sein-IND` |
| *kwenda* (Infinitiv) | `kw-end-a` | `KL15-gehen-IND` |

## Genitivpartikel immer segmentieren

Die Genitivpartikel ist Konkordanzpräfix + `-a` und wird **getrennt
geschrieben**, auch wenn die Orthographie sie zusammenschreibt:

| Satz | `gloss_morpheme` | `gloss_labels` |
|---|---|---|
| *kitabu cha mwalimu* | `ch-a` | `KL7-GEN` |
| *barua ya rafiki* | `y-a` | `KL9-GEN` |
| *jina la mtoto* | `l-a` | `KL5-GEN` |
| *viatu vya michezo* | `vy-a` | `KL8-GEN` |
| *mwanzoni mwa Julai* | `mw-a` | `KL18-GEN` |

Ebenso bei den negativen Subjektpräfixen: sie sind **ein** Segment, auch wenn
sie aus `ha-` plus Subjektpräfix verschmolzen sind — `hai-` (Kl. 9), `hau-`
(Kl. 3/11/14), `haya-` (Kl. 6), `hatu-` (1PL), `ham-` (2PL), `hawa-` (3PL).

## Konkordanzen

Jede Klasse steuert Adjektiv, Genitiv, Demonstrativ, Possessiv und Relativ.
Diese Tabelle ist die Quelle für das Drilldeck.

| Kl. | Nominalpräfix | SUBJ | OBJ | ADJ | GEN | DEM nah | DEM fern | POSS | REL |
|----:|---|---|---|---|---|---|---|---|---|
| 1 | m-/mw- | a- | -m-/-mw- | m-/mw- | wa | huyu | yule | w- | -ye |
| 2 | wa- | wa- | -wa- | wa- | wa | hawa | wale | w- | -o |
| 3 | m-/mw- | u- | -u- | m-/mw- | wa | huu | ule | w- | -o |
| 4 | mi- | i- | -i- | mi- | ya | hii | ile | y- | -yo |
| 5 | ji-/Ø | li- | -li- | ji-/Ø | la | hili | lile | l- | -lo |
| 6 | ma- | ya- | -ya- | ma- | ya | haya | yale | y- | -yo |
| 7 | ki- | ki- | -ki- | ki- | cha | hiki | kile | ch- | -cho |
| 8 | vi- | vi- | -vi- | vi- | vya | hivi | vile | vy- | -vyo |
| 9 | Ø/n- | i- | -i- | Ø/n- | ya | hii | ile | y- | -yo |
| 10 | Ø/n- | zi- | -zi- | Ø/n- | za | hizi | zile | z- | -zo |
| 11 | u- | u- | -u- | m-/mw- | wa | huu | ule | w- | -o |
| 14 | u- | u- | -u- | m-/mw- | wa | huu | ule | w- | -o |
| 15 | ku- | ku- | -ku- | ku- | kwa | huku | kule | kw- | -ko |
| 16 | pa- | pa- | -pa- | pa- | pa | hapa | pale | p- | -po |
| 17 | ku- | ku- | -ku- | ku- | kwa | huku | kule | kw- | -ko |
| 18 | mu-/m- | mu- | -mu- | mu- | mwa | humu | mule | mw- | -mo |

### Klassenpaare und typischer Inhalt

| Paar | Inhalt | Beispiel |
|---|---|---|
| 1/2 | Personen | *mtu / watu* |
| 3/4 | Pflanzen, Körperteile, Dinge | *mti / miti* |
| 5/6 | Paarige Dinge, Früchte, Augmentativa | *jicho / macho* |
| 7/8 | Dinge, Werkzeuge, Sprachen, Diminutiva | *kitabu / vitabu* |
| 9/10 | Tiere, Lehnwörter — Singular = Plural | *barua / barua* |
| 11/10 | Lange, dünne Dinge | *ubao / mbao* |
| 14 | Abstrakta, kein Plural | *upendo* |
| 15 | Verbalnomen | *kusoma* |
| 16–18 | Ortsangaben | *mahali*, *nyumbani* |

### Zwei Fallen, die eigene Kennzeichnung brauchen

**Personen kongruieren als 1/2, unabhängig von ihrer Form.** *rafiki* ist
formal Kl. 9/10, verhält sich aber wie Kl. 1/2: *rafiki yangu* (Kl. 9-Possessiv)
aber *rafiki anakuja* (Kl. 1-Subjekt). Solche Wörter tragen im Lexikon die
Spalte `kongruenz_abweichend`, und die Glosse nennt beide:
`KL9/KL1-Freund`.

**Kl. 9/10 unterscheidet Singular und Plural nicht am Nomen**, nur an der
Konkordanz: *barua hii* (eine) vs. *barua hizi* (mehrere). Deshalb ist für
diese Klasse der Kontrastsatz im Kontrastdeck obligatorisch — ohne
Konkordanz ist der Numerus nicht erkennbar.

## Register

Kiswahili sanifu, tansanische Norm. Kein Sheng, keine Nairobi-Umgangsformen.

Deutsches höfliches *Sie* hat keine Entsprechung. Es wird durch den
Numerus-Plural wiedergegeben (`m-` 2PL), was die Glosse sichtbar macht:
*mnasoma* → `m-na-som-a` / `2PL-PRÄS-lesen-IND`. Das ist Absicht und kein
Übersetzungsfehler — die Karte prüft Swahili, nicht die deutsche Anredeform.

## Feldnamen in den TSV-Dateien

| Feld | Inhalt |
|---|---|
| `satz_sw` | Swahili-Satz, normale Orthographie |
| `gloss_morpheme` | segmentierte Morphemzeile |
| `gloss_labels` | Labelzeile, segmentkongruent zu `gloss_morpheme` |
| `klassen` | Nominalklassen der Substantive samt Plural |
| `konkordanz` | Konkordanzreihe der im Satz geprüften Klasse |
