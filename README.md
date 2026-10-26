# Salep

Salep, çocuklara programlamayı **ana dillerinde** öğretmek için tasarlanmış, Türkçe
sözdizimli küçük bir programlama dilidir. Salep kodu satır satır Python'a çevrilir
ve Python ile çalıştırılır; böylece hatalar her zaman yazdığın özgün satırı gösterir
ve tüm Python kütüphaneleri kullanılabilir.

```
eğer hava == "soğuk":
    yazdır("Bir bardak salep iç!")
```

Sürüm: **0.1** · Gereksinim: Python 3.10+ · Dış bağımlılık yok.

## Kurulum

```sh
pip install .            # 'salep' komutunu kurar
pip install ".[test]"    # testler için pytest ile birlikte
```

Kurmadan da çalıştırabilirsin: `python -m salep dosya.salep`

## Kullanım

| Komut | Ne yapar |
|---|---|
| `salep dosya.salep` | Programı çalıştırır |
| `salep çevir dosya.salep` | Üretilen Python kodunu yazdırır |
| `salep` | Etkileşimli kip (REPL); `:` ile biten bloklar boş satırla biter |
| `--katı` | İngilizce anahtar sözcükleri (`if`, `for`, `def`...) hata sayar |

## Anahtar sözcükler

| Salep | Python | | Salep | Python |
|---|---|---|---|---|
| `eğer` | `if` | | `doğru` | `True` |
| `yoksa eğer` | `elif` | | `yanlış` | `False` |
| `yoksa` | `else` | | `hiç` | `None` |
| `KOŞUL iken:` | `while KOŞUL:` | | `kır` | `break` |
| `her X için Y içinde:` | `for X in Y:` | | `devam` | `continue` |
| `işlev` | `def` | | `geç` | `pass` |
| `döndür` | `return` | | `kullan` | `import` |
| `ve` | `and` | | `olarak` | `as` |
| `veya` | `or` | | `M içinden A kullan` | `from M import A` |
| `değil` | `not` | | | |

Sözcükler küçük harfle yazılır ve büyük/küçük harfe duyarlıdır (`Eğer` çevrilmez).

Türkçe söz dizimine uyması için `iken` koşuldan **sonra** gelir (`sayaç > 0 iken:`),
bir modülden ad almak için de `matematik içinden sqrt kullan` yazılır.

## Yerleşik işlevler

| Salep | Python | | Salep | Python |
|---|---|---|---|---|
| `yazdır` | `print` | | `küme` | `set` |
| `girdi` | `input` | | `topla` | `sum` |
| `aralık` | `range` | | `en_küçük` | `min` |
| `uzunluk` | `len` | | `en_büyük` | `max` |
| `tamsayı` | `int` | | `mutlak` | `abs` |
| `ondalık` | `float` | | `yuvarla` | `round` |
| `yazı` | `str` | | `sırala` | `sorted` |
| `liste` | `list` | | `tür` | `type` |
| `sözlük` | `dict` | | | |

Modüller: `kullan matematik` → `import math as matematik`; aynı şekilde
`rastgele` → `random`, `zaman` → `time`. Metotlar (`.append` gibi) şimdilik
İngilizce yazılır.

## Örnekler

**1. Toplam ve kareler**

```
sayılar = [3, 8, 1, 9]
toplam = 0

her s için sayılar içinde:
    toplam = toplam + s

yazdır("Toplam:", toplam)

işlev kare(x):
    döndür x * x

her i için aralık(1, 6) içinde:
    yazdır(kare(i))
```

**2. Not değerlendirme**

```
işlev harf_notu(puan):
    eğer puan >= 85:
        döndür "Pekiyi"
    yoksa eğer puan >= 65:
        döndür "İyi"
    yoksa:
        döndür "Tekrar çalış"

öğrenci = girdi("Adın ne? ")
puan = tamsayı(girdi("Puanın kaç? "))
yazdır(öğrenci, "→", harf_notu(puan))
```

**3. Büyüyen daireler**

```
kullan matematik
zaman içinden sleep kullan

yarıçap = 1
yarıçap <= 3 iken:
    alan = matematik.pi * yarıçap * yarıçap
    yazdır("Yarıçap", yarıçap, "→ alan", yuvarla(alan, 2))
    yarıçap = yarıçap + 1
    sleep(0.5)
```

