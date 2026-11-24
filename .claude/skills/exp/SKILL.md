---
name: exp
description: Gaya "Exp" — Curiosity-Driven Visual Explainer untuk video sains/fenomena sehari-hari 9:16 (TikTok/Reels/Shorts) ±60–110 detik. Hook kontras yang melawan logika, misteri/cerita lokal sebagai taruhan, "kita cek pakai sains", patahkan intuisi dengan skala, mekanisme lewat analogi berantai, "tapi itu belum cukup" + twist + payoff misteri, ringkasan satu napas, tips praktis, CTA "ngaku deh… tulis di komentar". Visual: peta satelit 3D bergantian dengan ilustrasi flat 2D + karakter chibi, teks dua baris berkode warna. Gunakan saat user menyebut "exp", "gaya exp", "curiosity-driven explainer", atau minta video "kenapa …" dengan gaya seperti video "Kenapa makin tinggi makin dingin padahal makin dekat matahari".
---

# Exp — Curiosity-Driven Visual Explainer

Referensi asli: video "Kenapa Makin Tinggi Makin Dingin Padahal Makin Dekat Matahari" (Dieng, 1:50, 720×1280). Contoh frame: `contoh_visual.jpg`. Semua komunikasi dengan user dalam Bahasa Indonesia; prompt gambar/video dalam bahasa Inggris.

**Inti gaya:** penonton tidak diajari — mereka diberi teka-teki lalu diajak menemukan jawabannya. Jawaban selalu **ditahan** dan dibuka bertahap; setiap klaim **dibuktikan** dengan visual.

## 1. Alur kerja
1. Minta / pilih topik berbentuk **paradoks sehari-hari** ("kenapa X padahal Y?"). Cari: (a) kontras dua tempat/situasi, (b) mitos atau cerita lokal yang terkait, (c) angka konkret, (d) twist yang berlawanan dengan dugaan.
2. Tulis naskah di `<topik>/naskah.md`: tabel per potongan (waktu, narasi, teks layar baris 1, teks layar baris 2 + warna, visual) + catatan fakta & sumber. Kirim ke user, tunggu persetujuan.
3. Baru lanjut ke visual/suara/render sesuai tools yang dipilih user. Commit & push setiap tahap.
4. Cek fakta setiap angka; laporkan jujur jika ada penyederhanaan (mis. "±6°C/km" adalah laju rata-rata).

## 2. Kerangka 7 babak (proporsi untuk ±110 dtk)

| # | Babak | Porsi | Isi wajib |
|---|---|---|---|
| 1 | Hook kontras | 5% (0–5 dtk) | Dua fakta yang diadu + pertanyaan yang melawan logika |
| 2 | Taruhan | 7% | Mitos/kata orang lokal + kerugian nyata ("semalam bisa matiin kentang satu ladang"). **Buka open loop** yang baru dijawab di babak 6 |
| 3 | Ajakan | 4% | "Kita cek pakai sains, mulai dari ___." |
| 4 | Patahkan intuisi | 10% | Angka besar → diterjemahkan ke benda sehari-hari → celetukan ("Mendekat, atau cuma gaya?") |
| 5 | Mekanisme | 30% | Analogi berantai, satu konsep = satu analogi = satu visual. Perkenalkan **metafora kunci** ("kompornya bumi", "jaketnya bumi"). Berakhir di angka konkret |
| 6 | Lapisan kedua + twist + payoff | 27% | "Tapi itu belum cukup buat ___." → lapisan baru → "Yang paling ___ justru ___" → jawab misteri babak 2 sesingkat mungkin ("Bukan racun. Itu es.") |
| 7 | Ringkasan + tips + CTA | 17% | "Bukan ___. ___, ___." (pakai ulang metafora kunci) → tips praktis → "Ngaku deh… ___? Tulis di komentar." (tahan teks CTA ±6 dtk) |

Versi pendek (±60 dtk): pertahankan semua babak, potong jumlah analogi di babak 5 menjadi 2.

