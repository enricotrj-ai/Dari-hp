#!/usr/bin/env python3
"""Assemble the 30s tea explainer: narration timeline, scene retime, SFX, music, subtitles."""
import json, subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "audio")
OUT = os.path.join(ROOT, "render")
os.makedirs(OUT, exist_ok=True)
TEMPO = 1.23         # narration speed-up
GAP = 0.06           # gap between narration segments (s)
LEAD = 0.15          # silence before first word
TAIL = 0.75          # hold after last word

def run(cmd):
    subprocess.run(cmd, check=True)

def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode())

# ---------- narration segments (original take-1 times) ----------
words = [w for w in json.load(open(os.path.join(A, "words_take1.json")))["words"]
         if w["type"] == "word" and not w["text"].startswith("[") and not w["text"].endswith("]")]
SEG = [(0.00, 5.50), (5.60, 8.38), (8.38, 14.94), (14.94, 19.18),
       (19.18, 22.93), (22.93, 31.75), (31.75, dur(os.path.join(A, "narasi_take1.mp3")))]

seg_new = []           # (orig_start, orig_end, new_start)
t = LEAD
for s, e in SEG:
    seg_new.append((s, e, t))
    t += (e - s) / TEMPO + GAP
narr_end = t - GAP
TOTAL = round(narr_end + TAIL, 2)

def remap(x):
    for s, e, n in seg_new:
        if s - 1e-6 <= x <= e + 1e-6:
            return n + (x - s) / TEMPO
    raise ValueError(x)

for w in words:
    w["ns"], w["ne"] = remap(w["start"]), remap(min(w["end"], SEG[-1][1]))

# narration: cut, speed, place
parts, labels = [], []
for i, (s, e, n) in enumerate(seg_new):
    parts.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={TEMPO},adelay={int(n*1000)}:all=1[n{i}]")
    labels.append(f"[n{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + \
     f"amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11[out]"
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(A, "narasi_take1.mp3"), "-filter_complex", fc,
     "-map", "[out]", "-ar", "48000", "-ac", "2", os.path.join(OUT, "narasi_timeline.wav")])

# ---------- scene boundaries follow narration ----------
st = [n for _, _, n in seg_new]
cuts = [0.0, st[2] - 0.08, st[3] - 0.08, st[5] - 0.08, st[6] - 0.08, TOTAL]
clips = [("adegan1", "adegan1_raw.mp4"), ("adegan2", "adegan2_30fps.mp4"), ("adegan3", "adegan3_30fps.mp4"),
         ("adegan4", "adegan4_30fps.mp4"), ("adegan5", "adegan5_30fps.mp4")]
scene_files = []
for i, (d, f) in enumerate(clips):
    src = os.path.join(ROOT, d, f)
    target = cuts[i + 1] - cuts[i]
    factor = target / dur(src)
    o = os.path.join(OUT, f"s{i+1}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf",
         f"setpts={factor:.5f}*PTS,fps=30,scale=1080:1920,trim=duration={target:.3f},setsar=1",
         "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", o])
    scene_files.append((o, factor))
lst = os.path.join(OUT, "concat.txt")
open(lst, "w").write("".join(f"file '{o}'\n" for o, _ in scene_files))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
     os.path.join(OUT, "video_cut.mp4")])

def wt(text, after=0.0):
    """new start time of first word containing text, after a given time"""
    for w in words:
        if text.lower() in w["text"].lower() and w["ns"] >= after:
            return w["ns"]
    raise KeyError(text)

# ---------- SFX placement ----------
f4 = scene_files[3][1]
sfx = [
    ("sfx1_daun", 0.05, -6),
    ("sfx2_taiko", wt("kaisar") - 0.05, -7),
    ("sfx9_pop", cuts[1] - 0.25, -10),
    ("sfx3_uap", cuts[1] + 1.2, -12),
    ("sfx9_pop", cuts[2] - 0.25, -10),
    ("sfx4_bata", wt("bata") - 0.05, -7),
    ("sfx5_kapal", wt("Belanda") - 0.2, -11),
    ("sfx9_pop", cuts[3] - 0.25, -10),
    ("sfx6_tegang", cuts[3] + 0.05, -9),
    ("sfx7_segel", cuts[3] + 6.6 * f4, -5),
    ("sfx9_pop", cuts[4] - 0.25, -10),
    ("sfx8_es", cuts[4] + 1.6, -8),
    ("sfx9_pop", TOTAL - 1.5, -9),
]
ins, fl, lab = [], [], []
for i, (name, at, gain) in enumerate(sfx):
    ins += ["-i", os.path.join(A, name + ".mp3")]
    fl.append(f"[{i}:a]volume={gain}dB,adelay={int(max(at,0)*1000)}:all=1[x{i}]")
    lab.append(f"[x{i}]")
fc = ";".join(fl) + ";" + "".join(lab) + f"amix=inputs={len(lab)}:normalize=0,apad,atrim=0:{TOTAL}[out]"
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-ac", "2",
     os.path.join(OUT, "sfx_timeline.wav")])

# ---------- subtitles + on-screen text (ASS) ----------
def ts(x):
    x = max(x, 0); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

GOLD = "&H003CC8F5&"
KEY = {"kaisar", "uang", "mata-mata", "bata", "belanda", "eropa", "bangsawan", "gila", "fortune",
       "menyamar", "india", "manis", "tawar", "komentar", "like", "shen", "nong", "tibet"}
NUM = {"dua ribu tujuh ratus tiga puluh tujuh": "2737", "seribu delapan ratus empat puluh delapan": "1848"}

