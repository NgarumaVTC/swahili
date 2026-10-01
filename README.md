# Swahili

Lernmaterial für Swahili, entstanden am Ngaruma Vocational Training Centre.

## [`Goethe-Institut/`](Goethe-Institut/) — Kartensatz auf Basis der A1-Wortliste

4.455 Anki-Karten und 1.521 Druckkarten für Swahili in vier Richtungen
(Swahili ↔ Deutsch, Swahili ↔ Englisch), jede mit Morphem-für-Morphem-Analyse,
Nominalklasse und Konkordanzreihe auf der Rückseite. Dazu 128 Minimalpaare, die
Nominalklassen und TAM-Marker gegenüberstellen, und 543 Grammatikkarten.

Einstieg: [`Goethe-Institut/README.md`](Goethe-Institut/README.md) ·
Anki einrichten: [`ANKI_SETUP.md`](Goethe-Institut/ANKI_SETUP.md) ·
Drucken: [`DRUCKEN.md`](Goethe-Institut/DRUCKEN.md)

## Herkunft der deutschen Sätze

Die 850 deutschen Beispielsätze sind **wörtlich** der Wortliste zum
*Goethe-Zertifikat A1 / Start Deutsch 1* entnommen, © Goethe-Institut e. V.
und telc GmbH. Das PDF liegt hier mit. **Eine Erlaubnis dafür wurde nicht
eingeholt.**

Einzelheiten, Quelle und das Angebot an den Rechteinhaber:
[`HERKUNFT.md`](HERKUNFT.md). Eine Anfrage ist formuliert:
[`goethe-anfrage.md`](goethe-anfrage.md).

## Lizenz

Eigenes Werk unter **CC BY-NC-SA 4.0**. Die acht Dateien mit Goethe-Material
sind ausdrücklich ausgenommen — lizenzieren kann man nur, was man besitzt.
Welche das sind und warum: [`LICENSE.md`](LICENSE.md).

Die Ausnahmeliste wird maschinell nachgehalten:

```sh
python3 pruefe_lizenz.py
```

## Voraussetzungen

Python-Standardbibliothek für die Pipeline, `xelatex` für die PDFs. Kein
`poppler`, kein `pypdf`, kein `genanki`, keine Pakete zu installieren.
