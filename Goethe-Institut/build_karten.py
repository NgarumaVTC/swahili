#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Uebersetzungsbatches + wortliste_de.tsv + Lexikon -> karten_haupt.tsv

Die Felder `klassen` und `konkordanz` werden nicht von Hand geschrieben,
sondern aus klassen_lexikon.tsv abgeleitet: welche Substantive im
Swahili-Satz vorkommen, bestimmt die angezeigte Klassen- und
Konkordanzinformation. So koennen sie ueber 850 Karten nicht driften, und
eine Korrektur im Lexikon wirkt sofort auf alle Karten.

Batchformat (TSV, Spalten):
  id  satz_sw  gloss_morpheme  gloss_labels  satz_en  hinweis

`hinweis` ist optional und nimmt auf, was die Ableitung nicht leisten kann:
Uhrzeit ab Sonnenaufgang, Reflexiv -ji-, Applikativ, Wortwahl-Fallen.
"""
import csv, glob, re, sys
import glossen_en as GE
import konkordanz as K

FELDER = ['id', 'seite', 'buchstabe', 'stichwort', 'untereintrag',
          'satz_de', 'satz_en', 'satz_sw', 'gloss_morpheme', 'gloss_labels',
          'gloss_labels_en', 'klassen', 'klassen_en', 'konkordanz',
          'konkordanz_en', 'hinweis', 'tags']


def lade_tsv(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))


def lexikon():
    """-> {swahili_wortform: lexikoneintrag}, Singular und Plural."""
    idx = {}
    for r in lade_tsv('klassen_lexikon.tsv'):
        for form, kl in ((r['sw_singular'], r['klasse_sg']),
                         (r['sw_plural'], r['klasse_pl'])):
            if not form or form == '—':
                continue
            # Mehrwortfuegungen ueber ihr Kopfnomen auffindbar machen, aber
            # einwortige Eintraege gewinnen: "simu" soll das Telefon treffen,
            # nicht "simu ya mkononi".
            kopf = form.split()[0]
            # Rangfolge: einwortiger Singulartreffer > einwortiger Pluraltreffer
            # > Kopfnomen einer Mehrwortfuegung. "maziwa" ist Milch (Kl. 6) und
            # Plural von ziwa (See) -- der Singulareintrag gewinnt.
            ist_sg = form == r['sw_singular']
            rang = (0 if len(form.split()) == 1 else 2) + (0 if ist_sg else 1)
            alt = idx.get(kopf)
            if alt is None or rang < alt[2]:
                idx[kopf] = (r, kl, rang)
    return idx


# Negative Subjektpraefixe sind laut GLOSSING.md ein Segment, auch wenn sie
# aus ha- plus Subjektpraefix verschmolzen sind.
NEG_PRAEFIX = re.compile(
    r'\bha-(i|u|li|ya|ki|vi|zi|tu|wa|m|ku|pa|mu)-')


def normalisiere_gloss(mo):
    """ha-wa-na -> hawa-na. Reine Schreibkonvention, keine Analyseaenderung."""
    return NEG_PRAEFIX.sub(lambda m: f'ha{m.group(1)}-', mo)


def tag(s):
    """Stichwort -> leerzeichenfreier Anki-Tag."""
    s = re.sub(r'^(der/die|der|die|das)\s+', '', s.strip())
    s = re.sub(r'\(sich\)\s*', '', s)
    s = re.sub(r'[,–\-]+.*$', '', s).strip()
    return re.sub(r'[^0-9A-Za-zÄÖÜäöüß/]', '_', s) or 'x'


KL_IM_LABEL = re.compile(r'KL(\d+)')


def ableiten(satz_sw, lex, labels=''):
    """-> (klassen_text, konkordanz_text) aus den Substantiven im Satz.

    Saetze ohne Lexikonnomen (reine Verbsaetze) blieben sonst ohne
    Grammatikfelder. Fuer sie werden die Klassen aus der Labelzeile gelesen,
    damit jede Karte eine Konkordanzreihe zeigt.
    """
    gefunden, klassen = [], []
    for wort in re.findall(r"[A-Za-zÄÖÜäöüß’']+", satz_sw):
        hit = lex.get(wort) or lex.get(wort.lower())
        if not hit:
            continue
        r, _kl = hit[0], hit[1]
        if r['de_nomen'] in [g['de_nomen'] for g in gefunden]:
            continue
        gefunden.append(r)
        kl = r['kongruenz'].split('/')[0] if r['kongruenz'] else r['klasse_sg']
        if kl and kl not in klassen:
            klassen.append(kl)
    kl_txt = ' · '.join(
        K.klassen_text(r['klasse_sg'], r['klasse_pl'],
                       r['sw_singular'], r['sw_plural'])
        + (f"  [{r['notiz']}]" if r['notiz'] else '')
        for r in gefunden if r['klasse_sg'])
    kl_en = ' · '.join(
        K.klassen_text_en(r['klasse_sg'], r['klasse_pl'],
                          r['sw_singular'], r['sw_plural'])
        + (f"  [{r['notiz_en']}]" if r.get('notiz_en') else '')
        for r in gefunden if r['klasse_sg'])
    if not klassen and labels:
        klassen = []
        for k in KL_IM_LABEL.findall(labels):
            if k in K.TABELLE and k not in klassen:
                klassen.append(k)
    ko_txt = ' · '.join(K.konkordanz_text(k) for k in klassen[:2])
    ko_en = ' · '.join(K.konkordanz_text_en(k) for k in klassen[:2])
    return kl_txt, kl_en, ko_txt, ko_en


def main(batchmuster='batch_haupt_*.tsv'):
    basis = {r['id']: r for r in lade_tsv('wortliste_de.tsv')}
    lex = lexikon()
    glossar, fehlend = GE.lade_glossar(), set()

    uebers = {}
    dateien = sorted(glob.glob(batchmuster))
    for p in dateien:
        for r in lade_tsv(p):
            if r['id'] in uebers:
                print(f'WARNUNG: id {r["id"]} doppelt ({p})')
            uebers[r['id']] = r
    if not dateien:
        sys.exit(f'keine Batchdateien gefunden ({batchmuster})')

    unbekannt = sorted(set(uebers) - set(basis), key=lambda x: int(x))
    if unbekannt:
        sys.exit(f'ids ohne Basiszeile: {unbekannt[:10]}')

    normalisiert = []
    with open('karten_haupt.tsv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, FELDER, delimiter='\t', lineterminator='\n',
                           extrasaction='ignore')
        w.writeheader()
        for kid in sorted(basis, key=lambda x: int(x)):
            u = uebers.get(kid)
            if not u:
                continue
            b = basis[kid]
            vorher = u['gloss_morpheme']
            u['gloss_morpheme'] = normalisiere_gloss(vorher)
            if u['gloss_morpheme'] != vorher:
                normalisiert.append(kid)
            kl, kl_en, ko, ko_en = ableiten(
                u['satz_sw'], lex, u['gloss_labels'])
            u['gloss_labels_en'] = GE.uebersetze_zeile(
                u['gloss_labels'], glossar, fehlend)
            w.writerow({**b, **u, 'klassen': kl, 'klassen_en': kl_en,
                        'konkordanz': ko, 'konkordanz_en': ko_en,
                        'tags': f"A1 SD1 {b['buchstabe']} {tag(b['stichwort'])}"})

    if fehlend:
        print(f'WARNUNG: {len(fehlend)} Label-Tokens ohne englische Glosse: '
              f'{", ".join(sorted(fehlend)[:10])}')
    if normalisiert:
        print(f'Negativpraefix normalisiert in {len(normalisiert)} Karten: '
              f'{", ".join(normalisiert[:8])}')
    fertig, gesamt = len(uebers), len(basis)
    print(f'karten_haupt.tsv: {fertig}/{gesamt} Karten '
          f'({100 * fertig // gesamt}%) aus {len(dateien)} Batches')
    offen = [k for k in sorted(basis, key=lambda x: int(x)) if k not in uebers]
    if offen:
        seiten = sorted({basis[k]['seite'] for k in offen}, key=int)
        print(f'offen: {len(offen)} Karten auf Seite(n) {", ".join(seiten)}')


if __name__ == '__main__':
    main(*sys.argv[1:])