# group words into 2–3 word chunks, merging spelled-out years into digits
toks = []
i = 0
while i < len(words):
    joined = False
    for phrase, digit in NUM.items():
        n = len(phrase.split())
        cand = " ".join(w["text"].strip(",").lower() for w in words[i:i+n])
        if cand == phrase:
            toks.append({"text": digit + ("," if words[i+n-1]["text"].endswith(",") else ""),
                         "ns": words[i]["ns"], "ne": words[i+n-1]["ne"], "num": True})
            i += n; joined = True; break
    if not joined:
        toks.append(dict(words[i])); i += 1
toks = [dict(t, text=t["text"].replace("Sebelum", "SM") if False else t["text"]) for t in toks]

chunks, cur = [], []
for t in toks:
    cur.append(t)
    end_punct = t["text"][-1] in ",.!?:"
    if len(cur) >= 3 or end_punct:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def style_word(t):
    raw = t["text"]
    core = raw.strip(",.!?:").lower()
    txt = raw.upper()
    if core in KEY or t.get("num"):
        return "{\\c" + GOLD + "}" + txt + "{\\c&H00FFFFFF&}"
    return txt

ev = []
for k, c in enumerate(chunks):
    start = c[0]["ns"] - 0.05
    end = chunks[k+1][0]["ns"] - 0.05 if k + 1 < len(chunks) else c[-1]["ne"] + 0.4
    end = min(end, c[-1]["ne"] + 0.6)
    text = " ".join(style_word(t) for t in c)
    ev.append(f"Dialogue: 1,{ts(start)},{ts(end)},Sub,,0,0,0,,{{\\fad(40,40)\\t(0,90,\\fscx108\\fscy108)\\t(90,180,\\fscx100\\fscy100)}}{text}")

def card(text, a, b, style="Card", extra=""):
    ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},{style},,0,0,0,,{{\\fad(120,120){extra}}}{text}")

pop = "\\fscx70\\fscy70\\t(0,160,\\fscx100\\fscy100)"
# hook stack builds word by word
h1, h2, h3 = wt("kaisar"), wt("uang"), wt("mata-mata")
card("DIJAGA KAISAR", h1, cuts[1], extra=pop + "\\pos(540,250)")
card("JADI UANG", h2, cuts[1], extra=pop + "\\pos(540,370)")
card("{\\c" + GOLD + "}DICURI MATA-MATA?!", h3, cuts[1], extra=pop + "\\pos(540,490)")
card("±2737 SM · LEGENDA", cuts[1] + 0.2, cuts[2] - 0.1, extra=pop + "\\pos(540,300)")
card("BATA TEH = UANG", wt("bata") - 0.1, wt("Lalu") - 0.1, extra=pop + "\\pos(540,300)")
card("ABAD KE-17 → EROPA", wt("Lalu"), cuts[3] - 0.1, extra=pop + "\\pos(540,300)")
card("{\\c" + GOLD + "}1848 · SPIONASE TEH", wt("tahun"), cuts[3] + 5.0 * f4, extra=pop + "\\pos(540,300)")
card("TIONGKOK → INDIA", cuts[3] + 5.0 * f4, cuts[4] - 0.1, extra=pop + "\\pos(540,300)")
card("TIM {\\c" + GOLD + "}MANIS{\\c&H00FFFFFF&} ATAU {\\c" + GOLD + "}TAWAR{\\c&H00FFFFFF&}?", cuts[4] + 0.1, TOTAL,
     extra=pop + "\\pos(540,260)")
card("TULIS DI KOMENTAR  ·  LIKE ♥", wt("Tulis") - 0.1, TOTAL, style="Small", extra=pop + "\\pos(540,385)")
card("RoyalPiggy-ID", TOTAL - 1.5, TOTAL, style="Brand", extra=pop + "\\pos(540,1700)")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,74,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,1,0,1,6,3,2,70,70,560,1
Style: Card,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00141E28,&HA0000000,-1,0,0,0,100,100,2,0,1,7,4,5,40,40,0,1
Style: Small,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00141E28,&HA0000000,-1,0,0,0,100,100,2,0,1,5,3,5,40,40,0,1
Style: Brand,Inter ExtraBold,64,&H003CC8F5,&H00FFFFFF,&H00141E28,&HA0000000,-1,0,0,0,100,100,3,0,1,6,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(os.path.join(OUT, "teks.ass"), "w").write(ass)

# ---------- final mix ----------
final = os.path.join(ROOT, "Teh_Kaisar_hingga_Rakyat_30s_1080x1920_30fps.mp4")
fc = (f"[2:a]atrim=0:{TOTAL},apad,atrim=0:{TOTAL},volume=-17dB,afade=t=in:d=0.4,afade=t=out:st={TOTAL-1.2}:d=1.2[mus];"
      f"[1:a]asplit=2[nar][key];"
      f"[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
      f"[nar][duck][3:a]amix=inputs=3:normalize=0,alimiter=limit=0.95[a];"
      f"[0:v]ass={os.path.join(OUT, 'teks.ass')},vignette=PI/6,format=yuv420p[v]")
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "video_cut.mp4"),
     "-i", os.path.join(OUT, "narasi_timeline.wav"), "-i", os.path.join(A, "musik.mp3"),
     "-i", os.path.join(OUT, "sfx_timeline.wav"), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
     "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", str(TOTAL), final])

print("TOTAL", TOTAL, "cuts", [round(c, 2) for c in cuts])
print("final", final)
