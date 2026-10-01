#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""Adjektivformen je Nominalklasse.

Die Formen sind ausgeschrieben statt aus einem Praefix berechnet, weil
gerade Kl. 9/10 unregelmaessig ist: -zuri wird nzuri, -kubwa bleibt kubwa,
-pya wird mpya. Eine Praefixregel wuerde hier falsche Formen erzeugen.
"""

FORMEN = {
    #        1        2         3        4         5       6         7         8         9        10       11       14
    'zuri': ('mzuri', 'wazuri', 'mzuri', 'mizuri', 'zuri', 'mazuri', 'kizuri', 'vizuri', 'nzuri', 'nzuri', 'mzuri', 'mzuri'),
    'dogo': ('mdogo', 'wadogo', 'mdogo', 'midogo', 'dogo', 'madogo', 'kidogo', 'vidogo', 'ndogo', 'ndogo', 'mdogo', 'mdogo'),
    'kubwa':('mkubwa','wakubwa','mkubwa','mikubwa','kubwa','makubwa','kikubwa','vikubwa','kubwa', 'kubwa', 'mkubwa','mkubwa'),
    'pya':  ('mpya',  'wapya',  'mpya',  'mipya',  'jipya','mapya',  'kipya',  'vipya',  'mpya',  'mpya',  'mpya',  'mpya'),
    'refu': ('mrefu', 'warefu', 'mrefu', 'mirefu', 'refu', 'marefu', 'kirefu', 'virefu', 'ndefu', 'ndefu', 'mrefu', 'mrefu'),
}

KLASSEN = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '14')

DEUTSCH = {'zuri': 'gut', 'dogo': 'klein', 'kubwa': 'groß',
           'pya': 'neu', 'refu': 'lang'}

ENGLISCH = {'zuri': 'good', 'dogo': 'small', 'kubwa': 'big',
            'pya': 'new', 'refu': 'long, tall'}

UNREGELMAESSIG = {
    ('zuri', '9'): 'Nasalpräfix n- vor z-',
    ('kubwa', '9'): 'kein Nasalpräfix vor k-',
    ('pya', '9'): 'Nasalpräfix wird m- vor p-',
    ('pya', '5'): 'Kl. 5 nimmt hier ji-, sonst Nullpräfix',
    ('zuri', '5'): 'Kl. 5 hat Nullpräfix',
}


# Formen, bei denen das Nasalpraefix den Stammanlaut veraendert und die
# Segmentierung darum nicht mechanisch abzuleiten ist.
SEGMENT_AUSNAHME = {
    ('refu', '9'): 'n-defu',
    ('refu', '10'): 'n-defu',
}


def form(stamm, kl):
    """-zuri + Kl. 7 -> kizuri"""
    return FORMEN[stamm][KLASSEN.index(str(kl))]


def segment(stamm, kl):
    """-zuri + Kl. 7 -> ('ki-zuri', '-')  ·  Kl. 5 -> ('zuri', '.')

    Zweiter Wert ist das Trennzeichen fuer die Labelzeile: Bindestrich, wenn
    ein Praefix sichtbar ist, sonst Punkt (Nullpraefix, nichts abtrennbar).
    """
    kl = str(kl)
    f = form(stamm, kl)
    if (stamm, kl) in SEGMENT_AUSNAHME:
        return SEGMENT_AUSNAHME[(stamm, kl)], '-'
    if f == stamm:
        return f, '.'
    if f.endswith(stamm):
        return f'{f[:-len(stamm)]}-{stamm}', '-'
    raise ValueError(f'Segmentierung unklar: -{stamm} Kl. {kl} -> {f}')


def hinweis(stamm, kl):
    return UNREGELMAESSIG.get((stamm, str(kl)), '')


if __name__ == '__main__':
    print('Stamm  ' + ' '.join(f'Kl{k:<7}' for k in KLASSEN))
    for s in FORMEN:
        print(f'-{s:<6}' + ' '.join(f'{form(s, k):<9}' for k in KLASSEN))
