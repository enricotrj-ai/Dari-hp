# The City Traded for a Fruit — paket produksi

Video explainer 60 detik, 9:16 (1080×1920), gaya **Whimsical 3D Cinematic**, narasi English, untuk RoyalPiggy-ID.

## Isi paket

| File | Isi |
|---|---|
| `scenes.json` | Semua 8 scene: waktu, narasi, prompt gambar dan video, ID aset ElevenLabs, kata kunci layar, SFX |
| `assemble.py` | Skrip perakit: gambar + klip + voiceover + teks Bangers jadi satu MP4 |
| `overlays/` | 8 PNG transparan 1080×1920, teks kata kunci font Bangers |
| `Bangers-Regular.ttf` | Font Bangers (SIL Open Font License, boleh komersial) |
| `assets/` | **Kosong.** Isi dengan file dari ElevenLabs (lihat di bawah) |

## 1. Unduh aset dari ElevenLabs

Buka flow: https://elevenlabs.io/app/flows/whkJoQOB0gx4AH4TJgJr
Unduh lalu ganti namanya persis seperti ini, taruh di folder `assets/`:

| Simpan sebagai | Isi | ID generation ElevenLabs |
|---|---|---|
| `voiceover.mp3` | Voiceover Mason (pilih 1 take) | `QzEiGvrCrexpfh0cLDOX` atau `qCRdJ2P7IN2cJamLHzpD` |
| `scene1.mp4` | Klip Kling, hook buah pala | `bYmlKZXM8KtFEkJ8ao30` |
| `scene2.png` | Kebun pala 3D | `JBncIgljbhvtuJUteGLw` |
| `scene3.png` | Timbangan pala vs koin | `lsfQyQc5oXMXTOFAxrQc` |
| `scene4.png` | Diorama Banda, Run pilih Inggris | `BMIyYDaWu3B6RQX4jKyS` |
| `scene5.mp4` | Klip Kling, pengepungan Run | `QLazEDHS6ZG6IVwk30AK` |
| `scene6.png` | New Amsterdam ke New York | `XujeqLOJRfrSpHFqfmJg` |
| `scene7.png` | Perjanjian Breda pop-up | `sZ4oTVJOq3PZ4TT5JnPH` |
| `scene8.mp4` | Klip Kling, ending globe | `BKLiMfTV0Vc312uBSLdi` |
| `music.mp3` | (Opsional) musik latar bebas hak cipta | — |

Gambar diam bisa diganti klip video kapan saja: ubah `asset` dan `asset_type` scene itu di `scenes.json`.

## 2. Rakit video

```bash
pip install pillow        # ffmpeg juga harus terpasang
python3 assemble.py       # hasil: RunManhattan_final_9x16.mp4
```

- Waktu scene di `scenes.json` dibuat untuk 60 detik. Skrip otomatis meregangkannya mengikuti panjang voiceover asli. Pakai `--no-scale` untuk memakai waktu apa adanya.
- Gambar diam diberi gerakan kamera pelan (`motion`: `zoom_in`, `zoom_out`, `pan_up`, `zoom_in_left`).
- Klip Kling yang lebih pendek dari scene-nya diperlambat sampai 1,6×, lalu frame terakhirnya ditahan.
- Kata kunci Bangers muncul dengan efek pop di detik `keyword.at` tiap scene, selama `keyword.hold` detik. Geser angka ini kalau kurang pas dengan ucapan narator.
- Musik (kalau ada) diputar −20 dB di bawah suara dan memudar di 2 detik terakhir.

## Prompt untuk Claude Code

> Ini paket produksi video saya di folder ini. Baca README.md dan scenes.json. Aset sudah ada di assets/. Jalankan assemble.py, lalu cek hasilnya: apakah teks kata kunci muncul tepat saat kata itu diucapkan di voiceover? Kalau belum pas, sesuaikan keyword.at di scenes.json dan render ulang.

## Catatan konten

- Hook sengaja provokatif. Scene 8 meluruskan bahwa ini bukan tukar langsung, melainkan Perjanjian Breda 1667 (masing-masing pihak mempertahankan wilayah yang dikuasainya).
- Scene 5 menyangkut penaklukan Banda 1621 yang menelan banyak korban jiwa. Pertahankan nada serius dan tanpa visual kekerasan.
- Bendera yang dipakai versi abad ke-17: St George's Cross untuk Inggris, oranye-putih-biru untuk Belanda.
