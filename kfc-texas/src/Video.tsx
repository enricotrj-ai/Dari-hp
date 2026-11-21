import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  Easing,
} from "remotion";
import timeline from "./timeline.json";
import { MapBg, planoScreen } from "./MapBg";

/* ---------------- fonts (plain @font-face, local files) ---------------- */
const FONT_CSS = `
@font-face{font-family:Anton;src:url(${staticFile("anton.woff2")}) format("woff2");font-display:block}
@font-face{font-family:Inter;font-weight:800;src:url(${staticFile("inter800.woff2")}) format("woff2");font-display:block}
@font-face{font-family:Inter;font-weight:600;src:url(${staticFile("inter600.woff2")}) format("woff2");font-display:block}`;

/* ---------------- tokens ---------------- */
const FPS = 30;
const C = {
  paper: "#F2E8D5",
  paper2: "#E8DABF",
  ink: "#1C1A17",
  red: "#D62828",
  redDark: "#9E1B1B",
  yellow: "#FFD23F",
  green: "#2A9D8F",
  grey: "#A49C8E",
  white: "#FFFDF8",
  brown: "#B86B2B",
};
const SHADOW = "0 4px 0 #1C1A17, 0 0 24px rgba(0,0,0,0.6)";
const HEAD = "Anton, Impact, sans-serif";
const BODY = "Inter, Arial, sans-serif";

const SEG = timeline.segments;
const S = (i: number) => SEG[i].start;
const E = (i: number) => SEG[i].end;
const SCENES = [0, S(2) - 0.1, S(6) - 0.15, S(9) - 0.15, S(13) - 0.15, S(16) - 0.15, S(19) - 0.15, timeline.total];

/* ---------------- animation helpers ---------------- */
const pop = (t: number, at: number, damping = 10, stiffness = 190) =>
  t < at ? 0 : spring({ frame: (t - at) * FPS, fps: FPS, config: { damping, stiffness, mass: 0.7 } });
