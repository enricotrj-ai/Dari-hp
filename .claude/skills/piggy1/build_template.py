#!/usr/bin/env python3
"""Assemble Part 2 as a seamless loop: end frame/narration/music flow back into the start."""
import json, subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "audio")
OUT = os.path.join(ROOT, "render")
os.makedirs(OUT, exist_ok=True)
TEMPO = 1.22
GAP = 0.06
LEAD = 0.05     # tiny: start word follows the last word of the previous loop
TAIL = 0.30     # "...bermuara di" -> wrap -> "segelas es teh..."
XF = 0.35       # visual blend of the last frames into frame 0

def run(cmd):
    subprocess.run(cmd, check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]).decode())

SRC = {"n": (os.path.join(A, "narasi_take1.mp3"), "words_take1.json"),
       "c": (os.path.join(A, "cta_take1.mp3"), "words_cta_take1.json")}
NARR = SRC["n"][0]
def load(key):
    out, inside = [], False
    for w in json.load(open(os.path.join(A, SRC[key][1])))["words"]:
        if w["type"] != "word":
            continue
        txt = w["text"]
        if txt.startswith("["):
            inside = not txt.endswith("]")
            continue
        if inside:
            inside = not txt.endswith("]")
            continue
        out.append(dict(w, src=key))
    return out
# segments: (source, start, end). CTA sits before the hanging loop line.
SEG = [("n", 0.12, 6.30), ("n", 6.42, 7.30), ("n", 7.45, 12.76), ("n", 12.90, 18.60), ("n", 18.60, 30.04),
       ("c", 0.0, 4.22), ("n", 30.04, dur(NARR))]

seg_new, t = [], LEAD
for k, s, e in SEG:
    seg_new.append((k, s, e, t)); t += (e - s) / TEMPO + GAP
TOTAL = round(t - GAP + TAIL, 2)

def remap(k, x):
    cand = [z for z in seg_new if z[0] == k]
    for _, s, e, n in cand:
        if s - 1e-6 <= x <= e + 1e-6:
            return n + (x - s) / TEMPO
    best = min(cand, key=lambda z: min(abs(x - z[1]), abs(x - z[2])))
    return best[3] + (min(max(x, best[1]), best[2]) - best[1]) / TEMPO
words = []
for k in ("n", "c"):
    for w in load(k):
        w["ns"], w["ne"] = remap(k, w["start"]), remap(k, w["end"])
        words.append(w)
words.sort(key=lambda w: w["ns"])

parts, labels = [], []
for i, (k, s, e, n) in enumerate(seg_new):
    idx = 0 if k == "n" else 1
    parts.append(f"[{idx}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={TEMPO},afade=t=out:st={max((e-s)/TEMPO-0.04,0):.3f}:d=0.04,adelay={int(n*1000)}:all=1[n{i}]")
    labels.append(f"[n{i}]")
run(["ffmpeg", "-v", "error", "-y", "-i", NARR, "-i", SRC["c"][0], "-filter_complex",
     ";".join(parts) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", os.path.join(OUT, "narasi_timeline.wav")])

# ---------- scenes ----------
st = [n for _, _, _, n in seg_new]
cuts = [0.0, st[2] - 0.08, st[3] - 0.08, st[4] - 0.08, st[5] + 1.9, TOTAL]
clips = ["adegan1/adegan1_raw.mp4", "adegan2/adegan2_30fps.mp4", "adegan3/adegan3_30fps.mp4",
         "adegan4/adegan4_30fps.mp4", "adegan5/adegan5_30fps.mp4"]
factors, files = [], []
for i, c in enumerate(clips):
    src = os.path.join(ROOT, c); target = cuts[i+1] - cuts[i]; f = target / dur(src)
    o = os.path.join(OUT, f"s{i+1}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf",
         f"setpts={f:.5f}*PTS,fps=30," + ("scale=1220:2168,crop=1080:1920:70:248," if i == 3 else "scale=1080:1920,") + f"trim=duration={target:.3f},setsar=1",
         "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", o])
    factors.append(f); files.append(o)
open(os.path.join(OUT, "concat.txt"), "w").write("".join(f"file '{o}'\n" for o in files))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "concat.txt"),
     "-c", "copy", os.path.join(OUT, "video_cut.mp4")])
