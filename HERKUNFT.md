# Herkunft der Vorlage

## Was übernommen wurde

Die **850 deutschen Beispielsätze** und die **Wortgruppenliste** in diesem
Repository sind **wörtlich** entnommen aus:

> *Goethe-Zertifikat A1 · Start Deutsch 1 · Wortliste*
> Herausgegeben vom Goethe-Institut und von Weiterbildungs-Testsysteme GmbH,
> heute telc GmbH. Auszug aus *Start Deutsch · Deutschprüfungen für Erwachsene
> · Prüfungsziele, Testbeschreibung*, erstmals erschienen 2004.
>
> Quelle: <https://www.goethe.de/pro/relaunch/prf/uk/A1_SD1_Wortliste_02.pdf>

Das PDF selbst liegt in diesem Repository mit, unter
`Goethe-Institut/A1_SD1_Wortliste_02.pdf`.

## Eine Erlaubnis wurde nicht eingeholt

Weder für die Übernahme der Sätze noch für die Aufnahme des PDF in ein
öffentliches Repository liegt eine Genehmigung des Rechteinhabers vor.

Eine Anfrage ist formuliert — siehe [`goethe-anfrage.md`](goethe-anfrage.md).
Eine Antwort liegt zum Zeitpunkt dieser Veröffentlichung nicht vor.

## Wozu

Ausschließlich zum eigenen Sprachenlernen. Die A1-Wortliste dient als
**Frequenzgerüst**: sie stellt sicher, dass der Kartensatz den
Alltagswortschatz abdeckt, statt dass Vokabeln willkürlich ausgewählt werden.
Gelernt wird mit diesen Karten **Swahili**, nicht Deutsch.

Nichts daran wird verkauft. Es gibt keine kommerzielle Nutzung, und die
Lizenz des eigenen Teils schließt sie ausdrücklich aus
([`LICENSE.md`](LICENSE.md)).

## Was eigenes Werk ist

Vom Goethe-Institut stammt die deutsche Wortliste. Alles Übrige entstand hier:

- die Swahili-Übersetzungen aller 850 Sätze
- die Morphem-für-Morphem-Glossierung, deutsch und englisch
- das Nominalklassenlexikon mit 330 Substantiven
- die Konkordanztabelle der Klassen 1–18 und die Adjektivtabellen
- 128 Minimalpaare und 543 Drillkarten, beide vollständig selbst konstruiert
- der gesamte Code, von der PDF-Extraktion bis zum Anki-Export

Der Umfang des eigenen Teils übersteigt den der Vorlage um ein Mehrfaches.

## Angebot an den Rechteinhaber

Auf Hinweis des Goethe-Instituts oder der telc GmbH wird umgehend und ohne
Diskussion umgesetzt, was gewünscht ist:

- Entfernen des PDF aus dem Repository, oder
- Entfernen der deutschen Beispielsätze, oder
- Umstellen des Repositorys auf privat, oder
- vollständige Löschung.

Kontakt: axel@ramge.de

Die Pipeline ist so gebaut, dass das möglich bleibt: `extract_wortliste.py`
erzeugt die deutschen Sätze aus dem PDF. Wer das PDF selbst herunterlädt, kann
den gesamten Kartensatz reproduzieren, ohne dass hier fremdes Material liegen
muss.
