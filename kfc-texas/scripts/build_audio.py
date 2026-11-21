#!/usr/bin/env python3
"""Tighten the ElevenLabs take to ~40s, then mix a synthesized music bed + SFX.
Writes public/mix.wav and src/timeline.json (segment times used by the animation)."""
import json, os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TEMPO = 1.11
LEAD, TAIL = 0.12, 1.0

# (raw_start, raw_end, text, gap_before_seconds)
SEG = [
    (0.00, 0.97, "KFC...", 0.0),
    (1.31, 2.84, "just filed for bankruptcy?!", 0.18),
    (3.32, 5.00, "Eighty-four restaurants at risk.", 0.22),
    (5.35, 7.34, "Forty-four already shut down this year.", 0.14),
    (7.77, 9.59, "Over sixteen hundred workers...", 0.14),
    (9.88, 10.51, "left hanging.", 0.16),
    (10.98, 12.74, "But people still love fried chicken.", 0.24),
    (13.15, 13.53, "So...", 0.14),
    (13.83, 14.52, "what went wrong?", 0.24),
    (15.07, 17.36, "Sales dropped nearly sixteen percent.", 0.26),
    (17.75, 18.82, "Costs kept rising.", 0.12),
    (19.24, 21.55, "Profit per store crashed from twelve percent...", 0.12),
    (21.78, 22.47, "to just four.", 0.22),
    (22.92, 24.45, "But here's what most people don't know.", 0.28),
    (24.81, 26.27, "This isn't happening everywhere.", 0.14),
    (26.68, 27.94, "It's happening in Texas.", 0.38),
    (28.34, 30.55, "The company going bankrupt is Tasty Chick'n,", 0.30),
    (30.83, 32.94, "one of KFC's biggest franchisees.", 0.10),
    (33.26, 38.98, "And KFC itself tried to cut ties, over fifteen point seven million dollars in unpaid fees.", 0.18),
    (39.33, 40.56, "So who's really to blame:", 0.26),
    (40.94, 42.64, "the franchisee, or KFC?", 0.10),
    (43.10, 45.20, "Tell me in the comments, and follow for more!", 0.22),
]

def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                                   "-af", f"atempo={TEMPO}", "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()

vo = load(os.path.join(ROOT, "public", "vo_raw.mp3"))
pad = 0.03
t, pieces, timeline = LEAD, [], []
for s, e, text, gap in SEG:
    t += gap
    a, b = int(max(0, s - pad) / TEMPO * SR), int((e + pad) / TEMPO * SR)
    chunk = vo[a:b].copy()
    f = int(0.012 * SR); chunk[:f] *= np.linspace(0, 1, f); chunk[-f:] *= np.linspace(1, 0, f)
    pieces.append((t, chunk))
    d = len(chunk) / SR
    timeline.append({"start": round(t + pad / TEMPO, 3), "end": round(t + d - pad / TEMPO, 3), "text": text})
    t += d
TOTAL = round(t + TAIL, 2)
N = int(TOTAL * SR)
voice = np.zeros(N, np.float32)
for st, ch in pieces:
    i = int(st * SR); voice[i:i + len(ch)] += ch[:N - i]

rng = np.random.default_rng(7)
tt = np.arange(N) / SR

# ---- music bed: tense pulse in A minor, lifts after the Texas reveal ----
def env_adsr(n, a=0.005, r=0.25):
    e = np.ones(n); ai = int(a * SR); e[:ai] = np.linspace(0, 1, ai)
    e *= np.exp(-np.arange(n) / (r * SR)); return e
