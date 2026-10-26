"""examples/ klasöründeki programların çıktısını .beklenen dosyalarıyla karşılaştırır."""

from pathlib import Path

import pytest

from salep import çalıştır

ÖRNEKLER = sorted((Path(__file__).parent.parent / "examples").glob("*.salep"))


def test_her_örneğin_beklenen_çıktısı_var():
    assert len(ÖRNEKLER) >= 5
    for yol in ÖRNEKLER:
        assert yol.with_suffix(".beklenen").exists(), yol.name


@pytest.mark.parametrize("yol", ÖRNEKLER, ids=lambda y: y.stem)
def test_örnek_çıktısı(yol, capsys):
    çalıştır(yol.read_text(encoding="utf-8"), dosya_adı=str(yol))
    beklenen = yol.with_suffix(".beklenen").read_text(encoding="utf-8")
    assert capsys.readouterr().out == beklenen
