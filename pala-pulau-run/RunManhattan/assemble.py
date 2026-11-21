#!/usr/bin/env python3
"""Assemble "The City Traded for a Fruit" (9:16, 1080x1920, 30 fps) from scenes.json.

Usage:  python3 assemble.py [--no-scale] [--out final.mp4]

Needs ffmpeg/ffprobe and Pillow. Put the downloaded assets in ./assets/
(voiceover.mp3, scene1.mp4, scene2.png ... scene8.mp4, optional music.mp3).
Scene timings in scenes.json are for a 60 s voiceover; by default they are
stretched proportionally to the real voiceover length.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + " ".join(cmd) + "\n" + r.stderr[-3000:])
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).strip())


def crop_overlay(png, tmp):
    """Crop a full-frame transparent PNG to its text box; return (path, cx, cy)."""
    im = Image.open(png).convert("RGBA")
    l, t, r, b = im.getchannel("A").getbbox()
    pad = 20
    box = (max(0, l - pad), max(0, t - pad), min(W, r + pad), min(H, b + pad))
    out = os.path.join(tmp, "ov_" + os.path.basename(png))
    im.crop(box).save(out)
    return out, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


MOTIONS = {
    # zoompan expressions; d = total frames, on = output frame index
    "zoom_in": ("min(1.0+0.12*on/{d},1.12)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_out": ("1.12-0.12*on/{d}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan_up": ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/{d})"),
    "zoom_in_left": ("min(1.0+0.12*on/{d},1.12)", "(iw-iw/zoom)*(0.5-0.5*on/{d})", "ih/2-(ih/zoom/2)"),
}


def build_scene(sc, dur, tmp):
    out = os.path.join(tmp, f"seg{sc['n']:02d}.mp4")
    src = os.path.join(HERE, sc["asset"])
    if not os.path.exists(src):
        sys.exit(f"Missing asset for scene {sc['n']}: {sc['asset']}")
    frames = max(1, round(dur * FPS))
    kw = sc.get("keyword")
    inputs, chain = [], []
    if sc["asset_type"] == "image" and sc.get("motion", "").startswith("pan_wide"):
        # gambar lebar (16:9): jendela 9:16 bergeser horizontal dari pan_from ke pan_to (0..1)
        p0, p1 = sc.get("pan_from", 0.0), sc.get("pan_to", 1.0)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", src]
        chain.append(f"[0:v]scale=-2:{H},crop=w={W}:h={H}:"
                     f"x='(iw-ow)*({p0}+({p1}-{p0})*t/{dur:.3f})':y=0,setsar=1[base]")
    elif sc["asset_type"] == "image":
        z, x, y = (e.format(d=frames) for e in MOTIONS.get(sc.get("motion", "zoom_in"), MOTIONS["zoom_in"]))
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", src]
        chain.append(f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                     f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},setsar=1[base]")
    else:
        clip = duration(src)
        inputs += ["-i", src]
        if dur > clip * 1.6:
            # too long even at 1.6x: play forward then backward (ping-pong), each half slowed
            slow = (dur / 2) / clip
            chain.append(f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                         f"split[fw][r0];[r0]reverse[bw];[fw][bw]concat=n=2:v=1,"
                         f"setpts={slow:.4f}*PTS,fps={FPS},tpad=stop_mode=clone:stop_duration=0.2,"
                         f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,setsar=1[base]")
        else:
            slow = max(1.0, dur / clip)                  # slow down to fill the scene
            chain.append(f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                         f"setpts={slow:.4f}*PTS,tpad=stop_mode=clone:stop_duration=0.2,"
                         f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,setsar=1[base]")
    last = "base"
    if kw and os.path.exists(os.path.join(HERE, kw["overlay"])):
        ov, cx, cy = crop_overlay(os.path.join(HERE, kw["overlay"]), tmp)
        at, hold = float(kw["at"]), float(kw["hold"])
        at = min(at, max(0.0, dur - 0.6)); hold = min(hold, dur - at)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", ov]
        # pop: scale 60% -> 112% -> 100% over 0.25 s, fade out at the end of the hold
        s = (f"if(lt(t,{at}),0.6,if(lt(t,{at}+0.15),0.6+(t-{at})/0.15*0.52,"
             f"if(lt(t,{at}+0.25),1.12-(t-{at}-0.15)/0.1*0.12,1)))")
        chain.append(f"[1:v]format=rgba,scale=w='iw*({s})':h='ih*({s})':eval=frame,"
                     f"fade=t=in:st={at}:d=0.12:alpha=1,fade=t=out:st={at + hold - 0.2:.3f}:d=0.2:alpha=1[kw]")
        chain.append(f"[{last}][kw]overlay=x='{cx}-w/2':y='{cy}-h/2':eval=frame:"
                     f"enable='between(t,{at},{at + hold:.3f})'[v]")
        last = "v"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{last}]",
         "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-scale", action="store_true", help="use scenes.json timings as-is")
    ap.add_argument("--out", default=os.path.join(HERE, "RunManhattan_final_9x16.mp4"))
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "scenes.json")))
    vo = os.path.join(HERE, cfg["voiceover"]["file"])
    if not os.path.exists(vo):
        sys.exit("Missing voiceover: " + cfg["voiceover"]["file"])
    vo_len = duration(vo)
    total = cfg["scenes"][-1]["end"]
    k = 1.0 if a.no_scale else (vo_len + 0.6) / total
    print(f"voiceover {vo_len:.2f}s -> timing scale x{k:.3f}")
    tmp = tempfile.mkdtemp(prefix="rm_")
    try:
        segs = []
        for sc in cfg["scenes"]:
            d = (sc["end"] - sc["start"]) * k
            sc = dict(sc); kw = sc.get("keyword")
            if kw: sc["keyword"] = dict(kw, at=kw["at"] * k)
            print(f"  scene {sc['n']}: {d:.2f}s ({sc['asset_type']})")
            segs.append(build_scene(sc, d, tmp))
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
        video = os.path.join(tmp, "video.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
        vlen = duration(video)
        music = os.path.join(HERE, cfg["music"]["file"])
        inputs = ["-i", video, "-i", vo]
        # voiceover dinormalkan ke -16 LUFS; musik dinormalkan juga lalu diturunkan volume_db di bawah suara;
        # hasil campuran akhirnya -14 LUFS (standar TikTok/Shorts/Reels)
        vo_chain = "[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad"
        final = "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000"
        if os.path.exists(music):
            inputs += ["-i", music]  # tidak di-loop: musik dibuat sepanjang video
            af = (f"{vo_chain}[vo];[2:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,"
                  f"volume={cfg['music']['volume_db']}dB,apad,"
                  f"afade=t=out:st={max(0, vlen - 2):.2f}:d=2[mu];[vo][mu]amix=inputs=2:duration=first:normalize=0,"
                  f"{final}[a]")
        else:
            af = f"{vo_chain},{final}[a]"
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", af, "-map", "0:v", "-map", "[a]",
             "-t", f"{vlen:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out])
        print(f"done: {a.out} ({duration(a.out):.2f}s)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