music = np.zeros(N, np.float32)
bpm = 112; beat = 60 / bpm
reveal = timeline[15]["start"]
bass_notes = [55.0, 55.0, 43.65, 49.0]  # A1 A1 F1 G1
k = 0
b = 0.0
while b < TOTAL - 0.5:
    bar = int(b / (beat * 4)) % 4
    fr = bass_notes[bar] * (1.0 if b < reveal else 1.0)
    n = int(beat * 0.9 * SR); i = int(b * SR)
    seg = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * fr * seg) + 0.4 * np.sin(2 * np.pi * fr * 2 * seg)) * env_adsr(n, r=0.18)
    music[i:i + n] += 0.22 * tone[:N - i]
    # hat on off-beats
    hn = int(0.04 * SR); hi = int((b + beat / 2) * SR)
    if hi + hn < N:
        music[hi:hi + hn] += 0.05 * rng.standard_normal(hn) * np.exp(-np.arange(hn) / (0.008 * SR))
    # kick every beat after the reveal, every 2 beats before
    if b >= reveal or k % 2 == 0:
        kn = int(0.18 * SR); ks = np.arange(kn) / SR
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-ks * 30)) * ks) * np.exp(-ks * 14)
        music[i:i + kn] += 0.35 * kick[:N - i]
    b += beat; k += 1
# pad drone
music += 0.04 * (np.sin(2 * np.pi * 220 * tt) + np.sin(2 * np.pi * 261.6 * tt) + np.sin(2 * np.pi * 329.6 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt))
fade = np.ones(N); fi = int(0.6 * SR); fade[:fi] = np.linspace(0, 1, fi); fo = int(1.2 * SR); fade[-fo:] = np.linspace(1, 0, fo)
music *= fade

# ---- SFX ----
sfx = np.zeros(N, np.float32)
def place(x, at, g=1.0):
    i = int(at * SR)
    if i >= N: return
    sfx[i:i + len(x)] += g * x[:N - i]
def pop():
    n = int(0.09 * SR); s = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 - 5000 * s) * s) * np.exp(-s * 45)
def whoosh(d=0.45):
    n = int(d * SR); x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(30) / 30, mode="same")
    return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * 1.4
def impact():
    n = int(0.9 * SR); s = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (40 + 120 * np.exp(-s * 18)) * s) * np.exp(-s * 4.5)
    crack = rng.standard_normal(n) * np.exp(-s * 25) * 0.6
    return boom + crack
def ding():
    n = int(0.6 * SR); s = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318 * s) + 0.5 * np.sin(2 * np.pi * 1976 * s)) * np.exp(-s * 6) * 0.5
def tick():
    n = int(0.03 * SR); s = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * s) * np.exp(-s * 160)

T = [x["start"] for x in timeline]
place(impact(), T[1] + 0.35, 0.9)            # BANKRUPT?!
place(pop(), T[2], 0.6); place(pop(), T[3], 0.6); place(pop(), T[4], 0.6)
place(whoosh(), T[6] - 0.25, 0.5)
place(pop(), T[8], 0.6)
for j in range(8): place(tick(), T[9] + j * 0.09, 0.4)   # numbers counting
place(whoosh(0.35), T[11] - 0.2, 0.45)
place(impact(), T[12], 0.55)                 # to just four
place(whoosh(0.6), T[15] - 0.45, 0.8)
place(impact(), T[15] + 0.6, 0.8)            # TEXAS
place(pop(), T[16] + 1.0, 0.6)
place(ding(), T[17] + 0.2, 0.6)
for j in range(10): place(tick(), T[18] + 1.6 + j * 0.08, 0.4)
place(pop(), T[19], 0.6); place(pop(), T[20] + 0.3, 0.6)
place(ding(), T[21], 0.7)

# duck music under voice
venv = np.convolve(np.abs(voice), np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
duck = 1.0 - 0.45 * np.clip(venv / (venv.max() * 0.25), 0, 1)
mix = voice * 1.0 + music * 0.55 * duck + sfx * 0.45
mix /= max(1.0, np.abs(mix).max() / 0.95)
tmp = os.path.join(ROOT, "public", "mix_tmp.wav")
import wave
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "public", "mix.wav")], check=True)
os.remove(tmp)
json.dump({"total": TOTAL, "segments": timeline}, open(os.path.join(ROOT, "src", "timeline.json"), "w"), indent=1)
print("TOTAL", TOTAL)
for i, x in enumerate(timeline): print(i, x["start"], x["end"], x["text"])
