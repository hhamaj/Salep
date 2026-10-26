"""Çalıştırma ortamına önceden yüklenen Türkçe yerleşik işlevler."""

import builtins

YERLEŞİKLER = {
    "yazdır": print,
    "girdi": input,
    "aralık": range,
    "uzunluk": len,
    "tamsayı": int,
    "ondalık": float,
    "yazı": str,
    "liste": list,
    "sözlük": dict,
    "küme": set,
    "topla": sum,
    "en_küçük": min,
    "en_büyük": max,
    "mutlak": abs,
    "yuvarla": round,
    "sırala": sorted,
    "tür": type,
}


def ortam_oluştur() -> dict:
    """Salep programının çalışacağı yeni bir globals sözlüğü döndürür."""
    return {"__name__": "__main__", "__builtins__": builtins, **YERLEŞİKLER}
