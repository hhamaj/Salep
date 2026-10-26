# Salep

Salep, çocuklara programlamayı **ana dillerinde** öğretmek için tasarlanmış, Türkçe
sözdizimli küçük bir programlama dilidir. Salep kodu satır satır Python'a çevrilir
ve Python ile çalıştırılır; böylece hatalar her zaman yazdığın özgün satırı gösterir
ve tüm Python kütüphaneleri kullanılabilir.

```
eğer hava == "soğuk" ise:
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
| `yoksa` | `else` | | `doğru` | `True` |
| `değil` | `not` | | `yanlış` | `False` |
| `ve` | `and` | | `hiç` | `None` |
| `işlev` | `def` | | `kır` | `break` |
| `döndür` | `return` | | `devam` | `continue` |
| `veya` | `or` | | `geç` | `pass` |
| `olarak` | `as` | | | |

Sözcükler küçük harfle yazılır ve büyük/küçük harfe duyarlıdır (`Eğer` çevrilmez).

## Satır kalıpları

Koşullar, döngüler ve modüller Türkçe söz dizimine uyması için bütün bir satır
olarak yazılır. Türkçede olduğu gibi `ise`, `iken`, `kullan` sona gelir.

| Salep | Python | Ne işe yarar |
|---|---|---|
| `eğer sayı > 10 ise:` | `if sayı > 10:` | Koşul doğruysa çalıştır |
| `yoksa eğer sayı > 5 ise:` | `elif sayı > 5:` | Önceki koşul yanlışsa bunu dene |
| `her s için sayılar içinde:` | `for s in sayılar:` | Listedeki her eleman için tekrarla |
| `sayaç > 0 iken:` | `while sayaç > 0:` | Koşul doğru olduğu sürece tekrarla |
| `kullan matematik` | `import math as matematik` | Bir modülü kullanıma aç |
| `matematik içinden sqrt kullan` | `from math import sqrt` | Modülden yalnızca bir adı al |

```
sayı = 7
eğer sayı > 10 ise:
    yazdır("büyük")
yoksa eğer sayı > 5 ise:
    yazdır("orta")
yoksa:
    yazdır("küçük")

sayaç = 3
sayaç > 0 iken:
    yazdır(sayaç)
    sayaç = sayaç - 1

matematik içinden sqrt, pi kullan
yazdır(sqrt(16), pi)
```

Kalıp yanlış yazılırsa Salep doğru biçimi gösterir:

```
Hata (2. satır): iken sayaç > 0:
'iken' sözcüğü koşuldan sonra gelir.
İpucu: Doğru biçim şöyle: sayaç > 0 iken:
```

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
    eğer puan >= 85 ise:
        döndür "Pekiyi"
    yoksa eğer puan >= 65 ise:
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
'eğer' satırı 'ise:' ile bitmeli.
İpucu: Doğru biçim şöyle: eğer sayı > 10 ise:
```

```
Hata (2. satır): yazdır(sonuç)
'sonuç' diye bir şey tanımlamadın.
İpucu: Yazımı doğru mu? Bir değişkeni kullanmadan önce ona değer vermelisin.
```

## Nasıl çalışır?

1. Kaynak Unicode NFC biçimine getirilir ve Python'un `tokenize` modülüyle
   belirteçlere ayrılır (`salep/lexer.py`).
2. Satır kalıpları (`eğer … ise:`, `her … için … içinde`, `… iken:`, `kullan …`,
   `… içinden … kullan`) ve modül takma adları işlenir (`salep/transform.py`),
   ardından Türkçe anahtar sözcükler değiştirilir.
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
- **`ise` zorunludur**: `eğer` ve `yoksa eğer` satırları `ise:` ile biter; `:`
  işareti de kalır (bütün blokları açan tek işaret olsun diye). Satır içi koşulda
  (`a = 1 eğer x yoksa 2`) `ise` yazılmaz.
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
- **Anahtar sözcükler ayrılmıştır**: `eğer`, `ise`, `her`, `iken`, `kullan` vb. değişken
  ya da işlev adı olarak kullanılamaz.
- **Hata mesajı biçimi** üç satırdır: başlık (satır numarası + satırın kendisi),
  ne olduğu, ipucu. Hatalar standart hata akışına yazılır, çıkış kodu 1'dir.
  Hata mesajlarında Python tür adları Türkçeleştirilir (`int` → `tamsayı`).
- **Satır numaraları** birebir korunur; satır içindeki sütunlar çeviri sırasında
  kayabilir (ör. `ise` ve `içinde` silinir, `while` satır başına eklenir).
- **REPL**: `:` ile biten bir satır içeren girdi boş bir satırla biter; tek
  başına yazılan ifadelerin değeri yazdırılır.
- **`sırala`** Python'un `sorted` işlevidir; Türkçe alfabe sırasına değil, Unicode
  kod sırasına göre sıralar.
