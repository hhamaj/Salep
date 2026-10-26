import pytest

from salep import SalepHatası, çalıştır, çevir


@pytest.mark.parametrize("kaynak, beklenen", [
    ("her s için sayılar içinde:\n", "for s in sayılar:\n"),
    ("her i için aralık(1, 6) içinde:\n", "for i in aralık(1, 6):\n"),
    ("her a, b için [(1, 2)] içinde:\n", "for a, b in [(1, 2)]:\n"),
    ("her x için f(için, içinde) içinde:\n", "for x in f(için, içinde):\n"),
    ("    her x için y içinde: yazdır(x)\n", "    for x in y: yazdır(x)\n"),
    ("her k için sözlük_ içinde:  # yorum\n", "for k in sözlük_:  # yorum\n"),
])
def test_her_kalıbı(kaynak, beklenen):
    assert çevir(kaynak) == beklenen


def test_her_kalıbı_çalışır(capsys):
    çalıştır("her harf için 'şık' içinde:\n    yazdır(harf)\n")
    assert capsys.readouterr().out == "ş\nı\nk\n"


@pytest.mark.parametrize("kaynak, parça", [
    ("her x sayılar içinde:\n", "'için' sözcüğü eksik"),
    ("her için sayılar içinde:\n", "değişken adı"),
    ("her x için sayılar:\n", "'içinde' sözcüğü eksik"),
    ("her x için içinde:\n", "üzerinde dönülecek"),
    ("her x için sayılar içinde\n", '":"'),
])
def test_bozuk_her_kalıbı_türkçe_hata(kaynak, parça):
    with pytest.raises(SalepHatası) as bilgi:
        çevir("x = 1\n" + kaynak)
    assert parça in bilgi.value.mesaj
    assert bilgi.value.satır == 2
    assert bilgi.value.ipucu


@pytest.mark.parametrize("kaynak, beklenen", [
    ("kullan matematik\n", "import math as matematik\n"),
    ("kullan rastgele\n", "import random as rastgele\n"),
    ("kullan zaman\n", "import time as zaman\n"),
    ("kullan matematik, os, zaman\n", "import math as matematik, os, time as zaman\n"),
    ("kullan matematik olarak m\n", "import math as m\n"),
    ("matematik içinden sqrt, pi kullan\n", "from math import sqrt, pi\n"),
    ("matematik içinden sqrt olarak kök kullan\n", "from math import sqrt as kök\n"),
    ("os.path içinden join kullan\n", "from os.path import join\n"),
    ("rastgele içinden (randint,\n    choice) kullan\n", "from random import (randint,\n    choice)\n"),
    ("from zaman import sleep\n", "from time import sleep\n"),
    ("kullan os.path\n", "import os.path\n"),
])
def test_içe_aktarma_takma_adları(kaynak, beklenen):
    assert çevir(kaynak) == beklenen


def test_içe_aktarılan_modül_çalışır(capsys):
    çalıştır(
        "kullan matematik\n"
        "matematik içinden sqrt kullan\n"
        "kullan rastgele\n"
        "rastgele.seed(1)\n"
        "yazdır(matematik.floor(2.7), sqrt(16), rastgele.randint(5, 5))\n"
    )
    assert capsys.readouterr().out == "2 4.0 5\n"


def test_yerleşikler_ortamda_hazır(capsys):
    ortam = çalıştır(
        "yazdır(uzunluk([1, 2]), tamsayı('3'), ondalık('1.5'), yazı(4))\n"
        "yazdır(topla([1, 2]), en_küçük(3, 1), en_büyük(3, 1), mutlak(-2))\n"
        "yazdır(yuvarla(2.6), sırala([2, 1]), tür(1) == tamsayı)\n"
        "yazdır(liste('ab'), sözlük(a=1), küme([1, 1]), liste(aralık(2)))\n"
    )
    assert capsys.readouterr().out == (
        "2 3 1.5 4\n3 1 3 2\n3 [1, 2] True\n['a', 'b'] {'a': 1} {1} [0, 1]\n"
    )
    assert ortam["girdi"] is input


def test_yerleşikler_kaynağa_eklenmez():
    assert çevir("yazdır(1)\n") == "yazdır(1)\n"


