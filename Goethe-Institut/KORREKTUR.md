# Korrekturen einarbeiten

Sekela liest die Bögen `korrektur_kurz.pdf` oder `korrektur_lang.pdf` gegen.
Diese Datei beschreibt, wie ihre Anmerkungen zurück in den Kartensatz kommen.

## Die Reihenfolge ist nicht beliebig

Korrekturen am **Lexikon** wirken auf alle drei Decks, weil Klassen und
Plurale nur dort entstehen. Korrekturen an einem **Einzelsatz** wirken nur auf
diese eine Karte. Darum zuerst Teil A, dann Teil B, dann Teil C.

## Teil A — Nominalklassen

Trage die Korrektur in `klassen_lexikon.tsv` ein. Spalten:

| Spalte | Bedeutung |
|---|---|
| `sw_singular` · `sw_plural` | die Swahili-Formen |
| `klasse_sg` · `klasse_pl` | Klassennummern, siehe `GLOSSING.md` |
| `kongruenz` | nur gefüllt, wenn Form- und Kongruenzklasse auseinanderfallen (`1/2`) |
| `en_nomen` | englische Bedeutung, erscheint auf ihrem Bogen |
| `notiz` · `notiz_en` | Anmerkung, deutsch und englisch |

Sagt sie etwa, *bosi* sei Kl. 9/10 und nicht 5/6, änderst du `klasse_sg` auf
`9`, `klasse_pl` auf `10` und `sw_plural` auf `bosi`. Dann:

```sh
python3 build_karten.py && python3 generate_kontrast.py && python3 generate_drill.py
python3 check_karten.py karten_haupt.tsv karten_kontrast.tsv
```

Die Klassen- und Konkordanzzeilen aller betroffenen Karten ziehen automatisch
nach, ebenso Kontrast- und Drilldeck.

## Teil B — Konkordanztabelle

Beanstandet sie eine Zelle der Tabelle Kl. 1–18, ändere sie in
`konkordanz.py` in `TABELLE`. Das ist der folgenreichste Eingriff überhaupt:
die Tabelle steuert Kontrastdeck, Drilldeck und jede Konkordanzzeile.

Adjektivformen stehen separat in `adjektive.py`, weil Kl. 9/10 unregelmäßig
ist (*nzuri*, aber *kubwa* und *mpya*).

## Teil C — Einzelsätze

Die Swahili-Sätze liegen in `batch_haupt_09.tsv` bis `batch_haupt_26.tsv`,
eine Datei pro Seite der Wortliste, Zeilen über die `id` adressiert. Die `id`
steht nicht auf ihrem Bogen — finde die Zeile über den Swahili-Satz:

```sh
grep -n "Tunaondoka saa sita" batch_haupt_*.tsv
```

Ändere `satz_sw`, und wenn sich die Morphologie mitändert auch
`gloss_morpheme` und `gloss_labels`. Dann `build_karten.py` und
`check_karten.py` — der Validator fängt Segmentzahlen, die nicht mehr
zusammenpassen.

## Danach

```sh
python3 build_anki.py              # Anki-Decks neu
python3 make_druckkarten.py haupt kontrast
python3 make_korrekturbogen.py     # Bögen neu, falls eine zweite Runde folgt
python3 pruefe_lizenz.py           # Ausnahmeliste prüfen
```

## Was sie nicht prüfen kann

Die deutschen Sätze und die deutschen Glossen-Labels stehen nicht auf ihrem
Bogen — sie liest kein Deutsch. Fehler auf der deutschen Seite musst du selbst
finden. Die deutschen Sätze sind allerdings wörtlich aus der Goethe-Liste
übernommen und damit so korrekt wie die Vorlage.
