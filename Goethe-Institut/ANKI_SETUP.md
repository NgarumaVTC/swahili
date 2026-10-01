# Anki einrichten

Zwei Wege. Der erste ist der, den man pflegen kann.

## Weg 1 — ein Notiztyp, vier Richtungen (empfohlen)

Eine Notiz erzeugt alle vier Karten. Korrigierst du einen Satz, ändert er
sich in allen vier Richtungen mit. Bei den flachen Decks (Weg 2) müsstest du
jede Korrektur viermal machen.

### Notiztyp anlegen

*Werkzeuge → Notiztypen → Hinzufügen → Grundlegend hinzufügen*, nenne ihn
**Swahili A1 SD1**. Dann *Felder…* und genau diese elf Felder in dieser
Reihenfolge anlegen:

```
Stichwort · Deutsch · Englisch · Swahili · Morpheme · Labels · Gloss
Klassen · Konkordanz · Hinweis · Quelle · Tags
```

`Gloss` enthält die Glossen als fertige HTML-Tabelle, in der Morpheme und
Labels exakt untereinander stehen. `Morpheme` und `Labels` bleiben zusätzlich
als Rohtext erhalten, damit du nach Morphemen suchen kannst.

Die Reihenfolge muss stimmen — `anki_master.tsv` hat keine Kopfzeile für den
Import, die Spalten werden der Position nach zugeordnet.

### Importieren

*Datei → Importieren → `anki_master.tsv`*

- Feldtrennzeichen: **Tabulator**
- Notiztyp: **Swahili A1 SD1**
- „Erste Zeile ist Kopfzeile": **an** (die Datei hat eine)
- „HTML in Feldern erlauben": **an**
- Feld 12 (`Tags`) als **Tags** zuordnen, nicht als Feld

### Die vier Kartenvorlagen

*Karten…*, dann über *Optionen → Kartentyp hinzufügen* insgesamt vier
anlegen. Vorderseite und Rückseite jeweils so:

**1 · SW → DE** (Swahili lesen, Deutsch produzieren)

```html
<div class=prompt>{{Swahili}}</div>
```
```html
{{FrontSide}}<hr id=answer>
<div class=ziel>{{Deutsch}}</div>
{{#Gloss}}<div class=glossbox>{{Gloss}}</div>{{/Gloss}}
{{#Klassen}}<div class=klassen>{{Klassen}}</div>{{/Klassen}}
{{#Konkordanz}}<div class=konkordanz>{{Konkordanz}}</div>{{/Konkordanz}}
{{#Hinweis}}<div class=hinweis>{{Hinweis}}</div>{{/Hinweis}}
<div class=quelle>{{Stichwort}} · {{Quelle}}</div>
```

**2 · SW → EN** — dieselbe Vorlage, `{{Deutsch}}` durch `{{Englisch}}` ersetzen.

**3 · DE → SW** (Deutsch lesen, Swahili produzieren — die Hauptrichtung)

```html
<div class=prompt>{{Deutsch}}</div>
<div class=stichwort>{{Stichwort}}</div>
```
```html
{{FrontSide}}<hr id=answer>
<div class=ziel>{{Swahili}}</div>
{{#Gloss}}<div class=glossbox>{{Gloss}}</div>{{/Gloss}}
{{#Klassen}}<div class=klassen>{{Klassen}}</div>{{/Klassen}}
{{#Konkordanz}}<div class=konkordanz>{{Konkordanz}}</div>{{/Konkordanz}}
{{#Hinweis}}<div class=hinweis>{{Hinweis}}</div>{{/Hinweis}}
<div class=quelle>{{Quelle}}</div>
```

**4 · EN → SW** — dieselbe Vorlage, `{{Deutsch}}` durch `{{Englisch}}`
ersetzen und die `stichwort`-Zeile weglassen.

Das Stichwort steht nur bei **DE → SW** auf der Vorderseite. Dort hilft es:
es sagt dir, welche Vokabel gemeint ist, wenn der deutsche Satz mehrere
Möglichkeiten zulässt. In der Richtung SW → DE wäre es ein Spoiler.

### CSS

*Karten… → Styling*:

