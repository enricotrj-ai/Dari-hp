---
name: piggy1
description: Gaya "piggy1" untuk video explainer sejarah 9:16 (TikTok/Reels/Shorts) ±30 detik yang berputar mulus (seamless loop) — visual Cinematic Historical Paper Diorama + 3D Motion Graphics, narator pria hangat (ElevenLabs "Janu – Calm Narrator"), hook mengejutkan, ajakan masuk cerita, twist, CTA komentar & like yang diucapkan, dan kalimat penutup menggantung yang menyambung ke kalimat pembuka. Gunakan saat user menyebut "piggy1", "gaya piggy1", atau meminta video dengan gaya yang sama seperti "Teh Part 2".
---

# piggy1 — gaya explainer sejarah loop (paper diorama)

Referensi asli: `teh-explainer/part2/` (video `Teh_Part2_Loop_30s_1080x1920_30fps.mp4`, naskah `naskah_part2.md`, skrip `build_part2.py`). Semua komunikasi dengan user dalam Bahasa Indonesia; semua prompt gambar/video dalam bahasa Inggris.

## 1. Alur kerja (wajib diikuti)
1. Tulis naskah dulu (5 adegan, tabel narasi + storyboard + catatan fakta) di `<topik>/naskah.md`, commit & push.
2. Buat **gambar kunci loop** (frame pertama adegan 1 = frame terakhir adegan 5).
3. Kerjakan **adegan 1 saja**, kirim **3 potret dari detik berbeda**, tunggu persetujuan.
4. Setelah disetujui: adegan 2–5, kirim 3 potret per adegan. Laporkan jujur setiap kekeliruan sejarah yang terlihat (anakronisme, tokoh salah etnis, tulisan acak) dan tawarkan buat ulang beserta biaya kreditnya.
5. **Suara baru dibuat setelah semua gambar disetujui.**
6. Rakit dengan skrip build (template: `build_template.py`), cek sambungan loop, kirim video final + klip cek sambungan (3 detik akhir → 3,5 detik awal).
7. Selalu sebut biaya kredit yang terpakai. Commit & push setiap tahap.

## 2. Tools & model
- Video: **Gemini Omni Flash 1.2** (`gemini-omni-1.2-flash`) lewat ElevenLabs Flows, `aspect_ratio 9:16`, `resolution 1080p`, durasi 5/9/8/5 detik (adegan 1: 5 s lalu dipercepat ke ±3–6 s sesuai narasi). Output 24 fps → dikonversi ke **30 fps**. (Higgsfield juga punya Omni Flash, tapi cek saldo dulu; sesi asli saldonya 0.)
- Gambar kunci: `gemini-3-pro-image`, 9:16, 2K, `generations_count 1`.
- Satu flow ElevenLabs per video; semua node di flow yang sama.
- Adegan 1: sambungkan gambar kunci ke port **`start_frame`** (bukan `images`).
- Adegan 5: model **wajib punya `start_frame` bila `end_frame` dipasang** → buat gambar awal adegan 5 dulu (pakai gambar kunci sebagai referensi `images`), lalu `start_frame` = gambar awal, `end_frame` = gambar kunci.
- Unduh hasil: host `elevenlabsusercontent.com` harus diizinkan di environment jaringan.

## 3. Gaya visual (tempel di setiap prompt video)
```
Cinematic historical paper diorama with 3D motion graphics, vertical frame, one continuous shot.
<SUBJEK & AKSI ADEGAN>. Layered textured paper like a pop-up book, visible paper fibres, cut edges,
soft drop shadows, parallax depth, tilt-shift depth of field, warm volumetric light,
teal, jade, gold and crimson palette, film grain, premium documentary look, not cartoonish.
No text, no letters, no logos, no dialogue, no voice; only <SFX ambien adegan>.
```
- Gambar kunci loop: objek ikonik sederhana di tengah (contoh: gelas es teh di meja warung kertas), latar diorama kertas, **sepertiga atas lega untuk teks**.
- Adegan 1 (hook): mulai tepat dari gambar kunci, kamera push-in / menyelam ke objek lalu bertransformasi ke dunia sejarahnya.
- Adegan 5: dimulai dari close-up, kamera mundur dan **mendarat persis di komposisi gambar kunci** lalu diam.
- Hindari anakronisme secara eksplisit di prompt (mis. "no skyscrapers", busana sesuai abad). Tema kelam (kerja paksa, perang): "sombre and dignified mood, no violence shown".
- Tokoh nyata: tulis etnis/ciri yang benar secara eksplisit ("clearly European, disguised in…"), tanpa close-up wajah realistis.

## 4. Struktur naskah & pembawaan narasi
Target ±72–80 kata, 5 adegan:
| Adegan | Fungsi | Pola kalimat |
|---|---|---|
| 1 Hook | 2–3 klaim mengejutkan | "*<objek sehari-hari>* ini ternyata lahir dari *<hal mengejutkan 1>*… dan *<hal mengejutkan 2>*!" (huruf kecil di awal — lanjutan dari kalimat penutup) |
| 2 Konteks | ajakan masuk cerita + latar | "Kok bisa? …" lalu siapa/kapan/di mana |
| 3 Penjelasan | fakta inti | 1–2 kalimat padat |
| 4 Twist | fakta paling tak terduga | "Dan yang paling tak terduga: konon tahun …" (pakai "konon/menurut legenda" untuk cerita populer) |
| 5 Payoff → loop | CTA diucapkan + kalimat menggantung | "Kalau baru tahu, tulis '<kata>' di komentar, dan jangan lupa like! Dari <A>, <B>, sampai <C>, semuanya bermuara di…" → kembali ke kalimat hook |

