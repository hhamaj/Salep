import pytest

from salep import hata_mesajı, ortam_oluştur, çalıştır


def hata(kaynak: str) -> str:
    ortam = ortam_oluştur()
    with pytest.raises(BaseException) as bilgi:
        çalıştır(kaynak, ortam=ortam)
    return hata_mesajı(bilgi.value, kaynak, "<salep>", ortam)


def test_iki_nokta_eksik_örneği():
    mesaj = hata("toplam = 0\nyazdır(toplam)\neğer toplam > 10\n    yazdır(1)\n")
    satırlar = mesaj.splitlines()
    assert satırlar[0] == "Hata (3. satır): eğer toplam > 10"
    assert satırlar[-1] == 'İpucu: Satırın sonunda ":" eksik olabilir.'


@pytest.mark.parametrize("kaynak, satır, parça", [
    ("x = (1,\n2\n", 1, "parantez"),
    ("yazdır('merhaba)\n", 1, "tırnağı kapanmamış"),
    ("x = 1\nyazdır(x))\n", 2, "kapanış parantezi"),
    ("x = 1\neğer x = 1:\n    geç\n", 2, '"=="'),
    ("döndür 1\n", 1, "işlevin içinde"),
    ("kır\n", 1, "döngünün içinde"),
])
def test_sözdizimi_hatası(kaynak, satır, parça):
    mesaj = hata(kaynak)
    assert mesaj.startswith(f"Hata ({satır}. satır):")
    assert parça in mesaj


@pytest.mark.parametrize("kaynak, satır, parça", [
    ("eğer doğru:\nyazdır(1)\n", 2, "içeriden (girintili) başlaması"),
    ("x = 1\n    y = 2\n", 2, "gereksiz yere içeriden"),
    ("eğer doğru:\n    x = 1\n  y = 2\n", 3, "uyuşmuyor"),
])
def test_girinti_hatası(kaynak, satır, parça):
    mesaj = hata(kaynak)
    assert mesaj.startswith(f"Hata ({satır}. satır):")
    assert parça in mesaj


def test_ad_hatası():
    mesaj = hata("a = 1\nyazdır(b)\n")
    assert mesaj.splitlines()[0] == "Hata (2. satır): yazdır(b)"
    assert "'b' diye bir şey tanımlamadın." in mesaj


def test_ad_hatası_benzer_ad_önerir():
    mesaj = hata("öğrenci = 1\nyazdir(öğrenc)\n")
    assert "'yazdir' diye bir şey tanımlamadın." in mesaj
    assert "'yazdır' demek istemiş" in mesaj


def test_tür_hatası():
    mesaj = hata("yaş = 10\nyazdır('Yaşın: ' + yaş)\n")
    assert mesaj.startswith("Hata (2. satır):")
    assert "Farklı türdeki değerleri" in mesaj
    assert "yazı" in mesaj and "tamsayı" in mesaj


def test_tür_hatası_yanlış_sayıda_değer():
    mesaj = hata("işlev f(a):\n    döndür a\nf(1, 2)\n")
    assert mesaj.startswith("Hata (3. satır):")
    assert "yanlış sayıda" in mesaj


def test_sıfıra_bölme():
    mesaj = hata("x = 0\nyazdır(5 / x)\n")
    assert mesaj.splitlines()[:2] == ["Hata (2. satır): yazdır(5 / x)", "0'a bölemezsin."]


def test_hata_işlev_içindeyse_o_satırı_gösterir():
    mesaj = hata("işlev böl(a):\n    döndür 1 / a\n\nböl(0)\n")
    assert mesaj.startswith("Hata (2. satır): döndür 1 / a")


def test_sıra_hatası():
    mesaj = hata("l = [1, 2]\nyazdır(l[5])\n")
    assert mesaj.startswith("Hata (2. satır):")
    assert "Bu sırada bir eleman yok." in mesaj


def test_anahtar_hatası():
    mesaj = hata("notlar = {'Ali': 90}\nyazdır(notlar['Ayşe'])\n")
    assert "Sözlükte 'Ayşe' diye bir anahtar yok." in mesaj


def test_değer_hatası():
    mesaj = hata("x = tamsayı('elma')\n")
    assert mesaj.startswith("Hata (1. satır):")
    assert "'elma' bir tamsayıya çevrilemez." in mesaj


def test_dosya_bulunamadı_hatası():
    mesaj = hata("open('olmayan_dosya.txt')\n")
    assert "'olmayan_dosya.txt' diye bir dosya bulunamadı." in mesaj


def test_modül_bulunamadı_hatası():
    mesaj = hata("kullan olmayan_modül\n")
    assert "'olmayan_modül' adında bir modül bulunamadı." in mesaj


def test_içe_aktarma_hatası():
    mesaj = hata("matematik içinden karekök kullan\n")
    assert "'math' içinde 'karekök' diye bir şey yok." in mesaj


def test_salep_hatası_mesajı():
    mesaj = hata("her x için liste:\n    geç\n")
    assert mesaj.splitlines()[0] == "Hata (1. satır): her x için liste:"
    assert "İpucu: Doğru biçim" in mesaj


def test_bilinmeyen_hata_türkçe_girişle_gösterilir():
    mesaj = hata("işlev f():\n    döndür f()\nf()\n")
    assert "Beklenmedik bir hata oluştu (RecursionError)" in mesaj