# frame 0 of the whole video, used to blend the ending back into the start
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "video_cut.mp4"), "-frames:v", "1",
     os.path.join(OUT, "frame0.png")])

def wt(text, after=0.0):
    for w in words:
        if text.lower() in w["text"].lower() and w["ns"] >= after:
            return w["ns"]
    raise KeyError(text)

# ---------- SFX ----------
f3, f4 = factors[2], factors[3]
sfx = [
    ("sfx8_es", 0.0, -9),
    ("sfx_selam", 1.0 * factors[0], -8),
    ("sfx2_taiko", wt("tanam") - 0.05, -9),
    ("sfx9_pop", cuts[1] - 0.25, -11),
    ("sfx_pelabuhan", cuts[1] + 0.05, -12),
    ("sfx9_pop", cuts[2] - 0.25, -11),
    ("sfx_kebun", cuts[2] + 0.05, -13),
    ("sfx5_kapal", wt("dikapalkan") - 0.2, -13),
    ("sfx9_pop", cuts[3] - 0.25, -11),
    ("sfx_mesintik", cuts[3] + 0.2, -12),
    ("sfx_plop", wt("Lahirlah") - 0.35, -7),
    ("sfx9_pop", cuts[4] - 0.25, -11),
    ("sfx8_es", cuts[4] + 1.0, -9),
]
ins, fl, lab = [], [], []
for i, (n, at, g) in enumerate(sfx):
    ins += ["-i", os.path.join(A, n + ".mp3")]
    fl.append(f"[{i}:a]volume={g}dB,adelay={int(max(at,0)*1000)}:all=1[x{i}]"); lab.append(f"[x{i}]")
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
     ";".join(fl) + ";" + "".join(lab) + f"amix=inputs={len(lab)}:normalize=0,apad,atrim=0:{TOTAL}[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", os.path.join(OUT, "sfx_timeline.wav")])

# ---------- music loop: output wraps to its own start ----------
# A = m[0.5 : T+0.5], crossfaded at the end into B = m[0 : 0.5]; after wrap playback resumes at m[0.5].
M0 = os.path.join(A, "musik_loop.mp3"); X = 0.5
M = os.path.join(OUT, "musik_2x.wav")   # music doubled with a crossfade so it covers any length
run(["ffmpeg", "-v", "error", "-y", "-i", M0, "-i", M0, "-filter_complex", "[0:a][1:a]acrossfade=d=1.5:c1=tri:c2=tri[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", M])
run(["ffmpeg", "-v", "error", "-y", "-i", M, "-i", M, "-filter_complex",
     f"[0:a]atrim={X}:{TOTAL+X},asetpts=PTS-STARTPTS[a];[1:a]atrim=0:{X},asetpts=PTS-STARTPTS[b];"
     f"[a][b]acrossfade=d={X}:c1=tri:c2=tri,atrim=0:{TOTAL}[o]",
     "-map", "[o]", "-ar", "48000", "-ac", "2", os.path.join(OUT, "musik_timeline.wav")])

# ---------- subtitles & cards ----------
def ts(x):
    x = max(x, 0); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
GOLD = "&H003CC8F5&"; WHITE = "{\\c&H00FFFFFF&}"
KEY = {"komentar", "like", "\"teh\"", "tanam", "paksa", "paksa…", "kesalahan", "belanda", "tiongkok", "jawa", "petani", "dunia", "new", "york",
       "sutra", "celup", "kebun", "kapal", "kantong", "warung"}
NUM = {"ke-sembilan belas": "KE-19", "seribu sembilan ratus delapan": "1908"}
toks, i = [], 0
while i < len(words):
    hit = False
    for ph, dg in NUM.items():
        n = len(ph.split()); cand = " ".join(w["text"].strip(",").lower() for w in words[i:i+n])
        if cand == ph:
            toks.append({"text": dg + ("," if words[i+n-1]["text"].endswith(",") else ""), "ns": words[i]["ns"],
                         "ne": words[i+n-1]["ne"], "num": True}); i += n; hit = True; break
    if not hit:
        toks.append(dict(words[i])); i += 1
