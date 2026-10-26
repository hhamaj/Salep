import os
import subprocess
import sys
from pathlib import Path

import pytest

from salep.cli import girdi_tamam_mı

KÖK = Path(__file__).parent.parent


def salep(*argümanlar, girdi=None):
    ortam = {**os.environ, "PYTHONPATH": str(KÖK), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, "-m", "salep", *argümanlar], input=girdi,
                          capture_output=True, text=True, encoding="utf-8", env=ortam)


@pytest.fixture
def dosya(tmp_path):
    def yaz(içerik):
        yol = tmp_path / "program.salep"
        yol.write_text(içerik, encoding="utf-8")
        return str(yol)
    return yaz


def test_dosya_çalıştırma(dosya):
    sonuç = salep(dosya("yazdır('merhaba', 'dünya')\n"))
    assert sonuç.returncode == 0
    assert sonuç.stdout == "merhaba dünya\n"


def test_çevir_komutu(dosya):
    sonuç = salep("çevir", dosya("eğer doğru:\n    yazdır(1)\n"))
    assert sonuç.returncode == 0
    assert sonuç.stdout == "if True:\n    yazdır(1)\n"


def test_hata_türkçe_ve_çıkış_kodu_1(dosya):
    sonuç = salep(dosya("yazdır('önce')\nyazdır(1 / 0)\n"))
    assert sonuç.returncode == 1
    assert sonuç.stdout == "önce\n"
    assert sonuç.stderr.startswith("Hata (2. satır): yazdır(1 / 0)\n0'a bölemezsin.")
    assert "Traceback" not in sonuç.stderr


def test_katı_bayrağı(dosya):
    yol = dosya("if True:\n    yazdır(1)\n")
    assert salep(yol).stdout == "1\n"
    sonuç = salep("--katı", yol)
    assert sonuç.returncode == 1
    assert "'if' İngilizce bir anahtar sözcük." in sonuç.stderr


def test_olmayan_dosya():
    sonuç = salep("yok.salep")
    assert sonuç.returncode == 1
    assert "'yok.salep' diye bir dosya bulunamadı." in sonuç.stderr


def test_hatalı_kullanım():
    sonuç = salep("çevir")
    assert sonuç.returncode == 2
    assert "Kullanım" in sonuç.stderr


def test_repl_çok_satırlı_blok():
    girdi = (
        "x = 5\n"
        "x * 2\n"
        "eğer x > 3:\n"
        "    yazdır('büyük')\n"
        "\n"
        "l = [1,\n"
        "2]\n"
        "uzunluk(l)\n"
        "yazdır(y)\n"
        "yazdır('son')\n"
    )
    sonuç = salep(girdi=girdi)
    assert sonuç.returncode == 0
    çıktı = sonuç.stdout.replace(">>> ", "").replace("... ", "")
    assert "10\nbüyük\n2\n" in çıktı
    assert "son\n" in çıktı
    assert "'y' diye bir şey tanımlamadın." in sonuç.stderr


@pytest.mark.parametrize("satırlar, tamam", [
    (["x = 1"], True),
    (["eğer x:"], False),
    (["eğer x:", "    y = 1"], False),
    (["eğer x:", "    y = 1", ""], True),
    (["l = [1,"], False),
    (["l = [1,", "2]"], True),
    (["s = '''a"], False),
    (["yazdır('kapanmamış)"], True),  # hata, çalıştırılınca gösterilir
])
def test_repl_girdi_tamam_mı(satırlar, tamam):
    assert girdi_tamam_mı(satırlar) is tamam
