from PIL import Image, ImageDraw, ImageFont
import textwrap, sys
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-ExtraBold.otf',22); fm=ImageFont.truetype(F+'Inter-Medium.otf',17); ft=ImageFont.truetype(F+'Inter-ExtraBold.otf',34); fs=ImageFont.truetype(F+'Inter-Medium.otf',20)
rows=[("0:00","Intro","(title, globe fades in)"),
("0:02","Hook","Why does Indonesia bake in drought one year,"),
("0:04","Hook","then drown in floods the next?"),
("0:07","Hook","The answer lies in the Pacific Ocean."),
("0:10","Normal","Normally, trade winds blow from east to west."),
("0:13","Normal","They push warm ocean water toward Indonesia."),
("0:18","Normal","That warm water evaporates, forms clouds, and falls as rain."),
("0:21","El Niño","When El Niño arrives, the trade winds weaken."),
("0:25","El Niño","Warm water drifts east, away from Indonesia."),
("0:34","El Niño","The result: long dry seasons, rising heat, drought, and forest fires."),
("0:36","Transition","Then the pendulum swings back."),
("0:39","La Niña","The trade winds grow stronger, and warm water piles up around Indonesia."),
("0:44","La Niña","More evaporation, thicker clouds, heavier rain."),
("0:47","La Niña","This is La Niña,"),
("0:49","La Niña","the trigger for floods and landslides."),
("0:54","Closing","Heat and floods are part of the same cycle. Know the signs, and prepare early.")]
W,H=340,604; CAP=96; pad=10; cols=8
SW=cols*W+(cols+1)*pad; SH=110+2*(H+CAP)+3*pad
sheet=Image.new('RGB',(SW,SH),(5,9,22)); d=ImageDraw.Draw(sheet)
d.text((pad+4,24),"STORYBOARD — El Niño & La Niña: What Causes the Heat and the Floods",font=ft,fill=(246,243,236))
d.text((pad+4,70),"9:16 · 1080×1920 · 30 fps · 57 s (1.710 frames) · VO: ElevenLabs “Ryan” · frames rendered from the animation code",font=fs,fill=(154,168,196))
tagc={'Hook':(255,210,51),'Normal':(143,211,255),'El Niño':(255,106,42),'La Niña':(61,139,255),'Transition':(200,200,220),'Intro':(200,200,220),'Closing':(255,210,51)}
for i,(tm,tag,vo) in enumerate(rows):
    r,c=divmod(i,cols); x=pad+c*(W+pad); y=110+r*(H+CAP+pad)
    im=Image.open(f'sb/{i:02d}.png').convert('RGB').resize((W,H),Image.LANCZOS); sheet.paste(im,(x,y))
    lab=f"{i+1:02d} · {tm}"; d.rectangle([x,y,x+W,y+30],fill=(5,9,22)); d.text((x+8,y+4),lab,font=fb,fill=(246,243,236))
    tw=d.textlength(tag,font=fb); d.rounded_rectangle([x+W-tw-20,y+3,x+W-4,y+28],radius=12,fill=tagc[tag]); d.text((x+W-tw-12,y+4),tag,font=fb,fill=(14,18,32))
    ty=y+H+8
    for ln in textwrap.wrap('“'+vo+'”',34)[:4]: d.text((x+4,ty),ln,font=fm,fill=(205,214,232)); ty+=21
sheet.save(sys.argv[1])
