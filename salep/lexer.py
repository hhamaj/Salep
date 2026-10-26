"""Belirteçlere ayırma ve Türkçe anahtar sözcüklerin Python karşılığına eşlenmesi.

Kaynak kod Python'un ``tokenize`` modülüyle belirteçlere ayrılır. Değişiklikler
(satır, başlangıç sütunu, bitiş sütunu, yeni metin) biçiminde "düzenleme"
olarak toplanır ve özgün satırların üzerine uygulanır; böylece satır sayısı
hiç değişmez. Metin (string), f-string ve yorum içeriğine dokunulmaz.
"""

from __future__ import annotations

import io
import tokenize
import unicodedata

from .errors import EksikGirdi, SalepHatası

# Sözcükler küçük harfli ve büyük/küçük harfe duyarlıdır: 'Eğer' çevrilmez.
ANAHTAR_SÖZCÜKLER = {
    "eğer": "if",
    "yoksa": "else",
    "işlev": "def",
    "döndür": "return",
    "ve": "and",
    "veya": "or",
    "değil": "not",
    "doğru": "True",
    "yanlış": "False",
    "hiç": "None",
    "kır": "break",
    "devam": "continue",
    "geç": "pass",
    "kullan": "import",
    "olarak": "as",
}

# --katı kipinde yasak olan İngilizce sözcükler ve Salep'teki karşılıkları.
KATI_KARŞILIKLAR = {ing: tr for tr, ing in ANAHTAR_SÖZCÜKLER.items()}
KATI_KARŞILIKLAR["elif"] = "yoksa eğer"
KATI_KARŞILIKLAR["for"] = "her ... için ... içinde"
KATI_KARŞILIKLAR["while"] = "... iken"
KATI_KARŞILIKLAR["from"] = "... içinden ... kullan"

# (satır, başlangıç sütunu, bitiş sütunu, yeni metin)
Düzenleme = tuple[int, int, int, str]

_ATLANAN_TÜRLER = {
    tokenize.COMMENT, tokenize.NL, tokenize.INDENT, tokenize.DEDENT,
    tokenize.ENCODING, tokenize.ENDMARKER,
}
_FSTRING_BAŞ = {getattr(tokenize, ad) for ad in ("FSTRING_START", "TSTRING_START")
                if hasattr(tokenize, ad)}
_FSTRING_SON = {getattr(tokenize, ad) for ad in ("FSTRING_END", "TSTRING_END")
                if hasattr(tokenize, ad)}
_AÇILAN = "([{"
_KAPANAN = ")]}"


def normalleştir(kaynak: str) -> str:
    return unicodedata.normalize("NFC", kaynak)


def belirteçler(kaynak: str, dosya_adı: str = "<salep>") -> list[tokenize.TokenInfo]:
    """Kaynağı belirteçlere ayırır; hataları satır bilgili SyntaxError'a çevirir."""
    sonuç: list[tokenize.TokenInfo] = []
    parantezler: list[int] = []  # açık parantezlerin satırları
    satırlar = io.StringIO(kaynak).readlines()

    def satır_metni(no: int) -> str:
        return satırlar[no - 1] if 1 <= no <= len(satırlar) else ""

    try:
        for b in tokenize.generate_tokens(io.StringIO(kaynak).readline):
            if b.type == tokenize.OP and b.string in _AÇILAN:
                parantezler.append(b.start[0])
            elif b.type == tokenize.OP and b.string in _KAPANAN and parantezler:
                parantezler.pop()
            sonuç.append(b)
    except tokenize.TokenError as e:
        mesaj, (satır, sütun) = e.args
        if "EOF in multi-line statement" in mesaj:
            satır = parantezler[-1] if parantezler else max(satır - 1, 1)
            raise EksikGirdi(mesaj, (dosya_adı, satır, 1, satır_metni(satır))) from None
        if "EOF in multi-line string" in mesaj:
            raise EksikGirdi(mesaj, (dosya_adı, satır, sütun + 1, satır_metni(satır))) from None
        raise SyntaxError(mesaj, (dosya_adı, satır, sütun + 1, satır_metni(satır))) from None
    except SyntaxError as e:  # IndentationError, TabError
        e.filename = dosya_adı
        raise
    return sonuç


