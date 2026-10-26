"""Salep hataları ve Python hatalarının Türkçe'ye çevrilmesi."""

from __future__ import annotations

import difflib
import re
import traceback


class SalepHatası(Exception):
    """Salep'in kendi bulduğu yazım hataları (ör. bozuk 'her' kalıbı)."""

    def __init__(self, mesaj: str, satır: int, ipucu: str | None = None):
        super().__init__(mesaj)
        self.mesaj = mesaj
        self.satır = satır
        self.ipucu = ipucu


class EksikGirdi(SyntaxError):
    """Kaynak yarım kalmış: parantez ya da üç tırnaklı metin kapanmamış."""


TÜR_ADLARI = {
    "int": "tamsayı",
    "float": "ondalık",
    "str": "yazı",
    "list": "liste",
    "dict": "sözlük",
    "set": "küme",
    "tuple": "demet",
    "bool": "doğru/yanlış",
    "NoneType": "hiç",
    "function": "işlev",
    "builtin_function_or_method": "işlev",
    "module": "modül",
}


def _tür(ad: str) -> str:
    return TÜR_ADLARI.get(ad, ad)


def _türleri_çevir(metin: str) -> list[str]:
    return [_tür(ad) for ad in re.findall(r"'(\w+)'", metin)]


# --- Hata türlerine göre açıklama ve ipucu ---------------------------------

def _sözdizimi(exc: SyntaxError) -> tuple[str, str | None]:
    msg = exc.msg or ""
    if isinstance(exc, TabError):
        return ("Girintide sekme (Tab) ve boşluk karışmış.",
                "Girintilerde yalnızca boşluk kullan (her seviye için 4 boşluk).")
    if isinstance(exc, IndentationError):
        if msg.startswith("expected an indented block"):
            return ("Bu satırın içeriden (girintili) başlaması gerekiyordu.",
                    "\":\" ile biten satırdan sonraki satırları 4 boşluk içeriden yaz.")
        if msg.startswith("unexpected indent"):
            return ("Bu satır gereksiz yere içeriden başlıyor.",
                    "Satırın başındaki boşlukları silmeyi dene.")
        if "unindent does not match" in msg:
            return ("Bu satırın girintisi üstteki satırlarla uyuşmuyor.",
                    "Aynı bloktaki satırlar aynı sayıda boşlukla başlamalı.")
        return ("Girintide bir sorun var.",
                "Satır başlarındaki boşlukları kontrol et.")
    if isinstance(exc, EksikGirdi) or "was never closed" in msg:
        return ("Açılan bir parantez ya da tırnak kapanmamış.",
                "Açtığın her parantezi ve tırnağı kapattığından emin ol.")
    if "unterminated string" in msg or "unterminated triple-quoted" in msg:
        return ("Bir metnin tırnağı kapanmamış.",
                "Metni başlattığın tırnağın aynısıyla bitir: \"merhaba\"")
    if msg.startswith("unmatched") or "does not match opening parenthesis" in msg:
        return ("Fazladan ya da yanlış bir kapanış parantezi var.",
                "Parantezleri tek tek eşleştirerek say.")
    if msg.startswith("expected ':'"):
        return ("Python bu satırı anlayamadı.",
                "Satırın sonunda \":\" eksik olabilir.")
    if "forgot a comma" in msg:
        return ("Python bu satırı anlayamadı.",
                "Arada bir virgül (,) eksik olabilir.")
    if "Maybe you meant '==' " in msg or "cannot assign to" in msg:
        return ("Bu satırda bir değer atanamıyor.",
                "Karşılaştırma yapıyorsan \"=\" yerine \"==\" yaz.")
    if "invalid character" in msg:
        return ("Bu satırda Salep'in tanımadığı bir işaret var.",
                "Kopyala-yapıştır ile gelen özel tırnak ya da işaretleri düzelt.")
    if "outside function" in msg:
        return ("'döndür' yalnızca bir işlevin içinde kullanılabilir.",
                "'döndür' satırını 'işlev' bloğunun içine (girintili) yaz.")
    if "outside loop" in msg:
        return ("'kır' ve 'devam' yalnızca bir döngünün içinde kullanılabilir.",
                "Bu satırı 'her' ya da 'iken' bloğunun içine yaz.")
    return ("Python bu satırı anlayamadı.",
            "Yazımı, iki noktayı (:) ve parantezleri kontrol et.")


def _ad(exc: NameError, ortam: dict | None) -> tuple[str, str | None]:
    ad = getattr(exc, "name", None)
    if ad is None:
        bulunan = re.search(r"'(\w+)'", str(exc))
        ad = bulunan.group(1) if bulunan else "?"
    açıklama = f"'{ad}' diye bir şey tanımlamadın."
    from .lexer import ANAHTAR_SÖZCÜKLER
    from .prelude import YERLEŞİKLER
    adaylar = set(YERLEŞİKLER) | set(ANAHTAR_SÖZCÜKLER)
    if ortam:
        adaylar |= {a for a in ortam if not a.startswith("__")}
    yakın = difflib.get_close_matches(ad, sorted(adaylar), n=1)
    if yakın:
        return açıklama, f"'{yakın[0]}' demek istemiş olabilir misin?"
    return açıklama, "Yazımı doğru mu? Bir değişkeni kullanmadan önce ona değer vermelisin."