Daha fazlası ve beklenen çıktıları `examples/` klasöründe.

## Hata mesajları

Python hataları kısa ve yol gösteren Türkçe mesajlara çevrilir:

```
Hata (3. satır): eğer toplam > 10
Python bu satırı anlayamadı.
İpucu: Satırın sonunda ":" eksik olabilir.
```

```
Hata (2. satır): yazdır(sonuç)
'sonuç' diye bir şey tanımlamadın.
İpucu: Yazımı doğru mu? Bir değişkeni kullanmadan önce ona değer vermelisin.
```

## Nasıl çalışır?

1. Kaynak Unicode NFC biçimine getirilir ve Python'un `tokenize` modülüyle
   belirteçlere ayrılır (`salep/lexer.py`).
2. `her ... için ... içinde` ve modül takma adları gibi satır kalıpları işlenir
   (`salep/transform.py`), ardından Türkçe anahtar sözcükler değiştirilir.
   Metin, f-string ve yorum içeriğine dokunulmaz; satır eklenmez ya da silinmez.
3. Sonuç `exec(compile(...))` ile, Türkçe yerleşiklerin önceden yüklendiği bir
   ortamda çalıştırılır (`salep/prelude.py`).
4. Hatalar özgün satıra bağlanıp Türkçeleştirilir (`salep/errors.py`).

## Yol haritası

Sonraki sürümlerde Türkçeleştirilecek metotlar ve modüller için
[ROADMAP.md](ROADMAP.md) dosyasına bak.

## Testler

```sh
python -m pytest
```

## Varsayımlar

Belirtimde açık olmayan noktalarda şu kararlar verildi:

- **`her` kalıbı yalnızca deyim başında** tanınır. Liste üreteçleri
  (`[x for x in l]`) için Türkçe karşılık yoktur; İngilizce yazılabilir.
  `için` ve `içinde` bu kalıbın dışında sıradan ad sayılır.
- **`iken`** satırın sonunda, `:` işaretinden hemen önce yazılır; başka yerde
  kullanılırsa Türkçe hata verilir. `içinden ... kullan` kalıbı, `kullan` ile
  biten satırlarda tanınır.
- **`yoksa eğer`** yalnızca deyim başında ve aynı satırda yan yana yazıldığında
  `elif` olur.
- **`--katı`** yalnızca Türkçe karşılığı olan İngilizce sözcükleri (`if`, `elif`,
  `else`, `while`, `for`, `def`, `return`, `and`, `or`, `not`, `True`, `False`,
  `None`, `break`, `continue`, `pass`, `import`, `as`, `from`) yasaklar. Karşılığı
  olmayanlar (`in`, `is`, `class`, `try`, `lambda`...) serbesttir.
- **f-string'lerin** `{...}` içindeki ifadelerde anahtar sözcükler çevrilmez
  (bütün f-string metin sayılır; bu, Python sürümleri arasında aynı davranışı
  sağlar). Yerleşik işlevler (`yazdır`, `uzunluk`...) orada da çalışır.
- **Nokta sonrası adlar** (`nesne.değil`) öznitelik sayılır ve çevrilmez.
- **Modül takma adları** `kullan`/`içinden` yanında İngilizce `import`/`from`
  ile de uygulanır. `kullan matematik olarak m` → `import math as m`.
- **Anahtar sözcükler ayrılmıştır**: `eğer`, `her` vb. değişken adı olarak
  kullanılamaz.
- **Hata mesajı biçimi** üç satırdır: başlık (satır numarası + satırın kendisi),
  ne olduğu, ipucu. Hatalar standart hata akışına yazılır, çıkış kodu 1'dir.
  Hata mesajlarında Python tür adları Türkçeleştirilir (`int` → `tamsayı`).
- **Satır numaraları** birebir korunur; satır içindeki sütunlar çeviri sırasında
  kayabilir (ör. `içinde` silinir, `while` satır başına eklenir).
- **REPL**: `:` ile biten bir satır içeren girdi boş bir satırla biter; tek
  başına yazılan ifadelerin değeri yazdırılır.
- **`sırala`** Python'un `sorted` işlevidir; Türkçe alfabe sırasına değil, Unicode
  kod sırasına göre sıralar.
