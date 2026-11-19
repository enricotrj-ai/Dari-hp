#!/usr/bin/env python3
"""Collage-style Shorts thumbnail (torn paper panels, heavy outlined headline, stickers)."""
import random, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

random.seed(7)
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.abspath(__file__))
S = sys.argv[1]                      # folder with panel frames + fonts
BANG = os.path.join(S, "fonts/bangers.ttf")
ANTON = os.path.join(S, "fonts/anton.ttf")
YEL, RED, BLK, WHT = (255, 214, 0), (222, 28, 36), (12, 12, 12), (255, 255, 255)

def fit(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))

def pop(img):
    img = ImageEnhance.Contrast(img).enhance(1.18)
    return ImageEnhance.Color(img).enhance(1.25)

def torn_mask(w, h, edges="tb", amp=18, step=14):
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    pts = []
    top = [(x, (random.randint(0, amp) if "t" in edges else 0)) for x in range(0, w + step, step)]
    bot = [(x, h - (random.randint(0, amp) if "b" in edges else 0)) for x in range(w, -step, -step)]
    pts = top + bot
    d.polygon(pts, fill=255)
    return m

def paste_panel(canvas, img, box, angle=0, edges="tb", border=10):
    x, y, w, h = box
    tile = pop(fit(img, w, h)).convert("RGBA")
    mask = torn_mask(w, h, edges)
    # white paper border behind the torn panel
    paper = Image.new("RGBA", (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
    pm = torn_mask(w + 2 * border, h + 2 * border, edges, amp=22)
    paper.paste(Image.new("RGBA", paper.size, (250, 246, 235, 255)), (0, 0), pm)
    paper.paste(tile, (border, border), mask)
    shadow = Image.new("RGBA", paper.size, (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", paper.size, (0, 0, 0, 150)), (0, 0), pm)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    if angle:
        paper = paper.rotate(angle, expand=True, resample=Image.BICUBIC)
        shadow = shadow.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(shadow, (x - border + 10, y - border + 14))
    canvas.alpha_composite(paper, (x - border, y - border))

def text(d, xy, s, font, size, fill, stroke=12, sfill=BLK, anchor="mm", shadow=True):
    f = ImageFont.truetype(font, size)
    if shadow:
        d.text((xy[0] + 8, xy[1] + 10), s, font=f, fill=BLK, stroke_width=stroke, stroke_fill=BLK, anchor=anchor)
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)
    return f

def sticker(canvas, s, center, size, bg, fg, angle=-6, font=BANG, pad=(26, 12)):
    f = ImageFont.truetype(font, size)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), s, font=f)
    w, h = r - l + 2 * pad[0], b - t + 2 * pad[1]
    st = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rectangle([4, 4, w + 11, h + 11], fill=BLK)
    d.rectangle([0, 0, w + 6, h + 6], fill=bg, outline=BLK, width=5)
    d.text(((w + 6) / 2, (h + 6) / 2), s, font=f, fill=fg, anchor="mm")
    st = st.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(st, (int(center[0] - st.width / 2), int(center[1] - st.height / 2)))

canvas = Image.new("RGBA", (W, H), (20, 20, 22, 255))
# background: key frame, darkened + paper texture feel
bg = fit(Image.open(os.path.join(ROOT, "frame_kunci_loop.png")).convert("RGB"), W, H)
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(6))).enhance(0.45)
canvas.alpha_composite(bg.convert("RGBA"))

kebun = Image.open(os.path.join(S, "pan_kebun.png")).convert("RGB")
celup = Image.open(os.path.join(S, "pan_celup.png")).convert("RGB")
glass = Image.open(os.path.join(ROOT, "frame_kunci_loop.png")).convert("RGB")
glass = glass.crop((int(glass.width * 0.16), int(glass.height * 0.33), int(glass.width * 0.84), int(glass.height * 0.86)))

# top yellow torn strip
strip = Image.new("RGBA", (W + 40, 120), YEL + (255,))
canvas.paste(strip, (-20, 0), torn_mask(W + 40, 120, "b", amp=16))
d = ImageDraw.Draw(canvas)
d.text((W // 2, 56), "SEJARAH KELAM SEGELAS TEH!", font=ImageFont.truetype(BANG, 76), fill=BLK, anchor="mm")

# panel 1: tanam paksa plantation
paste_panel(canvas, kebun, (40, 150, 1000, 560), angle=1.5)
sticker(canvas, "TANAM PAKSA 1830", (300, 640), 62, RED, WHT, angle=-5)

# panel 2: es teh glass (hero)
paste_panel(canvas, glass, (90, 760, 640, 760), angle=-2)
# panel 3: teh celup inset
paste_panel(canvas, celup, (600, 1060, 440, 470), angle=4)
sticker(canvas, "1908", (930, 1080), 70, YEL, BLK, angle=8)

d = ImageDraw.Draw(canvas)
# headline
text(d, (W // 2, 870), "ES TEH", BANG, 250, YEL, stroke=16)
# red arrow toward the glass
d.polygon([(110, 1215), (230, 1205), (222, 1160), (330, 1240), (232, 1320), (232, 1275), (114, 1285)],
          fill=RED, outline=BLK, width=7)
# bottom red torn banner with question
ban = Image.new("RGBA", (W + 40, 420), RED + (255,))
canvas.paste(ban, (-20, 1520), torn_mask(W + 40, 420, "t", amp=24))
d = ImageDraw.Draw(canvas)
text(d, (W // 2, 1612), "LAHIR DARI", BANG, 130, WHT, stroke=11)
text(d, (W // 2, 1755), "TANAM PAKSA?!", BANG, 160, YEL, stroke=13)
sticker(canvas, "TEH CELUP KARENA SALAH PAHAM?", (W // 2, 1862), 50, WHT, BLK, angle=-2, pad=(20, 6))

out = os.path.join(ROOT, "thumbnail_part2_kolase_1080x1920.jpg")
canvas.convert("RGB").save(out, quality=94)
canvas.convert("RGB").resize((540, 960)).save(os.path.join(S, "thumb_kolase_small.jpg"))
print(out)