def _tip(exc: TypeError) -> tuple[str, str | None]:
    msg = str(exc)
    if msg.startswith("unsupported operand") or "can only concatenate" in msg \
            or "not supported between" in msg:
        türler = _türleri_çevir(msg.replace('"', "'"))
        ek = f" ({' ve '.join(türler)})" if türler else ""
        return (f"Farklı türdeki değerleri birlikte kullanamazsın{ek}.",
                "Sayıyı metne çevirmek için yazı(...), metni sayıya çevirmek için tamsayı(...) kullan.")
    if "is not callable" in msg:
        tür = _türleri_çevir(msg)
        return (f"Bu bir işlev değil ({tür[0] if tür else '?'}), çağıramazsın.",
                "Adın sonundaki parantezleri kontrol et; aynı adı bir değişken için kullanmış olabilirsin.")
    if "is not subscriptable" in msg:
        return ("Bu değerin içinden [ ] ile eleman alamazsın.",
                "[ ] yalnızca liste, yazı ve sözlüklerde kullanılır.")
    if "is not iterable" in msg:
        return ("Bu değerin elemanları üzerinde dönemezsin.",
                "'her ... için ... içinde' kalıbında bir liste ya da aralık(...) kullan.")
    if "positional argument" in msg or "required" in msg and "argument" in msg:
        return ("İşleve yanlış sayıda değer verdin.",
                "İşlevin tanımındaki parantezde kaç değer istendiğine bak.")
    return ("Bir değer yanlış türde kullanıldı.",
            "Değerlerin türünü tür(...) ile kontrol edebilirsin.")


def _değer(exc: ValueError) -> tuple[str, str | None]:
    msg = str(exc)
    bulunan = re.search(r"invalid literal for int\(\) with base \d+: (.*)$", msg)
    if bulunan:
        return (f"{bulunan.group(1)} bir tamsayıya çevrilemez.",
                "Çevirdiğin metnin yalnızca rakamlardan oluştuğundan emin ol.")
    bulunan = re.search(r"could not convert string to float: (.*)$", msg)
    if bulunan:
        return (f"{bulunan.group(1)} bir ondalık sayıya çevrilemez.",
                "Ondalık sayılarda virgül değil nokta kullan: 3.5")
    return ("Bu değer burada uygun değil.",
            "Verdiğin değerin beklenen biçimde olduğunu kontrol et.")


def açıklama_ve_ipucu(exc: BaseException, ortam: dict | None = None) -> tuple[str, str | None]:
    if isinstance(exc, SalepHatası):
        return exc.mesaj, exc.ipucu
    if isinstance(exc, SyntaxError):
        return _sözdizimi(exc)
    if isinstance(exc, NameError):
        return _ad(exc, ortam)
    if isinstance(exc, TypeError):
        return _tip(exc)
    if isinstance(exc, ZeroDivisionError):
        return "0'a bölemezsin.", "Bölen sayının 0 olmadığından emin ol."
    if isinstance(exc, IndexError):
        return ("Bu sırada bir eleman yok.",
                "Sıra numaraları 0'dan başlar; son eleman uzunluk(liste) - 1 sırasındadır.")
    if isinstance(exc, KeyError):
        anahtar = exc.args[0] if exc.args else "?"
        return (f"Sözlükte {anahtar!r} diye bir anahtar yok.",
                "Anahtarın yazımını kontrol et; sözlükteki anahtarları yazdır(...) ile görebilirsin.")
    if isinstance(exc, ValueError):
        return _değer(exc)
    if isinstance(exc, FileNotFoundError):
        return (f"'{exc.filename}' diye bir dosya bulunamadı.",
                "Dosya adını ve bulunduğu klasörü kontrol et.")
    if isinstance(exc, ModuleNotFoundError):
        return (f"'{exc.name}' adında bir modül bulunamadı.",
                "Modül adının yazımını kontrol et (ör. matematik, rastgele, zaman).")
    if isinstance(exc, ImportError):
        bulunan = re.search(r"cannot import name '(\w+)' from '([\w.]+)'", str(exc))
        if bulunan:
            return (f"'{bulunan.group(2)}' içinde '{bulunan.group(1)}' diye bir şey yok.",
                    "Almak istediğin adın yazımını kontrol et.")
        return "Bir modül içe aktarılamadı.", None
    return (f"Beklenmedik bir hata oluştu ({type(exc).__name__}): {exc}", None)


def satır_numarası(exc: BaseException, dosya_adı: str) -> int | None:
    if isinstance(exc, SalepHatası):
        return exc.satır
    if isinstance(exc, SyntaxError) and exc.filename in (dosya_adı, None):
        return exc.lineno
    satır = None
    for çerçeve in traceback.extract_tb(exc.__traceback__):
        if çerçeve.filename == dosya_adı:
            satır = çerçeve.lineno
    return satır


def hata_mesajı(exc: BaseException, kaynak: str, dosya_adı: str = "<salep>",
                ortam: dict | None = None) -> str:
    """Hatayı çocuğa yol gösteren kısa bir Türkçe mesaja çevirir."""
    açıklama, ipucu = açıklama_ve_ipucu(exc, ortam)
    satır = satır_numarası(exc, dosya_adı)
    satırlar = kaynak.splitlines()
    if satır is not None and 1 <= satır <= len(satırlar):
        başlık = f"Hata ({satır}. satır): {satırlar[satır - 1].strip()}"
    elif satır is not None:
        başlık = f"Hata ({satır}. satır):"
    else:
        başlık = "Hata:"
    parçalar = [başlık, açıklama]
    if ipucu:
        parçalar.append(f"İpucu: {ipucu}")
    return "\n".join(parçalar)
