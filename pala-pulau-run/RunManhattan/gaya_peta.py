#!/usr/bin/env python3
"""Gaya "peta explainer" (referensi: video KFC & Chen Zhi): peta satelit gelap sebagai panggung,
kamera bergerak antar lokasi, wilayah disorot, kartu pop-up berbingkai putih berisi gambar/klip
yang sudah jadi, stiker label miring (Anton), bar timeline tahun di atas, takarir per kata di bawah.

  python3 gaya_peta.py contoh            -> contoh/*.png + contoh/storyboard.png (tanpa render video)
  python3 gaya_peta.py render [out.mp4]  -> video final (voiceover + musik dari scenes.json)

Sumber peta: NASA Blue Marble (domain publik, via github.com/turban/webgl-earth),
Natural Earth 1:10m/1:50m (domain publik).
"""
import json, math, os, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
W, H, FPS = 1080, 1920, 30
P = lambda *a: os.path.join(ROOT, *a)

# ---------- warna (dari referensi) ----------
RED, YEL, TEAL, BLK, WHT = (214, 40, 48), (255, 210, 50), (38, 166, 154), (18, 18, 20), (250, 248, 242)
ORANGE, NAVY = (240, 120, 30), (25, 40, 90)

# ---------- font ----------
@lru_cache(None)
def font(name, size):
    if name == "anton":
        return ImageFont.truetype(P("fonts", "Anton-Regular.ttf"), size)
    f = ImageFont.truetype(P("fonts", "Inter.ttf"), size)
    try:
        f.set_variation_by_axes([size if size < 32 else 32, 800])  # opsz, wght
    except Exception:
        try: f.set_variation_by_name("ExtraBold")
        except Exception: pass
    return f

# ---------- data kata (takarir) ----------
WORDS = json.load(open(os.path.join(HERE, "words_timeline.json")))
SCENES = {s["n"]: s for s in json.load(open(os.path.join(HERE, "scenes.json")))["scenes"]}
END = max(s["end"] for s in SCENES.values())


def wt(word, scene=None, after=0.0):
    """Detik mulai kata (di timeline baru)."""
    key = word.lower().strip(".,!?:…")
    for w in WORDS:
        if w["start"] >= after and (scene is None or w["scene"] == scene) and \
                w["text"].lower().strip(".,!?:…").replace("'s", "").startswith(key):
            return w["start"]
    raise KeyError(word)


S = lambda n: SCENES[n]["start"]
E = lambda n: SCENES[n]["end"]

# ---------- peta ----------
SAT = Image.open(P("peta", "2_no_clouds_4k.jpg")).convert("RGB")
SW, SH = SAT.size


def grade(im, dark=0.62, sat=0.85):
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    return ImageEnhance.Brightness(im).enhance(dark)


SAT_G = grade(SAT)
SAT_SOMBRE = grade(SAT, dark=0.42, sat=0.25)


def load_geo(path, key=None):
    g = json.load(open(path))
    out = []
    for f in g["features"]:
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]
            xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
            out.append(((min(xs), min(ys), max(xs), max(ys)), ring,
                        f["properties"].get(key) if key else None))
    return out


COUNTRIES = load_geo(P("peta", "ne_50m_countries.geojson"), "ADM0_A3")
STATES = load_geo(P("peta", "ne_50m_admin1.geojson"), "name")
LAND10 = [p for p in load_geo(P("peta", "ne_10m_land.geojson"))]
# Pulau Run tidak ada di Natural Earth: gambar sebagai pulau kecil memanjang di koordinat aslinya
_run = [(129.675 + 0.017 * math.cos(a) * math.cos(0.3) - 0.006 * math.sin(a) * math.sin(0.3),
         -4.552 + 0.017 * math.cos(a) * math.sin(0.3) * 0.4 + 0.006 * math.sin(a)) for a in
        [i / 40 * 2 * math.pi for i in range(41)]]
LAND10.append(((129.65, -4.57, 129.70, -4.54), _run, None))
FY = 880  # titik fokus kamera di layar (di atas tengah, agar kartu di bawah tidak menutupinya)
BANDA = {"Neira": (129.897, -4.524), "Gunung Api": (129.871, -4.505), "Lonthor": (129.925, -4.548),
         "Ai": (129.768, -4.529), "Run": (129.675, -4.552)}


