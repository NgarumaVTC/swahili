# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Textextraktion aus A1_SD1_Wortliste_02.pdf — nur Standardbibliothek.

Der PDF-Text liegt in drei Fonts:
  /TT0, /TT1  einfache TrueType-Fonts mit WinAnsiEncoding (1 Byte/Glyph)
  /C2_0       Type0 Identity-H (2 Byte/CID), Unicode nur über ToUnicode-CMap

Ohne die CMap fehlen ganze Einträge (z. B. "abfahren"), darum wird sie
hier ausgewertet statt die Hex-Strings zu überspringen.
"""
import re, zlib

NUM = rb'[-+]?[\d\.]+'


def load(path):
    data = open(path, 'rb').read()
    objs = {}
    for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj(.*?)endobj', data, re.S):
        objs[int(m.group(1))] = m.group(3)
    objs.update(_objektstroeme(objs))
    return data, objs


def _objektstroeme(objs):
    """Objekte aus /ObjStm-Containern holen.

    xelatex legt fast alle Objekte in komprimierten Objektstroemen ab. Ohne
    sie zu oeffnen findet man in einem xelatex-PDF keine einzige Seite.
    """
    aus = {}
    for raw in list(objs.values()):
        if b'/ObjStm' not in raw:
            continue
        inhalt = stream_of(raw)
        if not inhalt:
            continue
        n = re.search(rb'/N\s+(\d+)', raw)
        first = re.search(rb'/First\s+(\d+)', raw)
        if not (n and first):
            continue
        n, first = int(n.group(1)), int(first.group(1))
        kopf = inhalt[:first].split()
        paare = [(int(kopf[i]), int(kopf[i + 1]))
                 for i in range(0, min(len(kopf), 2 * n), 2)]
        for i, (num, off) in enumerate(paare):
            ende = first + (paare[i + 1][1] if i + 1 < len(paare)
                            else len(inhalt) - first)
            aus[num] = inhalt[first + off:ende]
    return aus


def stream_of(raw):
    m = re.search(rb'stream\r?\n(.*?)endstream', raw, re.S)
    if not m:
        return None
    s = m.group(1)
    try:
        return zlib.decompress(s)
    except Exception:
        return s


def parse_cmap(raw):
    """ToUnicode-CMap -> {cid: unicode-string}."""
    cm = stream_of(raw).decode('latin-1')
    out = {}
    for blk in re.findall(r'beginbfchar(.*?)endbfchar', cm, re.S):
        for src, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            out[int(src, 16)] = ''.join(
                chr(int(dst[i:i + 4], 16)) for i in range(0, len(dst), 4))
    for blk in re.findall(r'beginbfrange(.*?)endbfrange', cm, re.S):
        for lo, hi, dst in re.findall(
                r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            base = int(dst, 16)
            for i, c in enumerate(range(int(lo, 16), int(hi, 16) + 1)):
                out[c] = chr(base + i)
    # Die CMap bildet den Space-Glyph auf U+0009 ab. Als echtes Tab wuerde er
    # spaeter die TSV-Spalten zerreissen.
    for k, v in list(out.items()):
        if v == '\t':
            out[k] = ' '
    return out


_ESC = {ord('n'): b'\n', ord('r'): b'\r', ord('t'): b'\t', ord('b'): b'\b',
        ord('f'): b'\f', ord('('): b'(', ord(')'): b')', ord('\\'): b'\\'}


def unescape(b):
    """PDF-Literalstring (ohne Klammern) -> rohe Bytes."""
    out = bytearray()
    i = 0
    while i < len(b):
        c = b[i]
        if c != 0x5C:                      # kein Backslash
            out.append(c); i += 1; continue
        i += 1
        if i >= len(b):
            break
        c = b[i]
        if 0x30 <= c <= 0x37:              # oktal, 1-3 Ziffern
            dig = ''
            while i < len(b) and len(dig) < 3 and 0x30 <= b[i] <= 0x37:
                dig += chr(b[i]); i += 1
            out.append(int(dig, 8) & 0xFF)
        elif c in (0x0A, 0x0D):            # Zeilenfortsetzung
            i += 1
            if c == 0x0D and i < len(b) and b[i] == 0x0A:
                i += 1
        else:
            out += _ESC.get(c, bytes([c])); i += 1
    return bytes(out)


def simple_widths(fo, objs):
    """/Widths eines einfachen Fonts -> ({code: breite}, default)."""
    m = re.search(rb'/Widths\s*\[([^\]]*)\]', fo)
    if not m:
        m2 = re.search(rb'/Widths\s+(\d+)\s+\d+\s+R', fo)
        if not m2:
            return {}, 500.0
        m = re.search(rb'\[([^\]]*)\]', objs.get(int(m2.group(1)), b''))
        if not m:
            return {}, 500.0
    first = int(re.search(rb'/FirstChar\s+(\d+)', fo).group(1)) if re.search(
        rb'/FirstChar\s+(\d+)', fo) else 0
    ws = [float(x) for x in m.group(1).split()]
    mw = re.search(rb'/MissingWidth\s+([\d\.]+)', fo)
    return ({first + i: w for i, w in enumerate(ws) if w},
            float(mw.group(1)) if mw else 500.0)


def cid_widths(fo):
    """/W eines CIDFontType2 -> ({cid: breite}, /DW)."""
    m = re.search(rb'/W\s*\[(.*?)\]\s*/', fo, re.S)
    out = {}
    if m:
        toks = re.findall(rb'\[[^\]]*\]|[\d\.]+', m.group(1))
        i = 0
        while i < len(toks):
            if toks[i].startswith(b'['):
                i += 1
                continue
            c = int(float(toks[i]))
            if i + 1 < len(toks) and toks[i + 1].startswith(b'['):
                for k, w in enumerate(toks[i + 1][1:-1].split()):
                    out[c + k] = float(w)
                i += 2
            elif i + 2 < len(toks):
                c2, w = int(float(toks[i + 1])), float(toks[i + 2])
                for cc in range(c, c2 + 1):
                    out[cc] = w
                i += 3
            else:
                break
    dw = re.search(rb'/DW\s+([\d\.]+)', fo)
    return out, float(dw.group(1)) if dw else 1000.0


def page_fonts(objs, page_raw):
    """/Font-Resource einer Seite -> {name: fontinfo-dict}."""
    res = page_raw
    m = re.search(rb'/Resources\s+(\d+)\s+\d+\s+R', page_raw)
    if m:
        res = objs[int(m.group(1))]
    m = re.search(rb'/Font\s*(<<.*?>>|(\d+)\s+\d+\s+R)', res, re.S)
    if not m:
        return {}
    fdict = objs[int(m.group(2))] if m.group(2) else m.group(1)
    fonts = {}
    for name, num in re.findall(rb'/(\w+)\s+(\d+)\s+\d+\s+R', fdict):
        fo = objs.get(int(num), b'')
        if b'/Type0' in fo:
            tu = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', fo)
            df = re.search(rb'/DescendantFonts\s+(\d+)\s+\d+\s+R', fo)
            desc = objs.get(int(df.group(1)), b'') if df else b''
            if b'/CIDFontType' not in desc:          # Array mit einer Referenz
                r = re.search(rb'(\d+)\s+\d+\s+R', desc)
                desc = objs.get(int(r.group(1)), b'') if r else b''
            w, dw = cid_widths(desc)
            fonts[name.decode()] = dict(
                kind='cid', cmap=parse_cmap(objs[int(tu.group(1))]),
                widths=w, default=dw)
        else:
            w, dw = simple_widths(fo, objs)
            fonts[name.decode()] = dict(
                kind='winansi', cmap=None, widths=w, default=dw)
    return fonts


_FALLBACK = dict(kind='winansi', cmap=None, widths={}, default=500.0)


_TOK = re.compile(
    rb'(?P<tm>(?P<ma>' + NUM + rb')\s+(?P<mb>' + NUM + rb')\s+(?P<mc>' + NUM +
    rb')\s+(?P<md>' + NUM + rb')\s+(?P<me>' + NUM + rb')\s+(?P<mf>' + NUM + rb')\s+Tm)'
    rb'|(?P<td>(?P<dx>' + NUM + rb')\s+(?P<dy>' + NUM + rb')\s+T(?P<dkind>[dD]))'
    rb'|(?P<tstar>T\*)'
    rb'|(?P<tl>(?P<lead>' + NUM + rb')\s+TL)'
    rb'|(?P<tc>(?P<cval>' + NUM + rb')\s+Tc)'
    rb'|(?P<tw>(?P<wval>' + NUM + rb')\s+Tw)'
    rb'|(?P<tz>(?P<zval>' + NUM + rb')\s+Tz)'
    rb'|(?P<cm>(?P<ca>' + NUM + rb')\s+(?P<cb>' + NUM + rb')\s+(?P<cc>' + NUM +
    rb')\s+(?P<cd>' + NUM + rb')\s+(?P<ce>' + NUM + rb')\s+(?P<cf>' + NUM + rb')\s+cm)'
    rb'|(?P<q>\bq\b)'
    rb'|(?P<Q>\bQ\b)'
    rb'|(?P<bt>BT)'
    rb'|(?P<tf>/(?P<fname>\w+)\s+(?P<fsize>' + NUM + rb')\s+Tf)'
    rb'|(?P<show>(?:\[(?:[^\]\\]|\\.)*\]\s*TJ)|(?:(?:\((?:[^\\()]|\\.)*\)|<[0-9A-Fa-f\s]*>)\s*[\'"]?\s*Tj))',
    re.S)

_PIECE = re.compile(rb'\((?:[^\\()]|\\.)*\)|<[0-9A-Fa-f\s]*>')


def extract_items(content, fonts):
    """Content-Stream -> [(y, x, seq, text)] in Geraetekoordinaten.

    Die Glyphenvorschuebe werden aus /Widths bzw. /W berechnet. Ohne das
    bleibt x innerhalb einer Textzeile auf dem Wert der letzten
    Positionierung stehen, und Zeilen, die ohne Td-Bewegung von der
    Stichwort- in die Satzspalte laufen, sind nicht mehr trennbar.
    """
    a = d = 1.0; b = c = 0.0; e = f = 0.0          # Textmatrix
    la, lb, lc, ld, le, lf = a, b, c, d, e, f      # Line-Matrix
    lead = 0.0
    fsize, tc, tw, th = 1.0, 0.0, 0.0, 1.0
    # Grafikzustand: ohne die CTM stehen alle Positionen relativ zur letzten
    # cm-Transformation, bei xelatex also seitenweise verschoben.
    ctm = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    stapel = []
    fi = _FALLBACK
    items = []
    seq = 0

    def setmat(na, nb, nc, nd, ne, nf, line=True):
        nonlocal a, b, c, d, e, f, la, lb, lc, ld, le, lf
        a, b, c, d, e, f = na, nb, nc, nd, ne, nf
        if line:
            la, lb, lc, ld, le, lf = na, nb, nc, nd, ne, nf

    def newline(tx, ty):
        setmat(la, lb, lc, ld,
               tx * la + ty * lc + le,
               tx * lb + ty * ld + lf)

    def advance(tx):
        # [1 0 0 1 tx 0] x Tm, nur Translation entlang der Textrichtung
        setmat(a, b, c, d, tx * a + e, tx * b + f, line=False)

    def codes(piece):
        """Show-Operand -> [(code, unicode)] gemaess aktuellem Font."""
        if piece.startswith(b'<'):
            hx = re.sub(rb'\s', b'', piece[1:-1])
            if len(hx) % 2:
                hx += b'0'
            raw = bytes.fromhex(hx.decode())
        else:
            raw = unescape(piece[1:-1])
        if fi['kind'] == 'cid':
            return [((raw[i] << 8) | raw[i + 1],
                     fi['cmap'].get((raw[i] << 8) | raw[i + 1], '\ufffd'))
                    for i in range(0, len(raw) - 1, 2)]
        return [(byte, bytes([byte]).decode('cp1252', 'replace')) for byte in raw]

    for m in _TOK.finditer(content):
        if m.group('q'):
            stapel.append(ctm)
        elif m.group('Q'):
            if stapel:
                ctm = stapel.pop()
        elif m.group('cm'):
            na, nb, nc, nd, ne, nf = (
                float(m.group(k)) for k in ('ca', 'cb', 'cc', 'cd', 'ce', 'cf'))
            a0, b0, c0, d0, e0, f0 = ctm
            ctm = (na * a0 + nb * c0, na * b0 + nb * d0,
                   nc * a0 + nd * c0, nc * b0 + nd * d0,
                   ne * a0 + nf * c0 + e0, ne * b0 + nf * d0 + f0)
        elif m.group('bt'):
            setmat(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        elif m.group('tm'):
            setmat(*(float(m.group(k)) for k in ('ma', 'mb', 'mc', 'md', 'me', 'mf')))
        elif m.group('td'):
            tx, ty = float(m.group('dx')), float(m.group('dy'))
            if m.group('dkind') == b'D':
                lead = -ty
            newline(tx, ty)
        elif m.group('tstar'):
            newline(0.0, -lead)
        elif m.group('tl'):
            lead = float(m.group('lead'))
        elif m.group('tc'):
            tc = float(m.group('cval'))
        elif m.group('tw'):
            tw = float(m.group('wval'))
        elif m.group('tz'):
            th = float(m.group('zval')) / 100.0
        elif m.group('tf'):
            fi = fonts.get(m.group('fname').decode(), _FALLBACK)
            fsize = float(m.group('fsize'))
        else:
            op = m.group('show')
            parts = (re.findall(rb'\[|\]|' + NUM + rb'|' + _PIECE.pattern, op)
                     if op.rstrip().endswith(b'TJ') else _PIECE.findall(op))
            for p in parts:
                if p in (b'[', b']'):
                    continue
                if not (p.startswith(b'(') or p.startswith(b'<')):
                    advance(-float(p) / 1000.0 * fsize * th)   # Kerning
                    continue
                cs = codes(p)
                txt = ''.join(u for _, u in cs)
                if txt:
                    # Textmatrix mit der CTM verrechnen
                    a0, b0, c0, d0, e0, f0 = ctm
                    gx = e * a0 + f * c0 + e0
                    gy = e * b0 + f * d0 + f0
                    items.append((round(gy, 2), round(gx, 2), seq, txt))
                    seq += 1
                tx = 0.0
                for code, _u in cs:
                    w = fi['widths'].get(code, fi['default'])
                    tx += (w / 1000.0 * fsize + tc +
                           (tw if (fi['kind'] != 'cid' and code == 32) else 0.0))
                advance(tx * th)
    return items


def seitenbaum(objs):
    """Seitenobjekte in Dokumentreihenfolge.

    Bei vielen Seiten ist der /Pages-Baum verschachtelt; wer nur den ersten
    Knoten liest, sieht zwei von 164 Seiten.
    """
    katalog = next((v for v in objs.values() if b'/Type/Catalog' in v), None)
    if katalog is None:
        return []
    m = re.search(rb'/Pages\s+(\d+)\s+\d+\s+R', katalog)
    if not m:
        return []
    aus, stapel = [], [int(m.group(1))]
    gesehen = set()
    while stapel:
        num = stapel.pop(0)
        if num in gesehen or num not in objs:
            continue
        gesehen.add(num)
        raw = objs[num]
        if b'/Type/Page' in raw and b'/Type/Pages' not in raw:
            aus.append(num)
            continue
        km = re.search(rb'/Kids\s*\[(.*?)\]', raw, re.S)
        if km:
            kinder = [int(x) for x in
                      re.findall(rb'(\d+)\s+\d+\s+R', km.group(1))]
            stapel = kinder + stapel
    return aus


def seitentext(objs, num):
    """-> [(y, x, seq, text)] einer Seite."""
    raw = objs[num]
    cm = re.search(rb'/Contents\s*\[?\s*(\d+)\s+\d+\s+R', raw)
    if not cm or int(cm.group(1)) not in objs:
        return []
    inhalt = stream_of(objs[int(cm.group(1))])
    return extract_items(inhalt, page_fonts(objs, raw)) if inhalt else []


def pages(path='A1_SD1_Wortliste_02.pdf'):
    """-> {seitenzahl_aus_fusszeile: [(y, x, seq, text)]}"""
    data, objs = load(path)
    out = {}
    for num, raw in objs.items():
        if not (b'/Page' in raw and b'/Contents' in raw):
            continue
        if b'/Type0' in raw or b'/Pages' in raw.split(b'/Contents')[0][:200]:
            pass
        # /Contents kommt als Referenz oder als Array vor: xelatex schreibt
        # /Contents[4 0 R], Acrobat /Contents 4 0 R.
        cm = re.search(rb'/Contents\s*\[?\s*(\d+)\s+\d+\s+R', raw)
        if not cm or int(cm.group(1)) not in objs:
            continue
        content = stream_of(objs[int(cm.group(1))])
        if not content:
            continue
        items = extract_items(content, page_fonts(objs, raw))
        pg = None
        for *_, t in items:
            mm = re.match(r'^Seite (\d+)$', t.strip())
            if mm:
                pg = int(mm.group(1))
        if pg is not None:
            out[pg] = items
    return out