const ease = (t: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(t, [a, b], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

const Pop: React.FC<{
  t: number;
  at: number;
  out?: number;
  x?: number;
  y?: number;
  rot?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ t, at, out, x = 540, y = 960, rot = 0, children, style }) => {
  let s = pop(t, at);
  if (out !== undefined) s *= 1 - ease(t, out, out + 0.18);
  if (s <= 0.001) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(-50%,-50%) scale(${s}) rotate(${rot * (1.2 - 0.2 * s)}deg)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* Bold cut-paper label: text on a coloured slab with a hard offset shadow */
const Slab: React.FC<{
  children: React.ReactNode;
  bg?: string;
  color?: string;
  size?: number;
  pad?: string;
  font?: string;
}> = ({ children, bg = C.ink, color = C.white, size = 110, pad = "10px 34px 14px", font = HEAD }) => (
  <div
    style={{
      background: bg,
      color,
      fontFamily: font,
      fontWeight: 800,
      fontSize: size,
      lineHeight: 1.02,
      padding: pad,
      whiteSpace: "nowrap",
      boxShadow: `10px 12px 0 ${C.ink}`,
      border: `5px solid ${C.ink}`,
      letterSpacing: 1,
      textAlign: "center",
    }}
  >
    {children}
  </div>
);

/* ---------------- illustrations (all original, no brand marks) ---------------- */
const Bucket: React.FC<{ size?: number }> = ({ size = 520 }) => (
  <svg width={size} height={size * 1.1} viewBox="0 0 200 220">
    {[
      [60, 40], [95, 28], [130, 40], [78, 22], [115, 18], [148, 52], [48, 58],
    ].map(([cx, cy], i) => (
      <ellipse key={i} cx={cx} cy={cy + 10} rx={26} ry={20} fill={i % 2 ? "#C9782F" : C.brown} stroke={C.ink} strokeWidth={4} />
    ))}
    <clipPath id="bk">
      <path d="M28 70 L172 70 L152 210 L48 210 Z" />
    </clipPath>
    <g clipPath="url(#bk)">
      <rect x="0" y="60" width="200" height="160" fill={C.white} />
      {[0, 1, 2, 3, 4, 5, 6].map((i) => (
        <rect key={i} x={20 + i * 24} y="60" width="12" height="160" fill={C.red} />
      ))}
    </g>
    <path d="M28 70 L172 70 L152 210 L48 210 Z" fill="none" stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
    <rect x="20" y="62" width="160" height="18" rx="4" fill={C.white} stroke={C.ink} strokeWidth={6} />
  </svg>
);

const Store: React.FC<{ dead?: number; size?: number }> = ({ dead = 0, size = 64 }) => {
  const body = dead > 0.5 ? "#8E877B" : C.white;
  const awning = dead > 0.5 ? "#6E685E" : C.red;
  return (
    <svg width={size} height={size} viewBox="0 0 64 64">
      <rect x="8" y="26" width="48" height="32" fill={body} stroke={C.ink} strokeWidth="4" />
      <path d="M4 26 L10 10 L54 10 L60 26 Z" fill={awning} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
      <path d="M18 10 L15 26 M32 10 L32 26 M46 10 L49 26" stroke={dead > 0.5 ? "#9A948A" : C.white} strokeWidth="4" />
      <rect x="25" y="38" width="14" height="20" fill={dead > 0.5 ? "#5A554D" : C.yellow} stroke={C.ink} strokeWidth="3" />
      {dead > 0.5 && <path d="M12 30 L52 56 M52 30 L12 56" stroke={C.red} strokeWidth="6" strokeLinecap="round" />}
    </svg>
  );
};

const Worker: React.FC<{ size?: number; color?: string }> = ({ size = 70, color = C.ink }) => (
  <svg width={size} height={size * 1.4} viewBox="0 0 50 70">
    <circle cx="25" cy="14" r="11" fill={color} />
    <path d="M6 70 L6 44 Q6 30 25 30 Q44 30 44 44 L44 70 Z" fill={color} />
  </svg>
);

const Drumstick: React.FC<{ size?: number }> = ({ size = 420 }) => (
  <svg width={size} height={size} viewBox="0 0 200 200">
    <path d="M70 40 Q120 10 150 50 Q180 95 130 125 L110 140 Q80 160 60 130 Q30 90 70 40 Z" fill={C.brown} stroke={C.ink} strokeWidth="7" />
    <path d="M78 60 Q90 52 100 60 M118 72 Q128 66 136 76 M88 96 Q100 90 108 100" stroke="#8A4A18" strokeWidth="6" fill="none" strokeLinecap="round" />
    <rect x="92" y="128" width="22" height="48" rx="8" transform="rotate(30 103 152)" fill={C.white} stroke={C.ink} strokeWidth="7" />
    <circle cx="76" cy="182" r="13" fill={C.white} stroke={C.ink} strokeWidth="7" />
    <circle cx="96" cy="190" r="13" fill={C.white} stroke={C.ink} strokeWidth="7" />
  </svg>
);

const Heart: React.FC<{ size?: number }> = ({ size = 120 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 88 L12 50 Q-4 26 22 14 Q40 8 50 28 Q60 8 78 14 Q104 26 88 50 Z" fill={C.red} stroke={C.ink} strokeWidth="6" strokeLinejoin="round" />
  </svg>
);

// Simplified, hand-drawn style Texas silhouette
const TEXAS =
  "M22 2 L40 2 L40 32 L56 35 L72 38 L86 37 L94 42 L96 60 L90 70 L78 78 L68 87 L64 100 L54 97 L46 86 L40 74 L32 68 L24 64 L16 54 L2 42 L22 42 Z";

const Star: React.FC<{ size?: number; fill?: string }> = ({ size = 60, fill = C.yellow }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 4 L62 38 L98 38 L69 59 L80 94 L50 72 L20 94 L31 59 L2 38 L38 38 Z" fill={fill} stroke={C.ink} strokeWidth="6" strokeLinejoin="round" />
  </svg>
);

const Building: React.FC<{ w?: number }> = ({ w = 300 }) => (
  <svg width={w} height={w * 0.9} viewBox="0 0 100 90">
    <rect x="10" y="20" width="80" height="68" fill={C.white} stroke={C.ink} strokeWidth="4" />
    <path d="M4 22 L50 2 L96 22 Z" fill={C.red} stroke={C.ink} strokeWidth="4" strokeLinejoin="round" />
    {[0, 1, 2].map((r) =>
      [0, 1, 2, 3].map((c) => (
        <rect key={`${r}${c}`} x={18 + c * 18} y={30 + r * 16} width="10" height="9" fill={C.yellow} stroke={C.ink} strokeWidth="2" />
      ))
    )}
    <rect x="42" y="72" width="16" height="16" fill={C.ink} />
  </svg>
);

/* Hand-drawn circle / underline strokes */
const Scribble: React.FC<{ t: number; at: number; w: number; h: number; color?: string; kind?: "circle" | "under" }> = ({
  t, at, w, h, color = C.red, kind = "circle",
}) => {
  const p = ease(t, at, at + 0.45);
  const d =
    kind === "circle"
      ? `M ${w * 0.1} ${h * 0.3} C ${w * 0.3} ${-h * 0.05}, ${w * 0.95} ${-h * 0.05}, ${w * 0.97} ${h * 0.45} C ${w} ${h * 1.05}, ${w * 0.05} ${h * 1.08}, ${w * 0.03} ${h * 0.5} C ${w * 0.02} ${h * 0.2}, ${w * 0.3} ${h * 0.05}, ${w * 0.45} ${h * 0.06}`
      : `M 0 ${h * 0.6} Q ${w * 0.5} ${h * 0.2} ${w} ${h * 0.55}`;
  return (
    <svg width={w} height={h} style={{ position: "absolute", overflow: "visible", pointerEvents: "none" }}>
      <path d={d} fill="none" stroke={color} strokeWidth={12} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
    </svg>
  );
};

/* ---------------- scenes ---------------- */
type SP = { t: number }; // t = seconds since scene start
const local = (i: number, scene: number) => S(i) - SCENES[scene];

// 1. KFC... BANKRUPT?!
const Scene1: React.FC<SP> = ({ t }) => {
  const drop = pop(t, 0.05, 9, 140);
  const hit = local(1, 0) + 0.35;
  const crack = ease(t, hit, hit + 0.12);
  return (
    <>
      <div style={{ position: "absolute", left: 540, top: interpolate(drop, [0, 1], [-400, 900]), transform: "translate(-50%,-50%)" }}>
        <Bucket size={560} />
      </div>
      <Pop t={t} at={0.1} x={540} y={330} rot={-4}>
        <Slab bg={C.white} color={C.ink} size={150}>KFC...</Slab>
      </Pop>
      {crack > 0 && (
        <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
          {[
            "M540 900 L420 760 L380 600 L300 520",
            "M540 900 L700 780 L760 640 L880 560",
            "M540 900 L600 1100 L560 1300 L640 1500",
            "M540 900 L360 1020 L220 1000 L120 1120",
            "M540 900 L760 1040 L920 1020",
          ].map((d, i) => (
            <path key={i} d={d} stroke={C.white} strokeWidth={9} fill="none" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - crack} strokeLinejoin="round" />
          ))}
        </svg>
      )}
      <Pop t={t} at={hit} x={540} y={1330} rot={-6}>
        <Slab bg={C.red} size={190} pad="6px 40px 16px">BANKRUPT?!</Slab>
      </Pop>
    </>
  );
};

// 2. 84 stores, 44 closed, 1,600 workers
const Scene2: React.FC<SP> = ({ t }) => {
  const a2 = local(2, 1), a3 = local(3, 1), a4 = local(4, 1), a5 = local(5, 1);
  const closed = new Set<number>();
  for (let i = 0; closed.size < 44; i++) closed.add(Math.floor(random(`c${i}`) * 84));
  const order = [...closed];
  const up = ease(t, a4 - 0.1, a4 + 0.35);
  const count = Math.round(ease(t, a2, a2 + 0.9, 0, 84));
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, transform: `translateY(${-up * 190}px) scale(${1 - up * 0.22})`, transformOrigin: "540px 300px" }}>
        <Pop t={t} at={a2 - 0.05} x={540} y={300}>
          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <Slab size={150} bg={C.ink}>{count}</Slab>
            <div style={{ fontFamily: HEAD, fontSize: 92, color: C.white, lineHeight: 0.95, textShadow: SHADOW }}>STORES<br />AT RISK</div>
          </div>
        </Pop>
        <div style={{ position: "absolute", left: 60, top: 470, width: 960, display: "flex", flexWrap: "wrap", gap: 16 }}>
          {Array.from({ length: 84 }).map((_, i) => {
            const s = pop(t, a2 + i * 0.012, 12, 240);
            const k = order.indexOf(i);
            const dead = k >= 0 ? ease(t, a3 + 0.2 + k * 0.03, a3 + 0.25 + k * 0.03) : 0;
            return (
              <div key={i} style={{ transform: `scale(${s * (1 - dead * 0.12)}) rotate(${dead * (random(`r${i}`) * 16 - 8)}deg)` }}>
                <Store dead={dead} size={64} />
              </div>
            );
          })}
        </div>
        <Pop t={t} at={a3 + 0.1} x={540} y={1190} rot={3}>
          <Slab bg={C.red} size={104}>44 ALREADY CLOSED</Slab>
        </Pop>
      </div>
      {/* workers */}
      <div style={{ position: "absolute", left: 90, top: 1060, width: 900, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 10 }}>
        {Array.from({ length: 24 }).map((_, i) => {
          const s = pop(t, a4 + i * 0.02, 12, 240);
          const swing = t > a5 ? Math.sin((t - a5) * 9 + i) * 10 * ease(t, a5, a5 + 0.2) : 0;
          return (
            <div key={i} style={{ transform: `scale(${s}) rotate(${swing}deg)`, transformOrigin: "50% 0%" }}>
              <Worker size={62} color={i % 5 === 2 ? C.red : C.white} />
            </div>
          );
        })}
      </div>
      <Pop t={t} at={a4 + 0.15} x={540} y={1360} rot={-3}>
        <Slab bg={C.yellow} color={C.ink} size={110}>1,600+ WORKERS</Slab>
      </Pop>
      <Pop t={t} at={a5} x={900} y={980} rot={12}>
        <div style={{ fontFamily: HEAD, fontSize: 260, color: C.red, WebkitTextStroke: `8px ${C.ink}`, transform: `rotate(${Math.sin(t * 6) * 8}deg)` }}>?</div>
      </Pop>
    </>
  );
};