class Cam:
    def __init__(self, lon, lat, wdeg):
        self.lon, self.lat, self.w = lon, lat, wdeg
        self.h = wdeg * H / W

    def xy(self, lon, lat):
        return ((lon - self.lon) / self.w * W + W / 2, (self.lat - lat) / self.h * H + H / 2)

    def bbox(self):
        return (self.lon - self.w / 2, self.lat - self.h / 2, self.lon + self.w / 2, self.lat + self.h / 2)


def ease(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def back(p):  # pop dengan sedikit lewat
    p = max(0.0, min(1.0, p))
    c = 1.9
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


# kunci kamera: (waktu, lon, lat, lebar_derajat)
def cam_keys():
    NY, EU, IDN, BANDA = (-74.0, 40.7), (2.0, 50.5), (122.0, -2.0), (129.85, -4.55)
    return [
        (0.0, -82, 40, 70), (2.0, -74.5, 40.8, 22), (S(3) - 0.6, -74.5, 40.8, 22),
        (S(3) + 0.6, *EU, 34), (E(3) - 0.6, 3.5, 50.0, 30),
        (S(9) + 0.8, *IDN, 40), (wt("Whoever", 9), 127.5, -3.8, 22), (E(9), 129.0, -4.3, 12),
        (S(4) + 1.4, 129.79, -4.535, 0.62), (E(4), 129.78, -4.535, 0.56),
        (S(5) + 0.6, 129.675, -4.552, 0.32), (wt("In", 5) - 0.3, 129.70, -4.55, 0.40),
        (wt("In", 5) + 0.8, 129.82, -4.535, 0.75), (E(5), 129.8, -4.54, 0.9),
        (S(6) + 0.9, -74.0, 40.75, 14), (E(6), -74.0, 40.72, 9),
        (S(7) + 0.6, -74.0, 40.72, 9), (E(8), -74.0, 40.72, 9),
    ]


KEYS = cam_keys()


def camera(t):
    for a, b in zip(KEYS, KEYS[1:]):
        if a[0] <= t <= b[0]:
            p = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            lon = a[1] + (b[1] - a[1]) * p
            lat = a[2] + (b[2] - a[2]) * p
            w = math.exp(math.log(a[3]) + (math.log(b[3]) - math.log(a[3])) * p)
            return focus(lon, lat, w)
    k = KEYS[-1] if t > KEYS[-1][0] else KEYS[0]
    return focus(k[1], k[2], k[3])


def focus(lon, lat, w):
    """kamera yang menaruh (lon, lat) di y = FY"""
    return Cam(lon, lat - (H / 2 - FY) / H * (w * H / W), w)


def base_map(cam, sombre=0.0, highlights=()):
    x0 = (cam.lon - cam.w / 2 + 180) / 360 * SW
    x1 = (cam.lon + cam.w / 2 + 180) / 360 * SW
    y0 = (90 - (cam.lat + cam.h / 2)) / 180 * SH
    y1 = (90 - (cam.lat - cam.h / 2)) / 180 * SH
    src = SAT_G if sombre <= 0 else Image.blend(SAT_G, SAT_SOMBRE, sombre)
    im = src.transform((W, H), Image.EXTENT, (x0, y0, x1, y1), Image.BICUBIC).convert("RGBA")
    if cam.w < 25:  # zoom dekat: citra 4k kabur -> pertegas daratan dengan vektor 1:10m
        im = im.filter(ImageFilter.GaussianBlur(3))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bx = cam.bbox(); a = min(1.0, (25 - cam.w) / 10)
        for (b, ring, _) in LAND10:
            if b[2] < bx[0] or b[0] > bx[2] or b[3] < bx[1] or b[1] > bx[3]:
                continue
            pts = [cam.xy(*p) for p in ring]
            if len(pts) > 2:
                fa = 220 if cam.w < 3 else 70  # isian pekat hanya saat zoom sangat dekat (Banda)
                d.polygon(pts, fill=(70, 96, 58, int(fa * a)), outline=(235, 232, 205, int(200 * a)), width=3)
        im = Image.alpha_composite(im, lay)
    # sorotan wilayah: (sumber, kunci, warna, alpha 0..1)
    if highlights:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bx = cam.bbox()
        for src_name, key, col, al in highlights:
            if al <= 0: continue
            data = COUNTRIES if src_name == "c" else STATES
            for (b, ring, k) in data:
                if k != key or b[2] < bx[0] or b[0] > bx[2] or b[3] < bx[1] or b[1] > bx[3]:
                    continue
                pts = [cam.xy(*p) for p in ring]
                if len(pts) > 2:
                    d.polygon(pts, fill=col + (int(150 * al),), outline=col + (int(255 * al),), width=4)
        im = Image.alpha_composite(im, lay)
    # gradasi gelap atas & bawah untuk teks
    g = Image.new("L", (1, H))
    for y in range(H):
        v = max(0, 1 - y / 420) * 170 + max(0, (y - 1380) / 540) * 230
        g.putpixel((0, y), int(min(255, v)))
    im = Image.alpha_composite(im, Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [g.resize((W, H))]))
    return im


