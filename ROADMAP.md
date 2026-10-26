# Salep Yol Haritası

Bu belge Salep'te şu ana kadar Türkçeleştirilenleri ve ileride Türkçeleştirilecek
sözcük, işlev, metot ve modülleri listeler. İleriye dönük tablolardaki Türkçe
adlar **önerilerdir**; ilgili sürüm geliştirilirken kesinleşir.

Önceliği belirleyen ölçüt: **çocukların ilk aylarda en çok neye ihtiyaç
duyduğu.** Bu yüzden kaplumbağa çizimleri ve liste/metin metotları, dosya ya da
ağ işlerinden önce gelir.

| Sürüm | Odak | Durum |
|---|---|---|
| v0.1 | Çekirdek dil, temel yerleşikler, 3 modül adı, Türkçe hatalar | ✅ Tamamlandı |
| v0.2 | Metot eşlemesi, modül içi işlevlerin çevirisi, ek yerleşikler | ⏳ Sıradaki |
| v0.3 | Kaplumbağa (turtle), yeni anahtar sözcükler (`dene`, `sınıf`...) | 📋 Planlandı |
| v0.4 | Tarih, istatistik, dosya işlemleri | 📋 Planlandı |
| v1.0 | Kararlılık, editör desteği, Türkçe belgeler | 💭 Fikir |

---

## v0.1 — Tamamlandı ✅

### Anahtar sözcükler

| Salep | Python | Salep | Python |
|---|---|---|---|
| `eğer KOŞUL ise:` | `if KOŞUL:` | `doğru` | `True` |
| `yoksa eğer KOŞUL ise:` | `elif KOŞUL:` | `yanlış` | `False` |
| `yoksa` | `else` | `hiç` | `None` |
| `KOŞUL iken:` | `while KOŞUL:` | `kır` | `break` |
| `her X için Y içinde:` | `for X in Y:` | `devam` | `continue` |
| `işlev` | `def` | `geç` | `pass` |
| `döndür` | `return` | `kullan` | `import` |
| `ve` / `veya` / `değil` | `and` / `or` / `not` | `olarak` | `as` |
| | | `M içinden A kullan` | `from M import A` |

Dilbilgisi düzeltmesi: `ise`, `iken` ve `içinden … kullan` Türkçe söz dizimine
göre sona alındı (eski `iken x:` ve `şuradan … kullan …` biçimleri kaldırıldı).

### Yerleşik işlevler

`yazdır` (print), `girdi` (input), `aralık` (range), `uzunluk` (len),
`tamsayı` (int), `ondalık` (float), `yazı` (str), `liste` (list),
`sözlük` (dict), `küme` (set), `topla` (sum), `en_küçük` (min),
`en_büyük` (max), `mutlak` (abs), `yuvarla` (round), `sırala` (sorted),
`tür` (type)

### Modüller (yalnızca adları)

| Salep | Python | İçindeki işlevler |
|---|---|---|
| `matematik` | `math` | İngilizce (`matematik.floor`) → v0.2 |
| `rastgele` | `random` | İngilizce (`rastgele.randint`) → v0.2 |
| `zaman` | `time` | İngilizce (`zaman.sleep`) → v0.2 |

### Araçlar

- `salep dosya.salep`, `salep çevir dosya.salep`, REPL, `--katı` kipi
- Türkçe hata mesajları: SyntaxError, IndentationError, NameError, TypeError,
  ZeroDivisionError, IndexError, KeyError, ValueError, FileNotFoundError,
  ImportError

---

## v0.2 — Metotlar ve modül içi işlevler ⏳

### Tasarım sorunu: metot eşlemesi

`x.ekle(1)` satırında `x`'in liste mi yoksa yazı mı olduğu çeviri sırasında
bilinmez. Önerilen çözüm: `nesne.türkçe_ad` erişimlerini çalışma anında çözen
bir yardımcıya çevirmek. Örneğin `x.ekle(1)` → `__salep_metot(x, "ekle")(1)`.
Yardımcı, nesnenin türüne göre doğru İngilizce metodu bulur. Bu yöntem satır
numaralarını korur ve İngilizce metotlar (`x.append`) çalışmaya devam eder.

### Liste metotları

| Salep | Python | Salep | Python |
|---|---|---|---|
| `ekle` | `append` | `ters_çevir` | `reverse` |
| `uzat` | `extend` | `sırala` | `sort` |
| `araya_ekle` | `insert` | `say` | `count` |
| `çıkar` | `remove` | `bul` | `index` |
| `çek` | `pop` | `temizle` | `clear` |
| `kopyala` | `copy` | | |

### Yazı (metin) metotları

| Salep | Python | Salep | Python |
|---|---|---|---|
| `büyük_harf` | `upper` ⚠️ | `böl` | `split` |
| `küçük_harf` | `lower` ⚠️ | `birleştir` | `join` |
| `baş_harf_büyük` | `capitalize` ⚠️ | `değiştir` | `replace` |
| `kırp` | `strip` | `bul` | `find` |
| `ile_başlar` | `startswith` | `say` | `count` |
| `ile_biter` | `endswith` | `rakam_mı` | `isdigit` |

⚠️ Python'un `upper`/`lower` metotları Türkçeye uygun değil: `"i".upper()`
sonucu `"I"` olur, `"İ"` olmaz. Bu üç metot Türkçe kurallara göre (i↔İ, ı↔I)
yeniden yazılmalı.

### Sözlük ve küme metotları

