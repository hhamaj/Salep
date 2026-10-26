"""Satır düzeyindeki özel kalıplar ve Salep -> Python çevirisi.

* ``her X için Y içinde:``           ->  ``for X in Y:``
* ``KOŞUL iken:``                     ->  ``while KOŞUL:``
* ``kullan matematik``                ->  ``import math as matematik``
* ``matematik içinden sqrt kullan``   ->  ``from math import sqrt``
"""

from __future__ import annotations

import tokenize

from .errors import SalepHatası
from .lexer import (Düzenleme, anahtar_sözcük_düzenlemeleri, belirteçler,
                    düzenlemeleri_uygula, mantıksal_satırlar, normalleştir)

MODÜL_TAKMA_ADLARI = {
    "matematik": "math",
    "rastgele": "random",
    "zaman": "time",
}

_HER_İPUCU = "Doğru biçim şöyle: her sayı için sayılar içinde:"
_İKEN_İPUCU = "Doğru biçim şöyle: sayaç > 0 iken:"
_İÇİNDEN_İPUCU = "Doğru biçim şöyle: matematik içinden sqrt kullan"


def _derinlik_sıfır(bler, satır):
    """Satırda parantez dışında kalan (konum, belirteç) çiftlerini verir."""
    derinlik = 0
    for konum, i in enumerate(satır):
        b = bler[i]
        if b.type == tokenize.OP and b.string in "([{":
            derinlik += 1
        elif b.type == tokenize.OP and b.string in ")]}":
            derinlik -= 1
        elif derinlik == 0:
            yield konum, b


def _sil_önündeki_boşlukla(bler, satır, konum):
    """satır[konum] belirtecini önündeki boşlukla birlikte silen düzenleme."""
    b = bler[satır[konum]]
    önceki = bler[satır[konum - 1]]
    baş = önceki.end[1] if önceki.end[0] == b.start[0] else b.start[1]
    return (b.start[0], baş, b.end[1], "")


def _her_kalıbı(bler, satır, düzenlemeler, tüketilen):
    her = bler[satır[0]]
    no = her.start[0]
    derinlik = 0
    için = içinde = None
    for konum in range(1, len(satır)):
        b = bler[satır[konum]]
        if b.type == tokenize.OP and b.string in "([{":
            derinlik += 1
        elif b.type == tokenize.OP and b.string in ")]}":
            derinlik -= 1
        elif derinlik == 0 and b.type == tokenize.NAME:
            if için is None and b.string == "için":
                için = konum
            elif için is not None and b.string == "içinde":
                içinde = konum
                break
    if için is None:
        raise SalepHatası("'her' satırında 'için' sözcüğü eksik.", no, _HER_İPUCU)
    if için == 1:
        raise SalepHatası("'her' ile 'için' arasına bir değişken adı yazmalısın.", no, _HER_İPUCU)
    if içinde is None:
        raise SalepHatası("'her' satırında 'içinde' sözcüğü eksik.", no, _HER_İPUCU)
    if içinde == için + 1:
        raise SalepHatası("'için' ile 'içinde' arasına üzerinde dönülecek şeyi yazmalısın.",
                          no, _HER_İPUCU)
    if içinde + 1 >= len(satır) or bler[satır[içinde + 1]].string != ":":
        raise SalepHatası("'içinde' sözcüğünden sonra \":\" gelmeli.", no,
                          "Satırın sonunda \":\" eksik olabilir.")

    b_için = bler[satır[için]]
    düzenlemeler.append((no, her.start[1], her.end[1], "for"))
    düzenlemeler.append((b_için.start[0], b_için.start[1], b_için.end[1], "in"))
    # 'içinde' ile önündeki boşluk silinir: "for s in sayılar:"
    düzenlemeler.append(_sil_önündeki_boşlukla(bler, satır, içinde))
    tüketilen.update({satır[0], satır[için], satır[içinde]})


def _modül_adı_düzenle(b, takma_ad_ekle, düzenlemeler, tüketilen, i):
    gerçek = MODÜL_TAKMA_ADLARI[b.string]
    yeni = f"{gerçek} as {b.string}" if takma_ad_ekle else gerçek
    düzenlemeler.append((b.start[0], b.start[1], b.end[1], yeni))
    tüketilen.add(i)


def _kullan_kalıbı(bler, satır, düzenlemeler, tüketilen):
    # kullan a [olarak x], b.c [olarak y], ...
    konum = 1
    while konum < len(satır):
        b = bler[satır[konum]]
        if b.type != tokenize.NAME:
            return
        sonraki = bler[satır[konum + 1]].string if konum + 1 < len(satır) else None
        if b.string in MODÜL_TAKMA_ADLARI and sonraki != ".":
            _modül_adı_düzenle(b, sonraki not in ("olarak", "as"),
                               düzenlemeler, tüketilen, satır[konum])
        # noktalı adı ve isteğe bağlı 'olarak ad' kısmını geç
        konum += 1
        while konum + 1 < len(satır) and bler[satır[konum]].string == ".":
            konum += 2
        if konum < len(satır) and bler[satır[konum]].string in ("olarak", "as"):
            konum += 2
        if konum < len(satır) and bler[satır[konum]].string == ",":
            konum += 1
        else:
            return