# ---------- elemen grafis ----------
@lru_cache(None)
def sticker_img(text, bg, fg, size, fnt="anton", pad=(26, 10), outline=None):
    f = font(fnt, size)
    lines = text.split("\n")
    boxes = [f.getbbox(l) for l in lines]
    tw = max(b[2] - b[0] for b in boxes); lh = int(size * 1.08)
    w, h = tw + pad[0] * 2, lh * len(lines) + pad[1] * 2
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([10, 12, w + 10, h + 12], fill=(0, 0, 0, 140))            # bayangan
    d.rectangle([2, 2, w + 2, h + 2], fill=bg, outline=outline, width=4 if outline else 0)
    for i, l in enumerate(lines):
        b = f.getbbox(l)
        d.text((2 + (w - (b[2] - b[0])) / 2 - b[0], 2 + pad[1] + i * lh - b[1] + (lh - (b[3] - b[1])) / 2),
               l, font=f, fill=fg)
    return im


def paste_fx(canvas, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def pop(t, t0, t1=None, dur=0.28):
    """skala & alpha pop-in/out"""
    if t < t0: return 0.0, 0.0
    s = back((t - t0) / dur)
    a = min(1.0, (t - t0) / 0.12)
    if t1 is not None and t > t1 - 0.18:
        q = max(0.0, (t1 - t) / 0.18); s *= 0.85 + 0.15 * q; a *= q
    return s, a


_frames_cache = {}


def video_frame(path, t, size):
    """frame klip video (dicache per detik 1/30)"""
    key = (path, size)
    if key not in _frames_cache:
        w, h = size
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", P(path), "-vf",
                              f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (w * h * 3)
        _frames_cache[key] = [Image.frombytes("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]
    fr = _frames_cache[key]
    # ping-pong agar tidak berhenti
    n = len(fr); i = int(t * FPS) % (2 * n - 2) if n > 1 else 0
    return fr[i if i < n else 2 * n - 2 - i]


@lru_cache(None)
def still(path, size):
    im = Image.open(P(path)).convert("RGB")
    return ImageOps.fit(im, size, Image.LANCZOS)


def card(src, size, t_local, border=14, caption=None):
    w, h = size
    pic = video_frame(src, t_local, size) if src.endswith(".mp4") else still(src, size)
    # gerak pelan di dalam kartu (Ken Burns kecil) untuk gambar diam
    if not src.endswith(".mp4"):
        z = 1 + 0.06 * min(1.0, t_local / 6)
        pw, ph = int(w * z), int(h * z)
        pic = pic.resize((pw, ph), Image.BICUBIC).crop(((pw - w) // 2, (ph - h) // 2, (pw - w) // 2 + w, (ph - h) // 2 + h))
    capf = font("inter", 30); caph = 54 if caption else 0
    im = Image.new("RGBA", (w + border * 2 + 18, h + border * 2 + caph + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([12, 14, w + border * 2 + 12, h + border * 2 + caph + 14], fill=(0, 0, 0, 150))
    d.rectangle([0, 0, w + border * 2, h + border * 2 + caph], fill=WHT)
    im.paste(pic, (border, border))
    if caption:
        b = capf.getbbox(caption)
        d.text(((w + border * 2 - (b[2] - b[0])) / 2, h + border + 8), caption, font=capf, fill=BLK)
    return im


def pin(canvas, x, y, label, col=RED, t=99, t0=0, side="r", flag=None):
    s, a = pop(t, t0)
    if a <= 0: return
    d = ImageDraw.Draw(canvas)
    r = 13 * s
    d.ellipse([x - r - 5, y - r - 5, x + r + 5, y + r + 5], fill=(255, 255, 255, int(230 * a)))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(255 * a),))
    if flag:
        draw_flag(canvas, x, y - 22, flag, s, a)
    if label:
        im = sticker_img(label, WHT, BLK, 34, "inter", (14, 8))
        dx = 30 + im.width / 2 if side == "r" else -(30 + im.width / 2)
        paste_fx(canvas, im, x + dx * s, y, s, 0, a)


def draw_flag(canvas, x, y, kind, s=1.0, a=1.0):
    fw, fh = int(54 * s), int(36 * s)
    if fw < 4: return
    f = Image.new("RGBA", (fw, fh), WHT + (255,)); d = ImageDraw.Draw(f)
    if kind == "nl":   # bendera Pangeran (oranye-putih-biru) abad ke-17
        d.rectangle([0, 0, fw, fh / 3], fill=ORANGE); d.rectangle([0, 2 * fh / 3, fw, fh], fill=(30, 60, 150))
    else:              # Salib St George
        d.rectangle([fw / 2 - fw / 10, 0, fw / 2 + fw / 10, fh], fill=RED); d.rectangle([0, fh / 2 - fh / 7, fw, fh / 2 + fh / 7], fill=RED)
    d.rectangle([0, 0, fw - 1, fh - 1], outline=BLK, width=2)
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.line([x, y + fh / 2, x, y - fh / 2 - 4], fill=BLK + (int(255 * a),), width=4)
    lay.alpha_composite(f, (int(x + 1), int(y - fh / 2 - 4)))
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    canvas.alpha_composite(lay)


def ring(canvas, x, y, t, t0, rad=150, col=RED):
    if t < t0: return
    d = ImageDraw.Draw(canvas)
    for k in range(3):
        p = ((t - t0) * 0.7 + k / 3) % 1.0
        r = rad * (0.4 + 0.8 * p); al = int(220 * (1 - p))
        d.ellipse([x - r, y - r, x + r, y + r], outline=col + (al,), width=6)
    d.ellipse([x - rad * 0.55, y - rad * 0.55, x + rad * 0.55, y + rad * 0.55], outline=col + (255,), width=7)


# ---------- bar timeline (gaya Chen Zhi) ----------
YEARS = [1600, 1616, 1620, 1621, 1664, 1667, 2026]


def year_at(t):
    marks = [(0, 2026), (S(3), 1600), (S(4), 1616), (wt("killed", 5), 1620), (wt("In", 5), 1621),
             (S(6), 1664), (S(7), 1667), (S(8), 2026)]
    y, place = 2026, ""
    for tm, yr in marks:
        if t >= tm: y = yr
    places = [(0, "NEW YORK"), (S(3), "EROPA"), (S(9), "KEPULAUAN BANDA"), (S(4), "PULAU RUN"),
              (S(2), "BANDA"), (S(5), "PULAU RUN"), (wt("In", 5), "BANDA"), (S(6), "NEW AMSTERDAM"),
              (S(7), "BREDA"), (S(8), "RUN ↔ MANHATTAN")]
    for tm, pl in places:
        if t >= tm: place = pl
    return y, place


def timeline(canvas, t):
    d = ImageDraw.Draw(canvas)
    x0, x1, y = 70, W - 70, 92
    f = font("inter", 24)
    d.line([x0, y, x1, y], fill=(255, 255, 255, 200), width=3)
    pos = {yr: x0 + (x1 - x0) * i / (len(YEARS) - 1) for i, yr in enumerate(YEARS)}
    yr, place = year_at(t)
    for k, x in pos.items():
        d.line([x, y - 9, x, y + 9], fill=(255, 255, 255, 200), width=3)
        b = f.getbbox(str(k))
        d.text((x - (b[2] - b[0]) / 2, y - 46), str(k), font=f, fill=(255, 255, 255, 255 if k == yr else 150))
    # penunjuk bergerak halus
    px = pos[yr]
    d.polygon([(px - 12, y + 26), (px + 12, y + 26), (px, y + 10)], fill=WHT)
    im = sticker_img(f"{yr}  |  {place}", WHT, BLK, 28, "inter", (16, 6))
    paste_fx(canvas, im, W / 2, y + 66)


# ---------- takarir per kata (gaya KFC) ----------
HILITE = {"york", "this", "crazier", "europe", "obsessed", "plague", "banda", "price", "dutch", "tree", "run",
          "england", "nutmeg", "kitchen", "ugly", "courthope", "siege", "years", "1621", "terrible", "1664",
          "amsterdam", "1667", "breda", "manhattan", "swap", "spice", "fate", "keep"}


def chunks():
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        if len(cur) >= 3 or w["text"][-1] in ".,!?:…":
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


CHUNKS = chunks()


def captions(canvas, t):
    cur = None
    for i, c in enumerate(CHUNKS):
        nxt = CHUNKS[i + 1][0]["start"] if i + 1 < len(CHUNKS) else END
        if c[0]["start"] - 0.05 <= t < nxt - 0.02:
            cur = c
    if not cur: return
    f = font("inter", 46)
    d = ImageDraw.Draw(canvas)
    toks = [(w, w["text"].upper().strip("…").replace("...", "")) for w in cur]
    sp = 18; widths = [f.getbbox(s)[2] - f.getbbox(s)[0] for _, s in toks]
    x = (W - sum(widths) - sp * (len(toks) - 1)) / 2; y = 1640
    for (w, s), wd in zip(toks, widths):
        key = s.lower().strip(".,!?:'’").replace("'s", "")
        spoken = t >= w["start"] - 0.03
        if key in HILITE and spoken:
            d.rectangle([x - 8, y - 4, x + wd + 8, y + 58], fill=YEL)
            d.text((x, y), s, font=f, fill=BLK, anchor="la")
        else:
            col = (255, 255, 255, 255) if spoken else (255, 255, 255, 140)
            d.text((x, y), s, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0, 255))
        x += wd + sp


# ---------- adegan ----------
def render(t):
    cam = camera(t)
    sombre = 0.0
    t1621 = wt("In", 5)
    if t1621 - 0.5 < t < E(5):
        sombre = min(1.0, (t - t1621 + 0.5) / 0.8)
    hl = []
    if t < S(3):
        hl.append(("s", "New York", RED, ease((t - 0.6) / 0.6)))
    elif t < S(9):
        hl += [("c", "GBR", RED, ease((t - S(3) - 0.6) / 0.5)), ("c", "NLD", ORANGE, ease((t - S(3) - 0.9) / 0.5)),
               ("c", "FRA", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5)), ("c", "DEU", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5)),
               ("c", "ESP", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5)), ("c", "PRT", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5)),
               ("c", "BEL", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5)), ("c", "ITA", RED, 0.45 * ease((t - S(3) - 1.2) / 0.5))]
    elif t < S(4):
        hl.append(("c", "IDN", TEAL, 0.5 * ease((t - S(9) - 0.8) / 0.6)))
    elif S(6) <= t:
        hl.append(("s", "New York", RED, 0.6 * ease((t - S(6) - 0.9) / 0.6)))
    im = base_map(cam, sombre, hl)

    # ---- 1 hook ----
    if t < S(3):
        x, y = cam.xy(-74.0, 40.7)
        pin(im, x, y, "NEW YORK", RED, t, 0.9)
        tf = wt("for", 1)
        s, a = pop(t, tf, S(3)); paste_fx(im, card("RunManhattan/assets/hook_pala_9x16.png", (405, 720), t - tf), W / 2 + 150, 1230, s, 4, a)
        s, a = pop(t, wt("gave", 1) - 0.1, S(3))
        paste_fx(im, sticker_img("THE DUTCH\nGAVE UP NEW YORK…", BLK, WHT, 74), W / 2, 370, s, -3, a)
        s, a = pop(t, tf + 0.2, S(3)); paste_fx(im, sticker_img("FOR THIS?!", RED, WHT, 140), W / 2 - 70, 600, s, -5, a)
        s, a = pop(t, wt("crazier", 1) - 0.2, S(3))
        paste_fx(im, sticker_img("THE REAL STORY IS\nEVEN CRAZIER", YEL, BLK, 50), 260, 1180, s, -4, a)

    # ---- 3 Eropa ----
    elif t < S(9):
        x, y = cam.xy(-1.5, 52.5); pin(im, x, y, "ENGLAND", RED, t, S(3) + 0.8, "l")
        x, y = cam.xy(5.0, 52.3); pin(im, x, y, "THE DUTCH", ORANGE, t, S(3) + 1.1)
        tf = wt("Europe", 3)
        s, a = pop(t, S(3) + 0.4, S(9)); paste_fx(im, card("RunManhattan/assets/scene3_crop.png", (420, 560), t - S(3)), W / 2 + 200, 1290, s, -4, a)
        s, a = pop(t, tf, S(9)); paste_fx(im, sticker_img("EUROPE WAS\nOBSESSED", BLK, WHT, 80), W / 2, 380, s, -3, a)
        s, a = pop(t, tf + 0.3, S(9)); paste_fx(im, sticker_img("A FORTUNE", YEL, BLK, 110), W / 2 + 40, 600, s, 4, a)
        tp = wt("plague", 3)
        s, a = pop(t, tp - 0.25, S(9)); paste_fx(im, sticker_img("“IT CURES\nTHE PLAGUE”?!", RED, WHT, 60), 280, 1240, s, -6, a)

    # ---- 9 Banda ----
    elif t < S(4):
        x, y = cam.xy(129.9, -4.53)
        pin(im, x, y, "BANDA ISLANDS", RED, t, S(9) + 1.0, "l")
        s, a = pop(t, wt("Banda", 9) - 0.1, S(4))
        paste_fx(im, card("RunManhattan/assets/scene9_banda.png", (820, 461), t - S(9), caption="KEPULAUAN BANDA, MALUKU"), W / 2, 1300, s, 3, a)
        s, a = pop(t, S(9) + 0.3, S(4)); paste_fx(im, sticker_img("ONLY PLACE\nON EARTH", BLK, WHT, 84), W / 2, 380, s, -3, a)
        s, a = pop(t, wt("Whoever", 9), S(4)); paste_fx(im, sticker_img("NAMED THE PRICE", YEL, BLK, 76), W / 2 + 60, 600, s, 4, a)

    # ---- 4 Pulau Run ----
    elif t < S(2):
        for k, nm in enumerate(["Neira", "Gunung Api", "Lonthor", "Ai"]):
            x, y = cam.xy(*BANDA[nm]); draw_flag(im, x, y - 10, "nl", *pop(t, S(4) + 1.3 + 0.18 * k))
        x, y = cam.xy(*BANDA["Run"])
        tr = wt("Pulau", 4)
        pin(im, x, y, "PULAU RUN", RED, t, tr - 0.1, "r", flag="en")
        s, a = pop(t, S(4) + 1.0, S(2)); paste_fx(im, card("RunManhattan/assets/scene4.png", (380, 480), t - S(4)), 290, 1330, s, -5, a)
        s, a = pop(t, S(4) + 0.2, S(2)); paste_fx(im, sticker_img("THE DUTCH WANTED\nEVERY TREE", BLK, WHT, 70), W / 2, 360, s, -3, a)
        s, a = pop(t, tr - 0.05, S(2)); paste_fx(im, sticker_img("ONE TINY ISLAND", RED, WHT, 96), W / 2 - 30, 560, s, -4, a)
        s, a = pop(t, wt("chose", 4) - 0.05, S(2)); paste_fx(im, sticker_img("CHOSE ENGLAND", WHT, BLK, 70), 760, 1240, s, 5, a)

    # ---- 2 reveal pala ----
    elif t < S(5):
        s, a = pop(t, S(2) + 0.1, S(5), 0.35); paste_fx(im, card("RunManhattan/assets/scene2.png", (680, 940), t - S(2)), W / 2, 1070, s, 2, a)
        s, a = pop(t, S(2) - 0.05, S(5)); paste_fx(im, sticker_img("IT WAS…", BLK, WHT, 70), W / 2, 360, s, -3, a)
        tn = wt("nutmeg", 2)
        s, a = pop(t, tn, S(5)); paste_fx(im, sticker_img("NUTMEG!", YEL, BLK, 170), W / 2, 560, s, -4, a)
        s, a = pop(t, wt("kitchen", 2) - 0.3, S(5)); paste_fx(im, sticker_img("YES, THE ONE IN\nYOUR KITCHEN", RED, WHT, 54), W / 2 + 150, 1480, s, 3, a)

    # ---- 5 pengepungan ----
    elif t < S(6):
        x, y = cam.xy(*BANDA["Run"])
        if t < t1621:
            ring(im, x, y, t, S(5) + 0.3, 130)
            pin(im, x, y, "", RED, t, S(5), flag="en")
            s, a = pop(t, wt("Captain", 5) - 0.1, t1621)
            paste_fx(im, card("vid/s5.mp4", (420, 600), t - S(5), caption="CAPT. NATHANIEL COURTHOPE"), W / 2 + 200, 1300, s, -3, a)
            s, a = pop(t, S(5) + 0.1, t1621); paste_fx(im, sticker_img("THEN IT GOT UGLY", BLK, WHT, 76), W / 2, 360, s, -3, a)
            s, a = pop(t, wt("under", 5), t1621); paste_fx(im, sticker_img("UNDER SIEGE", RED, WHT, 120), W / 2 - 30, 560, s, -4, a)
            s, a = pop(t, wt("four", 5) - 0.1, t1621); paste_fx(im, sticker_img("4 YEARS\n1616–1620", YEL, BLK, 62), 250, 1240, s, -5, a)
        else:
            for nm in BANDA:
                x2, y2 = cam.xy(*BANDA[nm]); draw_flag(im, x2, y2 - 10, "nl", *pop(t, t1621 + 0.6))
            s, a = pop(t, t1621, S(6)); paste_fx(im, sticker_img("1621", RED, WHT, 190), W / 2, 450, s, -4, a)
            s, a = pop(t, wt("Dutch", 5, t1621) - 0.1, S(6)); paste_fx(im, sticker_img("THE DUTCH TOOK BANDA", BLK, WHT, 66), W / 2, 660, s, 2, a)
            s, a = pop(t, wt("terrible", 5) - 0.1, S(6)); paste_fx(im, sticker_img("AT A TERRIBLE COST\nTO ITS PEOPLE", WHT, BLK, 56), W / 2, 1240, s, -2, a)

    # ---- 6 1664 ----
    elif t < S(7):
        x, y = cam.xy(-74.0, 40.72)
        t64 = wt("1664", 6)
        pin(im, x, y, "NEW AMSTERDAM" if t < wt("renamed", 6) else "NEW YORK", ORANGE if t < wt("renamed", 6) else RED,
            t, S(6) + 1.0, "r", flag="en" if t > t64 + 0.6 else "nl")
        s, a = pop(t, t64 + 0.4, S(7)); paste_fx(im, card("RunManhattan/assets/scene6.png", (400, 540), t - t64), 300, 1320, s, -4, a)
        s, a = pop(t, S(6) + 0.1, S(7)); paste_fx(im, sticker_img("HERE'S WHERE\nNEW YORK COMES IN", BLK, WHT, 70), W / 2, 380, s, -3, a)
        s, a = pop(t, t64, S(7)); paste_fx(im, sticker_img("1664", YEL, BLK, 150), W / 2 + 230, 620, s, 5, a)
        s, a = pop(t, wt("seized", 6) - 0.1, S(7)); paste_fx(im, sticker_img("ENGLAND SEIZED IT", RED, WHT, 60), 760, 1200, s, 4, a)

    # ---- 7 Breda 1667 & 8 penutup: panel peta dunia ----
    else:
        world_panel(im, t)
    timeline(im, t)
    captions(im, t)
    return im.convert("RGB")


