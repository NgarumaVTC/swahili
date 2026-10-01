# Lernkarten drucken

Karten 66 × 69 mm, 12 pro A4-Blatt, Vorder- und Rückseite auf demselben Blatt.

## Zuerst das Testblatt

```sh
python3 make_druckkarten.py --testblatt      # druck_testblatt.pdf
```

Ein Blatt mit zwölf durchnummerierten Karten. **Drucke es duplex, bevor du
irgendetwas anderes druckst.** Halte es gegen das Licht: auf jeder Karte muss
vorn und hinten dieselbe Zahl stehen, und vorn ein `V`, hinten ein `R`.

Stimmt das nicht, steht die Wendeeinstellung falsch. Im Druckdialog:

- **Beidseitig: an langer Kante wenden** (nicht an kurzer Kante)
- **Skalierung: 100 %** — nicht „an Seite anpassen", sonst passt das Raster nicht
- Rand: keiner / randlos aus

Zwei `V` oder zwei `R` auf einem Blatt heißt: falsch gewendet.

## Dann die Karten

```sh
python3 make_druckkarten.py haupt kontrast   # 978 Karten, 82 Blätter
python3 make_druckkarten.py drill            # 543 Karten, 46 Blätter
python3 make_druckkarten.py --referenz       # 1 Blatt Konkordanztabelle
```

| Datei | Karten | Blätter | Druckseiten |
|---|---:|---:|---:|
| `druck_satzkarten.pdf` | 978 | 82 | 164 |
| `druck_drill.pdf` | 543 | 46 | 92 |
| `druck_konkordanz.pdf` | — | 1 | 1 |

Die Konkordanzreihe steht **nicht** auf den Karten. Sie ist je Klasse immer
dieselbe; sie 978-mal zu drucken wäre Papierverschwendung. Häng das
Referenzblatt stattdessen an die Wand.

## Schneiden

Die dünnen grauen Linien sind die Schnittkanten. Mit einer Schneidemaschine
schneidest du erst alle waagerechten, dann alle senkrechten Linien — dann
bleibt der Stapel ausgerichtet.

Papier: 160–200 g/m² hält dem Mischen stand. Bei dünnerem Papier scheint die
Rückseite durch.

## Wenn eine Karte überläuft

Der Generator verkleinert die Schrift nach Textmenge automatisch (10 pt / 9 pt
/ 8 pt). Zwei Karten im Satzdeck überschreiten ihre Zelle um 0,85 mm — das
fällt beim Schneiden nicht auf. Bei eigenen Ergänzungen meldet
`make_druckkarten.py` jeden Überlauf mit Zeilennummer.