def _iken_kalıbı(bler, satır, konum, düzenlemeler, tüketilen):
    # KOŞUL iken:  ->  while KOŞUL:
    no = bler[satır[konum]].start[0]
    if konum == 0:
        raise SalepHatası("'iken' sözcüğü koşuldan sonra gelir.", no, _İKEN_İPUCU)
    if konum + 1 >= len(satır) or bler[satır[konum + 1]].string != ":":
        raise SalepHatası("'iken' sözcüğünden hemen sonra \":\" gelmeli.", no, _İKEN_İPUCU)
    ilk = bler[satır[0]]
    # Boyu sıfır olan ekleme, aynı yerden başlayan düzenlemelerden sonra uygulanır.
    düzenlemeler.append((ilk.start[0], ilk.start[1], ilk.start[1], "while "))
    düzenlemeler.append(_sil_önündeki_boşlukla(bler, satır, konum))
    tüketilen.add(satır[konum])


def _içinden_kalıbı(bler, satır, düzenlemeler, tüketilen):
    # matematik içinden sqrt, pi kullan  ->  from math import sqrt, pi
    son = len(satır) - 1
    no = bler[satır[son]].start[0]
    içinden = next((k for k, b in _derinlik_sıfır(bler, satır)
                    if b.type == tokenize.NAME and b.string == "içinden"), None)
    if içinden is None:
        raise SalepHatası("Bu 'kullan' satırında 'içinden' sözcüğü eksik.", no,
                          _İÇİNDEN_İPUCU + "  (ya da: kullan matematik)")
    if içinden == 0:
        raise SalepHatası("'içinden' sözcüğünden önce bir modül adı yazmalısın.",
                          no, _İÇİNDEN_İPUCU)
    if içinden == son - 1:
        raise SalepHatası("'içinden' ile 'kullan' arasına almak istediğin adları yazmalısın.",
                          no, _İÇİNDEN_İPUCU)
    ilk = bler[satır[0]]
    düzenlemeler.append((ilk.start[0], ilk.start[1], ilk.start[1], "from "))
    if içinden == 1 and ilk.string in MODÜL_TAKMA_ADLARI:
        _modül_adı_düzenle(ilk, False, düzenlemeler, tüketilen, satır[0])
    b = bler[satır[içinden]]
    düzenlemeler.append((b.start[0], b.start[1], b.end[1], "import"))
    düzenlemeler.append(_sil_önündeki_boşlukla(bler, satır, son))
    tüketilen.update({satır[içinden], satır[son]})


def _from_kalıbı(bler, satır, düzenlemeler, tüketilen):
    # İngilizce: from matematik import ...
    if len(satır) >= 3:
        modül, aktar = bler[satır[1]], bler[satır[2]]
        if modül.string in MODÜL_TAKMA_ADLARI and aktar.string == "import":
            _modül_adı_düzenle(modül, False, düzenlemeler, tüketilen, satır[1])


def özel_kalıp_düzenlemeleri(bler, satırlar) -> tuple[list[Düzenleme], set[int]]:
    düzenlemeler: list[Düzenleme] = []
    tüketilen: set[int] = set()
    for satır in satırlar:
        ilk = bler[satır[0]]
        son = bler[satır[-1]]
        if ilk.type == tokenize.NAME and ilk.string == "her":
            _her_kalıbı(bler, satır, düzenlemeler, tüketilen)
        elif ilk.type == tokenize.NAME and ilk.string in ("kullan", "import"):
            _kullan_kalıbı(bler, satır, düzenlemeler, tüketilen)
        elif ilk.type == tokenize.NAME and ilk.string == "from":
            _from_kalıbı(bler, satır, düzenlemeler, tüketilen)
        elif son.type == tokenize.NAME and son.string == "kullan":
            _içinden_kalıbı(bler, satır, düzenlemeler, tüketilen)
        else:
            for konum, b in _derinlik_sıfır(bler, satır):
                if b.type == tokenize.NAME and b.string == "iken":
                    _iken_kalıbı(bler, satır, konum, düzenlemeler, tüketilen)
                    break
    return düzenlemeler, tüketilen


def çevir(kaynak: str, katı: bool = False, dosya_adı: str = "<salep>") -> str:
    """Salep kaynak kodunu satır satır eşleşen Python koduna çevirir."""
    kaynak = normalleştir(kaynak)
    bler = belirteçler(kaynak, dosya_adı)
    satırlar = mantıksal_satırlar(bler)
    düzenlemeler, tüketilen = özel_kalıp_düzenlemeleri(bler, satırlar)
    düzenlemeler += anahtar_sözcük_düzenlemeleri(bler, satırlar, tüketilen, katı)
    return düzenlemeleri_uygula(kaynak, düzenlemeler)