@lru_cache(None)
def world_base(w, h):
    im = SAT_G.resize((w, h), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(im)
    return im


def world_panel(im, t):
    pw, ph = 1000, 500; px, py = (W - pw) // 2, 560
    wb = world_base(pw, ph).copy()
    d = ImageDraw.Draw(wb)
    g = lambda lon, lat: ((lon + 180) / 360 * pw, (90 - lat) / 180 * ph)
    nx, ny = g(-74, 40.7); rx, ry = g(129.7, -4.5)
    # busur penghubung (lewat Afrika selatan, rute kapal)
    pts = []
    for i in range(61):
        p = i / 60
        lon = -74 + (129.7 + 74) * p; lat = 40.7 + (-4.5 - 40.7) * p - 38 * math.sin(math.pi * p)
        pts.append(g(lon, lat))
    prog = ease((t - S(7) - 0.3) / 1.5)
    n = max(2, int(len(pts) * prog))
    for i in range(0, n - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=YEL + (255,), width=5)
    s7, a7 = pop(t, S(7) + 0.1)
    frame = Image.new("RGBA", (pw + 28, ph + 28), WHT + (255,)); frame.alpha_composite(wb, (14, 14))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_fx(canvas, frame, W / 2, py + ph / 2, s7, -1.5, a7)
    im.alpha_composite(canvas)
    ox, oy = px - 0, py
    tk = wt("kept", 7)
    pin(im, ox + nx, oy + ny, "MANHATTAN → ENGLAND", RED, t, wt("England", 7, tk), "r", flag="en")
    pin(im, ox + rx, oy + ry, "RUN → DUTCH", ORANGE, t, tk - 0.1, "l", flag="nl")
    if t < S(8):
        s, a = pop(t, wt("1667", 7), S(8)); paste_fx(im, sticker_img("1667", YEL, BLK, 150), 250, 360, s, -5, a)
        s, a = pop(t, wt("Treaty", 7) - 0.1, S(8)); paste_fx(im, sticker_img("TREATY OF BREDA", BLK, WHT, 70), W / 2 + 140, 470, s, 3, a)
        s, a = pop(t, wt("let", 7) - 0.1, S(8)); paste_fx(im, card("RunManhattan/assets/scene7.png", (420, 560), t - S(7)), W / 2, 1360, s, -3, a)
    else:
        s, a = pop(t, S(8) + 0.05, wt("keep", 8)); paste_fx(im, sticker_img("NOT A STRAIGHT SWAP…", BLK, WHT, 64), W / 2, 380, s, -3, a)
        tr = wt("Run", 8)
        s, a = pop(t, wt("spice", 8) - 0.1, tr); paste_fx(im, sticker_img("BUT A SPICE DECIDED\nNEW YORK'S FATE", YEL, BLK, 60), W / 2, 1300, s, 2, a)
        s, a = pop(t, tr - 0.05); paste_fx(im, card("RunManhattan/assets/scene4.png", (330, 400), t - tr, caption="PULAU RUN"), 270, 1250, s, -5, a)
        s, a = pop(t, wt("Manhattan", 8, tr) - 0.05); paste_fx(im, card("RunManhattan/assets/scene6.png", (330, 400), t - tr, caption="MANHATTAN"), W - 270, 1250, s, 5, a)
        s, a = pop(t, wt("Manhattan", 8, tr) + 0.1); paste_fx(im, sticker_img("VS", RED, WHT, 90, outline=WHT), W / 2, 1230, s, 0, a)
        s, a = pop(t, wt("which", 8) - 0.1); paste_fx(im, sticker_img("WHICH WOULD YOU KEEP?", WHT, BLK, 60), W / 2, 1520, s, -2, a)
        s, a = pop(t, wt("keep", 8)); paste_fx(im, sticker_img("TELL ME IN THE COMMENTS", RED, WHT, 60), W / 2, 380, s, 2, a)


# ---------- main ----------
def contoh():
    out = os.path.join(HERE, "contoh"); os.makedirs(out, exist_ok=True)
    T = [(1.6, "hook NY"), (3.2, "FOR THIS"), (wt("plague", 3) + 0.4, "Eropa"), (wt("Whoever", 9) + 0.8, "Banda"),
         (wt("chose", 4) + 0.6, "Pulau Run"), (wt("kitchen", 2) + 0.1, "NUTMEG"), (wt("four", 5) + 1.0, "pengepungan"),
         (wt("terrible", 5) + 0.6, "1621"), (wt("renamed", 6) + 0.5, "1664"), (wt("let", 7) + 0.8, "Breda 1667"),
         (wt("Manhattan", 7) + 0.5, "Run vs Manhattan"), (wt("keep", 8) + 0.3, "penutup")]
    thumbs = []
    for i, (t, name) in enumerate(T, 1):
        im = render(t)
        im.save(os.path.join(out, f"{i:02d}_{name.replace(' ', '_')}.png"))
        thumbs.append(im.resize((270, 480), Image.LANCZOS)); print(f"{i:02d} {t:6.2f}s {name}")
    cols = 6; rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 270 + (cols - 1) * 8, rows * 480 + (rows - 1) * 8), (240, 240, 240))
    for i, th in enumerate(thumbs):
        sheet.paste(th, ((i % cols) * 278, (i // cols) * 488))
    sheet.save(os.path.join(out, "storyboard.png"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "contoh"
    if cmd == "contoh":
        contoh()