## 3. Pola kalimat
1. `Di ___ ___, di ___ ___. Padahal ___?`
2. `Kata ___: "___". ___ bisa ___.`
3. `Kita cek pakai sains, mulai dari ___.`
4. `___ itu ___ [angka]. ___ cuma ___ [angka], kayak ___.` + `___, atau cuma ___?`
5. `___ = ___-nya bumi.`
6. `Tapi itu belum cukup buat ___.`
7. `Yang paling ___ justru ___.` / `___ sambil ___.` (dua kondisi kontras yang lucu)
8. `___ bukan ___. Itu ___.`
9. `Bukan ___. ___, ___.`
10. `Ngaku deh… ___? Tulis di komentar.`

## 4. Aturan bahasa
- Lisan santai Jakarta-an: *matiin, manasin, ikutin, kelamaan, cuma, kayak, ngaku deh*.
- Potongan 3–7 kata; tiap ide = premis (baris 1) + punchline (baris 2).
- Celetukan/humor tiap ±20 dtk. Pertanyaan "kok bisa?" baru tiap ±15–20 dtk.
- Jangan pernah buka jawaban di 20% awal. Metafora kunci dipakai ulang sampai penutup.
- Angka selalu konkret dan dibandingkan dengan sesuatu yang bisa dibayangkan.

## 5. Aturan visual
- Format 9:16. Teks di tengah-atas (±20–25% dari atas), font sans tebal rounded, putih dengan bayangan halus.
- Teks dua baris: baris 1 putih (premis) muncul duluan, baris 2 menyusul (pop/scale-in) dengan warna:
  - **Kuning** (#FFD84D-ish) = kata kunci / angka / jawaban
  - **Merah koral** (#FF5A5A-ish) = panas / bahaya
  - **Biru muda** (#7FDBFF-ish) = dingin / es
- Dua dunia visual bergantian:
  - **Peta satelit 3D** (lokasi nyata, kamera terbang/miring, label lokasi putih, termometer & angka suhu) untuk konteks tempat.
  - **Ilustrasi flat 2D** (langit gradasi, malam berbintang, matahari bulat dengan glow, lanskap sederhana) untuk konsep.
- Karakter chibi sederhana (kepala bulat, badan kecil): penjelajah bertopi, petani bercaping, ilmuwan berjas. Ekspresi kecil (kaget, menggigil "BRRR!").
- Setiap analogi punya visual literal (kaca pembesar "setipis rambut", api unggun + garis 1 km, kotak "UDARA" ditembus sinar, tanda X merah, panah naik, sinar UV ungu).
- Watermark kanal tipis di tengah atas. Transisi: cut cepat atau wipe diagonal.

## 6. Template naskah
```
[HOOK]      Di ___ ___, di ___ ___. Padahal ___?
[TARUHAN]   Kata ___: "___". Bisa ___ dalam ___.
[AJAKAN]    Kita cek pakai sains, mulai dari ___.
[PATAHKAN]  ___ itu ___ [angka]. ___ cuma ___ [angka], kayak ___.
            ___, atau cuma gaya?
[MEKANISME] ___ itu kayak ___. ___ = ___-nya bumi. Jadi tiap ___, ___ [angka].
[TWIST]     Tapi itu belum cukup buat ___. ___
            Yang paling ___ justru ___. ___ sambil ___.
            ___ bukan ___. Itu ___.
[PENUTUP]   Bukan ___. ___, ___.
            [Tips]: ___ dan ___.
            Ngaku deh… ___? Tulis di komentar.
```

## 7. Checklist sebelum kirim naskah
- [ ] Hook berupa kontras + pertanyaan "padahal…?" dalam ≤5 dtk
- [ ] Ada misteri/mitos yang dibuka di awal dan dijawab di babak 6
- [ ] Minimal 1 perbandingan skala yang absurd tapi akurat
- [ ] Metafora kunci muncul di babak 5, 6, dan 7
- [ ] Ada "tapi itu belum cukup" + twist "justru"
- [ ] Penutup satu napas + tips + CTA "ngaku deh"
- [ ] Semua angka sudah dicek