// 3. People still love fried chicken... what went wrong?
const Scene3: React.FC<SP> = ({ t }) => {
  const a6 = local(6, 2), a7 = local(7, 2), a8 = local(8, 2);
  const shrink = ease(t, a8 - 0.1, a8 + 0.25);
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, transform: `translateY(${-shrink * 380}px) scale(${1 - shrink * 0.35})`, transformOrigin: "540px 700px" }}>
        <Pop t={t} at={a6 - 0.15} x={540} y={720} rot={-8}>
          <div style={{ transform: `rotate(${Math.sin(t * 3) * 4}deg)` }}><Drumstick size={500} /></div>
        </Pop>
        {[[230, 430, -14], [850, 470, 12], [880, 920, 8]].map(([x, y, r], i) => (
          <Pop key={i} t={t} at={a6 + 0.35 + i * 0.15} x={x} y={y + Math.sin(t * 4 + i) * 12} rot={r}>
            <Heart size={140} />
          </Pop>
        ))}
        <Pop t={t} at={a6 + 0.5} x={540} y={1150} rot={2}>
          <Slab bg={C.white} color={C.ink} size={92}>PEOPLE STILL LOVE IT</Slab>
        </Pop>
      </div>
      <Pop t={t} at={a7} out={a8 - 0.05} x={540} y={1380}>
        <div style={{ fontFamily: HEAD, fontSize: 160, color: C.white, textShadow: SHADOW }}>SO...</div>
      </Pop>
      <Pop t={t} at={a8} x={540} y={1260} rot={-4}>
        <div style={{ transform: `rotate(${Math.sin(t * 14) * 2 * (1 - ease(t, a8, a8 + 0.8))}deg)` }}>
          <Slab bg={C.red} size={150} pad="8px 34px 16px">WHAT WENT<br />WRONG?</Slab>
        </div>
      </Pop>
    </>
  );
};

