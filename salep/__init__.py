"""Salep: çocuklar için Türkçe sözdizimli, Python'a çevrilen programlama dili."""

from .errors import SalepHatası, hata_mesajı
from .prelude import ortam_oluştur
from .transform import çevir

__version__ = "0.1.0"
__all__ = ["çevir", "çalıştır", "hata_mesajı", "ortam_oluştur", "SalepHatası"]


def çalıştır(kaynak: str, dosya_adı: str = "<salep>", katı: bool = False,
             ortam: dict | None = None) -> dict:
    """Salep kaynak kodunu çevirip çalıştırır; kullanılan ortamı döndürür."""
    python = çevir(kaynak, katı=katı, dosya_adı=dosya_adı)
    kod = compile(python, dosya_adı, "exec")
    if ortam is None:
        ortam = ortam_oluştur()
    exec(kod, ortam)
    return ortam
