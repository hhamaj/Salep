import unicodedata

import pytest

from salep import SalepHatası, çalıştır, çevir
from salep.lexer import ANAHTAR_SÖZCÜKLER


@pytest.mark.parametrize("tr, py", sorted(ANAHTAR_SÖZCÜKLER.items()))
def test_her_anahtar_sözcük_tek_başına_çevrilir(tr, py):
    assert çevir(f"{tr}\n") == f"{py}\n"


@pytest.mark.parametrize("kaynak, beklenen", [
    ("eğer x:\n    geç\n", "if x:\n    pass\n"),
    ("eğer x:\n    geç\nyoksa eğer y:\n    geç\nyoksa:\n    geç\n",
     "if x:\n    pass\nelif y:\n    pass\nelse:\n    pass\n"),
    ("doğru iken:\n    kır\n", "while True:\n    break\n"),
    ("yanlış iken:\n    devam\n", "while False:\n    continue\n"),
    ("işlev f(x):\n    döndür hiç\n", "def f(x):\n    return None\n"),
    ("a = x ve y veya değil z\n", "a = x and y or not z\n"),
    ("kullan os olarak işletim\n", "import os as işletim\n"),
    ("os içinden path kullan\n", "from os import path\n"),
    ("a = 1 eğer x yoksa 2\n", "a = 1 if x else 2\n"),
])
def test_anahtar_sözcükler_bağlam_içinde(kaynak, beklenen):
    assert çevir(kaynak) == beklenen


def test_çalışan_program_tüm_akış_sözcükleri(capsys):
    çalıştır(
        "işlev sınıflandır(n):\n"
        "    eğer n < 0:\n"
        "        döndür 'eksi'\n"
        "    yoksa eğer n == 0 veya değil n:\n"
        "        döndür 'sıfır'\n"
        "    yoksa:\n"
        "        döndür 'artı'\n"
        "i = 0\n"
        "doğru iken:\n"
        "    i = i + 1\n"
        "    eğer i == 2:\n"
        "        devam\n"
        "    eğer i > 3 ve değil yanlış:\n"
        "        kır\n"
        "    yazdır(i, sınıflandır(i - 2))\n"
        "geç\n"
    )
    assert capsys.readouterr().out == "1 eksi\n3 artı\n"


@pytest.mark.parametrize("kaynak", [
    'yazdır("eğer doğru ise yoksa hiç")\n',
    "yazdır('her x için y içinde')\n",
    'x = """eğer\nyoksa eğer\nişlev"""\n',
    "x = 1  # eğer doğru yoksa yanlış\n",
    "# her x için y içinde:\n",
    "x = f'{y} eğer {z}'\n",
])
def test_metin_ve_yorumlara_dokunulmaz(kaynak):
    assert çevir(kaynak) == kaynak


def test_metin_çıktısı_aynen_kalır(capsys):
    çalıştır('yazdır("eğer doğru değil")  # yoksa\n')
    assert capsys.readouterr().out == "eğer doğru değil\n"


def test_satır_sayısı_ve_numaraları_korunur():
    kaynak = (
        "# başlık\n"
        "\n"
        "her i için aralık(3) içinde:\n"
        "    x = '''çok\n"
        "satırlı eğer'''\n"
        "    eğer (i >\n"
        "          1): yazdır(i)\n"
        "kullan matematik\n"
        "yoksa_değil = 1\n"
    )
    python = çevir(kaynak)
    assert len(python.splitlines()) == len(kaynak.splitlines())
    satırlar = python.splitlines()
    assert satırlar[2] == "for i in aralık(3):"
    assert satırlar[5] == "    if (i >"
    assert satırlar[7] == "import math as matematik"
    assert satırlar[8] == "yoksa_değil = 1"


def test_sonda_satır_sonu_olmasa_da_çalışır(capsys):
    çalıştır("yazdır(doğru)")
    assert capsys.readouterr().out == "True\n"


def test_türkçe_harfli_değişken_adları(capsys):
    çalıştır(
        "öğrenci = 'Ayşe'\n"
        "şeker = 3\n"
        "ığdır_çğüöşİ = şeker * 2\n"
        "yazdır(öğrenci, şeker, ığdır_çğüöşİ)\n"
    )
    assert capsys.readouterr().out == "Ayşe 3 6\n"


def test_büyük_küçük_harfe_duyarlı():
    assert çevir("Eğer\nEĞER\nDoğru\n") == "Eğer\nEĞER\nDoğru\n"


def test_nfc_normalleştirme(capsys):
    # 'ğ' harfi ayrışık biçimde (g + birleşik breve) yazılmış
    ayrışık = unicodedata.normalize("NFD", "eğer doğru:\n    yazdır('ğ')\n")
    assert ayrışık != unicodedata.normalize("NFC", ayrışık)
    assert çevir(ayrışık) == "if True:\n    yazdır('ğ')\n"
    çalıştır(ayrışık)
    assert capsys.readouterr().out == "ğ\n"


def test_öznitelik_adlarına_dokunulmaz():
    assert çevir("a.değil = b.hiç\n") == "a.değil = b.hiç\n"


def test_tanınmayan_belirteçler_aynen_geçer(capsys):
    kaynak = "import math\nfor x in [1]:\n    if x: print(math.floor(2.5))\n"
    assert çevir(kaynak) == kaynak
    çalıştır(kaynak)
    assert capsys.readouterr().out == "2\n"


@pytest.mark.parametrize("ingilizce, öneri", [
    ("if x: pass", "eğer"), ("def f(): pass", "işlev"), ("for x in y: pass", "her"),
    ("x = True", "doğru"), ("while x: pass", "iken"), ("from os import path", "içinden"),
])
def test_katı_kipte_ingilizce_sözcük_hata_verir(ingilizce, öneri):
    with pytest.raises(SalepHatası) as bilgi:
        çevir("x = 1\n" + ingilizce + "\n", katı=True)
    assert bilgi.value.satır == 2
    assert öneri in bilgi.value.ipucu


def test_katı_kip_türkçe_koda_izin_verir():
    assert çevir("eğer x:\n    geç\n", katı=True) == "if x:\n    pass\n"