// 4. Sales down, costs up, profit 11.8% -> 4%
const Scene4: React.FC<SP> = ({ t }) => {
  const a9 = local(9, 3), a10 = local(10, 3), a11 = local(11, 3), a12 = local(12, 3);
  const draw = ease(t, a9 + 0.1, a9 + 1.4);
  const margin = interpolate(t, [a11 + 0.3, a12 + 0.4], [11.8, 4], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const panelOut = ease(t, a11 - 0.2, a11 + 0.15);
  const chart = "M60 60 L160 90 L250 80 L340 150 L430 170 L520 250 L610 260 L700 340 L760 330";
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, opacity: 1 - panelOut, transform: `translateX(${-panelOut * 300}px)` }}>
        <Pop t={t} at={a9 - 0.15} x={540} y={330} rot={-2}>
          <Slab bg={C.ink} size={104}>SALES ▼ 15.6%</Slab>
        </Pop>
        <Pop t={t} at={a9 - 0.05} x={540} y={720}>
          <div style={{ width: 860, height: 440, background: C.white, border: `6px solid ${C.ink}`, boxShadow: `12px 14px 0 ${C.ink}`, position: "relative" }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ position: "absolute", left: 0, right: 0, top: i * 110, borderTop: `3px dashed ${C.grey}` }} />
            ))}
            <svg width={860} height={440} style={{ position: "absolute", left: 0, top: 0 }}>
              <path d={chart} stroke={C.red} strokeWidth={16} fill="none" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} />
            </svg>
            <div style={{ position: "absolute", left: 24, bottom: 14, fontFamily: BODY, fontWeight: 600, fontSize: 30, color: C.ink }}>last 3 fiscal years</div>
          </div>
        </Pop>
        <Pop t={t} at={a10} x={540} y={1210} rot={3}>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 18 }}>
            {[0, 1, 2, 3].map((i) => (
              <div key={i} style={{ width: 80, height: 60 + ease(t, a10 + i * 0.12, a10 + 0.5 + i * 0.12) * (60 + i * 60), background: C.red, border: `5px solid ${C.ink}` }} />
            ))}
            <Slab bg={C.red} size={104}>COSTS ▲</Slab>
          </div>
        </Pop>
      </div>
      {/* profit margin */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, opacity: panelOut }}>
        <Pop t={t} at={a11 - 0.05} x={540} y={360}>
          <Slab bg={C.white} color={C.ink} size={96}>PROFIT PER STORE</Slab>
        </Pop>
        <div style={{ position: "absolute", left: 540, top: 1500, transform: "translate(-50%,-100%)", display: "flex", alignItems: "flex-end", gap: 80 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ width: 240, height: 11.8 * 45 * pop(t, a11), background: C.green, border: `6px solid ${C.ink}`, boxShadow: `10px 0 0 ${C.ink}` }} />
            <div style={{ fontFamily: HEAD, fontSize: 70, color: C.white, marginTop: 10, textShadow: SHADOW }}>2023</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ width: 240, height: margin * 45 * pop(t, a11 + 0.2), background: margin < 6 ? C.red : C.yellow, border: `6px solid ${C.ink}`, boxShadow: `10px 0 0 ${C.ink}` }} />
            <div style={{ fontFamily: HEAD, fontSize: 70, color: C.white, marginTop: 10, textShadow: SHADOW }}>2026</div>
          </div>
        </div>
        <Pop t={t} at={a11 + 0.1} x={340} y={560}>
          <div style={{ fontFamily: HEAD, fontSize: 120, color: C.green, WebkitTextStroke: `4px ${C.ink}` }}>11.8%</div>
        </Pop>
        <Pop t={t} at={a11 + 0.3} x={740} y={560}>
          <div style={{ fontFamily: HEAD, fontSize: 140 + ease(t, a12, a12 + 0.2) * 40, color: C.red, WebkitTextStroke: `4px ${C.ink}` }}>
            {margin.toFixed(1)}%
          </div>
        </Pop>
        {t > a12 && (
          <div style={{ position: "absolute", left: 570, top: 440 }}>
            <Scribble t={t} at={a12} w={340} h={240} />
          </div>
        )}
      </div>
    </>
  );
};