def mantıksal_satırlar(bler: list[tokenize.TokenInfo]) -> list[list[int]]:
    """Belirteçleri deyimlere (mantıksal satırlara) böler.

    Her deyim, anlamlı belirteçlerin dizinlerinden oluşan bir listedir. Yorumlar
    ve boş satırlar atlanır; bir f-string tek belirteç (başlangıcı) sayılır.
    """
    satırlar: list[list[int]] = []
    şimdiki: list[int] = []
    derinlik = 0
    fstring = 0
    for i, b in enumerate(bler):
        if b.type in _FSTRING_BAŞ:
            if fstring == 0:
                şimdiki.append(i)
            fstring += 1
            continue
        if b.type in _FSTRING_SON:
            fstring -= 1
            continue
        if fstring or b.type in _ATLANAN_TÜRLER:
            continue
        if b.type == tokenize.OP and b.string in _AÇILAN:
            derinlik += 1
        elif b.type == tokenize.OP and b.string in _KAPANAN:
            derinlik = max(derinlik - 1, 0)
        if b.type == tokenize.NEWLINE or (b.string == ";" and derinlik == 0):
            if şimdiki:
                satırlar.append(şimdiki)
            şimdiki = []
            continue
        şimdiki.append(i)
    if şimdiki:
        satırlar.append(şimdiki)
    return satırlar


def anahtar_sözcük_düzenlemeleri(bler: list[tokenize.TokenInfo],
                                 satırlar: list[list[int]],
                                 tüketilen: set[int],
                                 katı: bool = False) -> list[Düzenleme]:
    """Türkçe anahtar sözcükleri Python karşılıklarıyla değiştirir."""
    düzenlemeler: list[Düzenleme] = []
    for satır in satırlar:
        atla = False
        for konum, i in enumerate(satır):
            if atla:
                atla = False
                continue
            b = bler[i]
            if i in tüketilen or b.type != tokenize.NAME:
                continue
            if konum > 0 and bler[satır[konum - 1]].string == ".":
                continue  # nesne.öznitelik: öznitelik adlarına dokunma
            if konum == 0 and b.string == "yoksa" and len(satır) > 1:
                sonraki = bler[satır[1]]
                if sonraki.string == "eğer" and sonraki.start[0] == b.start[0]:
                    düzenlemeler.append((b.start[0], b.start[1], sonraki.end[1], "elif"))
                    atla = True
                    continue
            if b.string in ANAHTAR_SÖZCÜKLER:
                düzenlemeler.append((b.start[0], b.start[1], b.end[1],
                                     ANAHTAR_SÖZCÜKLER[b.string]))
            elif katı and b.string in KATI_KARŞILIKLAR:
                raise SalepHatası(
                    f"'{b.string}' İngilizce bir anahtar sözcük.",
                    b.start[0],
                    f"Salep'te bunun yerine '{KATI_KARŞILIKLAR[b.string]}' yaz.",
                )
    return düzenlemeler


def düzenlemeleri_uygula(kaynak: str, düzenlemeler: list[Düzenleme]) -> str:
    """Düzenlemeleri sağdan sola uygular; satır sayısı korunur."""
    satırlar = io.StringIO(kaynak).readlines()
    # Aynı yerden başlayanlarda önce uzun olan uygulanır, sonra sıfır boylu ekleme.
    for satır, baş, son, yeni in sorted(düzenlemeler, key=lambda d: d[:3], reverse=True):
        metin = satırlar[satır - 1]
        satırlar[satır - 1] = metin[:baş] + yeni + metin[son:]
    return "".join(satırlar)