def test_metotlar_aynen_yazılır(capsys):
    çalıştır("l = []\nl.append(1)\nyazdır(l)\n")
    assert capsys.readouterr().out == "[1]\n"


def test_eski_içe_aktar_sözcüğü_artık_çevrilmez():
    assert çevir("içe_aktar matematik\n") == "içe_aktar matematik\n"


@pytest.mark.parametrize("kaynak, beklenen", [
    ("sayaç > 0 iken:\n", "while sayaç > 0:\n"),
    ("    x < 3 ve değil bitti iken: kır\n", "    while x < 3 and not bitti: break\n"),
    ("değil bitti iken:\n", "while not bitti:\n"),
    ("(a >\n  b) iken:\n", "while (a >\n  b):\n"),
    ("doğru iken:  # sonsuz döngü\n", "while True:  # sonsuz döngü\n"),
])
def test_iken_kalıbı(kaynak, beklenen):
    assert çevir(kaynak) == beklenen


def test_iken_kalıbı_çalışır(capsys):
    çalıştır("i = 0\ni < 3 iken:\n    yazdır(i)\n    i = i + 1\n")
    assert capsys.readouterr().out == "0\n1\n2\n"


@pytest.mark.parametrize("kaynak, parça", [
    ("iken x > 0:\n", "koşuldan sonra gelir"),
    ("x > 0 iken\n", '":"'),
    ("x > 0 iken yazdır(x)\n", '":"'),
])
def test_bozuk_iken_kalıbı_türkçe_hata(kaynak, parça):
    with pytest.raises(SalepHatası) as bilgi:
        çevir("x = 1\n" + kaynak)
    assert parça in bilgi.value.mesaj
    assert bilgi.value.satır == 2
    assert "sayaç > 0 iken:" in bilgi.value.ipucu


@pytest.mark.parametrize("kaynak, parça", [
    ("sqrt kullan\n", "'içinden' sözcüğü eksik"),
    ("içinden sqrt kullan\n", "modül adı"),
    ("matematik içinden kullan\n", "adları yazmalısın"),
])
def test_bozuk_içinden_kalıbı_türkçe_hata(kaynak, parça):
    with pytest.raises(SalepHatası) as bilgi:
        çevir(kaynak)
    assert parça in bilgi.value.mesaj
    assert "matematik içinden sqrt kullan" in bilgi.value.ipucu


def test_eski_şuradan_biçimi_artık_çevrilmez():
    assert çevir("şuradan os kullan path\n") == "şuradan os import path\n"


@pytest.mark.parametrize("kaynak, beklenen", [
    ("eğer x > 3 ise:\n", "if x > 3:\n"),
    ("yoksa eğer x ise: geç\n", "elif x: pass\n"),
    ("eğer değil bitti ise:\n", "if not bitti:\n"),
    ("eğer d[1:2] ise:  # dilim\n", "if d[1:2]:  # dilim\n"),
    ("eğer (a ve\n    b) ise:\n", "if (a and\n    b):\n"),
    ("a = 1 eğer x yoksa 2\n", "a = 1 if x else 2\n"),  # satır içi koşulda 'ise' yok
])
def test_ise_kalıbı(kaynak, beklenen):
    assert çevir(kaynak) == beklenen


@pytest.mark.parametrize("kaynak, parça, ipucu", [
    ("eğer x:\n", "'ise' gelmeli", "eğer sayı > 10 ise:"),
    ("yoksa eğer x:\n", "'ise' gelmeli", "eğer sayı > 10 ise:"),
    ("eğer x\n", "'ise:' ile bitmeli", "eğer sayı > 10 ise:"),
    ("eğer ise:\n", "koşul yazmalısın", "eğer sayı > 10 ise:"),
    ("eğer x ise\n", '":" gelmeli', '":" eksik'),
])
def test_bozuk_ise_kalıbı_türkçe_hata(kaynak, parça, ipucu):
    with pytest.raises(SalepHatası) as bilgi:
        çevir("x = 1\n" + kaynak)
    assert parça in bilgi.value.mesaj
    assert bilgi.value.satır == 2
    assert ipucu in bilgi.value.ipucu