// 5. The reveal: it's happening in TEXAS (the map does the heavy lifting)
const Scene5: React.FC<SP> = ({ t }) => {
  const a13 = local(13, 4), a14 = local(14, 4), a15 = local(15, 4);
  const noteOut = ease(t, a14 - 0.15, a14 + 0.1);
  return (
    <>
      <div style={{ opacity: 1 - noteOut }}>
        <Pop t={t} at={a13 - 0.15} x={540} y={820} rot={-3}>
          <div style={{ width: 820, padding: "60px 50px", background: C.yellow, border: `6px solid ${C.ink}`, boxShadow: `14px 16px 0 ${C.ink}`, fontFamily: HEAD, fontSize: 118, lineHeight: 1.05, color: C.ink, textAlign: "center" }}>
            WHAT MOST PEOPLE DON'T KNOW...
          </div>
          <div style={{ position: "absolute", left: 330, top: -40, width: 160, height: 60, background: "rgba(255,255,255,0.65)", transform: "rotate(-4deg)", border: "2px solid rgba(0,0,0,0.15)" }} />
        </Pop>
      </div>
      <Pop t={t} at={a14} out={a15 - 0.1} x={540} y={300}>
        <Slab bg={C.green} size={96}>NOT EVERYWHERE</Slab>
      </Pop>
      <Pop t={t} at={a15 + 0.35} x={540} y={300} rot={-4}>
        <Slab bg={C.white} color={C.red} size={200} pad="0 50px 10px">TEXAS</Slab>
      </Pop>
    </>
  );
};