chunks, cur = [], []
for tk in toks:
    cur.append(tk)
    if len(cur) >= 3 or tk["text"][-1] in ",.!?:…":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def sw(tk):
    core = tk["text"].strip(",.!?:…").lower()
    txt = tk["text"].upper()
    return ("{\\c" + GOLD + "}" + txt + WHITE) if (core in KEY or tk.get("num")) else txt

ev = []
for k, c in enumerate(chunks):
    a = 0.0 if k == 0 else c[0]["ns"] - 0.05
    b = chunks[k+1][0]["ns"] - 0.05 if k + 1 < len(chunks) else TOTAL - 0.02
    b = min(b, c[-1]["ne"] + 0.6) if k + 1 < len(chunks) else b
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad({0 if k == 0 else 40},40)" + ("" if k == 0 else "\\t(0,90,\\fscx108\\fscy108)\\t(90,180,\\fscx100\\fscy100)") + "}" +
              " ".join(sw(x) for x in c))

def card(text, a, b, y, style="Card"):
    ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},{style},,0,0,0,,{{\\fad(120,120)\\fscx70\\fscy70\\t(0,160,\\fscx100\\fscy100)\\pos(540,{y})}}{text}")

card("LAHIR DARI TANAM PAKSA", wt("tanam"), cuts[1], 250)
card("{\\c" + GOLD + "}& SEBUAH KESALAHAN?!", wt("kesalahan"), cuts[1], 370)
card("ABAD KE-19 · TIONGKOK → JAWA", wt("Awal"), cuts[2] - 0.1, 300)
card("TANAM PAKSA (1830–1870)", cuts[2] + 0.1, wt("dikapalkan") - 0.1, 300)
card("TEH JAWA → DUNIA", wt("dikapalkan"), cuts[3] - 0.1, 300)
card("{\\c" + GOLD + "}1908 · NEW YORK", wt("tahun", cuts[3]), wt("Lahirlah") - 0.1, 300)
card("TEH CELUP LAHIR!", wt("Lahirlah"), wt("tulis", st[5] - 0.2) - 0.15, 300)
card("TULIS \"TEH\" DI KOMENTAR!", wt("tulis", st[5] - 0.2) - 0.1, TOTAL - 0.45, 250, "Small")
card("JANGAN LUPA LIKE ♥", wt("like!", st[5] - 0.2) - 0.1, TOTAL - 0.45, 340, "Small")

ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,74,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,1,0,1,6,3,2,70,70,560,1
Style: Card,Inter ExtraBold,72,&H00FFFFFF,&H00FFFFFF,&H00141E28,&HA0000000,-1,0,0,0,100,100,2,0,1,7,4,5,40,40,0,1
Style: Small,Inter ExtraBold,56,&H00FFFFFF,&H00FFFFFF,&H00141E28,&HA0000000,-1,0,0,0,100,100,2,0,1,5,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(os.path.join(OUT, "teks.ass"), "w").write(ass)

final = os.path.join(ROOT, "Teh_Part2_Loop_30s_1080x1920_30fps.mp4")
xs = TOTAL - XF
fc = (f"[2:a]volume=-17dB[mus];[1:a]asplit=2[nar][key];"
      f"[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
      f"[nar][duck][3:a]amix=inputs=3:normalize=0,alimiter=limit=0.95[a];"
      f"[4:v]loop=loop=-1:size=1,trim=duration={TOTAL},fps=30,format=yuva420p,"
      f"fade=t=in:st={xs:.3f}:d={XF}:alpha=1[f0];"
      f"[0:v][f0]overlay=shortest=1[blend];"
      f"[blend]ass={os.path.join(OUT, 'teks.ass')},vignette=PI/6,format=yuv420p[v]")
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(OUT, "video_cut.mp4"),
     "-i", os.path.join(OUT, "narasi_timeline.wav"), "-i", os.path.join(OUT, "musik_timeline.wav"),
     "-i", os.path.join(OUT, "sfx_timeline.wav"), "-i", os.path.join(OUT, "frame0.png"),
     "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-r", "30",
     "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", str(TOTAL), final])
print("TOTAL", TOTAL, "cuts", [round(c, 2) for c in cuts], "factors", [round(f, 2) for f in factors])
