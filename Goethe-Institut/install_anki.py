#!/usr/bin/env python3
"""Baut das Deutsch-Swahili-Paket per AnkiConnect direkt in die laufende Anki-Sammlung.

Ersetzt die Klickstrecke aus ANKI_SETUP.md, Weg 1. Der Handimport ist die Stelle,
an der es schiefgeht: wer `anki_master.tsv` versehentlich auf einen Zwei-Feld-Notiztyp
legt, bekommt 1.521 Karten, bei denen ab Spalte 3 alles wortweise in den Tags landet
(und die Kopfzeile als Lernkarte).

Voraussetzung: Anki laeuft mit dem Add-on AnkiConnect (127.0.0.1:8765). Das Add-on
ist ein In-Process-Server — ohne offenes Anki antwortet nichts.

    python3 install_anki.py --dry-run     # nur zeigen, was passieren wuerde
    python3 install_anki.py               # anlegen, vorhandene Sammlung bleibt
    python3 install_anki.py --reset       # ALLE Notizen der Sammlung vorher loeschen
    python3 install_anki.py --export DATEI.apkg   # Deck als Paket herausschreiben

Nur Standardbibliothek, wie der Rest der Pipeline.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "http://127.0.0.1:8765"

# Spalten von anki_master.tsv. Die letzte Spalte sind Tags, kein Feld —
# darum steht sie nicht im Notiztyp. ANKI_SETUP.md nennt noch die alten elf
# Felder ohne die *EN-Varianten; maßgeblich ist die Kopfzeile der TSV.
MASTER_COLUMNS = [
    "Stichwort", "Deutsch", "Englisch", "Swahili", "Morpheme",
    "Labels", "LabelsEN", "Gloss", "GlossEN", "Klassen", "KlassenEN",
    "Konkordanz", "KonkordanzEN", "Hinweis", "HinweisEN", "Quelle", "Tags",
]
MASTER_FIELDS = [c for c in MASTER_COLUMNS if c != "Tags"]

MODEL_HAUPT = "Swahili A1 SD1"
MODEL_DRILL = "Swahili A1 SD1 Drill"

DECK_ROOT = "Kiswahili::A1 SD1"
DECK_HAUPT = DECK_ROOT + "::Hauptkarten"
DECK_KONTRAST = DECK_ROOT + "::Kontrast"
DECK_DRILL = DECK_ROOT + "::Drill"

# Rueckseite ist in beiden Richtungen gleich aufgebaut, nur das Zielfeld wechselt.
def _back(ziel, quelle_zeile):
    return (
        "{{FrontSide}}<hr id=answer>\n"
        "<div class=ziel>{{%s}}</div>\n"
        "{{#Gloss}}<div class=glossbox>{{Gloss}}</div>{{/Gloss}}\n"
        "{{#Klassen}}<div class=klassen>{{Klassen}}</div>{{/Klassen}}\n"
        "{{#Konkordanz}}<div class=konkordanz>{{Konkordanz}}</div>{{/Konkordanz}}\n"
        "{{#Hinweis}}<div class=hinweis>{{Hinweis}}</div>{{/Hinweis}}\n"
        "<div class=quelle>%s</div>" % (ziel, quelle_zeile)
    )

# Nur die beiden deutschen Richtungen. Die englischen Felder stecken trotzdem im
# Notiztyp: SW → EN und EN → SW sind spaeter zwei zusaetzliche Kartenvorlagen,
# ohne Neuimport. Das Stichwort steht nur bei DE → SW vorne — in der Richtung
# SW → DE waere es ein Spoiler.
TEMPLATES_HAUPT = [
    {
        "Name": "SW → DE",
        "Front": "<div class=prompt>{{Swahili}}</div>",
        "Back": _back("Deutsch", "{{Stichwort}} · {{Quelle}}"),
    },
    {
        "Name": "DE → SW",
        "Front": "<div class=prompt>{{Deutsch}}</div>\n"
                 "<div class=stichwort>{{Stichwort}}</div>",
        "Back": _back("Swahili", "{{Quelle}}"),
    },
]

TEMPLATES_DRILL = [
    {
        "Name": "Drill",
        "Front": "<div class=prompt>{{Vorderseite}}</div>",
        "Back": "{{FrontSide}}<hr id=answer>\n"
                "<div class=ziel>{{Rückseite}}</div>",
    },
]

# Wortwoertlich aus ANKI_SETUP.md, plus die letzten zwei Regeln: die Drill-Rueckseite
# bringt ihre Erklaerung als verschachteltes .konkordanz mit, das soll die
# Auszeichnung von .ziel nicht erben.
CSS = """.card { font-family: -apple-system, Segoe UI, system-ui, sans-serif;
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
.ziel .konkordanz { font-weight: 400; margin-top: 0.6em; }

.nightMode .card { color: #e8e8e6; background: #1f2023; }
.nightMode .glossbox { background: #2b2d31; }
.nightMode table.gloss tr.la td { color: #e0b05c; }
.nightMode .klassen, .nightMode .konkordanz { color: #a8a8a4; }
.nightMode .hinweis { color: #a8dcc0; background: #1d2f26; }
.nightMode .quelle { color: #76766f; }
.nightMode hr#answer { border-top-color: #3a3b3f; }
"""


def ac(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(
        ENDPOINT, payload, {"Content-Type": "application/json"})
    try:
        answer = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.URLError as exc:
        sys.exit("AnkiConnect nicht erreichbar (%s auf %s).\n"
                 "Laeuft Anki? Das Add-on lebt im Anki-Prozess, nicht als Daemon."
                 % (exc, ENDPOINT))
    if answer.get("error"):
        sys.exit("AnkiConnect-Fehler bei %s: %s" % (action, answer["error"]))
    return answer["result"]


def read_tsv(path, expected_columns, has_header):
    """TSV zeilenweise, bewusst ohne csv-Modul: die Felder enthalten HTML mit
    Anfuehrungszeichen, die ein Quoting-Dialekt zerlegen wuerde."""
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    rows = []
    for number, line in enumerate(lines, 1):
        if has_header and number == 1:
            continue
        cells = line.split("\t")
        if len(cells) != expected_columns:
            sys.exit("%s Zeile %d: %d Spalten statt %d"
                     % (os.path.basename(path), number, len(cells), expected_columns))
        rows.append(cells)
    return rows


def build_notes(basedir):
    """Liefert (deckname, modelname, fields, tags) je Notiz."""
    notes = []

    master = read_tsv(os.path.join(basedir, "anki_master.tsv"),
                      len(MASTER_COLUMNS), has_header=True)
    for cells in master:
        row = dict(zip(MASTER_COLUMNS, cells))
        quelle = row["Quelle"]
        # Die Drillkarten stehen zwar auch in anki_master.tsv, dort aber mit leeren
        # Gloss-/Morphem-Feldern: es sind richtungslose Swahili-interne Fragen, fuer
        # die eine Richtung SW → DE keinen Sinn ergibt. Sie kommen unten aus
        # anki_drill.tsv, wo sie als Vorderseite/Rueckseite fertig aufbereitet sind.
        if quelle == "Drilldeck":
            continue
        deck = DECK_KONTRAST if quelle == "Kontrastdeck" else DECK_HAUPT
        fields = {name: row[name] for name in MASTER_FIELDS}
        notes.append((deck, MODEL_HAUPT, fields, row["Tags"].split()))

    drill = read_tsv(os.path.join(basedir, "anki_drill.tsv"), 3, has_header=False)
    for vorne, hinten, tags in drill:
        notes.append((DECK_DRILL, MODEL_DRILL,
                      {"Vorderseite": vorne, "Rückseite": hinten}, tags.split()))

    return notes


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true",
                        help="ALLE Notizen der Sammlung vorher loeschen (Neustart)")
    parser.add_argument("--dry-run", action="store_true",
                        help="nur berichten, nichts aendern")
    parser.add_argument("--export", metavar="DATEI.apkg",
                        help="Deck %r als Anki-Paket schreiben und beenden; "
                             "ohne Lernverlauf, zum Weitergeben" % DECK_ROOT)
    args = parser.parse_args()

    if args.export:
        # Ein Paket, das die Empfaengerin per Doppelklick importiert: Notiztypen,
        # Kartenvorlagen, CSS, Unterdecks und Tags sind darin enthalten. Kein
        # AnkiConnect, keine Feldzuordnung, keine Anleitung noetig.
        # includeSched=False: der Lernverlauf ist meiner, sie faengt bei null an.
        ziel = os.path.abspath(args.export)
        if not ac("findNotes", query='deck:"%s"' % DECK_ROOT):
            sys.exit("Deck %r ist leer — erst installieren, dann exportieren."
                     % DECK_ROOT)
        ac("exportPackage", deck=DECK_ROOT, path=ziel, includeSched=False)
        print("Exportiert: %s (%.1f MB)" % (ziel, os.path.getsize(ziel) / 1e6))
        return

    basedir = os.path.dirname(os.path.abspath(__file__))
    notes = build_notes(basedir)

    from collections import Counter
    verteilung = Counter(deck for deck, _, _, _ in notes)
    print("Aus den TSV gelesen:")
    for deck in (DECK_HAUPT, DECK_KONTRAST, DECK_DRILL):
        print("  %-32s %5d Notizen" % (deck, verteilung[deck]))
    print("  %-32s %5d" % ("Summe", len(notes)))

    vorhanden = ac("findNotes", query="deck:*")
    print("\nIn Anki derzeit: %d Notizen, Decks %s" % (len(vorhanden), ac("deckNames")))

    if args.dry_run:
        print("\n--dry-run: nichts geaendert.")
        return

    if args.reset and vorhanden:
        print("\n--reset: loesche %d vorhandene Notizen." % len(vorhanden))
        ac("deleteNotes", notes=vorhanden)
        # Das Tag-Register ueberlebt das Loeschen von Notizen, und Anki vereinheitlicht
        # Tags case-insensitiv: die zuerst registrierte Schreibung gewinnt. Ohne diesen
        # Schritt erben die neuen Karten die Schreibweise der Altlast — aus Abschnitt
        # "A" wird "a", aus Stichwort "Kind" wird "kind".
        vorher = len(ac("getTags"))
        ac("clearUnusedTags")
        print("  Tag-Register aufgeraeumt: %d -> %d Eintraege"
              % (vorher, len(ac("getTags"))))

    print("\nNotiztypen:")
    bestehende = ac("modelNames")
    for name, fields, templates in ((MODEL_HAUPT, MASTER_FIELDS, TEMPLATES_HAUPT),
                                    (MODEL_DRILL, ["Vorderseite", "Rückseite"],
                                     TEMPLATES_DRILL)):
        if name in bestehende:
            print("  %r existiert schon — Felder/Vorlagen bleiben unveraendert." % name)
            continue
        ac("createModel", modelName=name, inOrderFields=fields, css=CSS,
           isCloze=False, cardTemplates=templates)
        print("  %r angelegt (%d Felder, %d Vorlagen)."
              % (name, len(fields), len(templates)))

    print("\nDecks:")
    for deck in (DECK_HAUPT, DECK_KONTRAST, DECK_DRILL):
        ac("createDeck", deck=deck)
        print("  %s" % deck)

    # allowDuplicate ist noetig: das erste Feld ist Stichwort, und 124 Stichworte
    # kommen mehrfach vor (ein Wort mit mehreren Beispielsaetzen). Ohne das Flag
    # verwirft Anki die Wiederholungen als Duplikate.
    print("\nNotizen anlegen:")
    payload = [{"deckName": deck, "modelName": model, "fields": fields,
                "tags": tags, "options": {"allowDuplicate": True}}
               for deck, model, fields, tags in notes]

    angelegt = 0
    for start in range(0, len(payload), 200):
        haufen = payload[start:start + 200]
        ergebnis = ac("addNotes", notes=haufen)
        gut = [x for x in ergebnis if x is not None]
        angelegt += len(gut)
        if len(gut) != len(haufen):
            print("  WARNUNG: %d von %d in Haufen ab %d abgelehnt"
                  % (len(haufen) - len(gut), len(haufen), start))
        print("  %d/%d" % (angelegt, len(payload)), end="\r", flush=True)
    print("  %d von %d Notizen angelegt." % (angelegt, len(payload)))

    print("\nKontrolle:")
    for deck in (DECK_HAUPT, DECK_KONTRAST, DECK_DRILL):
        n = len(ac("findNotes", query='deck:"%s"' % deck))
        k = len(ac("findCards", query='deck:"%s"' % deck))
        print("  %-32s %5d Notizen  %5d Karten" % (deck, n, k))


if __name__ == "__main__":
    main()