// 6. Tasty Chick'n, franchisee, $15.7M
const Scene6: React.FC<SP> = ({ t }) => {
  const a16 = local(16, 5), a17 = local(17, 5), a18 = local(18, 5);
  const cardOut = ease(t, a18 - 0.15, a18 + 0.15);
  const tear = ease(t, a18 + 0.5, a18 + 1.1);
  const money = interpolate(t, [a18 + 1.5, a18 + 3.6], [0, 15.7], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const [px, py] = planoScreen(t + SCENES[5]);
  return (
    <>
      <div style={{ opacity: 1 - cardOut }}>
        <Pop t={t} at={a16 - 0.15} x={540} y={220} rot={2}>
          <Slab bg={C.red} size={80}>THE BANKRUPT COMPANY:</Slab>
        </Pop>
        <Pop t={t} at={a16 + 1.0} x={540} y={380} rot={-3}>
          <Slab bg={C.ink} size={130}>TASTY CHICK'N</Slab>
        </Pop>
        {/* HQ label that follows the Plano pin on the map */}
        {pop(t, a16 + 1.2) > 0 && (
          <div style={{ position: "absolute", left: px, top: py - 36, transform: `translate(-50%,-100%) scale(${pop(t, a16 + 1.2)})`, fontFamily: BODY, fontWeight: 800, fontSize: 34, color: C.ink, background: C.yellow, border: `4px solid ${C.ink}`, padding: "4px 14px", whiteSpace: "nowrap", boxShadow: `5px 6px 0 ${C.ink}` }}>
            HQ: PLANO, TEXAS
          </div>
        )}
        <Pop t={t} at={a17 + 0.4} x={540} y={1250} rot={2}>
          <div style={{ position: "relative" }}>
            <Slab bg={C.white} color={C.ink} size={92}>84 STORES · 10 STATES</Slab>
            <div style={{ position: "absolute", right: -30, top: -118, transform: `rotate(10deg) scale(${pop(t, a17 + 1.0, 8, 200)})` }}>
              <div style={{ border: `8px solid ${C.red}`, color: C.red, fontFamily: HEAD, fontSize: 70, padding: "0 18px", background: "rgba(255,253,248,0.92)" }}>BANKRUPT</div>
            </div>
          </div>
        </Pop>
        <Pop t={t} at={a17 + 0.8} x={540} y={1420}>
          <Slab bg={C.yellow} color={C.ink} size={44} pad="8px 22px 10px" font={BODY}>ONE OF KFC'S BIGGEST FRANCHISEES</Slab>
        </Pop>
      </div>
      {/* contract tear + money */}
      <div style={{ opacity: cardOut }}>
        <Pop t={t} at={a18} x={540} y={330}>
          <Slab bg={C.white} color={C.ink} size={92}>KFC WANTS OUT</Slab>
        </Pop>
        {[0, 1].map((side) => (
          <div key={side} style={{ position: "absolute", left: 540, top: 820, width: 300, height: 600, overflow: "hidden", transform: `translate(${side ? 0 : -300}px,-50%) translateX(${(side ? 1 : -1) * tear * 90}px) rotate(${(side ? 1 : -1) * tear * 10}deg) scale(${pop(t, a18 + 0.1)})`, transformOrigin: side ? "0% 100%" : "100% 100%" }}>
            <div style={{ position: "absolute", left: side ? -300 : 0, width: 600, height: 600, background: C.white, border: `6px solid ${C.ink}` }}>
              <div style={{ fontFamily: HEAD, fontSize: 70, color: C.ink, textAlign: "center", marginTop: 30 }}>FRANCHISE AGREEMENT</div>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} style={{ height: 14, margin: "22px 50px", width: 400 + ((i * 37) % 100), background: C.paper2 }} />
              ))}
              <div style={{ position: "absolute", left: 60, bottom: 40, fontFamily: BODY, fontWeight: 600, fontSize: 30, color: C.grey }}>signed: KFC · Taco Bell</div>
            </div>
          </div>
        ))}
        <Pop t={t} at={a18 + 1.4} x={540} y={1300} rot={-3}>
          <Slab bg={C.red} size={170} pad="4px 40px 14px">${money.toFixed(1)}M</Slab>
        </Pop>
        <Pop t={t} at={a18 + 1.7} x={540} y={1470}>
          <div style={{ fontFamily: HEAD, fontSize: 80, color: C.white, textShadow: SHADOW }}>IN UNPAID FEES</div>
        </Pop>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1800, textAlign: "center", fontFamily: BODY, fontWeight: 600, fontSize: 26, color: "rgba(255,255,255,0.75)" }}>
        Source: Tasty Chick'n Chapter 11 filing, Nov 16, 2026 · Map: NASA Blue Marble
      </div>
    </>
  );
};

