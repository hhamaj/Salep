"""Komut satırı arayüzü.

    salep dosya.salep          programı çalıştırır
    salep çevir dosya.salep    üretilen Python kodunu yazdırır
    salep                      etkileşimli kip (REPL)
"""

from __future__ import annotations

import sys
import tokenize

from . import __version__, çalıştır
from .errors import EksikGirdi, hata_mesajı
from .lexer import belirteçler, normalleştir
from .prelude import ortam_oluştur
from .transform import çevir

KULLANIM = """Kullanım:
  salep [--katı] dosya.salep        programı çalıştırır
  salep [--katı] çevir dosya.salep  Python karşılığını yazdırır
  salep                             etkileşimli kipi açar

  --katı   İngilizce anahtar sözcükleri (if, for, def...) hata sayar."""


def _dosya_oku(yol: str) -> str | None:
    try:
        with open(yol, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Hata: '{yol}' diye bir dosya bulunamadı.", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"Hata: '{yol}' dosyası UTF-8 olarak okunamadı.", file=sys.stderr)
    except OSError as e:
        print(f"Hata: '{yol}' dosyası açılamadı ({e.strerror}).", file=sys.stderr)
    return None


def dosya_çalıştır(yol: str, katı: bool = False) -> int:
    kaynak = _dosya_oku(yol)
    if kaynak is None:
        return 1
    ortam = ortam_oluştur()
    try:
        çalıştır(kaynak, dosya_adı=yol, katı=katı, ortam=ortam)
    except KeyboardInterrupt:
        print("\nProgram durduruldu.", file=sys.stderr)
        return 130
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001 - her hatayı Türkçe göster
        sys.stdout.flush()
        print(hata_mesajı(e, normalleştir(kaynak), yol, ortam), file=sys.stderr)
        return 1
    return 0


def dosya_çevir(yol: str, katı: bool = False) -> int:
    kaynak = _dosya_oku(yol)
    if kaynak is None:
        return 1
    try:
        sys.stdout.write(çevir(kaynak, katı=katı, dosya_adı=yol))
    except Exception as e:  # noqa: BLE001
        print(hata_mesajı(e, normalleştir(kaynak), yol), file=sys.stderr)
        return 1
    return 0


# --- REPL --------------------------------------------------------------------

def _blok_mu(kaynak: str) -> bool:
    """Kaynakta ':' ile biten (blok açan) bir satır var mı?"""
    try:
        bler = [b for b in belirteçler(kaynak)
                if b.type not in (tokenize.COMMENT, tokenize.NL)]
    except SyntaxError:
        return False
    return any(a.string == ":" and b.type == tokenize.NEWLINE
               for a, b in zip(bler, bler[1:]))


def girdi_tamam_mı(satırlar: list[str]) -> bool:
    """Toplanan satırlar çalıştırılmaya hazır mı, yoksa devamı mı bekleniyor?"""
    kaynak = "\n".join(satırlar) + "\n"
    try:
        belirteçler(kaynak)
    except EksikGirdi:
        return False
    except SyntaxError:
        return True  # hatayı çalıştırırken göstereceğiz
    if _blok_mu(kaynak):
        return satırlar[-1].strip() == ""  # blok boş bir satırla biter
    return True


def repl(katı: bool = False) -> int:
    try:
        import readline  # noqa: F401 - ok tuşlarıyla geçmiş için
    except ImportError:
        pass
    print(f"Salep {__version__} — çıkmak için Ctrl+D'ye bas.")
    ortam = ortam_oluştur()
    while True:
        satırlar: list[str] = []
        try:
            while True:
                satır = input("... " if satırlar else ">>> ")
                if not satırlar and not satır.strip():
                    break
                satırlar.append(satır)
                if girdi_tamam_mı(satırlar):
                    break
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print("\n(iptal edildi)")
            continue
        if not satırlar:
            continue
        kaynak = normalleştir("\n".join(satırlar) + "\n")
        try:
            python = çevir(kaynak, katı=katı, dosya_adı="<salep>")
            exec(compile(python, "<salep>", "single"), ortam)
        except KeyboardInterrupt:
            print("\n(durduruldu)")
        except SystemExit:
            raise
        except BaseException as e:  # noqa: BLE001
            print(hata_mesajı(e, kaynak, "<salep>", ortam), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    argümanlar = list(sys.argv[1:] if argv is None else argv)
    for akış in (sys.stdout, sys.stderr):
        if hasattr(akış, "reconfigure"):
            akış.reconfigure(encoding="utf-8")
    katı = False
    if "--katı" in argümanlar:
        katı = True
        argümanlar.remove("--katı")
    if any(a in ("-h", "--help", "--yardım") for a in argümanlar):
        print(KULLANIM)
        return 0
    if not argümanlar:
        return repl(katı)
    if argümanlar[0] == "çevir" and len(argümanlar) == 2:
        return dosya_çevir(argümanlar[1], katı)
    if len(argümanlar) == 1 and argümanlar[0] != "çevir":
        return dosya_çalıştır(argümanlar[0], katı)
    print(KULLANIM, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
