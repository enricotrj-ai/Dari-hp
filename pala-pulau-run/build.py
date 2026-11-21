#!/usr/bin/env python3
"""Rakit video "Pala & Pulau Run" 9:16, 30 fps.

Aset dari ElevenLabs Flow (img/, vid/, audio/narasi_a.mp3).
Teks layar: kata kunci saja (font Bangers), narasi tidak ditampilkan.
Jalankan dari folder ini:  python3 build.py
"""
import os, subprocess

FPS = 30
W, H = 1080, 1920
NARASI = "audio/narasi_a.mp3"
TAIL = 0.7  # detik diam setelah kata terakhir (62.24 s)

# Scene 1 memakai gambar diam: klip Kling vid/s1.mp4 memunculkan batang kaca aneh mulai ±1.7 s.
# (awal, akhir, sumber, teks ASS, muncul_pada) — batas = awal paragraf narasi
Y = r"{\c&H00D7FF&}"   # kuning (BGR)
Wt = r"{\c&HFFFFFF&}"  # putih
END = 62.24 + TAIL
SCENES = [
    (0.00,   6.72,  "img/s1.png", Y + "FOR THIS?",   2.36),
    (6.72,  15.067, "img/s2.png", Y + "NUTMEG",      7.36),
    (15.067, 22.907, "img/s3.png", Y + "A FORTUNE",  20.40),  # "Whoever owned Banda named the price"
    (22.907, 28.80, "img/s4.png", Wt + "PULAU RUN",  26.56),
    (28.80, 40.96,  "vid/s5.mp4", Wt + "UNDER SIEGE", 32.64),
    (40.96, 48.267, "img/s6.png", Y + "1664",        43.24),
    (48.267, 55.92, "img/s7.png", Y + "1667",        48.44),
    (55.92, END,    "vid/s8.mp4", Wt + r"RUN OR\N" + Y + "MANHATTAN?", 59.76),
]

os.makedirs("render", exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def frames(t):
    return round(t * FPS)


def clip_scene(i, a, b, src):
    out = f"render/scene{i}.mp4"
    n = frames(b) - frames(a)
    dur = n / FPS
    if src.endswith(".png"):
        # Ken Burns pelan: zoom 1.00 -> 1.10, arah bergantian
        up = 4  # render besar dulu agar zoompan tidak bergetar
        z = f"1+0.10*on/{n}"
        if i % 2:
            x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        else:
            x, y = "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(0.35+0.3*on/{n})"
        vf = (f"scale={W*up}:{H*up}:flags=lanczos,"
              f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
              "format=yuv420p")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", src, "-vf", vf,
             "-frames:v", str(n), "-c:v", "libx264", "-crf", "16", "-preset", "medium", out])
    else:
        # klip Kling 5.04 s @24 fps
        src_d = 5.0
        if dur <= src_d * 1.5:
            # cukup diperlambat
            vf = f"setpts={dur/src_d:.5f}*PTS,fps={FPS},scale={W}:{H},format=yuv420p"
            run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf,
                 "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "16", out])
        else:
            # terlalu panjang: maju lalu mundur (ping-pong), masing-masing diperlambat
            half = dur / 2
            fc = (f"[0:v]trim=0:{src_d},setpts=PTS-STARTPTS,split[f][r0];"
                  f"[r0]reverse[r];[f][r]concat=n=2:v=1,"
                  f"setpts={half/src_d:.5f}*PTS,fps={FPS},scale={W}:{H},format=yuv420p[v]")
            run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc,
                 "-map", "[v]", "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "16", out])
    return out


def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass():
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kunci,Bangers,190,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,4,0,1,11,9,8,60,60,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, (a, b, _, txt, t0) in enumerate(SCENES, 1):
        size = 150 if i == 8 else 190
        # pop-in: 0 -> 118% -> 100%, sedikit miring
        anim = (rf"{{\fs{size}\fscx0\fscy0\frz-3"
                rf"\t(0,140,\fscx118\fscy118)\t(140,260,\fscx100\fscy100)}}")
        # teks hilang tepat di pergantian scene (tanpa fade)
        mv = 140 if i == 7 else 0  # scene 7: naikkan agar tidak menutupi segel lilin
        lines.append(f"Dialogue: 0,{ts(t0)},{ts(b - 0.005)},Kunci,,0,0,{mv},,{anim}{txt}")
    with open("render/teks.ass", "w") as f:
        f.write(hdr + "\n".join(lines) + "\n")


def main():
    parts = [clip_scene(i, a, b, s) for i, (a, b, s, _, _) in enumerate(SCENES, 1)]
    with open("render/list.txt", "w") as f:
        f.writelines(f"file '{os.path.basename(p)}'\n" for p in parts)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "render/list.txt",
         "-c", "copy", "render/gambar.mp4"])
    write_ass()
    total = frames(END) / FPS
    out = "Pala_Pulau_Run_Manhattan_1080x1920_30fps.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", "render/gambar.mp4", "-i", NARASI,
         "-filter_complex",
         "[0:v]subtitles=render/teks.ass:fontsdir=fonts[v];"
         f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,apad,atrim=0:{total:.3f}[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", out])
    print("selesai:", out)


if __name__ == "__main__":
    main()