// 7. Who's to blame? + comment CTA
const Scene7: React.FC<SP> = ({ t }) => {
  const a19 = local(19, 6), a20 = local(20, 6), a21 = local(21, 6);
  const cmt = pop(t, a21, 11, 170);
  const tap = ease(t, a21 + 1.1, a21 + 1.3);
  return (
    <>
      <Pop t={t} at={a19 - 0.15} x={540} y={300} rot={-3}>
        <Slab bg={C.ink} size={130}>WHO'S TO BLAME?</Slab>
      </Pop>
      <Pop t={t} at={a20} x={290} y={760} rot={-6}>
        <div style={{ width: 420, height: 520, background: C.white, border: `6px solid ${C.ink}`, boxShadow: `12px 14px 0 ${C.ink}`, textAlign: "center", paddingTop: 50 }}>
          <div style={{ display: "flex", justifyContent: "center", gap: 6 }}>{[0, 1, 2].map((i) => <Store key={i} size={100} />)}</div>
          <div style={{ fontFamily: HEAD, fontSize: 70, color: C.ink, marginTop: 40, lineHeight: 1 }}>THE<br />FRANCHISEE</div>
        </div>
      </Pop>
      <Pop t={t} at={a20 + 0.75} x={790} y={760} rot={6}>
        <div style={{ width: 420, height: 520, background: C.red, border: `6px solid ${C.ink}`, boxShadow: `12px 14px 0 ${C.ink}`, textAlign: "center", paddingTop: 40 }}>
          <Building w={220} />
          <div style={{ fontFamily: HEAD, fontSize: 130, color: C.white, marginTop: 10, WebkitTextStroke: `3px ${C.ink}` }}>KFC</div>
        </div>
      </Pop>
      <Pop t={t} at={a20 + 0.4} x={540} y={760}>
        <div style={{ width: 170, height: 170, borderRadius: 999, background: C.yellow, border: `7px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: HEAD, fontSize: 90, color: C.ink }}>VS</div>
      </Pop>
      {cmt > 0 && (
        <div style={{ position: "absolute", left: 540, top: 1130, transform: `translate(-50%,-50%) scale(${cmt})` }}>
          <div style={{ position: "relative", width: 880, background: C.white, border: `6px solid ${C.ink}`, borderRadius: 40, boxShadow: `12px 14px 0 ${C.ink}`, padding: "30px 40px", display: "flex", alignItems: "center", gap: 30 }}>
            <svg width={110} height={110} viewBox="0 0 100 100">
              <path d="M10 18 Q10 8 20 8 L80 8 Q90 8 90 18 L90 62 Q90 72 80 72 L42 72 L22 92 L24 72 L20 72 Q10 72 10 62 Z" fill={C.yellow} stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
              {[32, 50, 68].map((x, i) => <circle key={x} cx={x} cy={40} r={6 + 2 * Math.max(0, Math.sin(t * 8 - i))} fill={C.ink} />)}
            </svg>
            <div style={{ fontFamily: HEAD, fontSize: 84, color: C.ink, lineHeight: 1 }}>TELL ME IN<br />THE COMMENTS</div>
          </div>
        </div>
      )}
      <Pop t={t} at={a21 + 0.7} x={540} y={1430}>
        <div style={{ position: "relative" }}>
          <div style={{ background: tap > 0.5 ? C.grey : C.red, color: C.white, fontFamily: HEAD, fontSize: 90, whiteSpace: "nowrap", padding: "6px 70px 14px", border: `6px solid ${C.ink}`, borderRadius: 24, boxShadow: `10px ${12 - tap * 8}px 0 ${C.ink}`, transform: `translateY(${tap * 6}px)` }}>
            {tap > 0.5 ? "FOLLOWING" : "+ FOLLOW"}
          </div>
          <svg width={110} height={130} viewBox="0 0 50 60" style={{ position: "absolute", right: -40, top: 60 - tap * 30 + (1 - ease(t, a21 + 0.8, a21 + 1.1)) * 120 }}>
            <path d="M8 4 L8 46 L18 37 L25 54 L32 51 L25 34 L38 34 Z" fill={C.white} stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
          </svg>
        </div>
      </Pop>
    </>
  );
};

/* ---------------- captions ---------------- */
type W = { text: string; start: number; end: number };
const PAGES: { words: W[]; start: number; end: number }[] = (() => {
  const pages: { words: W[]; start: number; end: number }[] = [];
  SEG.forEach((seg, si) => {
    const raw = seg.text.split(" ");
    const weights = raw.map((w) => w.replace(/[^A-Za-z0-9']/g, "").length + 2);
    const tot = weights.reduce((a, b) => a + b, 0);
    let acc = seg.start;
    const words: W[] = raw.map((w, i) => {
      const d = ((seg.end - seg.start) * weights[i]) / tot;
      const o = { text: w, start: acc, end: acc + d };
      acc += d;
      return o;
    });
    for (let i = 0; i < words.length; i += 4) {
      const chunk = words.slice(i, i + 4);
      pages.push({ words: chunk, start: chunk[0].start, end: chunk[chunk.length - 1].end });
    }
    const next = SEG[si + 1];
    if (pages.length) pages[pages.length - 1].end = next ? Math.min(next.start, seg.end + 0.25) : seg.end + 0.8;
  });
  return pages;
})();

const Captions: React.FC<{ s: number }> = ({ s }) => {
  const page = PAGES.find((p) => s >= p.start - 0.05 && s < p.end);
  if (!page) return null;
  const k = pop(s, page.start - 0.05, 14, 260);
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 1610, display: "flex", justifyContent: "center", flexWrap: "wrap", gap: "0 18px", transform: `scale(${0.85 + 0.15 * k})` }}>
      {page.words.map((w, i) => {
        const on = s >= w.start;
        const cur = on && s < w.end + 0.05;
        return (
          <span key={i} style={{ fontFamily: BODY, fontWeight: 800, fontSize: 62, color: cur ? C.ink : C.white, background: cur ? C.yellow : "transparent", padding: "0 10px", borderRadius: 10, opacity: on ? 1 : 0.55, WebkitTextStroke: cur ? "0" : `2px ${C.ink}`, textShadow: cur ? "none" : `4px 4px 0 ${C.ink}`, textTransform: "uppercase" }}>
            {w.text}
          </span>
        );
      })}
    </div>
  );
};

/* ---------------- paper texture + grain ---------------- */
const Paper: React.FC<{ frame: number }> = ({ frame }) => (
  <>
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, ${C.paper} 55%, ${C.paper2} 100%)` }} />
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, mixBlendMode: "multiply", opacity: 0.35 }}>
      <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="3" /><feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.48  0 0 0 0 0.38  0 0 0 0.9 0" /></filter>
      <rect width="1080" height="1920" filter="url(#paper)" />
    </svg>
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, mixBlendMode: "multiply", opacity: 0.12 }}>
      <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="1" seed={Math.floor(frame / 2) % 50} /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="1080" height="1920" filter="url(#grain)" />
    </svg>
  </>
);