| Salep | Python | Salep | Python |
|---|---|---|---|
| `anahtarlar` | `keys` | `al` | `get` |
| `değerler` | `values` | `güncelle` | `update` |
| `öğeler` | `items` | `ekle` (küme) | `add` |
| `çek` | `pop` | `çıkar` (küme) | `remove` |

### `matematik` (math)

| Salep | Python | Salep | Python |
|---|---|---|---|
| `karekök` | `sqrt` | `sinüs` / `kosinüs` / `tanjant` | `sin` / `cos` / `tan` |
| `üs` | `pow` | `derece` / `radyan` | `degrees` / `radians` |
| `aşağı_yuvarla` | `floor` | `logaritma` | `log` |
| `yukarı_yuvarla` | `ceil` | `faktöriyel` | `factorial` |
| `pi`, `e` | `pi`, `e` | `ebob` / `ekok` | `gcd` / `lcm` |
| `sonsuz` | `inf` | | |

### `rastgele` (random)

| Salep | Python | Salep | Python |
|---|---|---|---|
| `tamsayı` | `randint` | `karıştır` | `shuffle` |
| `seç` | `choice` | `örnek` | `sample` |
| `kesir` | `random` | `tohum` | `seed` |

### `zaman` (time)

| Salep | Python |
|---|---|
| `bekle` | `sleep` |
| `şimdi` | `time` |
| `kronometre` | `perf_counter` |

### Ek yerleşik işlevler

| Salep | Python | Salep | Python |
|---|---|---|---|
| `numaralandır` | `enumerate` | `hepsi` | `all` |
| `eşleştir` | `zip` | `herhangi` | `any` |
| `tersine` | `reversed` | `mantıksal` | `bool` |
| `demet` | `tuple` | `aç` | `open` |

**Uygulama notu:** Modüllerin Türkçe adları, İngilizce adları da taşıyan küçük
sarmalayıcı modüller olarak (`salep/kutuphaneler/matematik.py` gibi)
yazılacak. Böylece `matematik.floor` da çalışmayı sürdürür.

---

## v0.3 — Kaplumbağa ve yeni sözcükler 📋

### `kaplumbağa` (turtle)

Çocuklar için en etkili öğretim aracı olduğundan önceliği yüksek.

| Salep | Python | Salep | Python |
|---|---|---|---|
| `ileri` | `forward` | `kalem_kaldır` | `penup` |
| `geri` | `backward` | `kalem_indir` | `pendown` |
| `sağa` | `right` | `renk` | `color` |
| `sola` | `left` | `kalınlık` | `pensize` |
| `git` | `goto` | `hız` | `speed` |
| `daire` | `circle` | `doldur_başla` / `doldur_bitir` | `begin_fill` / `end_fill` |
| `gizle` / `göster` | `hideturtle` / `showturtle` | `ekran` | `Screen` |
| `bitir` | `done` | `yaz` | `write` |

Renk adları da çevrilecek: `"kırmızı"` → `"red"`, `"mavi"` → `"blue"` vb.
turtle çalışmak için tkinter'a ihtiyaç duyar; tkinter standart kütüphanededir ama
bazı Linux dağıtımlarında ayrıca kurulması gerekir.

### Yeni anahtar sözcükler

| Salep | Python | Not |
|---|---|---|
| `dene` | `try` | |
| `hata` | `except` | `hata SıfıraBölme:` gibi Türkçe hata adlarıyla |
| `sonunda` | `finally` | |
| `yükselt` | `raise` | |
| `sınıf` | `class` | `öz` → `self` (önerilen alışkanlık) |
| `ile` | `with` | `ile aç("a.txt") olarak f:` |
| `küresel` | `global` | |

**Açık sorular:**
- `in` ve `is` işleçlerinin Türkçesi ne olacak? `eğer x liste içinde ise:` biçimi
  `her` kalıbıyla karışabilir; ayrıntılı bir tasarım gerekiyor.
- Liste üreteçleri (`[x*2 her x için l içinde]`) desteklenecek mi?

---

## v0.4 — Günlük hayat modülleri 📋

| Salep modülü | Python | Örnek çeviriler |
|---|---|---|
| `tarih` | `datetime` | `bugün` (date.today), `şimdi` (datetime.now), `.yıl` / `.ay` / `.gün` |
| `istatistik` | `statistics` | `ortalama` (mean), `ortanca` (median), `tepe_değer` (mode), `standart_sapma` (stdev) |
| `dosya` | `pathlib` | `Yol` (Path), `.oku` (read_text), `.yaz` (write_text), `.var_mı` (exists) |
| `json` | `json` | `yükle` (loads), `metne_çevir` (dumps) |

Ayrıca Türkçe alfabe sırasına göre sıralama: `sırala(isimler)` çağrısı ç, ğ, ı,
ö, ş, ü harflerini doğru yere koymalı.

---

## v1.0 — Kararlılık 💭

- VS Code / editör sözdizimi renklendirmesi
- Türkçe dil belgeleri ve alıştırma kitapçığı
- Python 3.10–3.14 için sürekli entegrasyon (CI) testleri
- Python hata mesajlarının daha geniş kapsamda çevrilmesi

## Kapsam dışı

Dış bağımlılık gerektiren kütüphaneler (pygame, numpy, requests...) yol
haritasında yok. Salep yalnızca standart kütüphane ile çalışmayı hedefliyor.
Bu kütüphaneler İngilizce adlarıyla kullanılabilmeye devam eder.
