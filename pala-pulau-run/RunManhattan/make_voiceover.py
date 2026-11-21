#!/usr/bin/env python3
"""Susun ulang kalimat voiceover asli supaya buah pala baru diungkap di tengah cerita.

Sumber: ../audio/narasi_a.mp3 (take qCRdJ2P7IN2cJamLHzpD) + transkrip per kata
../audio/narasi_a_words.json (eleven_scribe_v1). Tanpa TTS baru, suara tetap sama.

Hasil: assets/voiceover.wav, dan start/end + keyword.at di scenes.json diperbarui.
Jalankan: python3 make_voiceover.py && python3 assemble.py --no-scale
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "../audio/narasi_a.mp3")
WORDS = os.path.join(HERE, "../audio/narasi_a_words.json")
OUT = os.path.join(HERE, "assets/voiceover.wav")
TAIL = 0.6

words = [w for w in json.load(open(WORDS))["words"]
         if w.get("type", "word") == "word" and not w["text"].startswith("[")]
clean = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))


def find(phrase, start=0):
    """Indeks kata pertama & terakhir dari frasa di transkrip."""
    p = [clean(x) for x in phrase.split()]
    for i in range(start, len(words) - len(p) + 1):
        if all(clean(words[i + k]["text"]) == p[k] for k in range(len(p))):
            return i, i + len(p) - 1
    raise SystemExit("frasa tidak ditemukan: " + phrase)


def span(first, last):
    """Potong di tengah jeda dengan kata sebelum/sesudahnya agar napas alami ikut."""
    i, _ = find(first)
    _, j = find(last, i)
    a = words[i]["start"] if i == 0 else (words[i - 1]["end"] + words[i]["start"]) / 2
    b = words[j]["end"] + 0.12 if j == len(words) - 1 else (words[j]["end"] + words[j + 1]["start"]) / 2
    return i, j, a, b


# (nomor scene, [(kata awal kalimat, kata akhir kalimat), ...]) dalam urutan baru
ORDER = [
    (1, [("The Dutch gave", "for this."), ("And the real", "even crazier.")]),
    (3, [("But here's the catch", "was obsessed."), ("They even thought", "the plague.")]),
    (9, [("Four hundred years", "Banda Islands."), ("Whoever owned Banda", "the price.")]),
    (4, [("The Dutch wanted", "every tree."), ("But one tiny", "chose England.")]),
    (2, [("This is nutmeg", "your kitchen.")]),
    (5, [("Then it got", "its people.")]),
    (6, [("And here's where", "comes in."), ("In 1664,", "renamed it New York.")]),
    (7, [("In 1667,", "kept Manhattan.")]),
    (8, [("Not a straight", "would you keep?")]),
]
# kata kunci: (scene, kata pemicu)
KEY = {1: "for this.", 3: "Europe was", 4: "Pulau Run,", 2: "nutmeg,", 5: "under siege",
       6: "1664,", 7: "1667,", 8: "Run or"}
GAP_SCENE = 0.25  # jeda tambahan di pergantian scene
NO_GAP_AFTER = {9}  # scene Banda 9 -> 4 satu alur, tanpa jeda tambahan

pieces, t, bounds, kw_abs, new_words = [], 0.0, {}, {}, []
for n, sents in ORDER:
    t0 = t
    for k, (f, l) in enumerate(sents):
        i, j, a, b = span(f, l)
        # waktu kata kunci (absolut di timeline baru)
        try:
            ki, _ = find(KEY[n], i)  # KeyError bila scene tanpa kata kunci
            if ki <= j and n not in kw_abs:
                kw_abs[n] = t + (words[ki]["start"] - a)
        except (SystemExit, KeyError):
            pass
        pieces.append((a, b))
        for w in words[i:j + 1]:  # waktu kata di timeline baru (untuk takarir)
            new_words.append({"text": w["text"], "start": round(t + w["start"] - a, 3),
                              "end": round(t + w["end"] - a, 3), "scene": n})
        t += b - a
    if n != ORDER[-1][0] and n not in NO_GAP_AFTER:
        pieces.append((None, GAP_SCENE)); t += GAP_SCENE
    bounds[n] = (t0, t)

n_last = ORDER[-1][0]
bounds[n_last] = (bounds[n_last][0], t + TAIL)

# rakit audio
fc, labels = [], []
for k, (a, b) in enumerate(pieces):
    if a is None:
        fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{b:.3f}[p{k}]")
    else:
        d = b - a
        fc.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.01,afade=t=out:st={d - 0.015:.3f}:d=0.015[p{k}]")
    labels.append(f"[p{k}]")
fc.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1,apad=pad_dur={TAIL}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc),
                "-map", "[out]", "-ac", "1", "-ar", "44100", OUT], check=True)

json.dump(new_words, open(os.path.join(HERE, "words_timeline.json"), "w"), indent=1)

# perbarui scenes.json: urutkan scene sesuai urutan baru
cfg = json.load(open(os.path.join(HERE, "scenes.json")))
by_n = {s["n"]: s for s in cfg["scenes"]}
new = []
for n, _ in ORDER:
    s = by_n[n]
    a, b = bounds[n]
    s["start"], s["end"] = round(a, 3), round(b, 3)
    if n in kw_abs and s.get("keyword"):
        at = kw_abs[n] - a
        s["keyword"]["at"] = round(at, 2)
        s["keyword"]["hold"] = round(min(s["keyword"].get("hold", 2.2), b - a - at - 0.05), 2)
    new.append(s)
cfg["scenes"] = new
cfg["voiceover"]["file"] = "assets/voiceover.wav"
cfg["voiceover"]["note"] = ("Disusun ulang oleh make_voiceover.py dari take qCRdJ2P7IN2cJamLHzpD: "
                            "buah pala diungkap di tengah cerita. Render dengan --no-scale.")
json.dump(cfg, open(os.path.join(HERE, "scenes.json"), "w"), indent=2, ensure_ascii=False)
for s in new:
    kw = f"{s['keyword']['text']!r} @ {s['start'] + s['keyword']['at']:.2f}s" if s.get("keyword") else "(tanpa teks)"
    print(f"scene {s['n']}: {s['start']:6.2f}-{s['end']:6.2f}  {kw}  ({s['asset']})")