/* ---------------- main ---------------- */
const SHAKES = [S(1) + 0.35, S(12), S(15) + 0.6];
const SCENE_COMPONENTS = [Scene1, Scene2, Scene3, Scene4, Scene5, Scene6, Scene7];

export const Video: React.FC = () => {
  const frame = useCurrentFrame();
  const s = frame / FPS;
  let idx = SCENES.findIndex((b, i) => s >= b && s < SCENES[i + 1]);
  if (idx < 0) idx = SCENE_COMPONENTS.length - 1;
  const Scene = SCENE_COMPONENTS[idx];
  const t = s - SCENES[idx];

  let sx = 0, sy = 0;
  for (const h of SHAKES) {
    if (s >= h && s < h + 0.35) {
      const amp = 26 * (1 - (s - h) / 0.35);
      sx += (random(`x${frame}`) - 0.5) * amp * 2;
      sy += (random(`y${frame}`) - 0.5) * amp * 2;
    }
  }
  // quick wipe flash at each cut
  const sinceCut = t;
  const flash = idx > 0 ? 1 - ease(sinceCut, 0, 0.12) : 0;

  return (
    <AbsoluteFill style={{ background: C.paper, overflow: "hidden" }}>
      <style>{FONT_CSS}</style>
      <MapBg s={s} />
      <AbsoluteFill style={{ transform: `translate(${sx}px,${sy}px)` }}>
        <Scene t={t} />
      </AbsoluteFill>
      {flash > 0 && <AbsoluteFill style={{ background: C.ink, opacity: flash * 0.35 }} />}
      <Captions s={s} />
      <Audio src={staticFile("mix.wav")} />
    </AbsoluteFill>
  );
};
