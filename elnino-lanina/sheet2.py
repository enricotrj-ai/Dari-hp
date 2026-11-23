from PIL import Image, ImageDraw, ImageFont
import textwrap, sys
F='/usr/share/fonts/opentype/inter/'
fb=ImageFont.truetype(F+'Inter-ExtraBold.otf',22); fm=ImageFont.truetype(F+'Inter-Medium.otf',17); ft=ImageFont.truetype(F+'Inter-ExtraBold.otf',34); fs=ImageFont.truetype(F+'Inter-Medium.otf',20)
rows=[("0:00","Intro","(title, globe fades in)"),
("0:02","Hook","Why does the planet run a fever,"),
("0:04","Hook","then get drenched?"),
("0:06","Hook","Blame the Pacific."),
("0:08","Normal","Normally, trade winds push warm water west,"),
("0:10","Normal","while cold water rises in the east."),
("0:13","El Niño","When those winds weaken, warm water sloshes east"),
("0:15","El Niño","and cold upwelling stops: El Niño."),
("0:17","El Niño","Global temperatures spike."),
("0:19","El Niño","Peru floods;"),
("0:20","El Niño","Australia dries out."),
("0:23","Transition","When that heat runs out, cold water surges back"),
("0:26","La Niña","and the winds strengthen: La Niña."),
("0:28","La Niña","Now Australia floods,"),
("0:30","La Niña","and the southern US dries out."),
("0:35","Closing","Right now, a strong El Niño is expected to last into early 2027.")]
W,H=340,604; CAP=96; pad=10; cols=8
SW=cols*W+(cols+1)*pad; SH=110+2*(H+CAP)+3*pad
sheet=Image.new('RGB',(SW,SH),(5,9,22)); d=ImageDraw.Draw(sheet)
d.text((pad+4,24),"STORYBOARD v2 — El Niño to La Niña: The Global Swing",font=ft,fill=(246,243,236))
d.text((pad+4,70),"9:16 · 1080×1920 · 30 fps · ±40 s (timing estimated, before voiceover) · frames rendered from the animation code",font=fs,fill=(154,168,196))
tagc={'Hook':(255,210,51),'Normal':(143,211,255),'El Niño':(255,106,42),'La Niña':(61,139,255),'Transition':(200,200,220),'Intro':(200,200,220),'Closing':(255,210,51)}
for i,(tm,tag,vo) in enumerate(rows):
    r,c=divmod(i,cols); x=pad+c*(W+pad); y=110+r*(H+CAP+pad)
    im=Image.open(f'sb2/{i:02d}.png').convert('RGB').resize((W,H),Image.LANCZOS); sheet.paste(im,(x,y))
    lab=f"{i+1:02d} · {tm}"; d.rectangle([x,y,x+W,y+30],fill=(5,9,22)); d.text((x+8,y+4),lab,font=fb,fill=(246,243,236))
    tw=d.textlength(tag,font=fb); d.rounded_rectangle([x+W-tw-20,y+3,x+W-4,y+28],radius=12,fill=tagc[tag]); d.text((x+W-tw-12,y+4),tag,font=fb,fill=(14,18,32))
    ty=y+H+8
    for ln in textwrap.wrap('“'+vo+'”',34)[:4]: d.text((x+4,ty),ln,font=fm,fill=(205,214,232)); ty+=21
sheet.save(sys.argv[1])