Aturan pembawaan:
- Suara: **ElevenLabs `eleven_v4`, voice_id `TIXYCOMzK2Vw9OZovSLs` (Janu – Calm Narrator)**, 2 take, pakai take terbaik.
- Tag arahan per kalimat: `[intriguing]` hook, `[curious]` "Kok bisa?", `[warm]` konteks, `[serious]` tema kelam, `[playful]` twist, `[friendly, upbeat]` CTA, `[warm, slowing down]` kalimat menggantung.
- Tulis angka & tahun sebagai kata ("seribu sembilan ratus delapan", "ke-sembilan belas") agar dibaca benar; di subtitle tampil sebagai angka (1908, KE-19).
- Kalimat CTA boleh direkam terpisah lalu disisipkan **sebelum** kalimat menggantung.
- **Jangan** mengucapkan atau menampilkan nama merek/akun (tanpa "RoyalPiggy-ID").
- Tempo akhir: atempo **1,2–1,22×**, jeda antar kalimat 0,06 s, LEAD 0,05 s, TAIL 0,30 s, loudness −14 LUFS.

## 5. Audio
- Musik: `eleven_music_v2_5`, instrumental, ±32 s, prompt "Seamless looping … no intro, no fade, no final ending chord", gamelan + guzheng + strings lembut + hand-drum 90 BPM. Di build: digandakan dengan crossfade lalu ekornya di-crossfade ke awal (loop tanpa putus). Musik −17 dB + sidechain ducking di bawah narasi.
- SFX (`eleven_text_to_sound_v3`, 1–5 s, `generations_count 1`): es berdenting di awal & di adegan 5, "whoosh" masuk objek, ambien tiap lokasi, taiko di kata kunci hook, "pop" kertas di tiap pergantian adegan, efek "aha" di momen twist. Jangan ada SFX yang melintasi akhir video.

## 6. Teks layar & subtitle (ASS, font Inter ExtraBold)
- Subtitle 2–3 kata, putih outline gelap, `MarginV 560`; kata kunci & angka **emas** (`&H003CC8F5&`).
- Subtitle pertama muncul tepat di frame 0 tanpa fade; subtitle terakhir bertahan sampai frame terakhir → di sambungan loop teks langsung berlanjut.
- Kartu judul di atas (y≈250–370): hook dua baris, label tahun/tempat per adegan, CTA ("TULIS '<KATA>' DI KOMENTAR!", "JANGAN LUPA LIKE ♥") muncul sesuai suara dan hilang 0,45 s sebelum akhir.
- Jangan pakai emoji di ASS (font tidak punya glyph); ♥ aman.
- Filter tag arahan suara dari transkrip, termasuk kata di dalam tag multi-kata (`[warm, slowing down]`).

## 7. Perakitan loop (lihat `build_template.py`)
- Transkrip narasi (`eleven_scribe_v1`, gratis) → timing kata → potong per kalimat, percepat, susun ulang.
- Batas adegan mengikuti awal kalimat; klip di-retime (`setpts`) agar pas. Crop/zoom ringan untuk menyembunyikan tulisan acak.
- 0,35 s terakhir: frame 0 di-overlay dengan fade-in alpha → frame akhir ≈ frame awal (target SSIM ≥ 0,9).
- Output: H.264 High, CRF 17, 1080×1920, 30 fps, AAC 192 kbps, `+faststart`; file perantara di `render/` (di-gitignore).

## 8. Paket unggahan
Judul berbentuk pertanyaan mengejutkan + emoji, deskripsi 2 kalimat + ajakan komentar/like, komentar yang di-pin dengan dua pilihan emoji, 8–10 hashtag (#sejarah #faktaunik #edukasi #fyp #shorts + topik). Sertakan catatan fakta & sumber keraguan di naskah.

## 9. Thumbnail gaya kolase (disukai user)
Template: `thumbnail_template.py` (font Bangers & Anton ada di `fonts/`, OFL). Jalankan: `python3 thumbnail_template.py <folder berisi pan_*.png dan fonts/>`.
- 1080×1920, latar gambar kunci yang diburamkan & digelapkan.
- Strip kuning sobek di atas berisi teaser hitam (Bangers ±76 pt).
- 2–3 panel frame video dengan tepi kertas sobek, bingkai kertas putih, bayangan, sedikit miring; warna & kontras dinaikkan.
- Headline raksasa kuning (Bangers ±250 pt) berstroke hitam tebal + bayangan; panah merah berstroke hitam ke objek utama.
- Stiker label kotak (merah/kuning/putih) miring berisi tahun/fakta.
- Banner merah sobek di bawah: pertanyaan dua baris (putih + kuning) + stiker putih kecil. Klaim yang masih "konon" diberi tanda tanya.