```css
.card { font-family: -apple-system, Segoe UI, system-ui, sans-serif;
        font-size: 19px; text-align: center; line-height: 1.5;
        color: #1a1a1a; background: #fcfcfa; }
.prompt    { font-size: 23px; font-weight: 500; }
.ziel      { font-size: 25px; font-weight: 600; margin: 0.4em 0 0.7em; }
.stichwort { font-size: 15px; color: #777; margin-top: 0.5em; }
.glossbox  { display: inline-block; background: #f2f1ec; padding: 6px 10px;
             border-radius: 6px; margin: 0.5em 0; overflow-x: auto;
             max-width: 100%; }
table.gloss { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
             font-size: 13px; border-collapse: collapse; margin: 0 auto; }
table.gloss td { padding: 1px 7px; text-align: left; white-space: nowrap;
             vertical-align: top; }
table.gloss tr.mo td { font-weight: 600; }
table.gloss tr.la td { color: #8a5a00; font-size: 12px; }
.klassen, .konkordanz { font-size: 14px; color: #555; margin-top: 0.5em; }
.konkordanz { font-family: ui-monospace, Menlo, monospace; font-size: 13px; }
.hinweis   { font-size: 14px; color: #1c5d3a; background: #eef6f1;
             padding: 7px 11px; border-radius: 6px; margin: 0.7em auto 0;
             max-width: 34em; text-align: left; }
.quelle    { font-size: 12px; color: #999; margin-top: 1em; }
hr#answer  { border: none; border-top: 1px solid #ddd; margin: 1em 0; }

.nightMode .card { color: #e8e8e6; background: #1f2023; }
.nightMode .glossbox { background: #2b2d31; }
.nightMode table.gloss tr.la td { color: #e0b05c; }
.nightMode .klassen, .nightMode .konkordanz { color: #a8a8a4; }
.nightMode .hinweis { color: #a8dcc0; background: #1d2f26; }
.nightMode .quelle { color: #76766f; }
.nightMode hr#answer { border-top-color: #3a3b3f; }
```

### Drilldeck

`anki_drill.tsv` ist richtungslos (Swahili-intern) und braucht den Notiztyp
nicht. Importiere es als **Grundlegend** in ein eigenes Deck: Spalte 1 =
Vorderseite, Spalte 2 = Rückseite, Spalte 3 = Tags, „HTML erlauben" an.

## Weg 2 — flache Decks

Vier Dateien, je drei Spalten: Vorderseite, Rückseite, Tags. Notiztyp
**Grundlegend**, „HTML in Feldern erlauben" **an**. Glossen, Klassen,
Konkordanz und Hinweis sind in die Rückseite eingebaut.

| Datei | Richtung |
|---|---|
| `anki_sw_de.tsv` | Swahili → Deutsch |
| `anki_sw_en.tsv` | Swahili → Englisch |
| `anki_de_sw.tsv` | Deutsch → Swahili |
| `anki_en_sw.tsv` | Englisch → Swahili |
| `anki_drill.tsv` | Klassen- und Konkordanzdrill |

Nachteil: vier Kopien desselben Satzes. Eine Korrektur musst du vierfach
machen — oder `build_anki.py` neu laufen lassen und neu importieren.

## Tags

Jede Karte trägt `A1 SD1` plus:

- den Abschnittsbuchstaben der Wortliste (`A` … `Z`)
- das deutsche Stichwort, leerzeichenfrei
- bei Kontrastkarten: `kontrast` plus Typ (`numerus`, `tam`, `kaskade`,
  `negation`, `demonstrativ`, `possessiv`)
- bei Drillkarten: `drill` plus Typ (`klasse`, `plural`, `konkordanz`,
  `adjektiv`, `luecke`)
- Klassenangaben (`kl7`, `kl8` …) und TAM-Marker (`tam-na`, `tam-me` …)

Damit lässt sich gezielt üben, zum Beispiel `tag:kl9 tag:kontrast` für alle
Minimalpaare der Klasse 9, oder `tag:tam-me` für alles zum Perfekt.

## Umfang

| Deck | Notizen | Karten |
|---|---:|---:|
| Hauptkarten (Goethe-Sätze) | 850 | 3.400 |
| Kontrastdeck (Minimalpaare) | 128 | 512 |
| Drilldeck | 543 | 543 |
| **Summe** | **1.521** | **4.455** |

Bei 20 neuen Karten am Tag sind das gut sieben Monate Einführung. Fang mit
dem Drilldeck und den Kontrastkarten an — ohne die Klassenlogik bleiben die
850 Satzkarten Einzelfälle.
