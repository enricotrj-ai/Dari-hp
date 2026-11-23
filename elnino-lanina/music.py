import numpy as np, wave, sys
D=float(sys.argv[1]); sr=48000; n=int(D*sr); t=np.arange(n)/sr
def note(f): return 440*2**((f-69)/12)
# slow chord progression (Am - F - C - G), 4 s per chord, soft pads + subtle pulse at 100 BPM
chords=[[57,60,64,69],[53,57,60,65],[48,55,60,64],[55,59,62,67]]
out=np.zeros(n)
for ci in range(int(D//4)+2):
    st=ci*4.0; seg=(t>=st-0.5)&(t<st+4.5)
    env=np.clip((t-st+0.5)/1.2,0,1)*np.clip((st+4.5-t)/1.2,0,1)
    for m in chords[ci%4]:
        f=note(m)
        for det in (-0.08,0.08):
            out+=seg*env*0.05*np.sin(2*np.pi*f*(1+det/100)*t+det)
        out+=seg*env*0.02*np.sin(2*np.pi*f*2*t)
    out+=seg*env*0.06*np.sin(2*np.pi*note(chords[ci%4][0]-12)*t)
beat=60/100; ph=(t%beat)/beat
out+=0.05*np.sin(2*np.pi*55*t)*np.exp(-ph*10)                 # soft kick-like pulse
hh=np.random.default_rng(1).standard_normal(n)*np.exp(-((t+beat/2)%beat)/beat*40)*0.012
out+=hh
out*=np.clip(t/1.5,0,1)
out/=np.max(np.abs(out))*1.25
st=np.stack([out,np.roll(out,240)],1)
w=wave.open(sys.argv[2],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
