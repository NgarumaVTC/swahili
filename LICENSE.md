# Lizenz

Dieses Repository enthält zweierlei: eigenes Werk und fremdes Material. Das
muss getrennt bleiben, denn lizenzieren kann man nur, was man besitzt.

## Was unter dieser Lizenz steht

Alles in diesem Repository **mit Ausnahme der unten genannten Dateien**:

> **Creative Commons Namensnennung – Nicht kommerziell –
> Weitergabe unter gleichen Bedingungen 4.0 International**
> (CC BY-NC-SA 4.0)

- **Namensnennung** — nenne den Urheber
- **Nicht kommerziell** — keine kommerzielle Nutzung
- **Weitergabe unter gleichen Bedingungen** — Ableitungen unter derselben Lizenz

Lizenztext: <https://creativecommons.org/licenses/by-nc-sa/4.0/deed.de>
Rechtsverbindliche Fassung: <https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.de>

SPDX-Kennung: `CC-BY-NC-SA-4.0`

Darunter fallen insbesondere: die Swahili-Sätze, die Morphemanalysen und
Glossen, das Nominalklassenlexikon, die Konkordanz- und Adjektivtabellen, das
Kontrastdeck, das Drilldeck, die Korrekturbögen und sämtlicher Code.

## Was NICHT unter dieser Lizenz steht

Die folgenden Dateien enthalten Material des **Goethe-Instituts e. V.** und
der **telc GmbH** — die 850 deutschen Beispielsätze und die Wortgruppenliste
aus der Wortliste zum *Goethe-Zertifikat A1 / Start Deutsch 1*, wörtlich
übernommen:

<!-- AUSNAHMEN -->
- `Goethe-Institut/A1_SD1_Wortliste_02.pdf`
- `Goethe-Institut/wortliste_de.tsv`
- `Goethe-Institut/wortgruppen_de.tsv`
- `Goethe-Institut/karten_haupt.tsv`
- `Goethe-Institut/anki_master.tsv`
- `Goethe-Institut/anki_de_sw.tsv`
- `Goethe-Institut/anki_sw_de.tsv`
- `Goethe-Institut/druck_satzkarten.pdf`
<!-- /AUSNAHMEN -->

Für diese Dateien gilt: **alle Rechte beim Rechteinhaber.** Es wird keine
Lizenz erteilt, weil keine erteilt werden kann. Eine Erlaubnis zur Aufnahme
in dieses Repository wurde nicht eingeholt; Einzelheiten in
[`HERKUNFT.md`](HERKUNFT.md).

**Wer von diesem Repository ableitet, muss diese Ausnahme mitübernehmen.**
Die Share-Alike-Klausel verlangt das für den eigenen Teil; für den fremden
Teil verlangt es das Urheberrecht.

Dass die Liste `CC BY-NC-SA` trägt, heißt also **nicht**, dass die deutschen
Sätze frei verwendbar wären. Sie sind es nicht.

## Prüfung

Die Ausnahmeliste ist nicht handgepflegt, sondern maschinell nachgehalten:

```sh
python3 pruefe_lizenz.py
```

Das Skript nimmt die deutschen Sätze als Referenz, durchsucht jede Datei im
Repository und meldet jede Abweichung in beide Richtungen — eine
undeklarierte Datei mit Goethe-Text ebenso wie eine deklarierte ohne.

## Urheber des eigenen Teils

Axel Ramge für das Ngaruma Vocational Training Centre, 2026.
